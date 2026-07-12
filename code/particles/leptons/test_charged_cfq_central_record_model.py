"""Tests for the canonical formal CFQ central-record model."""

from __future__ import annotations

import json

import derive_charged_cfq_central_record_model as lane


def artifact() -> dict:
    raw = lane.CONDITIONAL_CFQ.read_bytes()
    return lane.build_artifact(json.loads(raw), lane.sha256(raw))


def test_ten_event_occurrences_and_central_records_are_exact():
    result = artifact()
    occurrences = result["event_occurrences"]
    assert len(occurrences) == 10
    assert len({row["id"] for row in occurrences}) == 10
    assert all(row["event_rank"] == 1 for row in occurrences)
    assert all(all(row["pinching_properties"].values()) for row in occurrences)
    assert all(row["central_pointer_algebra"].startswith("D2") for row in occurrences)


def test_path_products_and_inert_refinements_match_exactly():
    result = artifact()
    assert [row["signed_trace_product"] for row in result["path_models"]] == [
        "1/50",
        "-1/31",
        "-1/310",
        "1/512",
        "1/77",
        "1/21",
        "1/27",
        "1/135",
    ]
    assert all(row["matches_schema"] for row in result["path_models"])
    assert len(result["inert_refinement_checks"]) == 16
    assert all(row["trace_preserved"] for row in result["inert_refinement_checks"])


def test_formal_model_does_not_promote_physical_selection():
    result = artifact()
    assert not any(result["physical_selection_gates"].values())
    assert result["scope_boundary"]["global_response_update_constructed"] is False
    assert result["scope_boundary"]["physical_regulator_refinement_constructed"] is False
    assert result["scope_boundary"]["historical_ancestry_repaired"] is False
    assert result["historical_charged_target_informed"] is True
    assert result["global_source_only"] is False
    assert result["public_prediction_promotion_allowed"] is False
    assert result["checks_pass"] is True


def test_committed_receipt_is_byte_reproducible():
    result = artifact()
    expected = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    assert lane.DEFAULT_OUT.read_bytes() == expected
