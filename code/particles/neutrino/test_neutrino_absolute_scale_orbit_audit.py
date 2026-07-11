#!/usr/bin/env python3
"""Validate the neutrino positive-scale-orbit audit artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_absolute_scale_orbit_audit.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_absolute_scale_orbit_audit.json"


def test_neutrino_absolute_scale_orbit_audit_fails_closed_on_rejected_candidate() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_neutrino_absolute_scale_orbit_audit"
    assert payload["status"] == "rejected_candidate_scale_audit"
    assert payload["proof_chain_role"] == "nonpromoting_diagnostic"
    assert payload["must_not_feed_back"] is True
    assert payload["theorem_status"] == "not_established"
    assert payload["no_hidden_discrete_branch"]["status"] == "not_established"
    assert payload["no_hidden_discrete_branch"]["open_discrete_blockers"]
    assert payload["remaining_positive_scale_orbit"]["status"] == "conditional_candidate_family_only"
    assert payload["remaining_positive_scale_orbit"]["group"] == "R_{>0}"
    assert payload["remaining_object"] == "source_closed_neutrino_operator_basis_and_mass_label_contract"
