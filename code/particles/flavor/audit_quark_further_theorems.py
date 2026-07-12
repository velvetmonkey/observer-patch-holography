#!/usr/bin/env python3
"""Audit the further-theorem/QFRC packet without promoting its physical ansatz.

The retained mathematics is deliberately split into exact no-go results and
conditional certificate arithmetic.  In particular, enumerating a primitive
path table is not evidence that an OPH carrier realizes that table.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
from typing import Any

import mpmath as mp


CODE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    CODE_ROOT / "particles" / "runs" / "flavor" / "quark_further_theorem_audit.json"
)
SUBMITTED_BUNDLE_SHA256 = "e43ee9972c2560f03b0b610e50ad71271bf6417f6f21a15446d70e19379e9c36"


def _moments(probabilities: list[Fraction]) -> dict[str, Fraction]:
    support = [-2, -1, 0, 1, 2]
    mean = sum((p * x for p, x in zip(probabilities, support)), Fraction())
    centered = [Fraction(x) - mean for x in support]
    mu2 = sum((p * x**2 for p, x in zip(probabilities, centered)), Fraction())
    mu4 = sum((p * x**4 for p, x in zip(probabilities, centered)), Fraction())
    return {"mean": mean, "variance": mu2, "fourth_cumulant": mu4 - 3 * mu2**2}


def _finite_maxent_witness() -> dict[str, Any]:
    """Solve the symmetric finite-spectrum MaxEnt law with variance one."""

    mp.mp.dps = 70
    support = [mp.mpf(-2), mp.mpf(-1), mp.mpf(0), mp.mpf(1), mp.mpf(2)]

    def probabilities(lam: mp.mpf) -> list[mp.mpf]:
        weights = [mp.exp(lam * x * x) for x in support]
        total = mp.fsum(weights)
        return [weight / total for weight in weights]

    def variance(lam: mp.mpf) -> mp.mpf:
        return mp.fsum(p * x * x for p, x in zip(probabilities(lam), support))

    lam = mp.findroot(lambda value: variance(value) - 1, (-2, 0))
    probs = probabilities(lam)
    mu4 = mp.fsum(p * x**4 for p, x in zip(probs, support))
    kappa4 = mu4 - 3
    if abs(variance(lam) - 1) > mp.mpf("1e-50") or abs(kappa4) < mp.mpf("1e-20"):
        raise AssertionError("finite-MaxEnt witness failed")
    return {
        "support": [-2, -1, 0, 1, 2],
        "lagrange_multiplier_x2": mp.nstr(lam, 40),
        "probabilities": [mp.nstr(value, 40) for value in probs],
        "variance": mp.nstr(variance(lam), 30),
        "fourth_cumulant": mp.nstr(kappa4, 30),
    }


def build_artifact() -> dict[str, Any]:
    distribution_a = [
        Fraction(1, 12), Fraction(1, 6), Fraction(1, 2), Fraction(1, 6), Fraction(1, 12)
    ]
    distribution_b = [
        Fraction(1, 16), Fraction(1, 4), Fraction(3, 8), Fraction(1, 4), Fraction(1, 16)
    ]
    moments_a = _moments(distribution_a)
    moments_b = _moments(distribution_b)
    if moments_a["mean"] != moments_b["mean"] or moments_a["variance"] != moments_b["variance"]:
        raise AssertionError("countermodels do not share the first two moments")
    if moments_a["fourth_cumulant"] == moments_b["fourth_cumulant"]:
        raise AssertionError("countermodels do not separate the fourth cumulant")

    dimensions = {
        "C_tensor_F": 3 * 5,
        "M_mu_up": 5**2 + 4,
        "M_mu_down": 24 * 6 * 3,
        "M_a_up": 2 * (5 + 6),
        "M_a_down_linear": 24 + 2 * 4,
        "M_a_down_quadratic": 24 * (3 + 4) * 5,
        "M_g_common": 24 * 6 * (3 + 4),
        "M_g_color": 24 * 6 * 3,
        "M_g_relabel": 24 * 6 * (5 + 6),
        "M_even_up": 2 * 5,
        "M_even_down": 4,
    }
    weights = {
        "heat_family_return": Fraction(-1, 5),
        "common_color_centered_exposure": Fraction(4, dimensions["C_tensor_F"]),
        "up_mean_quadratic": Fraction(1, dimensions["M_mu_up"]),
        "down_mean_quadratic": Fraction(-1, dimensions["M_mu_down"]),
        "up_endpoint_centered": Fraction(4, 5),
        "up_endpoint_quadratic": Fraction(1, dimensions["M_a_up"]),
        "down_endpoint_linear": Fraction(1, dimensions["M_a_down_linear"]),
        "down_endpoint_quadratic": Fraction(2, dimensions["M_a_down_quadratic"]),
        "up_even": Fraction(-1, dimensions["M_even_up"]),
        "down_even": Fraction(-1, dimensions["M_even_down"]),
        "scale_common": Fraction(1, dimensions["M_g_common"]),
        "scale_color": Fraction(1, dimensions["M_g_color"]),
        "scale_relabel": Fraction(-1, dimensions["M_g_relabel"]),
    }

    return {
        "artifact": "oph_quark_further_theorem_audit_v1",
        "submitted_bundle_sha256": SUBMITTED_BUNDLE_SHA256,
        "promotion_allowed": False,
        "exact_results_retained": {
            "finite_maxent_non_gaussianity": {
                "status": "exact_counterexample_and_finite_variational_form",
                "statement": (
                    "On a finite spectrum, MaxEnt subject to first and second moments has an "
                    "exponential-quadratic Gibbs law; it is not thereby a Gaussian density."
                ),
                "same_mean_variance_countermodels": {
                    "support": [-2, -1, 0, 1, 2],
                    "distribution_a": [str(value) for value in distribution_a],
                    "distribution_b": [str(value) for value in distribution_b],
                    "mean": str(moments_a["mean"]),
                    "variance": str(moments_a["variance"]),
                    "fourth_cumulant_a": str(moments_a["fourth_cumulant"]),
                    "fourth_cumulant_b": str(moments_b["fourth_cumulant"]),
                },
                "finite_maxent_witness": _finite_maxent_witness(),
                "effect_on_rscc": (
                    "The former finite-MaxEnt-to-Gaussian justification is false. An exact "
                    "primitive-path closure or a proved refinement CLT is required instead."
                ),
            },
            "selector_boundary": {
                "status": "exact_general_theorems",
                "equivariant_obstruction": (
                    "An equivariant section requires a stabilizer-fixed point in each orbit fiber."
                ),
                "positive_gap_selector": (
                    "A complete finite invariant candidate class with a unique positive-gap "
                    "minimizer remains unique under sup-norm cost errors smaller than half the gap."
                ),
                "physical_selector_present": False,
            },
            "scale_and_scheme_no_go": {
                "status": "exact_structural_obstructions",
                "absolute_scale": (
                    "Dimensionless source data are invariant under a common positive rescaling and "
                    "cannot select GeV values without an operational dimensionful receipt."
                ),
                "renormalization_scheme": (
                    "Running quark masses are scheme coordinates; a convention-labelled sextet "
                    "requires frozen beta functions, thresholds, matching, and endpoint definitions."
                ),
            },
        },
        "qfrc_conditional_rigidity": {
            "status": "exact_arithmetic_given_postulated_QF1_to_QF9",
            "typed_register_dimensions": dimensions,
            "primitive_path_weights": {name: str(value) for name, value in weights.items()},
            "what_is_forced": (
                "Normalized trace fixes rank/dimension weights once the typed registers, exact "
                "projectors, multiplicities, signs, winding, and exhaustive primitive paths are supplied."
            ),
            "what_is_not_forced": (
                "The present OPH axioms do not select that register ledger, path catalogue, ranks, "
                "signs, winding character, exhaustion statement, or positive-gap winner."
            ),
            "physical_QF1_to_QF9_certificate_present": False,
            "neutral_register_nonuniqueness": {
                "status": "valid_model_independence_boundary_for_the_broad_signature",
                "scope": (
                    "Changing an otherwise unobserved finite register dimension preserves the broad "
                    "structural signature while changing normalized coefficients. This does not by "
                    "itself construct a realization of every stronger OPH carrier condition."
                ),
            },
        },
        "conditional_routes": {
            "refinement_gaussianization": {
                "status": "not_instantiated",
                "requires": [
                    "exported triangular array or controlled dependent increments",
                    "Lindeberg or adequate mixing/bounded-dependency bounds",
                    "covariance convergence and normalization",
                ],
            },
            "source_root": {
                "status": "schema_only_no_actual_map_or_interval_inclusion",
                "requires": "target-free map plus strict interval-Newton or Krawczyk inclusion",
            },
            "rg_transport": {
                "status": "standard_conditional_well_posedness_only",
                "requires": "frozen locally-Lipschitz beta/matching packet and non-blowup domain",
            },
        },
        "standard_theorem_surfaces": {
            "one_higgs_singular_values": {
                "status": "standard_exact_given_canonical_kinetic_terms",
                "statement": (
                    "For one Higgs doublet and canonically normalized quark fields, the "
                    "mass eigenvalues at a common scale are v/sqrt(2) times the singular "
                    "values of the corresponding Yukawa matrix."
                ),
                "source_yukawa_packet_present": False,
            },
            "own_scale_and_pole_roots": {
                "status": "conditional_local_uniqueness",
                "statement": (
                    "A simple own-scale or complex-pole root is locally unique by the "
                    "implicit-function theorem after the running self-energy packet is fixed."
                ),
                "physical_root_packet_present": False,
            },
            "family_label_stability": {
                "status": "exact_given_positive_spectral_gap",
                "statement": (
                    "A continuous Hermitian family with a uniform positive eigenvalue gap has "
                    "continuous ordered spectral projectors and no label crossing."
                ),
                "source_gap_certificate_present": False,
            },
            "hash_freeze": {
                "status": "integrity_theorem_not_evidence_upgrade",
                "statement": (
                    "A collision-resistant pre-release commitment detects later mutation, but "
                    "a hash made after target-exposed discovery cannot make the packet prospective."
                ),
            },
        },
        "closure_effect": {
            "all_F1_to_F6_receipts_remain_open": True,
            "current_repository_emits_physical_quark_sextet": False,
            "numeric_quark_prediction_rows_allowed": False,
            "strongest_valid_implication": (
                "OPH structural branch plus a physical QFRC certificate, a target-free source root, "
                "an operational scale, and a frozen RG/mass-definition packet would determine a "
                "unique convention-labelled sextet. Those physical certificates are not supplied."
            ),
        },
        "historical_status": (
            "The RSCC/QFRC packet follows target-exposed formula discovery and is not prospective evidence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    payload = build_artifact()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    if args.print_json:
        print(text, end="")
    else:
        print(f"saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
