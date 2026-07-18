#!/usr/bin/env python3
"""Emit a conditional residual bridge-invariant diagnostic for the rejected candidate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
NORMALIZER = ROOT / "particles" / "runs" / "neutrino" / "same_label_overlap_defect_weight_normalizer.json"
BRIDGE_CANDIDATE = ROOT / "particles" / "runs" / "neutrino" / "neutrino_lambda_nu_bridge_candidate.json"
IRREDUCIBILITY = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_irreducibility_theorem.json"
DEFECT_WEIGHTED_FAMILY = ROOT / "particles" / "runs" / "neutrino" / "defect_weighted_mu_e_family.json"
BRIDGE_SCALAR_CORRIDOR = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_bridge_scalar_corridor.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_bridge_invariant_scaffold.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(
    normalizer: dict[str, Any],
    bridge_candidate: dict[str, Any],
    irreducibility: dict[str, Any] | None,
    defect_weighted_family: dict[str, Any],
    bridge_scalar_corridor: dict[str, Any] | None,
) -> dict[str, Any]:
    smaller_gate = bridge_candidate.get("strictly_smaller_missing_clause")
    return {
        "artifact": "oph_neutrino_attachment_bridge_invariant_scaffold",
        "generated_utc": _timestamp(),
        "status": "diagnostic_attachment_scaffold_on_rejected_candidate",
        "public_promotion_allowed": False,
        "exact_missing_object": "source_closed_neutrino_operator_basis_and_mass_label_contract",
        "conditional_absolute_attachment_missing_object": "oph_neutrino_attachment_bridge_invariant",
        "conditional_lower_object": normalizer.get("artifact"),
        "conditional_lower_object_status": normalizer.get("status"),
        "bridge_factor_schema": bridge_candidate.get("bridge_factor_schema"),
        "residual_invariant_symbol": "B_nu",
        "exact_residual_moduli_space": "R_{>0}",
        "no_hidden_discrete_branch": False,
        "one_additional_positive_bridge_invariant_is_necessary_and_sufficient": False,
        "immediate_theorem_gate": smaller_gate,
        "contract": {
            "must_emit": "a source-closed neutrino operator, physical basis placement, charged basis, and mass-label rule before any residual attachment scalar is considered",
            "must_imply": "lambda_nu = (m_star_eV / q_mean^p_nu) * B_nu",
            "must_not_use": [
                "external_oscillation_anchors",
                "PDG_target_backsolve",
                "PMNS_target_seed",
            ],
        },
        "ruled_out_current_selected_point_scalar": {
            "status": "internal_to_declared_candidate_stack_not_the_missing_bridge_scalar",
            "definition": "I_nu^(wc) = 0.5 * sum_e qbar_e * |z_e(psi_wc) - 1|^2",
            "equivalent_if_edge_character_norm_closes": "I_nu^(wc) = sum_e qbar_e * (1 - cos(delta_psi_e))",
            "selected_point": "weighted_cycle_selector_psi_wc",
            "gate": bridge_candidate["bridge_interface_theorem_stack"][1]["id"],
            "type": "positive_dimensionless_scalar",
            "why_ruled_out": (
                "The candidate qbar_e, psi_wc, and psi* data fix the selected-point scalar, so it cannot be an independent bridge-external scalar."
            ),
        },
        "qbar_only_collapse_status": (
            "refuted_on_current_attached_stack_by_attachment_irreducibility_theorem"
            if irreducibility is not None
            else "unresolved_on_current_attached_stack"
        ),
        "collapse_alternative": (
            "neither a qbar-only collapse nor a selected-point scalar collapse is derivable from the declared attached stack; closure requires one positive non-homogeneous bridge scalar or an exactly equivalent theorem"
            if irreducibility is not None
            else "prove_the_residual_bridge_scalar_is_internal_to_the_present_stack"
        ),
        "current_attached_stack_irreducibility_theorem": None if irreducibility is None else {
            "artifact": irreducibility.get("artifact"),
            "status": irreducibility.get("status"),
            "sharpened_conclusion": irreducibility.get("theorem", {}).get("sharpened_conclusion"),
        },
        "best_constructive_subbridge_object": {
            "artifact": defect_weighted_family["artifact"],
            "status": defect_weighted_family["proof_status"],
            "role": "first supported spectrum-moving local object beneath the irreducible bridge scalar B_nu",
            "raw_edge_score_rule": defect_weighted_family["raw_edge_score_rule"],
            "mu_family_rule": "mu_e = mu_nu * exp(eta_e) / mean_f(exp(eta_f))",
        },
        "smallest_exact_missing_object": {
            "name": "source_closed_neutrino_operator_basis_and_mass_label_contract",
            "status": "open",
        },
        "conditional_absolute_attachment_object": (
            None if irreducibility is None else irreducibility.get("reduced_remaining_object")
        ),
        "smaller_exact_object_above_emitted_proxy": (
            None
            if bridge_scalar_corridor is None
            else bridge_scalar_corridor.get("exact_reduced_correction_scalar")
        ),
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
            }
        ),
        "residual_attachment_quotient_theorem": (
            "Conditional on fixing the rejected weighted-cycle coordinates, their PMNS-like readout, "
            "scale-free masses/splittings, the D10 amplitude anchor m_star, and the source-open normalized "
            "same-label overlap-defect weight section qbar_e, the candidate absolute family is algebraically "
            "m_i = lambda_nu * mhat_i and Delta m^2_ij = lambda_nu^2 * Delta_hat_ij with lambda_nu > 0. "
            "Equivalently, inside that conditional ansatz the residual non-homogeneous attachment scalar can be "
            "parameterized as B_nu = lambda_nu * q_mean^p_nu / m_star_eV. This quotient identity does not close a physical PMNS branch."
        ),
        "notes": [
            "The normalized same-label overlap-defect weight section inherits source-open inputs.",
            "This scaffold isolates a conditional positive scalar quotient inside the rejected candidate.",
            "One-dimensionality of that conditional quotient does not establish a physical branch or exclude missing discrete operator, basis, or mass-label choices.",
            "The conditional attached-stack algebra does not collapse the bridge factor to a qbar-only law.",
            "The selected-point scalar I_nu^(wc) is diagnostic-only because the candidate stack fixes it.",
            "The defect-weighted same-label edge family is numerically complete but inherits source-open flavor inputs.",
            "Factoring through the internal candidate proxy exposes a conditional correction scalar C_nu for debugging only.",
            "The first physical missing object is the source-closed operator, basis, charged-basis, and mass-label contract, not C_nu.",
            "Direct C_nu auditing gives the narrowest measured-reference B_nu window; it remains compare-only and does not collapse the irreducibility theorem.",
            "The shortlist-consensus window is a target-informed route-agreement diagnostic and has no theorem status.",
            "The exact remaining scalar is better parameterized as B_nu := lambda_nu * q_mean^p_nu / m_star_eV, equivalently A_nu / m_star_eV.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the neutrino attachment bridge-invariant scaffold.")
    parser.add_argument("--normalizer", default=str(NORMALIZER))
    parser.add_argument("--bridge-candidate", default=str(BRIDGE_CANDIDATE))
    parser.add_argument("--irreducibility", default=str(IRREDUCIBILITY))
    parser.add_argument("--defect-weighted-family", default=str(DEFECT_WEIGHTED_FAMILY))
    parser.add_argument("--bridge-scalar-corridor", default=str(BRIDGE_SCALAR_CORRIDOR))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(
        normalizer=_load_json(Path(args.normalizer)),
        bridge_candidate=_load_json(Path(args.bridge_candidate)),
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
