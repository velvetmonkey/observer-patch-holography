#!/usr/bin/env python3
"""Compute OPH D6 de Sitter capacity quantities.

This script intentionally uses only the Python standard library. It is a
starter calculator for the root-level cosmology workspace, not a paper build
tool.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Any


C = 299_792_458.0
G = 6.67430e-11
HBAR = 1.054_571_817e-34
K_B = 1.380_649e-23
L_P = math.sqrt(HBAR * G / C**3)

DEFAULT_N_SCR = 3.31e122

MINIMAL_NORMAL_REFERENCE_SUM_MNU_EV = 0.0589

REJECTED_WEIGHTED_CYCLE_MASSES_EV = (
    0.017454720257976796,
    0.019481987935919015,
    0.05307522145074924,
)
REJECTED_WEIGHTED_CYCLE_SUM_MNU_EV = sum(REJECTED_WEIGHTED_CYCLE_MASSES_EV)

# Cosmology needs a supplied neutrino background even though OPH currently emits
# no physical neutrino masses.  Use a conventional external reference by default;
# the historical weighted-cycle tuple is retained only as an anti-promotion
# comparison record.
DEFAULT_COSMOLOGY_SUM_MNU_EV = MINIMAL_NORMAL_REFERENCE_SUM_MNU_EV

NEUTRINO_BOUNDS_95_EV = {
    "Planck2018_BAO_LambdaCDM": 0.12,
    "DESI_DR1_CMB_LambdaCDM_positive_prior": 0.072,
    "DESI_DR1_CMB_LambdaCDM_minimum_mass_prior": 0.113,
    "DESI_DR2_CMB_LambdaCDM": 0.064,
    "DESI_DR2_CMB_w0wa": 0.16,
    "ACT_DR6_extended": 0.082,
}


def neutrino_mass_input_provenance(sum_mnu_eV: float) -> dict[str, Any]:
    """Classify a supplied cosmological neutrino mass without promoting it."""

    if math.isclose(
        sum_mnu_eV,
        REJECTED_WEIGHTED_CYCLE_SUM_MNU_EV,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        return {
            "status": "rejected_target_informed_weighted_cycle_compare_only",
            "role": "legacy_comparison_diagnostic",
            "sum_mnu_eV": sum_mnu_eV,
            "oph_prediction": False,
            "source_closed_oph_input": False,
            "rejected_candidate": True,
            "public_promotion_allowed": False,
            "promotion_blocker": (
                "The weighted-cycle point is target-informed, source-open, basis-open, "
                "and rejected by the NuFIT 6.1 correlated profile."
            ),
        }
    if math.isclose(
        sum_mnu_eV,
        MINIMAL_NORMAL_REFERENCE_SUM_MNU_EV,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        status = "external_minimal_normal_reference"
    else:
        status = "external_user_supplied_neutrino_mass_input"
    return {
        "status": status,
        "role": "external_cosmology_background_input",
        "sum_mnu_eV": sum_mnu_eV,
        "oph_prediction": False,
        "source_closed_oph_input": False,
        "rejected_candidate": False,
        "public_promotion_allowed": False,
        "promotion_blocker": "OPH currently emits no source-closed physical neutrino mass sum.",
    }


def compute(n_scr: float) -> dict[str, Any]:
    lambda_si = 3.0 * math.pi / (n_scr * L_P**2)
    lambda_lp2 = lambda_si * L_P**2
    r_ds_m = math.sqrt(3.0 / lambda_si)
    h_ds_s_inv = C / r_ds_m
    t_lambda_s = r_ds_m / C
    temp_k = HBAR * h_ds_s_inv / (2.0 * math.pi * K_B)
    area_m2 = 4.0 * L_P**2 * n_scr
    n_patch = n_scr / math.pi
    bits = n_scr / math.log(2.0)
    scrambling_time_s = t_lambda_s * math.log(n_scr)
    d12_a0_benchmark = (15.0 / (8.0 * math.pi**2)) * (C**2 / r_ds_m)

    sum_mnu = REJECTED_WEIGHTED_CYCLE_SUM_MNU_EV
    neutrino_comparison = {
        name: {
            "upper_95_eV": bound,
            "candidate_sum_eV": sum_mnu,
            "within_bound": sum_mnu < bound,
            "margin_eV": bound - sum_mnu,
        }
        for name, bound in NEUTRINO_BOUNDS_95_EV.items()
    }

    return {
        "inputs": {
            "N_scr": n_scr,
            "constants": {
                "c_m_s": C,
                "G_m3_kg_s2": G,
                "hbar_J_s": HBAR,
                "k_B_J_K": K_B,
                "l_P_m": L_P,
            },
        },
        "d6_capacity_outputs": {
            "Lambda_m_inv2": lambda_si,
            "Lambda_lP2": lambda_lp2,
            "N_patch": n_patch,
            "S_dS_nats": n_scr,
            "S_dS_bits": bits,
            "A_dS_m2": area_m2,
            "r_dS_m": r_ds_m,
            "H_dS_s_inv": h_ds_s_inv,
            "H_dS_km_s_Mpc": h_ds_s_inv * 3.085_677_581_491_3673e19,
            "t_Lambda_s": t_lambda_s,
            "t_Lambda_Gyr": t_lambda_s / (365.25 * 24.0 * 3600.0 * 1.0e9),
            "T_dS_K": temp_k,
            "scrambling_time_s_approx": scrambling_time_s,
            "scrambling_time_Tyr_approx": scrambling_time_s
            / (365.25 * 24.0 * 3600.0 * 1.0e12),
        },
        "d12_benchmarks_not_theorem_outputs": {
            "a0_modular_anomaly_benchmark_m_s2": d12_a0_benchmark,
            "formula": "(15 / (8 pi^2)) * c^2 / r_dS",
        },
        "neutrino_mass_input_policy": {
            "default_sum_mnu_eV": DEFAULT_COSMOLOGY_SUM_MNU_EV,
            "default_provenance": neutrino_mass_input_provenance(
                DEFAULT_COSMOLOGY_SUM_MNU_EV
            ),
            "oph_neutrino_prediction_available": False,
        },
        "rejected_weighted_cycle_neutrino_comparison": {
            "provenance": neutrino_mass_input_provenance(sum_mnu),
            "mass_eigenvalues_eV": list(REJECTED_WEIGHTED_CYCLE_MASSES_EV),
            "sum_mnu_eV": sum_mnu,
            "bounds_95_comparison": neutrino_comparison,
        },
    }


def print_human(payload: dict[str, Any]) -> None:
    d6 = payload["d6_capacity_outputs"]
    bench = payload["d12_benchmarks_not_theorem_outputs"]
    nu = payload["rejected_weighted_cycle_neutrino_comparison"]

    print("OPH D6 capacity calculator")
    print(f"N_scr: {payload['inputs']['N_scr']:.6e}")
    print(f"Lambda l_P^2: {d6['Lambda_lP2']:.6e}")
    print(f"Lambda: {d6['Lambda_m_inv2']:.6e} m^-2")
    print(f"N_patch: {d6['N_patch']:.6e}")
    print(f"S_dS bits: {d6['S_dS_bits']:.6e}")
    print(f"r_dS: {d6['r_dS_m']:.6e} m")
    print(f"H_dS: {d6['H_dS_s_inv']:.6e} s^-1")
    print(f"H_dS: {d6['H_dS_km_s_Mpc']:.6f} km/s/Mpc")
    print(f"t_Lambda: {d6['t_Lambda_Gyr']:.6f} Gyr")
    print(f"T_dS: {d6['T_dS_K']:.6e} K")
    print(
        "scrambling time approx: "
        f"{d6['scrambling_time_Tyr_approx']:.6f} trillion years"
    )
    print()
    print("D12 benchmark, not a theorem output")
    print(f"a0 benchmark: {bench['a0_modular_anomaly_benchmark_m_s2']:.6e} m/s^2")
    print()
    print("Rejected weighted-cycle neutrino comparison (not an OPH prediction)")
    print(f"status: {nu['provenance']['status']}")
    print(f"sum m_nu: {nu['sum_mnu_eV']:.15f} eV")
    for name, row in nu["bounds_95_comparison"].items():
        status = "within" if row["within_bound"] else "above"
        print(
            f"{name}: {status} 95% bound "
            f"({row['upper_95_eV']:.3f} eV, margin {row['margin_eV']:.6f} eV)"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--n-scr",
        type=float,
        default=DEFAULT_N_SCR,
        help="Dimensionless de Sitter entropy capacity. Default: paper benchmark.",
    )
    parser.add_argument(
        "--lambda-lp2",
        type=float,
        default=None,
        help="Alternative input Lambda*l_P^2. If supplied, it determines N_scr.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    n_scr = args.n_scr
    if args.lambda_lp2 is not None:
        n_scr = 3.0 * math.pi / args.lambda_lp2

    payload = compute(n_scr)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
