"""Tests for the fail-closed blind charged-lepton prediction gate."""

from __future__ import annotations

import copy

import pytest

import derive_charged_blind_prediction_gate as gate


@pytest.fixture
def inputs():
    return (
        gate._load(gate.DEFAULT_ORDERED),
        gate._load(gate.DEFAULT_SCALARS),
        gate._load(gate.DEFAULT_TRANSPORT),
    )


def test_live_gate_fails_closed_without_mass_rows(inputs):
    artifact = gate.build_artifact(*inputs)
    assert artifact["status"] == "OPEN"
    assert artifact["public_promotion_allowed"] is False
    assert artifact["charged_mass_rows"] == []
    assert "eta_source_support_extension_log_per_side" in artifact["blockers"]
    assert "sigma_source_support_extension_total_log_per_side" in artifact["blockers"]


def test_current_support_has_only_order_one_direct_ratios(inputs):
    artifact = gate.build_artifact(*inputs)
    ratios = artifact["source_shape_gate"]["direct_current_support_ratio_diagnostic"]
    assert ratios["middle_over_light"] < 10.0
    assert ratios["heavy_over_light"] < 10.0
    assert artifact["source_shape_gate"]["direct_current_support_predictive_status"].startswith("rejected")


def test_target_fed_transport_cannot_close_normalization(inputs):
    artifact = gate.build_artifact(*inputs)
    normalization = artifact["normalization_gate"]
    assert normalization["closed"] is False
    assert "target_anchored_lepton_ratios_in_solve_path" in normalization["target_leaks"]
    assert "charged_mass_information_in_solve_path" in normalization["target_leaks"]


def test_even_hypothetical_source_scalars_require_clean_transport_and_freeze(inputs):
    ordered, scalars, transport = copy.deepcopy(inputs)
    scalars["eta_source_support_extension_log_per_side"] = 1.0
    scalars["sigma_source_support_extension_total_log_per_side"] = 2.0
    artifact = gate.build_artifact(ordered, scalars, transport)
    assert artifact["source_shape_gate"]["closed"] is True
    assert artifact["public_promotion_allowed"] is False
    assert artifact["freeze_gate"]["closed"] is False
