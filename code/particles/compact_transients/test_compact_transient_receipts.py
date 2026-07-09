#!/usr/bin/env python3
"""Smoke-test the compact-transient receipt scaffold."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "compact_transients" / "build_compact_transient_receipts.py"


def test_build_compact_transient_receipts(tmp_path: pathlib.Path) -> None:
    out_dir = tmp_path / "compact_transients"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(out_dir)],
        check=True,
        cwd=ROOT,
    )

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["milestone"] == "COMPACT_TRANSIENT_RECEIPT_SCAFFOLD"
    assert manifest["strongest_allowed_claim"] == "CR2_CONDITIONAL_PHENOMENOLOGY"
    assert manifest["first_blocked_gate"] == "CONTROLS"
    assert manifest["promotion_allowed"] is False
    assert manifest["physical_claim"] is False
    assert manifest["missing_files"] == []

    for rel_path in manifest["required_files"]:
        assert (out_dir / rel_path).is_file(), rel_path

    frb = json.loads((out_dir / "frb_controls.json").read_text(encoding="utf-8"))
    assert frb["controls"]["M2"] == "young_plus_old_gc_repair_reload_timing"

    bh = json.loads((out_dir / "bh_recycling.json").read_text(encoding="utf-8"))
    assert bh["genealogy_dag_required"] is True
    assert "ringdown_residual" in bh["forbidden_path"]


def test_rejects_ringdown_residual_as_generation_prior_input(tmp_path: pathlib.Path) -> None:
    config = tmp_path / "source_config.json"
    config.write_text(json.dumps({"inputs": ["ringdown_residual"]}), encoding="utf-8")
    out_dir = tmp_path / "leaky"

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--output",
            str(out_dir),
            "--config",
            str(config),
        ],
        check=True,
        cwd=ROOT,
    )

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    audit = json.loads((out_dir / "promotion_audit.json").read_text(encoding="utf-8"))
    assert manifest["strongest_allowed_claim"] == "CR1_QUOTIENT_DIAGNOSTIC"
    assert manifest["first_blocked_gate"] == "NO_GENERATION_LEAKAGE_RECEIPT"
    assert "ringdown_residual" in manifest["target_leak_hits"]
    assert audit["readiness_gates"]["NO_GENERATION_LEAKAGE_RECEIPT"] is False
