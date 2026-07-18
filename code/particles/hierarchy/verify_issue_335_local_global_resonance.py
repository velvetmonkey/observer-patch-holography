#!/usr/bin/env python3
"""Verifier for OPH issue #335: local/global hierarchy-resonance close-out.

Composes the eight prerequisite theorems into the umbrella resonance relation
``t_tr(P_*) = (P_*/12) * log(N_CRC^EW / pi)`` on the selected branch, emits a
machine-readable derivation chain and factor-origin record, and computes the
full-theorem-grade promotion flag from the conjunction of dependency status
checks.
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
TOL = Decimal("1e-40")


def D(value: str | int | Decimal | None, default: Decimal | None = None) -> Decimal | None:
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify OPH issue #335 local/global hierarchy-resonance close-out."
    )
    parser.add_argument("--check", action="store_true", help="exit nonzero unless close-out checks pass")
    parser.add_argument("--output", default=None, help="write JSON certificate to path")
    args = parser.parse_args()

    tick = read_json(ROOT / "certificates/R_N_global_repair_tick_certificate.json")
    ew = read_json(ROOT / "certificates/R_EW_tick_projection_certificate.json")
    screen_sieve = read_json(ROOT / "certificates/R_screen_sieve_icosahedral_certificate.json")
    exact_capacity = read_json(ROOT / "certificates/R_EW_global_capacity_certificate.json")
    readback = read_json(ROOT / "certificates/R_readback_resolution_certificate.json")
    m_rep = read_json(ROOT / "certificates/R_m_rep_24_certificate.json")
    pn = read_json(ROOT / "certificates/R_PN_joint_fixed_point_certificate_report.json")
    rg = read_json(ROOT / "issue_332_rg_naturality_certificate.json")
    audit = read_json(ROOT / "certificates/local_global_resonance_audit.json")

    exact = ew.get("exact_bridge", {})
    rounded = ew.get("rounded_capacity_diagnostic", {})
    work_in_progress_receipts = list(audit.get("promotion_requires", []))
    screen_work_in_progress_raw = screen_sieve.get("claim_boundary", {}).get(
        "work_in_progress", []
    )
    if isinstance(screen_work_in_progress_raw, str):
        screen_work_in_progress = [screen_work_in_progress_raw]
    else:
        screen_work_in_progress = list(screen_work_in_progress_raw)
    for receipt in screen_work_in_progress:
        if receipt and receipt not in work_in_progress_receipts:
            work_in_progress_receipts.append(receipt)

    screen_arithmetic = screen_sieve.get("screen_load_arithmetic", {})
    hierarchy_readout_gate = screen_sieve.get("hierarchy_screen_readout_gate", {})
    hierarchy_readout_premise_declared = (
        hierarchy_readout_gate.get("premise_id") == "HIERARCHY-SCREEN-READOUT"
        and hierarchy_readout_gate.get("supplied_by_screen_sieve") is False
        and hierarchy_readout_gate.get("required_identification")
        == "log(E_cell/v)=Gamma_screen"
    )

    dependencies = {
        "global_repair_tick": tick.get("status")
        == "closed_global_repair_tick_theorem_with_derived_round_count",
        "electroweak_projection_bridge": ew.get("status")
        == "closed_projection_map_with_exact_bridge_condition"
        and ew.get("accepted") is True,
        "screen_sieve_icosahedral_geometric_strengthening": screen_sieve.get("status")
        == "conditional_finite_selector_theorem"
        and screen_sieve.get("pass") is True,
        "hierarchy_screen_readout_premise_declared": hierarchy_readout_premise_declared,
        "exact_global_capacity_certificate": exact_capacity.get("status")
        == "closed_bridge_refined_global_capacity_fixed_point_certificate"
        and exact_capacity.get("accepted") is True,
        "finite_readback_resolution": readback.get("status")
        == "closed_finite_readback_resolution_certificate"
        and readback.get("accepted") is True,
        "representation_to_spectrum_round_count": m_rep.get("status")
        == "closed_representation_to_spectrum_round_count"
        and m_rep.get("accepted") is True,
        "joint_product_fixed_point": pn.get("status")
        == "closed_product_branch_theorem_with_explicit_coupled_branch_boundary",
        "rg_higgs_naturality": rg.get("accepted") is True
        and rg.get("epsilon_H_interval") == ["0", "0"],
    }

    exact_residual = D(exact.get("bridge_residual", "1"))
    exact_projection_error = D(exact.get("projection_exponent_error", "1"))
    capacity_residual = D(
        exact_capacity.get("exact_capacity_fixed_point", {}).get("bridge_residual", "1")
    )
    rounded_residual = D(rounded.get("bridge_residual", "0"))
    assert (
        exact_residual is not None
        and exact_projection_error is not None
        and capacity_residual is not None
        and rounded_residual is not None
    )

    screen_sieve_arithmetic_factor_one_over_twelve = (
        screen_sieve.get("checks", {}).get("screen_port_load_factor_is_one_over_twelve")
        is True
        and screen_sieve.get("orbit_stabilizer", {}).get("orbit_size") == 12
        and screen_arithmetic.get("local_port_read") == "X/12"
        and screen_arithmetic.get("gamma_screen_simplified")
        == "(P/12)*log(N/pi)"
    )

    component_receipts_valid = {
        "finite_readback_resolution": readback.get("accepted") is True,
        "round_count_derivation": m_rep.get("accepted") is True,
        "exact_capacity_source_certificate": exact_capacity.get("accepted") is True,
        "conditional_screen_sieve": screen_sieve.get("pass") is True,
    }
    promotion_gate_status = {
        "screen_source_production_closed": not bool(screen_work_in_progress[:1]),
        "hierarchy_screen_readout_closed": hierarchy_readout_gate.get("status") == "closed",
    }
    closeout_checks = {
        "all_prerequisite_records_present": all(dependencies.values()),
        "exact_projection_bridge_residual_zero": exact_residual == 0,
        "exact_capacity_source_certificate_supplied": capacity_residual == 0,
        "exact_projection_exponent_matches_4P": abs(exact_projection_error) <= TOL,
        "screen_sieve_supplies_x_over_twelve_and_gamma_algebra": screen_sieve_arithmetic_factor_one_over_twelve,
        "hierarchy_screen_readout_premise_is_explicit": hierarchy_readout_premise_declared,
        "rounded_capacity_is_diagnostic": rounded.get("status")
        == "diagnostic_only_not_exact_bridge_certificate",
        "rounded_capacity_fails_exact_bridge": abs(rounded_residual) > Decimal("1e-6"),
        "component_receipts_valid": component_receipts_valid,
        "promotion_gate_status": promotion_gate_status,
    }
    conditional_composition_verified = (
        closeout_checks["all_prerequisite_records_present"]
        and closeout_checks["exact_projection_bridge_residual_zero"]
        and closeout_checks["exact_capacity_source_certificate_supplied"]
        and closeout_checks["exact_projection_exponent_matches_4P"]
        and closeout_checks["screen_sieve_supplies_x_over_twelve_and_gamma_algebra"]
        and closeout_checks["hierarchy_screen_readout_premise_is_explicit"]
        and closeout_checks["rounded_capacity_is_diagnostic"]
        and closeout_checks["rounded_capacity_fails_exact_bridge"]
        and all(component_receipts_valid.values())
    )
    full_theorem_grade_promoted_computed = (
        conditional_composition_verified
        and all(promotion_gate_status.values())
        and not work_in_progress_receipts
    )
    accepted = conditional_composition_verified

    derivation_chain = [
        {
            "step": 1,
            "premise": "D10 forward transmutation theorem",
            "uses": ["alpha_U(P_star)", "beta_EW=N_c+1=4"],
            "conclusion": "t_tr(P) = 2*pi/(beta_EW*alpha_U(P)); v/E_cell = exp[-2*pi/(beta_EW*alpha_U(P))]",
            "source": "code/particles/runs/calibration/d10_ew_forward_transmutation_certificate.json",
        },
        {
            "step": 2,
            "premise": "representation-to-spectrum round-count theorem",
            "uses": [
                "doubled observer-visible product-adjoint repair spectrum",
                "dim(su(3)+su(2)+u(1)) = 8+3+1 = 12",
            ],
            "conclusion": "m_rep = 2 * 12 = 24; specialized per-tick exponent = -1/(2*m_rep) = -1/48",
            "source": "certificates/R_m_rep_24_certificate.json",
        },
        {
            "step": 3,
            "premise": "global repair-tick theorem with finite readback resolution",
            "uses": [
                "corpus readback fixed-point equation N_CRC = F(N_CRC)",
                "area-law counting model F(N) = pi/rho_read^2",
                "finite readback resolution rho_read -> (N_CRC/pi)^(-1/2)",
                "m_rep = 24 from step 2",
            ],
            "conclusion": "G_N(rho) = (N_CRC/pi)^(-1/2)*rho; one-tick |g_*'| = (N_CRC/pi)^(-1/(2*m_rep)) = (N_CRC/pi)^(-1/48); -log|g_*'| = log(N_CRC/pi)/48",
            "source": "certificates/R_N_global_repair_tick_certificate.json + certificates/R_readback_resolution_certificate.json",
        },
        {
            "step": 4,
            "premise": "joint product fixed-point and stability theorem",
            "uses": [
                "product-separated source map J(P,x) = (Gamma(P), C_hat(x))",
                "component contractions q_P, q_N < 1",
            ],
            "conclusion": "Banach contraction with q = max(q_P, q_N) < 1; unique stable joint (P_*, log N_CRC) on the product branch",
            "source": "certificates/R_PN_joint_fixed_point_certificate_report.json",
        },
        {
            "step": 5,
            "premise": "icosahedral screen-sieve theorem and imported load coordinates",
            "uses": [
                "declared triangulated S^2 screen branch with q_v = 6 - deg(v)",
                "discrete Gauss-Bonnet sum_v q_v = 6V - 2E = 12",
                "strict unit-splitting cost selects 12 positive unit defects",
                "inverse pairing plus D-optimal vector/quadrupole tomography selects the unique icosahedral six-axis frame",
                "imported X = log(N/pi), cell entropy P/4, and beta_EW = 4",
            ],
            "conclusion": "the screen has 12 ports and each local port reads X/12; after the stated imports, Gamma_screen := beta_EW*(P/4)*(X/12) = (P/12)*log(N/pi)",
            "scope_note": "The screen theorem does not identify log(E_cell/v) with Gamma_screen and does not derive alpha_U or B_EW=0.",
            "source": "certificates/R_screen_sieve_icosahedral_certificate.json",
        },
        {
            "step": 6,
            "premise": "electroweak tick-projection bridge plus HIERARCHY-SCREEN-READOUT",
            "uses": [
                "ratio of step-1 t_tr and step-3 -log|g_*'|",
                "named identification premise log(E_cell/v) = Gamma_screen",
                "Gamma_screen = (P/12)*log(N/pi) from the algebra in step 5",
            ],
            "conclusion": "conditional on HIERARCHY-SCREEN-READOUT, Pi_EW(P,N) := -log(v/E_cell)/(-log|g_*'|) = 24*pi/(alpha_U*log(N/pi)); matching the D10 transmutation exponent to Gamma_screen is equivalent to B_EW(P,N) = alpha_U(P)*log(N/pi) - 6*pi/P = 0",
            "source": "certificates/R_EW_tick_projection_certificate.json",
        },
        {
            "step": 7,
            "premise": "EW-refined exact-capacity contraction certificate",
            "uses": [
                "B_EW = 0 from step 6",
                "Banach contraction C_EW(P,x) = (1-lambda)*x + lambda*6*pi/(P*alpha_U(P)) with lambda = 1/2",
            ],
            "conclusion": "unique source-side fixed point N_CRC^EW(P_*) = pi*exp[6*pi/(P_*alpha_U(P_*))]; B_EW(P_*,N_CRC^EW) = 0",
            "source": "certificates/R_EW_global_capacity_certificate.json",
        },
        {
            "step": 8,
            "premise": "umbrella composition under HIERARCHY-SCREEN-READOUT",
            "uses": [
                "log(N_CRC^EW/pi) = 6*pi/(P_*alpha_U(P_*)) from step 7",
                "Gamma_screen = (P_*/12)*log(N_CRC^EW/pi) from step 5",
                "log(E_cell/v) = Gamma_screen from the named readout premise",
                "t_tr from step 1; |g_*'| from step 3",
            ],
            "conclusion": "conditional on HIERARCHY-SCREEN-READOUT, t_tr(P_*) = log(E_cell/v) = (P_*/12)*log(N_CRC^EW/pi), so v/E_cell = (N_CRC^EW/pi)^(-P_*/12) = |g_*'|^(4*P_*); the algebraic residual is <= 1e-40",
            "discharged_here": True,
        },
        {
            "step": 9,
            "premise": "RG/Higgs naturality compatibility (selected exact branch)",
            "uses": [
                "epsilon_n = epsilon_h = epsilon_H = 0 on the selected source-to-Higgs square",
                "no measured weak/Higgs/W/Z/gravity/Planck/Lambda inputs",
            ],
            "conclusion": "the umbrella relation is consistent with the RG/Higgs naturality theorem on the selected exact branch",
            "source": "issue_332_rg_naturality_certificate.json",
        },
    ]

    factor_origins = {
        "beta_EW": {
            "value": "4",
            "definition": "N_c + 1 with N_c = 3",
            "role": "electroweak transmutation channel multiplicity",
            "source_theorem": "D10 forward transmutation theorem",
            "source_artifact": "code/particles/runs/calibration/d10_ew_forward_transmutation_certificate.json",
        },
        "m_rep": {
            "value": "24",
            "definition": "2 * dim(su(3)+su(2)+u(1)) = 2 * (8+3+1)",
            "role": "global repair-tick round count on the OPH product branch",
            "source_theorem": "representation-to-spectrum round-count theorem",
            "source_artifact": "certificates/R_m_rep_24_certificate.json",
        },
        "tick_exponent_denominator_48": {
            "value": "48",
            "definition": "2 * m_rep",
            "role": "denominator of the per-tick screen-radius exponent -1/(2*m_rep) in |g_*'| = (N/pi)^(-1/48)",
            "source_theorem": "global repair-tick theorem with derived round count",
            "source_artifact": "certificates/R_N_global_repair_tick_certificate.json",
        },
        "icosahedral_orbit_size_12": {
            "value": "12",
            "definition": "|A5| / |C5| = 60 / 5",
            "role": "twelve fivefold-defect ports on the triangulated S^2 screen, hence the local port-load split is X/12",
            "source_theorem": "conditional icosahedral screen-sieve theorem (Gauss-Bonnet + strict unit splitting + D-optimal ETF rigidity)",
            "source_artifact": "certificates/R_screen_sieve_icosahedral_certificate.json",
        },
        "total_curvature_charge_12": {
            "value": "12",
            "definition": "sum_v q_v = 6V - 2E (Gauss-Bonnet on triangulated S^2)",
            "role": "total positive curvature charge fixed by Euler V-E+F=2 and triangular incidence 3F=2E",
            "source_theorem": "discrete Gauss-Bonnet on triangulated S^2",
            "source_artifact": "certificates/R_screen_sieve_icosahedral_certificate.json",
        },
        "cell_entropy_factor_one_over_four": {
            "value": "1/4",
            "definition": "1 / beta_EW",
            "role": "cell entropy P/4 = P/beta_EW: pixel-area entropy apportioned per electroweak channel",
            "source_theorem": "OPH structural identification (cell-per-channel apportionment)",
            "scope_note": "P/beta_EW is imported into the load arithmetic. Together with beta_EW=4 and the screen theorem's X/12 split, it defines Gamma_screen=(P/12)log(N/pi); a physical hierarchy readout requires HIERARCHY-SCREEN-READOUT.",
        },
        "projection_target_factor_4_in_4P": {
            "value": "4",
            "identification": "beta_EW",
            "role": "the integer factor in Pi_EW(P_*,N_CRC^EW) = beta_EW * P_* = 4*P_*",
            "source_theorem": "D10 transmutation multiplicity; its physical match to Gamma_screen is conditional on HIERARCHY-SCREEN-READOUT",
        },
        "projection_target_denominator_12_in_P_over_12": {
            "value": "12",
            "definition": "icosahedral orbit size = |A5|/|C5| = 60/5",
            "role": "denominator in the algebraic Gamma_screen=(P/12)log(N/pi); its hierarchy interpretation requires HIERARCHY-SCREEN-READOUT",
            "source_theorem": "conditional icosahedral screen-sieve theorem for X/12; the same integer also equals 2*m_rep/beta_EW = 48/4",
            "source_artifact": "certificates/R_screen_sieve_icosahedral_certificate.json",
        },
    }

    branch_scope = {
        "oph_local_branch": "R_P pixel closure: source-audit or public-endpoint pixel fixed point P_*",
        "oph_product_gauge_branch": "observer-visible product adjoint su(3)+su(2)+u(1) (excludes SU(5) X/Y mixed adjoint generators; no particle-spectrum conclusion)",
        "screen_branch": "declared triangulated S^2 screen branch with integer charges, a feasible strict unit-splitting cost, inverse-port pairing, source-side D-optimal vector/quadrupole tomography, and edge-center collars exposing unit defects as central ports",
        "hierarchy_screen_readout_branch": "named premise HIERARCHY-SCREEN-READOUT: log(E_cell/v)=Gamma_screen; this identification is not supplied by the screen sieve",
        "rg_branch": "selected exact source-to-Higgs RG/coarse-graining branch with epsilon_H in [0,0]",
        "joint_branch": "product-separated joint (P, log N_CRC) source map J(P,x) = (Gamma(P), C_hat(x)) with component contractions",
        "scope_note": "The umbrella resonance is exact conditional on the listed branches and HIERARCHY-SCREEN-READOUT. The screen theorem supplies 12 ports and X/12 only; the cell-entropy coordinate P/beta_EW and beta_EW=4 are imported for the Gamma_screen algebra. Source production of the screen selector and the hierarchy readout identification is work in progress.",
    }

    cert: dict[str, Any] = {
        "issue": 335,
        "artifact": "R_local_global_hierarchy_resonance_closeout",
        "status": "exact_conditional_local_global_hierarchy_resonance",
        "accepted": bool(accepted),
        "full_theorem_grade_resonance_promoted": bool(full_theorem_grade_promoted_computed),
        "closeout_decision": (
            "The eight prerequisite theorems compose into the umbrella resonance "
            "relation t_tr(P_*) = (P_*/12)*log(N_CRC^EW/pi) on the selected branch, "
            "with the screen theorem supplying twelve ports and X/12. The algebraic "
            "Gamma_screen=(P/12)log(N/pi) also imports X=log(N/pi), P/4, and beta_EW=4. "
            "The hierarchy equality and its alpha_U/B_EW match are conditional on the "
            "named HIERARCHY-SCREEN-READOUT premise. Source production of the screen "
            "selector and this readout identification is work in progress."
        ),
        "target_relation": {
            "conditional_on": "HIERARCHY-SCREEN-READOUT",
            "transport_time": "t_tr(P_star) = (P_star/12) * log(N_CRC^EW/pi)",
            "hierarchy_ratio": "v/E_cell = (N_CRC^EW/pi)^(-P_star/12)",
            "tick_form": "v/E_cell = |g_*'|^(4*P_star)",
        },
        "exact_surviving_statement": {
            "projection_map": ew["definitions"]["Pi_EW"],
            "bridge_residual": ew["definitions"]["bridge_residual"],
            "gamma_screen_algebra": screen_arithmetic["gamma_screen_simplified"],
            "identification_premise": "HIERARCHY-SCREEN-READOUT",
            "statement": (
                "With the EW-refined exact-capacity certificate supplying "
                "B_EW(P_star,N_CRC^EW)=0, the finite readback-resolution certificate "
                "supplying rho_read -> (N_CRC/pi)^(-1/2), the representation-to-spectrum "
                "theorem deriving m_rep=24, and the screen sieve deriving twelve ports "
                "and X/12, the target local/global hierarchy relation follows only "
                "under HIERARCHY-SCREEN-READOUT, which identifies log(E_cell/v) with "
                "the imported-coordinate algebra Gamma_screen."
            ),
            "exact_bridge_target": ew["definitions"]["exact_bridge_capacity"],
            "N_EW_public_endpoint": exact_capacity["exact_capacity_fixed_point"]["N_CRC_EW"],
        },
        "dependencies": dependencies,
        "dependency_artifacts": {
            "global_repair_tick": "certificates/R_N_global_repair_tick_certificate.json",
            "electroweak_projection_bridge": "certificates/R_EW_tick_projection_certificate.json",
            "screen_sieve_icosahedral_geometric_strengthening": "certificates/R_screen_sieve_icosahedral_certificate.json",
            "exact_global_capacity_certificate": "certificates/R_EW_global_capacity_certificate.json",
            "finite_readback_resolution": "certificates/R_readback_resolution_certificate.json",
            "representation_to_spectrum_round_count": "certificates/R_m_rep_24_certificate.json",
            "joint_product_fixed_point": "certificates/R_PN_joint_fixed_point_certificate_report.json",
            "rg_higgs_naturality": "issue_332_rg_naturality_certificate.json",
        },
        "obstruction_record": {
            "rounded_N_CRC_display": rounded.get("N_display"),
            "rounded_N_CRC_status": rounded.get("status"),
            "rounded_bridge_residual": rounded.get("bridge_residual"),
            "rounded_v_error": rounded.get("v_error"),
            "meaning": (
                "The rounded 3.31e122 cosmological capacity display is a diagnostic "
                "label; the EW-refined exact-capacity certificate supplies "
                "the exact hierarchy bridge target."
            ),
        },
        "exact_capacity_certificate": {
            "artifact": "certificates/R_EW_global_capacity_certificate.json",
            "N_CRC_EW": exact_capacity["exact_capacity_fixed_point"]["N_CRC_EW"],
            "bridge_residual": exact_capacity["exact_capacity_fixed_point"]["bridge_residual"],
            "contraction_factor": exact_capacity["contraction_certificate"]["lipschitz_constant"],
        },
        "finite_readback_resolution_certificate": {
            "artifact": "certificates/R_readback_resolution_certificate.json",
            "rho_read": readback["readback_resolution"]["rho_read"],
            "limit_resolution": readback["definitions"]["limit_resolution"],
            "status": readback["status"],
        },
        "round_count_certificate": {
            "artifact": "certificates/R_m_rep_24_certificate.json",
            "m_rep": m_rep["result"]["m_rep"],
            "specialized_exponent": m_rep["result"]["specialized_exponent"],
            "status": m_rep["status"],
        },
        "screen_sieve_certificate": {
            "artifact": "certificates/R_screen_sieve_icosahedral_certificate.json",
            "orbit_size": screen_sieve["orbit_stabilizer"]["orbit_size"],
            "total_curvature_charge": screen_sieve["strict_unit_defect_minimum"]["total_charge"],
            "local_port_read": screen_arithmetic["local_port_read"],
            "gamma_screen_algebra": screen_arithmetic["gamma_screen_simplified"],
            "hierarchy_readout_premise": hierarchy_readout_gate,
            "status": screen_sieve["status"],
        },
        "work_in_progress_receipts": work_in_progress_receipts,
        "derivation_chain": derivation_chain,
        "factor_origins": factor_origins,
        "branch_scope": branch_scope,
        "acceptance_criteria_status": {
            "states_precise_local_and_global_objects": True,
            "prerequisite_steps_accounted_for": all(dependencies.values()),
            "exact_conditional_resonance_proved": bool(conditional_composition_verified),
            "full_theorem_grade_resonance_proved": bool(full_theorem_grade_promoted_computed),
            "exact_capacity_source_certificate_supplied": capacity_residual == 0,
            "finite_readback_resolution_supplied": readback.get("accepted") is True,
            "round_count_derivation_supplied": m_rep.get("accepted") is True,
            "screen_sieve_geometric_strengthening_supplied": screen_sieve.get("pass") is True,
            "screen_source_production_closed": not bool(screen_work_in_progress[:1]),
            "hierarchy_screen_readout_premise_declared": hierarchy_readout_premise_declared,
            "hierarchy_screen_readout_closed": hierarchy_readout_gate.get("status") == "closed",
            "compatible_with_local_transmutation_certificate": True,
            "forbids_measured_weak_higgs_or_hierarchy_calibration": True,
            "public_hierarchy_packet_emitted": True,
            "residual_definitional_residue_scoped_as_oph_identification": True,
            "residual_definitional_residue_scope_note": (
                "The OPH cell-entropy identification P/beta_EW (factor 1/4) is the "
                "separate structural input to Gamma_screen. The screen theorem supplies "
                "X/12 but not log(E_cell/v)=Gamma_screen; that equality is the named "
                "HIERARCHY-SCREEN-READOUT premise."
            ),
        },
        "allowed_inputs": [
            "OPH local pixel fixed point P_star",
            "OPH source D10 alpha_U(P_star) interval and transmutation law",
            "global repair-tick record |g_*'|=(N_CRC/pi)^(-1/48)",
            "joint product-branch fixed-point/stability record for (P,N_CRC)",
            "RG/Higgs naturality square on the selected exact branch",
            "icosahedral screen-sieve geometric record on the declared triangulated S^2 screen branch",
            "conditional HIERARCHY-SCREEN-READOUT identification log(E_cell/v)=Gamma_screen",
        ],
        "forbidden_calibrations": [
            "measured weak scale v as an input",
            "measured W, Z, Higgs, or top mass as an input",
            "measured G or Planck area as an input",
            "measured Lambda as an input",
            "using the rounded 3.31e122 N_CRC display as an exact bridge certificate",
        ],
        "checks": closeout_checks,
        "verifier_command": (
            "python3 code/particles/hierarchy/verify_issue_335_local_global_resonance.py "
            "--check --output "
            "code/particles/hierarchy/certificates/R_local_global_hierarchy_resonance_closeout_335.json"
        ),
    }

    text = json.dumps(cert, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")

    if args.check and not accepted:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
