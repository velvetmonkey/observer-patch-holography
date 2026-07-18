#!/usr/bin/env python3
"""Guard the neutrino lambda_nu bridge candidate scaffold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORRECTION_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_bridge_correction_candidate_audit.py"
CORRIDOR_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_attachment_bridge_scalar_corridor.py"
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_lambda_nu_bridge_candidate.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_lambda_nu_bridge_candidate.json"


def test_neutrino_lambda_nu_bridge_candidate() -> None:
    subprocess.run([sys.executable, str(CORRECTION_SCRIPT)], check=True, capture_output=True, text=True)
    subprocess.run([sys.executable, str(CORRIDOR_SCRIPT)], check=True, capture_output=True, text=True)
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(OUTPUT)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_neutrino_lambda_nu_bridge_candidate"
    assert payload["current_candidate_interface_artifact"] == "oph_majorana_overlap_defect_scalar_evaluator"
    assert payload["closed_normalizer_artifact"] == "oph_same_label_overlap_defect_weight_normalizer"
    assert payload["exact_next_theorem_object"] == "source_closed_neutrino_operator_basis_and_mass_label_contract"
    assert payload["conditional_absolute_scale_next_object"] == "one_positive_neutrino_bridge_correction_invariant"
    assert payload["paper_facing_attachment_parameterization"] == "oph_neutrino_attachment_bridge_invariant"
    assert payload["strictly_smaller_missing_clause"] is None
    assert payload["current_attached_stack_collapse_status"] == "refuted_by_attachment_irreducibility_theorem"
    assert payload["bridge_ansatz"] == "lambda_nu = (m_star_eV / q_mean^p_nu) * B_nu"
    assert payload["bridge_factor_schema"] == "B_nu = lambda_nu * q_mean^p_nu / m_star_eV"
    constructive = payload["best_constructive_subbridge_object"]
    assert constructive["artifact"] == "oph_defect_weighted_majorana_edge_weight_family"
    assert constructive["status"] == "conditional_constructive_subbridge_from_source_open_inputs"
    assert constructive["raw_edge_score_rule"] == "q_e = sqrt(gap_e * defect_e)"
    assert constructive["mu_family_rule"] == "mu_e = mu_nu * exp(eta_e) / mean_f(exp(eta_f))"
    assert constructive["anisotropy_diagnostics"]["max_mu_over_min_mu"] > 2.0
    assert constructive["anisotropy_diagnostics"]["sigma_mu_over_mean_mu"] > 0.3
    residual = payload["residual_amplitude_parameterization"]
    assert residual["definition"] == "B_nu = lambda_nu * q_mean^p_nu / m_star_eV"
    assert residual["compare_only_B_nu_star"] > 1.0
    ruled_out = payload["ruled_out_current_selected_point_scalar"]
    assert ruled_out["status"] == "internal_to_declared_candidate_stack_not_the_missing_bridge_scalar"
    assert ruled_out["selected_point"] == "weighted_cycle_selector_psi_wc"
    assert ruled_out["gate"] == "selector_overlap_phase_coboundary_trivializes_same_label_edge_transport"
    assert "0.5 * sum_e qbar_e" in ruled_out["definition"]
    stack = payload["bridge_interface_theorem_stack"]
    assert stack[0]["id"] == "oph_same_label_overlap_defect_weight_normalizer"
    assert stack[0]["status"] == "conditional_normalizer_from_source_open_scalar_certificate"
    assert stack[1]["id"] == "selector_overlap_phase_coboundary_trivializes_same_label_edge_transport"
    assert stack[1]["status"] == "closed_from_normalized_lift_coboundary"
    assert stack[2]["id"] == "selector_centered_unitary_common_refinement_descent_on_edge_bundle"
    assert stack[2]["status"] == "closed_from_normalized_common_refinement_unitary_transport"
    assert stack[3]["id"] == "oph_majorana_scalar_from_centered_edge_norm"
    assert stack[3]["status"] == "exact_scalar_evaluator_conditional_on_source_open_inputs"
    assert stack[4]["id"] == "oph_neutrino_attachment_bridge_invariant"
    assert "inside the rejected candidate" in stack[4]["role"]
    assert stack[5]["id"] == "neutrino_weighted_cycle_absolute_attachment"
    assert payload["compare_only_bridge_factor"]["F_nu_star"] > 1.0
    assert payload["compare_only_residual_amplitude_ratio"]["B_nu_star"] > 1.0
    smallest = payload["smallest_exact_missing_object"]
    assert smallest["symbol"] == "C_nu"
    assert smallest["status"] == "conditionally_irreducible_on_declared_candidate_stack"
    assert payload["next_theorem_if_this_route_is_right"]["conditional_absolute_attachment_object"] == "one_positive_neutrino_bridge_correction_invariant"
    reduced = payload["smaller_exact_object_above_emitted_proxy"]
    assert reduced["symbol"] == "C_nu"
    assert reduced["compare_only_target"] > 0.99
    assert reduced["compare_only_target"] < 1.01
    corridor = payload["strongest_compare_only_bridge_scalar_corridor"]
    assert corridor["artifact"] == "oph_neutrino_attachment_bridge_scalar_corridor"
    assert corridor["primary_cross_route_corridor"]["contains_compare_only_target"] is True
    assert corridor["strongest_target_containing_bridge_scalar_corridor"]["contains_compare_only_target"] is True
    assert corridor["strongest_target_containing_bridge_scalar_corridor"]["relative_half_width"] < corridor["primary_cross_route_corridor"]["relative_half_width"]
    assert corridor["shortlist_route_consensus_window"]["narrowing_vs_primary_cross_route_corridor"]["is_narrower"] is True
    assert corridor["shortlist_route_consensus_window"]["contains_compare_only_target"] is False
    assert corridor["bridge_correction_candidate_audit"]["artifact"] == "oph_neutrino_bridge_correction_candidate_audit"
    assert corridor["top_candidate_envelope"]["relative_half_width"] < 0.004
    assert corridor["family_assisted_route"]["route_id"] == "defect_family_assisted_residual_route"
    assert payload["current_attached_stack_irreducibility_theorem"]["artifact"] == "oph_neutrino_attachment_irreducibility_theorem"
    closed_form = payload["target_free_closed_form_candidates"][0]
    assert closed_form["name"] == "gamma_over_sqrt_ratio_hat"
    assert closed_form["status"] == "exactly_refuted_as_theorem_grade_absolute_scale_law"
    assert closed_form["proof_obstruction"] == "positive_rescaling_nonidentifiability"
    assert abs(closed_form["residual_sigma"]["21"]) < 0.1
    assert abs(closed_form["residual_sigma"]["32"]) < 0.2
