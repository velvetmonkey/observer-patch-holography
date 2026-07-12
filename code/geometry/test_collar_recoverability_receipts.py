#!/usr/bin/env python3
"""Focused tests for the issue-307 collar recoverability finite proxy."""

from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from collar_recoverability_receipts import (  # noqa: E402
    REPORT_PATH,
    FiniteRangeGibbsMixingConstants,
    PowerLawBoundarySchedule,
    build_report,
    collar_log_bound,
    collar_log_bound_from_log_boundary,
    counterexample_receipt,
    finite_stage_receipt,
    full_rate_margin,
    sharp_geometric_margin,
    stable_exp,
    sufficient_schedule_receipt,
)


@pytest.fixture
def constants() -> FiniteRangeGibbsMixingConstants:
    return FiniteRangeGibbsMixingConstants(
        ell_uv=0.01,
        beta=0.8,
        local_hilbert_dimension=2,
        coordination_number_bound=4,
        interaction_strength_bound=1.2,
        interaction_range_steps=2.0,
        mixing_prefactor_kappa=3.0,
        mixing_length_steps_zeta=1.5,
    )


def test_finite_range_constants_and_physical_dictionary(constants):
    assert constants.interaction_range == pytest.approx(0.02)
    assert constants.correlation_length_xi == pytest.approx(0.015)
    assert constants.continuum_prefactor_c == pytest.approx(
        3.0 * math.exp(2.0 / 1.5)
    )
    with pytest.raises(ValueError, match="local_hilbert_dimension"):
        replace(constants, local_hilbert_dimension=1)
    with pytest.raises(ValueError, match="mixing_length_steps_zeta"):
        replace(constants, mixing_length_steps_zeta=0.0)


def test_log_bound_equals_envelope_and_negative_full_margin(constants):
    boundary = 128.0
    m = 17.0
    expected_log = math.log(3.0 * boundary) - (m - 2.0) / 1.5
    direct = collar_log_bound(
        boundary_size_uv=boundary,
        collar_width_steps=m,
        constants=constants,
    )
    logged = collar_log_bound_from_log_boundary(
        log_boundary_size=math.log(boundary),
        collar_width_steps=m,
        constants=constants,
    )
    assert direct == pytest.approx(expected_log)
    assert logged == pytest.approx(expected_log)
    assert full_rate_margin(
        log_boundary_size=math.log(boundary),
        collar_width_steps=m,
        constants=constants,
    ) == pytest.approx(-expected_log)
    assert stable_exp(logged) == pytest.approx(
        3.0 * boundary * math.exp(-(m - 2.0) / 1.5)
    )


def test_bound_is_stable_at_extreme_log_scales(constants):
    assert stable_exp(-1000.0) == 0.0
    assert stable_exp(1000.0) == math.inf
    # A huge boundary can be handled without constructing its cardinality.
    log_bound = collar_log_bound_from_log_boundary(
        log_boundary_size=10000.0,
        collar_width_steps=20000.0,
        constants=constants,
    )
    assert math.isfinite(log_bound)
    assert log_bound < 0.0


def test_mixing_envelope_rejects_collars_shorter_than_range(constants):
    with pytest.raises(ValueError, match="interaction_range_steps"):
        collar_log_bound_from_log_boundary(
            log_boundary_size=0.0,
            collar_width_steps=1.999,
            constants=constants,
        )


def test_physical_and_lattice_forms_are_identical(constants):
    m = 23.0
    log_boundary = math.log(500.0)
    receipt = finite_stage_receipt(
        log_boundary_size=log_boundary,
        collar_width_steps=m,
        constants=constants,
    )
    physical_log_bound = (
        math.log(constants.continuum_prefactor_c)
        + log_boundary
        - receipt["physical_collar_width_delta"]
        / constants.correlation_length_xi
    )
    assert receipt["log_cmi_upper_bound_nats"] == pytest.approx(
        physical_log_bound
    )
    assert receipt["sharp_geometric_margin"] == pytest.approx(
        receipt["physical_collar_width_delta"]
        / constants.correlation_length_xi
        - log_boundary
    )


def test_power_law_schedule_has_declared_rate_margin(constants):
    schedule = PowerLawBoundarySchedule(
        ell0=1.0,
        boundary_prefactor=5.0,
        boundary_power=2.0,
        eta=0.4,
    )
    logs = (5.0, 10.0, 20.0, 40.0)
    receipt = sufficient_schedule_receipt(
        log_refinements=logs,
        constants=constants,
        schedule=schedule,
    )
    for stage, log_refinement in zip(receipt["stages"], logs):
        expected_log_bound = (
            math.log(constants.mixing_prefactor_kappa * 5.0)
            + constants.interaction_range_steps
            / constants.mixing_length_steps_zeta
            - 0.4 * log_refinement
        )
        assert stage["finite_range_floor_active"] is False
        assert stage["log_cmi_upper_bound_nats"] == pytest.approx(
            expected_log_bound
        )
        assert stage["analytic_log_bound_from_schedule"] == pytest.approx(
            expected_log_bound
        )
        assert stage["schedule_threshold_delta"] == pytest.approx(
            constants.mixing_length_steps_zeta
            * stage["ell_uv"]
            * (2.0 + 0.4)
            * log_refinement
        )
    checks = receipt["finite_proxy_checks"]
    assert checks["log_bounds_strictly_decrease"] is True
    assert checks["full_rate_margins_strictly_increase"] is True
    assert checks["width_ratio_increases"] is True
    assert checks["physical_delta_decreases_on_displayed_tail"] is True


def test_sharp_criterion_tracks_boundary_growth(constants):
    # The width may grow while the sharp margin fails if log boundary grows
    # even faster.
    narrow_margin = sharp_geometric_margin(
        log_boundary_size=100.0,
        collar_width_steps=120.0,
        constants=replace(constants, mixing_length_steps_zeta=1.0),
    )
    wide_margin = sharp_geometric_margin(
        log_boundary_size=250.0,
        collar_width_steps=200.0,
        constants=replace(constants, mixing_length_steps_zeta=1.0),
    )
    assert narrow_margin == pytest.approx(20.0)
    assert wide_margin == pytest.approx(-50.0)


def test_explicit_counterexample_rejects_width_ratio_alone():
    receipt = counterexample_receipt(range(2, 10))
    stages = receipt["stages"]
    for stage in stages:
        n = stage["n"]
        assert stage["ell_uv"] == pytest.approx(math.exp(-(n**2)))
        assert stage["delta"] == pytest.approx(n * math.exp(-(n**2)))
        assert stage["delta_over_ell_uv"] == pytest.approx(float(n))
        assert stage["sharp_geometric_margin"] == pytest.approx(n - n**2)
        assert stage["log_cmi_envelope"] == pytest.approx(n**2 - n)
    checks = receipt["finite_proxy_checks"]
    assert checks == {
        "delta_over_ell_uv_increases": True,
        "sharp_margin_strictly_decreases": True,
        "log_envelope_strictly_increases": True,
    }
    assert receipt["analytic_limit"]["delta_over_ell_uv"] == "+infinity"
    assert "does not tend to zero" in receipt["analytic_limit"]["cmi_envelope"]


def test_report_is_json_safe_and_forbids_claim_promotion():
    report = build_report()
    encoded = json.dumps(report, allow_nan=False)
    assert encoded
    assert report["artifact_class"] == "analytic_finite_proxy"
    assert report["empirical_evidence"] is False
    assert report["promotes_theorem_status"] is False
    assert "assumption_not_inferred_here" in report["assumption_contract"][
        "strong_conditional_matrix_mixing"
    ]["status"]
    assert "BW, Einstein" in " ".join(report["claim_boundary"]["not_certified"])
    assert json.loads(REPORT_PATH.read_text(encoding="utf-8")) == report
