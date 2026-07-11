#!/usr/bin/env python3
"""Tests for the free-fermion modular-clock instrumentation (#503)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from modular_clock_instrumentation import (  # noqa: E402
    arc_entanglement_hamiltonian,
    cft_profile,
    crossratio_receipt,
    instrument_tower,
    kms_profile_receipt,
    resummed_profile,
    ring_correlation_value,
    stage_data,
)


def test_correlations_are_half_filled_and_exact():
    # C(0) = 1/2 exactly at half filling
    assert abs(float(ring_correlation_value(16, 0)) - 0.5) < 1e-30


def test_extended_precision_resolves_the_spectrum():
    # float64 saturates interior EH bonds near |h| ~ 18; the extended-
    # precision computation must exceed that on the 64-ring, whose true
    # midpoint bond value is ~ beta_CFT/2 = 32
    h = arc_entanglement_hamiltonian(64, 32)
    interior = max(abs(h[j, j + 1]) for j in range(14, 18))
    assert interior > 25.0


def test_profile_matches_2pi_bw_and_wrong_normalization_separated():
    data = stage_data(32)
    receipt = kms_profile_receipt(data, 32)
    assert receipt["median_relative_residual_2pi"] < 5e-3
    assert receipt["separation_factor"] > 5.0


def test_nearest_neighbour_truncation_alone_fails():
    # the ~9 percent defect of the r=1 truncation is real physics: without
    # the odd-range chiral resummation the KMS receipt must NOT pass
    h = arc_entanglement_hamiltonian(32, 16)
    beta_r1 = resummed_profile(h, rmax=1)
    xs = np.arange(15) + 0.5
    beta_geo = cft_profile(32, xs, -0.5, 15.5)
    mid = slice(5, 10)
    rel = np.abs(beta_r1[mid] / beta_geo[mid] - 1.0)
    assert np.median(rel) > 0.05


def test_crossratio_converges_to_moebius():
    r16 = crossratio_receipt(stage_data(16), 16)
    r32 = crossratio_receipt(stage_data(32), 32)
    assert r32["relative_error"] < r16["relative_error"]
    assert r32["relative_error"] < 0.05
    # the Moebius target is stage-independent for proportional quadruples
    assert abs(r16["cr_moebius"] - r32["cr_moebius"]) < 1e-9


def test_instrumented_tower_witnesses_both_families():
    report = instrument_tower(rings=(16, 32))
    w = report["receipts_witnessed"]
    assert w["geometric_2pi_kms_boundary_collar"] is True
    assert w["modular_cross_ratio_boundary_collar"] is True
    assert "boundary-collar" in report["scope"]
    assert len(report["receipts_pending"]) >= 4
