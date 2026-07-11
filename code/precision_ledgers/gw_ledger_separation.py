"""Numerical verification for PAPER.tex Section 5.14 (issue #537).

The section keeps two error ledgers separate:

1. State--observable ledger: trace distance controls expectation values of
   bounded local observables via the dual-norm inequality
   |Tr O (rho - sigma)| <= ||O||_inf * ||rho - sigma||_1.
2. Dynamical-parameter ledger: propagation speed is a spectral/dispersion
   property of a generator. Trace distance between states at one time does
   NOT control it. The conditional bridge lemma of Section 5.14 states that
   IF a band-uniform generator estimate eta_dyn is supplied, THEN
   sup_{k in B} |c_GW(k)/c - 1| <= L_B * eta_dyn,  L_B = 1 + 4 M_B,
   and stationary propagation over path length D obeys the group-delay bound
   |Delta t| <= (D/c) * q / (1 - q) with q = L_B * eta_dyn < 1.

This module verifies three things numerically:

A. Counterexample (ledger separation is necessary): two generators H_0(k)
   and (1 + gamma) H_0(k) share the same band eigenstate at every k, so the
   trace distance between the corresponding states is exactly zero and every
   equal-time bounded observable agrees exactly, while the group velocities
   differ by the arbitrary fraction gamma. No trace-distance certificate can
   bound |c_GW/c - 1|.

B. Conditional bridge lemma: for randomized C^1 fiber families H_0(k) with a
   simple band omega_0(k) = c k isolated by a uniform gap, and randomized C^1
   perturbations with eta_dyn < 1/4, the Davis--Kahan projector bound
   ||P_nu - P_0||_inf <= 2 eta_dyn, the group-velocity bound with
   L_B = 1 + 4 M_B, and the group-delay bound all hold on the sampled band.

C. State--observable ledger: the dual-norm inequality holds for random
   states and random bounded observables.

The suite is deterministic (fixed seeds, no timestamps). Run from the repo
root:

    python3 code/precision_ledgers/gw_ledger_separation.py
    python3 -m pytest code/precision_ledgers/test_gw_ledger_separation.py

It validates only the mathematics of the two ledgers and of the conditional
bridge gate. It does not construct the OPH TT generator and proves no
estimate eta_dyn <= C_B r_N; that bridge remains open in Section 5.14.
"""

from __future__ import annotations

import json
import os

import numpy as np

C_LIGHT = 1.0  # angular-frequency units, hbar = 1; band wave numbers are O(1)


# ---------------------------------------------------------------------------
# Fiber-family construction
# ---------------------------------------------------------------------------

def _random_hermitian(rng: np.random.Generator, dim: int, norm: float = 1.0) -> np.ndarray:
    m = rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
    h = 0.5 * (m + m.conj().T)
    return norm * h / np.linalg.norm(h, ord=2)


def make_reference_family(rng: np.random.Generator, dim: int = 6, gap: float = 1.0):
    """Return (H0, band_index) where H0(k) has the simple band omega_0(k) = c k.

    Eigenvalues: lambda_0(k) = c k and lambda_j(k) = c k + gap * (j + 0.3 sin(k + j))
    for j >= 1, so the band is isolated by a uniform spectral gap >= 0.7 * gap.
    Eigenvectors rotate smoothly via U(k) = expm(i k A) for a fixed Hermitian A.
    """
    a = _random_hermitian(rng, dim, norm=0.5)
    evals_a, evecs_a = np.linalg.eigh(a)

    def unitary(k: float) -> np.ndarray:
        return (evecs_a * np.exp(1j * k * evals_a)) @ evecs_a.conj().T

    def h0(k: float) -> np.ndarray:
        levels = np.array(
            [C_LIGHT * k]
            + [C_LIGHT * k + gap * (j + 0.3 * np.sin(k + j)) for j in range(1, dim)]
        )
        u = unitary(k)
        return u @ np.diag(levels) @ u.conj().T

    return h0


def make_perturbation(rng: np.random.Generator, dim: int, strength: float):
    """Smooth C^1 Hermitian perturbation V(k) with ||V||, ||V'|| = O(strength)."""
    w1 = _random_hermitian(rng, dim)
    w2 = _random_hermitian(rng, dim)
    w3 = _random_hermitian(rng, dim)

    def v(k: float) -> np.ndarray:
        return strength * (w1 + np.sin(k) * w2 + 0.5 * np.cos(2.0 * k) * w3)

    return v


def _derivative(fam, k: float, step: float = 1e-6) -> np.ndarray:
    return (fam(k + step) - fam(k - step)) / (2.0 * step)


def _band_state(h: np.ndarray, target: float):
    """Eigenpair of h with eigenvalue closest to target."""
    evals, evecs = np.linalg.eigh(h)
    idx = int(np.argmin(np.abs(evals - target)))
    return evals[idx], evecs[:, idx]


# ---------------------------------------------------------------------------
# Part A: trace distance does not bound dispersion (counterexample)
# ---------------------------------------------------------------------------

def run_counterexample(seed: int = 7, gamma: float = 0.05, dim: int = 6,
                       band=(0.5, 2.0), samples: int = 21) -> dict:
    """Generators H0 and (1+gamma) H0: identical band states, different speeds."""
    rng = np.random.default_rng(seed)
    h0 = make_reference_family(rng, dim=dim)
    ks = np.linspace(band[0], band[1], samples)

    max_trace_distance = 0.0
    max_observable_gap = 0.0
    for k in ks:
        h = h0(k)
        _, psi0 = _band_state(h, C_LIGHT * k)
        _, psi1 = _band_state((1.0 + gamma) * h, (1.0 + gamma) * C_LIGHT * k)
        rho0 = np.outer(psi0, psi0.conj())
        rho1 = np.outer(psi1, psi1.conj())
        diff = rho0 - rho1
        max_trace_distance = max(
            max_trace_distance, 0.5 * np.sum(np.abs(np.linalg.eigvalsh(diff)))
        )
        obs = _random_hermitian(rng, dim)
        max_observable_gap = max(max_observable_gap, abs(np.trace(obs @ diff).real))

    # Group velocities via Hellmann--Feynman on both generators.
    def group_velocity(fam, k, target):
        _, psi = _band_state(fam(k), target)
        dh = _derivative(fam, k)
        return (psi.conj() @ dh @ psi).real

    k_mid = float(np.mean(band))
    v0 = group_velocity(h0, k_mid, C_LIGHT * k_mid)
    v1 = group_velocity(lambda k: (1.0 + gamma) * h0(k), k_mid,
                        (1.0 + gamma) * C_LIGHT * k_mid)

    return {
        "gamma": gamma,
        "max_trace_distance": float(max_trace_distance),
        "max_bounded_observable_gap": float(max_observable_gap),
        "fractional_speed_error": float(abs(v1 / v0 - 1.0)),
    }


# ---------------------------------------------------------------------------
# Part B: conditional bridge lemma (L_B = 1 + 4 M_B) and group delay
# ---------------------------------------------------------------------------

def run_bridge_lemma(seed: int, strength: float, dim: int = 6,
                     band=(0.5, 2.0), samples: int = 41,
                     path_length: float = 1.0e6) -> dict:
    """Check the Section 5.14 conditional estimates on one random family."""
    rng = np.random.default_rng(seed)
    h0 = make_reference_family(rng, dim=dim)
    v = make_perturbation(rng, dim, strength)
    h_nu = lambda k: h0(k) + v(k)
    ks = np.linspace(band[0], band[1], samples)

    # Band-derived constants: uniform gap g_B, slope bound M_B.
    gap_b = min(
        np.min(np.abs(np.delete(np.linalg.eigvalsh(h0(k)),
                                int(np.argmin(np.abs(np.linalg.eigvalsh(h0(k)) - C_LIGHT * k))))
                      - C_LIGHT * k))
        for k in ks
    )
    m_b = max(np.linalg.norm(_derivative(h0, k), ord=2) for k in ks) / C_LIGHT

    # Dynamical error eta_dyn as defined in Section 5.14.
    eta_dyn = max(
        max(np.linalg.norm(v(k), ord=2) for k in ks) / gap_b,
        max(np.linalg.norm(_derivative(v, k), ord=2) for k in ks) / C_LIGHT,
    )

    max_projector_gap = 0.0
    max_speed_error = 0.0
    for k in ks:
        _, psi0 = _band_state(h0(k), C_LIGHT * k)
        _, psi_nu = _band_state(h_nu(k), C_LIGHT * k)
        p0 = np.outer(psi0, psi0.conj())
        p_nu = np.outer(psi_nu, psi_nu.conj())
        max_projector_gap = max(
            max_projector_gap, np.linalg.norm(p_nu - p0, ord=2)
        )
        v_nu = (psi_nu.conj() @ _derivative(h_nu, k) @ psi_nu).real
        max_speed_error = max(max_speed_error, abs(v_nu / C_LIGHT - 1.0))

    l_b = 1.0 + 4.0 * m_b
    q = l_b * eta_dyn

    # Group-delay check: worst arrival-time mismatch over the band vs the bound.
    max_delay = 0.0
    for k in ks:
        _, psi_nu = _band_state(h_nu(k), C_LIGHT * k)
        v_nu = (psi_nu.conj() @ _derivative(h_nu, k) @ psi_nu).real
        max_delay = max(max_delay, abs(path_length / v_nu - path_length / C_LIGHT))
    delay_bound = (path_length / C_LIGHT) * q / (1.0 - q) if q < 1.0 else float("inf")

    return {
        "seed": seed,
        "strength": strength,
        "gap_B": float(gap_b),
        "M_B": float(m_b),
        "L_B": float(l_b),
        "eta_dyn": float(eta_dyn),
        "eta_below_quarter": bool(eta_dyn < 0.25),
        "projector_gap": float(max_projector_gap),
        "projector_bound": float(2.0 * eta_dyn),
        "projector_ok": bool(max_projector_gap <= 2.0 * eta_dyn + 1e-12),
        "speed_error": float(max_speed_error),
        "speed_bound": float(l_b * eta_dyn),
        "speed_ok": bool(max_speed_error <= l_b * eta_dyn + 1e-12),
        "group_delay": float(max_delay),
        "group_delay_bound": float(delay_bound),
        "group_delay_ok": bool(max_delay <= delay_bound + 1e-9),
    }


# ---------------------------------------------------------------------------
# Part C: state--observable ledger (dual-norm inequality)
# ---------------------------------------------------------------------------

def run_dual_norm_check(seed: int = 11, dim: int = 8, trials: int = 200) -> dict:
    rng = np.random.default_rng(seed)
    worst_ratio = 0.0
    for _ in range(trials):
        def random_state():
            m = rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
            rho = m @ m.conj().T
            return rho / np.trace(rho).real

        rho, sigma = random_state(), random_state()
        obs = _random_hermitian(rng, dim, norm=float(rng.uniform(0.1, 5.0)))
        lhs = abs(np.trace(obs @ (rho - sigma)).real)
        rhs = np.linalg.norm(obs, ord=2) * np.sum(np.abs(np.linalg.eigvalsh(rho - sigma)))
        worst_ratio = max(worst_ratio, lhs / rhs)
    return {"trials": trials, "worst_lhs_over_rhs": float(worst_ratio),
            "dual_norm_ok": bool(worst_ratio <= 1.0 + 1e-12)}


# ---------------------------------------------------------------------------
# Receipt
# ---------------------------------------------------------------------------

def run_suite() -> dict:
    counterexample = run_counterexample()
    bridge = [
        run_bridge_lemma(seed=seed, strength=strength)
        for seed in (1, 2, 3)
        for strength in (0.002, 0.01, 0.05)
    ]
    dual = run_dual_norm_check()
    return {
        "section": "PAPER.tex 5.14 (state--observable vs dynamical-parameter ledgers)",
        "issue": 537,
        "counterexample": counterexample,
        "counterexample_separates_ledgers": bool(
            counterexample["max_trace_distance"] < 1e-10
            and counterexample["fractional_speed_error"] > 1e-3
        ),
        "bridge_lemma_cases": bridge,
        "bridge_lemma_all_ok": bool(all(
            c["eta_below_quarter"] and c["projector_ok"] and c["speed_ok"]
            and c["group_delay_ok"] for c in bridge
        )),
        "dual_norm": dual,
    }


def main() -> None:
    receipt = run_suite()
    out_dir = os.path.join(os.path.dirname(__file__), "runs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "gw_ledger_separation_current.json")
    with open(out_path, "w") as fh:
        json.dump(receipt, fh, indent=2)
        fh.write("\n")
    print(json.dumps(receipt, indent=2))
    print(f"receipt written to {out_path}")
    assert receipt["counterexample_separates_ledgers"]
    assert receipt["bridge_lemma_all_ok"]
    assert receipt["dual_norm"]["dual_norm_ok"]


if __name__ == "__main__":
    main()
