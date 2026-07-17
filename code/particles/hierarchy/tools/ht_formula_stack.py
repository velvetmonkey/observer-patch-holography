#!/usr/bin/env python3
"""Higgs/top declared-surface formula stack in the directed-rounding backend.

Issue #333. This module re-evaluates the frozen R_HT declared-surface map of
certificates/R_HT_declared_surface_certificate.json in outward-rounded
binary64 interval arithmetic (tools/outward_interval.py), with forward-mode
interval automatic differentiation in all eleven input variables for the
Jacobian enclosure over the full input box.

The declared surface is the finite formula stack

    A_T   = 3/2 + beta_EW/4
    B_H   = 4/3 - beta_EW/54
    rho_HT = log(1 + tau2_tree_exact)
    R_T   = -tau2*eta^2 + (1 + beta_EW/28)*eta^6 + eta^8/14 + eta^9/27
    R_H   = eta^5 - (3/25)*eta^6 + lambda_EW*eta^6/18 + eta^8/(2*beta_EW)
    pi_y      = (eta + A_T*rho_HT + R_T)/sqrt(pi)
    pi_lambda = (eta - B_H*rho_HT + R_H)/sqrt(pi)
    delta_y_t     = pi_y * y_t_core_mt
    delta_lambda  = -(16/9) * pi_lambda * lambda_core_mt
    m_t = mt_pole_core_gev + d_mt_pole_d_y_t * delta_y_t
    m_H = mH_core_gev + d_mH_d_lambda * delta_lambda

with the diagnostic exactifier scalars

    c_T_live = (A_T*(rho_HT - tau2) + R_T)/delta_n_tree_exact
    c_H_live = (-(4/3)*tau2 + B_H*rho_HT - R_H)/delta_n_tree_exact.

Interval extension policy: every node above is evaluated with the backend
primitives of outward_interval.py. Integer powers of eta evaluate as a fixed
chain of outward interval products (eta^2, eta^4=eta^2*eta^2, eta^5, eta^6,
eta^8=eta^4*eta^4, eta^9). log(1+tau2) evaluates as the in-module interval
log applied to the interval 1+tau2, which is strictly positive on the box.
sqrt(pi) evaluates as the correctly rounded sqrt of the bracketed pi
constant, stepped one ulp outward. All rational coefficients are bracketed
from exact fractions. No function outside the existing backend is used and
no libm exp/log is called.

Input character: the eleven scalar inputs are declared branch inputs, split
into the candidate D10 tuple (eta_source, beta_EW, lambda_EW,
tau2_tree_exact, delta_n_tree_exact) and the declared D11 calibration
surface constants (y_t_core_mt, lambda_core_mt, mH_core_gev,
mt_pole_core_gev, d_mH_d_lambda, d_mt_pole_d_y_t). No measured particle
mass value appears numerically in the input box. The D10 tuple descends
from the MSbar gauge couplings at the Z scale on the legacy D10 calibration
branch; the D11 surface constants belong to a declared running, matching,
and threshold surface whose historical selection used target inspection.
Both facts are recorded per input in INPUT_METADATA and repeated in the
emitted certificate; the enclosure certifies the arithmetic of the declared
surface, and the provenance gates stay open upstream.
"""

from __future__ import annotations

from fractions import Fraction

from outward_interval import (
    IV,
    ONE,
    PI,
    TWO,
    ZERO,
    bracket_exact_decimal,
    bracket_fraction,
    iv_log,
    iv_sqrt,
    iv_to_json,
)

STACK_ID = "oph-ht-declared-surface-formula-stack"
STACK_VERSION = "1.0.0"

VAR_NAMES = (
    "eta_source",
    "beta_EW",
    "lambda_EW",
    "tau2_tree_exact",
    "delta_n_tree_exact",
    "y_t_core_mt",
    "lambda_core_mt",
    "mH_core_gev",
    "mt_pole_core_gev",
    "d_mH_d_lambda",
    "d_mt_pole_d_y_t",
)

N_VARS = len(VAR_NAMES)

DECLARED_INPUT_KEYS = tuple(f"{name}_decimal" for name in VAR_NAMES) + (
    "box_relative_half_width_decimal",
)

DEFAULT_DECLARED_INPUTS = {
    "eta_source_decimal": "0.022147000871961295",
    "beta_EW_decimal": "0.5385291530498766",
    "lambda_EW_decimal": "0.00022769874427635073",
    "tau2_tree_exact_decimal": "-0.0002311623001746158",
    "delta_n_tree_exact_decimal": "0.0002346358802434819",
    "y_t_core_mt_decimal": "0.92046435",
    "lambda_core_mt_decimal": "0.13164915",
    "mH_core_gev_decimal": "126.62263",
    "mt_pole_core_gev_decimal": "170.26125",
    "d_mH_d_lambda_decimal": "480.0",
    "d_mt_pole_d_y_t_decimal": "184.97",
    "box_relative_half_width_decimal": "1e-9",
}

_D10_SOURCE = "code/particles/runs/calibration/d10_ew_source_transport_pair.json"
_D10_REPAIR = "code/particles/runs/calibration/d10_ew_target_free_repair_value_law.json"
_D11_SURFACE = "code/particles/runs/calibration/d11_declared_calibration_surface.json"

_D10_NOTE = (
    "Candidate D10 tuple entry on the legacy D10 calibration branch; descends "
    "from the MSbar gauge couplings alpha2_mz and alphaY_mz at the Z scale "
    "and the alpha_U seed; candidate-only upstream, no measured particle "
    "mass value enters numerically."
)
_D11_NOTE = (
    "Declared D11 calibration-surface constant on the printed D10/D11 "
    "running, matching, and threshold surface; the historical selection of "
    "this surface used target inspection (target-anchored fit), and its "
    "source derivation is an open upstream gate."
)

INPUT_METADATA = {
    "eta_source": {
        "role": "candidate D10 tuple scalar; leading split coordinate seed",
        "normalization": "dimensionless",
        "provenance_class": "declared_branch_input_d10_tuple",
        "source_artifact": _D10_SOURCE,
        "note": _D10_NOTE + " Formula: alpha_u_from_seed * beta_EW.",
    },
    "beta_EW": {
        "role": "candidate D10 tuple scalar; electroweak coupling asymmetry (paper symbol rho_EW)",
        "normalization": "dimensionless",
        "provenance_class": "declared_branch_input_d10_tuple",
        "source_artifact": _D10_SOURCE,
        "note": _D10_NOTE + " Formula: (alpha2_mz - alphaY_mz)/(alpha2_mz + alphaY_mz).",
    },
    "lambda_EW": {
        "role": "candidate D10 tuple scalar; quartic-channel repair coordinate",
        "normalization": "dimensionless",
        "provenance_class": "declared_branch_input_d10_tuple",
        "source_artifact": _D10_REPAIR,
        "note": _D10_NOTE,
    },
    "tau2_tree_exact": {
        "role": "candidate D10 tuple scalar; charged-channel tree repair coordinate",
        "normalization": "dimensionless",
        "provenance_class": "declared_branch_input_d10_tuple",
        "source_artifact": _D10_REPAIR,
        "note": _D10_NOTE,
    },
    "delta_n_tree_exact": {
        "role": "candidate D10 tuple scalar; neutral-channel tree repair coordinate (diagnostic exactifier denominator)",
        "normalization": "dimensionless",
        "provenance_class": "declared_branch_input_d10_tuple",
        "source_artifact": _D10_REPAIR,
        "note": _D10_NOTE,
    },
    "y_t_core_mt": {
        "role": "declared D11 core top Yukawa at mu_t",
        "normalization": "dimensionless",
        "provenance_class": "declared_branch_input_d11_surface",
        "source_artifact": _D11_SURFACE,
        "note": _D11_NOTE,
    },
    "lambda_core_mt": {
        "role": "declared D11 core Higgs quartic at mu_t",
        "normalization": "dimensionless",
        "provenance_class": "declared_branch_input_d11_surface",
        "source_artifact": _D11_SURFACE,
        "note": _D11_NOTE,
    },
    "mH_core_gev": {
        "role": "declared D11 core Higgs chart coordinate",
        "normalization": "GeV",
        "provenance_class": "declared_branch_input_d11_surface",
        "source_artifact": _D11_SURFACE,
        "note": _D11_NOTE,
    },
    "mt_pole_core_gev": {
        "role": "declared D11 core top pole chart coordinate",
        "normalization": "GeV",
        "provenance_class": "declared_branch_input_d11_surface",
        "source_artifact": _D11_SURFACE,
        "note": _D11_NOTE,
    },
    "d_mH_d_lambda": {
        "role": "declared D11 Jacobian entry d m_H / d lambda",
        "normalization": "GeV per unit quartic",
        "provenance_class": "declared_branch_input_d11_surface",
        "source_artifact": _D11_SURFACE,
        "note": _D11_NOTE,
    },
    "d_mt_pole_d_y_t": {
        "role": "declared D11 Jacobian entry d m_t / d y_t",
        "normalization": "GeV per unit Yukawa",
        "provenance_class": "declared_branch_input_d11_surface",
        "source_artifact": _D11_SURFACE,
        "note": _D11_NOTE,
    },
    "box_relative_half_width_decimal": {
        "role": "declared relative half width of the certification box around each input center",
        "normalization": "dimensionless",
        "provenance_class": "enclosure_choice",
        "source_artifact": "this certificate",
        "note": (
            "Enclosure-domain choice; the enclosure and the non-singularity "
            "conditions are proved over the entire box, so the choice widens "
            "rather than weakens the certified statement."
        ),
    },
}

ALLOWED_PROVENANCE_CLASSES = (
    "declared_branch_input_d10_tuple",
    "declared_branch_input_d11_surface",
    "enclosure_choice",
)

DECLARED_BRANCH_INPUT_WHITELIST = VAR_NAMES

_ZERO_GRAD = tuple(ZERO for _ in range(N_VARS))


class ADN:
    """Forward-mode pair (value interval, gradient interval tuple) in N_VARS variables."""

    __slots__ = ("v", "g")

    def __init__(self, v: IV, g: tuple):
        self.v = v
        self.g = g

    @staticmethod
    def _wrap(x):
        return x if isinstance(x, ADN) else ADN(x, _ZERO_GRAD)

    def __add__(self, other):
        o = ADN._wrap(other)
        return ADN(self.v + o.v, tuple(a + b for a, b in zip(self.g, o.g)))

    __radd__ = __add__

    def __sub__(self, other):
        o = ADN._wrap(other)
        return ADN(self.v - o.v, tuple(a - b for a, b in zip(self.g, o.g)))

    def __rsub__(self, other):
        o = ADN._wrap(other)
        return ADN(o.v - self.v, tuple(a - b for a, b in zip(o.g, self.g)))

    def __neg__(self):
        return ADN(-self.v, tuple(-a for a in self.g))

    def __mul__(self, other):
        o = ADN._wrap(other)
        return ADN(
            self.v * o.v,
            tuple(a * o.v + self.v * b for a, b in zip(self.g, o.g)),
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = ADN._wrap(other)
        den = o.v * o.v
        return ADN(
            self.v / o.v,
            tuple((a * o.v - self.v * b) / den for a, b in zip(self.g, o.g)),
        )

    def __rtruediv__(self, other):
        return ADN._wrap(other).__truediv__(self)


def x_log(x):
    if isinstance(x, ADN):
        return ADN(iv_log(x.v), tuple(a / x.v for a in x.g))
    return iv_log(x)


def _rat(num: int, den: int) -> IV:
    return bracket_fraction(Fraction(num, den))


C_3_2 = _rat(3, 2)
C_1_4 = _rat(1, 4)
C_4_3 = _rat(4, 3)
C_1_54 = _rat(1, 54)
C_1_28 = _rat(1, 28)
C_1_14 = _rat(1, 14)
C_1_27 = _rat(1, 27)
C_3_25 = _rat(3, 25)
C_1_18 = _rat(1, 18)
C_16_9 = _rat(16, 9)
C_1_2 = _rat(1, 2)
SQRT_PI = iv_sqrt(PI)


class Inputs:
    """Declared branch inputs resolved to backend centers and box intervals."""

    def __init__(self, declared: dict):
        keys = tuple(sorted(declared.keys()))
        if keys != tuple(sorted(DECLARED_INPUT_KEYS)):
            raise ValueError(
                f"declared input keys {keys} do not match the declared allowlist"
            )
        self.declared = dict(declared)
        half_width = Fraction(declared["box_relative_half_width_decimal"])
        if not half_width > 0:
            raise ValueError("box relative half width must be positive")
        self.centers: dict[str, IV] = {}
        self.boxes: dict[str, IV] = {}
        for name in VAR_NAMES:
            center_frac = Fraction(declared[f"{name}_decimal"])
            if center_frac == 0:
                raise ValueError(f"input {name} must be nonzero for the relative box")
            width_frac = abs(center_frac) * half_width
            self.centers[name] = bracket_exact_decimal(declared[f"{name}_decimal"])
            lo = bracket_fraction(center_frac - width_frac).lo
            hi = bracket_fraction(center_frac + width_frac).hi
            self.boxes[name] = IV(lo, hi)


def evaluate_ht(inp: Inputs, on_box: bool):
    """Interval image (and gradient enclosure) of every named formula node.

    on_box False evaluates at the input centers with plain intervals;
    on_box True evaluates over the full input box with forward-mode
    gradients in all N_VARS variables.
    """
    if on_box:
        values = {}
        for i, name in enumerate(VAR_NAMES):
            grad = tuple(ONE if j == i else ZERO for j in range(N_VARS))
            values[name] = ADN(inp.boxes[name], grad)
    else:
        values = {name: inp.centers[name] for name in VAR_NAMES}

    eta = values["eta_source"]
    beta = values["beta_EW"]
    lam = values["lambda_EW"]
    tau2 = values["tau2_tree_exact"]
    dn = values["delta_n_tree_exact"]
    ytc = values["y_t_core_mt"]
    lamc = values["lambda_core_mt"]
    mhc = values["mH_core_gev"]
    mtc = values["mt_pole_core_gev"]
    j_h = values["d_mH_d_lambda"]
    j_t = values["d_mt_pole_d_y_t"]

    nodes = dict(values)

    a_t = C_3_2 + (beta * C_1_4)
    nodes["A_T"] = a_t
    b_h = C_4_3 - (beta * C_1_54)
    nodes["B_H"] = b_h

    one_plus_tau2 = ONE + tau2
    nodes["one_plus_tau2"] = one_plus_tau2
    rho = x_log(one_plus_tau2)
    nodes["rho_HT"] = rho

    eta2 = eta * eta
    eta4 = eta2 * eta2
    eta5 = eta4 * eta
    eta6 = eta5 * eta
    eta8 = eta4 * eta4
    eta9 = eta8 * eta
    nodes["eta_pow_2"] = eta2
    nodes["eta_pow_4"] = eta4
    nodes["eta_pow_5"] = eta5
    nodes["eta_pow_6"] = eta6
    nodes["eta_pow_8"] = eta8
    nodes["eta_pow_9"] = eta9

    r_t = (
        (-(tau2 * eta2))
        + ((ONE + (beta * C_1_28)) * eta6)
        + (eta8 * C_1_14)
        + (eta9 * C_1_27)
    )
    nodes["R_T"] = r_t
    r_h = (
        eta5
        - (C_3_25 * eta6)
        + ((lam * eta6) * C_1_18)
        + (eta8 / (TWO * beta))
    )
    nodes["R_H"] = r_h

    pi_y = (eta + (a_t * rho) + r_t) / SQRT_PI
    nodes["pi_y"] = pi_y
    pi_lambda = (eta - (b_h * rho) + r_h) / SQRT_PI
    nodes["pi_lambda"] = pi_lambda

    delta_y = pi_y * ytc
    nodes["delta_y_t_mt"] = delta_y
    delta_lambda = -(C_16_9 * (pi_lambda * lamc))
    nodes["delta_lambda_mt"] = delta_lambda

    m_t = mtc + (j_t * delta_y)
    nodes["m_t_D11_GeV"] = m_t
    m_h = mhc + (j_h * delta_lambda)
    nodes["m_H_GeV"] = m_h

    nodes["Sigma_HT"] = (pi_y + pi_lambda) * C_1_2
    nodes["w_HT"] = pi_y - pi_lambda
    nodes["c_T_live"] = ((a_t * (rho - tau2)) + r_t) / dn
    nodes["c_H_live"] = ((-(C_4_3 * tau2)) + (b_h * rho) - r_h) / dn

    return nodes


def _node_json(x) -> dict:
    if isinstance(x, ADN):
        return {
            "value": iv_to_json(x.v),
            "gradient": {name: iv_to_json(g) for name, g in zip(VAR_NAMES, x.g)},
        }
    return iv_to_json(x)


JACOBIAN_OUTPUT_NODES = ("pi_y", "pi_lambda", "m_H_GeV", "m_t_D11_GeV")


def run_full_evaluation(inp: Inputs) -> dict:
    """Compute the complete outward-rounded R_HT declared-surface record.

    Returns a JSON-ready dict with the interval image of every named formula
    node at the input centers and over the full input box with the gradient
    enclosure, the Jacobian interval enclosure of the four output nodes over
    the full box, the chart-block non-singularity certificate, the output
    inclusion checks, and the uniqueness scope. Every bound is serialized
    bit-exactly.
    """
    center_nodes = evaluate_ht(inp, on_box=False)
    box_nodes = evaluate_ht(inp, on_box=True)

    jacobian = {
        out: {name: iv_to_json(g) for name, g in zip(VAR_NAMES, box_nodes[out].g)}
        for out in JACOBIAN_OUTPUT_NODES
    }

    dmt_dpiy = inp.boxes["d_mt_pole_d_y_t"] * inp.boxes["y_t_core_mt"]
    dmh_dpilambda = -(C_16_9 * (inp.boxes["d_mH_d_lambda"] * inp.boxes["lambda_core_mt"]))
    det = dmt_dpiy * dmh_dpilambda
    non_singularity = {
        "chart_block": "d(m_t_D11_GeV, m_H_GeV) / d(pi_y, pi_lambda)",
        "d_mt_d_pi_y": iv_to_json(dmt_dpiy),
        "d_mt_d_pi_lambda_identically_zero": True,
        "d_mH_d_pi_y_identically_zero": True,
        "d_mH_d_pi_lambda": iv_to_json(dmh_dpilambda),
        "determinant": iv_to_json(det),
        "top_diagonal_strictly_positive": dmt_dpiy.lo > 0.0,
        "higgs_diagonal_strictly_negative": dmh_dpilambda.hi < 0.0,
        "determinant_excludes_zero": det.hi < 0.0,
        "off_diagonal_note": (
            "On the declared stack m_t_D11_GeV carries no pi_lambda "
            "dependence and m_H_GeV carries no pi_y dependence, so the "
            "chart block is diagonal by construction."
        ),
    }

    inclusion = {}
    for out in ("m_H_GeV", "m_t_D11_GeV", "pi_y", "pi_lambda"):
        c = center_nodes[out]
        b = box_nodes[out].v
        inclusion[out] = {
            "center_enclosure": iv_to_json(c),
            "box_enclosure": iv_to_json(b),
            "center_enclosure_inside_box_enclosure": b.lo <= c.lo and c.hi <= b.hi,
        }

    uniqueness = {
        "statement": (
            "F_HT is an explicit finite composition of backend primitives on "
            "the input box, so it assigns exactly one output pair "
            "(m_H_GeV, m_t_D11_GeV) to every point of the box, and the "
            "emitted box enclosures contain every such output. The diagonal "
            "chart block d(m_t, m_H)/d(pi_y, pi_lambda) has entries bounded "
            "away from zero with fixed signs over the entire box, so the "
            "readout (pi_y, pi_lambda) -> (m_t, m_H) is injective on the box "
            "image. This is the interval-grade form of the single-valued "
            "local implication stated for the declared surface."
        ),
        "scope": (
            "The certificate encloses the declared frozen D10/D11 surface "
            "map only. It is a statement about the arithmetic of the "
            "declared surface; it is neither an existence nor a uniqueness "
            "statement for the two-loop criticality system lambda=0, "
            "beta_lambda=0, which stays on the conditional criticality "
            "branch, and it leaves the source-root, physical-scale, "
            "QT1-QT5, RG/scheme, rigidity, provenance, uncertainty, and "
            "complex-pole gates open."
        ),
    }

    return {
        "evaluations": {
            "at_input_centers": {name: _node_json(v) for name, v in center_nodes.items()},
            "over_full_input_box_with_gradient": {
                name: _node_json(v) for name, v in box_nodes.items()
            },
        },
        "jacobian_enclosure_over_full_box": jacobian,
        "readout_non_singularity": non_singularity,
        "output_inclusion": inclusion,
        "uniqueness": uniqueness,
    }


def declared_input_block(inp: Inputs) -> dict:
    """Declared inputs with resolved binary64 centers, boxes, and provenance."""
    resolved = {}
    for name in VAR_NAMES:
        meta = INPUT_METADATA[name]
        resolved[name] = {
            "decimal": inp.declared[f"{name}_decimal"],
            "center": iv_to_json(inp.centers[name]),
            "box": iv_to_json(inp.boxes[name]),
            "role": meta["role"],
            "normalization": meta["normalization"],
            "provenance_class": meta["provenance_class"],
            "source_artifact": meta["source_artifact"],
            "note": meta["note"],
        }
    return {
        "declared": dict(inp.declared),
        "resolved": resolved,
        "box_policy": {
            "relative_half_width_decimal": inp.declared["box_relative_half_width_decimal"],
            "construction": (
                "For each input with center decimal c and half width h, the "
                "box is the outward binary64 bracket of the exact rational "
                "interval [c - |c|*h, c + |c|*h], so the box contains the "
                "declared decimal centers."
            ),
            "provenance_class": INPUT_METADATA["box_relative_half_width_decimal"][
                "provenance_class"
            ],
            "note": INPUT_METADATA["box_relative_half_width_decimal"]["note"],
        },
        "declared_branch_input_whitelist": list(DECLARED_BRANCH_INPUT_WHITELIST),
        "input_character": (
            "All eleven scalars are declared branch inputs of the frozen "
            "declared surface: the candidate D10 tuple descends from the "
            "MSbar gauge couplings at the Z scale on the legacy D10 "
            "calibration branch, and the D11 core/Jacobian constants belong "
            "to a declared surface whose historical selection used target "
            "inspection. No measured particle mass value appears numerically "
            "in the input box. The enclosure certifies the declared-surface "
            "arithmetic; source derivation of the inputs stays an open "
            "upstream gate."
        ),
    }


def interval_extension_block() -> dict:
    """Machine-readable definition of the interval extension per equation node."""
    return {
        "policy": (
            "Each node of the declared Higgs/top stack is evaluated with the "
            "directed-rounding primitives of tools/outward_interval.py in a "
            "fixed deterministic operation order; the verifier reproduces "
            "every bound bit-exactly."
        ),
        "nodes": {
            "A_T, B_H, R_T, R_H, pi_y, pi_lambda, delta_y_t_mt, delta_lambda_mt, m_t_D11_GeV, m_H_GeV, Sigma_HT, w_HT, c_T_live, c_H_live": (
                "outward-rounded binary64 interval +, -, *, / with rational "
                "coefficients bracketed from exact fractions"
            ),
            "eta powers": (
                "fixed chain of outward interval products: eta^2, "
                "eta^4=eta^2*eta^2, eta^5=eta^4*eta, eta^6=eta^5*eta, "
                "eta^8=eta^4*eta^4, eta^9=eta^8*eta"
            ),
            "rho_HT": (
                "in-module interval log applied to the strictly positive "
                "interval 1+tau2_tree_exact (frexp reduction, atanh series "
                "with explicit remainder pad; no libm log)"
            ),
            "sqrt(pi)": (
                "correctly rounded math.sqrt of the bracketed pi decimal "
                "string, stepped one ulp outward per side"
            ),
            "gradient": (
                "forward-mode interval automatic differentiation in all "
                "eleven inputs with the same primitives, giving the Jacobian "
                "interval enclosure over the full input box"
            ),
        },
        "backend_functions_added_for_this_stack": "none",
    }
