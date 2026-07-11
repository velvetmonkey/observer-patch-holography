#!/usr/bin/env python3
"""Validate the repaired neutrino absolute-amplitude bridge audit."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_weighted_cycle_absolute_amplitude_bridge.py"
REPAIR = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"
ANCHOR = ROOT / "particles" / "runs" / "neutrino" / "neutrino_scale_anchor.json"


def test_absolute_amplitude_bridge_remains_open_but_direct_anchor_is_diagnostic() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_neutrino_amp_bridge_") as tmpdir:
        out = pathlib.Path(tmpdir) / "bridge.json"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repair",
                str(REPAIR),
                "--scale-anchor",
                str(ANCHOR),
                "--output",
                str(out),
            ],
            check=True,
            cwd=ROOT,
        )
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["artifact"] == "oph_neutrino_weighted_cycle_absolute_amplitude_bridge"
        assert payload["status"] == "conditional_scale_audit_on_rejected_source_open_candidate"
        assert payload["public_promotion_allowed"] is False
        assert payload["first_physical_missing_object"] == "source_closed_neutrino_operator_basis_and_mass_label_contract"
        assert payload["remaining_object"] == "neutrino_weighted_cycle_absolute_amplitude_bridge"
        assert payload["direct_scale_anchor_attachment_diagnostic"]["candidate_rule"] == "lambda_nu = m_star_eV"
        assert payload["direct_scale_anchor_attachment_diagnostic"]["status"] == "diagnostic_only_nonpromotable"
        assert payload["equivalent_scalar"]["name"] == "lambda_nu"
