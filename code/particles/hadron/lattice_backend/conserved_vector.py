"""Transverse local-local and conserved-local vector correlators.

Output class: diagnostic, non-promoting. Companion to
``vector_correlator.py``; adds the measurement pieces the hybrid IR bracket
diagnostic needs and leaves the existing module untouched.

Axis and polarization conventions (verified numerically in
``test_hybrid_ir_bracket.py``)
-----------------------------------------------------------------------

The engine pairs hopping direction mu with GAMMA[mu] and with site axis mu.
The correlator time axis is axis 0, so GAMMA[0] is the temporal
polarization: on a free field its zero-momentum local correlator vanishes
for t > 0 at the level of the local current's O(a) non-conservation. The
three transverse polarizations along the time axis are GAMMA[1], GAMMA[2],
GAMMA[3]. The pre-existing ``vector_correlator.vector_correlator`` averages
GAMMA[0..2], i.e. one temporal plus two transverse channels; relative to
the per-polarization transverse correlator that average carries a factor
2/3 (plus the small temporal remnant). ``transverse_vector_correlator``
below averages the three true transverse channels and is the contraction
the hybrid IR diagnostic uses.

Conserved (point-split) vector current
--------------------------------------

For the hopping-normalized Wilson-clover action of ``dirac.py`` the exact
Noether current of the U(1) phase rotation is

    V_mu(x) = kappa * [ psibar(x+mu) (1+gamma_mu) U_mu(x)^dag psi(x)
                        - psibar(x) (1-gamma_mu) U_mu(x) psi(x+mu) ],

which satisfies the exact backward-difference Ward identity
sum_mu [V_mu(x) - V_mu(x-mu)] = 0 inside correlation functions away from
contact points (the clover term is invariant under the phase rotation, so
the identity is unchanged by c_SW). The identity is checked numerically on
a rough gauge background by ``ward_divergence_offsource_max``.

Because the current is exactly conserved it needs no renormalization;
the local current renormalization follows from the standard estimator

    Z_V^eff(t) = C_CL(t) / (2 kappa C_LL(t)).

Derivation of the 2 kappa: in physical field normalization
psi_phys = sqrt(2 kappa) psi_hop, the current above equals the standard
conserved current (1/2)[psibar_p(x+mu)(1+gamma_mu)U^dag psi_p(x) - ...],
while the local hopping current is J_phys/(2 kappa). With V_R = Z_V J_loc
and V_cons = V_R exactly, the computed hopping-normalized ratio is
C_CL/C_LL = 2 kappa Z_V up to O(a) and excited-state contamination. On the
free field the estimator plateaus at exactly 1 (verified in
``test_hybrid_ir_bracket.py``), which anchors both the sign and the
normalization.

Hopping-field normalization of the moments: a local-local correlator built
from hopping propagators is the physical one times (2 kappa)^2. The
analysis layer applies that factor; nothing here does.
"""

from __future__ import annotations

import numpy as np

from .core import GAMMA, GAMMA5, IDSPIN, shift

TRANSVERSE_DIRS = (1, 2, 3)


def _local_channel(prop: np.ndarray, k: int) -> np.ndarray:
    """Local-local channel Re Tr[gamma_k S gamma_k gamma_5 S^dag gamma_5]."""
    a = GAMMA5 @ GAMMA[k]
    b = GAMMA[k] @ GAMMA5
    term = np.einsum(
        "fb,txyzbicj,ce,txyzfiej->t", a, prop, b, np.conj(prop), optimize=True)
    return np.real(term)


def transverse_vector_correlator(prop: np.ndarray) -> np.ndarray:
    """(1/3) sum over the three transverse polarizations GAMMA[1..3].

    Same normalization conventions as ``vector_correlator.vector_correlator``
    (single flavor, unit charge, color trace included, hopping-normalized
    propagator) with the temporal channel excluded.
    """
    total = np.zeros(prop.shape[0])
    for k in TRANSVERSE_DIRS:
        total += _local_channel(prop, k)
    return total / 3.0


def temporal_vector_correlator(prop: np.ndarray) -> np.ndarray:
    """Temporal (GAMMA[0]) local-local channel, for diagnostics."""
    return _local_channel(prop, 0)


def _conserved_local_channel(
    prop: np.ndarray, ubc: np.ndarray, kappa: float, mu: int, nu: int
) -> np.ndarray:
    """Per-site Re < V_mu^cons(x) J_nu^loc(0) > with the fermion-loop sign.

    Returns the site field (T, X, Y, Z); the caller sums the spatial axes.
    Uses the boundary-adjusted links ``ubc`` so the contraction is exactly
    consistent with the operator that produced ``prop``.
    """
    u_mu = ubc[mu]
    prop_shift = shift(prop, mu, +1)
    a_plus = GAMMA5 @ (IDSPIN + GAMMA[mu])
    a_minus = GAMMA5 @ (IDSPIN - GAMMA[mu])
    b = GAMMA[nu] @ GAMMA5
    # term1 = -kappa Tr[(1+g_mu) U_mu(x)^dag S(x) g_nu g5 S(x+mu)^dag g5]
    term1 = np.einsum(
        "fb,txyzqp,txyzbqcj,ce,txyzfpej->txyz",
        a_plus, np.conj(u_mu), prop, b, np.conj(prop_shift), optimize=True)
    # term2 = +kappa Tr[(1-g_mu) U_mu(x) S(x+mu) g_nu g5 S(x)^dag g5]
    term2 = np.einsum(
        "fb,txyzpq,txyzbqcj,ce,txyzfpej->txyz",
        a_minus, u_mu, prop_shift, b, np.conj(prop), optimize=True)
    # Overall sign chosen so the free-field estimator C_CL/(2 kappa C_LL)
    # plateaus at +1, matching the fermion-loop sign convention of the
    # local-local contraction.
    return kappa * np.real(term1 - term2)


def conserved_local_correlator(
    prop: np.ndarray, ubc: np.ndarray, kappa: float
) -> np.ndarray:
    """C_CL(t): (1/3) sum_k sum_x of conserved(sink)-local(source), k=1..3.

    Sign convention matches ``transverse_vector_correlator`` (both are
    -<J J> with the fermion-loop minus absorbed), so C_CL(t)/C_LL(t) is the
    positive Z_V^eff estimator.
    """
    t_extent = prop.shape[0]
    total = np.zeros(t_extent)
    for k in TRANSVERSE_DIRS:
        site = _conserved_local_channel(prop, ubc, kappa, k, k)
        total += site.sum(axis=(1, 2, 3))
    return total / 3.0


def zv_effective(
    c_cl: np.ndarray, c_ll: np.ndarray, kappa: float
) -> np.ndarray:
    """Z_V^eff(t) = C_CL(t) / (2 kappa C_LL(t)); NaN where C_LL vanishes."""
    out = np.full(len(c_cl), np.nan)
    ok = c_ll != 0.0
    out[ok] = c_cl[ok] / (2.0 * kappa * c_ll[ok])
    return out


def ward_divergence_offsource_max(
    prop: np.ndarray, ubc: np.ndarray, kappa: float, nu: int = 1
) -> tuple[float, float]:
    """Max |sum_mu backward-difference of <V_mu^cons(x) J_nu^loc(0)>| off-source.

    Returns (max_offsource, scale) where scale is the max |V_mu correlator|
    over sites, so max_offsource/scale is a relative Ward-identity defect.
    Exact up to solver tolerance for every gauge background.
    """
    div = np.zeros(prop.shape[:4])
    scale = 0.0
    for mu in range(4):
        site = _conserved_local_channel(prop, ubc, kappa, mu, nu)
        scale = max(scale, float(np.max(np.abs(site))))
        div += site - np.roll(site, +1, axis=mu)
    mask = np.ones(prop.shape[:4], dtype=bool)
    mask[0, 0, 0, 0] = False  # contact point at the source
    return float(np.max(np.abs(div[mask]))), scale
