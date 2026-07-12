#!/usr/bin/env python3
"""Fail-closed end-to-end gate for a blind charged-lepton prediction.

The gate separates three logically independent requirements: a source-emitted
two-ratio shape, an electromagnetic transport packet that fixes the common
scale, and a freeze-before-comparison receipt.  It never substitutes current
family targets or empirical transport for a missing source object.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "particles" / "runs" / "leptons"
DEFAULT_ORDERED = RUNS / "charged_sector_local_ordered_package_source_emission.json"
DEFAULT_SCALARS = RUNS / "charged_sector_local_support_extension_source_scalar_pair_readback.json"
DEFAULT_TRANSPORT = RUNS / "charged_kappa_interval_from_alpha_transport.json"
DEFAULT_OUT = RUNS / "charged_blind_prediction_gate.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(
    ordered: dict[str, Any], scalars: dict[str, Any], transport: dict[str, Any]
) -> dict[str, Any]:
    source_logs = [
        float(value)
        for value in ordered["source_side_ordered_package_log_per_side_emitted"]
    ]
    if len(source_logs) != 3 or source_logs != sorted(source_logs):
        raise ValueError("ordered source package must contain three ordered log coordinates")

    direct_ratios = {
        "middle_over_light": math.exp(source_logs[1] - source_logs[0]),
        "heavy_over_light": math.exp(source_logs[2] - source_logs[0]),
    }
    eta = scalars.get("eta_source_support_extension_log_per_side")
    sigma = scalars.get("sigma_source_support_extension_total_log_per_side")
    shape_closed = eta is not None and sigma is not None

    guards = dict(transport.get("guards", {}))
    transport_blockers = sorted(
        name
        for name in (
            "source_only",
            "blind_normalization_prediction",
        )
        if guards.get(name) is not True
    )
    target_leaks = sorted(
        name
        for name in (
            "target_anchored_lepton_ratios_in_solve_path",
            "measured_lepton_triple_used_to_calibrate_higher_order_remainder",
            "charged_mass_information_in_solve_path",
            "measured_alpha_in_solve_path",
            "external_cross_section_data_used",
        )
        if guards.get(name) is True
    )
    normalization_closed = not transport_blockers and not target_leaks
    freeze_receipt_present = False
    promotion_allowed = shape_closed and normalization_closed and freeze_receipt_present

    blockers: list[str] = []
    if eta is None:
        blockers.append("eta_source_support_extension_log_per_side")
    if sigma is None:
        blockers.append("sigma_source_support_extension_total_log_per_side")
    blockers.extend(f"transport:{name}" for name in transport_blockers)
    blockers.extend(f"target_leak:{name}" for name in target_leaks)
    if not freeze_receipt_present:
        blockers.append("freeze_before_PDG_comparison_receipt")

    return {
        "artifact": "oph_charged_blind_prediction_gate",
        "status": "PASS_BLIND_CHARGED_PREDICTION" if promotion_allowed else "OPEN",
        "public_promotion_allowed": promotion_allowed,
        "charged_mass_rows": [] if not promotion_allowed else transport["conditional_mass_rows"],
        "source_shape_gate": {
            "closed": shape_closed,
            "eta_source": eta,
            "sigma_source": sigma,
            "direct_current_support_ratio_diagnostic": direct_ratios,
            "direct_current_support_predictive_status": "rejected_insufficient_hierarchy",
            "reason": (
                "The current support emits only order-one ratios. The declared support "
                "extension requires independently emitted eta and sigma values; formulas "
                "alone do not constitute a prediction."
            ),
        },
        "normalization_gate": {
            "closed": normalization_closed,
            "mechanism": "electromagnetic_transport_unique_common_scale",
            "identifiability_derivative": "d(packet)/d(kappa) = -2/pi",
            "transport_blockers": transport_blockers,
            "target_leaks": target_leaks,
        },
        "freeze_gate": {
            "closed": freeze_receipt_present,
            "required": "hash-bound mass triple produced before any PDG charged-mass comparison",
        },
        "blockers": blockers,
        "theorem_boundary": (
            "The electromagnetic transport removes the continuous normalization freedom "
            "once its inputs are source-emitted, but it cannot determine the two charged "
            "shape scalars. No charged mass is emitted until shape, normalization, and "
            "freeze-before-comparison gates all close."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ordered", type=Path, default=DEFAULT_ORDERED)
    parser.add_argument("--scalars", type=Path, default=DEFAULT_SCALARS)
    parser.add_argument("--transport", type=Path, default=DEFAULT_TRANSPORT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build_artifact(_load(args.ordered), _load(args.scalars), _load(args.transport))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "blockers": artifact["blockers"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
