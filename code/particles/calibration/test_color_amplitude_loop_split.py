#!/usr/bin/env python3
"""Tests for the color amplitude/loop split derivation (#521 A2/A3)."""

from __future__ import annotations

import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from derive_color_amplitude_loop_split import build  # noqa: E402


def test_guards_no_source_theorem_claimed() -> None:
    report = build()
    assert report["guards"]["measured_values_in_any_oph_solve_path"] is False
    assert report["guards"]["source_only_theorem_emitted"] is False
    assert report["guards"]["public_promotion_allowed"] is False
    assert report["guards"]["complete_archived_value_law_tested_as_constant_c_competitor"] is False


def test_legacy_mw_profile_arithmetic_is_retained_without_selection_claim() -> None:
    report = build()
    ds = report["data_selection"]
    assert report["guards"]["wz_physical_comparison_status"] == "NOT_EVALUABLE"
    assert abs(ds["MW_best_c"] - math.sqrt(3) / 2) < 0.005


def test_legacy_mz_profile_arithmetic_is_retained_without_selection_claim() -> None:
    report = build()
    ds = report["data_selection"]
    assert abs(ds["MZ_best_d"] - 1.5) < 0.06


def test_legacy_profile_does_not_emit_physical_exclusions() -> None:
    report = build()
    comps = report["data_selection"]["competitors"]
    assert comps["color_amplitude_loop  c=sqrt(Nc)/2"]["inside_legacy_reference_error_profile"] is True
    assert comps["loop_symmetric        c=Nc/2"]["inside_legacy_reference_error_profile"] is False
    assert "not physically evaluated" in report["verdict"]["loop_symmetric_law"]
    for key in ("MW_chart_gev", "MZ_chart_gev"):
        row = report["comparison_compare_only"][key]
        assert row["physical_comparison_status"] == "NOT_EVALUABLE"
        assert row["physical_pull"] is None
        assert "delta_over_sigma" not in row


def test_channel_identification_remains_open() -> None:
    report = build()
    assert "channel_identification_open" in report["verdict"]["status"]
