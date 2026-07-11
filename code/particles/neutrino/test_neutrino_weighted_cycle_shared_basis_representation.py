#!/usr/bin/env python3
"""Validate the weighted-cycle shared-basis audit."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_weighted_cycle_shared_basis_representation.py"
WEIGHTED_CYCLE = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"
SHARED_CHARGED_LEFT = ROOT / "particles" / "runs" / "neutrino" / "shared_charged_lepton_left_basis.json"


def test_weighted_cycle_shared_basis_transport_is_flagged_as_tautological() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_neutrino_shared_basis_repr_") as tmpdir:
        out = pathlib.Path(tmpdir) / "representation.json"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--weighted-cycle",
                str(WEIGHTED_CYCLE),
                "--shared-charged-left",
                str(SHARED_CHARGED_LEFT),
                "--output",
                str(out),
            ],
            check=True,
            cwd=ROOT,
        )
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["artifact"] == "oph_neutrino_weighted_cycle_shared_basis_representation"
        assert payload["status"] == "basis_placement_open_tautological_transport_audit"
        assert payload["physical_branch_closed"] is False
        assert payload["public_surface_candidate_allowed"] is False
        assert payload["basis_placement_source_derived"] is False
        assert payload["transport_checks"]["shared_basis_symmetry_max_abs"] < 1.0e-12
        assert payload["transport_checks"]["shared_basis_diagonalized_offdiag_max_abs"] < 1.0e-12
        assert payload["transport_checks"]["shared_basis_diagonalized_imag_max_abs"] < 1.0e-12
        assert payload["transport_checks"]["pmns_recovery_max_abs"] < 1.0e-12
        assert abs(payload["weighted_cycle_observables_match"]["theta12_deg_abs_delta"]) < 1.0e-10
        assert abs(payload["weighted_cycle_observables_match"]["theta23_deg_abs_delta"]) < 1.0e-10
        assert abs(payload["weighted_cycle_observables_match"]["theta13_deg_abs_delta"]) < 1.0e-10
        assert abs(payload["weighted_cycle_observables_match"]["delta_deg_abs_delta"]) < 1.0e-10
        assert payload["source_artifacts"]["weighted_cycle_branch"] == "code/particles/runs/neutrino/neutrino_weighted_cycle_repair.json"
        assert payload["source_artifacts"]["shared_charged_left_basis"] == "code/particles/runs/neutrino/shared_charged_lepton_left_basis.json"
        assert payload["pmns_matrix_real"][0][0] > 0.0
        assert payload["pmns_matrix_real"][0][1] > 0.0
        assert payload["pmns_matrix_real"][0][2] > 0.0
        assert payload["emitted_parameters"] is None
        assert payload["basis_audit"]["historical_recovery_is_tautology"] is True
        assert payload["basis_audit"]["historical_recovery_independent_empirical_content"] is False
        literal = payload["basis_audit"]["literal_source_basis_pmns_observables"]
        assert abs(literal["theta13_deg"] - 44.828312032869384) < 1.0e-9
        assert abs(literal["theta23_deg"] - 76.27586231032956) < 1.0e-9
