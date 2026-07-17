#!/usr/bin/env python3
"""Verify the outward-rounded interval log for the R_U hierarchy certificate.

Issue #331. The verifier rebuilds the structural inputs from the log's
declared-input block, re-runs the full R_U formula stack in the
directed-rounding binary64 backend, and requires:

1. the backend declaration in the log matches the backend module policy;
2. the declared input keys match the structural allowlist exactly and the
   resolved binary64 brackets reproduce bit-exactly;
3. every serialized interval bound in the computed block reproduces
   bit-exactly from directed rounding alone;
4. the endpoint sign conditions, the strictly negative derivative
   enclosure, and the strict Krawczyk interior inclusion hold when
   re-derived from the logged hex bounds;
5. the Krawczyk image recomputed from the logged center, preconditioner,
   Phi(c), and derivative enclosure equals the logged witness interval;
6. the high-precision root recorded in the log's consistency block lies
   inside the outward-rounded witness interval (exact rational check);
7. no measured endpoint constant appears in the verify path: the input
   allowlist is enforced and the log, the backend module, the formula
   stack module, and this verifier are scanned for measured-constant
   markers.

The verifier consumes P_fwd and structural integers/rationals only. It
does not read any other certificate file and it does not import any
measured endpoint constant.

Usage, from code/particles/hierarchy:

    python3 validators/verify_ru_outward_rounded_log.py \
        [certificates/R_U_outward_rounded_interval_log.json]
"""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from outward_interval import IV, ONE, backend_declaration  # noqa: E402
from ru_formula_stack import (  # noqa: E402
    DECLARED_INPUT_KEYS,
    Inputs,
    run_full_evaluation,
    structural_input_block,
)

DEFAULT_LOG = ROOT / "certificates" / "R_U_outward_rounded_interval_log.json"

# Markers of measured endpoint constants from external metrology and
# particle-data compilations. The tokens are assembled from fragments so
# this file does not trip its own scan. The digit strings cover the
# fine-structure endpoint, alpha, v in GeV, m_Z, m_W, m_H, alpha_s(m_Z),
# G_F, the weak mixing angle, and G.
_FORBIDDEN_TOKENS = [
    "COD" + "ATA",
    "P" + "DG",
    "137." + "0359",
    "137." + "036",
    "0.00729" + "73525",
    "246." + "22",
    "91." + "1876",
    "80." + "377",
    "80." + "36",
    "125." + "25",
    "0.11" + "79",
    "1.16637" + "87",
    "0.23" + "121",
    "6.67" + "43",
]


def _f(hexstr: str) -> float:
    return float.fromhex(hexstr)


def _scan_no_measured_constants(log_text: str) -> dict:
    sources = {
        "log": log_text,
        "outward_interval.py": (ROOT / "tools" / "outward_interval.py").read_text(encoding="utf-8"),
        "ru_formula_stack.py": (ROOT / "tools" / "ru_formula_stack.py").read_text(encoding="utf-8"),
        "verifier": pathlib.Path(__file__).read_text(encoding="utf-8"),
    }
    hits = []
    for name, text in sources.items():
        for token in _FORBIDDEN_TOKENS:
            if token in text:
                hits.append({"source": name, "token": token})
    return {"clean": not hits, "hits": hits}


def main(log_path: str | None = None) -> int:
    path = pathlib.Path(log_path) if log_path else DEFAULT_LOG
    log_text = path.read_text(encoding="utf-8")
    log = json.loads(log_text)
    checks: dict[str, bool] = {}

    # 1. Backend declaration matches the module policy.
    checks["backend_declaration_matches_module"] = log["backend"] == backend_declaration()

    # 2. Structural input allowlist and bit-exact resolved brackets.
    declared = log["declared_inputs"]["declared"]
    checks["declared_input_keys_match_allowlist"] = tuple(sorted(declared.keys())) == tuple(
        sorted(DECLARED_INPUT_KEYS)
    )
    inp = Inputs(declared)
    checks["resolved_input_brackets_bit_exact"] = (
        structural_input_block(inp) == log["declared_inputs"]
    )

    # 3. Bit-exact recomputation of the entire computed block.
    recomputed = run_full_evaluation(inp)
    recomputed = json.loads(json.dumps(recomputed))
    checks["computed_block_bit_exact"] = recomputed == log["computed"]

    # 4. Independent re-derivation of the inclusion conditions from the
    # logged hex bounds.
    signs = log["computed"]["endpoint_signs"]
    phi_lo_lo = _f(signs["Phi_at_I_U_lower"]["lo_hex"])
    phi_hi_hi = _f(signs["Phi_at_I_U_upper"]["hi_hex"])
    checks["endpoint_signs_strict"] = phi_lo_lo > 0.0 and phi_hi_hi < 0.0

    deriv = log["computed"]["derivative_enclosure"]["dPhi_over_I_U"]
    checks["derivative_enclosure_strictly_negative"] = _f(deriv["hi_hex"]) < 0.0

    kr = log["computed"]["krawczyk"]
    X_lo = _f(kr["X"]["lo_hex"])
    X_hi = _f(kr["X"]["hi_hex"])
    K_lo = _f(kr["K_of_X"]["lo_hex"])
    K_hi = _f(kr["K_of_X"]["hi_hex"])
    checks["krawczyk_image_strictly_inside_interior"] = X_lo < K_lo <= K_hi < X_hi

    # 5. Recompute the Krawczyk image from the logged operands.
    c = _f(kr["center_c"]["hex"])
    Y = _f(kr["Y"]["hex"])
    X = IV(X_lo, X_hi)
    c_iv = IV(c, c)
    Y_iv = IV(Y, Y)
    phi_c = IV(_f(kr["Phi_at_center"]["lo_hex"]), _f(kr["Phi_at_center"]["hi_hex"]))
    dphi = IV(_f(kr["dPhi_over_X"]["lo_hex"]), _f(kr["dPhi_over_X"]["hi_hex"]))
    one_minus = ONE - (Y_iv * dphi)
    K = (c_iv - (Y_iv * phi_c)) + (one_minus * (X - c_iv))
    checks["krawczyk_image_recomputed_bit_exact"] = (
        K.lo.hex() == kr["K_of_X"]["lo_hex"] and K.hi.hex() == kr["K_of_X"]["hi_hex"]
    )

    witness = log["computed"]["witness"]["R_U_witness_interval"]
    checks["witness_equals_krawczyk_image"] = (
        witness["lo_hex"] == kr["K_of_X"]["lo_hex"] and witness["hi_hex"] == kr["K_of_X"]["hi_hex"]
    )

    # 6. Consistency with the high-precision root, by exact rational
    # comparison of the decimal string recorded in the log.
    consistency = log["consistency_with_high_precision_certificates"]
    hp_root = Fraction(consistency["high_precision_root_decimal"])
    w_lo = Fraction(_f(witness["lo_hex"]))
    w_hi = Fraction(_f(witness["hi_hex"]))
    checks["high_precision_root_in_outward_witness"] = w_lo <= hp_root <= w_hi
    hp_K = consistency["high_precision_krawczyk_image"]
    checks["high_precision_krawczyk_image_inside_outward_witness"] = (
        w_lo <= Fraction(hp_K["lower"]) and Fraction(hp_K["upper"]) <= w_hi
    )

    # 7. No measured endpoint constants on the verify path.
    scan = _scan_no_measured_constants(log_text)
    checks["no_measured_endpoint_constants"] = scan["clean"]

    payload = {
        "log": str(path),
        "checks": checks,
        "forbidden_token_scan": scan,
        "R_U_witness_interval": witness,
        "witness_width_decimal": log["computed"]["witness"]["width_decimal"],
        "pass": all(checks.values()),
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
