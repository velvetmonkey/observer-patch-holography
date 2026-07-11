#!/usr/bin/env python3
"""Backward-compatible view of the OPH/BD target-side proxy calculation.

The issue-368 receipt builder is canonical.  This adapter preserves the legacy
report keys while sourcing every number and open gate from that builder; it
cannot emit a positive BD compatibility certificate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_oph_bd_threshold_spectrum_receipts import (
    DEFAULT_PACKET,
    build_receipts,
)


def _operator_audit() -> dict[str, Any]:
    hypercharge = {
        "Q": 1 / 6,
        "Hu": 1 / 2,
        "Hd": -1 / 2,
        "uc": -2 / 3,
        "dc": 1 / 3,
        "L": -1 / 2,
        "ec": 1,
    }
    operators = {
        "Q Hu uc": ("Q", "Hu", "uc"),
        "Q Hd dc": ("Q", "Hd", "dc"),
        "L Hd ec": ("L", "Hd", "ec"),
        "L L ec": ("L", "L", "ec"),
        "L Q dc": ("L", "Q", "dc"),
        "uc dc dc": ("uc", "dc", "dc"),
        "Q Q Q L": ("Q", "Q", "Q", "L"),
        "uc uc dc ec": ("uc", "uc", "dc", "ec"),
    }
    return {
        name: {
            "hypercharge_sum": sum(hypercharge[field] for field in fields),
            "hypercharge_neutral": abs(
                sum(hypercharge[field] for field in fields)
            )
            < 1e-12,
        }
        for name, fields in operators.items()
    }


def compute_report() -> dict[str, Any]:
    packet = json.loads(DEFAULT_PACKET.read_text(encoding="utf-8"))
    receipts = build_receipts(DEFAULT_PACKET)
    proxy = receipts["proxy_targets.json"]
    certificate = receipts["threshold_spectrum_certificate.json"]
    low = proxy["low_energy_tree_coordinates"]
    gauge_row = next(
        row
        for row in proxy["gauge_unification_proxy"]["rows"]
        if row["M_SUSY_GeV"] == "1000"
    )

    inputs = {
        name: float(record["value"])
        for name, record in packet["target_coordinates"].items()
    }
    inputs.update(
        {
            "alpha3_reference_mz": float(
                packet["reference_inputs"]["alpha3_reference_mz"]["value"]
            ),
            "mZ_reference_gev": float(
                packet["reference_inputs"]["mZ_reference_gev"]["value"]
            ),
        }
    )
    stop_rows = [
        {
            "tan_beta": float(row["tan_beta"]),
            "X_t_over_M_S": float(row["X_t_over_M_S"]),
            "required_M_S_GeV": float(row["required_M_S_GeV"]),
        }
        for row in proxy["stop_threshold_proxy"]
    ]

    return {
        "status": certificate["status"],
        "selected_representative": (
            "BD_n=1_OPH_Bouchard-Donagi_massless-cohomology_candidate"
        ),
        "inputs": inputs,
        "low_energy_targets": {
            "y_t_OPH": float(low["y_t_tree_coordinate"]),
            "lambda_H_OPH": float(low["lambda_H_tree_coordinate"]),
            "lambda_MSSM_tree_max": float(
                low["lambda_MSSM_tree_ceiling_coordinate"]
            ),
            "Delta_lambda_min": float(
                low["Delta_lambda_large_tan_beta_coordinate"]
            ),
            "m_h_tree_max_GeV": float(low["m_h_tree_ceiling_GeV"]),
        },
        "stop_threshold_proxy": stop_rows,
        "gauge_unification_proxy": {
            "M_SUSY_GeV": float(gauge_row["M_SUSY_GeV"]),
            "log10_MU_GeV": float(gauge_row["log10_MU_GeV"]),
            "M_U_GeV": float(gauge_row["M_U_GeV"]),
            "alpha_U_inverse": float(gauge_row["alpha_U_inverse"]),
            "alpha3_pred_mZ": float(gauge_row["alpha3_pred_mZ"]),
            "delta_alpha3_inverse_needed": float(
                gauge_row["required_combined_inverse_coupling_correction"][
                    "central"
                ]
            ),
        },
        "operator_audit": _operator_audit(),
        "open_gates": certificate["missing_source_objects"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    encoded = json.dumps(compute_report(), indent=2, sort_keys=True) + "\n"
    if args.out is None:
        print(encoded, end="")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
