#!/usr/bin/env python3
"""Validate the exact current-family quark PDG reconstruction theorem artifact."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
LANE_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_lane_closure_contract.py"
AFFINE_SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_current_family_affine_anchor_theorem.py"
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_current_family_exact_pdg_theorem.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_pdg_theorem.json"


def test_quark_current_family_exact_pdg_theorem() -> None:
    subprocess.run([sys.executable, str(AFFINE_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(LANE_SCRIPT)], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_current_family_exact_pdg_theorem"
    assert payload["proof_status"] == "closed_current_family_exact_pdg_reconstruction"
    assert payload["theorem_scope"] == "current_family_only"
    assert payload["public_promotion_allowed"] is False

    for residual in payload["exact_fit_residuals_gev"].values():
        assert math.isclose(float(residual), 0.0, rel_tol=0.0, abs_tol=1e-12)

    frontier = payload["next_target_free_bridge"]["remaining_public_frontier"]
    assert frontier == []
    assert "selected-public-class closure is carried by the public physical-sigma" in (
        payload["next_target_free_bridge"]["note"]
    )
