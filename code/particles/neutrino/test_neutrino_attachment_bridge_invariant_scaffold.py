#!/usr/bin/env python3
"""Guard the corrected neutrino bridge-invariant scaffold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORRECTION_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_bridge_correction_candidate_audit.py"
CORRIDOR_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_attachment_bridge_scalar_corridor.py"
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_attachment_bridge_invariant_scaffold.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_bridge_invariant_scaffold.json"


def test_neutrino_attachment_bridge_invariant_scaffold() -> None:
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
    assert payload["artifact"] == "oph_neutrino_attachment_bridge_invariant_scaffold"
    assert payload["status"] == "diagnostic_attachment_scaffold_on_rejected_candidate"
    assert payload["bridge_factor_schema"] == "B_nu = lambda_nu * q_mean^p_nu / m_star_eV"
    assert payload["residual_invariant_symbol"] == "B_nu"
    assert payload["contract"]["must_emit"].startswith("a source-closed neutrino operator")
    assert payload["contract"]["must_imply"] == "lambda_nu = (m_star_eV / q_mean^p_nu) * B_nu"
    ruled_out = payload["ruled_out_current_selected_point_scalar"]
    assert ruled_out["status"] == "already_internal_to_current_candidate_stack_not_the_missing_bridge_scalar"
    assert ruled_out["selected_point"] == "weighted_cycle_selector_psi_wc"
    assert payload["qbar_only_collapse_status"] == "refuted_on_current_attached_stack_by_attachment_irreducibility_theorem"
    constructive = payload["best_constructive_subbridge_object"]
    assert constructive["artifact"] == "oph_defect_weighted_majorana_edge_weight_family"
    assert constructive["status"] == "conditional_constructive_subbridge_from_source_open_inputs"
    assert constructive["raw_edge_score_rule"] == "q_e = sqrt(gap_e * defect_e)"
    smallest = payload["smallest_exact_missing_object"]
    assert smallest["name"] == "source_closed_neutrino_operator_basis_and_mass_label_contract"
    assert smallest["status"] == "open"
    conditional_attachment = payload["conditional_absolute_attachment_object"]
    assert conditional_attachment["symbol"] == "C_nu"
    assert conditional_attachment["status"] == "conditionally_irreducible_on_declared_candidate_stack"
    reduced = payload["smaller_exact_object_above_emitted_proxy"]
    assert reduced["symbol"] == "C_nu"
    assert reduced["compare_only_target"] > 0.99
    assert reduced["compare_only_target"] < 1.01
    corridor = payload["strongest_compare_only_bridge_scalar_corridor"]
    assert corridor["artifact"] == "oph_neutrino_attachment_bridge_scalar_corridor"
    assert corridor["primary_cross_route_corridor"]["contains_compare_only_target"] is True
    assert corridor["strongest_target_containing_bridge_scalar_corridor"]["contains_compare_only_target"] is True
    assert corridor["strongest_target_containing_bridge_scalar_corridor"]["relative_half_width"] < corridor["primary_cross_route_corridor"]["relative_half_width"]
    assert corridor["bridge_correction_candidate_audit"]["artifact"] == "oph_neutrino_bridge_correction_candidate_audit"
    assert corridor["shortlist_route_consensus_window"]["narrowing_vs_primary_cross_route_corridor"]["is_narrower"] is True
    assert "B_nu = lambda_nu * q_mean^p_nu / m_star_eV" in payload["residual_attachment_quotient_theorem"]
