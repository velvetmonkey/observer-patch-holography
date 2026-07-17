#!/usr/bin/env python3
"""Reduced-parameter checks for the maximal-domain uniqueness extension.

Runs the envelope lemma and the pixel-window sweep at low cutoffs and digits
(fast) and asserts the machinery:

- the envelope lemma certifies the global 1/a3 floor, a positive screening
  window, a positive global P range, and a positive inverse-alpha readout
  floor;
- the sweep covers the full pixel window with decisive verdicts, the handoff
  hull sits inside the declared physical interval, and the certified alpha
  outer bound brackets the physical interval;
- the composition inputs (the 2026-07-14 existence and at-most-one
  certificates) verify;
- interval intersection handles the disjoint, nested, and overlapping cases;
- the construction is deterministic.
"""

from __future__ import annotations

import global_uniqueness_extension_certificate as ext
import interval_contraction_certificate as icc


REDUCED = dict(
    mp_dps=30,
    iv_dps=30,
    su2_cutoff=24,
    su3_cutoff=16,
)

SWEEP_PARAMS = dict(
    initial_pieces=24,
    depth_cap=12,
    eval_budget=600,
    iters=6,
    kernel_pieces=16,
)


def _frame() -> ext.Frame:
    return ext.Frame(**REDUCED)


def test_envelope_lemma_certifies() -> None:
    frame = _frame()
    env = ext.envelope_lemma(frame)
    report = env["report"]

    assert report["case_su3_subcritical"]["refuted"] is True
    assert report["case_su3_nonpositive"]["refuted"] is True
    assert float(report["case_su3_subcritical"]["identity_lower_bound"]) > 4.0
    assert float(report["case_su3_nonpositive"]["identity_lower_bound"]) > 4.0

    assert float(report["a3_inv_global"]["lo"]) >= 4.0
    assert 0.0 < float(report["screening_global"]["lo"]) < 1.0
    assert 0.0 < float(report["p_global"]["lo"]) < float(report["p_global"]["hi"])
    assert float(report["alpha_inv_readout_floor"]) > 0.0
    cap = float(report["fixed_point_alpha_cap"])
    assert 0.0 < cap < 0.1


def test_sweep_certifies_and_hands_off_to_physical_interval() -> None:
    frame = _frame()
    env = ext.envelope_lemma(frame)
    sweep = ext.sweep_pixel_window(frame, env, **SWEEP_PARAMS)

    counts = sweep["verdict_counts"]
    assert sum(counts.values()) == sweep["subdivision"]["total_pieces"]
    assert sweep["exceptional_set"] == []
    assert set(counts) <= ext.DECISIVE_VERDICTS
    assert counts.get(ext.VERDICT_HANDOFF, 0) >= 1
    assert counts.get(ext.VERDICT_GAP, 0) >= 1
    assert counts.get(ext.VERDICT_MZ_WINDOW, 0) >= 1
    assert sweep["conclusion"]["certified"] is True

    handoff = sweep["handoff_alpha_hull"]
    assert handoff is not None
    assert float(handoff["lo"]) >= float(ext.PHYSICAL_ALPHA[0])
    assert float(handoff["hi"]) <= float(ext.PHYSICAL_ALPHA[1])

    outer = sweep["domain_alpha_outer_hull"]
    assert outer is not None
    assert float(outer["lo"]) < 0.0 < float(outer["hi"])
    assert float(outer["hi"]) > float(ext.PHYSICAL_ALPHA[1])


def test_sweep_is_deterministic() -> None:
    frame = _frame()
    env = ext.envelope_lemma(frame)
    first = ext.sweep_pixel_window(frame, env, **SWEEP_PARAMS)
    second = ext.sweep_pixel_window(frame, env, **SWEEP_PARAMS)
    assert first == second


def test_composition_inputs_verify() -> None:
    out = ext.verify_composition_inputs()
    assert out["at_most_one_on_declared_interval_all_modes"] is True
    assert out["existence_on_declared_interval_all_modes"] is True


def test_intersection_cases() -> None:
    frame = _frame()
    ivb = frame.ivb

    def mk(lo: str, hi: str):
        return frame.box(frame.mpb.num(lo), frame.mpb.num(hi))

    a = mk("1", "3")
    b = mk("2", "5")
    c = frame.isect(a, b)
    assert c is not None
    assert frame.iv_lo(c) == 2 and frame.iv_hi(c) == 3

    nested = frame.isect(mk("0", "10"), mk("4", "5"))
    assert nested is not None
    assert frame.iv_lo(nested) == 4 and frame.iv_hi(nested) == 5

    assert frame.isect(mk("1", "2"), mk("3", "4")) is None

    touching = frame.isect(mk("1", "2"), mk("2", "3"))
    assert touching is not None
    assert frame.iv_lo(touching) == 2 and frame.iv_hi(touching) == 2

    hull = frame.hull2(mk("1", "2"), mk("4", "6"))
    assert frame.iv_lo(hull) == 1 and frame.iv_hi(hull) == 6
    assert ivb is frame.ivb


def test_kernel_enclosure_tightens_with_subdivision() -> None:
    frame = _frame()
    a_box = frame.box(frame.mpb.num("0.5"), frame.mpb.num("4"))
    coarse = frame.kernel_enclosure(a_box, frame.ivb.one, frame.ivb.one, pieces=8)
    fine = frame.kernel_enclosure(a_box, frame.ivb.one, frame.ivb.one, pieces=128)
    assert frame.iv_lo(fine) > 0
    assert frame.iv_lo(fine) >= frame.iv_lo(coarse)
    assert frame.iv_hi(fine) <= frame.iv_hi(coarse)


def test_classify_piece_excludes_mz_window_at_low_u() -> None:
    frame = _frame()
    env = ext.envelope_lemma(frame)
    record = ext.classify_u_piece(
        frame, env, frame.mpb.num("0.02"), frame.mpb.num("0.021"),
        iters=6, kernel_pieces=16,
    )
    assert record["verdict"] == ext.VERDICT_MZ_WINDOW


def test_classify_piece_excludes_gap_far_from_fixed_point() -> None:
    frame = _frame()
    env = ext.envelope_lemma(frame)
    record = ext.classify_u_piece(
        frame, env, frame.mpb.num("0.06"), frame.mpb.num("0.061"),
        iters=6, kernel_pieces=16,
    )
    assert record["verdict"] == ext.VERDICT_GAP
    assert record["mode_status"][icc.MODE_SOURCE] == "excluded_gap"
    assert record["mode_status"][icc.MODE_GAUGE_WIDTH] == "excluded_gap"
