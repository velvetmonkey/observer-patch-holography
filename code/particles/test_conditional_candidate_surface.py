#!/usr/bin/env python3
"""Tests for the conditional candidate output surface."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

PARTICLES_ROOT = pathlib.Path(__file__).resolve().parent
BUILDER = PARTICLES_ROOT / "scripts" / "build_conditional_candidate_surface.py"
D11_SPLIT_PAIR_JSON = PARTICLES_ROOT / "runs" / "calibration" / "d11_live_exact_split_pair_theorem.json"
D10_VALUE_LAW_JSON = PARTICLES_ROOT / "runs" / "calibration" / "d10_ew_target_free_repair_value_law.json"


def _build(tmp_path: pathlib.Path) -> dict:
    json_out = tmp_path / "conditional_candidates.json"
    subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--markdown-out",
            str(tmp_path / "CONDITIONAL_CANDIDATES.md"),
            "--json-out",
            str(json_out),
            "--forward-out",
            str(tmp_path / "conditional_candidates_current.json"),
        ],
        check=True,
    )
    return json.loads(json_out.read_text(encoding="utf-8"))


def test_every_row_stays_non_promotable(tmp_path: pathlib.Path) -> None:
    payload = _build(tmp_path)
    assert payload["must_not_feed_back"] is True
    rows = (
        payload["gev_chart_candidates"]
        + payload["scale_free_chart_ratios"]
        + payload["dimensionless_candidates"]
    )
    assert rows
    for row in rows:
        assert row["promotable"] is False
        assert row["open_gates"]
        assert row["source_artifact"]


def test_values_match_source_artifacts(tmp_path: pathlib.Path) -> None:
    payload = _build(tmp_path)
    by_key = {(row["observable"], row["chart"]): row for row in payload["gev_chart_candidates"]}

    split_pair = json.loads(D11_SPLIT_PAIR_JSON.read_text(encoding="utf-8"))["exact_split_pair"]
    higgs = by_key[("m_H", "declared_d10_d11_running_matching_threshold_surface")]
    top = by_key[("m_t", "declared_d10_d11_running_matching_threshold_surface")]
    assert higgs["value"] == split_pair["mH_gev"]
    assert top["value"] == split_pair["mt_pole_gev"]

    quintet = json.loads(D10_VALUE_LAW_JSON.read_text(encoding="utf-8"))["coherent_emitted_quintet"]
    w_row = by_key[("M_W", "archived_d10_value_law_candidate")]
    z_row = by_key[("M_Z", "archived_d10_value_law_candidate")]
    assert w_row["value"] == quintet["MW_pole"]
    assert z_row["value"] == quintet["MZ_pole"]

    ratio_by_key = {
        (row["observable"], row["chart"]): row for row in payload["scale_free_chart_ratios"]
    }
    ratio_row = ratio_by_key[("M_W / M_Z", "archived_d10_value_law_candidate")]
    assert ratio_row["value"] == quintet["MW_pole"] / quintet["MZ_pole"]
    assert ratio_by_key[("sin2_theta_W_eff", "archived_d10_value_law_candidate")]["value"] == quintet["sin2w_eff"]
    higgs_top = ratio_by_key[("m_H / m_t", "declared_d10_d11_running_matching_threshold_surface")]
    assert higgs_top["value"] == split_pair["mH_gev"] / split_pair["mt_pole_gev"]
