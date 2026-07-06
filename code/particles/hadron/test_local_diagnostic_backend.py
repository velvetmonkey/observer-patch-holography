#!/usr/bin/env python3
"""Integration test for the local diagnostic hadron backend."""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SEQUENCE_POPULATION = ROOT / "particles" / "runs" / "hadron" / "stable_channel_sequence_population.json"
RECEIPT = ROOT / "particles" / "runs" / "hadron" / "runtime_schedule_receipt_N_therm_and_N_sep.json"
PAYLOAD = ROOT / "particles" / "runs" / "hadron" / "stable_channel_cfg_source_measure_payload.json"
BACKEND = ROOT / "particles" / "hadron" / "run_local_diagnostic_backend.py"
WRITEBACK = ROOT / "particles" / "hadron" / "run_production_backend_writeback.py"


def _copy_json(src: pathlib.Path, dst: pathlib.Path) -> None:
    payload = json.loads(src.read_text(encoding="utf-8"))
    dst.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_local_diagnostic_backend_exercises_pipeline_without_public_promotion() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        sequence_population_path = tmpdir / "sequence_population.json"
        receipt_path = tmpdir / "receipt.json"
        payload_path = tmpdir / "payload.json"
        backend_path = tmpdir / "local_diagnostic_backend_export.json"
        dump_path = tmpdir / "backend_correlator_dump.production.json"
        manifest_path = tmpdir / "oph_hadron_production_backend_manifest.json"
        evaluation_path = tmpdir / "stable_channel_sequence_evaluation.json"
        closure_path = tmpdir / "hadron_production_closure_validation_report.json"
        readiness_path = tmpdir / "hadron_production_readiness_report.json"

        _copy_json(SEQUENCE_POPULATION, sequence_population_path)
        _copy_json(RECEIPT, receipt_path)
        _copy_json(PAYLOAD, payload_path)

        subprocess.run(
            [
                sys.executable,
                str(BACKEND),
                "--receipt",
                str(receipt_path),
                "--payload",
                str(payload_path),
                "--output",
                str(backend_path),
                "--run-id",
                "pytest-local-diagnostic",
            ],
            check=True,
            cwd=ROOT,
        )
        backend_payload = json.loads(backend_path.read_text(encoding="utf-8"))
        assert backend_payload["execution_class"] == "diagnostic_surrogate"
        assert backend_payload["public_promotion_allowed"] is False

        subprocess.run(
            [
                sys.executable,
                str(WRITEBACK),
                "--sequence-population",
                str(sequence_population_path),
                "--receipt",
                str(receipt_path),
                "--payload",
                str(payload_path),
                "--backend-bundle",
                str(backend_path),
                "--dump-output",
                str(dump_path),
                "--manifest-output",
                str(manifest_path),
                "--evaluation-output",
                str(evaluation_path),
                "--closure-output",
                str(closure_path),
                "--readiness-output",
                str(readiness_path),
                "--n-therm",
                "2048",
                "--n-sep",
                "512",
                "--schedule-provenance",
                "pytest_local_diagnostic_backend",
            ],
            check=True,
            cwd=ROOT,
        )

        dump = json.loads(dump_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        closure = json.loads(closure_path.read_text(encoding="utf-8"))
        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))

        assert dump["production_execution"] is False
        assert dump["surrogate_execution"] is True
        assert dump["execution_class"] == "diagnostic_surrogate"
        assert manifest["execution_class"] == "diagnostic_surrogate"
        assert manifest["public_promotion_allowed"] is False

        first_ensemble = evaluation["ensemble_evaluations"][0]
        pi_mass = first_ensemble["pi_iso"]["mass_gev_candidate"]
        n_mass = first_ensemble["N_iso"]["mass_gev_candidate"]
        assert math.isfinite(float(pi_mass))
        assert math.isfinite(float(n_mass))
        assert first_ensemble["pi_iso"]["forward_window_limit_exists"] is True
        assert first_ensemble["N_iso"]["forward_window_limit_exists"] is True

        assert closure["public_unsuppression_ready"] is False
        assert closure["production_dump_present"] is False
        assert readiness["publication_bundle_ready"] is False
        assert readiness["smallest_backend_residual_object"] == (
            "real production backend execution class, not a diagnostic or surrogate backend bundle"
        )
