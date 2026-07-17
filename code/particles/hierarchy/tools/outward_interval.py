#!/usr/bin/env python3
"""Directed-rounding interval arithmetic backend for the R_U hierarchy log.

Backend policy (issue #331):

* Number format: IEEE-754 binary64 (Python float).
* Primitive operations: machine +, -, *, / and math.sqrt evaluate in
  round-to-nearest and are correctly rounded per IEEE-754. Every primitive
  result is stepped one ulp outward on each interval bound with
  math.nextafter. This makes each interval operation a sound enclosure of
  the exact real operation without any assumption beyond IEEE-754 correct
  rounding of +, -, *, /, sqrt.
* Transcendentals: exp and log are implemented inside this module and do
  not call libm exp/log. exp uses the reduction x = k*ln2 + r with
  |r| <= 0.36, a degree-20 Taylor polynomial evaluated in outward interval
  arithmetic, an explicit symmetric remainder pad, and an exact power-of-two
  rescale via math.ldexp (padded one ulp to cover subnormal rounding).
  log uses the exact math.frexp reduction x = m * 2^e with
  m in [sqrt(1/2), sqrt(2)), the atanh series
  log m = 2*atanh((m-1)/(m+1)) with |u| <= 0.1716 truncated at n = 14,
  an explicit symmetric remainder pad, and e*ln2 added in interval
  arithmetic.
* Constants: pi and ln2 enter as high-precision decimal strings, are
  bracketed by exact rational (fractions.Fraction) comparison against the
  two nearest binary64 values, and are padded one ulp outward on each side
  to cover the decimal truncation of the strings.
* Series coefficients 1/n! and 1/(2n+1) are bracketed from exact rationals
  by the same Fraction comparison, with no truncation pad needed.
* Deep underflow: for arguments x <= -710, exp returns the enclosure
  [0, 1e-308], valid because exp(-710) < 4.5e-309 < 1e-308.
* Serialization: every interval bound is serialized as float.hex() plus its
  repr decimal, so a log entry pins the exact binary64 bit pattern.

Assumption set: IEEE-754 correct rounding of +, -, *, /, sqrt on binary64;
exactness of math.nextafter, math.ldexp on normal outputs, math.frexp; and
correctness of the recorded decimal strings for pi and ln2. No libm exp/log
accuracy assumption is used.
"""

from __future__ import annotations

import math
from fractions import Fraction

BACKEND_ID = "oph-outward-float64-directed-rounding"
BACKEND_VERSION = "1.0.0"

_INF = math.inf


def _down(x: float) -> float:
    return math.nextafter(x, -_INF)


def _up(x: float) -> float:
    return math.nextafter(x, _INF)


class IV:
    """Closed interval [lo, hi] of binary64 values."""

    __slots__ = ("lo", "hi")

    def __init__(self, lo: float, hi: float):
        if not (math.isfinite(lo) and math.isfinite(hi) and lo <= hi):
            raise ValueError(f"invalid interval [{lo!r}, {hi!r}]")
        self.lo = lo
        self.hi = hi

    def __repr__(self) -> str:
        return f"IV({self.lo!r}, {self.hi!r})"

    def __add__(self, other: "IV") -> "IV":
        if not isinstance(other, IV):
            return NotImplemented
        return IV(_down(self.lo + other.lo), _up(self.hi + other.hi))

    def __sub__(self, other: "IV") -> "IV":
        if not isinstance(other, IV):
            return NotImplemented
        return IV(_down(self.lo - other.hi), _up(self.hi - other.lo))

    def __neg__(self) -> "IV":
        return IV(-self.hi, -self.lo)

    def __mul__(self, other: "IV") -> "IV":
        if not isinstance(other, IV):
            return NotImplemented
        p1 = self.lo * other.lo
        p2 = self.lo * other.hi
        p3 = self.hi * other.lo
        p4 = self.hi * other.hi
        return IV(_down(min(p1, p2, p3, p4)), _up(max(p1, p2, p3, p4)))

    def __truediv__(self, other: "IV") -> "IV":
        if not isinstance(other, IV):
            return NotImplemented
        if not (other.lo > 0.0 or other.hi < 0.0):
            raise ZeroDivisionError(f"denominator {other!r} contains zero")
        q1 = self.lo / other.lo
        q2 = self.lo / other.hi
        q3 = self.hi / other.lo
        q4 = self.hi / other.hi
        return IV(_down(min(q1, q2, q3, q4)), _up(max(q1, q2, q3, q4)))

    def contains_zero(self) -> bool:
        return self.lo <= 0.0 <= self.hi


ZERO = IV(0.0, 0.0)
ONE = IV(1.0, 1.0)
TWO = IV(2.0, 2.0)


def iv_from_int(n: int) -> IV:
    if abs(n) > 2 ** 53:
        raise ValueError("integer too large for exact binary64")
    f = float(n)
    return IV(f, f)


def bracket_fraction(q: Fraction) -> IV:
    """Tightest binary64 bracket of an exact rational."""
    f = float(q)
    qf = Fraction(f)
    if qf == q:
        return IV(f, f)
    if qf < q:
        return IV(f, _up(f))
    return IV(_down(f), f)


def bracket_exact_decimal(s: str) -> IV:
    """Bracket of the exact value named by a decimal string."""
    return bracket_fraction(Fraction(s))


def bracket_truncated_decimal(s: str, min_digits: int = 40) -> IV:
    """Bracket of a real constant recorded as a truncated decimal string.

    The string must carry at least min_digits fractional digits; the bracket
    of the string value is padded one ulp outward on each side, which covers
    a truncation error below 10**-min_digits.
    """
    frac_digits = len(s.split(".", 1)[1])
    if frac_digits < min_digits:
        raise ValueError(f"constant string {s!r} carries too few digits")
    b = bracket_exact_decimal(s)
    return IV(_down(b.lo), _up(b.hi))


PI_STRING = "3.1415926535897932384626433832795028841971693993751"
LN2_STRING = "0.6931471805599453094172321214581765680755001343602552"

PI = bracket_truncated_decimal(PI_STRING)
LN2 = bracket_truncated_decimal(LN2_STRING)

_EXP_TERMS = 20
_EXP_REMAINDER = 1e-28  # >= 0.36^21/21! * 1/(1 - 0.36/22)
_EXP_REM_IV = IV(-_EXP_REMAINDER, _EXP_REMAINDER)
_EXP_UNDERFLOW = -710.0
_EXP_TINY = 1e-308  # exp(-710) < 4.5e-309 < 1e-308

_LOG_TERMS = 14
_LOG_REMAINDER = 1e-25  # >= 0.1717^31 / (31 * (1 - 0.1717^2))
_LOG_REM_IV = IV(-_LOG_REMAINDER, _LOG_REMAINDER)
_SQRT_HALF = 0.7071067811865476

_INV_FACT = [bracket_fraction(Fraction(1, math.factorial(n))) for n in range(_EXP_TERMS + 1)]
_INV_ODD = [bracket_fraction(Fraction(1, 2 * n + 1)) for n in range(_LOG_TERMS + 1)]

_LN2_APPROX = 0.6931471805599453


def _exp_point(x: float) -> IV:
    """Enclosure of exp(x) for a single binary64 x with x < 700."""
    if x <= _EXP_UNDERFLOW:
        return IV(0.0, _EXP_TINY)
    if x >= 700.0:
        raise OverflowError("exp argument out of the supported range")
    k = round(x / _LN2_APPROX)
    r = IV(x, x) - (LN2 * iv_from_int(k))
    if not (-0.36 < r.lo and r.hi < 0.36):
        raise AssertionError("exp argument reduction out of range")
    p = _INV_FACT[_EXP_TERMS]
    for n in range(_EXP_TERMS - 1, -1, -1):
        p = p * r + _INV_FACT[n]
    p = p + _EXP_REM_IV
    lo = _down(math.ldexp(p.lo, k))
    hi = _up(math.ldexp(p.hi, k))
    if lo < 0.0:
        lo = 0.0
    return IV(lo, hi)


def iv_exp(x: IV) -> IV:
    """Enclosure of exp over an interval; exp is monotone increasing."""
    lo = 0.0 if x.lo <= _EXP_UNDERFLOW else _exp_point(x.lo).lo
    hi = _EXP_TINY if x.hi <= _EXP_UNDERFLOW else _exp_point(x.hi).hi
    return IV(lo, hi)


def _log_point(x: float) -> IV:
    """Enclosure of log(x) for a single binary64 x > 0."""
    if not (x > 0.0 and math.isfinite(x)):
        raise ValueError("log argument must be positive and finite")
    m, e = math.frexp(x)
    if m < _SQRT_HALF:
        m *= 2.0  # exact
        e -= 1
    mi = IV(m, m)
    u = (mi - ONE) / (mi + ONE)
    if not (-0.1716 < u.lo and u.hi < 0.1716):
        raise AssertionError("log argument reduction out of range")
    u2 = u * u
    t = _INV_ODD[_LOG_TERMS]
    for n in range(_LOG_TERMS - 1, -1, -1):
        t = t * u2 + _INV_ODD[n]
    s = (u * t) + _LOG_REM_IV
    return (TWO * s) + (iv_from_int(e) * LN2)


def iv_log(x: IV) -> IV:
    """Enclosure of log over an interval; log is monotone increasing."""
    if x.lo <= 0.0:
        raise ValueError("log interval must be strictly positive")
    return IV(_log_point(x.lo).lo, _log_point(x.hi).hi)


def iv_sqrt(x: IV) -> IV:
    """Enclosure of sqrt; math.sqrt is correctly rounded per IEEE-754."""
    if x.lo < 0.0:
        raise ValueError("sqrt interval must be nonnegative")
    lo = _down(math.sqrt(x.lo))
    if lo < 0.0:
        lo = 0.0
    return IV(lo, _up(math.sqrt(x.hi)))


def iv_to_json(x: IV) -> dict:
    return {
        "lo_hex": x.lo.hex(),
        "hi_hex": x.hi.hex(),
        "lo": repr(x.lo),
        "hi": repr(x.hi),
    }


def backend_declaration() -> dict:
    """Machine-readable backend, rounding, precision, and format policy."""
    return {
        "backend_id": BACKEND_ID,
        "backend_version": BACKEND_VERSION,
        "number_format": "IEEE-754 binary64",
        "rounding_mode": (
            "hardware round-to-nearest for the correctly rounded primitives "
            "+, -, *, /, sqrt, followed by one math.nextafter step outward "
            "on each interval bound after every primitive"
        ),
        "transcendental_policy": {
            "exp": (
                "in-module: x = k*ln2 + r with |r| <= 0.36, degree-20 Taylor "
                "polynomial in outward interval arithmetic, symmetric "
                "remainder pad 1e-28, exact ldexp rescale padded one ulp"
            ),
            "log": (
                "in-module: exact frexp reduction to m in [sqrt(1/2), sqrt(2)), "
                "atanh series 2*atanh((m-1)/(m+1)) truncated at n=14 in outward "
                "interval arithmetic, symmetric remainder pad 1e-25, plus "
                "e*ln2 in interval arithmetic"
            ),
            "deep_underflow": (
                "exp(x) for x <= -710 returns [0, 1e-308]; "
                "exp(-710) < 4.5e-309 < 1e-308"
            ),
            "libm_assumption": (
                "none for exp/log; libm exp/log are not called on the "
                "certificate path"
            ),
        },
        "constant_policy": (
            "pi and ln2 enter as recorded decimal strings, bracketed against "
            "binary64 by exact rational comparison and padded one ulp outward "
            "per side for decimal truncation; series coefficients 1/n! and "
            "1/(2n+1) are bracketed from exact rationals"
        ),
        "constants": {
            "pi": {"decimal_string": PI_STRING, "bracket": iv_to_json(PI)},
            "ln2": {"decimal_string": LN2_STRING, "bracket": iv_to_json(LN2)},
        },
        "serialization_format": (
            "JSON; every interval bound carries float.hex() plus repr decimal, "
            "pinning the exact binary64 bit pattern"
        ),
        "assumption_set": [
            "IEEE-754 correct rounding of +, -, *, /, sqrt on binary64",
            "exactness of math.nextafter, math.frexp, and math.ldexp on normal outputs",
            "correctness of the recorded decimal strings for pi and ln2",
        ],
    }
