#!/usr/bin/env python3
"""Emit the outward-rounded interval log for the R_U hierarchy certificate.

Issue #331. The log re-evaluates the full R_U formula stack in the
directed-rounding binary64 interval backend (tools/outward_interval.py),
records the interval image of every named formula-DAG node at both I_U
endpoints, at the center, and over the full interval with the derivative
enclosure, and records the Krawczyk inclusion data and the witness
interval. A consistency block compares the outward-rounded witness against
the high-precision mpmath certificates.

Usage, from code/particles/hierarchy:

    python3 computations/generate_ru_outward_rounded_log.py

The log lands at certificates/R_U_outward_rounded_interval_log.json and is
checked by validators/verify_ru_outward_rounded_log.py.
"""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from outward_interval import backend_declaration  # noqa: E402
from ru_formula_stack import (  # noqa: E402
    DEFAULT_DECLARED_INPUTS,
    STACK_ID,
    STACK_VERSION,
    Inputs,
    run_full_evaluation,
    structural_input_block,
)

LOG_PATH = ROOT / "certificates" / "R_U_outward_rounded_interval_log.json"


def _fraction_from_hex(h: str) -> Fraction:
    return Fraction(float.fromhex(h))


def consistency_block(computed: dict) -> dict:
    """Compare the outward-rounded record against the mpmath certificates."""
    interval_cert = json.loads((ROOT / "certificates" / "R_U_interval_certificate.json").read_text())
    krawczyk_cert = json.loads((ROOT / "certificates" / "R_U_krawczyk_certificate.json").read_text())

    witness = computed["witness"]["R_U_witness_interval"]
    w_lo = _fraction_from_hex(witness["lo_hex"])
    w_hi = _fraction_from_hex(witness["hi_hex"])

    hp_root = interval_cert["candidate_recomputed_root"]
    hp_root_frac = Fraction(hp_root)
    display = interval_cert["candidate_display"]
    display_frac = Fraction(display)

    hp_K_lo = Fraction(krawczyk_cert["K_I"]["lower"])
    hp_K_hi = Fraction(krawczyk_cert["K_I"]["upper"])
    hp_D_lo = Fraction(krawczyk_cert["derivative_interval"]["lower"])
    hp_D_hi = Fraction(krawczyk_cert["derivative_interval"]["upper"])

    d = computed["derivative_enclosure"]["dPhi_over_I_U"]
    d_lo = _fraction_from_hex(d["lo_hex"])
    d_hi = _fraction_from_hex(d["hi_hex"])

    return {
        "high_precision_interval_certificate": "certificates/R_U_interval_certificate.json",
        "high_precision_krawczyk_certificate": "certificates/R_U_krawczyk_certificate.json",
        "high_precision_root_decimal": hp_root,
        "high_precision_root_in_outward_witness": w_lo <= hp_root_frac <= w_hi,
        "candidate_display_decimal": display,
        "candidate_display_in_outward_witness": w_lo <= display_frac <= w_hi,
        "high_precision_krawczyk_image": dict(krawczyk_cert["K_I"]),
        "high_precision_krawczyk_image_inside_outward_witness": w_lo <= hp_K_lo and hp_K_hi <= w_hi,
        "high_precision_derivative_interval": {
            "lower": krawczyk_cert["derivative_interval"]["lower"],
            "upper": krawczyk_cert["derivative_interval"]["upper"],
        },
        "high_precision_derivative_interval_inside_outward_enclosure": d_lo <= hp_D_lo and hp_D_hi <= d_hi,
        "note": (
            "The outward-rounded witness is wider than the 80-digit mpmath "
            "witness because binary64 dependency effects widen the derivative "
            "enclosure; both witnesses certify the same unique zero, and the "
            "high-precision root and Krawczyk image lie inside the "
            "outward-rounded witness interval."
        ),
    }


def checks_block(computed: dict, consistency: dict) -> dict:
    return {
        "endpoint_signs_strict": computed["endpoint_signs"]["existence_by_intermediate_value_theorem"],
        "derivative_enclosure_strictly_negative": computed["derivative_enclosure"]["strictly_negative"],
        "krawczyk_image_strictly_inside_interior": computed["krawczyk"]["K_strictly_inside_interior_of_X"],
        "high_precision_root_in_outward_witness": consistency["high_precision_root_in_outward_witness"],
        "high_precision_krawczyk_image_inside_outward_witness": consistency[
            "high_precision_krawczyk_image_inside_outward_witness"
        ],
        "pass": all(
            [
                computed["endpoint_signs"]["existence_by_intermediate_value_theorem"],
                computed["derivative_enclosure"]["strictly_negative"],
                computed["krawczyk"]["K_strictly_inside_interior_of_X"],
                consistency["high_precision_root_in_outward_witness"],
                consistency["high_precision_krawczyk_image_inside_outward_witness"],
            ]
        ),
    }


def main() -> int:
    inp = Inputs(dict(DEFAULT_DECLARED_INPUTS))
    computed = run_full_evaluation(inp)
    consistency = consistency_block(computed)
    checks = checks_block(computed, consistency)

    log = {
        "artifact": "R_U_outward_rounded_interval_log",
        "issue": 331,
        "status": "outward_rounded_interval_log_supplied",
        "stack_id": STACK_ID,
        "stack_version": STACK_VERSION,
        "backend": backend_declaration(),
        "declared_inputs": structural_input_block(inp),
        "computed": computed,
        "consistency_with_high_precision_certificates": consistency,
        "checks": checks,
        "reproduction": {
            "generator": "python3 computations/generate_ru_outward_rounded_log.py",
            "verifier": "python3 validators/verify_ru_outward_rounded_log.py",
            "determinism": (
                "The computed block is a deterministic function of the "
                "declared inputs under the backend policy; the verifier "
                "recomputes every node and requires bit-exact agreement of "
                "all serialized bounds."
            ),
        },
    }

    LOG_PATH.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    summary = {
        "written": str(LOG_PATH.relative_to(ROOT)),
        "R_U_witness_interval": computed["witness"]["R_U_witness_interval"],
        "width_decimal": computed["witness"]["width_decimal"],
        "pass": checks["pass"],
    }
    print(json.dumps(summary, indent=2))
    return 0 if checks["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
