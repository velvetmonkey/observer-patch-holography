#!/usr/bin/env python3
"""Run CAMB comparisons across explicitly labeled neutrino-mass scenarios.

This is the first Boltzmann-code comparison surface in the OPH cosmology
workspace. It holds a simple Planck-like flat FLRW background fixed and compares
linear spectra across neutrino-mass branches. It is not a likelihood analysis.

Run without installing into the repo:

    uv run --with camb python cosmology/scripts/camb_fixed_neutrino_compare.py
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from typing import Any

from d6_capacity_calculator import (
    MINIMAL_NORMAL_REFERENCE_SUM_MNU_EV,
    REJECTED_WEIGHTED_CYCLE_MASSES_EV,
    REJECTED_WEIGHTED_CYCLE_SUM_MNU_EV,
)


OMEGA_NU_H2_DENOMINATOR_EV = 93.14


@dataclass(frozen=True)
class BoltzmannBackground:
    name: str = "planck2018_fixed_total_omega_m"
    H0_km_s_Mpc: float = 67.4
    Omega_m: float = 0.315
    ombh2: float = 0.02237
    omk: float = 0.0
    tau: float = 0.0544
    As: float = 2.1e-9
    ns: float = 0.965
    nnu: float = 3.044


@dataclass(frozen=True)
class NeutrinoScenario:
    name: str
    sum_mnu_eV: float
    hierarchy: str
    num_massive_neutrinos: int
    exact_masses_eV: tuple[float, ...] | None = None
    scientific_status: str = "external_reference_comparison"
    oph_prediction: bool = False
    public_promotion_allowed: bool = False
    source_artifact: str | None = None


SCENARIOS = [
    NeutrinoScenario(
        name="massless_reference",
        sum_mnu_eV=0.0,
        hierarchy="degenerate",
        num_massive_neutrinos=0,
    ),
    NeutrinoScenario(
        name="minimal_normal_reference",
        sum_mnu_eV=MINIMAL_NORMAL_REFERENCE_SUM_MNU_EV,
        hierarchy="normal",
        num_massive_neutrinos=3,
    ),
    NeutrinoScenario(
        name="desi_dr2_lcdm_95_bound",
        sum_mnu_eV=0.064,
        hierarchy="normal",
        num_massive_neutrinos=3,
    ),
    NeutrinoScenario(
        name="rejected_weighted_cycle_compare_only",
        sum_mnu_eV=REJECTED_WEIGHTED_CYCLE_SUM_MNU_EV,
        hierarchy="normal",
        num_massive_neutrinos=3,
        exact_masses_eV=REJECTED_WEIGHTED_CYCLE_MASSES_EV,
        scientific_status="rejected_target_informed_compare_only",
        source_artifact="code/particles/runs/neutrino/neutrino_weighted_cycle_repair.json",
    ),
]


def import_camb() -> tuple[Any, Any]:
    try:
        import camb  # type: ignore
        import numpy as np  # type: ignore
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "CAMB is not installed in this Python environment. Run with:\n"
            "  uv run --with camb python "
            "cosmology/scripts/camb_fixed_neutrino_compare.py\n"
            "or install optional dependencies from "
            "cosmology/requirements-boltzmann.txt"
        ) from exc
    return camb, np


def omega_nu_h2(sum_mnu_eV: float) -> float:
    return sum_mnu_eV / OMEGA_NU_H2_DENOMINATOR_EV


def omega_c_h2(background: BoltzmannBackground, sum_mnu_eV: float) -> float:
    h = background.H0_km_s_Mpc / 100.0
    total_matter_h2 = background.Omega_m * h * h
    omch2 = total_matter_h2 - background.ombh2 - omega_nu_h2(sum_mnu_eV)
    if omch2 <= 0.0:
        raise ValueError(f"Nonpositive omch2 for sum_mnu={sum_mnu_eV}")
    return omch2


def log_interp(np: Any, x: float, xs: Any, ys: Any) -> float:
    return float(math.exp(np.interp(math.log(x), np.log(xs), np.log(ys))))


def run_scenario(
    camb: Any,
    np: Any,
    background: BoltzmannBackground,
    scenario: NeutrinoScenario,
    *,
    kmax: float,
    lmax: int,
    k_samples: list[float],
    ell_samples: list[int],
) -> dict[str, Any]:
    pars = camb.CAMBparams()
    pars.set_cosmology(
        H0=background.H0_km_s_Mpc,
        ombh2=background.ombh2,
        omch2=omega_c_h2(background, scenario.sum_mnu_eV),
        omk=background.omk,
        tau=background.tau,
        mnu=scenario.sum_mnu_eV,
        nnu=background.nnu,
        neutrino_hierarchy=scenario.hierarchy,
        num_massive_neutrinos=scenario.num_massive_neutrinos,
    )
    if scenario.exact_masses_eV:
        total = sum(scenario.exact_masses_eV)
        pars.nu_mass_eigenstates = len(scenario.exact_masses_eV)
        for index, mass in enumerate(scenario.exact_masses_eV):
            pars.nu_mass_numbers[index] = 1
            pars.nu_mass_fractions[index] = mass / total
            pars.nu_mass_degeneracies[index] = background.nnu / len(
                scenario.exact_masses_eV
            )
    pars.InitPower.set_params(As=background.As, ns=background.ns)
    pars.set_matter_power(redshifts=[0.0], kmax=kmax)
    pars.set_for_lmax(lmax, lens_potential_accuracy=1)

    results = camb.get_results(pars)
    kh, z_values, pk_values = results.get_matter_power_spectrum(
        minkh=1.0e-3, maxkh=kmax, npoints=240
    )
    pk_z0 = pk_values[0]
    powers = results.get_cmb_power_spectra(pars, CMB_unit="muK")
    tt = powers["total"][:, 0]
    sigma8_values = results.get_sigma8()
    sigma8_z0 = float(sigma8_values[-1])
    s8 = sigma8_z0 * math.sqrt(background.Omega_m / 0.3)

    matter_samples = {
        f"k_hMpc_{k:g}": log_interp(np, k, kh, pk_z0)
        for k in k_samples
        if k <= kmax
    }
    tt_samples = {
        f"ell_{ell}": float(tt[ell])
        for ell in ell_samples
        if ell < len(tt)
    }
    h = background.H0_km_s_Mpc / 100.0
    omega_nu = omega_nu_h2(scenario.sum_mnu_eV) / (h * h)
    f_nu = omega_nu / background.Omega_m if background.Omega_m else 0.0

    return {
        "scenario": asdict(scenario),
        "derived_parameters": {
            "omch2_adjusted_to_keep_total_Omega_m_fixed": omega_c_h2(
                background, scenario.sum_mnu_eV
            ),
            "omega_nu_h2_approx": omega_nu_h2(scenario.sum_mnu_eV),
            "Omega_nu_approx": omega_nu,
            "f_nu_approx": f_nu,
            "sigma8_z0": sigma8_z0,
            "S8_z0": s8,
            "returned_matter_redshifts": [float(z) for z in z_values],
        },
        "matter_power_z0_Mpc3_samples": matter_samples,
        "cmb_total_TT_Dell_uK2_samples": tt_samples,
    }


def add_ratios(payload: dict[str, Any], reference_name: str) -> None:
    scenarios = payload["scenarios"]
    reference = next(
        row for row in scenarios if row["scenario"]["name"] == reference_name
    )
    ref_sigma8 = reference["derived_parameters"]["sigma8_z0"]
    ref_s8 = reference["derived_parameters"]["S8_z0"]
    ref_pk = reference["matter_power_z0_Mpc3_samples"]
    ref_tt = reference["cmb_total_TT_Dell_uK2_samples"]

    for row in scenarios:
        ratios: dict[str, Any] = {
            "reference": reference_name,
            "delta_sigma8_over_reference": (
                row["derived_parameters"]["sigma8_z0"] / ref_sigma8 - 1.0
            ),
            "delta_S8_over_reference": (
                row["derived_parameters"]["S8_z0"] / ref_s8 - 1.0
            ),
            "matter_power_delta_over_reference": {},
            "TT_Dell_delta_over_reference": {},
        }
        for key, value in row["matter_power_z0_Mpc3_samples"].items():
            ratios["matter_power_delta_over_reference"][key] = value / ref_pk[key] - 1.0
        for key, value in row["cmb_total_TT_Dell_uK2_samples"].items():
            ratios["TT_Dell_delta_over_reference"][key] = value / ref_tt[key] - 1.0
        row["ratios"] = ratios


def compute(args: argparse.Namespace) -> dict[str, Any]:
    camb, np = import_camb()
    background = BoltzmannBackground(
        H0_km_s_Mpc=args.H0,
        Omega_m=args.omega_m,
        ombh2=args.ombh2,
        tau=args.tau,
        As=args.As,
        ns=args.ns,
    )
    k_samples = [float(item) for item in args.k_samples.split(",") if item]
    ell_samples = [int(item) for item in args.ell_samples.split(",") if item]
    rows = [
        run_scenario(
            camb,
            np,
            background,
            scenario,
            kmax=args.kmax,
            lmax=args.lmax,
            k_samples=k_samples,
            ell_samples=ell_samples,
        )
        for scenario in SCENARIOS
    ]
    payload = {
        "status": {
            "category": "CAMB fixed-neutrino comparison, not a likelihood analysis",
            "camb_version": camb.__version__,
            "public_promotion_allowed": False,
            "rejected_weighted_cycle_comparison_included": True,
            "notes": [
                "CAMB normal hierarchy uses its built-in approximation from the total mass.",
                "CDM density is adjusted to keep total Omega_m fixed across mass branches.",
                "The rejected weighted-cycle row uses explicit mass fractions only as a legacy comparison diagnostic.",
                "No scenario in this comparison is an OPH neutrino prediction or a promotion surface.",
            ],
        },
        "background": asdict(background),
        "rejected_weighted_cycle_mass_eigenvalues_eV": list(
            REJECTED_WEIGHTED_CYCLE_MASSES_EV
        ),
        "scenarios": rows,
    }
    add_ratios(payload, args.reference)
    return payload


def print_markdown(payload: dict[str, Any]) -> None:
    print("# CAMB Fixed-Neutrino Comparison")
    print()
    status = payload["status"]
    print(f"CAMB version: `{status['camb_version']}`.")
    print(
        "Status: fixed-background Boltzmann comparison, not a cosmological "
        "likelihood analysis."
    )
    print()
    print("| Scenario | sum mnu eV | omch2 | f_nu | sigma8 | S8 | dS8 vs ref |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["scenarios"]:
        scenario = row["scenario"]
        derived = row["derived_parameters"]
        ratios = row["ratios"]
        print(
            f"| {scenario['name']} | {scenario['sum_mnu_eV']:.9f} | "
            f"{derived['omch2_adjusted_to_keep_total_Omega_m_fixed']:.8f} | "
            f"{derived['f_nu_approx']:.6f} | "
            f"{derived['sigma8_z0']:.6f} | {derived['S8_z0']:.6f} | "
            f"{100.0 * ratios['delta_S8_over_reference']:+.3f}% |"
        )

    print()
    print("Matter power change relative to reference:")
    keys = list(payload["scenarios"][0]["matter_power_z0_Mpc3_samples"].keys())
    print("| Scenario | " + " | ".join(keys) + " |")
    print("| --- | " + " | ".join(["---:"] * len(keys)) + " |")
    for row in payload["scenarios"]:
        ratios = row["ratios"]["matter_power_delta_over_reference"]
        values = [f"{100.0 * ratios[key]:+.3f}%" for key in keys]
        print(f"| {row['scenario']['name']} | " + " | ".join(values) + " |")

    print()
    print("CMB TT D_ell change relative to reference:")
    tt_keys = list(payload["scenarios"][0]["cmb_total_TT_Dell_uK2_samples"].keys())
    print("| Scenario | " + " | ".join(tt_keys) + " |")
    print("| --- | " + " | ".join(["---:"] * len(tt_keys)) + " |")
    for row in payload["scenarios"]:
        ratios = row["ratios"]["TT_Dell_delta_over_reference"]
        values = [f"{100.0 * ratios[key]:+.3f}%" for key in tt_keys]
        print(f"| {row['scenario']['name']} | " + " | ".join(values) + " |")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--H0", type=float, default=67.4)
    parser.add_argument("--omega-m", type=float, default=0.315)
    parser.add_argument("--ombh2", type=float, default=0.02237)
    parser.add_argument("--tau", type=float, default=0.0544)
    parser.add_argument("--As", type=float, default=2.1e-9)
    parser.add_argument("--ns", type=float, default=0.965)
    parser.add_argument("--kmax", type=float, default=2.0)
    parser.add_argument("--lmax", type=int, default=1600)
    parser.add_argument("--k-samples", default="0.01,0.05,0.1,0.2,0.5,1.0")
    parser.add_argument("--ell-samples", default="30,200,1000,1400")
    parser.add_argument("--reference", default="minimal_normal_reference")
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
