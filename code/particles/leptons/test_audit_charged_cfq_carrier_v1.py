"""Tests for the compare-only finite CFQ carrier archive audit."""

from __future__ import annotations

import json
import pytest

import audit_charged_cfq_carrier_v1 as lane


pytestmark = pytest.mark.skipif(
    not lane.DEFAULT_ARCHIVE.exists(),
    reason="external correspondence archive is not present in this workspace snapshot",
)


def review() -> dict:
    return lane.build_review(lane.DEFAULT_ARCHIVE, lane.CANONICAL_CFQ)


def test_archive_is_safe_hash_bound_and_crc_clean():
    result = review()
    assert result["archive"]["checks_pass"] is True
    assert all(result["archive"]["checks"].values())
    assert result["archive"]["member_count"] == 46
    assert result["provenance"]["archive_sha256"] == lane.EXPECTED_ARCHIVE_SHA256


def test_finite_digital_model_exports_reproduce_exactly():
    result = review()
    model = result["verified_digital_model"]
    assert model["explicit_finite_model_exists"] is True
    assert model["model_relative_submitted_cfq_gate_count"] == 8
    assert model["checks_pass"] is True
    assert sum(model["matrix_unit_counts"].values()) == 6467
    assert all(model["matrix_unit_checks"].values())
    assert all(model["paths"].values())
    assert all(
        all(row.values()) for row in model["register_graphs"].values()
    )
    assert "accepted/rejected central D2" in model["central_record_resolution"]


def test_model_relative_pass_does_not_promote_source_or_ancestry():
    result = review()
    boundary = result["historical_and_physical_boundary"]
    assert boundary["submitted_no_target_ancestry_claim_accepted"] is False
    assert boundary["checks"]["strict_historical_no_target_ancestry_pass"] is False
    assert boundary["checks"]["physical_charged_sector_identified_with_constructed_patch"] is False
    assert boundary["checks"]["five_oph_axioms_uniquely_select_constructed_patch"] is False
    assert result["historical_charged_target_informed"] is True
    assert result["global_source_only"] is False
    assert result["branch_tuple_coherent"] is False
    assert result["mass_scheme_certified"] is False
    assert result["public_prediction_promotion_allowed"] is False


def test_verifier_and_negative_control_limitations_are_frozen():
    result = review()
    reproduction = result["independent_reproduction_observation"]
    assert reproduction["semantic_rebuild_passed_all_submitted_gates"] is True
    assert reproduction["adversarial_source_law_and_provenance_binding_passed"] is False
    assert reproduction["byte_reproducible_across_tested_python_numpy_environment"] is False
    assert "accepts any nonzero verifier exit" in result["verified_digital_model"][
        "negative_control_harness_boundary"
    ]
    assert "declared by the builder" in result["verified_digital_model"][
        "path_exhaustion_scope"
    ]


def test_committed_review_is_byte_reproducible():
    result = review()
    expected = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    assert lane.DEFAULT_OUT.read_bytes() == expected
