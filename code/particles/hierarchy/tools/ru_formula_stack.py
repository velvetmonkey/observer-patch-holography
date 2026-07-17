#!/usr/bin/env python3
"""R_U formula stack evaluated in the directed-rounding interval backend.

This module re-evaluates the full R_U hierarchy formula stack of
computations/hierarchy_recompute.py in outward-rounded binary64 interval
arithmetic (tools/outward_interval.py), with forward-mode interval
automatic differentiation for the derivative enclosure used by the
Krawczyk operator

    K(X) = c - Y*Phi(c) + (1 - Y*Phi'(X))*(X - c).

The stack consumes only structural inputs: the forward pixel constant
P_fwd as a decimal string, the representation cutoffs N2, N3, the one-loop
coefficients b1 = 33/5, b2 = 1, b3 = -3, the weight 3/5, the fixed-point
seed 0.3714 with its iteration count, and the enclosure interval I_U with
the center and preconditioner choices. No measured endpoint constant
appears anywhere in this module.

Formula stack, matching hierarchy_recompute.py:

    MU  = exp(-2*pi) * P^(1/6)
    v   = P^(-1/2) * exp(-2*pi/(4*a))
    alpha(mu, b) = 1 / (1/a + b/(2*pi) * log(MU/mu))
    fmu(mu) = (v/2) * sqrt(4*pi*alpha(mu,b2) + 4*pi*(3/5)*alpha(mu,b1))
    mu  = fmu^(60)(v * 0.3714)
    t2  = 4*pi^2 * alpha(mu, b2);  t3 = 4*pi^2 * alpha(mu, b3)
    Phi = ell_su2(t2; N2) + ell_su3(t3; N3) - P/4

with the heat-kernel entropy sums

    ell_su2(t) = sum_n (n+1) e^{-t n(n+2)/4} log(n+1) / Z2
    ell_su3(t) = sum_{p,q} d_{pq} e^{-t C_{pq}} log(d_{pq}) / Z3,
    d_{pq} = (p+1)(q+1)(p+q+2)/2,  C_{pq} = (p^2+q^2+pq+3p+3q)/3.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction

from outward_interval import (
    IV,
    ONE,
    ZERO,
    TWO,
    PI,
    backend_declaration,
    bracket_exact_decimal,
    iv_exp,
    iv_from_int,
    iv_log,
    iv_sqrt,
    iv_to_json,
)

getcontext().prec = 90

STACK_ID = "oph-ru-formula-stack"
STACK_VERSION = "1.0.0"

TWO_PI = TWO * PI
FOUR_PI = iv_from_int(4) * PI
FOUR_PI2 = FOUR_PI * PI
NEG_TWO_PI = -TWO_PI


class AD:
    """Forward-mode pair (value interval, derivative interval) in one variable."""

    __slots__ = ("v", "d")

    def __init__(self, v: IV, d: IV):
        self.v = v
        self.d = d

    @staticmethod
    def _wrap(x):
        return x if isinstance(x, AD) else AD(x, ZERO)

    def __add__(self, other):
        o = AD._wrap(other)
        return AD(self.v + o.v, self.d + o.d)

    __radd__ = __add__

    def __sub__(self, other):
        o = AD._wrap(other)
        return AD(self.v - o.v, self.d - o.d)

    def __rsub__(self, other):
        o = AD._wrap(other)
        return AD(o.v - self.v, o.d - self.d)

    def __neg__(self):
        return AD(-self.v, -self.d)

    def __mul__(self, other):
        o = AD._wrap(other)
        return AD(self.v * o.v, self.d * o.v + self.v * o.d)

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = AD._wrap(other)
        return AD(self.v / o.v, (self.d * o.v - self.v * o.d) / (o.v * o.v))

    def __rtruediv__(self, other):
        return AD._wrap(other).__truediv__(self)


def x_exp(x):
    if isinstance(x, AD):
        e = iv_exp(x.v)
        return AD(e, e * x.d)
    return iv_exp(x)


def x_log(x):
    if isinstance(x, AD):
        return AD(iv_log(x.v), x.d / x.v)
    return iv_log(x)


def x_sqrt(x):
    if isinstance(x, AD):
        s = iv_sqrt(x.v)
        return AD(s, x.d / (TWO * s))
    return iv_sqrt(x)


DECLARED_INPUT_KEYS = (
    "P_fwd_decimal",
    "N2",
    "N3",
    "b1_fraction",
    "b2_fraction",
    "b3_fraction",
    "hypercharge_weight_fraction",
    "mu_seed_decimal",
    "mu_iterations",
    "I_U_lower_decimal",
    "I_U_upper_decimal",
    "center_c_hex",
    "krawczyk_Y_hex",
)

DEFAULT_DECLARED_INPUTS = {
    "P_fwd_decimal": "1.630968209403959324879279847782648941",
    "N2": 128,
    "N3": 64,
    "b1_fraction": "33/5",
    "b2_fraction": "1",
    "b3_fraction": "-3",
    "hypercharge_weight_fraction": "3/5",
    "mu_seed_decimal": "0.3714",
    "mu_iterations": 60,
    "I_U_lower_decimal": "0.041123336195630494",
    "I_U_upper_decimal": "0.041125336195630496",
    "center_c_hex": float("0.041124336195630495").hex(),
    "krawczyk_Y_hex": float("-0.09098746682540293").hex(),
}


class Inputs:
    """Structural inputs resolved to backend values."""

    def __init__(self, declared: dict):
        keys = tuple(sorted(declared.keys()))
        if keys != tuple(sorted(DECLARED_INPUT_KEYS)):
            raise ValueError(f"declared input keys {keys} do not match the structural allowlist")
        self.declared = dict(declared)
        self.P = bracket_exact_decimal(declared["P_fwd_decimal"])
        self.N2 = int(declared["N2"])
        self.N3 = int(declared["N3"])
        self.b1 = _bracket_fraction_string(declared["b1_fraction"])
        self.b2 = _bracket_fraction_string(declared["b2_fraction"])
        self.b3 = _bracket_fraction_string(declared["b3_fraction"])
        self.w_hyper = _bracket_fraction_string(declared["hypercharge_weight_fraction"])
        self.mu_seed = bracket_exact_decimal(declared["mu_seed_decimal"])
        self.mu_iterations = int(declared["mu_iterations"])
        # X is the outward binary64 bracket of the decimal I_U, so X contains I_U.
        self.X_lo = bracket_exact_decimal(declared["I_U_lower_decimal"]).lo
        self.X_hi = bracket_exact_decimal(declared["I_U_upper_decimal"]).hi
        self.c = float.fromhex(declared["center_c_hex"])
        self.Y = float.fromhex(declared["krawczyk_Y_hex"])
        if not (self.X_lo < self.c < self.X_hi):
            raise ValueError("center c must lie inside I_U")
        if not self.Y < 0.0:
            raise ValueError("preconditioner Y must be negative for this stack")


def _bracket_fraction_string(s: str) -> IV:
    from outward_interval import bracket_fraction

    return bracket_fraction(Fraction(s))


_LOG_DIM_CACHE: dict[float, IV] = {}


def _log_dim(d: float) -> IV:
    cached = _LOG_DIM_CACHE.get(d)
    if cached is None:
        cached = iv_log(IV(d, d))
        _LOG_DIM_CACHE[d] = cached
    return cached


def ell_su2(t, N2: int):
    Z = None
    S = None
    for n in range(N2 + 1):
        d = float(n + 1)  # exact
        casimir = float(n * (n + 2)) / 4.0  # exact: /4 is a power-of-two scale
        c_iv = IV(casimir, casimir)
        w = iv_from_int(n + 1) * x_exp(-(t * c_iv))
        term = w * _log_dim(d)
        if Z is None:
            Z, S = w, term
        else:
            Z, S = Z + w, S + term
    return S / Z, Z


def ell_su3(t, N3: int):
    Z = None
    S = None
    for p in range(N3 + 1):
        for q in range(N3 + 1):
            dim2 = (p + 1) * (q + 1) * (p + q + 2)  # 2*d, exact integer
            d = float(dim2) / 2.0  # exact: /2 is a power-of-two scale
            c_iv = iv_from_int(p * p + q * q + p * q + 3 * p + 3 * q) / iv_from_int(3)
            w = IV(d, d) * x_exp(-(t * c_iv))
            term = w * _log_dim(d)
            if Z is None:
                Z, S = w, term
            else:
                Z, S = Z + w, S + term
    return S / Z, Z


def evaluate_phi(inp: Inputs, a_iv: IV, with_derivative: bool):
    """Interval image (and derivative enclosure) of every named DAG node."""
    a = AD(a_iv, ONE) if with_derivative else a_iv
    nodes = {}
    nodes["a"] = a
    inv_a = ONE / a
    nodes["inv_a"] = inv_a
    log_P = x_log(inp.P)
    nodes["log_P"] = log_P
    p_sixth = x_exp(log_P / iv_from_int(6))
    nodes["P_pow_one_sixth"] = p_sixth
    MU = x_exp(NEG_TWO_PI) * p_sixth
    nodes["MU_over_E_star"] = MU
    v = x_exp(NEG_TWO_PI / (iv_from_int(4) * a)) / x_sqrt(inp.P)
    nodes["v_over_E_star"] = v

    def alpha(log_mu_ratio, b: IV):
        return ONE / (inv_a + (b * log_mu_ratio) / TWO_PI)

    def fmu(mu):
        log_ratio = x_log(MU / mu)
        a2 = alpha(log_ratio, inp.b2)
        a1 = alpha(log_ratio, inp.b1)
        return (v / TWO) * x_sqrt(FOUR_PI * a2 + FOUR_PI * (inp.w_hyper * a1))

    mu = v * inp.mu_seed
    nodes["mu_seed_scaled"] = mu
    mu_trace = [mu]
    for _ in range(inp.mu_iterations):
        mu = fmu(mu)
        mu_trace.append(mu)
    nodes["mu_final"] = mu
    log_ratio_final = x_log(MU / mu)
    nodes["log_MU_over_mu_final"] = log_ratio_final
    alpha1 = alpha(log_ratio_final, inp.b1)
    alpha2 = alpha(log_ratio_final, inp.b2)
    alpha3 = alpha(log_ratio_final, inp.b3)
    nodes["alpha_b1"] = alpha1
    nodes["alpha_b2"] = alpha2
    nodes["alpha_b3"] = alpha3
    t2 = FOUR_PI2 * alpha2
    t3 = FOUR_PI2 * alpha3
    nodes["t2"] = t2
    nodes["t3"] = t3
    ell2, Z2 = ell_su2(t2, inp.N2)
    nodes["Z_su2"] = Z2
    nodes["ell_su2"] = ell2
    ell3, Z3 = ell_su3(t3, inp.N3)
    nodes["Z_su3"] = Z3
    nodes["ell_su3"] = ell3
    p_over_4 = inp.P / iv_from_int(4)
    nodes["P_over_4"] = p_over_4
    phi = (ell2 + ell3) - p_over_4
    nodes["Phi"] = phi
    return nodes, mu_trace


def _node_json(x) -> dict:
    if isinstance(x, AD):
        return {"value": iv_to_json(x.v), "derivative": iv_to_json(x.d)}
    return iv_to_json(x)


def _context_json(nodes: dict, mu_trace: list) -> dict:
    return {
        "nodes": {name: _node_json(val) for name, val in nodes.items()},
        "mu_fixed_point_trace": [_node_json(m) for m in mu_trace],
    }


def _dec(x: float) -> Decimal:
    return Decimal(x)


def run_full_evaluation(inp: Inputs) -> dict:
    """Compute the complete outward-rounded R_U record.

    Returns a JSON-ready dict with the interval image of every named DAG
    node at both I_U endpoints, at the center c, and over the full interval
    X with the derivative enclosure, plus the Krawczyk inclusion data and
    the witness interval. Every bound is serialized bit-exactly.
    """
    X = IV(inp.X_lo, inp.X_hi)
    c_iv = IV(inp.c, inp.c)
    Y_iv = IV(inp.Y, inp.Y)

    lo_nodes, lo_trace = evaluate_phi(inp, IV(inp.X_lo, inp.X_lo), False)
    hi_nodes, hi_trace = evaluate_phi(inp, IV(inp.X_hi, inp.X_hi), False)
    c_nodes, c_trace = evaluate_phi(inp, c_iv, False)
    full_nodes, full_trace = evaluate_phi(inp, X, True)

    phi_lo = lo_nodes["Phi"]
    phi_hi = hi_nodes["Phi"]
    phi_c = c_nodes["Phi"]
    dphi_X = full_nodes["Phi"].d

    one_minus = ONE - (Y_iv * dphi_X)
    K = (c_iv - (Y_iv * phi_c)) + (one_minus * (X - c_iv))

    endpoint_signs = {
        "Phi_at_I_U_lower": iv_to_json(phi_lo),
        "Phi_at_I_U_upper": iv_to_json(phi_hi),
        "Phi_lower_strictly_positive": phi_lo.lo > 0.0,
        "Phi_upper_strictly_negative": phi_hi.hi < 0.0,
        "existence_by_intermediate_value_theorem": phi_lo.lo > 0.0 and phi_hi.hi < 0.0,
    }

    derivative_block = {
        "dPhi_over_I_U": iv_to_json(dphi_X),
        "strictly_negative": dphi_X.hi < 0.0,
        "uniqueness_by_monotonicity": dphi_X.hi < 0.0,
    }

    inclusion = X.lo < K.lo and K.hi < X.hi
    krawczyk = {
        "operator": "K(X) = c - Y*Phi(c) + (1 - Y*Phi'(X))*(X - c)",
        "X": iv_to_json(X),
        "center_c": {"hex": inp.c.hex(), "decimal": repr(inp.c)},
        "Y": {"hex": inp.Y.hex(), "decimal": repr(inp.Y)},
        "Phi_at_center": iv_to_json(phi_c),
        "dPhi_over_X": iv_to_json(dphi_X),
        "one_minus_Y_dPhi": iv_to_json(one_minus),
        "K_of_X": iv_to_json(K),
        "K_strictly_inside_interior_of_X": inclusion,
        "left_margin_decimal": str(_dec(K.lo) - _dec(X.lo)),
        "right_margin_decimal": str(_dec(X.hi) - _dec(K.hi)),
    }

    witness = {
        "statement": (
            "Phi has exactly one zero in X; the zero lies in the witness "
            "interval K(X). Existence and uniqueness follow from the "
            "Krawczyk inclusion together with the strictly negative "
            "derivative enclosure; the endpoint sign block gives an "
            "independent existence proof by the intermediate value theorem."
        ),
        "R_U_witness_interval": iv_to_json(K),
        "width_decimal": str(_dec(K.hi) - _dec(K.lo)),
    }

    return {
        "evaluations": {
            "a_at_I_U_lower_endpoint": _context_json(lo_nodes, lo_trace),
            "a_at_I_U_upper_endpoint": _context_json(hi_nodes, hi_trace),
            "a_at_center_c": _context_json(c_nodes, c_trace),
            "a_over_full_I_U_with_derivative": _context_json(full_nodes, full_trace),
        },
        "endpoint_signs": endpoint_signs,
        "derivative_enclosure": derivative_block,
        "krawczyk": krawczyk,
        "witness": witness,
    }


def structural_input_block(inp: Inputs) -> dict:
    """Declared inputs with resolved binary64 brackets."""
    return {
        "declared": dict(inp.declared),
        "resolved": {
            "P_fwd_bracket": iv_to_json(inp.P),
            "b1_bracket": iv_to_json(inp.b1),
            "b2_bracket": iv_to_json(inp.b2),
            "b3_bracket": iv_to_json(inp.b3),
            "hypercharge_weight_bracket": iv_to_json(inp.w_hyper),
            "mu_seed_bracket": iv_to_json(inp.mu_seed),
            "X_lo_hex": inp.X_lo.hex(),
            "X_hi_hex": inp.X_hi.hex(),
            "X_contains_decimal_I_U": True,
            "center_c_hex": inp.c.hex(),
            "krawczyk_Y_hex": inp.Y.hex(),
        },
        "input_character": (
            "P_fwd is the forward pixel constant of the frozen source packet; "
            "N2, N3, b1, b2, b3, 3/5, the seed, and the iteration count are "
            "structural integers and rationals of the declared formula stack; "
            "I_U, c, and Y are enclosure choices whose soundness is proved by "
            "the log, not assumed. No measured endpoint constant is consumed."
        ),
    }
