#!/usr/bin/env python3
"""Construct a finite OPH dark-branch repair transition matrix."""

from __future__ import annotations

import argparse
import json
import math
from typing import Any

import numpy as np


def truncated_poisson(mu: float, n_max: int) -> np.ndarray:
    weights = np.array(
        [math.exp(-mu + n * math.log(mu) - math.lgamma(n + 1)) for n in range(n_max + 1)],
        dtype=float,
    )
    return weights / weights.sum()


def nearest_neighbor_metropolis(pi: np.ndarray, hold: float) -> np.ndarray:
    n_state = len(pi)
    matrix = np.zeros((n_state, n_state), dtype=float)
    for state in range(n_state):
        proposals: list[tuple[int, float]] = []
        if state > 0:
            proposals.append((state - 1, (1.0 - hold) / 2.0))
        else:
            matrix[state, state] += (1.0 - hold) / 2.0
        if state + 1 < n_state:
            proposals.append((state + 1, (1.0 - hold) / 2.0))
        else:
            matrix[state, state] += (1.0 - hold) / 2.0
        matrix[state, state] += hold
        for target, proposal_prob in proposals:
            accept = min(1.0, pi[target] / pi[state])
            matrix[state, target] += proposal_prob * accept
            matrix[state, state] += proposal_prob * (1.0 - accept)
    return matrix


def spectral_gap(matrix: np.ndarray) -> dict[str, float]:
    eigenvalues = np.linalg.eigvals(matrix)
    real_values = sorted((float(ev.real) for ev in eigenvalues), reverse=True)
    nontrivial_abs = sorted(
        (abs(complex(ev)) for ev in eigenvalues if abs(complex(ev) - 1.0) > 1e-10),
        reverse=True,
    )
    lambda_two_abs = float(nontrivial_abs[0]) if nontrivial_abs else 0.0
    return {
        "lambda_1": real_values[0],
        "lambda_2_abs": lambda_two_abs,
        "gamma_rec": 1.0 - lambda_two_abs,
    }


def compute(args: argparse.Namespace) -> dict[str, Any]:
    pi = truncated_poisson(args.mu_eq, args.n_max)
    matrix = nearest_neighbor_metropolis(pi, args.hold)
    gap = spectral_gap(matrix)
    stationary_mean = float(sum(index * value for index, value in enumerate(pi)))
    stationary_var = float(
        sum((index - stationary_mean) ** 2 * value for index, value in enumerate(pi))
    )
    target_tau = [0.3, 0.5, 1.0]
    return {
        "status": {
            "category": "finite repair transition-matrix diagnostic",
            "public_promotion_allowed": False,
            "mu_eq_role": "explicit_or_caller_derived_input",
        },
        "inputs": {
            "mu_eq": args.mu_eq,
            "n_max": args.n_max,
            "hold": args.hold,
        },
        "stationary_distribution": {
            "mean": stationary_mean,
            "variance": stationary_var,
            "tail_at_n_max": float(pi[-1]),
        },
        "matrix_checks": {
            "row_sum_max_error": float(np.max(np.abs(matrix.sum(axis=1) - 1.0))),
            "detailed_balance_max_error": float(
                np.max(np.abs(pi[:, None] * matrix - pi[None, :] * matrix.T))
            ),
        },
        "gap": gap,
        "timescale": {
            "tau_rec_over_t_commit": 1.0 / gap["gamma_rec"],
            "t_commit_gyr_needed": {
                f"tau_{tau:g}_gyr": tau * gap["gamma_rec"] for tau in target_tau
            },
        },
    }


def print_markdown(payload: dict[str, Any]) -> None:
    inputs = payload["inputs"]
    stat = payload["stationary_distribution"]
    checks = payload["matrix_checks"]
    gap = payload["gap"]
    timescale = payload["timescale"]
    print("# Dark Repair Transition Matrix")
    print()
    print("| Quantity | Value |")
    print("| --- | ---: |")
    print(f"| mu_eq | `{inputs['mu_eq']:.9f}` |")
    print(f"| n_max | `{inputs['n_max']}` |")
    print(f"| hold probability | `{inputs['hold']:.6f}` |")
    print(f"| stationary mean | `{stat['mean']:.9f}` |")
    print(f"| stationary variance | `{stat['variance']:.9f}` |")
    print(f"| tail at n_max | `{stat['tail_at_n_max']:.9e}` |")
    print(f"| row-sum max error | `{checks['row_sum_max_error']:.3e}` |")
    print(f"| detailed-balance max error | `{checks['detailed_balance_max_error']:.3e}` |")
    print(f"| lambda_2 abs | `{gap['lambda_2_abs']:.9f}` |")
    print(f"| gamma_rec | `{gap['gamma_rec']:.9f}` |")
    print(f"| tau_rec / t_commit | `{timescale['tau_rec_over_t_commit']:.6f}` |")
    print()
    print("## Commit-Time Targets")
    print()
    print("| target tau_rec | required t_commit |")
    print("| --- | ---: |")
    for label, value in timescale["t_commit_gyr_needed"].items():
        tau = label.removeprefix("tau_").removesuffix("_gyr")
        print(f"| `{tau} Gyr` | `{value:.9f} Gyr` |")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mu-eq",
        type=float,
        required=True,
        help="Explicit repair-distribution mean; no legacy cosmology ratio is implicit.",
    )
    parser.add_argument("--n-max", type=int, default=40)
    parser.add_argument("--hold", type=float, default=0.25)
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
