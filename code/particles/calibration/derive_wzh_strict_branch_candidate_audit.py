#!/usr/bin/env python3
"""Compute the strongest same-P W/Z/H formula-stack candidate, fail closed.

This audit deliberately distinguishes a reproducible candidate coordinate from
an actual source-only pole prediction. It uses the stored source-audit P and
clock-gap candidates, evaluates the canonical D10 conditional law on that
branch, and evaluates the declared D11 split. Missing carrier, clock, RG, and
BRST packets remain explicit blockers.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, getcontext
import json
import math
from pathlib import Path

try:
    from calibration.derive_d10_ew_observable_family import build_artifact as build_observable
    from calibration.derive_d10_ew_source_transport_pair import build_artifact as build_source_pair
    from calibration.derive_d10_ew_target_free_repair_value_law import (
        evaluate_candidate_from_source_basis,
    )
except ModuleNotFoundError:
    from derive_d10_ew_observable_family import build_artifact as build_observable
    from derive_d10_ew_source_transport_pair import build_artifact as build_source_pair
    from derive_d10_ew_target_free_repair_value_law import evaluate_candidate_from_source_basis


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "particles" / "hierarchy" / "certificates" / "R_P_source_audit_pixel_certificate.json"
CLOCK = ROOT / "particles" / "hierarchy" / "certificates" / "R_gamma_noG_DAG_certificate.json"
D11_SURFACE = ROOT / "particles" / "runs" / "calibration" / "d11_declared_calibration_surface.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "calibration" / "wzh_strict_branch_candidate_audit.json"

PLANCK_H = Decimal("6.62607015e-34")
CESIUM_HZ = Decimal("9192631770")
GEV_JOULE = Decimal("1.602176634e-10")
LEGACY_E_PLANCK_GEV = Decimal("1.220890e19")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(root: dict, clock: dict, d11_surface: dict) -> dict:
    getcontext().prec = 60
    p_value = float(root["P_cand"])
    observable = build_observable(p_value)
    source_pair = build_source_pair(observable)
    compact = source_pair["compact_hypercharge_only_mass_slice"]
    pair = source_pair["source_pair"]

    epsilon_cs = Decimal(clock["candidate_values_from_sources"]["epsilon_Cs"])
    e_star_gev = PLANCK_H * CESIUM_HZ / epsilon_cs / GEV_JOULE
    scale_factor = e_star_gev / LEGACY_E_PLANCK_GEV
    v_gev = float(Decimal(str(observable["core_source"]["v"])) * scale_factor)
    d10 = evaluate_candidate_from_source_basis(
        alpha_2=float(pair["alpha2_mz"]),
        alpha_y=float(pair["alphaY_mz"]),
        eta_source=float(compact["eta_EW"]),
        v_value=v_gev,
    )

    basis = d10["basis"]
    repair = d10["repair_chart"]
    core = d11_surface["core"]
    eta = float(basis["eta_source"])
    rho = float(basis["beta_EW"])
    lambda_ew = float(basis["lambda_EW"])
    tau2 = float(repair["tau2_tree_exact"])
    rho_ht = math.log1p(tau2)
    r_t = (
        -tau2 * eta**2
        + (1.0 + rho / 28.0) * eta**6
        + eta**8 / 14.0
        + eta**9 / 27.0
    )
    r_h = eta**5 - (3.0 / 25.0) * eta**6 + lambda_ew * eta**6 / 18.0 + eta**8 / (2.0 * rho)
    pi_y = (eta + (1.5 + rho / 4.0) * rho_ht + r_t) / math.sqrt(math.pi)
    pi_lambda = (eta - (4.0 / 3.0 - rho / 54.0) * rho_ht + r_h) / math.sqrt(math.pi)
    y_t = float(core["y_t_core_mt"]) * (1.0 + pi_y)
    lambda_h = float(core["lambda_core_mt"]) * (1.0 - (16.0 / 9.0) * pi_lambda)
    mt_running = v_gev * y_t / math.sqrt(2.0)
    mh_running = v_gev * math.sqrt(2.0 * lambda_h)

    w_mass = float(d10["coherent_emitted_quintet"]["MW_pole"])
    z_mass = float(d10["coherent_emitted_quintet"]["MZ_pole"])
    blockers = [
        "source_root_is_witness_not_interval_proof",
        "clock_R_alpha_missing",
        "clock_R_e_abs_missing",
        "clock_R_QCD_nuc_133Cs_missing",
        "clock_R_atom_133Cs_missing",
        "D10_QT1_QT5_carrier_certificate_missing",
        "D11_source_character_and_rigidity_certificate_missing",
        "D11_core_and_Jacobian_are_declared_not_source_emitted",
        "physical_RG_threshold_matching_packet_missing",
        "BRST_complete_W_Z_H_self_energies_missing",
        "fermion_complete_loop_inputs_not_source_closed",
        "complex_pole_width_residue_and_uncertainty_receipts_missing",
        "prospective_no_target_claim_freeze_missing",
    ]
    return {
        "artifact": "oph_wzh_strict_branch_candidate_audit",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "same_branch_formula_candidate_not_physical_prediction",
        "promotion_allowed": False,
        "branch": {
            "id": "source_audit_P_cand",
            "P": root["P_cand"],
            "alpha_U": root["alpha_U_P_cand"],
            "root_status": root["status"],
        },
        "clock_candidate": {
            "epsilon_Cs": str(epsilon_cs),
            "E_star_GeV": str(e_star_gev),
            "legacy_scale_rescaling_factor": str(scale_factor),
            "component_status": clock["component_status"],
            "source_clock_closed": False,
        },
        "same_branch_candidate_coordinates": {
            "v_GeV": v_gev,
            "W_tree_chart_GeV": w_mass,
            "Z_tree_chart_GeV": z_mass,
            "H_running_chart_GeV": mh_running,
            "top_running_companion_GeV": mt_running,
            "Gamma_W_GeV": None,
            "Gamma_Z_GeV": None,
            "Gamma_H_GeV": None,
        },
        "d10": d10,
        "d11_declared_surface": {
            "pi_y": pi_y,
            "pi_lambda": pi_lambda,
            "y_t": y_t,
            "lambda_H": lambda_h,
            "core_source_status": "declared_calibration_surface_not_source_emitted",
        },
        "tree_pole_control": {
            "s_W_GeV2": [w_mass**2, 0.0],
            "s_Z_GeV2": [z_mass**2, 0.0],
            "s_H_GeV2": [mh_running**2, 0.0],
            "status": "zero_width_tree_controls_not_physical_unstable_boson_poles",
        },
        "blockers": blockers,
        "claim_boundary": (
            "These are the strongest reproducible same-P formula-stack coordinates in the current "
            "corpus. They are not actual W/Z/H pole predictions because the carrier, clock, D11, "
            "RG, self-energy, width, residue, uncertainty, and provenance packets are absent."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--clock", type=Path, default=CLOCK)
    parser.add_argument("--d11-surface", type=Path, default=D11_SURFACE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build_artifact(_load(args.source_root), _load(args.clock), _load(args.d11_surface))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
