"""Tests for the compare-only charged nature/pole theorem audit."""

from __future__ import annotations

import json

import pytest

import audit_charged_nature_pole_theorem_v1 as lane


pytestmark = pytest.mark.skipif(
    not lane.DEFAULT_ARCHIVE.exists(),
    reason="external correspondence archive is not present in this workspace snapshot",
)


def review() -> dict:
    return lane.build_review(lane.DEFAULT_ARCHIVE, lane.PARENT_REVIEW)


def test_archive_is_safe_hash_bound_and_reconstructs_endpoint():
    result = review()
    assert result["archive"]["checks_pass"] is True
    assert result["archive"]["member_count"] == 20
    assert result["finite_face_endpoint_reconstruction"]["checks_pass"] is True
    assert result["provenance"]["archive_sha256"] == lane.EXPECTED_ARCHIVE_SHA256


def test_conditional_bridge_is_valid_but_load_bearing_equalities_are_premises():
    result = review()
    boundary = result["conditional_theorem_boundary"]
    checks = boundary["checks"]
    assert checks["regular_C3_character_lemma_valid"] is True
    assert checks["positive_square_root_transport_valid"] is True
    assert checks["NI6_assumes_physical_Yukawa_response_equals_face_response"] is True
    assert checks["RP4_assumes_singularity_readout_equals_face_response"] is True
    assert checks["substantive_necessary_and_sufficient_OPH_derivation_proved"] is False


def test_all_physical_nature_and_interacting_kernel_gates_remain_open():
    result = review()
    checks = result["physical_gate_status"]["checks"]
    assert checks["all_NI_physical_gates_open"] is True
    assert checks["all_RP_physical_gates_open"] is True
    assert result["physical_nature_identification_proved"] is False
    assert result["interacting_pole_kernel_proved"] is False
    assert result["mass_scheme_certified"] is False
    assert result["public_prediction_promotion_allowed"] is False


def test_submitted_verifier_does_not_bind_mass_operator_to_response_shape():
    result = review()
    boundary = result["submitted_verifier_boundary"]
    assert boundary["submitted_verifier_binds_M_to_g_end_times_response_shape"] is False
    assert boundary["submitted_verifier_binds_parent_artifact_hashes"] is False
    assert boundary["same_product_alternate_spectrum_exists"] is True


def test_parent_candidate_remains_hybrid_and_target_informed():
    result = review()
    checks = result["provenance_and_branch_boundary"]["checks"]
    assert checks["historical_target_exposure_declared"] is True
    assert checks["prospective_prediction_status_rejected"] is True
    assert checks["parent_artifacts_hash_bound_in_bundle"] is False
    assert checks["parent_candidate_branch_coherent"] is False
    assert result["global_source_only"] is False
    assert result["branch_tuple_coherent"] is False


def test_committed_review_is_byte_reproducible():
    result = review()
    expected = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    assert lane.DEFAULT_OUT.read_bytes() == expected
