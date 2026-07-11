#!/usr/bin/env python3
"""Guard the neutrino attachment irreducibility theorem artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORRECTION_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_bridge_correction_candidate_audit.py"
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_attachment_irreducibility.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_irreducibility_theorem.json"


def test_neutrino_attachment_irreducibility_theorem() -> None:
    subprocess.run([sys.executable, str(CORRECTION_SCRIPT)], check=True, capture_output=True, text=True)
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(OUTPUT)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "saved:" in completed.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["artifact"] == "oph_neutrino_attachment_irreducibility_theorem"
    assert payload["status"] == "conditional_algebraic_no_go_on_rejected_candidate_stack"
    assert payload["public_surface_candidate_allowed"] is False
    assert payload["prediction_promotion_allowed"] is False
    assert payload["proof_grade"] == "exact_factorization_plus_one_orbit_underdetermination_conditional_on_declared_candidate"
    assert payload["remaining_object"]["status"] == "conditionally_irreducible_on_declared_candidate_stack"
    reduced = payload["reduced_remaining_object"]
    assert reduced["symbol"] == "C_nu"
    assert reduced["status"] == "conditionally_irreducible_on_declared_candidate_stack"
    assert reduced["compare_only_target"] > 0.99
    assert reduced["compare_only_target"] < 1.01
    assert payload["internal_positive_proxy_object"]["route_id"] == "core_residual_scalar_route"
    assert payload["theorem"]["name"] == "weighted_cycle_attachment_irreducibility_after_full_attached_stack"
    assert "not derivable" in payload["theorem"]["sharpened_conclusion"]
    assert "conditional stack fixes B_nu if and only if it fixes C_nu" in " ".join(payload["theorem"]["reduced_exact_factorization"])
    assert "conditionally irreducible" in payload["theorem"]["reduced_sharpened_conclusion"]
    checks = payload["factorization_validation"]["q_rescaling_orbit_checks"]
    assert len(checks) == 3
    assert max(item["max_relative_dm_scaling_error"] for item in checks) < 1e-12
    assert max(item["max_abs_difference_in_abs_unitary"] for item in checks) < 1e-12
