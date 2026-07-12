"""Tests for the exact A5/W5 twelve-port representation frontier."""

from __future__ import annotations

import math

import derive_charged_a5_w5_port_frontier as lane


def test_vertex_representation_decomposes_as_one_three_three_prime_five():
    assert lane.vertex_representation_multiplicities() == {
        "1": 1,
        "3": 1,
        "3_prime": 1,
        "4": 0,
        "5": 1,
    }


def test_first_and_quadrupole_maps_see_exactly_three_and_five_dimensions():
    checks = lane.moment_map_checks()
    assert checks["first_moment_map_rank"] == 3
    assert checks["quadrupole_map_rank"] == 5
    assert checks["singlet_plus_first_plus_quadrupole_rank"] == 9
    assert checks["unseen_complement_dimension"] == 3


def test_uniform_and_orientation_only_singlets_have_zero_quadrupole():
    checks = lane.moment_map_checks()
    assert checks["uniform_first_moment_norm"] < 1.0e-12
    assert checks["uniform_quadrupole_norm"] < 1.0e-12
    assert checks["orientation_even_quadrupole_norm"] < 1.0e-12
    assert checks["orientation_odd_quadrupole_norm"] < 1.0e-12


def test_exact_antipodal_projector_and_schur_normalization():
    checks = lane.w5_projector_checks()
    assert checks["antipode_is_involution_residual"] < 1.0e-12
    assert checks["P5_rank"] == 5
    assert checks["P5_projector_residual"] < 1.0e-12
    assert checks["Q_star_Q_minus_8_over_5_P5_norm"] < 1.0e-12
    assert checks["P3_rank"] == 3
    assert checks["P3_projector_residual"] < 1.0e-12
    assert checks["first_star_first_minus_4P3_norm"] < 1.0e-12


def test_nonuniform_antipodal_odd_record_still_has_no_quadrupole():
    checks = lane.w5_projector_checks()
    assert checks["antipodal_odd_nonuniform_Q_norm"] < 1.0e-12
    assert checks["example_even_W5_norm"] > 1.0e-6
    assert checks["example_even_quadrupole_norm"] > 1.0e-6


def test_traceless_discriminant_detects_simple_spectrum():
    assert lane.traceless_cubic_discriminant((-2.0, -0.5, 2.5)) > 0.0
    assert math.isclose(
        lane.traceless_cubic_discriminant((-1.0, -1.0, 2.0)),
        0.0,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_artifact_is_source_only_and_fail_closed():
    screen = {
        "orbit_stabilizer": {"orbit_size": 12},
    }
    round_count = {
        "result": {"m_rep": 24},
    }
    artifact = lane.build_artifact(screen, round_count)
    assert artifact["checks_pass"] is True
    assert artifact["charged_reference_data_consumed"] is False
    assert artifact["public_charged_mass_promotion_allowed"] is False
    assert artifact["why_12_24_does_not_derive_the_stage5_determinant"]["z6_projector_check"][
        "normalized_trivial_character_average"
    ] == 1.0
    assert artifact["status"] == "CLOSED_A5_REPRESENTATION_FRONTIER_W5_REQUIRED_AND_ABSENT"
