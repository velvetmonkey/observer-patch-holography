"""Vector-current two-point correlator and TMR dispersion moment.

Output class: diagnostic, non-promoting. Nothing in this module carries
promotion weight for the #425 closure.

Object measured
---------------

On a fixed gauge configuration, from the point propagator S(x, 0) of one
Wilson-clover flavor, the zero-momentum local-vector correlator

    G(t) = -(1/3) sum_k sum_x < J_k(x, t) J_k(0) >
         =  (1/3) sum_k sum_x Re Tr[ gamma_k S(x,0) gamma_k
                                     gamma_5 S(x,0)^dag gamma_5 ],

with J_k = psibar gamma_k psi the local (non-conserved) vector current and
the sink relation S(0, x) = gamma_5 S(x, 0)^dag gamma_5. The color trace is
included, so a single flavor of unit charge corresponds to the R-ratio
normalization N_c * Q^2 with N_c = 3 and Q = 1. The local current requires a
multiplicative renormalization Z_V; this module declares Z_V = 1 and lists it
as an uncontrolled conversion factor.

Time-momentum representation (Bernecker-Meyer)
----------------------------------------------

With the spectral representation G(t) = int_0^inf domega omega^2
rho(omega^2) exp(-omega t) and rho(s) = R(s) / (12 pi^2), the once-subtracted
vacuum polarization at Euclidean Q^2 is

    Pihat(Q^2) = Pi(Q^2) - Pi(0)
               = int_0^inf dt G(t) [ t^2 - (4/Q^2) sin^2(Q t / 2) ]
               = Q^2 int ds rho(s) / (s (s + Q^2)).

Correspondence to the payload contract
--------------------------------------

The declared contract in ``ward_projected_payload/payload_harness.py`` emits

    Delta_had = mZ^2/(3 pi) * int ds rho_R(s) / (s (s + mZ^2)),

with rho_R in R-ratio normalization (free massless parton contributes
N_c Q^2), kernel string "mZ^2/(3*pi*s*(s+mZ^2))", scheme
``d10_ward_projected_once_subtracted_at_mZ2``. Using rho_R = 12 pi^2 rho,

    Delta_had = (12 pi^2 / (3 pi)) * Pihat(mZ^2) = 4 pi * Pihat(mZ^2),

so the contract moment equals 4 pi times the TMR integral with the kernel
K(t; mZ) = t^2 - (4/mZ^2) sin^2(mZ t / 2). This algebraic identity is exact;
``tmr_moment`` therefore returns 4 pi * sum_t G(t) K(t; a*mZ) in lattice
units. The identity is verified by ``test_vector_correlator.py`` against the
contract-side closed form ``payload_harness.kernel_moment_atom``.

Conversion factors that this module cannot certify, emitted as separate
declared fields by the diagnostic runner:

- a*mZ: the contract mZ in lattice units. A source-emitted scale setting is
  work in progress; the runner evaluates the kernel on a declared a*mZ grid
  and in the a*mZ -> infinity limit K(t) -> t^2, which is the coarse-lattice
  regime (any a^-1 far below mZ gives K(t) = t^2 to relative accuracy
  4/(a*mZ)^2 for t >= 1).
- Z_V^2: local-current renormalization, declared 1, uncertified.
- charge factor: the U(1)_Q light connected doublet carries
  Q_u^2 + Q_d^2 = 5/9 per the contract normalization (N_c is inside the
  color trace); quark-line disconnected contributions are absent.

Discrete-time conventions
-------------------------

The correlator on an antiperiodic-time lattice satisfies G(t) = G(T - t) for
the vector channel; ``fold_correlator`` symmetrizes to t in [0, T/2]. The
moment sums the folded correlator over t = 0 .. T/2 with unit lattice
spacing; K(0; anything) = 0, so the t = 0 contact term drops out exactly.
The truncation at T/2 and the missing backward-tail correction are finite-T
effects listed in the runner's systematics block.
"""

from __future__ import annotations

import math

import numpy as np

from .core import GAMMA, GAMMA5

FOUR_PI = 4.0 * math.pi


def vector_correlator(prop: np.ndarray) -> np.ndarray:
    """G(t) for one flavor of unit charge from a point propagator.

    prop has shape (T, X, Y, Z, 4, 3, 4, 3) as returned by
    ``dirac.point_propagator``. Returns a real array of length T with

        G(t) = (1/3) sum_k sum_x Re Tr[ A_k S B_k S^dag ],
        A_k = gamma_5 gamma_k,  B_k = gamma_k gamma_5,

    which is the spin-color trace written out in the module docstring.
    """
    total = np.zeros(prop.shape[0])
    for k in range(3):
        a = GAMMA5 @ GAMMA[k]
        b = GAMMA[k] @ GAMMA5
        term = np.einsum(
            "fb,txyzbicj,ce,txyzfiej->t",
            a, prop, b, np.conj(prop), optimize=True)
        total += np.real(term)
    return total / 3.0


def fold_correlator(g: np.ndarray) -> np.ndarray:
    """Symmetrize G(t) about T/2; returns length T//2 + 1 (T even)."""
    t_extent = len(g)
    if t_extent % 2 != 0:
        raise ValueError("fold_correlator requires even time extent")
    half = t_extent // 2
    out = np.empty(half + 1)
    out[0] = g[0]
    out[half] = g[half]
    for t in range(1, half):
        out[t] = 0.5 * (g[t] + g[t_extent - t])
    return out


def tmr_kernel(t: np.ndarray, amz: float | None = None) -> np.ndarray:
    """K(t; a*mZ) = t^2 - (4/(a*mZ)^2) sin^2(a*mZ*t/2); None gives t^2.

    K(0) = 0 in both branches, so the contact term at t = 0 never enters
    the moment.
    """
    t = np.asarray(t, dtype=float)
    if amz is None:
        return t * t
    return t * t - (4.0 / (amz * amz)) * np.sin(0.5 * amz * t) ** 2


def tmr_moment(g_folded: np.ndarray, amz: float | None = None) -> float:
    """Contract-normalized moment 4*pi * sum_t G(t) K(t; a*mZ).

    For a correlator whose spectral density has R-ratio normalization this
    equals the payload-contract moment mZ^2/(3*pi) int rho/(s(s+mZ^2)) ds in
    lattice units, before the a*mZ, Z_V^2, and charge-factor conversions
    documented in the module docstring. amz = None selects the t^2 kernel,
    the a*mZ -> infinity limit.
    """
    t = np.arange(len(g_folded), dtype=float)
    return FOUR_PI * float(np.sum(g_folded * tmr_kernel(t, amz)))


def jackknife_scalar(samples: np.ndarray) -> tuple[float, float]:
    """Jackknife mean and error of a 1D sample array."""
    n = len(samples)
    if n < 2:
        return float(np.mean(samples)), float("nan")
    means = np.array([np.mean(np.delete(samples, i)) for i in range(n)])
    center = float(np.mean(means))
    err = float(np.sqrt((n - 1) / n * np.sum((means - center) ** 2)))
    return center, err


def jackknife_correlator(samples: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per-timeslice jackknife mean and error for samples of shape (n, T)."""
    n = samples.shape[0]
    mean = samples.mean(axis=0)
    if n < 2:
        return mean, np.full(samples.shape[1], np.nan)
    means = np.array([np.mean(np.delete(samples, i, axis=0), axis=0) for i in range(n)])
    center = means.mean(axis=0)
    err = np.sqrt((n - 1) / n * np.sum((means - center) ** 2, axis=0))
    return center, err


def jackknife_moment(
    correlator_samples: np.ndarray,
    amz: float | None = None,
) -> tuple[float, float]:
    """Jackknife mean and error of the TMR moment over configurations.

    correlator_samples has shape (n_cfg, T); each row is folded and summed
    with the kernel inside the jackknife loop, so the error propagates
    through the full pipeline.
    """
    moments = np.array([
        tmr_moment(fold_correlator(row), amz) for row in correlator_samples
    ])
    return jackknife_scalar(moments)


# ----------------------------------------------------------------------------
# Analytic references for the round-trip tests.
# ----------------------------------------------------------------------------


def synthetic_atom_correlator(
    t_extent: int,
    s0: float,
    weight: float,
) -> np.ndarray:
    """G(t) of a single spectral atom rho_R(s) = weight * delta(s - s0).

    With rho = rho_R/(12 pi^2), G(t) = weight * sqrt(s0)/(24 pi^2)
    * exp(-sqrt(s0) t), on t = 0 .. t_extent - 1 in lattice units.
    """
    omega = math.sqrt(s0)
    t = np.arange(t_extent, dtype=float)
    return weight * omega / (24.0 * math.pi**2) * np.exp(-omega * t)


def analytic_atom_moment_discrete(
    t_extent: int,
    s0: float,
    weight: float,
    amz: float | None = None,
) -> float:
    """Exact discrete-time sum of the atom moment (geometric series).

    Closed forms with q = exp(-omega), omega = sqrt(s0), summed over
    t = 0 .. t_extent - 1:

        sum t^2 q^t and sum q^t cos(amz t)

    evaluated exactly; the kernel combination matches ``tmr_moment`` applied
    to ``synthetic_atom_correlator`` on the same time range, so this
    validates the kernel and summation code with no discretization slack.
    """
    omega = math.sqrt(s0)
    q = math.exp(-omega)
    n = t_extent

    # sum_{t=0}^{n-1} t^2 q^t by differentiating the finite geometric sum.
    def sum_t2_qt() -> float:
        total = 0.0
        for t in range(n):
            total += t * t * q**t
        return total

    def sum_qt_cos() -> float:
        total = 0.0
        for t in range(n):
            total += q**t * math.cos(amz * t)
        return total

    prefactor = weight * omega / (24.0 * math.pi**2)
    if amz is None:
        kernel_sum = sum_t2_qt()
    else:
        # sin^2(x) = (1 - cos 2x)/2 with x = amz t / 2.
        sum_q = (1.0 - q**n) / (1.0 - q)
        kernel_sum = sum_t2_qt() - (2.0 / (amz * amz)) * (sum_q - sum_qt_cos())
    return FOUR_PI * prefactor * kernel_sum


def analytic_atom_moment_continuum(
    s0: float,
    weight: float,
    mz2: float,
) -> float:
    """Contract-side closed form weight * mZ^2/(3 pi s0 (s0 + mZ^2)).

    Identical to weight * kernel_moment_atom(s0/mZ^2) in
    ``ward_projected_payload/payload_harness.py``.
    """
    return weight * mz2 / (3.0 * math.pi * s0 * (s0 + mz2))
