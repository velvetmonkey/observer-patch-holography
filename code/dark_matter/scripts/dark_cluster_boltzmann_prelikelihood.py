#!/usr/bin/env python3
"""Carry OPH dark repair outputs into cluster and Boltzmann pre-likelihood tables."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import dark_perturbation_parameters
import dark_repair_transition_matrix


PLANCK_H = 0.674
DEFAULT_REFERENCE_OMEGA_B = 0.04924319136384048
DEFAULT_REFERENCE_OMEGA_A = 0.26484971204748087
DEFAULT_REFERENCE_OMEGA_LAMBDA = 0.6844233323779534
DEFAULT_REFERENCE_OMEGA_R = 9.17e-5
DEFAULT_REFERENCE_MU_EQ = DEFAULT_REFERENCE_OMEGA_A / DEFAULT_REFERENCE_OMEGA_B


def parse_csv_floats(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def load_parent_payload(path: str | None) -> dict[str, Any] | None:
    if path is None:
        return None
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def cluster_rows(
    gamma_rec: float,
    tau_values_gyr: list[float],
    separation_kpc: float,
    time_since_passage_gyr: float,
    observed_offset_kpc: float | None,
    offset_sigma_kpc: float | None,
) -> list[dict[str, float]]:
    rows = []
    for tau in tau_values_gyr:
        retained = math.exp(-time_since_passage_gyr / tau)
        model_offset = separation_kpc * retained
        row: dict[str, float] = {
            "tau_rec_Gyr": tau,
            "t_commit_Gyr_from_K": gamma_rec * tau,
            "retention_fraction": retained,
            "model_offset_kpc": model_offset,
        }
        if observed_offset_kpc is not None and offset_sigma_kpc is not None:
            z_score = (model_offset - observed_offset_kpc) / offset_sigma_kpc
            row["offset_z"] = z_score
            row["offset_chi2"] = z_score * z_score
        rows.append(row)
    return rows


def boltzmann_rows(
    tau_values_gyr: list[float],
    redshifts: list[float],
    omega_b: float,
    omega_anomaly: float,
    omega_lambda: float,
    omega_r: float,
    h0_km_s_mpc: float,
) -> list[dict[str, float]]:
    rows = []
    for tau in tau_values_gyr:
        payload = dark_perturbation_parameters.compute(
            omega_b=omega_b,
            omega_cdm_like_anomaly=omega_anomaly,
            tau_rec_gyr=tau,
            redshifts=redshifts,
            h0_km_s_mpc=h0_km_s_mpc,
            omega_lambda=omega_lambda,
            omega_r=omega_r,
        )
        for row in payload["rows"]:
            rows.append(
                {
                    "tau_rec_Gyr": tau,
                    "z": row["z"],
                    "a": row["a"],
                    "Gamma_over_H": row["Gamma_over_H"],
                    "H_Gyr_inv": row["H_Gyr_inv"],
                }
            )
    return rows


def parent_summary(parent_payload: dict[str, Any] | None, omega_b: float, omega_anomaly: float) -> dict[str, Any]:
    target_ratio = omega_anomaly / omega_b
    if parent_payload is None:
        return {
            "status": "finite-collar parent grid absent from run",
            "target_rho_A_over_rho_b": target_ratio,
            "rho_A_over_rho_b": None,
            "B_A_grid_points": 0,
        }
    kernel_grid = parent_payload.get("B_A_grid", [])
    return {
        "status": parent_payload.get("status", "finite-collar parent grid supplied"),
        "target_rho_A_over_rho_b": target_ratio,
        "rho_A_over_rho_b": parent_payload.get("rho_A_over_rho_b"),
        "B_A_grid_points": len(kernel_grid),
    }


def compute(args: argparse.Namespace) -> dict[str, Any]:
    repair_args = argparse.Namespace(mu_eq=args.mu_eq, n_max=args.n_max, hold=args.hold)
    repair_payload = dark_repair_transition_matrix.compute(repair_args)
    gamma_rec = repair_payload["gap"]["gamma_rec"]
    tau_values_gyr = parse_csv_floats(args.tau_values_gyr)
    redshifts = parse_csv_floats(args.redshifts)
    parent_payload = load_parent_payload(args.parent_collar_json)
    cluster = cluster_rows(
        gamma_rec=gamma_rec,
        tau_values_gyr=tau_values_gyr,
        separation_kpc=args.separation_kpc,
        time_since_passage_gyr=args.time_since_passage_gyr,
        observed_offset_kpc=args.observed_offset_kpc,
        offset_sigma_kpc=args.offset_sigma_kpc,
    )
    boltzmann = boltzmann_rows(
        tau_values_gyr=tau_values_gyr,
        redshifts=redshifts,
        omega_b=args.omega_b,
        omega_anomaly=args.omega_anomaly,
        omega_lambda=args.omega_lambda,
        omega_r=args.omega_r,
        h0_km_s_mpc=args.h0_km_s_mpc,
    )
    return {
        "status": {
            "category": "dark-sector cluster and Boltzmann pre-likelihood interface",
            "public_promotion_allowed": False,
            "default_background_status": "external_minimal_normal_neutrino_reference",
            "neutrino_input_status": getattr(
                args,
                "neutrino_input_status",
                "external_minimal_normal_reference",
            ),
            "cluster_likelihood_ready": args.observed_offset_kpc is not None
            and args.offset_sigma_kpc is not None,
            "boltzmann_likelihood_ready": parent_payload is not None
            and bool(parent_payload.get("B_A_grid")),
        },
        "repair_matrix": repair_payload,
        "parent_collar": parent_summary(parent_payload, args.omega_b, args.omega_anomaly),
        "cluster": {
            "inputs": {
                "separation_kpc": args.separation_kpc,
                "time_since_passage_Gyr": args.time_since_passage_gyr,
                "observed_offset_kpc": args.observed_offset_kpc,
                "offset_sigma_kpc": args.offset_sigma_kpc,
            },
            "rows": cluster,
        },
        "boltzmann_inputs": {
            "inputs": {
                "Omega_b": args.omega_b,
                "Omega_A": args.omega_anomaly,
                "Omega_Lambda": args.omega_lambda,
                "Omega_r": args.omega_r,
                "H0_km_s_Mpc": args.h0_km_s_mpc,
                "redshifts": redshifts,
            },
            "rows": boltzmann,
        },
    }


def print_markdown(payload: dict[str, Any]) -> None:
    repair = payload["repair_matrix"]
    parent = payload["parent_collar"]
    status = payload["status"]
    print("# Dark Cluster And Boltzmann Pre-Likelihood Interface")
    print()
    print("| Quantity | Value |")
    print("| --- | ---: |")
    print(f"| gamma_rec from K | `{repair['gap']['gamma_rec']:.9f}` |")
    print(f"| tau_rec / t_commit | `{repair['timescale']['tau_rec_over_t_commit']:.6f}` |")
    print(f"| parent grid status | `{parent['status']}` |")
    print(f"| target rho_A/rho_b | `{parent['target_rho_A_over_rho_b']:.9f}` |")
    if parent["rho_A_over_rho_b"] is None:
        print("| supplied rho_A/rho_b | `absent` |")
    else:
        print(f"| supplied rho_A/rho_b | `{parent['rho_A_over_rho_b']:.9f}` |")
    print(f"| B_A grid points | `{parent['B_A_grid_points']}` |")
    print(f"| cluster likelihood ready | `{status['cluster_likelihood_ready']}` |")
    print(f"| Boltzmann likelihood ready | `{status['boltzmann_likelihood_ready']}` |")
    print()
    print("## Cluster Timing")
    print()
    has_chi2 = any("offset_chi2" in row for row in payload["cluster"]["rows"])
    if has_chi2:
        print("| tau_rec Gyr | t_commit Myr | retained fraction | offset kpc | z | chi2 |")
        print("| ---: | ---: | ---: | ---: | ---: | ---: |")
    else:
        print("| tau_rec Gyr | t_commit Myr | retained fraction | offset kpc |")
        print("| ---: | ---: | ---: | ---: |")
    for row in payload["cluster"]["rows"]:
        cells = [
            f"{row['tau_rec_Gyr']:.6g}",
            f"{1000.0 * row['t_commit_Gyr_from_K']:.6g}",
            f"{row['retention_fraction']:.6g}",
            f"{row['model_offset_kpc']:.6g}",
        ]
        if has_chi2:
            cells.extend(
                [
                    f"{row.get('offset_z', float('nan')):.6g}",
                    f"{row.get('offset_chi2', float('nan')):.6g}",
                ]
            )
        print("| " + " | ".join(cells) + " |")
    print()
    print("## Boltzmann Inputs")
    print()
    print("| tau_rec Gyr | z | a | H Gyr^-1 | Gamma_rec/H |")
    print("| ---: | ---: | ---: | ---: | ---: |")
    for row in payload["boltzmann_inputs"]["rows"]:
        print(
            f"| {row['tau_rec_Gyr']:.6g} | {row['z']:.6g} | "
            f"{row['a']:.6g} | {row['H_Gyr_inv']:.6g} | "
            f"{row['Gamma_over_H']:.6g} |"
        )
    print()
    print(
        "Publication use requires a finite-collar parent grid for "
        "`rho_A(a)` and `B_A(k,a)`, plus measured cluster mass-map covariance "
        "and a CAMB or CLASS implementation."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mu-eq", type=float, default=DEFAULT_REFERENCE_MU_EQ)
    parser.add_argument("--n-max", type=int, default=40)
    parser.add_argument("--hold", type=float, default=0.25)
    parser.add_argument("--tau-values-gyr", default="0.3,0.5,1.0")
    parser.add_argument("--separation-kpc", type=float, default=200.0)
    parser.add_argument("--time-since-passage-gyr", type=float, default=0.2)
    parser.add_argument("--observed-offset-kpc", type=float, default=None)
    parser.add_argument("--offset-sigma-kpc", type=float, default=None)
    parser.add_argument("--omega-b", type=float, default=DEFAULT_REFERENCE_OMEGA_B)
    parser.add_argument("--omega-anomaly", type=float, default=DEFAULT_REFERENCE_OMEGA_A)
    parser.add_argument("--omega-lambda", type=float, default=DEFAULT_REFERENCE_OMEGA_LAMBDA)
    parser.add_argument("--omega-r", type=float, default=DEFAULT_REFERENCE_OMEGA_R)
    parser.add_argument("--h0-km-s-mpc", type=float, default=67.4)
    parser.add_argument("--redshifts", default="0,10,1100")
    parser.add_argument("--parent-collar-json", default=None)
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
