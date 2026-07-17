#!/usr/bin/env python3
"""Verify the raw interval input box log for the R_HT declared surface.

Issue #333. The verifier rebuilds the declared branch inputs from the log's
declared-input block, re-runs the full Higgs/top declared-surface formula
stack in the directed-rounding binary64 backend, and requires:

1. the backend declaration in the log matches the backend module policy;
2. the declared input keys match the declared allowlist exactly, the
   resolved centers, boxes, and provenance blocks reproduce bit-exactly,
   and the interval-extension block matches the stack module definition;
3. every serialized interval bound in the computed block reproduces
   bit-exactly from directed rounding alone;
4. the output inclusion conditions hold when re-derived from the logged
   hex bounds: the declared-surface output decimals lie inside the box
   enclosures by exact rational comparison and every center enclosure lies
   inside its box enclosure;
5. the readout non-singularity conditions hold when re-derived from the
   logged hex bounds: the diagonal chart-block entries keep their signs
   over the full box, and the determinant enclosure recomputed from the
   logged diagonal entries is bit-exact and excludes zero;
6. the uniqueness block carries the declared-surface scope: single-valued
   arithmetic on the box, injective diagonal readout, and an explicit
   disclaimer that no criticality-system existence or uniqueness statement
   is made;
7. the provenance contract holds: every input carries an allowed
   provenance class, the declared branch inputs are exactly the
   whitelisted names, and the log, the backend module, the formula stack
   module, and this verifier are scanned for measured-constant markers.

The declared branch inputs (the candidate D10 tuple and the D11 surface
constants) are labeled as such in the log; no measured particle mass value
appears numerically in the input box, and the scan enforces the marker
list below on the whole verify path.

Usage, from code/particles/hierarchy:

    python3 validators/verify_ht_interval_box.py \
        [certificates/R_HT_interval_input_box_log.json]
"""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from outward_interval import IV, backend_declaration  # noqa: E402
from ht_formula_stack import (  # noqa: E402
    ALLOWED_PROVENANCE_CLASSES,
    C_16_9,
    DECLARED_BRANCH_INPUT_WHITELIST,
    DECLARED_INPUT_KEYS,
    Inputs,
    declared_input_block,
    interval_extension_block,
    run_full_evaluation,
)

DEFAULT_LOG = ROOT / "certificates" / "R_HT_interval_input_box_log.json"

# Markers of measured endpoint constants from external metrology and
# particle-data compilations. The tokens are assembled from fragments so
# this file does not trip its own scan. The digit strings cover the
# fine-structure endpoint, alpha, v in GeV, m_Z, m_W, the measured Higgs
# and top mass averages, alpha_s(m_Z), G_F, the weak mixing angle, and G.
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
    "172." + "57",
    "172." + "69",
    "0.11" + "79",
    "1.16637" + "87",
    "0.23" + "121",
    "6.67" + "43",
]

_UNIQUENESS_STATEMENT_REQUIRED = [
    "exactly one output pair",
    "injective on the box image",
]
_UNIQUENESS_SCOPE_REQUIRED = [
    "declared frozen D10/D11 surface map only",
    "neither an existence nor a uniqueness statement for the two-loop criticality system",
    "complex-pole gates open",
]


def _f(hexstr: str) -> float:
    return float.fromhex(hexstr)


def _frac(hexstr: str) -> Fraction:
    return Fraction(float.fromhex(hexstr))


def _scan_no_measured_constants(log_text: str) -> dict:
    sources = {
        "log": log_text,
        "outward_interval.py": (ROOT / "tools" / "outward_interval.py").read_text(encoding="utf-8"),
        "ht_formula_stack.py": (ROOT / "tools" / "ht_formula_stack.py").read_text(encoding="utf-8"),
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

    # 2. Declared input allowlist, bit-exact resolved blocks, and the
    # interval-extension definition.
    declared = log["declared_inputs"]["declared"]
    checks["declared_input_keys_match_allowlist"] = tuple(sorted(declared.keys())) == tuple(
        sorted(DECLARED_INPUT_KEYS)
    )
    inp = Inputs(declared)
    checks["resolved_input_blocks_bit_exact"] = (
        declared_input_block(inp) == log["declared_inputs"]
    )
    checks["interval_extension_matches_module"] = (
        log["interval_extension"] == interval_extension_block()
    )

    # 3. Bit-exact recomputation of the entire computed block.
    recomputed = json.loads(json.dumps(run_full_evaluation(inp)))
    checks["computed_block_bit_exact"] = recomputed == log["computed"]

    # 4. Independent re-derivation of the output inclusion conditions from
    # the logged hex bounds and the declared-surface output decimals.
    consistency = log["consistency_with_declared_surface_certificate"]
    outputs = consistency["declared_outputs"]
    inclusion = log["computed"]["output_inclusion"]
    member_ok = True
    for key in ("m_H_GeV", "m_t_D11_GeV"):
        box = inclusion[key]["box_enclosure"]
        value = Fraction(outputs[key])
        member_ok = member_ok and _frac(box["lo_hex"]) <= value <= _frac(box["hi_hex"])
    checks["declared_outputs_inside_box_enclosures"] = member_ok
    nest_ok = True
    for entry in inclusion.values():
        c = entry["center_enclosure"]
        b = entry["box_enclosure"]
        nest_ok = nest_ok and _f(b["lo_hex"]) <= _f(c["lo_hex"]) and _f(c["hi_hex"]) <= _f(b["hi_hex"])
    checks["center_enclosures_inside_box_enclosures"] = nest_ok

    # 5. Non-singularity of the diagonal chart block, re-derived from the
    # logged hex bounds, with a bit-exact determinant recomputation.
    ns = log["computed"]["readout_non_singularity"]
    top = IV(_f(ns["d_mt_d_pi_y"]["lo_hex"]), _f(ns["d_mt_d_pi_y"]["hi_hex"]))
    higgs = IV(
        _f(ns["d_mH_d_pi_lambda"]["lo_hex"]), _f(ns["d_mH_d_pi_lambda"]["hi_hex"])
    )
    det = top * higgs
    checks["top_diagonal_strictly_positive"] = top.lo > 0.0
    checks["higgs_diagonal_strictly_negative"] = higgs.hi < 0.0
    checks["determinant_recomputed_bit_exact"] = (
        det.lo.hex() == ns["determinant"]["lo_hex"]
        and det.hi.hex() == ns["determinant"]["hi_hex"]
    )
    checks["determinant_excludes_zero"] = det.hi < 0.0
    top_direct = inp.boxes["d_mt_pole_d_y_t"] * inp.boxes["y_t_core_mt"]
    higgs_direct = -(C_16_9 * (inp.boxes["d_mH_d_lambda"] * inp.boxes["lambda_core_mt"]))
    checks["chart_diagonals_reproduce_from_input_boxes"] = (
        top_direct.lo.hex() == ns["d_mt_d_pi_y"]["lo_hex"]
        and top_direct.hi.hex() == ns["d_mt_d_pi_y"]["hi_hex"]
        and higgs_direct.lo.hex() == ns["d_mH_d_pi_lambda"]["lo_hex"]
        and higgs_direct.hi.hex() == ns["d_mH_d_pi_lambda"]["hi_hex"]
    )

    # 6. Uniqueness statement and scope.
    uniqueness = log["computed"]["uniqueness"]
    checks["uniqueness_statement_scoped"] = all(
        needle in uniqueness["statement"] for needle in _UNIQUENESS_STATEMENT_REQUIRED
    ) and all(needle in uniqueness["scope"] for needle in _UNIQUENESS_SCOPE_REQUIRED)

    # 7. Provenance contract: allowed classes only, exact declared-branch
    # whitelist, and no measured endpoint constants on the verify path.
    resolved = log["declared_inputs"]["resolved"]
    classes_ok = all(
        entry["provenance_class"] in ALLOWED_PROVENANCE_CLASSES
        for entry in resolved.values()
    )
    branch_names = sorted(
        name
        for name, entry in resolved.items()
        if entry["provenance_class"].startswith("declared_branch_input")
    )
    checks["provenance_classes_allowed"] = classes_ok
    checks["declared_branch_inputs_match_whitelist"] = branch_names == sorted(
        DECLARED_BRANCH_INPUT_WHITELIST
    )
    scan = _scan_no_measured_constants(log_text)
    checks["no_measured_endpoint_constants"] = scan["clean"]

    payload = {
        "log": str(path),
        "checks": checks,
        "forbidden_token_scan": scan,
        "m_H_box_enclosure": inclusion["m_H_GeV"]["box_enclosure"],
        "m_t_box_enclosure": inclusion["m_t_D11_GeV"]["box_enclosure"],
        "chart_determinant": ns["determinant"],
        "pass": all(checks.values()),
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
