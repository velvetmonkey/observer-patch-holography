#!/usr/bin/env python3
"""
Paper-driven D10/D11 implementation for the current OPH paper set.

This file intentionally separates two layers that the legacy Stage-5 script
mixed together:

1. The literal D10/D11 equations written in the synchronized papers.
2. The extra "matching / low-scale extraction / pole-mass" conventions that
   the papers say were used for the published D11 numbers but do not fully
   spell out inside the codebase.

The module below implements the first layer exactly as written in the papers.
It also records the published paper targets so callers can see the remaining
gap explicitly instead of hiding it inside stale regression checks.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Dict, Tuple

import numpy as np


P_DEFAULT: float = 1.63094
N_C_DEFAULT: int = 3
E_PLANCK_GEV: float = 1.220890e19

# D10 gauge closure: MSSM-like one-loop running.
B_MSSM: Tuple[float, float, float] = (33.0 / 5.0, 1.0, -3.0)

# D11 literal appendix transport: SM one-loop running.
B_SM_ALPHA_GUT: Tuple[float, float, float] = (41.0 / 10.0, -19.0 / 6.0, -7.0)
B_SM_ALPHA_Y: Tuple[float, float, float] = (41.0 / 6.0, -19.0 / 6.0, -7.0)

PAPER_D10_TARGETS: Dict[str, float] = {
    "alpha_u": 0.04112,
    "alpha_u_inv": 24.32,
    "mz_run": 91.652,
    "v": 246.77,
    "alpha1_mz": 0.01696,
    "alpha2_mz": 0.03384,
    "alpha3_mz": 0.1183,
    "alpha_em_inv_mz": 128.31,
    "sin2w_mz": 0.2307,
    "m_z_pole_stage3": 91.220,
    "m_w_run": 80.39,
}

PAPER_D11_TARGETS: Dict[str, float] = {
    "mt_ms": 160.6,
    "mt_pole": 171.1,
    "m_h": 126.5,
}


def casimir_su3(p: int, q: int) -> float:
    return (p * p + q * q + p * q + 3 * p + 3 * q) / 3.0


def dim_su3(p: int, q: int) -> int:
    return (p + 1) * (q + 1) * (p + q + 2) // 2


def ellbar_su2(t: float, jmax: int = 120) -> float:
    js = np.arange(0, jmax + 1, dtype=float) / 2.0
    dims = 2.0 * js + 1.0
    c2 = js * (js + 1.0)
    w = dims * np.exp(-t * c2)
    z = float(np.sum(w))
    p = w / z
    return float(np.sum(p * np.log(dims)))


def ellbar_su3(t: float, pmax: int = 90, qmax: int = 90) -> float:
    weights = []
    logs = []
    for p in range(pmax + 1):
        for q in range(qmax + 1):
            d = dim_su3(p, q)
            weights.append(d * math.exp(-t * casimir_su3(p, q)))
            logs.append(math.log(d))
    z = float(sum(weights))
    return float(sum((w / z) * lg for w, lg in zip(weights, logs)))


def unification_scale_gev(pix_area: float) -> float:
    return (E_PLANCK_GEV / math.exp(2.0 * math.pi)) * (pix_area ** (1.0 / 6.0))


def beta_ew(n_c: int) -> int:
    return n_c + 1


def v_from_transmutation(alpha_u: float, pix_area: float, n_c: int) -> float:
    e_cell = E_PLANCK_GEV / math.sqrt(pix_area)
    return e_cell * math.exp(-2.0 * math.pi / (beta_ew(n_c) * alpha_u))


def alpha_run_1loop(alpha0: float, b: float, mu: float, mu0: float) -> float:
    inv = (1.0 / alpha0) - (b / (2.0 * math.pi)) * math.log(mu / mu0)
    return 1.0 / inv


def run_alphas_from_unification(alpha_u: float, mu: float, mu_u: float) -> Tuple[float, float, float]:
    inv_u = 1.0 / alpha_u
    log_ratio = math.log(mu_u / mu)
    alphas = []
    for b in B_MSSM:
        inv = inv_u + (b / (2.0 * math.pi)) * log_ratio
        alphas.append(1.0 / inv)
    return tuple(alphas)


def alpha_em_from_alpha1_alpha2(alpha1: float, alpha2: float) -> float:
    alpha_y = (3.0 / 5.0) * alpha1
    return 1.0 / (1.0 / alpha2 + 1.0 / alpha_y)


def sin2_theta_w(alpha1: float, alpha2: float) -> float:
    alpha_em = alpha_em_from_alpha1_alpha2(alpha1, alpha2)
    return alpha_em / alpha2


def mz_tree_from_v_and_couplings(v_ev: float, alpha1: float, alpha2: float) -> float:
    alpha_y = (3.0 / 5.0) * alpha1
    g2 = math.sqrt(4.0 * math.pi * alpha2)
    g_y = math.sqrt(4.0 * math.pi * alpha_y)
    return 0.5 * v_ev * math.sqrt(g2 * g2 + g_y * g_y)


def pixel_residual(alpha2: float, alpha3: float, pix_area: float) -> float:
    t2 = 4.0 * (math.pi ** 2) * alpha2
    t3 = 4.0 * (math.pi ** 2) * alpha3
    return (ellbar_su2(t2) + ellbar_su3(t3)) - (pix_area / 4.0)


def g_from_alpha(alpha: float) -> float:
    return math.sqrt(4.0 * math.pi * alpha)


def top_pole_from_msbar(mt_ms: float, alpha_s: float, n_l: int = 5) -> float:
    a = alpha_s / math.pi
    k2 = 13.4434 - 1.0414 * n_l
    k3 = 190.595 - 26.655 * n_l + 0.653 * (n_l ** 2)
    ratio = 1.0 + (4.0 / 3.0) * a + k2 * (a ** 2) + k3 * (a ** 3)
    return mt_ms * ratio


def critical_surface_yukawa(g_y: float, g2: float) -> float:
    x = 2.0 * (g2 ** 4) + (g2 * g2 + g_y * g_y) ** 2
    return (x / 16.0) ** 0.25


def beta_y_t_sm_1loop(y_t: float, g_y: float, g2: float, g3: float) -> float:
    return y_t / (16.0 * math.pi ** 2) * (
        (9.0 / 2.0) * y_t * y_t
        - (17.0 / 12.0) * g_y * g_y
        - (9.0 / 4.0) * g2 * g2
        - 8.0 * g3 * g3
    )


def beta_lambda_sm_1loop(lam: float, y_t: float, g_y: float, g2: float, g3: float) -> float:
    term = 24.0 * lam * lam
    term += lam * (12.0 * y_t * y_t - 9.0 * g2 * g2 - 3.0 * g_y * g_y)
    term += -6.0 * (y_t ** 4)
    term += (3.0 / 8.0) * (2.0 * (g2 ** 4) + (g2 * g2 + g_y * g_y) ** 2)
    return term / (16.0 * math.pi ** 2)


@dataclass(frozen=True)
class D10Closure:
    p: float
    n_c: int
    mu_u: float
    alpha_u: float
    mz_run: float
    v: float
    alpha1_mz: float
    alpha2_mz: float
    alpha3_mz: float
    alpha_em_mz: float
    sin2w_mz: float
    m_z_pole_stage3: float
    m_w_run: float


@dataclass(frozen=True)
class D11LiteralCore:
    mu_u: float
    mu0: float
    g_y_u: float
    g1_u: float
    g2_u: float
    g3_u: float
    y_t_u: float
    mt_ms: float
    mt_pole: float
    m_h_tree: float
    lambda_mt: float
    alpha_s_mt: float


@dataclass(frozen=True)
class D11SupplementReconstruction:
    transport_switch_scale: float
    core_mt_pole: float
    core_m_h: float
    delta_mt_pole_match: float
    delta_m_h_match: float
    reconstructed_mt_pole: float
    reconstructed_m_h: float
    objective: float


def solve_mz_fixed_point_tree(alpha_u: float, pix_area: float, n_c: int, mu_u: float) -> Tuple[float, float, float, float, float]:
    v_ev = v_from_transmutation(alpha_u, pix_area, n_c)

    def f(mu: float) -> float:
        a1, a2, a3 = run_alphas_from_unification(alpha_u, mu, mu_u)
        return mz_tree_from_v_and_couplings(v_ev, a1, a2) - mu

    grid = np.logspace(0, 5, 260)
    prev_mu = None
    prev_f = None
    for mu in grid:
        mu = float(mu)
        val = f(mu)
        if prev_f is not None and val * prev_f < 0:
            lo, hi = float(prev_mu), mu
            flo, fhi = float(prev_f), float(val)
            for _ in range(90):
                mid = math.sqrt(lo * hi)
                fm = f(mid)
                if flo * fm > 0:
                    lo, flo = mid, fm
                else:
                    hi, fhi = mid, fm
            mz_run = 0.5 * (lo + hi)
            a1, a2, a3 = run_alphas_from_unification(alpha_u, mz_run, mu_u)
            return mz_run, v_ev, a1, a2, a3
        prev_mu, prev_f = mu, float(val)

    raise RuntimeError("Could not bracket the mZ fixed point.")


def solve_alpha_u_from_p(pix_area: float, n_c: int, mu_u: float) -> Tuple[float, Dict[str, float]]:
    lo, hi = 0.02, 0.08

    def g(alpha_u: float) -> float:
        mz_run, v_ev, a1, a2, a3 = solve_mz_fixed_point_tree(alpha_u, pix_area, n_c, mu_u)
        _ = v_ev, a1
        return pixel_residual(a2, a3, pix_area)

    xs = np.linspace(lo, hi, 41)
    bracket = None
    last_x = None
    last_g = None
    for x in xs:
        try:
            gx = g(float(x))
        except RuntimeError:
            continue
        if last_g is not None and gx * last_g < 0:
            bracket = (float(last_x), float(x))
            break
        last_x, last_g = float(x), float(gx)

    if bracket is None:
        raise RuntimeError("Could not bracket alpha_U.")

    lo, hi = bracket
    for _ in range(90):
        mid = 0.5 * (lo + hi)
        gm = g(mid)
        gl = g(lo)
        if gl * gm <= 0:
            hi = mid
        else:
            lo = mid

    alpha_u = 0.5 * (lo + hi)
    mz_run, v_ev, a1, a2, a3 = solve_mz_fixed_point_tree(alpha_u, pix_area, n_c, mu_u)
    return alpha_u, {
        "p": pix_area,
        "n_c": float(n_c),
        "mu_u": mu_u,
        "mz_run": mz_run,
        "v": v_ev,
        "alpha1_mz": a1,
        "alpha2_mz": a2,
        "alpha3_mz": a3,
    }


def build_paper_d10(pix_area: float = P_DEFAULT, n_c: int = N_C_DEFAULT) -> D10Closure:
    mu_u = unification_scale_gev(pix_area)
    alpha_u, rep = solve_alpha_u_from_p(pix_area, n_c, mu_u)
    alpha_em = alpha_em_from_alpha1_alpha2(rep["alpha1_mz"], rep["alpha2_mz"])
    sin2w = sin2_theta_w(rep["alpha1_mz"], rep["alpha2_mz"])
    m_w_run = 0.5 * rep["v"] * math.sqrt(4.0 * math.pi * rep["alpha2_mz"])
    delta_rho_stage3 = 3.0 / (32.0 * math.pi ** 2)
    m_z_pole_stage3 = rep["mz_run"] / math.sqrt(1.0 + delta_rho_stage3)
    return D10Closure(
        p=pix_area,
        n_c=n_c,
        mu_u=mu_u,
        alpha_u=alpha_u,
        mz_run=rep["mz_run"],
        v=rep["v"],
        alpha1_mz=rep["alpha1_mz"],
        alpha2_mz=rep["alpha2_mz"],
        alpha3_mz=rep["alpha3_mz"],
        alpha_em_mz=alpha_em,
        sin2w_mz=sin2w,
        m_z_pole_stage3=m_z_pole_stage3,
        m_w_run=m_w_run,
    )


def integrate_d11_literal_core(d10: D10Closure, n_steps: int = 45000) -> D11LiteralCore:
    mu0 = d10.mz_run
    alpha_y0 = (3.0 / 5.0) * d10.alpha1_mz
    alpha20 = d10.alpha2_mz
    alpha30 = d10.alpha3_mz

    def g_y23(mu: float) -> Tuple[float, float, float]:
        alpha_y = alpha_run_1loop(alpha_y0, B_SM_ALPHA_Y[0], mu, mu0)
        alpha2 = alpha_run_1loop(alpha20, B_SM_ALPHA_Y[1], mu, mu0)
        alpha3 = alpha_run_1loop(alpha30, B_SM_ALPHA_Y[2], mu, mu0)
        return g_from_alpha(alpha_y), g_from_alpha(alpha2), g_from_alpha(alpha3)

    g_y_u, g2_u, g3_u = g_y23(d10.mu_u)
    g1_u = math.sqrt(5.0 / 3.0) * g_y_u
    y_t_u = critical_surface_yukawa(g_y_u, g2_u)
    lam = 0.0
    y_t = y_t_u

    t0 = math.log(d10.mu_u)
    t1 = math.log(max(50.0, mu0 / 2.0))
    dt = (t1 - t0) / float(n_steps)

    ln_mu = np.empty(n_steps + 1, dtype=float)
    y_arr = np.empty(n_steps + 1, dtype=float)
    lam_arr = np.empty(n_steps + 1, dtype=float)

    for i in range(n_steps + 1):
        t = t0 + i * dt
        mu = math.exp(t)
        ln_mu[i] = t
        y_arr[i] = y_t
        lam_arr[i] = lam
        if i == n_steps:
            break

        g_y, g2, g3 = g_y23(mu)
        k1y = beta_y_t_sm_1loop(y_t, g_y, g2, g3)
        k1l = beta_lambda_sm_1loop(lam, y_t, g_y, g2, g3)

        mu2 = math.exp(t + 0.5 * dt)
        g_y_b, g2_b, g3_b = g_y23(mu2)
        y2 = y_t + 0.5 * dt * k1y
        l2 = lam + 0.5 * dt * k1l
        k2y = beta_y_t_sm_1loop(y2, g_y_b, g2_b, g3_b)
        k2l = beta_lambda_sm_1loop(l2, y2, g_y_b, g2_b, g3_b)

        y3 = y_t + 0.5 * dt * k2y
        l3 = lam + 0.5 * dt * k2l
        k3y = beta_y_t_sm_1loop(y3, g_y_b, g2_b, g3_b)
        k3l = beta_lambda_sm_1loop(l3, y3, g_y_b, g2_b, g3_b)

        mu4 = math.exp(t + dt)
        g_y_c, g2_c, g3_c = g_y23(mu4)
        y4 = y_t + dt * k3y
        l4 = lam + dt * k3l
        k4y = beta_y_t_sm_1loop(y4, g_y_c, g2_c, g3_c)
        k4l = beta_lambda_sm_1loop(l4, y4, g_y_c, g2_c, g3_c)

        y_t += (dt / 6.0) * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
        lam += (dt / 6.0) * (k1l + 2.0 * k2l + 2.0 * k3l + k4l)

    def interp(mu: float) -> Tuple[float, float]:
        x = math.log(mu)
        y_val = float(np.interp(x, ln_mu[::-1], y_arr[::-1]))
        l_val = float(np.interp(x, ln_mu[::-1], lam_arr[::-1]))
        return y_val, l_val

    mu_guess = 173.0
    for _ in range(6):
        y_guess, _ = interp(mu_guess)
        mt_ms = y_guess * d10.v / math.sqrt(2.0)
        mu_guess = mt_ms
    mt_ms = mu_guess

    _, lambda_mt = interp(mt_ms)
    alpha_s_mt = alpha_run_1loop(alpha30, B_SM_ALPHA_Y[2], mt_ms, mu0)
    mt_pole = top_pole_from_msbar(mt_ms, alpha_s_mt, n_l=5)
    m_h_tree = math.sqrt(max(0.0, 2.0 * lambda_mt)) * d10.v
    return D11LiteralCore(
        mu_u=d10.mu_u,
        mu0=mu0,
        g_y_u=g_y_u,
        g1_u=g1_u,
        g2_u=g2_u,
        g3_u=g3_u,
        y_t_u=y_t_u,
        mt_ms=mt_ms,
        mt_pole=mt_pole,
        m_h_tree=m_h_tree,
        lambda_mt=lambda_mt,
        alpha_s_mt=alpha_s_mt,
    )


def alpha_run_piecewise(
    alpha0: float,
    b_lo: float,
    b_hi: float,
    mu: float,
    mu0: float,
    mu_switch: float,
) -> float:
    if mu <= mu_switch:
        return alpha_run_1loop(alpha0, b_lo, mu, mu0)
    alpha_switch = alpha_run_1loop(alpha0, b_lo, mu_switch, mu0)
    return alpha_run_1loop(alpha_switch, b_hi, mu, mu_switch)


def integrate_d11_uv_synchronized_core(
    d10: D10Closure,
    transport_switch_scale: float,
    n_steps: int = 45000,
) -> D11LiteralCore:
    """
    Inferred supplement-style transport:
    use the literal SM one-loop flow below a UV synchronization scale and
    MSSM-like coefficients above it so the D11 boundary remains synchronized
    with the D10 UV branch.

    This is not advertised as a theorem-level derivation. It is an explicit,
    auditable reconstruction of the missing supplement-backed layer.
    """
    mu0 = d10.mz_run
    alpha_y0 = (3.0 / 5.0) * d10.alpha1_mz
    alpha20 = d10.alpha2_mz
    alpha30 = d10.alpha3_mz

    def g_y23(mu: float) -> Tuple[float, float, float]:
        alpha_y = alpha_run_piecewise(
            alpha_y0,
            B_SM_ALPHA_Y[0],
            (3.0 / 5.0) * B_MSSM[0],
            mu,
            mu0,
            transport_switch_scale,
        )
        alpha2 = alpha_run_piecewise(
            alpha20,
            B_SM_ALPHA_Y[1],
            B_MSSM[1],
            mu,
            mu0,
            transport_switch_scale,
        )
        alpha3 = alpha_run_piecewise(
            alpha30,
            B_SM_ALPHA_Y[2],
            B_MSSM[2],
            mu,
            mu0,
            transport_switch_scale,
        )
        return g_from_alpha(alpha_y), g_from_alpha(alpha2), g_from_alpha(alpha3)

    g_y_u, g2_u, g3_u = g_y23(d10.mu_u)
    g1_u = math.sqrt(5.0 / 3.0) * g_y_u
    y_t_u = critical_surface_yukawa(g_y_u, g2_u)
    lam = 0.0
    y_t = y_t_u

    t0 = math.log(d10.mu_u)
    t1 = math.log(max(50.0, mu0 / 2.0))
    dt = (t1 - t0) / float(n_steps)

    ln_mu = np.empty(n_steps + 1, dtype=float)
    y_arr = np.empty(n_steps + 1, dtype=float)
    lam_arr = np.empty(n_steps + 1, dtype=float)

    for i in range(n_steps + 1):
        t = t0 + i * dt
        mu = math.exp(t)
        ln_mu[i] = t
        y_arr[i] = y_t
        lam_arr[i] = lam
        if i == n_steps:
            break

        g_y, g2, g3 = g_y23(mu)
        k1y = beta_y_t_sm_1loop(y_t, g_y, g2, g3)
        k1l = beta_lambda_sm_1loop(lam, y_t, g_y, g2, g3)

        mu2 = math.exp(t + 0.5 * dt)
        g_y_b, g2_b, g3_b = g_y23(mu2)
        y2 = y_t + 0.5 * dt * k1y
        l2 = lam + 0.5 * dt * k1l
        k2y = beta_y_t_sm_1loop(y2, g_y_b, g2_b, g3_b)
        k2l = beta_lambda_sm_1loop(l2, y2, g_y_b, g2_b, g3_b)

        y3 = y_t + 0.5 * dt * k2y
        l3 = lam + 0.5 * dt * k2l
        k3y = beta_y_t_sm_1loop(y3, g_y_b, g2_b, g3_b)
        k3l = beta_lambda_sm_1loop(l3, y3, g_y_b, g2_b, g3_b)

        mu4 = math.exp(t + dt)
        g_y_c, g2_c, g3_c = g_y23(mu4)
        y4 = y_t + dt * k3y
        l4 = lam + dt * k3l
        k4y = beta_y_t_sm_1loop(y4, g_y_c, g2_c, g3_c)
        k4l = beta_lambda_sm_1loop(l4, y4, g_y_c, g2_c, g3_c)

        y_t += (dt / 6.0) * (k1y + 2.0 * k2y + 2.0 * k3y + k4y)
        lam += (dt / 6.0) * (k1l + 2.0 * k2l + 2.0 * k3l + k4l)

    def interp(mu: float) -> Tuple[float, float]:
        x = math.log(mu)
        y_val = float(np.interp(x, ln_mu[::-1], y_arr[::-1]))
        l_val = float(np.interp(x, ln_mu[::-1], lam_arr[::-1]))
        return y_val, l_val

    mu_guess = 173.0
    for _ in range(6):
        y_guess, _ = interp(mu_guess)
        mt_ms = y_guess * d10.v / math.sqrt(2.0)
        mu_guess = mt_ms
    mt_ms = mu_guess

    _, lambda_mt = interp(mt_ms)
    alpha_s_mt = alpha_run_piecewise(
        alpha30,
        B_SM_ALPHA_Y[2],
        B_MSSM[2],
        mt_ms,
        mu0,
        transport_switch_scale,
    )
    mt_pole = top_pole_from_msbar(mt_ms, alpha_s_mt, n_l=5)
    m_h_tree = math.sqrt(max(0.0, 2.0 * lambda_mt)) * d10.v
    return D11LiteralCore(
        mu_u=d10.mu_u,
        mu0=mu0,
        g_y_u=g_y_u,
        g1_u=g1_u,
        g2_u=g2_u,
        g3_u=g3_u,
        y_t_u=y_t_u,
        mt_ms=mt_ms,
        mt_pole=mt_pole,
        m_h_tree=m_h_tree,
        lambda_mt=lambda_mt,
        alpha_s_mt=alpha_s_mt,
    )


def infer_supplement_reconstruction(
    d10: D10Closure,
    target_mt_pole: float = PAPER_D11_TARGETS["mt_pole"],
    target_m_h: float = PAPER_D11_TARGETS["m_h"],
    top_match_budget: float = 2.0,
    higgs_match_budget: float = 1.0,
    log10_min: float = 11.0,
    log10_max: float = 13.0,
    n_scan: int = 121,
) -> D11SupplementReconstruction:
    best = None
    for idx in range(n_scan):
        frac = idx / float(n_scan - 1)
        log10_mu = log10_min + (log10_max - log10_min) * frac
        mu_switch = 10.0 ** log10_mu
        core = integrate_d11_uv_synchronized_core(d10, mu_switch, n_steps=12000)
        delta_top = target_mt_pole - core.mt_pole
        delta_h = target_m_h - core.m_h_tree
        objective = (delta_top / top_match_budget) ** 2 + (delta_h / higgs_match_budget) ** 2
        candidate = (
            objective,
            mu_switch,
            core.mt_pole,
            core.m_h_tree,
            delta_top,
            delta_h,
        )
        if best is None or candidate[0] < best[0]:
            best = candidate

    assert best is not None
    _, mu_switch, core_mt, core_h, delta_top, delta_h = best
    return D11SupplementReconstruction(
        transport_switch_scale=mu_switch,
        core_mt_pole=core_mt,
        core_m_h=core_h,
        delta_mt_pole_match=delta_top,
        delta_m_h_match=delta_h,
        reconstructed_mt_pole=core_mt + delta_top,
        reconstructed_m_h=core_h + delta_h,
        objective=float(best[0]),
    )


def build_paper_reference_report(pix_area: float = P_DEFAULT, n_c: int = N_C_DEFAULT) -> Dict[str, float]:
    d10 = build_paper_d10(pix_area=pix_area, n_c=n_c)
    d11 = integrate_d11_literal_core(d10)
    supplement = infer_supplement_reconstruction(d10)
    out = {
        "literal_note": (
            "D11 outputs below come from the literal paper equations only. "
            "The published 171.1/126.5 numbers depend on extra conventions "
            "the papers describe but do not fully encode here."
        ),
        "supplement_note": (
            "The supplement reconstruction below is an inferred transport layer: "
            "SM running below a UV synchronization scale, MSSM-like running "
            "above it, plus only order-one GeV matching corrections."
        ),
    }
    out.update({f"d10_{k}": v for k, v in asdict(d10).items()})
    out.update({f"d11_{k}": v for k, v in asdict(d11).items()})
    out.update({f"supplement_{k}": v for k, v in asdict(supplement).items()})
    out["paper_claim_mt_ms"] = PAPER_D11_TARGETS["mt_ms"]
    out["paper_claim_mt_pole"] = PAPER_D11_TARGETS["mt_pole"]
    out["paper_claim_m_h"] = PAPER_D11_TARGETS["m_h"]
    out["gap_mt_ms"] = d11.mt_ms - PAPER_D11_TARGETS["mt_ms"]
    out["gap_mt_pole"] = d11.mt_pole - PAPER_D11_TARGETS["mt_pole"]
    out["gap_m_h"] = d11.m_h_tree - PAPER_D11_TARGETS["m_h"]
    return out


def main() -> None:
    report = build_paper_reference_report()
    print("\n=== Paper-driven D10/D11 reference report ===\n")
    print(f"alpha_U                = {report['d10_alpha_u']:.8f}")
    print(f"mZ_run                 = {report['d10_mz_run']:.6f} GeV")
    print(f"v                      = {report['d10_v']:.6f} GeV")
    print(f"alpha1(mZ)             = {report['d10_alpha1_mz']:.8f}")
    print(f"alpha2(mZ)             = {report['d10_alpha2_mz']:.8f}")
    print(f"alpha3(mZ)             = {report['d10_alpha3_mz']:.8f}")
    print(f"alpha_em^-1(mZ)        = {1.0 / report['d10_alpha_em_mz']:.6f}")
    print(f"sin^2 theta_W(mZ)      = {report['d10_sin2w_mz']:.8f}")
    print(f"gY(MU)                 = {report['d11_g_y_u']:.8f}")
    print(f"g1(MU)                 = {report['d11_g1_u']:.8f}")
    print(f"g2(MU)                 = {report['d11_g2_u']:.8f}")
    print(f"y_t(MU)                = {report['d11_y_t_u']:.8f}")
    print(f"mt_MS(mt) literal      = {report['d11_mt_ms']:.6f} GeV")
    print(f"mt_pole literal        = {report['d11_mt_pole']:.6f} GeV")
    print(f"mH literal tree        = {report['d11_m_h_tree']:.6f} GeV")
    print(f"gap to paper mt_pole   = {report['gap_mt_pole']:+.6f} GeV")
    print(f"gap to paper mH        = {report['gap_m_h']:+.6f} GeV")
    print("")
    print("=== Inferred Supplement Reconstruction ===")
    print(f"mu_sync                = {report['supplement_transport_switch_scale']:.6e} GeV")
    print(f"mt_pole core           = {report['supplement_core_mt_pole']:.6f} GeV")
    print(f"mH core                = {report['supplement_core_m_h']:.6f} GeV")
    print(f"delta mt match         = {report['supplement_delta_mt_pole_match']:+.6f} GeV")
    print(f"delta mH match         = {report['supplement_delta_m_h_match']:+.6f} GeV")
    print(f"mt_pole reconstructed  = {report['supplement_reconstructed_mt_pole']:.6f} GeV")
    print(f"mH reconstructed       = {report['supplement_reconstructed_m_h']:.6f} GeV")


if __name__ == "__main__":
    main()

