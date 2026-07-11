#!/usr/bin/env python3
"""Guard the closed same-label overlap-defect weight normalizer."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_same_label_overlap_defect_weight_normalizer.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "same_label_overlap_defect_weight_normalizer.json"


def test_same_label_overlap_defect_weight_normalizer() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(OUTPUT)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_same_label_overlap_defect_weight_normalizer"
    assert payload["status"] == "conditional_normalizer_from_source_open_scalar_certificate"
    assert payload["proof_status"] == "exact_normalization_identity_conditional_on_certificate"
    assert payload["source_only_physical_input_eligible"] is False
    assert payload["identities_verified"]["qbar_matches_exp_eta_bar"] is True
    assert payload["identities_verified"]["mu_e_matches_base_times_qbar"] is True
    assert payload["next_exact_object"]["artifact"] == "source_closed_neutrino_operator_basis_and_mass_label_contract"
