#!/usr/bin/env python3
"""Compressed CMB, BAO, growth, and S8 checks for an OPH dark parent grid."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from camb_fixed_neutrino_compare import OMEGA_NU_H2_DENOMINATOR_EV
from d6_capacity_calculator import (
    DEFAULT_COSMOLOGY_SUM_MNU_EV,
    neutrino_mass_input_provenance,
)


ROOT = Path(__file__).resolve().parents[1]
COMPARISONS_PATH = ROOT / "data" / "observational_comparisons.json"


def import_camb() -> Any:
    try:
        import camb  # type: ignore
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "CAMB is not installed. Run `python3 -m pip install --user camb`."
        ) from exc
    return camb


def load_comparisons() -> dict[str, Any]:
    with COMPARISONS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)["comparisons"]


def load_parent(path: str | None) -> dict[str, Any] | None:
    if path is None:
        return None
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def gaussian_row(name: str, prediction: float, central: float, sigma: float, source: str) -> dict[str, Any]:
    residual = prediction - central
    z_score = residual / sigma
    return {
        "name": name,
        "prediction": prediction,
        "central": central,
        "sigma": sigma,
        "residual": residual,
        "z": z_score,
        "chi2": z_score * z_score,
        "source": source,
    }


def omega_nu_h2(sum_mnu_eV: float) -> float:
    return sum_mnu_eV / OMEGA_NU_H2_DENOMINATOR_EV


def run_camb(
    *,
    H0: float,
    ombh2: float,
    omAh2: float,
    sum_mnu_eV: float,
    neutrino_hierarchy: str,
    tau: float,
    As: float,
    ns: float,
    lmax: int,
    kmax: float,
) -> dict[str, Any]:
    camb = import_camb()
    pars = camb.CAMBparams()
    pars.set_cosmology(
        H0=H0,
        ombh2=ombh2,
        omch2=omAh2,
        omk=0.0,
        tau=tau,
        mnu=sum_mnu_eV,
        nnu=3.044,
        neutrino_hierarchy=neutrino_hierarchy,
        num_massive_neutrinos=3 if sum_mnu_eV > 0.0 else 0,
    )
    pars.InitPower.set_params(As=As, ns=ns)
    pars.set_matter_power(redshifts=[0.0], kmax=kmax)
    pars.set_for_lmax(lmax, lens_potential_accuracy=1)
    results = camb.get_results(pars)
    sigma8 = float(results.get_sigma8()[-1])
    h = H0 / 100.0
    omega_m = (ombh2 + omAh2 + omega_nu_h2(sum_mnu_eV)) / (h * h)
    s8 = sigma8 * math.sqrt(omega_m / 0.3)
    powers = results.get_cmb_power_spectra(pars, CMB_unit="muK")
    tt = powers["total"][:, 0]
    return {
        "camb_version": camb.__version__,
        "Omega_m": omega_m,
        "sigma8": sigma8,
        "S8": s8,
        "TT_Dell_uK2": {
            "ell_30": float(tt[30]),
            "ell_200": float(tt[200]),
            "ell_1000": float(tt[1000]),
            "ell_1400": float(tt[1400]) if len(tt) > 1400 else None,
        },
    }


def blocked_payload(
    parent: dict[str, Any] | None,
    neutrino_provenance: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": {
            "category": "compressed dark-sector likelihood gate",
            "ready": False,
            "public_promotion_allowed": False,
            "reason": "finite-collar parent grid absent or incomplete",
            "required_fields": ["rho_A_over_rho_b", "B_A_grid"],
            "neutrino_input_status": neutrino_provenance["status"],
        },
        "neutrino_mass_input_provenance": neutrino_provenance,
        "parent_status": None if parent is None else parent.get("status", {}),
        "rows": [],
        "total_chi2": None,
    }


def compute(args: argparse.Namespace) -> dict[str, Any]:
    parent = load_parent(args.parent_grid)
    neutrino_provenance = neutrino_mass_input_provenance(args.sum_mnu_eV)
    if (
        parent is None
        or parent.get("rho_A_over_rho_b") is None
        or not parent.get("B_A_grid")
    ):
        return blocked_payload(parent, neutrino_provenance)

    comparisons = load_comparisons()
    planck = comparisons["planck_2018_vi"]
    desi = comparisons["desi_dr1_bao"]
    h = args.H0 / 100.0
    rho_ratio = float(parent["rho_A_over_rho_b"])
    omAh2 = args.ombh2 * rho_ratio
    neutrino_hierarchy = getattr(args, "neutrino_hierarchy", "normal")
    camb_payload = run_camb(
        H0=args.H0,
        ombh2=args.ombh2,
        omAh2=omAh2,
        sum_mnu_eV=args.sum_mnu_eV,
        neutrino_hierarchy=neutrino_hierarchy,
        tau=args.tau,
        As=args.As,
        ns=args.ns,
        lmax=args.lmax,
        kmax=args.kmax,
    )
    omega_m = camb_payload["Omega_m"]
    planck_s8 = planck["sigma8"]["central"] * math.sqrt(
        planck["Omega_m"]["central"] / 0.3
    )
    planck_s8_sigma = math.hypot(
        planck["sigma8"]["sigma"] * math.sqrt(planck["Omega_m"]["central"] / 0.3),
        0.5
        * planck["sigma8"]["central"]
        / math.sqrt(0.3 * planck["Omega_m"]["central"])
        * planck["Omega_m"]["sigma"],
    )

    rows = [
        gaussian_row(
            "Planck Omega_m",
            omega_m,
            planck["Omega_m"]["central"],
            planck["Omega_m"]["sigma"],
            "planck_2018_vi",
        ),
        gaussian_row(
            "Planck sigma8",
            camb_payload["sigma8"],
            planck["sigma8"]["central"],
            planck["sigma8"]["sigma"],
            "planck_2018_vi",
        ),
        gaussian_row(
            "Planck S8 derived compression",
            camb_payload["S8"],
            planck_s8,
            planck_s8_sigma,
            "planck_2018_vi",
        ),
        gaussian_row(
            "DESI DR1 BAO Omega_m",
            omega_m,
            desi["Omega_m_bao_only"]["central"],
            desi["Omega_m_bao_only"]["sigma"],
            "desi_dr1_bao",
        ),
        gaussian_row(
            "DESI DR1 BAO+BBN+theta H0",
            args.H0,
            desi["H0_with_BBN_theta_star_km_s_Mpc"]["central"],
            desi["H0_with_BBN_theta_star_km_s_Mpc"]["sigma"],
            "desi_dr1_bao",
        ),
    ]
    if args.weak_lensing_s8 is not None and args.weak_lensing_s8_sigma is not None:
        rows.append(
            gaussian_row(
                "weak-lensing S8",
                camb_payload["S8"],
                args.weak_lensing_s8,
                args.weak_lensing_s8_sigma,
                args.weak_lensing_source,
            )
        )

    return {
        "status": {
            "category": "compressed dark-sector CMB BAO growth S8 likelihood",
            "ready": True,
            "full_likelihood": False,
            "public_promotion_allowed": False,
            "covariances_ignored": True,
            "parent_paper_grade": bool(parent.get("status", {}).get("paper_grade", False)),
            "neutrino_input_status": neutrino_provenance["status"],
            "notes": [
                "The anomaly is passed to CAMB as a cold pressureless component.",
                "A scale-dependent B_A(k,a) requires a custom Boltzmann module.",
                "The diagonal Gaussian rows are compressed checks. Full Planck and DESI likelihood replacements require experimental covariances.",
                "The supplied neutrino mass is an external background input, not an OPH neutrino prediction.",
                *(
                    [
                        "This run uses the rejected weighted-cycle mass sum and is compare-only; every promotion gate is closed."
                    ]
                    if neutrino_provenance["rejected_candidate"]
                    else []
                ),
            ],
        },
        "inputs": {
            "H0": args.H0,
            "h": h,
            "ombh2": args.ombh2,
            "omAh2": omAh2,
            "rho_A_over_rho_b": rho_ratio,
            "sum_mnu_eV": args.sum_mnu_eV,
            "neutrino_hierarchy": neutrino_hierarchy,
            "neutrino_mass_input_provenance": neutrino_provenance,
            "tau": args.tau,
            "As": args.As,
            "ns": args.ns,
        },
        "parent_status": parent.get("status", {}),
        "boltzmann": camb_payload,
        "rows": rows,
        "total_chi2_diagonal": sum(row["chi2"] for row in rows),
        "dof_diagonal": len(rows),
    }


def print_markdown(payload: dict[str, Any]) -> None:
    status = payload["status"]
    print("# Dark CMB BAO Growth S8 Likelihood")
    print()
    print(f"Ready: `{status['ready']}`")
    if not status["ready"]:
        print(f"Reason: `{status['reason']}`")
        return
    print(f"Full likelihood: `{status['full_likelihood']}`")
    print(f"Parent paper grade: `{status['parent_paper_grade']}`")
    print(f"Neutrino input status: `{status['neutrino_input_status']}`")
    print(f"CAMB version: `{payload['boltzmann']['camb_version']}`")
    print()
    print("| Quantity | Prediction | Target | z | chi2 | Source |")
    print("| --- | ---: | ---: | ---: | ---: | --- |")
    for row in payload["rows"]:
        print(
            f"| {row['name']} | {row['prediction']:.9g} | "
            f"{row['central']:.9g} +/- {row['sigma']:.3g} | "
            f"{row['z']:+.3f} | {row['chi2']:.3f} | `{row['source']}` |"
        )
    print()
    print(
        f"Diagonal chi2: `{payload['total_chi2_diagonal']:.3f}` "
        f"for `{payload['dof_diagonal']}` compressed rows."
    )
    print()
    print("## Boltzmann Outputs")
    print()
    boltz = payload["boltzmann"]
    print(f"Omega_m: `{boltz['Omega_m']:.9f}`")
    print(f"sigma8: `{boltz['sigma8']:.9f}`")
    print(f"S8: `{boltz['S8']:.9f}`")
    print()
    print("CMB TT D_ell samples:")
    for key, value in boltz["TT_Dell_uK2"].items():
        if value is not None:
            print(f"- `{key}`: `{value:.9f}`")
    print()
    print("## Notes")
    print()
    for note in status.get("notes", []):
        print(f"- {note}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-grid", default=None)
    parser.add_argument("--H0", type=float, default=67.4)
    parser.add_argument("--ombh2", type=float, default=0.0224)
    parser.add_argument(
        "--sum-mnu-eV",
        type=float,
        default=DEFAULT_COSMOLOGY_SUM_MNU_EV,
        help=(
            "Externally supplied neutrino mass sum. The default is the minimal-normal "
            "reference, not an OPH prediction."
        ),
    )
    parser.add_argument(
        "--neutrino-hierarchy",
        choices=("normal", "inverted", "degenerate"),
        default="normal",
        help="CAMB hierarchy for the explicitly supplied neutrino mass input.",
    )
    parser.add_argument("--tau", type=float, default=0.0544)
    parser.add_argument("--As", type=float, default=2.1e-9)
    parser.add_argument("--ns", type=float, default=0.965)
    parser.add_argument("--lmax", type=int, default=1600)
    parser.add_argument("--kmax", type=float, default=2.0)
    parser.add_argument("--weak-lensing-s8", type=float, default=0.790)
    parser.add_argument("--weak-lensing-s8-sigma", type=float, default=0.016)
    parser.add_argument(
        "--weak-lensing-source",
        default="DES_Y3_KiDS_1000_joint_cosmic_shear_compressed",
    )
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
