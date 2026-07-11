#!/usr/bin/env python3
"""Validate the bundle-descent candidate fields beneath the neutrino quadraticity sublemma."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_majorana_overlap_defect_scalar_evaluator.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "majorana_overlap_defect_scalar_evaluator.json"


def test_bundle_descent_candidate_fields() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["bundle_descent_candidate_id"] == "selector_centered_unitary_common_refinement_descent_on_edge_bundle"
    assert payload["bundle_descent_status"] == "closed_from_normalized_common_refinement_unitary_transport"
    assert payload["phase_cocycle_triviality_candidate_id"] == "selector_overlap_phase_coboundary_trivializes_same_label_edge_transport"
    assert payload["phase_cocycle_triviality_status"] == "closed_from_normalized_lift_coboundary"
    assert payload["all_triangle_phases_one_certificate"] is True
    assert payload["normalized_transport_cocycle_equation"] == "U_wv_e_norm o U_vu_e_norm = U_wu_e_norm"
    assert payload["smaller_exact_missing_clause_id"] is None
    assert payload["bundle_descent_gate_if_closed"] == "promotion_gate_for_xi±eta_and_xi±i_eta_cleared"
    assert payload["exact_remaining_ingredient"] == "source_closed_neutrino_operator_basis_and_mass_label_contract"
    assert payload["proof_status"] == "exact_scalar_evaluator_conditional_on_source_open_inputs"
