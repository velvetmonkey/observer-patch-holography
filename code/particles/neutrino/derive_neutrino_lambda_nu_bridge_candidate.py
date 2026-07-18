#!/usr/bin/env python3
"""Record the sharpest current local bridge candidate for lambda_nu."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCALE_ANCHOR = ROOT / "particles" / "runs" / "neutrino" / "neutrino_scale_anchor.json"
COMPARE_FIT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_compare_only_scale_fit.json"
SCALAR_EVALUATOR = ROOT / "particles" / "runs" / "neutrino" / "majorana_overlap_defect_scalar_evaluator.json"
NORMALIZER = ROOT / "particles" / "runs" / "neutrino" / "same_label_overlap_defect_weight_normalizer.json"
THEOREM_OBJECT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_theorem_object.json"
IRREDUCIBILITY = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_irreducibility_theorem.json"
DEFECT_WEIGHTED_FAMILY = ROOT / "particles" / "runs" / "neutrino" / "defect_weighted_mu_e_family.json"
BRIDGE_SCALAR_CORRIDOR = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_bridge_scalar_corridor.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_lambda_nu_bridge_candidate.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(
    *,
    scale_anchor: dict[str, Any],
    compare_fit: dict[str, Any],
    scalar_evaluator: dict[str, Any],
    normalizer: dict[str, Any],
    theorem_object: dict[str, Any],
    irreducibility: dict[str, Any] | None,
    defect_weighted_family: dict[str, Any],
    bridge_scalar_corridor: dict[str, Any] | None,
) -> dict[str, Any]:
    m_star_eV = float(scale_anchor["anchors"]["m_star_gev"]) * 1.0e9
    lambda_cmp = float(compare_fit["fits"]["weighted_least_squares"]["lambda_nu"])
    bridge_factor = lambda_cmp / m_star_eV
    q_mean = float(normalizer["q_mean"])
    p_nu = float(theorem_object["live_inputs"]["p_nu"])
    q_mean_to_p = q_mean**p_nu
    residual_amplitude_ratio = lambda_cmp * q_mean_to_p / m_star_eV
    gamma = float(theorem_object["live_inputs"]["gamma"])
    ratio_hat = float(theorem_object["live_outputs"]["dimensionless_ratio_dm21_over_dm32"])
    lambda_closed_form = gamma / (ratio_hat ** 0.5)
    delta_hat = compare_fit["scale_free_branch"]["delta_hat_m_sq_eV2"]
    masses_hat = compare_fit["scale_free_branch"]["m_hat_eV"]
    residuals = {
        "21": (
            lambda_closed_form**2 * float(delta_hat["21"])
            - float(compare_fit["reference_central_values"]["delta_m21_sq_eV2"])
        )
        / float(compare_fit["reference_central_values"]["delta_m21_sq_sigma_eV2"]),
        "32": (
            lambda_closed_form**2 * float(delta_hat["32"])
            - float(compare_fit["reference_central_values"]["delta_m32_sq_eV2"])
        )
        / float(compare_fit["reference_central_values"]["delta_m32_sq_sigma_eV2"]),
    }
    phase_clause = scalar_evaluator["phase_cocycle_triviality_candidate_id"]
    smaller_clause = scalar_evaluator["strictly_smaller_missing_clause_if_not_closed"]
    bundle_clause = scalar_evaluator["bundle_descent_candidate_id"]
    normalizer_id = scalar_evaluator["attachment_normalizer_candidate_id"]
    bridge_invariant_id = "oph_neutrino_attachment_bridge_invariant"
    exact_smallest_object = None if irreducibility is None else irreducibility.get("reduced_remaining_object")
    scalar_theorem_id = scalar_evaluator.get("remaining_theorem_object") or scalar_evaluator["theorem_candidate_id"]
    mu_values = list(defect_weighted_family["edge_weights"].values())
    mu_mean = sum(mu_values) / len(mu_values)
    mu_spread = (
        sum((value - mu_mean) ** 2 for value in mu_values) / len(mu_values)
    ) ** 0.5
    max_min_ratio = max(mu_values) / min(mu_values)
    return {
        "artifact": "oph_neutrino_lambda_nu_bridge_candidate",
        "generated_utc": _timestamp(),
        "status": "candidate_interface_contract_corrected_not_promoted",
        "public_promotion_allowed": False,
        "current_dimensionless_theorem_object": None,
        "current_dimensionless_candidate_law": (theorem_object.get("candidate_law") or {}).get("name"),
        "weighted_cycle_base_status": theorem_object.get("status"),
        "weighted_cycle_prediction_promotion_allowed": theorem_object.get("prediction_promotion_allowed"),
        "dimensionful_anchor": {
            "name": "m_star",
            "formula": scale_anchor["anchors"]["m_star_formula"],
            "m_star_gev": scale_anchor["anchors"]["m_star_gev"],
            "m_star_eV": m_star_eV,
        },
        "current_candidate_interface_artifact": "oph_majorana_overlap_defect_scalar_evaluator",
        "closed_normalizer_artifact": normalizer.get("artifact"),
        "normalizer_status": normalizer.get("status"),
        "exact_next_theorem_object": "source_closed_neutrino_operator_basis_and_mass_label_contract",
        "conditional_absolute_scale_next_object": None if exact_smallest_object is None else exact_smallest_object.get("name"),
        "paper_facing_attachment_parameterization": bridge_invariant_id,
        "strictly_smaller_missing_clause": smaller_clause,
        "bridge_ansatz": "lambda_nu = (m_star_eV / q_mean^p_nu) * B_nu",
        "bridge_factor_schema": "B_nu = lambda_nu * q_mean^p_nu / m_star_eV",
        "residual_amplitude_parameterization": {
            "definition": "B_nu = lambda_nu * q_mean^p_nu / m_star_eV",
            "equivalent_amplitude": "A_nu = lambda_nu * q_mean^p_nu",
            "q_mean": q_mean,
            "p_nu": p_nu,
            "q_mean_to_p_nu": q_mean_to_p,
            "compare_only_B_nu_star": residual_amplitude_ratio,
        },
        "ruled_out_current_selected_point_scalar": {
            "status": "internal_to_declared_candidate_stack_not_the_missing_bridge_scalar",
            "name": "I_nu^(wc)",
            "definition": "I_nu^(wc) = 0.5 * sum_e qbar_e * |z_e(psi_wc) - 1|^2",
            "equivalent_if_edge_character_norm_closes": "I_nu^(wc) = sum_e qbar_e * (1 - cos(delta_psi_e))",
            "selected_point": "weighted_cycle_selector_psi_wc",
            "gate": phase_clause,
            "why_ruled_out": (
            "The declared candidate stack fixes qbar_e, psi_wc, and psi*, hence I_nu^(wc) is fixed on that conditional one-parameter positive amplitude orbit and cannot be the missing bridge-external scalar."
            ),
        },
        "where_B_nu_should_come_from": (
            "Only after a source-closed physical neutrino operator, basis, and mass-label contract exists could one seek a positive non-homogeneous attachment scalar fixing A_nu / m_star."
        ),
        "smallest_exact_missing_object": exact_smallest_object,
        "smaller_exact_object_above_emitted_proxy": (
            None if bridge_scalar_corridor is None else bridge_scalar_corridor.get("exact_reduced_correction_scalar")
        ),
        "best_constructive_subbridge_object": {
            "artifact": defect_weighted_family["artifact"],
            "status": defect_weighted_family["proof_status"],
            "role": "first supported spectrum-moving local object beneath the irreducible reduced correction scalar C_nu, equivalently beneath the paper-facing amplitude parameterization B_nu",
            "raw_edge_score_rule": defect_weighted_family["raw_edge_score_rule"],
            "centered_log_rule": defect_weighted_family["centered_log_rule"],
            "mu_family_rule": "mu_e = mu_nu * exp(eta_e) / mean_f(exp(eta_f))",
            "raw_edge_score": defect_weighted_family["raw_edge_score"],
            "edge_weights": defect_weighted_family["edge_weights"],
            "anisotropy_diagnostics": {
                "max_mu_over_min_mu": max_min_ratio,
                "sigma_mu_over_mean_mu": mu_spread / mu_mean,
            },
        },
        "current_attached_stack_collapse_status": (
            "refuted_by_attachment_irreducibility_theorem"
            if irreducibility is not None
            else "unresolved"
        ),
        "current_attached_stack_irreducibility_theorem": None if irreducibility is None else {
            "artifact": irreducibility.get("artifact"),
            "status": irreducibility.get("status"),
            "statement": irreducibility.get("theorem", {}).get("statement"),
        },
        "bridge_interface_theorem_stack": [
            {
                "id": normalizer_id,
                "status": normalizer.get("status", "candidate_only"),
                "role": "normalized same-label overlap-defect weight section computed conditionally from the source-open scalar certificate",
            },
            {
                "id": phase_clause,
                "status": scalar_evaluator["phase_cocycle_triviality_status"],
                "role": "same-label normalized-lift phase-cocycle theorem beneath the finite-angle scalar interface",
            },
            {
                "id": bundle_clause,
                "status": scalar_evaluator["bundle_descent_status"],
                "role": "closed selector-centered common-refinement edge-bundle descent theorem above the same-label phase-cocycle layer",
            },
            {
                "id": scalar_theorem_id,
                "status": scalar_evaluator["proof_status"],
                "role": "parent finite-angle centered edge-norm theorem furnishing the scalar side of the attachment route",
            },
            {
                "id": bridge_invariant_id,
                "status": "open",
                "role": "conditional positive attachment parameterization B_nu = lambda_nu * q_mean^p_nu / m_star_eV; inside the rejected candidate, the residual coordinate above the internal proxy is C_nu",
            },
            {
                "id": "neutrino_weighted_cycle_absolute_attachment",
                "status": "open",
                "role": "absolute-attachment theorem upgrading the weighted-cycle normal form to absolute masses and splittings",
            },
        ],
        "why_this_is_the_sharpest_local_candidate": [
            "The weighted-cycle law is a rejected source-open candidate, not a closed dimensionless theorem.",
            "The scale anchor closes only the isotropic dimensionful amplitude m_star.",
            "The scalar evaluator is a conditional local object at the interface between the source-open candidate and the D10 scale sector.",
        ],
        "compare_only_bridge_factor": {
            "lambda_nu_weighted_fit": lambda_cmp,
            "F_nu_star": bridge_factor,
            "interpretation": "This target-derived factor is a diagnostic coordinate on the rejected candidate branch.",
        },
        "compare_only_residual_amplitude_ratio": {
            "B_nu_star": residual_amplitude_ratio,
            "interpretation": "After exact q_mean^p_nu factorization, this is the size of the remaining compare-only non-homogeneous attachment scalar.",
        },
        "strongest_compare_only_bridge_scalar_corridor": (
            None
            if bridge_scalar_corridor is None
            else {
                "artifact": bridge_scalar_corridor.get("artifact"),
                "status": bridge_scalar_corridor.get("status"),
                "primary_cross_route_corridor": bridge_scalar_corridor.get("primary_cross_route_corridor"),
                "strongest_target_containing_bridge_scalar_corridor": bridge_scalar_corridor.get(
                    "strongest_target_containing_bridge_scalar_corridor"
                ),
                "shortlist_route_consensus_window": bridge_scalar_corridor.get("shortlist_route_consensus_window"),
                "bridge_correction_candidate_audit": bridge_scalar_corridor.get("bridge_correction_candidate_audit"),
                "top_candidate_envelope": {
                    "interval": (bridge_scalar_corridor.get("top_candidate_envelope") or {}).get("interval"),
                    "relative_half_width": (bridge_scalar_corridor.get("top_candidate_envelope") or {}).get(
                        "relative_half_width"
                    ),
                },
                "family_assisted_route": (
                    (bridge_scalar_corridor.get("primary_route_representatives") or [None, None, None])[2]
                ),
            }
        ),
        "target_free_closed_form_candidates": [
            {
                "name": "gamma_over_sqrt_ratio_hat",
                "status": "exactly_refuted_as_theorem_grade_absolute_scale_law",
                "formula": "lambda_nu = gamma / sqrt(Delta_hat_21 / Delta_hat_32)",
                "equivalent_statement": "Delta m21^2 = gamma^2 * Delta_hat_32",
                "lambda_nu": lambda_closed_form,
                "masses_eV": [lambda_closed_form * float(val) for val in masses_hat],
                "delta_m_sq_eV2": {
                    key: lambda_closed_form**2 * float(val) for key, val in delta_hat.items()
                },
                "residual_sigma": residuals,
                "proof_obstruction": "positive_rescaling_nonidentifiability",
                "why_refuted": (
                    "gamma and Delta_hat_21 / Delta_hat_32 are orbit invariants on the positive-rescaling family, so no theorem-grade absolute-scale law can be a function of those invariants alone."
                ),
            }
        ],
        "ruled_out_shortcuts": {
            "lambda_nu_equals_m_star_eV": {
                "status": "ruled_out",
                "source_artifact": "neutrino_weighted_cycle_absolute_amplitude_bridge.json",
            },
            "trace_determinant_minor_repackages_of_isotropic_majorana_matrix": {
                "status": "not_weighted_cycle_sensitive",
                "reason": "They reconstruct the isotropic amplitude sector again rather than the weighted-cycle branch attachment.",
            },
            "edge_amplitude_only_formulas": {
                "status": "ruled_out_local_shape_only",
                "reason": "Current edge-amplitude invariants are far too small and do not carry the required bridge factor.",
            },
        },
        "next_theorem_if_this_route_is_right": {
            "id": "source_closed_neutrino_operator_basis_and_mass_label_contract",
            "current_status": "open",
            "promotion_gate": None,
            "smallest_missing_clause": "derive_the_physical_operator_and_basis_before_absolute_attachment",
            "corrected_parameterization": "lambda_nu = (m_star_eV / q_mean^p_nu) * B_nu",
            "conditional_absolute_attachment_object": None if exact_smallest_object is None else exact_smallest_object.get("name"),
        },
        "notes": [
            "This bridge candidate does not emit lambda_nu.",
            "It packages a conditional interface between the D10 amplitude scale and the rejected weighted-cycle candidate law.",
            "The normalized overlap-defect weight section inherits a source-open scalar certificate; any one-scalar attachment statement is conditional on that rejected stack.",
            "Inside the conditional attached-stack algebra, the bridge factor cannot collapse to a qbar-only law and one positive coordinate remains external.",
            "The candidate qbar_e, psi_wc, and psi* data fix the selected-point scalar I_nu^(wc), so it cannot be an independent bridge-external scalar.",
            "The strongest constructive local object beneath that bridge is the defect-weighted same-label edge family q_e = sqrt(g_e * d_e); its real, sizable mu_e anisotropy does not emit the final bridge scalar.",
            "The narrowest compare-only B_nu result is a cross-route corridor combining the symmetric-normalizer, core-residual, and defect-assisted residual routes.",
            "Relative to the best emitted residual-amplitude proxy sqrt(I_nu * ratio_hat) / sum_defect, the remaining exact bridge can also be written as a near-unity positive correction scalar C_nu on the live branch.",
            "C_nu is only the smallest missing coordinate inside the conditional absolute-scale subproblem. The first physical missing object is the source-closed operator, basis, charged-basis, and mass-label contract.",
            "Direct auditing of C_nu yields the narrowest measured-reference induced B_nu corridor, but that result remains compare-only.",
            "A stricter shortlist-consensus window inside the admitted route families remains a route-agreement diagnostic rather than an emitted law.",
            "The exact remaining scalar is better parameterized as B_nu := lambda_nu * q_mean^p_nu / m_star_eV, equivalently A_nu / m_star_eV.",
            "The closed-form gamma-over-sqrt-ratio numerology is retained only as a refuted compare-only audit target; it is incompatible with the exact positive-rescaling no-go.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the neutrino lambda_nu bridge candidate artifact.")
    parser.add_argument("--scale-anchor", default=str(SCALE_ANCHOR))
    parser.add_argument("--compare-fit", default=str(COMPARE_FIT))
    parser.add_argument("--scalar-evaluator", default=str(SCALAR_EVALUATOR))
    parser.add_argument("--normalizer", default=str(NORMALIZER))
    parser.add_argument("--theorem-object", default=str(THEOREM_OBJECT))
    parser.add_argument("--irreducibility", default=str(IRREDUCIBILITY))
    parser.add_argument("--defect-weighted-family", default=str(DEFECT_WEIGHTED_FAMILY))
    parser.add_argument("--bridge-scalar-corridor", default=str(BRIDGE_SCALAR_CORRIDOR))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(
        scale_anchor=_load_json(Path(args.scale_anchor)),
        compare_fit=_load_json(Path(args.compare_fit)),
        scalar_evaluator=_load_json(Path(args.scalar_evaluator)),
        normalizer=_load_json(Path(args.normalizer)),
        theorem_object=_load_json(Path(args.theorem_object)),
        irreducibility=_load_json(Path(args.irreducibility)) if Path(args.irreducibility).exists() else None,
        defect_weighted_family=_load_json(Path(args.defect_weighted_family)),
        bridge_scalar_corridor=_load_json(Path(args.bridge_scalar_corridor)) if Path(args.bridge_scalar_corridor).exists() else None,
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
