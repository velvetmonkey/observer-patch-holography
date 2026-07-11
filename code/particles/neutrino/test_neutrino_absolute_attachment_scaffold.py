#!/usr/bin/env python3
"""Guard the neutrino absolute-attachment scaffold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORRECTION_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_bridge_correction_candidate_audit.py"
CORRIDOR_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_attachment_bridge_scalar_corridor.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_absolute_attachment_scaffold.json"


def test_neutrino_absolute_attachment_scaffold_contract() -> None:
    subprocess.run([sys.executable, str(CORRECTION_SCRIPT)], check=True, capture_output=True, text=True)
    subprocess.run([sys.executable, str(CORRIDOR_SCRIPT)], check=True, capture_output=True, text=True)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_neutrino_absolute_attachment_scaffold"
    assert payload["status"] == "superseded_conditional_absolute_scale_scaffold"
    assert payload["exact_missing_object"] == "source_closed_neutrino_operator_basis_and_mass_label_contract"
    assert payload["conditional_candidate_missing_object"] == "neutrino_weighted_cycle_absolute_attachment"
    assert payload["current_no_go"]["one_additional_positive_bridge_invariant_is_necessary_and_sufficient"] is False
    assert payload["equivalent_scalar"]["name"] == "lambda_nu"
    assert payload["current_no_go"]["current_candidate_interface_artifact"] == "oph_majorana_overlap_defect_scalar_evaluator"
    assert payload["current_no_go"]["closed_normalizer_artifact"] == "oph_same_label_overlap_defect_weight_normalizer"
    assert payload["current_no_go"]["exact_next_theorem_object"] == "source_closed_neutrino_operator_basis_and_mass_label_contract"
    assert payload["current_no_go"]["conditional_absolute_scale_next_object"] == "one_positive_neutrino_bridge_correction_invariant"
    assert payload["current_no_go"]["strictly_smaller_missing_clause"] is None
    assert payload["current_no_go"]["corrected_bridge_parameterization"] == "lambda_nu = (m_star_eV / q_mean^p_nu) * B_nu"
    assert payload["current_no_go"]["residual_amplitude_parameterization"]["definition"] == "B_nu = lambda_nu * q_mean^p_nu / m_star_eV"
    reduced = payload["current_no_go"]["smaller_exact_object_above_emitted_proxy"]
    assert reduced["symbol"] == "C_nu"
    assert reduced["compare_only_target"] > 0.99
    assert reduced["compare_only_target"] < 1.01
    corridor = payload["current_no_go"]["strongest_compare_only_bridge_scalar_corridor"]
    assert corridor["artifact"] == "oph_neutrino_attachment_bridge_scalar_corridor"
    assert corridor["primary_cross_route_corridor"]["contains_compare_only_target"] is True
    assert corridor["strongest_target_containing_bridge_scalar_corridor"]["contains_compare_only_target"] is True
    assert corridor["strongest_target_containing_bridge_scalar_corridor"]["relative_half_width"] < corridor["primary_cross_route_corridor"]["relative_half_width"]
    assert corridor["bridge_correction_candidate_audit"]["artifact"] == "oph_neutrino_bridge_correction_candidate_audit"
    assert corridor["shortlist_route_consensus_window"]["narrowing_vs_primary_cross_route_corridor"]["is_narrower"] is True
    assert payload["extension_contract"]["must_emit"].startswith("lambda_nu")
    assert payload["extension_contract"]["scope"] == "conditional_only_after_source_closed_physical_operator_basis_and_label_contract"
    stack = payload["extension_contract"]["current_theorem_stack"]
    assert stack[0]["id"] == "oph_same_label_overlap_defect_weight_normalizer"
    assert stack[1]["id"] == "selector_overlap_phase_coboundary_trivializes_same_label_edge_transport"
    assert stack[1]["status"] == "closed_from_normalized_lift_coboundary"
    assert stack[2]["id"] == "selector_centered_unitary_common_refinement_descent_on_edge_bundle"
    assert stack[2]["status"] == "closed_from_normalized_common_refinement_unitary_transport"
