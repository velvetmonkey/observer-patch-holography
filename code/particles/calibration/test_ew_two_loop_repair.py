"""Tests for the preregistered CL-5 two-loop repair lane."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

import derive_ew_two_loop_repair as lane
import sm_two_loop_rge_engine as engine

SPEC = lane.SPEC_PATH
ARTIFACT = lane.DEFAULT_OUT
FROZEN_RESULTS = (
    lane.REPO / "falsification" / "preregistered"
    / "ew_repair_results_2026-07-14.json"
)


@pytest.fixture(scope="module")
def spec() -> dict:
    return json.loads(SPEC.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def artifact() -> dict:
    if not ARTIFACT.exists():
        pytest.skip("repair artifact not yet generated")
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_spec_hash_verifies(spec):
    body = {k: v for k, v in spec.items() if k != "spec_sha256"}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert digest == spec["spec_sha256"]["hexdigest"]


def test_loader_fails_closed_on_tampered_spec(tmp_path, spec, monkeypatch):
    tampered = dict(spec)
    tampered["date"] = "2099-01-01"
    path = tmp_path / "spec.json"
    path.write_text(json.dumps(tampered), encoding="utf-8")
    monkeypatch.setattr(lane, "SPEC_PATH", path)
    with pytest.raises(SystemExit):
        lane.load_and_verify_spec()


def test_spec_declares_zero_tunables_and_closed_menu(spec):
    assert "zero tunable elements" in spec["revision_declaration"]["zero_tunable_elements"]
    menu = spec["discrete_branch_menu"]
    assert len(menu["yukawa_feed"]) == 2
    assert len(menu["tier"]) == 2
    assert len(menu["value_law"]) == 2
    assert len(menu["z_scheme"]) == 2
    assert "all 16 combinations" in menu["cells_emitted"]


def test_artifact_binds_to_spec_hash(spec, artifact):
    assert artifact["spec_sha256"] == spec["spec_sha256"]["hexdigest"]


def test_artifact_emits_full_declared_grid(artifact):
    ids = {c["id"] for c in artifact["cells"]}
    expected = {
        f"tier={t}|yukawa={y}|law={l}|z={z}"
        for t in ("A_readout_shift", "B_full_resolve")
        for y in ("ytcs", "yt0")
        for l in ("zero_selector", "nonzero_carrier")
        for z in ("z_tree", "z_stage3")
    }
    gated_groups = {g["cell_group"] for g in artifact["gates_triggered"]}
    for cell_id in expected:
        tier_tag = "tier_A" if "A_readout_shift" in cell_id else "tier_B"
        branch = "ytcs" if "yukawa=ytcs" in cell_id else "yt0"
        if f"{tier_tag}|{branch}" in gated_groups:
            continue
        assert cell_id in ids


def test_baseline_matches_frozen_sweep(artifact):
    frozen = json.loads(FROZEN_RESULTS.read_text(encoding="utf-8"))
    base = frozen["baseline_consistency"]
    got = artifact["baseline_one_loop"]
    assert abs(got["alpha_U"] - base["alpha_u_recomputed"]) < 1e-12
    cells = got["cells"]
    assert abs(
        cells["zero_selector|z_tree"]["MW_GeV"]
        - base["MW_zero_selector_recomputed_GeV"]
    ) < 1e-9
    assert abs(
        cells["zero_selector|z_tree"]["MZ_GeV"]
        - base["MZ_zero_selector_recomputed_GeV"]
    ) < 1e-9


def test_engine_certification_recorded_ok(artifact):
    assert artifact["engine_certification"]["all_ok"] is True
    assert all(artifact["engine_certification"]["endpoint_ok"].values())


def test_one_loop_gauge_betas_are_yukawa_blind():
    """The increment isolates two-loop terms only because the loops=1 gauge
    betas carry no Yukawa or quartic dependence."""

    a = engine.beta_1loop(0.46, 0.65, 1.16, 0.0, 0.0)
    b = engine.beta_1loop(0.46, 0.65, 1.16, 0.95, 0.13)
    for i in range(3):
        assert a[i] == b[i]


def test_apply_increments_is_the_declared_identity():
    delta = {"alpha1": -0.21, "alpha2": -0.28, "alpha3": 0.45}
    a1, a2, a3 = 0.0169, 0.0338, 0.1183
    r1, r2, r3 = lane.apply_increments(a1, a2, a3, delta)
    assert abs(1.0 / r1 - (1.0 / a1 - delta["alpha1"])) < 1e-12
    assert abs(1.0 / r2 - (1.0 / a2 - delta["alpha2"])) < 1e-12
    assert abs(1.0 / r3 - (1.0 / a3 - delta["alpha3"])) < 1e-12


def test_apply_increments_fails_closed_past_pole():
    with pytest.raises(OverflowError):
        lane.apply_increments(0.5, 0.5, 0.5, {"alpha1": 3.0, "alpha2": 0.0, "alpha3": 0.0})


def test_recorded_increment_reproduces(artifact):
    """Regression guard: the tier_A yt0 increment recomputes from the
    recorded baseline couplings with the certified engine."""

    base = artifact["baseline_one_loop"]
    inc = lane.two_loop_increments(
        base["alpha1_mz"],
        base["alpha2_mz"],
        base["alpha3_mz"],
        base["mz_run_fixed_point_GeV"],
        base["mu_U_GeV"],
        "yt0",
        lane.NEWTON_GUESS,
    )
    recorded = artifact["diagnostics"]["tier_A|yt0"]["delta_invalpha"]
    for name in ("alpha1", "alpha2", "alpha3"):
        assert abs(inc["delta_invalpha"][name] - recorded[name]) < 1e-9


def test_pulls_and_shifts_are_internally_consistent(artifact):
    mw_t, mw_s = artifact["targets_GeV"]["MW"]
    mz_t, mz_s = artifact["targets_GeV"]["MZ"]
    base_cells = artifact["baseline_one_loop"]["cells"]
    for c in artifact["cells"]:
        assert abs(c["MW_pull_sigma"] - (c["MW_GeV"] - mw_t) / mw_s) < 1e-9
        assert abs(c["MZ_pull_sigma"] - (c["MZ_GeV"] - mz_t) / mz_s) < 1e-9
        law = "zero_selector" if "law=zero_selector" in c["id"] else "nonzero_carrier"
        z = "z_tree" if "z=z_tree" in c["id"] else "z_stage3"
        base = base_cells[f"{law}|{z}"]
        assert abs(
            c["shift_from_baseline_MW_GeV"] - (c["MW_GeV"] - base["MW_GeV"])
        ) < 1e-9
        assert abs(
            c["shift_from_baseline_MZ_GeV"] - (c["MZ_GeV"] - base["MZ_GeV"])
        ) < 1e-9
        assert c["landing"] == (
            abs(c["MW_offset_GeV"]) <= mw_s and abs(c["MZ_offset_GeV"]) <= mz_s
        )


def test_verdict_follows_declared_rule(artifact):
    verdict = artifact["summary"]["verdict"]
    if verdict["status"] == "not_evaluable":
        assert artifact["physical_comparison"]["status"] == "NOT_EVALUABLE"
        assert artifact["physical_comparison"]["physical_pull_allowed"] is False
        verdict = verdict["internal_prescription_diagnostic"]
    primary = next(
        (c for c in artifact["cells"] if c["id"] == verdict["primary_cell"]), None
    )
    if primary is None:
        assert verdict["status"] == "gated"
        return
    mw_t, _ = artifact["targets_GeV"]["MW"]
    mz_t, _ = artifact["targets_GeV"]["MZ"]
    base = artifact["baseline_one_loop"]["cells"]["zero_selector|z_tree"]
    mw_shrinks = abs(primary["MW_offset_GeV"]) < abs(base["MW_GeV"] - mw_t)
    mz_shrinks = abs(primary["MZ_offset_GeV"]) < abs(base["MZ_GeV"] - mz_t)
    if mw_shrinks and mz_shrinks:
        expected = "toward_measurement"
    elif not mw_shrinks and not mz_shrinks:
        expected = "away_from_measurement"
    else:
        expected = "mixed"
    assert verdict["direction"] == expected


def test_declared_gates_present(artifact):
    gates = artifact["gates_declared_open"]
    tags = " ".join(gates)
    for tag in ("GATE-2L-01", "GATE-2L-02", "GATE-2L-03", "GATE-2L-04", "GATE-2L-05"):
        assert tag in tags


def test_frozen_artifacts_untouched():
    """The 2026-07-14 sweep artifacts stay byte-identical inputs."""

    frozen = json.loads(FROZEN_RESULTS.read_text(encoding="utf-8"))
    assert frozen["date"] == "2026-07-14"
    assert frozen["summary"]["landing_count"] == 1
