#!/usr/bin/env python3
"""Evaluate the conditional OPH Z6 shared-edge reserve coefficient."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from d6_capacity_calculator import compute as compute_d6  # noqa: E402
from galaxy_channel_selector_candidates import Candidate, evaluate_candidate  # noqa: E402
from sparc_rar_compare import (  # noqa: E402
    DEFAULT_RAR_ALL,
    DEFAULT_RAR_BINS,
    parse_numeric_rows,
)
from sparc_rotation_curve_compare import (  # noqa: E402
    DEFAULT_MASS_MODELS,
    parse_mass_model_rows,
)


P_PIXEL = 1.630968209403959
Z6_ORDER = 6
ELLBAR_SHARED = P_PIXEL / 4.0
EPSILON_Z6 = ELLBAR_SHARED / Z6_ORDER


def z6_scenarios() -> list[dict[str, Any]]:
    linear_lambda = 1.0 - EPSILON_Z6
    poisson_lambda = math.exp(-EPSILON_Z6)
    return [
        {
            "name": "z6_poisson_reserve_thinning",
            "lambda_collar": poisson_lambda,
            "reserve_fraction": 1.0 - poisson_lambda,
            "law": "lambda_collar = exp(-P/24)",
            "status": "selected by edge-capacity activity normalization under independent-increment Poisson counting",
        },
        {
            "name": "z6_linear_capacity_reserve",
            "lambda_collar": linear_lambda,
            "reserve_fraction": 1.0 - linear_lambda,
            "law": "lambda_collar = 1 - P/24",
            "status": "finite-slot approximation or alternative model; not selected by independent-increment theorem",
        },
    ]


def compute(args: argparse.Namespace) -> dict[str, Any]:
    rar_rows = parse_numeric_rows(args.rar_all, 4)
    bin_rows = parse_numeric_rows(args.rar_bins, 4)
    mass_rows = parse_mass_model_rows(args.mass_models)
    a0_oph = compute_d6(args.n_scr)["d12_benchmarks_not_theorem_outputs"][
        "a0_modular_anomaly_benchmark_m_s2"
    ]

    rows = []
    for scenario in z6_scenarios():
        candidate = Candidate(
            name=scenario["name"],
            reserve_fraction=scenario["reserve_fraction"],
            source=scenario["law"],
            status=scenario["status"],
        )
        row = evaluate_candidate(
            candidate,
            a0_oph,
            rar_rows,
            bin_rows,
            mass_rows,
            args.upsilon_disk,
            args.upsilon_bulge,
        )
        row["law"] = scenario["law"]
        rows.append(row)

    return {
        "status": {
            "category": "conditional Z6 shared-edge reserve law",
            "claim": "Poisson thinning follows if a physical order-six reserve occupies the independent activation-count layer",
            "branch_inputs": [
                "ellbar_shared = P/4",
                "a physical Z6 quotient from trace-balanced block integration, tensor-kernel triviality, and axis-center descent",
                "the MAR-selected matter and Higgs action is trivial on that kernel",
            ],
            "open_bridge": (
                "promote the premise that protected quotient-center edge "
                "capacity occupies the same independent local opportunity "
                "layer as the scalar activation count"
            ),
        },
        "inputs": {
            "N_scr": args.n_scr,
            "a0_OPH_m_s2": a0_oph,
            "P_pixel": P_PIXEL,
            "Z6_order": Z6_ORDER,
            "ellbar_shared_P_over_4": ELLBAR_SHARED,
            "epsilon_Z6_P_over_24": EPSILON_Z6,
            "rar_rows": len(rar_rows),
            "rar_bin_rows": len(bin_rows),
            "mass_model_rows": len(mass_rows),
        },
        "branch_gap": {
            "poisson_minus_linear": math.exp(-EPSILON_Z6) - (1.0 - EPSILON_Z6),
            "quadratic_upper_bound": 0.5 * EPSILON_Z6 * EPSILON_Z6,
        },
        "scenarios": rows,
    }


def print_markdown(payload: dict[str, Any]) -> None:
    print("# Z6 Shared-Edge Reserve")
    print()
    print(payload["status"]["claim"])
    print()
    print("Branch inputs:")
    for item in payload["status"]["branch_inputs"]:
        print(f"- {item}")
    print()
    print(f"P: `{payload['inputs']['P_pixel']:.15f}`")
    print(f"ellbar_shared=P/4: `{payload['inputs']['ellbar_shared_P_over_4']:.12f}`")
    print(f"epsilon_Z6=P/24: `{payload['inputs']['epsilon_Z6_P_over_24']:.12f}`")
    print(
        "Poisson-linear gap: "
        f"`{payload['branch_gap']['poisson_minus_linear']:.12f}` "
        "with quadratic bound "
        f"`{payload['branch_gap']['quadratic_upper_bound']:.12f}`"
    )
    print()
    print(
        "| Scenario | law | lambda | C_response | a0_eff | "
        "RAR RMS dex | binned RMS | rot RMS km/s |"
    )
    print("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["scenarios"]:
        print(
            f"| {row['name']} | `{row['law']}` | {row['lambda_collar']:.6f} | "
            f"{row['C_response']:.6f} | {row['a0_eff_m_s2']:.9e} | "
            f"{row['rar_all_rms_dex']:.6f} | "
            f"{row['rar_binned_weighted_rms_dex']:.6f} | "
            f"{row['rotation_rms_km_s']:.6f} |"
        )
    print()
    print(f"Paper-grade condition: {payload['status']['open_bridge']}.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=3.31e122)
    parser.add_argument("--rar-all", type=Path, default=DEFAULT_RAR_ALL)
    parser.add_argument("--rar-bins", type=Path, default=DEFAULT_RAR_BINS)
    parser.add_argument("--mass-models", type=Path, default=DEFAULT_MASS_MODELS)
    parser.add_argument("--upsilon-disk", type=float, default=0.5)
    parser.add_argument("--upsilon-bulge", type=float, default=0.7)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = compute(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_markdown(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
