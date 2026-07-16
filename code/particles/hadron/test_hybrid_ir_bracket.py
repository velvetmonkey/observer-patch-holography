#!/usr/bin/env python3
"""Tests for the hybrid IR bracket diagnostic lane.

Coverage: (a) conserved-current contraction anchors (exact off-source Ward
identity on a rough gauge background, free-field Z_V^eff plateau at exactly
1, temporal-channel suppression), (b) analysis rules (autocorrelation,
effective-mass window, matching, envelope math), (c) free-field S_IR
round trip near 1, (d) hybrid-bracket identity against the frozen
zero/free modules and non-promotion gates of the emitted payload.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from lattice_backend.core import cold_start, sweep
from lattice_backend.dirac import WilsonClover, point_propagator
from lattice_backend.conserved_vector import (
    conserved_local_correlator,
    temporal_vector_correlator,
    transverse_vector_correlator,
    ward_divergence_offsource_max,
    zv_effective,
)
from lattice_backend.vector_correlator import fold_correlator, tmr_moment
from hybrid_ir_bracket import (
    apply_envelope,
    build_hybrid_rows,
    delta_ir_free,
    effective_mass_windowed,
    effmass_window,
    estimate_s_ir,
    integrated_autocorrelation_time,
    kappa_free_for_vector_mass,
    physical_moment,
)


@pytest.fixture(scope="module")
def free_field_measurement():
    """Free-field propagator and correlators at kappa 0.11 on 16 x 4^3."""
    shape = (16, 4, 4, 4)
    kappa = 0.11
    u = cold_start(shape)
    op = WilsonClover(u, kappa=kappa, c_sw=1.0)
    prop, _ = point_propagator(op, shape, tol=1e-11)
    return {
        "shape": shape,
        "kappa": kappa,
        "prop": prop,
        "ubc": op.ubc,
        "g_ll": transverse_vector_correlator(prop),
        "g_cl": conserved_local_correlator(prop, op.ubc, kappa),
    }


def test_free_field_zv_plateau_is_one(free_field_measurement):
    m = free_field_measurement
    zv = zv_effective(m["g_cl"], m["g_ll"], m["kappa"])
    plateau = zv[5:9]
    assert np.all(np.abs(plateau - 1.0) < 5e-3), plateau


def test_free_field_temporal_channel_suppressed(free_field_measurement):
    m = free_field_measurement
    g_temp = temporal_vector_correlator(m["prop"])
    g_trans = m["g_ll"]
    # transverse channel dominates the temporal remnant (a small constant
    # from the local current's O(a) non-conservation) at early times
    for t in range(1, 4):
        assert abs(g_temp[t]) < 3e-2 * abs(g_trans[t]), t
    # the remnant is flat, the transverse channel decays
    assert abs(g_temp[5] - g_temp[1]) < 0.05 * abs(g_temp[1])
    assert g_trans[5] < 0.05 * g_trans[1]


def test_ward_identity_offsource_rough_field():
    shape = (8, 4, 4, 4)
    kappa = 0.12
    rng = np.random.default_rng(11)
    u = cold_start(shape)
    for _ in range(10):
        sweep(rng, u, beta=5.5, n_or=1)
    op = WilsonClover(u, kappa=kappa, c_sw=1.0)
    prop, _ = point_propagator(op, shape, tol=1e-12)
    for nu in (1, 2):
        defect, scale = ward_divergence_offsource_max(prop, op.ubc, kappa, nu=nu)
        assert defect < 1e-9 * scale, (nu, defect, scale)


def test_integrated_autocorrelation_time_iid():
    rng = np.random.default_rng(7)
    tau = integrated_autocorrelation_time(rng.normal(size=4000))
    assert abs(tau - 0.5) < 0.15, tau


def test_integrated_autocorrelation_time_correlated():
    rng = np.random.default_rng(7)
    x = np.zeros(6000)
    for i in range(1, len(x)):
        x[i] = 0.8 * x[i - 1] + rng.normal()
    tau = integrated_autocorrelation_time(x)
    # AR(1) with rho=0.8 has tau_int = 0.5*(1+rho)/(1-rho) = 4.5
    assert 3.0 < tau < 6.5, tau


def test_effective_mass_window_cosh_exact():
    """Exact recovery of m from a folded cosh correlator, including the
    image-dominated points near T/2 that bias the plain log ratio."""
    t_extent = 16
    m = 0.7
    t = np.arange(t_extent // 2 + 1, dtype=float)
    folded = 3.0 * (np.exp(-m * t) + np.exp(-m * (t_extent - t)))
    assert effmass_window(folded) == [3, 4, 5, 6, 7]
    assert abs(effective_mass_windowed(folded) - m) < 1e-9


def test_kappa_free_matching_round_trip():
    for kappa in (0.10, 0.11, 0.118):
        am_q = math.log(1.0 + (0.5 / kappa - 4.0))
        assert abs(kappa_free_for_vector_mass(2.0 * am_q) - kappa) < 1e-12


def test_apply_envelope_quadrature_and_clamp():
    env = apply_envelope(1.0, 0.0, factors={"a": 0.3, "b": 0.4})
    assert abs(env["e_total"] - 0.5) < 1e-12
    assert abs(env["s_ir_lo"] - 0.5) < 1e-12
    assert abs(env["s_ir_hi"] - 1.5) < 1e-12
    clamped = apply_envelope(0.5, 0.0, factors={"a": 3.0})
    assert clamped["s_ir_lo"] == 0.0


def test_s_ir_free_field_round_trip(free_field_measurement):
    """Feeding the free field through the pipeline must give S_IR near 1.

    Residual deviation comes only from the effective-mass window sitting
    above the asymptotic 2*am_q (excited states) and the resulting
    kappa_free mismatch; Z_V is exactly 1 on the free field.
    """
    m = free_field_measurement
    g_ll = np.stack([m["g_ll"]] * 3)
    g_cl = np.stack([m["g_cl"]] * 3)
    m_v = effective_mass_windowed(fold_correlator(m["g_ll"]))
    kappa_f = kappa_free_for_vector_mass(m_v)
    u = cold_start(m["shape"])
    op = WilsonClover(u, kappa=kappa_f, c_sw=1.0)
    prop, _ = point_propagator(op, m["shape"], tol=1e-11)
    g_free = transverse_vector_correlator(prop)
    model = {
        "m_v_ref": m_v,
        "m_free_phys_ref": physical_moment(fold_correlator(g_free), kappa_f),
        "dm_free_phys_dm_v": 0.0,
    }
    res = estimate_s_ir(g_ll, g_cl, m["kappa"], model)
    assert abs(res["z_v"] - 1.0) < 0.02, res["z_v"]
    assert 0.7 < res["s_ir"] < 1.3, res["s_ir"]
    # identical samples: jackknife error must vanish
    assert res["errors"]["s_ir"] < 1e-12


@pytest.fixture(scope="module")
def evaluation_point():
    import payload_harness as ph
    return ph.build_evaluation_point(precision=40)


def test_hybrid_rows_zero_free_identity_and_bounds(evaluation_point):
    """The zero/free identity gate runs inside build_hybrid_rows; at
    S_IR in {0, 1} the hybrid row values reproduce the frozen zero and
    free rows."""
    import payload_harness as ph
    import spectral_modules as sm
    ep = evaluation_point
    out = build_hybrid_rows(
        ep, 0.0, 1.0,
        lambda_keys=("lane_central",), k_cuts=(4.0,), orders=(3,))
    assert out["max_zero_free_identity_defect"] < 1e-9
    row = out["rows"][0]
    naive = out["quark_delta_alpha_inv_naive"]
    zero = ph.emit_delta_source(sm.make_pqcd("lane_central", 4.0, "zero", 3), ep)
    free = ph.emit_delta_source(sm.make_pqcd("lane_central", 4.0, "free", 3), ep)
    s_zero = zero["diagnostics"]["s_effective"]
    s_free = free["diagnostics"]["s_effective"]
    assert abs(row["s_eff_at_s_ir_lo"] - s_zero) < 1e-12
    assert abs(row["s_eff_at_s_ir_hi"] - s_free) < 1e-12
    assert naive == pytest.approx(ph.quark_naive_transport(ep))


def test_delta_ir_free_positive_and_growing_with_k(evaluation_point):
    import spectral_modules as sm
    lam = sm.LAMBDA3_GRID["lane_central"]
    vals = [delta_ir_free(evaluation_point, lam, k) for k in (2.0, 4.0, 8.0)]
    assert all(v > 0.0 for v in vals)
    assert vals[0] < vals[1] < vals[2]


def test_artifact_gates_and_labels(tmp_path, free_field_measurement, evaluation_point, monkeypatch):
    """Non-promotion gates of the emitted payload on a tiny injected report."""
    import run_hybrid_ir_bracket_diagnostic as runner

    m = free_field_measurement
    report = {
        "ensemble_id": "gate_test",
        "n_configs": 3,
        "plaquette_mean": 1.0,
        "spectroscopy": {"am_vector_windowed": 1.0,
                         "am_vector_jackknife_error": 0.1},
        "z_v": {"windowed_mean": 1.0},
        "moments": {"relative_statistical_error_moment": 0.1},
        "s_ir": {
            "central": 0.9,
            "jackknife_error": 0.09,
            "relative_statistical_error_inflated": 0.1,
        },
    }
    monkeypatch.setattr(
        runner, "build_hybrid_rows",
        lambda ep, lo, hi, **kw: {
            "quark_delta_alpha_inv_naive": 4.93,
            "rows": [{
                "lambda3_key": "lane_central", "k_cut": 4.0, "order": 3,
                "delta_above_alpha_inv": 3.2,
                "delta_ir_free_alpha_inv": 1.9,
                "s_eff_at_s_ir_lo": (3.2 + lo * 1.9) / 4.93,
                "s_eff_at_s_ir_hi": (3.2 + hi * 1.9) / 4.93,
            }],
            "max_zero_free_identity_defect": 0.0,
            "s_effective_hybrid": {
                "lo": (3.2 + lo * 1.9) / 4.93,
                "hi": (3.2 + hi * 1.9) / 4.93,
                "width": (hi - lo) * 1.9 / 4.93,
            },
        })
    monkeypatch.setattr(
        runner.ph, "build_evaluation_point",
        lambda precision=40: evaluation_point)
    payload = runner.build_payload({"A": report}, "A", log=lambda *a: None)
    assert payload["label"] == "compare_only_non_blind"
    assert payload["row_class"] == "diagnostic_non_promoting"
    assert payload["physical_claim"] is False
    guards = payload["guards"]
    assert guards["promotion_allowed"] is False
    assert guards["satisfies_issue_425_closure"] is False
    assert guards["frozen_v2_target_modified"] is False
    assert payload["envelope_spec"]["sha256"]
    assert payload["containment_check"]["comparison"] == "compare_only_non_blind"
    assert payload["external_inputs_used_in_computation"] is False
    # envelope must include the declared systematic factors, so the
    # interval is strictly wider than statistics alone
    env = payload["s_ir_interval"]
    assert env["e_total"] > env["e_stat"]
    note = tmp_path / "note.md"
    runner.write_note(payload, note)
    assert "compare_only_non_blind" in note.read_text(encoding="utf-8")
