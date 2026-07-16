#!/usr/bin/env python3
"""Analysis layer for the hybrid IR bracket diagnostic (generator G1 lane).

Output class: diagnostic, non-promoting; comparison label
compare_only_non_blind. Nothing here carries promotion weight and nothing
here modifies the frozen payload machinery: ``ward_projected_payload/`` is
imported read-only.

Construction, per the declared spec
``code/particles/runs/hadron/hybrid_ir_bracket_envelope_spec_2026-07-16.json``
(written and hashed before any evaluation):

- The frozen pqcd grid (Lambda3 x k_cut x order) keeps its above-cutoff
  treatment exactly: Delta_above = Delta_had of the frozen below='zero'
  module.
- The below-cutoff free-versus-zero dichotomy factor {0, 1} is replaced by
  a measured interval [S_IR_lo, S_IR_hi]:

      S_eff_new = (Delta_above + S_IR * Delta_IR_free) / Delta_quark_naive,

  with Delta_IR_free the frozen closed-form parton moment restricted to
  [y_thr, y0], and S_IR the lattice-measured interacting-over-free TMR
  moment ratio at matched vector scale with a declared multiplicative
  systematic envelope.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
WPP = HERE / "ward_projected_payload"
for p in (str(HERE), str(WPP)):
    if p not in sys.path:
        sys.path.insert(0, p)

import payload_harness as ph  # noqa: E402  (read-only frozen import)
import spectral_modules as sm  # noqa: E402  (read-only frozen import)

from lattice_backend.vector_correlator import (  # noqa: E402
    FOUR_PI,
    fold_correlator,
    tmr_moment,
)

# Declared envelope factors (mirror of the spec file; the artifact embeds
# the spec and its sha as the authoritative record).
ENVELOPE_FACTORS = {
    "e_z_v": 0.30,
    "e_quenching": 0.15,
    "e_discretization": 0.25,
    "e_finite_volume": 0.20,
    "e_transfer": 0.30,
    "e_kernel": 0.02,
}

EFFMASS_WINDOW_START = 3  # window [3, T/2 - 1], per the spec


# ---------------------------------------------------------------------------
# Chain statistics: thermalization and autocorrelation.
# ---------------------------------------------------------------------------


def integrated_autocorrelation_time(series: np.ndarray) -> float:
    """Madras-Sokal tau_int with self-consistent window W >= 4*tau_int."""
    x = np.asarray(series, dtype=float)
    n = len(x)
    if n < 4:
        return 0.5
    x = x - x.mean()
    var = float(np.dot(x, x)) / n
    if var == 0.0:
        return 0.5
    tau = 0.5
    for w in range(1, n // 2):
        rho = float(np.dot(x[:-w], x[w:])) / ((n - w) * var)
        tau += rho
        if w >= 4.0 * tau:
            break
    return max(tau, 0.5)


# ---------------------------------------------------------------------------
# Correlator-level extraction rules (declared in the spec).
# ---------------------------------------------------------------------------


def effmass_window(folded: np.ndarray) -> list[int]:
    """Contiguous window from t = 3 to T/2 - 1 with positive, decaying pairs."""
    half = len(folded) - 1
    ts: list[int] = []
    for t in range(EFFMASS_WINDOW_START, half):
        if folded[t] > 0.0 and folded[t + 1] > 0.0 and folded[t] > folded[t + 1]:
            ts.append(t)
        elif ts:
            break
    return ts


def cosh_effective_mass(t: int, ratio: float, half: int) -> float:
    """Solve cosh(m*(T/2 - t))/cosh(m*(T/2 - t - 1)) = ratio by bisection.

    Image-corrected effective mass for a correlator symmetric about
    T/2 = half; removes the backward-image bias of the plain log ratio near
    T/2 (spec amendment 2026-07-16, motivated by the free-field anchor
    before any interacting evaluation).
    """
    if ratio <= 1.0:
        return float("nan")
    lo, hi = 1e-8, 50.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        val = math.cosh(mid * (half - t)) / math.cosh(mid * (half - t - 1))
        if val > ratio:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def effective_mass_windowed(folded: np.ndarray) -> float:
    """Plain mean of the cosh effective mass over the declared window."""
    half = len(folded) - 1
    ts = effmass_window(folded)
    vals = [cosh_effective_mass(t, folded[t] / folded[t + 1], half)
            for t in ts]
    vals = [v for v in vals if math.isfinite(v)]
    if not vals:
        return float("nan")
    return float(np.mean(vals))


def zv_windowed(folded_cl: np.ndarray, folded_ll: np.ndarray, kappa: float
                ) -> tuple[float, list[float]]:
    """Plain mean of Z_V^eff(t) over t in [3, T/2 - 1]; returns (mean, per-t)."""
    half = len(folded_ll) - 1
    vals = []
    for t in range(EFFMASS_WINDOW_START, half):
        if folded_ll[t] != 0.0:
            vals.append(float(folded_cl[t] / (2.0 * kappa * folded_ll[t])))
    return float(np.mean(vals)), vals


def physical_moment(folded_hop: np.ndarray, kappa: float) -> float:
    """TMR t^2-kernel moment in physical field normalization."""
    return tmr_moment(folded_hop, amz=None) / (2.0 * kappa) ** 2


def kappa_free_for_vector_mass(am_v: float) -> float:
    """Matching rule 2*am_q_free = am_V with am_q = log(1 + 1/(2k) - 4)."""
    m_bare = math.exp(0.5 * am_v) - 1.0
    return 0.5 / (m_bare + 4.0)


def continuum_free_moment_context(
    am_q: float, t_extent: int, ncq2: float = 3.0
) -> float:
    """Infinite-volume continuum free-parton moment on the same t-window.

    Context-only number per the spec (incommensurable with the small-volume
    lattice at these parameters); deterministic Gauss-Legendre in omega.
    """
    nodes, weights = ph.gauss_legendre(200)
    lo, hi = 2.0 * am_q, 2.0 * am_q + 60.0
    w = 0.5 * (hi + lo) + 0.5 * (hi - lo) * np.asarray(nodes)
    wt = 0.5 * (hi - lo) * np.asarray(weights)
    beta = np.sqrt(np.maximum(1.0 - (2.0 * am_q) ** 2 / (w * w), 0.0))
    rho_r = ncq2 * beta * (3.0 - beta * beta) / 2.0
    half = t_extent // 2
    total = 0.0
    for t in range(half + 1):
        g_t = float(np.sum(
            wt * w * w * rho_r * (np.exp(-w * t) + np.exp(-w * (t_extent - t)))
        )) / (12.0 * math.pi ** 2)
        total += g_t * t * t
    return FOUR_PI * total


# ---------------------------------------------------------------------------
# S_IR estimation with jackknife (free reference linearized in m_V).
# ---------------------------------------------------------------------------


def estimate_s_ir(
    g_ll: np.ndarray,
    g_cl: np.ndarray,
    kappa: float,
    free_moment_model: dict[str, float],
) -> dict[str, Any]:
    """S_IR = [Z_V^2 M_LL/(2k)^2] / [M_free(kappa_free(m_V))/(2k_free)^2].

    free_moment_model: {"m_v_ref", "m_free_phys_ref", "dm_free_phys_dm_v"}
    with M_free_phys already in physical normalization (the /(2 kappa_free)^2
    of the matched free run is inside the model, including its m_V
    dependence through the matching rule).
    """
    n_cfg = g_ll.shape[0]

    def free_phys(m_v: float) -> float:
        return (free_moment_model["m_free_phys_ref"]
                + free_moment_model["dm_free_phys_dm_v"]
                * (m_v - free_moment_model["m_v_ref"]))

    def pipeline(ll_mean: np.ndarray, cl_mean: np.ndarray) -> dict[str, float]:
        folded_ll = fold_correlator(ll_mean)
        folded_cl = fold_correlator(cl_mean)
        m_v = effective_mass_windowed(folded_ll)
        z_v, _ = zv_windowed(folded_cl, folded_ll, kappa)
        m_ll_phys = physical_moment(folded_ll, kappa)
        s_ir = z_v * z_v * m_ll_phys / free_phys(m_v)
        return {"m_v": m_v, "z_v": z_v, "m_ll_phys": m_ll_phys, "s_ir": s_ir}

    central = pipeline(g_ll.mean(axis=0), g_cl.mean(axis=0))
    if n_cfg < 2:
        return {**central, "errors": {k: float("nan") for k in central}}
    samples: dict[str, list[float]] = {k: [] for k in central}
    for i in range(n_cfg):
        ll_i = np.delete(g_ll, i, axis=0).mean(axis=0)
        cl_i = np.delete(g_cl, i, axis=0).mean(axis=0)
        res = pipeline(ll_i, cl_i)
        for k, v in res.items():
            samples[k].append(v)
    errors = {}
    for k, vals in samples.items():
        arr = np.array(vals)
        center = arr.mean()
        errors[k] = float(np.sqrt((n_cfg - 1) / n_cfg
                                  * np.sum((arr - center) ** 2)))
    return {**central, "errors": errors}


def apply_envelope(
    s_ir_central: float,
    e_stat: float,
    factors: dict[str, float] = ENVELOPE_FACTORS,
) -> dict[str, Any]:
    """Quadrature combination, multiplicative interval, clamp at zero."""
    e_total = math.sqrt(e_stat ** 2 + sum(v * v for v in factors.values()))
    lo = max(0.0, s_ir_central * (1.0 - e_total))
    hi = s_ir_central * (1.0 + e_total)
    return {
        "e_stat": e_stat,
        "declared_factors": dict(factors),
        "combination": "quadrature",
        "e_total": e_total,
        "s_ir_lo": lo,
        "s_ir_hi": hi,
    }


# ---------------------------------------------------------------------------
# Hybrid bracket over the frozen pqcd grid.
# ---------------------------------------------------------------------------

LAMBDA_KEYS = ("lane_lo", "lane_central", "lane_hi")
K_CUTS = (2.0, 4.0, 8.0)
ORDERS = (1, 2, 3)


def delta_ir_free(ep: Any, lambda3_over_mz: float, k_cut: float) -> float:
    """Frozen closed-form parton moment restricted to [y_thr, y0]."""
    y0 = (k_cut * lambda3_over_mz) ** 2
    total = 0.0
    for name in ph.QUARK_ORDER:
        y_thr = 4.0 * (ep.quark_masses[name] / ep.mz_run) ** 2
        if y0 > y_thr:
            total += ph.parton_moment(
                y_thr, ph.N_C * ph.QUARK_CHARGES_SQ[name], y_lo=y_thr, y_hi=y0)
    return total


def build_hybrid_rows(
    ep: Any,
    s_ir_lo: float,
    s_ir_hi: float,
    *,
    gauss_n: int = 48,
    splits_per_decade: int = 4,
    lambda_keys=LAMBDA_KEYS,
    k_cuts=K_CUTS,
    orders=ORDERS,
    consistency_tol: float = 1e-9,
) -> dict[str, Any]:
    """Evaluate the hybrid grid; checks the zero/free identity first."""
    naive = ph.quark_naive_transport(ep)
    rows = []
    max_identity_defect = 0.0
    for key in lambda_keys:
        lam = sm.LAMBDA3_GRID[key]
        for k in k_cuts:
            ir_free = delta_ir_free(ep, lam, k)
            for order in orders:
                zero = ph.emit_delta_source(
                    sm.make_pqcd(key, k, "zero", order), ep,
                    gauss_n=gauss_n, splits_per_decade=splits_per_decade)
                free = ph.emit_delta_source(
                    sm.make_pqcd(key, k, "free", order), ep,
                    gauss_n=gauss_n, splits_per_decade=splits_per_decade)
                d_zero = zero["components_alpha_inv"]["delta_had"]
                d_free = free["components_alpha_inv"]["delta_had"]
                defect = abs(d_zero + ir_free - d_free)
                max_identity_defect = max(max_identity_defect, defect)
                if defect > consistency_tol:
                    raise RuntimeError(
                        f"zero/free identity defect {defect} at "
                        f"({key}, k={k}, order={order})")
                rows.append({
                    "lambda3_key": key,
                    "k_cut": k,
                    "order": order,
                    "delta_above_alpha_inv": d_zero,
                    "delta_ir_free_alpha_inv": ir_free,
                    "s_eff_at_s_ir_lo": (d_zero + s_ir_lo * ir_free) / naive,
                    "s_eff_at_s_ir_hi": (d_zero + s_ir_hi * ir_free) / naive,
                })
    values = [r["s_eff_at_s_ir_lo"] for r in rows]
    values += [r["s_eff_at_s_ir_hi"] for r in rows]
    return {
        "quark_delta_alpha_inv_naive": naive,
        "rows": rows,
        "max_zero_free_identity_defect": max_identity_defect,
        "s_effective_hybrid": {
            "lo": min(values),
            "hi": max(values),
            "width": max(values) - min(values),
        },
    }
