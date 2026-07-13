"""Tests for the conditional OPH orientation-isometry Koide theorem."""

from __future__ import annotations

import math

import derive_charged_koide_orientation_isometry as lane


def test_two_orientation_isometry_forces_koide_balance() -> None:
    modulus = lane.orientation_isometry_modulus(2)
    assert math.isclose(modulus, 1.0 / math.sqrt(2.0), rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(
        lane.koide_from_modulus_ratio(modulus),
        2.0 / 3.0,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_uniform_physical_blocks_differ_from_uniform_microstates() -> None:
    assert lane.quotient_block_weights((1, 2)) == (0.5, 0.5)
    assert lane.lifted_micro_weights((1, 2)) == ((0.5,), (0.25, 0.25))


def test_connected_m6_event_and_gns_square_root_force_balance() -> None:
    source_dimension, z0_rank, zc_rank, admitted_rank = (
        lane.connected_register_event_ranks()
    )
    assert (source_dimension, z0_rank, zc_rank, admitted_rank) == (6, 2, 2, 4)
    p0, pc = lane.born_lueders_block_probabilities(z0_rank, zc_rank)
    assert (p0, pc) == (0.5, 0.5)
    modulus = lane.gns_modulus_from_block_probabilities(p0, pc)
    assert math.isclose(modulus, 1.0 / math.sqrt(2.0), abs_tol=1.0e-15)
    assert math.isclose(
        lane.koide_from_action_gap(math.log(2.0)),
        2.0 / 3.0,
        abs_tol=1.0e-15,
    )
    assert lane.c3_gns_gram_matrix() == (
        (1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j),
        (0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j),
        (0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j),
    )


def test_symmetry_without_isometry_leaves_continuous_countermodels() -> None:
    assert not math.isclose(
        lane.koide_from_modulus_ratio(0.4),
        lane.koide_from_modulus_ratio(0.6),
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )
    for ratio in (0.4, 0.6, lane.orientation_isometry_modulus(2)):
        assert math.isclose(
            abs(lane.koide_from_modulus_ratio(ratio) - 2.0 / 3.0),
            abs(lane.response_isometry_defect(ratio)) / 3.0,
            rel_tol=0.0,
            abs_tol=1.0e-15,
        )


def test_phase_independence_requires_the_positive_root_chamber() -> None:
    modulus = lane.orientation_isometry_modulus(2)
    for phase in (0.0, 0.1, 2.0 / 9.0):
        roots = lane.circulant_roots(modulus, phase)
        assert lane.balanced_positive_chamber(phase)
        assert min(roots) >= 0.0
        assert math.isclose(
            lane.physical_koide_from_roots(roots),
            2.0 / 3.0,
            rel_tol=0.0,
            abs_tol=1.0e-14,
        )

    roots = lane.circulant_roots(modulus, 0.4)
    assert not lane.balanced_positive_chamber(0.4)
    assert min(roots) < 0.0
    assert not math.isclose(
        lane.physical_koide_from_roots(roots),
        2.0 / 3.0,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_physical_attachment_remains_open() -> None:
    artifact = lane.build_artifact()
    assert artifact["checks_pass"] is True
    assert artifact["charged_reference_data_consumed"] is False
    assert artifact["public_koide_promotion_allowed"] is False
    assert artifact["status"] == (
        "CLOSED_FINITE_TRACIAL_GNS_KOIDE_THEOREM_"
        "PHYSICAL_CHIRAL_RECOVERY_ATTACHMENT_OPEN"
    )
    assert artifact["open_physical_gate"]["derived"] is False
    assert lane.c3_trivial_to_charged_intertwiner_dimension() == 0
