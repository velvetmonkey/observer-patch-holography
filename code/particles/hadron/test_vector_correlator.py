#!/usr/bin/env python3
"""Tests for the vector-correlator / TMR-moment diagnostic lane.

Coverage: (a) synthetic-correlator round trip of the TMR integration against
exact closed forms on both the contract side and the discrete-time side,
(b) determinism of the emitted artifact hash under a fixed seed, (c) gate
check that the artifact declares itself non-promoting, (d) free-field lattice
anchor for the contraction (vector effective mass at twice the quark pole
mass, positivity).
"""

from __future__ import annotations

import math

import numpy as np

from lattice_backend.core import cold_start
from lattice_backend.dirac import WilsonClover, point_propagator
from lattice_backend.vector_correlator import (
    analytic_atom_moment_continuum,
    analytic_atom_moment_discrete,
    fold_correlator,
    jackknife_moment,
    synthetic_atom_correlator,
    tmr_kernel,
    tmr_moment,
    vector_correlator,
)
from run_vector_correlator_diagnostic import SMOKE_PARAMS, build_payload


def _quiet(_msg: str) -> None:
    pass


def test_tmr_kernel_vanishes_at_origin() -> None:
    for amz in (None, 0.5, 1.0, 5.0):
        assert tmr_kernel(np.array([0.0]), amz)[0] == 0.0


def test_synthetic_round_trip_discrete_exact() -> None:
    """tmr_moment on a spectral atom matches the exact geometric-series sum."""
    for amz in (None, 0.7, 1.0, 3.0):
        g = synthetic_atom_correlator(64, s0=0.81, weight=2.5)
        got = tmr_moment(g, amz)
        ref = analytic_atom_moment_discrete(64, s0=0.81, weight=2.5, amz=amz)
        assert abs(got - ref) < 1e-12 * abs(ref), (amz, got, ref)


def test_synthetic_round_trip_contract_closed_form() -> None:
    """At fine effective discretization the discrete moment approaches the
    contract-side closed form weight * mZ^2/(3*pi*s0*(s0+mZ^2)), the same
    expression as payload_harness.kernel_moment_atom."""
    s0, weight, amz = 0.04, 1.3, 2.0
    g = synthetic_atom_correlator(400, s0=s0, weight=weight)
    got = tmr_moment(g, amz)
    ref = analytic_atom_moment_continuum(s0, weight, mz2=amz * amz)
    assert abs(got / ref - 1.0) < 5e-3, (got, ref)
    # kernel_moment_atom cross-check without importing the payload package:
    y = s0 / (amz * amz)
    atom = 1.0 / (3.0 * math.pi * y * (1.0 + y)) / (amz * amz)
    assert abs(ref - weight * atom) < 1e-12 * abs(ref)


def test_fold_correlator_symmetrizes() -> None:
    g = np.array([10.0, 4.0, 2.0, 1.0, 0.5, 1.2, 2.2, 4.4])
    folded = fold_correlator(g)
    assert len(folded) == 5
    assert folded[0] == 10.0
    assert folded[4] == 0.5
    assert folded[1] == 0.5 * (4.0 + 4.4)
    assert folded[3] == 0.5 * (1.0 + 1.2)


def test_jackknife_moment_zero_error_on_identical_samples() -> None:
    g = synthetic_atom_correlator(32, s0=1.0, weight=1.0)
    samples = np.stack([g, g, g])
    center, err = jackknife_moment(samples, amz=1.0)
    assert abs(center - tmr_moment(fold_correlator(g), 1.0)) < 1e-12
    assert err < 1e-14


def test_free_field_vector_channel_anchor() -> None:
    """On U = 1 the vector correlator is positive at early times and its
    effective mass sits near twice the free quark pole mass."""
    shape = (16, 2, 2, 2)
    kappa = 0.10
    am_q = np.log(1.0 + (0.5 / kappa - 4.0))
    u = cold_start(shape)
    op = WilsonClover(u, kappa=kappa, c_sw=1.0)
    prop, _ = point_propagator(op, shape, tol=1e-11)
    g = vector_correlator(prop)
    assert np.all(g[:7] > 0.0)
    meff = [math.log(g[t] / g[t + 1]) for t in range(4, 7)]
    assert np.allclose(meff, 2.0 * am_q, rtol=0.08), meff


def test_artifact_determinism_same_seed_same_hash() -> None:
    p1 = build_payload(SMOKE_PARAMS, smoke=True, log=_quiet)
    p2 = build_payload(SMOKE_PARAMS, smoke=True, log=_quiet)
    assert p1["content_sha256"] == p2["content_sha256"]
    assert p1["moments"] == p2["moments"]


def test_artifact_declares_non_promotion() -> None:
    payload = build_payload(SMOKE_PARAMS, smoke=True, log=_quiet)
    assert payload["row_class"] == "diagnostic_non_promoting_lattice_backend"
    assert payload["physical_claim"] is False
    guards = payload["guards"]
    assert guards["promotion_allowed"] is False
    assert guards["public_promotion_allowed"] is False
    assert guards["satisfies_issue_425_closure"] is False
    assert guards["target_anchored"] is False
    conv = payload["contract_correspondence"]["uncertified_conversion_factors"]
    assert conv["z_v_squared"]["declared_value"] == 1.0
    sys_list = payload["precision_statement"]["uncontrolled_systematics"]
    assert any("quenched" in s for s in sys_list)
    assert any("scale setting" in s for s in sys_list)
