"""Tests for the fail-closed electroweak physical-readout gate."""

from __future__ import annotations

from ew_physical_readout_gate import (
    REQUIRED_TARGET_FIELDS,
    REQUIRED_THEORY_FIELDS,
    classify_physical_comparison,
)


def complete_contract() -> dict:
    return {
        "theory": {field: f"closed:{field}" for field in REQUIRED_THEORY_FIELDS},
        "target": {field: f"closed:{field}" for field in REQUIRED_TARGET_FIELDS},
        "observable_identity_receipt": "sha256:synthetic-test-receipt",
    }


def test_historical_packet_without_contract_is_not_evaluable():
    status = classify_physical_comparison(
        {"fail_closed_gates_declared_open": ["GATE-PP-05: vev scheme open"]}
    )
    assert status["status"] == "NOT_EVALUABLE"
    assert status["physical_pull_allowed"] is False
    assert "physical_readout_contract" in status["blockers"][
        "missing_or_open_contract_fields"
    ]


def test_complete_contract_remains_blocked_by_declared_open_gate():
    status = classify_physical_comparison(
        {
            "fail_closed_gates_declared_open": ["GATE-THRESHOLD"],
            "physical_readout_contract": complete_contract(),
        }
    )
    assert status["status"] == "NOT_EVALUABLE"
    assert status["blockers"]["declared_open_gates"] == ["GATE-THRESHOLD"]


def test_mismatched_observable_fails_closed():
    contract = complete_contract()
    contract["theory"]["output_observable"] = "complex_pole"
    contract["target"]["observable"] = "mass_dependent_width_breit_wigner"
    status = classify_physical_comparison(
        {"fail_closed_gates_declared_open": []}, contract
    )
    assert status["status"] == "NOT_EVALUABLE"
    assert "observable_identity_receipt" in status["blockers"][
        "missing_or_open_contract_fields"
    ]


def test_complete_same_observable_contract_is_evaluable():
    contract = complete_contract()
    contract["theory"]["output_observable"] = "complex_pole"
    contract["target"]["observable"] = "complex_pole"
    status = classify_physical_comparison(
        {"fail_closed_gates_declared_open": []}, contract
    )
    assert status["status"] == "EVALUABLE"
    assert status["physical_pull_allowed"] is True

