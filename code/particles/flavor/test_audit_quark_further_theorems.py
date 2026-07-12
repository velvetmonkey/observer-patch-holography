"""Regression tests for the audited further-theorem/QFRC boundary."""

from __future__ import annotations

from audit_quark_further_theorems import build_artifact


def test_finite_maxent_correction_and_countermodels() -> None:
    payload = build_artifact()
    result = payload["exact_results_retained"]["finite_maxent_non_gaussianity"]
    pair = result["same_mean_variance_countermodels"]
    assert pair["mean"] == "0"
    assert pair["variance"] == "1"
    assert pair["fourth_cumulant_a"] != pair["fourth_cumulant_b"]
    assert abs(float(result["finite_maxent_witness"]["fourth_cumulant"])) > 0.4


def test_qfrc_arithmetic_is_conditional_and_fail_closed() -> None:
    payload = build_artifact()
    qfrc = payload["qfrc_conditional_rigidity"]
    assert qfrc["primitive_path_weights"]["up_mean_quadratic"] == "1/29"
    assert qfrc["primitive_path_weights"]["down_endpoint_quadratic"] == "1/420"
    assert qfrc["physical_QF1_to_QF9_certificate_present"] is False
    assert payload["closure_effect"]["all_F1_to_F6_receipts_remain_open"] is True
    assert payload["closure_effect"]["numeric_quark_prediction_rows_allowed"] is False


def test_conditional_routes_are_not_misreported_as_exports() -> None:
    routes = build_artifact()["conditional_routes"]
    assert routes["refinement_gaussianization"]["status"] == "not_instantiated"
    assert routes["source_root"]["status"] == "schema_only_no_actual_map_or_interval_inclusion"
    assert routes["rg_transport"]["status"] == "standard_conditional_well_posedness_only"
