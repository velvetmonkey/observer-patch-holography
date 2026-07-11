#!/usr/bin/env python3
"""Regression checks for the independently refreshed PDG reference surface."""

from __future__ import annotations

import json
from pathlib import Path


PARTICLES = Path(__file__).resolve().parent
REFERENCE = PARTICLES / "data" / "particle_reference_values.json"
RESULTS = PARTICLES / "results_status.json"

MODEL_HEADLINE_VALUES_GEV = {
    "higgs": 125.1995304097179,
    "top_quark": 172.3523553288312,
    "tau": 1.77693246513409,
    "z_boson": 91.18797809193725,
}


def test_pdg_headline_references_are_not_model_outputs() -> None:
    payload = json.loads(REFERENCE.read_text(encoding="utf-8"))
    entries = payload["entries"]
    edition = str(payload["source"]["edition"])
    assert edition.isdigit()
    for particle, model_value in MODEL_HEADLINE_VALUES_GEV.items():
        entry = entries[particle]
        assert entry["source"]["edition"] == edition
        assert entry["source"]["summary_id"]
        assert entry["source"]["request_timestamp"]
        assert entry["value_gev"] != model_value
        assert entry["raw_value"] is not None
        assert entry["value_text"]


def test_tau_uncertainty_is_converted_to_gev() -> None:
    tau = json.loads(REFERENCE.read_text(encoding="utf-8"))["entries"]["tau"]
    assert tau["raw_unit"] == "MeV"
    assert 1.0e-5 < tau["error_plus_gev"] < 1.0e-3
    assert 1.0e-5 < tau["error_minus_gev"] < 1.0e-3


def test_public_status_uses_independent_references_and_withholds_headline_candidates() -> None:
    references = json.loads(REFERENCE.read_text(encoding="utf-8"))["entries"]
    rows = {
        row["particle_id"]: row
        for row in json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    }
    for particle in ("higgs", "top_quark", "tau"):
        assert rows[particle]["reference_value_gev"] == references[particle]["value_gev"]
        assert rows[particle]["prediction_value_gev"] is None
    d10 = json.loads(
        (PARTICLES / "runs/calibration/d10_ew_target_free_repair_value_law.json").read_text(
            encoding="utf-8"
        )
    )
    assert d10["compare_only_validation_against_frozen_surface"]["MZ_reference_gev"] == references["z_boson"]["value_gev"]


def test_d10_compare_surface_no_longer_reports_an_exact_pdg_coincidence() -> None:
    artifact = json.loads(
        (PARTICLES / "runs/calibration/d10_ew_target_free_repair_value_law.json").read_text(
            encoding="utf-8"
        )
    )
    comparison = artifact["compare_only_validation_against_frozen_surface"]
    assert abs(comparison["delta_MW_gev"]) > 1.0e-3
    assert abs(comparison["delta_MZ_gev"]) > 1.0e-5
    assert artifact["promotion_allowed"] is False
