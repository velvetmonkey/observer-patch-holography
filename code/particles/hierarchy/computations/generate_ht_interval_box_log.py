#!/usr/bin/env python3
"""Emit the raw interval input box log for the R_HT declared surface.

Issue #333. The log publishes the raw interval input box of the Higgs/top
declared-surface map (eleven declared branch inputs with centers, boxes,
units, and provenance), re-evaluates the frozen formula stack of
certificates/R_HT_declared_surface_certificate.json in the directed-rounding
binary64 interval backend (tools/outward_interval.py), and records the
interval image of every named formula node at the input centers and over
the full input box with the Jacobian gradient enclosure, the diagonal
chart-block non-singularity certificate, the output inclusion checks, and
the uniqueness scope. A consistency block checks by exact rational
comparison that the outputs recorded in the declared-surface certificate
lie inside the emitted enclosures.

Usage, from code/particles/hierarchy:

    python3 computations/generate_ht_interval_box_log.py

The log lands at certificates/R_HT_interval_input_box_log.json and is
checked by validators/verify_ht_interval_box.py.
"""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from outward_interval import backend_declaration  # noqa: E402
from ht_formula_stack import (  # noqa: E402
    DEFAULT_DECLARED_INPUTS,
    STACK_ID,
    STACK_VERSION,
    Inputs,
    declared_input_block,
    interval_extension_block,
    run_full_evaluation,
)

LOG_PATH = ROOT / "certificates" / "R_HT_interval_input_box_log.json"
SURFACE_CERT = ROOT / "certificates" / "R_HT_declared_surface_certificate.json"


def _fraction_from_hex(h: str) -> Fraction:
    return Fraction(float.fromhex(h))


def _membership(decimal: str, enclosure: dict) -> bool:
    value = Fraction(decimal)
    lo = _fraction_from_hex(enclosure["lo_hex"])
    hi = _fraction_from_hex(enclosure["hi_hex"])
    return lo <= value <= hi


def consistency_block(computed: dict) -> dict:
    """Exact rational membership of the declared-surface outputs."""
    surface = json.loads(SURFACE_CERT.read_text(encoding="utf-8"))
    outputs = surface["outputs"]
    inclusion = computed["output_inclusion"]
    block = {
        "declared_surface_certificate": "certificates/R_HT_declared_surface_certificate.json",
        "declared_outputs": dict(outputs),
    }
    for key, node in (("m_H_GeV", "m_H_GeV"), ("m_t_D11_GeV", "m_t_D11_GeV")):
        block[f"{key}_inside_box_enclosure"] = _membership(
            outputs[key], inclusion[node]["box_enclosure"]
        )
        block[f"{key}_inside_center_enclosure"] = _membership(
            outputs[key], inclusion[node]["center_enclosure"]
        )
    block["note"] = (
        "Box membership is the certified condition; the center-enclosure "
        "booleans are recorded data, since the stored decimal outputs were "
        "computed in round-to-nearest binary64 and can sit a few ulps from "
        "the true real value pinned by the center enclosure."
    )
    return block


def checks_block(computed: dict, consistency: dict) -> dict:
    ns = computed["readout_non_singularity"]
    inclusion = computed["output_inclusion"]
    checks = {
        "declared_outputs_inside_box_enclosures": (
            consistency["m_H_GeV_inside_box_enclosure"]
            and consistency["m_t_D11_GeV_inside_box_enclosure"]
        ),
        "center_enclosures_inside_box_enclosures": all(
            entry["center_enclosure_inside_box_enclosure"]
            for entry in inclusion.values()
        ),
        "top_diagonal_strictly_positive": ns["top_diagonal_strictly_positive"],
        "higgs_diagonal_strictly_negative": ns["higgs_diagonal_strictly_negative"],
        "determinant_excludes_zero": ns["determinant_excludes_zero"],
    }
    checks["pass"] = all(checks.values())
    return checks


def main() -> int:
    inp = Inputs(dict(DEFAULT_DECLARED_INPUTS))
    computed = run_full_evaluation(inp)
    consistency = consistency_block(computed)
    checks = checks_block(computed, consistency)

    log = {
        "artifact": "R_HT_interval_input_box_log",
        "issue": 333,
        "status": "raw_interval_input_box_and_jacobian_enclosure_supplied",
        "stack_id": STACK_ID,
        "stack_version": STACK_VERSION,
        "backend": backend_declaration(),
        "interval_extension": interval_extension_block(),
        "declared_inputs": declared_input_block(inp),
        "computed": computed,
        "consistency_with_declared_surface_certificate": consistency,
        "checks": checks,
        "reproduction": {
            "generator": "python3 computations/generate_ht_interval_box_log.py",
            "verifier": "python3 validators/verify_ht_interval_box.py",
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
        "m_H_box_enclosure": computed["output_inclusion"]["m_H_GeV"]["box_enclosure"],
        "m_t_box_enclosure": computed["output_inclusion"]["m_t_D11_GeV"]["box_enclosure"],
        "determinant": computed["readout_non_singularity"]["determinant"],
        "pass": checks["pass"],
    }
    print(json.dumps(summary, indent=2))
    return 0 if checks["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
