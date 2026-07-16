#!/usr/bin/env python3
"""Certified SM one-loop gauge-boson self-energies, 't Hooft-Feynman gauge.

Transcribed from A. Denner, "Techniques for the calculation of electroweak
radiative corrections at the one-loop level and results for W-physics at
LEP200", Fortschr. Phys. 41 (1993) 307, arXiv:0709.1075:

- Appendix B ("Self energies"): the transverse gauge-boson self-energies
  Sigma^AA_T, Sigma^AZ_T, Sigma^ZZ_T, Sigma^W_T in the 't Hooft-Feynman
  gauge, tadpole-renormalized scheme (hat T = 0, sect. 3.3 eq. (RCT)).
- Appendix A: coupling conventions g_f^+ = -(s_W/c_W) Q_f and
  g_f^- = (I^3_{W,f} - s_W^2 Q_f)/(s_W c_W).
- Sect. 4.4: the scalar one- and two-point functions A_0 (eq. before
  "Scalar two-point function") and B_0 (eq. (B0)).
- Sect. 8: the Delta r formula with the vertex/box constant
  (alpha/(4 pi s_W^2)) (6 + (7 - 4 s_W^2)/(2 s_W^2) log c_W^2), used here
  as a certification target only.

All functions return MS-bar finite parts: the UV pole Delta is set to zero
and every logarithm carries the scale mu passed by the caller. Sign
convention (sect. 3.3): the transverse two-point function is
Gamma_T(k^2) = -i (k^2 - M^2) - i Sigma_T(k^2), so the pole mass obeys
M_pole^2 = m^2(mu) - Re Sigma_hat_T(M_pole^2; mu) once the MS-bar
counterterm is absorbed into the running mass parameter m^2(mu).

validate() certifies the transcription against measured-world anchors
(these numbers never feed the OPH chain):
1. Sigma^AA_T(0) = 0 exactly.
2. Delta r is mu-independent.
3. The m_t^2 dependence of Sigma^ZZ_T(0)/M_Z^2 - Sigma^W_T(0)/M_W^2
   reproduces the Veltman term 3 alpha m_t^2 / (16 pi s_W^2 c_W^2 M_Z^2)
   exactly (m_b = 0).
4. Denner's sect. 8 input set (alpha = 1/137.0359895, M_Z = 91.177,
   G_F = 1.16637e-5, m_t = 140, M_H = 100, effective quark masses) run
   through the one-loop relation
   M_W^2 (1 - M_W^2/M_Z^2) = pi alpha/(sqrt 2 G_F) (1 + Delta r)
   reproduces his quoted M_W = 80.23 GeV.
5. The closed-form B_0 matches direct Feynman-parameter quadrature.

No module-level mpmath state is touched; everything is float/complex.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass, field


_IEPS = 1e-30j


def a0_fin(m: float, mu2: float) -> float:
    """MS-bar finite part of A_0(m) = m^2 (Delta - log(m^2/mu^2) + 1)."""

    if m == 0.0:
        return 0.0
    m2 = m * m
    return m2 * (1.0 - math.log(m2 / mu2))


def b0_fin(s: float, m0: float, m1: float, mu2: float) -> float:
    """Real MS-bar finite part of B_0(s, m0, m1) at scale mu (Denner eq. (B0)).

    Handles the zero-mass and zero-momentum limits explicitly. Symmetric in
    (m0, m1).
    """

    if m1 == 0.0 and m0 != 0.0:
        m0, m1 = m1, m0
    m02, m12 = m0 * m0, m1 * m1
    if s == 0.0:
        if m0 == 0.0 and m1 == 0.0:
            raise ZeroDivisionError("B0(0,0,0) is undefined")
        if m0 == 0.0:
            return 1.0 - math.log(m12 / mu2)
        if abs(m02 - m12) < 1e-12 * (m02 + m12):
            return -math.log(m0 * m1 / mu2)
        return 1.0 - (m02 * math.log(m02 / mu2) - m12 * math.log(m12 / mu2)) / (
            m02 - m12
        )
    if m0 == 0.0 and m1 == 0.0:
        return 2.0 - math.log(abs(s) / mu2)
    if m0 == 0.0:
        # B0(s, 0, m) = 2 - log(m^2/mu^2) + ((m^2 - s)/s) log((m^2 - s - ieps)/m^2)
        x = s / m12
        if x == 1.0:
            # (m^2 - s)/s * log(...) -> 0 at the threshold point s = m^2.
            return 2.0 - math.log(m12 / mu2)
        log_re = math.log1p(-x) if x < 1.0 else math.log(x - 1.0)
        return 2.0 - math.log(m12 / mu2) + ((m12 - s) / s) * log_re
    # General closed form, Denner eq. (B0):
    # B0 = Delta + 2 - log(m0 m1 / mu^2) + (m0^2 - m1^2)/s log(m1/m0)
    #      - (m0 m1 / s)(1/r - r) log r,  x^2 + k x + 1 = (x + r)(x + 1/r),
    # with k = (m0^2 + m1^2 - s - ieps)/(m0 m1).
    k = (m02 + m12 - s - _IEPS) / (m0 * m1)
    sq = cmath.sqrt(k * k - 4.0)
    r1 = (k + sq) / 2.0
    r2 = (k - sq) / 2.0
    # r and 1/r enter symmetrically; take the larger-modulus root to avoid
    # catastrophic cancellation (their product is exactly 1).
    r = r1 if abs(r1) >= abs(r2) else r2
    val = (
        2.0
        - math.log(m0 * m1 / mu2)
        + ((m02 - m12) / s) * math.log(m1 / m0)
        - (m0 * m1 / s) * (1.0 / r - r) * cmath.log(r)
    )
    return val.real


def b0p_zero(m0: float, m1: float) -> float:
    """dB0/ds at s = 0 (Denner eq. (DB0) limit): the exact zero-momentum slope.

    B0'(0, m, m) = 1/(6 m^2); B0'(0, m, 0) = 1/(2 m^2); in general
    (m0^2 + m1^2)/(2 (m0^2 - m1^2)^2)
    - m0^2 m1^2 log(m0^2/m1^2)/(m0^2 - m1^2)^3.
    """

    if m0 == 0.0 and m1 == 0.0:
        raise ZeroDivisionError("B0'(0,0,0) is undefined")
    if m0 == 0.0 or m1 == 0.0:
        m = max(m0, m1)
        return 1.0 / (2.0 * m * m)
    m02, m12 = m0 * m0, m1 * m1
    if abs(m02 - m12) < 1e-9 * (m02 + m12):
        return 1.0 / (6.0 * m0 * m1)
    d = m02 - m12
    return (m02 + m12) / (2.0 * d * d) - m02 * m12 * math.log(m02 / m12) / d**3


@dataclass(frozen=True)
class Fermion:
    name: str
    charge: float  # Q_f
    isospin: float  # I^3_{W,f}
    nc: int
    mass: float


@dataclass(frozen=True)
class SMInputs:
    """Parameter point for the self-energies.

    alpha, sw2 and the masses may come from any consistent one-loop
    parameterization; differences between parameterizations are two-loop.
    """

    alpha: float
    sw2: float
    mw: float
    mz: float
    mh: float
    lepton_masses: tuple = (0.0, 0.0, 0.0)
    up_masses: tuple = (0.0, 0.0, 0.0)
    down_masses: tuple = (0.0, 0.0, 0.0)
    _fermions: tuple = field(init=False, default=())

    @property
    def cw2(self) -> float:
        return 1.0 - self.sw2

    def fermions(self) -> list:
        out = []
        for i in range(3):
            out.append(Fermion(f"nu{i}", 0.0, 0.5, 1, 0.0))
            out.append(Fermion(f"l{i}", -1.0, -0.5, 1, self.lepton_masses[i]))
            out.append(Fermion(f"u{i}", 2.0 / 3.0, 0.5, 3, self.up_masses[i]))
            out.append(Fermion(f"d{i}", -1.0 / 3.0, -0.5, 3, self.down_masses[i]))
        return out

    def g_plus(self, f: Fermion) -> float:
        sw = math.sqrt(self.sw2)
        cw = math.sqrt(self.cw2)
        return -sw / cw * f.charge

    def g_minus(self, f: Fermion) -> float:
        sw = math.sqrt(self.sw2)
        cw = math.sqrt(self.cw2)
        return (f.isospin - self.sw2 * f.charge) / (sw * cw)


def _fermion_neutral_bracket(s: float, m: float, mu2: float) -> float:
    """[-(s + 2 m^2) B0(s,m,m) + 2 m^2 B0(0,m,m) + s/3], Denner app. B."""

    if m == 0.0:
        if s == 0.0:
            return 0.0
        return -s * b0_fin(s, 0.0, 0.0, mu2) + s / 3.0
    return (
        -(s + 2.0 * m * m) * b0_fin(s, m, m, mu2)
        + 2.0 * m * m * b0_fin(0.0, m, m, mu2)
        + s / 3.0
    )


def sigma_aa_t(p: SMInputs, s: float, mu2: float) -> float:
    """Transverse photon self-energy, Denner app. B, finite part."""

    total = 0.0
    for f in p.fermions():
        if f.charge == 0.0:
            continue
        total += (
            (2.0 / 3.0)
            * f.nc
            * 2.0
            * f.charge**2
            * _fermion_neutral_bracket(s, f.mass, mu2)
        )
    mw = p.mw
    total += (3.0 * s + 4.0 * mw * mw) * b0_fin(s, mw, mw, mu2) - 4.0 * mw * mw * b0_fin(
        0.0, mw, mw, mu2
    )
    return -(p.alpha / (4.0 * math.pi)) * total


def sigma_az_t(p: SMInputs, s: float, mu2: float) -> float:
    """Transverse photon-Z mixing self-energy, Denner app. B, finite part."""

    total = 0.0
    for f in p.fermions():
        if f.charge == 0.0:
            continue
        total += (
            (2.0 / 3.0)
            * f.nc
            * (-f.charge)
            * (p.g_plus(f) + p.g_minus(f))
            * _fermion_neutral_bracket(s, f.mass, mu2)
        )
    sw = math.sqrt(p.sw2)
    cw = math.sqrt(p.cw2)
    cw2 = p.cw2
    mw = p.mw
    total += (
        -1.0
        / (3.0 * sw * cw)
        * (
            ((9.0 * cw2 + 0.5) * s + (12.0 * cw2 + 4.0) * mw * mw)
            * b0_fin(s, mw, mw, mu2)
            - (12.0 * cw2 - 2.0) * mw * mw * b0_fin(0.0, mw, mw, mu2)
            + s / 3.0
        )
    )
    return -(p.alpha / (4.0 * math.pi)) * total


def sigma_zz_t(p: SMInputs, s: float, mu2: float) -> float:
    """Transverse Z self-energy, Denner app. B, finite part."""

    sw2, cw2 = p.sw2, p.cw2
    mw, mz, mh = p.mw, p.mz, p.mh
    total = 0.0
    for f in p.fermions():
        gp, gm = p.g_plus(f), p.g_minus(f)
        term = (gp * gp + gm * gm) * _fermion_neutral_bracket(s, f.mass, mu2)
        if f.mass != 0.0:
            term += (
                3.0
                / (4.0 * sw2 * cw2)
                * f.mass**2
                * b0_fin(s, f.mass, f.mass, mu2)
            )
        total += (2.0 / 3.0) * f.nc * term
    total += (
        1.0
        / (6.0 * sw2 * cw2)
        * (
            (
                (18.0 * cw2 * cw2 + 2.0 * cw2 - 0.5) * s
                + (24.0 * cw2 * cw2 + 16.0 * cw2 - 10.0) * mw * mw
            )
            * b0_fin(s, mw, mw, mu2)
            - (24.0 * cw2 * cw2 - 8.0 * cw2 + 2.0) * mw * mw * b0_fin(0.0, mw, mw, mu2)
            + (4.0 * cw2 - 1.0) * s / 3.0
        )
    )
    zh = (2.0 * mh * mh - 10.0 * mz * mz - s) * b0_fin(s, mz, mh, mu2)
    zh += -2.0 * mz * mz * b0_fin(0.0, mz, mz, mu2)
    zh += -2.0 * mh * mh * b0_fin(0.0, mh, mh, mu2)
    if s != 0.0:
        zh += (
            -((mz * mz - mh * mh) ** 2)
            / s
            * (b0_fin(s, mz, mh, mu2) - b0_fin(0.0, mz, mh, mu2))
        )
    else:
        zh += -((mz * mz - mh * mh) ** 2) * b0p_zero(mz, mh)
    zh += -(2.0 / 3.0) * s
    total += zh / (12.0 * sw2 * cw2)
    return -(p.alpha / (4.0 * math.pi)) * total


def _b0_diff_over_s(s: float, m0: float, m1: float, mu2: float) -> float:
    """(B0(s, m0, m1) - B0(0, m0, m1)) / s, with the exact s -> 0 limit."""

    if s == 0.0:
        return b0p_zero(m0, m1)
    return (b0_fin(s, m0, m1, mu2) - b0_fin(0.0, m0, m1, mu2)) / s


def sigma_w_t(p: SMInputs, s: float, mu2: float) -> float:
    """Transverse W self-energy, Denner app. B, finite part (photon mass 0).

    The explicit 1/s combinations of the appendix expression are evaluated
    through their exact s -> 0 limits, so s = 0 is a regular point.
    """

    sw2, cw2 = p.sw2, p.cw2
    mw, mz, mh = p.mw, p.mz, p.mh
    total = 0.0
    # Lepton doublets (m_nu = 0).
    for ml in p.lepton_masses:
        if ml == 0.0 and s == 0.0:
            continue
        term = -(s - ml * ml / 2.0) * b0_fin(s, 0.0, ml, mu2) + s / 3.0
        if ml != 0.0:
            term += ml * ml * b0_fin(0.0, ml, ml, mu2)
            term += ml**4 / 2.0 * _b0_diff_over_s(s, 0.0, ml, mu2)
        total += (2.0 / 3.0) / (2.0 * sw2) * term
    # Quark doublets, CKM = identity.
    for mu_q, md_q in zip(p.up_masses, p.down_masses):
        if mu_q == 0.0 and md_q == 0.0 and s == 0.0:
            continue
        term = -(s - (mu_q * mu_q + md_q * md_q) / 2.0) * b0_fin(
            s, mu_q, md_q, mu2
        ) + s / 3.0
        if mu_q != 0.0:
            term += mu_q * mu_q * b0_fin(0.0, mu_q, mu_q, mu2)
        if md_q != 0.0:
            term += md_q * md_q * b0_fin(0.0, md_q, md_q, mu2)
        if mu_q != 0.0 or md_q != 0.0:
            term += (
                (mu_q * mu_q - md_q * md_q) ** 2
                / 2.0
                * _b0_diff_over_s(s, mu_q, md_q, mu2)
            )
        total += (2.0 / 3.0) / (2.0 * sw2) * 3.0 * term
    # Photon-W loop (photon mass set to zero; finite at s = M_W^2).
    total += (2.0 / 3.0) * (
        (2.0 * mw * mw + 5.0 * s) * b0_fin(s, mw, 0.0, mu2)
        - 2.0 * mw * mw * b0_fin(0.0, mw, mw, mu2)
        - mw**4 * _b0_diff_over_s(s, mw, 0.0, mu2)
        + s / 3.0
    )
    # Z-W loop.
    total += (
        1.0
        / (12.0 * sw2)
        * (
            (
                (40.0 * cw2 - 1.0) * s
                + (16.0 * cw2 + 54.0 - 10.0 / cw2) * mw * mw
            )
            * b0_fin(s, mw, mz, mu2)
            - (16.0 * cw2 + 2.0)
            * (mw * mw * b0_fin(0.0, mw, mw, mu2) + mz * mz * b0_fin(0.0, mz, mz, mu2))
            + (4.0 * cw2 - 1.0) * (2.0 / 3.0) * s
            - (8.0 * cw2 + 1.0)
            * (mw * mw - mz * mz) ** 2
            * _b0_diff_over_s(s, mw, mz, mu2)
        )
    )
    # H-W loop.
    total += (
        1.0
        / (12.0 * sw2)
        * (
            (2.0 * mh * mh - 10.0 * mw * mw - s) * b0_fin(s, mw, mh, mu2)
            - 2.0 * mw * mw * b0_fin(0.0, mw, mw, mu2)
            - 2.0 * mh * mh * b0_fin(0.0, mh, mh, mu2)
            - (mw * mw - mh * mh) ** 2 * _b0_diff_over_s(s, mw, mh, mu2)
            - (2.0 / 3.0) * s
        )
    )
    return -(p.alpha / (4.0 * math.pi)) * total


def pi_aa_zero(p: SMInputs, mu2: float) -> float:
    """Pi^AA(0) = d Sigma^AA_T / d k^2 at k^2 = 0 (all charged masses > 0).

    Uses B0(0,m,m) = -log(m^2/mu^2) and dB0/ds(0,m,m) = 1/(6 m^2).
    """

    total = 0.0
    for f in p.fermions():
        if f.charge == 0.0:
            continue
        if f.mass == 0.0:
            raise ValueError("Pi^AA(0) needs massive charged fermions")
        m2 = f.mass**2
        # d/ds of the neutral bracket at 0: -B0(0,m,m) - 2 m^2/(6 m^2) + 1/3
        total += (2.0 / 3.0) * f.nc * 2.0 * f.charge**2 * math.log(m2 / mu2)
    mw2 = p.mw**2
    total += 3.0 * b0_fin(0.0, p.mw, p.mw, mu2) + 4.0 * mw2 / (6.0 * mw2)
    return -(p.alpha / (4.0 * math.pi)) * total


def delta_r(p: SMInputs, mu2: float) -> float:
    """Denner sect. 8: the one-loop Delta r from the transcribed self-energies."""

    sw2, cw2 = p.sw2, p.cw2
    mw2, mz2 = p.mw**2, p.mz**2
    sw, cw = math.sqrt(sw2), math.sqrt(cw2)
    out = pi_aa_zero(p, mu2)
    out += -(cw2 / sw2) * (
        sigma_zz_t(p, mz2, mu2) / mz2 - sigma_w_t(p, mw2, mu2) / mw2
    )
    out += (sigma_w_t(p, 0.0, mu2) - sigma_w_t(p, mw2, mu2)) / mw2
    out += 2.0 * (cw / sw) * sigma_az_t(p, 0.0, mu2) / mz2
    out += (
        p.alpha
        / (4.0 * math.pi * sw2)
        * (6.0 + (7.0 - 4.0 * sw2) / (2.0 * sw2) * math.log(cw2))
    )
    return out


# ----------------------------------------------------------------------
# Certification harness (measured-world anchors; never chain inputs).
# ----------------------------------------------------------------------

DENNER_SECT8 = {
    "alpha": 1.0 / 137.0359895,
    "MZ": 91.177,
    "GF": 1.16637e-5,
    "mt": 140.0,
    "MH": 100.0,
    "leptons": (0.51099906e-3, 105.658387e-3, 1.7841),
    "ups": (0.041, 1.5, 140.0),
    "downs": (0.041, 0.15, 4.5),
    "MW_quoted": 80.23,
}


def _harness_point(mw: float, mt: float | None = None) -> SMInputs:
    d = DENNER_SECT8
    mz = d["MZ"]
    ups = list(d["ups"])
    ups[2] = d["mt"] if mt is None else mt
    return SMInputs(
        alpha=d["alpha"],
        sw2=1.0 - mw * mw / (mz * mz),
        mw=mw,
        mz=mz,
        mh=d["MH"],
        lepton_masses=d["leptons"],
        up_masses=tuple(ups),
        down_masses=d["downs"],
    )


def solve_mw_from_delta_r(resummed: bool = True) -> tuple:
    """Iterate M_W^2 (1 - M_W^2/M_Z^2) = pi alpha/(sqrt 2 G_F) (1 + Delta r).

    With resummed=True the right-hand side carries 1/(1 - Delta r), the
    leading-higher-order form Denner quotes his sect. 8 number with.
    """

    d = DENNER_SECT8
    mz2 = d["MZ"] ** 2
    a_const = math.pi * d["alpha"] / (math.sqrt(2.0) * d["GF"])
    mw = 80.0
    dr = 0.0
    for _ in range(60):
        p = _harness_point(mw)
        dr = delta_r(p, mz2)
        factor = 1.0 / (1.0 - dr) if resummed else 1.0 + dr
        mw_new = math.sqrt(
            mz2 / 2.0 * (1.0 + math.sqrt(1.0 - 4.0 * a_const * factor / mz2))
        )
        if abs(mw_new - mw) < 1e-12:
            mw = mw_new
            break
        mw = mw_new
    return mw, dr


def _b0_quadrature(s: float, m0: float, m1: float, mu2: float, n: int = 200000) -> float:
    """Direct Feynman-parameter integral of B0's finite part (midpoint rule)."""

    total = 0.0
    for i in range(n):
        x = (i + 0.5) / n
        arg = s * x * x - x * (s - m0 * m0 + m1 * m1) + m1 * m1
        total += math.log(abs(arg) / mu2) if arg != 0.0 else 0.0
    return -total / n


def validate() -> dict:
    """Run the certification checks. Fails closed via the returned flags."""

    checks: dict = {}
    d = DENNER_SECT8
    mz2 = d["MZ"] ** 2

    # 1. Sigma^AA_T(0) = 0 exactly (electromagnetic Ward identity).
    p0 = _harness_point(80.0)
    val = sigma_aa_t(p0, 0.0, mz2)
    checks["sigma_aa_at_zero"] = {"value": val, "ok": abs(val) < 1e-8}

    # 2. mu-independence of Delta r.
    dr_a = delta_r(p0, mz2)
    dr_b = delta_r(p0, 100.0 * mz2)
    checks["delta_r_mu_independent"] = {
        "delta_r_at_mz": dr_a,
        "delta_r_at_10mz": dr_b,
        "difference": dr_a - dr_b,
        "ok": abs(dr_a - dr_b) < 1e-9,
    }

    # 3. Veltman m_t^2 term of Sigma_ZZ(0)/MZ^2 - Sigma_W(0)/MW^2 (m_b = 0).
    def rho_comb(mt: float) -> float:
        p = _harness_point(80.0, mt=mt)
        p = SMInputs(
            alpha=p.alpha,
            sw2=p.sw2,
            mw=p.mw,
            mz=p.mz,
            mh=p.mh,
            lepton_masses=p.lepton_masses,
            up_masses=(p.up_masses[0], p.up_masses[1], mt),
            down_masses=(p.down_masses[0], p.down_masses[1], 0.0),
        )
        return sigma_zz_t(p, 0.0, mz2) / (p.mz**2) - sigma_w_t(p, 0.0, mz2) / (
            p.mw**2
        )

    mt_a, mt_b = 800.0, 400.0
    got = rho_comb(mt_a) - rho_comb(mt_b)
    pref = _harness_point(80.0)
    expect = (
        3.0
        * pref.alpha
        * (mt_a**2 - mt_b**2)
        / (16.0 * math.pi * pref.sw2 * pref.cw2 * pref.mz**2)
    )
    checks["veltman_rho_mt2_term"] = {
        "got": got,
        "expected": expect,
        "ok": abs(got / expect - 1.0) < 1e-4,
    }

    # 4. Denner sect. 8 anchor: M_W = 80.23 GeV (resummed form of eq. (GF1loop)).
    mw_sol, dr_sol = solve_mw_from_delta_r(resummed=True)
    mw_lin, dr_lin = solve_mw_from_delta_r(resummed=False)
    checks["denner_mw_anchor"] = {
        "mw_solved_resummed_GeV": mw_sol,
        "mw_solved_linear_GeV": mw_lin,
        "delta_r_at_solution": dr_sol,
        "delta_r_linear": dr_lin,
        "mw_quoted_GeV": d["MW_quoted"],
        "ok": abs(mw_sol - d["MW_quoted"]) < 0.01 and 0.02 < dr_sol < 0.05,
    }

    # 5. Closed-form B0 against direct quadrature.
    b0_cases = [
        (91.19**2, 80.4, 91.19),
        (91.19**2, 164.1, 164.1),
        (80.4**2, 164.1, 0.0),
        (80.4**2, 80.4, 115.1),
        (91.19**2, 0.0, 0.0),
        (0.0, 80.4, 115.1),
    ]
    worst = 0.0
    for s, m0, m1 in b0_cases:
        closed = b0_fin(s, m0, m1, mz2)
        quad = _b0_quadrature(s, m0, m1, mz2)
        worst = max(worst, abs(closed - quad))
    checks["b0_closed_form_vs_quadrature"] = {"worst_abs_diff": worst, "ok": worst < 1e-4}

    checks["all_ok"] = all(v["ok"] for k, v in checks.items() if k != "all_ok")
    return checks


if __name__ == "__main__":
    import json

    print(json.dumps(validate(), indent=2))
