#!/usr/bin/env python3
"""Compute the homogeneous OPH anomaly charge from a flat capacity-saturated branch."""

from __future__ import annotations

import argparse
import json
import math
from typing import Any

from d6_capacity_calculator import (
    DEFAULT_COSMOLOGY_SUM_MNU_EV,
    DEFAULT_N_SCR,
    G,
    compute as compute_d6,
    neutrino_mass_input_provenance,
)


MPC_M = 3.085_677_581_491_3673e22
OMEGA_NU_H2_DENOMINATOR_EV = 93.14


def compute(args: argparse.Namespace) -> dict[str, Any]:
    d6 = compute_d6(args.n_scr)["d6_capacity_outputs"]
    h0_s_inv = args.H0_km_s_Mpc * 1000.0 / MPC_M
    h = args.H0_km_s_Mpc / 100.0
    omega_lambda = (d6["H_dS_km_s_Mpc"] / args.H0_km_s_Mpc) ** 2
    omega_b = args.ombh2 / (h * h)
    sum_mnu = args.sum_mnu_eV
    neutrino_provenance = neutrino_mass_input_provenance(sum_mnu)
    omega_nu_h2 = sum_mnu / OMEGA_NU_H2_DENOMINATOR_EV
    omega_nu = omega_nu_h2 / (h * h)
    omega_anomaly = 1.0 - omega_lambda - omega_b - omega_nu - args.omega_r
    rho_crit = 3.0 * h0_s_inv**2 / (8.0 * math.pi * G)
    rho_lambda = omega_lambda * rho_crit
    rho_b = omega_b * rho_crit
    rho_nu = omega_nu * rho_crit
    rho_r = args.omega_r * rho_crit
    rho_anomaly = omega_anomaly * rho_crit
    return {
        "status": {
            "category": "flat capacity-saturated homogeneous anomaly diagnostic",
            "paper_grade": False,
            "public_promotion_allowed": False,
            "named_premise": "flat capacity-saturated FLRW state selection",
            "neutrino_input_status": neutrino_provenance["status"],
            "notes": [
                "The formula is a Hamiltonian-constraint residual after H0, baryon density, neutrino mass, radiation, flatness, and the capacity Lambda are supplied.",
                "It is not selected by the static galaxy RAR law.",
                "The supplied neutrino mass is not an OPH neutrino prediction.",
            ],
        },
        "inputs": {
            "N_scr": args.n_scr,
            "H0_km_s_Mpc": args.H0_km_s_Mpc,
            "h": h,
            "ombh2": args.ombh2,
            "sum_mnu_eV": sum_mnu,
            "neutrino_mass_input_provenance": neutrino_provenance,
            "omega_nu_h2": omega_nu_h2,
            "Omega_r": args.omega_r,
        },
        "capacity": {
            "H_dS_km_s_Mpc": d6["H_dS_km_s_Mpc"],
            "Lambda_m_inv2": d6["Lambda_m_inv2"],
            "r_dS_m": d6["r_dS_m"],
        },
        "density_fractions": {
            "Omega_Lambda_OPH": omega_lambda,
            "Omega_b": omega_b,
            "Omega_nu": omega_nu,
            "Omega_r": args.omega_r,
            "Omega_A": omega_anomaly,
            "Omega_m_total": omega_b + omega_nu + omega_anomaly,
        },
        "densities_kg_m3": {
            "rho_crit_0": rho_crit,
            "rho_Lambda": rho_lambda,
            "rho_b0": rho_b,
            "rho_nu0": rho_nu,
            "rho_r0": rho_r,
            "rho_A0": rho_anomaly,
        },
    }


def print_markdown(payload: dict[str, Any]) -> None:
    fractions = payload["density_fractions"]
    densities = payload["densities_kg_m3"]
    capacity = payload["capacity"]
    print("# Homogeneous OPH Anomaly State Selection")
    print()
    print(
        "Neutrino input status: "
        f"`{payload['inputs']['neutrino_mass_input_provenance']['status']}`."
    )
    print()
    print("| Quantity | Value |")
    print("| --- | ---: |")
    print(f"| H_dS | `{capacity['H_dS_km_s_Mpc']:.9f} km/s/Mpc` |")
    print(f"| Omega_Lambda_OPH | `{fractions['Omega_Lambda_OPH']:.9f}` |")
    print(f"| Omega_b | `{fractions['Omega_b']:.9f}` |")
    print(f"| Omega_nu | `{fractions['Omega_nu']:.9f}` |")
    print(f"| Omega_r | `{fractions['Omega_r']:.9f}` |")
    print(f"| Omega_A residual | `{fractions['Omega_A']:.9f}` |")
    print(f"| Omega_m total | `{fractions['Omega_m_total']:.9f}` |")
    print(f"| rho_crit_0 | `{densities['rho_crit_0']:.9e} kg/m^3` |")
    print(f"| rho_A0 | `{densities['rho_A0']:.9e} kg/m^3` |")
    print()
    print("The homogeneous branch is `rho_A(a) = rho_A0 a^-3` under transported dust and no homogeneous repair exchange.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=DEFAULT_N_SCR)
    parser.add_argument("--H0-km-s-Mpc", type=float, default=67.4)
    parser.add_argument("--ombh2", type=float, default=0.02237)
    parser.add_argument(
        "--sum-mnu-eV",
        type=float,
        default=DEFAULT_COSMOLOGY_SUM_MNU_EV,
        help=(
            "Externally supplied neutrino mass sum. The default is the minimal-normal "
            "reference, not an OPH prediction."
        ),
    )
    parser.add_argument("--omega-r", type=float, default=9.17e-5)
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
