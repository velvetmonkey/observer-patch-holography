"""Tests for the preregistered CL-5 radiative pole packet lane."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

import derive_ew_pole_packet as lane
import sm_one_loop_self_energy_engine as engine

SPEC = lane.SPEC_PATH
ARTIFACT = lane.DEFAULT_OUT
AUDIT = (
    lane.ROOT / "particles" / "runs" / "calibration"
    / "ew_pole_packet_audit_2026-07-16.json"
)
FROZEN_SWEEP = (
    lane.REPO / "falsification" / "preregistered"
    / "ew_repair_results_2026-07-14.json"
)
FROZEN_TWO_LOOP = (
    lane.ROOT / "particles" / "runs" / "calibration"
    / "ew_two_loop_repair_2026-07-16.json"
)

CELL_IDS = {
    f"tier={t}|mt={m}|law={l}"
    for t in ("A_readout_shift", "B_pole_fixed_point")
    for m in ("mt_pole_stage5", "mt_msbar_stage5")
    for l in ("zero_selector", "nonzero_carrier")
}


@pytest.fixture(scope="module")
def spec() -> dict:
    return json.loads(SPEC.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def artifact() -> dict:
    if not ARTIFACT.exists():
        pytest.skip("pole packet artifact not yet generated")
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
    assert "zero tunable elements" in spec["revision_declaration"][
        "zero_tunable_elements"
    ]
    menu = spec["discrete_branch_menu"]
    assert len(menu["tier"]) == 2
    assert len(menu["mt_loop"]) == 2
    assert len(menu["value_law"]) == 2
    assert "all 8 combinations" in menu["cells_emitted"]
    assert "z_stage3" in menu["z_scheme_retired"]
    assert (
        menu["primary_display_cell"]
        == "tier=B_pole_fixed_point|mt=mt_pole_stage5|law=zero_selector "
        "(same law as the baseline chain key)"
    )


def test_artifact_binds_to_spec_hash(spec, artifact):
    assert artifact["spec_sha256"] == spec["spec_sha256"]["hexdigest"]


def test_artifact_emits_full_declared_grid(artifact):
    ids = {c["id"] for c in artifact["cells"]}
    gated = {g["cell_group"] for g in artifact["gates_triggered"]}
    for cell_id in CELL_IDS:
        tier = "tier_A" if "A_readout_shift" in cell_id else "tier_B"
        branch = "mt_pole_stage5" if "mt=mt_pole_stage5" in cell_id else "mt_msbar_stage5"
        law = "zero_selector" if "law=zero_selector" in cell_id else "nonzero_carrier"
        if f"{tier}|{branch}" in gated or f"{tier}|{branch}|{law}" in gated:
            continue
        assert cell_id in ids


def test_baseline_matches_frozen_sweep(artifact):
    frozen = json.loads(FROZEN_SWEEP.read_text(encoding="utf-8"))
    base = frozen["baseline_consistency"]
    got = artifact["baseline_one_loop"]
    assert abs(got["alpha_U"] - base["alpha_u_recomputed"]) < 1e-12
    cells = got["cells"]
    assert abs(
        cells["zero_selector"]["MW_GeV"] - base["MW_zero_selector_recomputed_GeV"]
    ) < 1e-9
    assert abs(
        cells["zero_selector"]["MZ_GeV"] - base["MZ_zero_selector_recomputed_GeV"]
    ) < 1e-9


def test_engine_certification_recorded_ok(artifact):
    assert artifact["engine_certification"]["all_ok"] is True


def test_engine_validators_pass_live():
    cert = engine.validate()
    assert cert["all_ok"] is True


def test_b0_zero_slope_matches_finite_difference():
    """Richardson-extrapolated finite difference; small h loses all digits to
    cancellation between the O(1/s) terms of the closed form."""

    for m0, m1 in ((80.4, 91.2), (80.4, 0.0), (91.2, 91.2), (164.1, 115.1)):
        h = 4.0
        mu2 = 91.2**2
        b0_0 = engine.b0_fin(0.0, m0, m1, mu2)
        f1 = (engine.b0_fin(h, m0, m1, mu2) - b0_0) / h
        f2 = (engine.b0_fin(h / 2.0, m0, m1, mu2) - b0_0) / (h / 2.0)
        fd = 2.0 * f2 - f1
        assert abs(fd - engine.b0p_zero(m0, m1)) < 1e-10


def test_pole_shift_determinism_from_recorded_baseline(artifact):
    """Regression guard: the tier A zero-selector primary-branch cell
    recomputes bit-level from the recorded baseline basis with the certified
    engine, without rerunning the chain."""

    base = artifact["baseline_one_loop"]
    stage5 = artifact["stage5_internal_masses_GeV"]
    e_star = artifact["display_adapter"]["E_star_display_GeV"]
    a2 = base["alpha2_mz"]
    ay = 0.6 * base["alpha1_mz"]
    sin2_0 = ay / (ay + a2)
    eta = base["alpha_U"] * (1.0 - 2.0 * sin2_0)
    v_over_e = base["v_over_E_star"]
    # zero-selector law: a2p = a2, ayp = ay (1 - 2 eta).
    ayp = ay * (1.0 - 2.0 * eta)
    law = {
        "MW_over_E_star": v_over_e * math.sqrt(math.pi * a2),
        "MZ_over_E_star": v_over_e * math.sqrt(math.pi * (a2 + ayp)),
        "sin2w_eff": ayp / (a2 + ayp),
    }
    shifted = lane.pole_shift_pair(
        law,
        v_over_e,
        e_star,
        base["mz_run_fixed_point_GeV"],
        stage5["mt_pole_stage5"],
        stage5["mH_stage5"],
    )
    recorded_cell = next(
        c
        for c in artifact["cells"]
        if c["id"] == "tier=A_readout_shift|mt=mt_pole_stage5|law=zero_selector"
    )
    recorded_diag = artifact["diagnostics"]["tier_A|mt_pole_stage5"]["zero_selector"]
    assert abs(shifted["MW_GeV"] - recorded_cell["MW_GeV"]) < 1e-9
    assert abs(shifted["MZ_GeV"] - recorded_cell["MZ_GeV"]) < 1e-9
    assert abs(
        shifted["sigma_over_m2_W"] - recorded_diag["sigma_over_m2_W"]
    ) < 1e-12
    assert abs(
        shifted["sigma_over_m2_Z"] - recorded_diag["sigma_over_m2_Z"]
    ) < 1e-12


def test_pulls_and_shifts_are_internally_consistent(artifact):
    mw_t, mw_s = artifact["targets_GeV"]["MW"]
    mz_t, mz_s = artifact["targets_GeV"]["MZ"]
    base_cells = artifact["baseline_one_loop"]["cells"]
    for c in artifact["cells"]:
        assert abs(c["MW_pull_sigma"] - (c["MW_GeV"] - mw_t) / mw_s) < 1e-9
        assert abs(c["MZ_pull_sigma"] - (c["MZ_GeV"] - mz_t) / mz_s) < 1e-9
        law = "zero_selector" if "law=zero_selector" in c["id"] else "nonzero_carrier"
        base = base_cells[law]
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
    base = artifact["baseline_one_loop"]["cells"]["zero_selector"]
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
    tags = " ".join(artifact["gates_declared_open"])
    for tag in (
        "GATE-PP-01",
        "GATE-PP-02",
        "GATE-PP-03",
        "GATE-PP-04",
        "GATE-PP-05",
        "GATE-PP-06",
        "GATE-PP-07",
    ):
        assert tag in tags


def test_kill_condition_audit_recorded(artifact):
    """Adverse-in-every-cell outcomes carry the completed audit artifact."""

    verdict = artifact["summary"]["verdict"]
    if verdict["status"] == "not_evaluable":
        verdict = verdict["internal_prescription_diagnostic"]
    if verdict["direction"] != "away_from_measurement":
        pytest.skip("audit artifact required for adverse verdicts only")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert audit["audit_pass"] is True
    assert audit["audited_run_spec_sha256"] == artifact["spec_sha256"]
    for row in audit["jkv_divergence_structure"]:
        assert row["universality_spread"] < 1e-10
    assert audit["tadpole_universality"]["split_sign_disagrees"] is True


def test_frozen_artifacts_untouched():
    frozen = json.loads(FROZEN_SWEEP.read_text(encoding="utf-8"))
    assert frozen["date"] == "2026-07-14"
    assert frozen["summary"]["landing_count"] == 1
    two_loop = json.loads(FROZEN_TWO_LOOP.read_text(encoding="utf-8"))
    assert two_loop["date"] == "2026-07-16"
    assert (
        two_loop["summary"]["verdict"]["direction"] == "away_from_measurement"
    )
