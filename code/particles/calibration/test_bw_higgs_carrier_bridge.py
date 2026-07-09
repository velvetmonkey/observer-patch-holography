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


def test_bw_higgs_carrier_bridge_is_minimal_carrier_not_mass_theorem() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_bw_higgs_") as tmpdir:
        out = pathlib.Path(tmpdir) / "bw_higgs_carrier_bridge.json"
        subprocess.run([sys.executable, str(SCRIPT), "--output", str(out)], check=True, cwd=ROOT)
        payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_bw_higgs_carrier_bridge"
    assert payload["BOREL_WEIL_HIGGS_CARRIER_RECEIPT"] is True
    assert payload["carrier"]["section_degree_n"] == 1
    assert payload["carrier"]["complex_dimension"] == 2
    assert payload["carrier"]["real_degrees_of_freedom"] == 4
    assert payload["representation"]["Y_H"] == 0.5
    assert payload["representation"]["Q_phi0"] == 0.0
    assert payload["symmetry_breaking_geometry"]["goldstone_count"] == 3
    assert payload["symmetry_breaking_geometry"]["radial_higgs_modes"] == 1
    assert "Higgs mass m_H" in payload["explicit_nonclaims"]
    assert "weak scale v" in payload["explicit_nonclaims"]
