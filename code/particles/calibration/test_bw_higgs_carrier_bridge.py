#!/usr/bin/env python3
"""Validate the Borel-Weil one-Higgs carrier bridge artifact."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "calibration" / "derive_bw_higgs_carrier_bridge.py"


def _build_at_phase(phase: float) -> dict:
    with tempfile.TemporaryDirectory(prefix="oph_bw_higgs_") as tmpdir:
        out = pathlib.Path(tmpdir) / "bw_higgs_carrier_bridge.json"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--output",
                str(out),
                "--acceptance-phase",
                str(phase),
            ],
            check=True,
            cwd=ROOT,
        )
        return json.loads(out.read_text(encoding="utf-8"))


def test_bw_higgs_carrier_bridge_is_minimal_carrier_not_mass_theorem() -> None:
    payload = _build_at_phase(0.731)

    assert payload["artifact"] == "oph_bw_higgs_carrier_bridge"
    assert payload["BOREL_WEIL_HIGGS_CARRIER_RECEIPT"] is True
    assert payload["carrier"]["section_degree_n"] == 1
    assert payload["carrier"]["complex_dimension"] == 2
    assert payload["carrier"]["real_degrees_of_freedom"] == 4
    assert payload["representation"]["Y_H"] == 0.5
    assert payload["representation"]["Q_phi0"] == 0.0
    geometry = payload["symmetry_breaking_geometry"]
    assert geometry["projective_ray_stabilizer"] == "(U(1)_T3 x U(1)_Y)/finite_center"
    assert geometry["projective_stabilizer_dimension"] == 2
    assert geometry["projective_orbit_dimension"] == 2
    assert geometry["projectivization_forgets_scalar_hypercharge_phase"] is True
    assert geometry["vector_stabilizer"] == "U(1)_Q"
    assert geometry["vector_stabilizer_generator"] == "Q = T3 + Y"
    assert geometry["vector_stabilizer_dimension"] == 1
    assert geometry["broken_generator_count"] == 3
    assert geometry["goldstone_count"] == 3
    assert geometry["radial_higgs_modes"] == 1
    assert "Higgs mass m_H" in payload["explicit_nonclaims"]
    assert "weak scale v" in payload["explicit_nonclaims"]


def test_ray_and_vector_stabilizer_acceptance_for_arbitrary_hypercharge_phases() -> None:
    for phase in (0.173, 0.731, 1.417):
        acceptance = _build_at_phase(phase)["group_action_acceptance"]
        assert acceptance["hypercharge_phase_is_nontrivial"] is True
        assert acceptance["pure_hypercharge_fixes_projective_ray"] is True
        assert acceptance["pure_hypercharge_fixes_vacuum_vector"] is False
        assert acceptance["pure_T3_fixes_projective_ray"] is True
        assert acceptance["pure_T3_fixes_vacuum_vector"] is False
        assert acceptance["diagonal_Q_fixes_vacuum_vector"] is True
