#!/usr/bin/env python3
"""Validate the explicit neutrino weighted-cycle candidate-law object."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_weighted_cycle_theorem_object.py"
COCYCLE = ROOT / "particles" / "runs" / "flavor" / "overlap_edge_transport_cocycle.json"
SELECTOR = ROOT / "particles" / "runs" / "neutrino" / "neutrino_transport_load_segment_selector.json"
REPAIR = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"


def test_weighted_cycle_law_object_matches_live_midpoint_without_theorem_promotion() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_neutrino_theorem_object_") as tmpdir:
        out = pathlib.Path(tmpdir) / "theorem_object.json"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--cocycle",
                str(COCYCLE),
                "--selector",
                str(SELECTOR),
                "--repair",
                str(REPAIR),
                "--output",
                str(out),
            ],
            check=True,
            cwd=ROOT,
        )
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["artifact"] == "oph_neutrino_weighted_cycle_theorem_object"
        assert payload["status"] == "retrospective_weighted_cycle_candidate_law"
        assert payload["theorem_status"] == "not_established"
        assert payload["public_surface_candidate_allowed"] is False
        assert payload["prediction_promotion_allowed"] is False
        assert payload["candidate_law"]["selected_tau_nu"] == 0.5
        assert abs(payload["live_inputs"]["D_nu"] - 1.127883690210334) < 1.0e-15
        assert abs(payload["live_inputs"]["p_nu"] - 1.395092021318097) < 1.0e-15
        assert abs(payload["live_outputs"]["dimensionless_ratio_dm21_over_dm32"] - 0.030721110097966534) < 1.0e-15
        assert payload["remaining_open_object"]["name"] == "source_derived_weighted_cycle_operator_and_basis_map"
        assert payload["audit"]["physical_basis_placement_derived"] is False
