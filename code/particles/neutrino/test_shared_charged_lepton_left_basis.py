#!/usr/bin/env python3
"""Validate the shared charged-lepton left basis builder."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_shared_charged_lepton_left_basis.py"


def test_shared_charged_left_basis_closes_only_from_closed_nondegenerate_artifact() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_shared_charged_basis_") as tmpdir:
        tmp = pathlib.Path(tmpdir)
        source = tmp / "blind.json"
        out = tmp / "basis.json"
        source.write_text(
            json.dumps(
                {
                    "artifact": "oph_charged_lepton_blind_forward",
                    "closure_state": "closed",
                    "labels": ["f1", "f2", "f3"],
                    "singular_values_shape": [1.0, 2.0, 3.0],
                    "U_e_left": {
                        "real": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
                        "imag": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
                    },
                    "metadata": {"observable_artifact": "oph_flavor_observable"},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(source), "--output", str(out)],
            check=True,
            cwd=ROOT,
        )

        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["status"] == "closed"
        assert payload["theorem_status"] == "shape_closed_scale_invariant_left_basis"
        assert payload["basis_contract"]["orientation_preserved"] is True
        assert payload["basis_contract"]["physical_identification_closed"] is True
        assert payload["pmns_use_allowed"] is True
        assert payload["labels"] == ["f1", "f2", "f3"]


def test_open_nearly_degenerate_charged_artifact_cannot_close_pmns_basis() -> None:
    with tempfile.TemporaryDirectory(prefix="oph_open_charged_basis_") as tmpdir:
        tmp = pathlib.Path(tmpdir)
        source = tmp / "blind.json"
        out = tmp / "basis.json"
        source.write_text(
            json.dumps(
                {
                    "artifact": "oph_charged_lepton_blind_forward",
                    "closure_state": "open",
                    "labels": ["f1", "f2", "f3"],
                    "singular_values_shape": [
                        0.3333333333326792,
                        0.3333333333335484,
                        0.33333333333377224,
                    ],
                    "U_e_left": {
                        "real": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
                        "imag": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(source), "--output", str(out)],
            check=True,
            cwd=ROOT,
        )

        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["status"] == "open_upstream_charged_basis_not_identified"
        assert payload["theorem_status"] == "not_established"
        assert payload["pmns_use_allowed"] is False
        assert payload["basis_spectrum"]["nondegenerate"] is False
