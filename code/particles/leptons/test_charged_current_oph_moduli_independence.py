"""Tests for the current-OPH charged moduli independence theorem."""

from __future__ import annotations

import math

import derive_charged_current_oph_moduli_independence as lane


def test_natural_trace_and_one_bit_balance_are_distinct_admissible_laws():
    assert lane.koide_from_action_gap(0.0) == 1.0
    assert math.isclose(
        lane.koide_from_action_gap(math.log(2.0)),
        2.0 / 3.0,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_balanced_phase_is_not_selected_by_koide_or_determinant():
    artifact = lane.build_artifact()
    phase = artifact["distinct_failed_selector_audits"]["balanced_phase"]
    left = phase["countermodel_A"]
    right = phase["countermodel_B"]
    assert left["positive_simple_spectrum"] is True
    assert right["positive_simple_spectrum"] is True
    assert math.isclose(left["Q"], 2.0 / 3.0, rel_tol=0.0, abs_tol=1.0e-14)
    assert math.isclose(right["Q"], 2.0 / 3.0, rel_tol=0.0, abs_tol=1.0e-14)
    assert math.isclose(
        math.prod(left["determinant_normalized_masses"]),
        1.0,
        rel_tol=0.0,
        abs_tol=1.0e-13,
    )
    assert math.isclose(
        math.prod(right["determinant_normalized_masses"]),
        1.0,
        rel_tol=0.0,
        abs_tol=1.0e-13,
    )
    assert left["mass_ratios_to_lightest"] != right["mass_ratios_to_lightest"]
    assert not math.isclose(
        left["loop_phase_3delta_mod_2pi"],
        right["loop_phase_3delta_mod_2pi"],
        rel_tol=0.0,
        abs_tol=1.0e-14,
    )


def test_exact_family_has_two_independent_shape_directions_and_one_scale_direction():
    artifact = lane.build_artifact()
    family = artifact["independent_spectral_coordinate_family"]
    assert family["shape_jacobian_rank"] == 2
    assert family["full_log_jacobian_rank"] == 3
    assert family["base"]["positive_simple_spectrum"] is True
    assert family["x_direction"]["positive_simple_spectrum"] is True
    assert family["y_direction"]["positive_simple_spectrum"] is True
    for key in ("base", "x_direction", "y_direction"):
        assert math.isclose(
            family[key]["product_singular_values"],
            1.0,
            rel_tol=0.0,
            abs_tol=1.0e-14,
        )
    assert family["base"]["centered_log_singular_values"] != family["x_direction"]["centered_log_singular_values"]
    assert family["base"]["centered_log_singular_values"] != family["y_direction"]["centered_log_singular_values"]


def test_common_shift_preserves_shape_and_changes_determinant():
    artifact = lane.build_artifact()
    scale = artifact["distinct_failed_selector_audits"]["common_affine_scale"]
    assert all(
        math.isclose(left, right, rel_tol=0.0, abs_tol=1.0e-14)
        for left, right in zip(scale["centered_logs_Y0"], scale["centered_logs_Y1"], strict=True)
    )
    assert math.isclose(scale["determinant_Y0"], 1.0, rel_tol=0.0, abs_tol=1.0e-14)
    assert math.isclose(scale["determinant_Y1"], 8.0, rel_tol=0.0, abs_tol=1.0e-13)


def test_z6_residues_do_not_select_absolute_exponent_lengths():
    artifact = lane.build_artifact()
    exponents = artifact["distinct_failed_selector_audits"]["z6_defect_lengths"]
    assert exponents["residues_mod_6_A"] == exponents["residues_mod_6_B"]
    assert exponents["sum_A"] == 14
    assert exponents["sum_B"] == 32


def test_current_signature_is_explicitly_nonpromoting():
    artifact = lane.build_artifact()
    assert artifact["runtime_charged_reference_packet_consumed"] is False
    assert artifact["historical_target_informed_examples_present"] is True
    assert artifact["public_charged_mass_promotion_allowed"] is False
    assert artifact["status"] == (
        "CLOSED_SCOPED_CHARGED_SIGNATURE_NONIDENTIFIABILITY_CERTIFICATE"
    )


def test_scope_excludes_mass_dependent_em_transport_and_binds_receipts():
    artifact = lane.build_artifact()
    excluded = " ".join(artifact["scope"]["excluded"])
    assert "electromagnetic" in excluded
    assert len(artifact["source_receipt_bindings"]) == len(lane.RECEIPTS)
    assert all(len(binding["sha256"]) == 64 for binding in artifact["source_receipt_bindings"])
    assert artifact["source_scope_checks_pass"] is True
    assert all(artifact["source_scope_checks"].values())


def test_attachment_claim_is_relative_to_an_independent_family_observable():
    artifact = lane.build_artifact()
    attachment = artifact["distinct_failed_selector_audits"]["family_attachment"]
    assert "separately fixed physical family observable" in attachment["changed"]
    assert "unordered mass triple" in attachment["boundary"]
