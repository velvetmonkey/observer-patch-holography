#!/usr/bin/env python3
"""Analytic finite proxies for collar CMI decay (GitHub issue #307).

This module does not estimate conditional mutual information from samples and
does not promote a theorem.  It makes the regulator and mixing contract used by
the collar-recoverability continuation explicit, then evaluates its finite
consequences without exponentiating until the last step.

Regulator contract
------------------
At UV spacing ``ell_uv`` let

    rho = exp(-beta H) / Z,       H = sum_X Phi_X,

on a finite-degree lattice with finite on-site dimension.  The interaction
constants have the uniform bounds

    diam(X) <= r0 * ell_uv,
    sup_x sum_{X containing x} ||Phi_X|| <= J.

Finite range by itself, or ordinary connected-correlation clustering by
itself, is not used as a hidden implication.  The quantitative input is the
separate *strong conditional/matrix-mixing* envelope, uniform over the collar
family,

    I(A_delta:D_delta | B_delta)
        <= kappa * |partial C|_UV * exp(-(m-r0)/zeta),               (1)

where ``m = delta / ell_uv``, ``xi = zeta * ell_uv``, and entropies are in
nats.  Equivalently, with ``c = kappa * exp(r0/zeta)``, (1) is

    I <= c * |partial C|_UV * exp(-delta/xi).

The numerically stable full rate margin is

    M = (m-r0)/zeta - log(kappa) - log(|partial C|_UV),

so the logarithm of the right-hand side of (1) is exactly ``-M``.  For fixed
``kappa``, ``r0``, and ``zeta``, its sharp vanishing-envelope criterion is

    delta/xi - log(|partial C|_UV) -> +infinity.                    (2)

Thus ``delta/ell_uv -> infinity`` alone is insufficient when the regulated
boundary grows.  ``counterexample_receipt`` records the explicit choice
``ell_uv = exp(-n^2)``, ``delta = n * ell_uv``, and
``|partial C|_UV = exp(n^2)``: the width ratio tends to infinity while the
margin ``n-n^2`` tends to minus infinity.

For a boundary envelope

    |partial C|_UV <= C_partial * (ell0/ell_uv)^p,

the analytic schedule

    delta >= zeta * ell_uv * (p+eta) * log(ell0/ell_uv), eta > 0,  (3)

gives

    log(I upper bound)
        <= log(kappa*C_partial) + r0/zeta
           - eta*log(ell0/ell_uv) -> -infinity.

Running this file writes
``runs/collar_recoverability_analytic_finite_proxy.json``.  The emitted JSON is
an analytic finite proxy for (1)--(3), not empirical evidence for the mixing
hypothesis and not a theorem-status promotion for any downstream branch.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "runs" / "collar_recoverability_analytic_finite_proxy.json"

_LOG_FLOAT_MAX = math.log(sys.float_info.max)
# ``min * epsilon`` is the smallest positive IEEE-754 binary64 subnormal.
_LOG_FLOAT_MIN_SUBNORMAL = math.log(sys.float_info.min * sys.float_info.epsilon)


def _finite_positive(name: str, value: float) -> None:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")


def _finite_nonnegative(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True)
class FiniteRangeGibbsMixingConstants:
    """Uniform constants for one regulated finite-range Gibbs/mixing stage.

    ``interaction_strength_bound`` means
    ``sup_x sum_{X containing x} ||Phi_X|| <= J``.  The last two fields are
    constants of the separately assumed strong conditional/matrix-mixing
    estimate; this class does not infer them from the preceding Gibbs data.
    """

    ell_uv: float
    beta: float
    local_hilbert_dimension: int
    coordination_number_bound: int
    interaction_strength_bound: float
    interaction_range_steps: float
    mixing_prefactor_kappa: float
    mixing_length_steps_zeta: float

    def __post_init__(self) -> None:
        _finite_positive("ell_uv", self.ell_uv)
        _finite_nonnegative("beta", self.beta)
        if isinstance(self.local_hilbert_dimension, bool) or not isinstance(
            self.local_hilbert_dimension, int
        ) or self.local_hilbert_dimension < 2:
            raise ValueError("local_hilbert_dimension must be an integer >= 2")
        if isinstance(self.coordination_number_bound, bool) or not isinstance(
            self.coordination_number_bound, int
        ) or self.coordination_number_bound < 1:
            raise ValueError("coordination_number_bound must be an integer >= 1")
        _finite_nonnegative(
            "interaction_strength_bound", self.interaction_strength_bound
        )
        _finite_nonnegative(
            "interaction_range_steps", self.interaction_range_steps
        )
        _finite_positive("mixing_prefactor_kappa", self.mixing_prefactor_kappa)
        _finite_positive("mixing_length_steps_zeta", self.mixing_length_steps_zeta)

    @property
    def interaction_range(self) -> float:
        """Physical interaction range ``r0 * ell_uv``."""
        return self.interaction_range_steps * self.ell_uv

    @property
    def correlation_length_xi(self) -> float:
        """Physical mixing length ``xi = zeta * ell_uv``."""
        return self.mixing_length_steps_zeta * self.ell_uv

    @property
    def continuum_prefactor_c(self) -> float:
        """Prefactor in ``c |boundary| exp(-delta/xi)``."""
        return self.mixing_prefactor_kappa * math.exp(
            self.interaction_range_steps / self.mixing_length_steps_zeta
        )


@dataclass(frozen=True)
class PowerLawBoundarySchedule:
    """Boundary-growth envelope and a positive schedule margin ``eta``."""

    ell0: float
    boundary_prefactor: float
    boundary_power: float
    eta: float

    def __post_init__(self) -> None:
        _finite_positive("ell0", self.ell0)
        _finite_positive("boundary_prefactor", self.boundary_prefactor)
        _finite_nonnegative("boundary_power", self.boundary_power)
        _finite_positive("eta", self.eta)

    def log_refinement(self, ell_uv: float) -> float:
        _finite_positive("ell_uv", ell_uv)
        if ell_uv > self.ell0:
            raise ValueError("ell_uv must not exceed the reference scale ell0")
        return math.log(self.ell0 / ell_uv)

    def log_boundary_upper_bound(self, ell_uv: float) -> float:
        return (
            math.log(self.boundary_prefactor)
            + self.boundary_power * self.log_refinement(ell_uv)
        )

    def minimum_delta(self, ell_uv: float, zeta: float) -> float:
        """Right-hand side of the sufficient physical schedule (3)."""
        _finite_positive("zeta", zeta)
        return (
            zeta
            * ell_uv
            * (self.boundary_power + self.eta)
            * self.log_refinement(ell_uv)
        )


def stable_exp(log_value: float) -> float:
    """Exponentiate a log-envelope without overflow or unstable underflow."""
    if math.isnan(log_value):
        raise ValueError("log_value must not be NaN")
    if log_value == -math.inf or log_value <= _LOG_FLOAT_MIN_SUBNORMAL:
        return 0.0
    if log_value == math.inf or log_value >= _LOG_FLOAT_MAX:
        return math.inf
    return math.exp(log_value)


def collar_log_bound_from_log_boundary(
    *,
    log_boundary_size: float,
    collar_width_steps: float,
    constants: FiniteRangeGibbsMixingConstants,
) -> float:
    """Logarithm of the conditional/matrix-mixing CMI envelope (1).

    The mixing contract is only asserted once the collar separates the two
    sides by at least the interaction range, hence ``m >= r0`` is enforced.
    Accepting ``log_boundary_size`` directly keeps large refinement stages
    numerically representable.
    """
    _finite_nonnegative("log_boundary_size", log_boundary_size)
    _finite_nonnegative("collar_width_steps", collar_width_steps)
    if collar_width_steps < constants.interaction_range_steps:
        raise ValueError(
            "collar_width_steps must be at least interaction_range_steps"
        )
    return (
        math.log(constants.mixing_prefactor_kappa)
        + log_boundary_size
        - (
            collar_width_steps - constants.interaction_range_steps
        ) / constants.mixing_length_steps_zeta
    )


def collar_log_bound(
    *,
    boundary_size_uv: float,
    collar_width_steps: float,
    constants: FiniteRangeGibbsMixingConstants,
) -> float:
    """Convenience wrapper for a directly representable boundary cardinality."""
    _finite_positive("boundary_size_uv", boundary_size_uv)
    if boundary_size_uv < 1.0:
        raise ValueError("boundary_size_uv is a cardinality and must be >= 1")
    return collar_log_bound_from_log_boundary(
        log_boundary_size=math.log(boundary_size_uv),
        collar_width_steps=collar_width_steps,
        constants=constants,
    )


def full_rate_margin(
    *,
    log_boundary_size: float,
    collar_width_steps: float,
    constants: FiniteRangeGibbsMixingConstants,
) -> float:
    """Return ``-log(bound)``; divergence to ``+inf`` makes (1) vanish."""
    return -collar_log_bound_from_log_boundary(
        log_boundary_size=log_boundary_size,
        collar_width_steps=collar_width_steps,
        constants=constants,
    )


def sharp_geometric_margin(
    *,
    log_boundary_size: float,
    collar_width_steps: float,
    constants: FiniteRangeGibbsMixingConstants,
) -> float:
    """The asymptotic margin ``delta/xi - log(|partial C|_UV)`` in (2)."""
    _finite_nonnegative("log_boundary_size", log_boundary_size)
    _finite_nonnegative("collar_width_steps", collar_width_steps)
    return (
        collar_width_steps / constants.mixing_length_steps_zeta
        - log_boundary_size
    )


def finite_stage_receipt(
    *,
    log_boundary_size: float,
    collar_width_steps: float,
    constants: FiniteRangeGibbsMixingConstants,
) -> dict[str, float]:
    """Evaluate one finite analytic proxy stage in stable log coordinates."""
    log_bound = collar_log_bound_from_log_boundary(
        log_boundary_size=log_boundary_size,
        collar_width_steps=collar_width_steps,
        constants=constants,
    )
    return {
        "ell_uv": constants.ell_uv,
        "interaction_range": constants.interaction_range,
        "correlation_length_xi": constants.correlation_length_xi,
        "collar_width_steps_m": collar_width_steps,
        "physical_collar_width_delta": collar_width_steps * constants.ell_uv,
        "log_boundary_size_uv": log_boundary_size,
        "log_cmi_upper_bound_nats": log_bound,
        "cmi_upper_bound_nats": stable_exp(log_bound),
        "full_rate_margin": -log_bound,
        "sharp_geometric_margin": sharp_geometric_margin(
            log_boundary_size=log_boundary_size,
            collar_width_steps=collar_width_steps,
            constants=constants,
        ),
    }


def sufficient_schedule_receipt(
    *,
    log_refinements: Iterable[float],
    constants: FiniteRangeGibbsMixingConstants,
    schedule: PowerLawBoundarySchedule,
) -> dict:
    """Evaluate the power-law boundary schedule and its analytic limit bound.

    Each supplied ``L`` denotes ``log(ell0/ell_uv)``.  The finite proxy uses
    the exact threshold in (3), rather than rounding ``m`` to lattice steps;
    taking ``ceil(m)`` on a discrete regulator can only improve the bound.
    """
    stages = []
    for raw_log_refinement in log_refinements:
        log_refinement = float(raw_log_refinement)
        _finite_nonnegative("log_refinement", log_refinement)
        ell_uv = schedule.ell0 * math.exp(-log_refinement)
        stage_constants = replace(constants, ell_uv=ell_uv)
        m_threshold = (
            stage_constants.mixing_length_steps_zeta
            * (schedule.boundary_power + schedule.eta)
            * log_refinement
        )
        # Very early stages may not yet clear the finite interaction range.
        # The physical schedule is therefore the maximum of the asymptotic
        # threshold and r0; this affects no large-refinement conclusion.
        m_used = max(m_threshold, stage_constants.interaction_range_steps)
        log_boundary = (
            math.log(schedule.boundary_prefactor)
            + schedule.boundary_power * log_refinement
        )
        stage = finite_stage_receipt(
            log_boundary_size=log_boundary,
            collar_width_steps=m_used,
            constants=stage_constants,
        )
        analytic_log_bound = (
            math.log(
                stage_constants.mixing_prefactor_kappa
                * schedule.boundary_prefactor
            )
            + stage_constants.interaction_range_steps
            / stage_constants.mixing_length_steps_zeta
            - schedule.eta * log_refinement
        )
        stage.update(
            {
                "log_refinement_ell0_over_ell_uv": log_refinement,
                "boundary_power_law_log_upper_bound": log_boundary,
                "schedule_threshold_delta": schedule.minimum_delta(
                    ell_uv, stage_constants.mixing_length_steps_zeta
                ),
                "schedule_threshold_steps": m_threshold,
                "analytic_log_bound_from_schedule": analytic_log_bound,
                "finite_range_floor_active": m_used > m_threshold,
            }
        )
        stages.append(stage)

    log_bounds = [stage["log_cmi_upper_bound_nats"] for stage in stages]
    full_margins = [stage["full_rate_margin"] for stage in stages]
    width_ratios = [stage["collar_width_steps_m"] for stage in stages]
    deltas = [stage["physical_collar_width_delta"] for stage in stages]
    return {
        "boundary_envelope": (
            "|partial C|_UV <= C_partial * (ell0/ell_uv)^p"
        ),
        "sufficient_schedule": (
            "delta >= zeta*ell_uv*(p+eta)*log(ell0/ell_uv)"
        ),
        "derived_log_bound": (
            "log I_bound <= log(kappa*C_partial) + r0/zeta "
            "- eta*log(ell0/ell_uv)"
        ),
        "schedule_constants": asdict(schedule),
        "stages": stages,
        "finite_proxy_checks": {
            "log_bounds_strictly_decrease": all(
                left > right for left, right in zip(log_bounds, log_bounds[1:])
            ),
            "full_rate_margins_strictly_increase": all(
                left < right
                for left, right in zip(full_margins, full_margins[1:])
            ),
            "width_ratio_increases": all(
                left < right
                for left, right in zip(width_ratios, width_ratios[1:])
            ),
            "physical_delta_decreases_on_displayed_tail": all(
                left > right for left, right in zip(deltas, deltas[1:])
            ),
        },
        "analytic_limit": {
            "ell_uv": "0",
            "delta": "0 because ell_uv*log(ell0/ell_uv) -> 0",
            "delta_over_ell_uv": "+infinity",
            "full_rate_margin": "+infinity at least linearly in eta*log(ell0/ell_uv)",
            "cmi_envelope": "0",
            "conditional_on_uniform_mixing_envelope": True,
        },
    }


def counterexample_receipt(n_values: Iterable[int] = range(2, 13)) -> dict:
    """Reject ``delta/ell_uv -> infinity`` as a sufficient criterion.

    Uses ``ell_uv=e^{-n^2}``, ``delta=n*ell_uv``, unit ``zeta`` and
    ``|partial C|_UV=e^{n^2}``.  All rate calculations use logs so the same
    construction remains meaningful beyond floating-point boundary sizes.
    """
    constants = FiniteRangeGibbsMixingConstants(
        ell_uv=1.0,
        beta=1.0,
        local_hilbert_dimension=2,
        coordination_number_bound=2,
        interaction_strength_bound=1.0,
        interaction_range_steps=0.0,
        mixing_prefactor_kappa=1.0,
        mixing_length_steps_zeta=1.0,
    )
    stages = []
    previous_n = None
    for raw_n in n_values:
        if isinstance(raw_n, bool) or not isinstance(raw_n, int) or raw_n < 1:
            raise ValueError("n_values must contain positive integers")
        if previous_n is not None and raw_n <= previous_n:
            raise ValueError("n_values must be strictly increasing")
        previous_n = raw_n
        n = raw_n
        ell_uv = math.exp(-(n**2))
        delta = n * ell_uv
        log_boundary = float(n**2)
        log_bound = collar_log_bound_from_log_boundary(
            log_boundary_size=log_boundary,
            collar_width_steps=float(n),
            constants=replace(constants, ell_uv=ell_uv),
        )
        stages.append(
            {
                "n": n,
                "ell_uv": ell_uv,
                "delta": delta,
                "delta_over_ell_uv": float(n),
                "log_boundary_size_uv": log_boundary,
                "sharp_geometric_margin": float(n - n**2),
                "log_cmi_envelope": log_bound,
            }
        )
    width_ratios = [stage["delta_over_ell_uv"] for stage in stages]
    margins = [stage["sharp_geometric_margin"] for stage in stages]
    log_bounds = [stage["log_cmi_envelope"] for stage in stages]
    return {
        "construction": {
            "ell_uv_n": "exp(-n^2)",
            "delta_n": "n*ell_uv_n",
            "boundary_size_uv_n": "exp(n^2)",
            "zeta": 1.0,
            "kappa": 1.0,
            "r0": 0.0,
        },
        "stages": stages,
        "finite_proxy_checks": {
            "delta_over_ell_uv_increases": all(
                left < right
                for left, right in zip(width_ratios, width_ratios[1:])
            ),
            "sharp_margin_strictly_decreases": all(
                left > right for left, right in zip(margins, margins[1:])
            ),
            "log_envelope_strictly_increases": all(
                left < right for left, right in zip(log_bounds, log_bounds[1:])
            ),
        },
        "analytic_limit": {
            "delta_over_ell_uv": "+infinity",
            "sharp_geometric_margin": "-infinity because n-n^2 -> -infinity",
            "cmi_envelope": "does not tend to zero (its log is n^2-n)",
            "conclusion": (
                "delta/ell_uv -> infinity alone does not force the declared "
                "CMI envelope to vanish when the UV boundary cardinality grows"
            ),
        },
    }


def build_report() -> dict:
    """Build the canonical issue-307 analytic finite-proxy report."""
    constants = FiniteRangeGibbsMixingConstants(
        ell_uv=1.0,
        beta=0.75,
        local_hilbert_dimension=2,
        coordination_number_bound=6,
        interaction_strength_bound=1.5,
        interaction_range_steps=2.0,
        mixing_prefactor_kappa=3.0,
        mixing_length_steps_zeta=1.25,
    )
    schedule = PowerLawBoundarySchedule(
        ell0=1.0,
        boundary_prefactor=4.0,
        boundary_power=2.0,
        eta=0.75,
    )
    schedule_receipt = sufficient_schedule_receipt(
        log_refinements=(4.0, 8.0, 12.0, 16.0, 20.0),
        constants=constants,
        schedule=schedule,
    )
    counterexample = counterexample_receipt()
    return {
        "artifact": "oph_collar_recoverability_analytic_finite_proxy",
        "object_id": "CollarRecoverabilityAnalyticFiniteProxy_Issue307",
        "issue": 307,
        "artifact_class": "analytic_finite_proxy",
        "claim_status": (
            "conditional_envelope_evaluator_not_empirical_evidence_"
            "and_not_theorem_promotion"
        ),
        "empirical_evidence": False,
        "promotes_theorem_status": False,
        "scope": (
            "finite log-domain evaluation of the collar CMI consequence of a "
            "declared uniform strong conditional/matrix-mixing envelope"
        ),
        "assumption_contract": {
            "finite_range_gibbs": {
                "state": "rho = exp(-beta*H)/Z, H = sum_X Phi_X",
                "finite_range": "diam(X) <= r0*ell_uv",
                "uniform_interaction_bound": (
                    "sup_x sum_{X containing x} ||Phi_X|| <= J"
                ),
                "finite_local_dimension_and_degree": True,
                "illustrative_finite_proxy_constants": asdict(constants),
            },
            "strong_conditional_matrix_mixing": {
                "status": "assumption_not_inferred_here_from_ordinary_clustering",
                "uniformity": (
                    "same kappa, r0, and zeta over caps and refinement stages"
                ),
                "envelope": (
                    "I(A_delta:D_delta|B_delta) <= kappa*|partial C|_UV*"
                    "exp(-(m-r0)/zeta)"
                ),
                "physical_form": (
                    "I <= c*|partial C|_UV*exp(-delta/xi), "
                    "xi=zeta*ell_uv, c=kappa*exp(r0/zeta)"
                ),
                "entropy_units": "nats",
            },
        },
        "stable_rate_contract": {
            "log_bound": (
                "log(kappa)+log(|partial C|_UV)-(m-r0)/zeta"
            ),
            "full_rate_margin": (
                "(m-r0)/zeta-log(kappa)-log(|partial C|_UV)"
            ),
            "sharp_fixed_constant_criterion": (
                "delta/xi-log(|partial C|_UV) -> +infinity"
            ),
            "meaning": (
                "the declared upper envelope tends to zero iff its full rate "
                "margin tends to +infinity"
            ),
        },
        "sufficient_power_law_schedule": schedule_receipt,
        "mere_width_ratio_counterexample": counterexample,
        "finite_receipt_proxies": [
            "log boundary cardinality",
            "collar width in regulator steps m=delta/ell_uv",
            "physical mixing length xi=zeta*ell_uv",
            "stable log CMI upper envelope",
            "full and sharp rate margins",
            "uniform fitted-or-proved kappa, r0, and zeta with provenance",
        ],
        "claim_boundary": {
            "certified_by_this_artifact": (
                "algebraic decay and schedule implications conditional on the "
                "stated uniform mixing envelope"
            ),
            "not_certified": [
                "the strong conditional/matrix-mixing envelope for an OPH state",
                "derivation of strong conditional mixing from ordinary two-point clustering",
                "empirical CMI decay",
                "EC/Markov-split alignment",
                "BW, Einstein, dark-sector, or other downstream branch entry",
            ],
            "safe_use": (
                "analytic finite proxy and falsifiable receipt schema only; no "
                "empirical or theorem promotion"
            ),
        },
    }


def main() -> None:
    report = build_report()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({
        "artifact": report["artifact"],
        "claim_status": report["claim_status"],
        "schedule_checks": report["sufficient_power_law_schedule"][
            "finite_proxy_checks"
        ],
        "counterexample_checks": report["mere_width_ratio_counterexample"][
            "finite_proxy_checks"
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
