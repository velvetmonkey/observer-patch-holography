#!/usr/bin/env python3
"""Emit the legacy conditional neutrino absolute-attachment scaffold.

This does not emit ``lambda_nu``. The one-scalar quotient is meaningful only
inside the rejected weighted-cycle candidate. The physical lane is blocked
earlier by the source-open neutrino operator, charged basis, and mass-label rule.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_absolute_amplitude_bridge.json"
BRIDGE_CANDIDATE_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_lambda_nu_bridge_candidate.json"
THEOREM_OBJECT_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_theorem_object.json"
BRIDGE_SCALAR_CORRIDOR_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_bridge_scalar_corridor.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_absolute_attachment_scaffold.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(
    bridge: dict[str, Any],
    bridge_candidate: dict[str, Any],
    theorem_object: dict[str, Any],
    bridge_scalar_corridor: dict[str, Any] | None,
) -> dict[str, Any]:
    diagnostic = dict(bridge["direct_scale_anchor_attachment_diagnostic"])
    candidate_law = dict(theorem_object.get("candidate_law") or theorem_object.get("theorem_object") or {})
    return {
        "artifact": "oph_neutrino_absolute_attachment_scaffold",
        "generated_utc": _timestamp(),
        "status": "superseded_conditional_absolute_scale_scaffold",
        "public_promotion_allowed": False,
        "exact_missing_object": "source_closed_neutrino_operator_basis_and_mass_label_contract",
        "conditional_candidate_missing_object": "neutrino_weighted_cycle_absolute_attachment",
        "equivalent_scalar": {
            "name": "lambda_nu",
            "meaning": "positive absolute normalization scalar for the weighted-cycle scale-free normal form",
        },
        "current_no_go": {
            "statement": bridge["no_go_statement"],
            "direct_attachment_diagnostic": diagnostic,
            "current_candidate_interface_artifact": bridge_candidate.get("current_candidate_interface_artifact"),
            "closed_normalizer_artifact": bridge_candidate.get("closed_normalizer_artifact"),
            "normalizer_status": bridge_candidate.get("normalizer_status"),
            "exact_next_theorem_object": bridge_candidate.get("exact_next_theorem_object"),
            "conditional_absolute_scale_next_object": bridge_candidate.get("conditional_absolute_scale_next_object"),
            "strictly_smaller_missing_clause": bridge_candidate.get("strictly_smaller_missing_clause"),
            "exact_residual_moduli_space": "R_{>0}",
            "one_additional_positive_bridge_invariant_is_necessary_and_sufficient": False,
            "conditional_candidate_absolute_scale_is_one_dimensional": True,
            "corrected_bridge_parameterization": bridge_candidate.get("bridge_ansatz"),
            "residual_amplitude_parameterization": bridge_candidate.get("residual_amplitude_parameterization"),
            "smaller_exact_object_above_emitted_proxy": (
                None if bridge_scalar_corridor is None else bridge_scalar_corridor.get("exact_reduced_correction_scalar")
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
        },
        "extension_contract": {
            "scope": "conditional_only_after_source_closed_physical_operator_basis_and_label_contract",
            "input_objects": [
                "oph_neutrino_weighted_cycle_theorem_object",
                "oph_neutrino_scale_anchor",
                "oph_neutrino_family_response",
                "oph_forward_majorana_matrix",
            ],
            "forbidden_inputs": [
                "external_oscillation_anchors",
                "PDG_target_backsolve",
                "PMNS_target_seed",
            ],
            "must_emit": "lambda_nu > 0 or an exactly equivalent amplitude attachment A_nu",
            "must_imply": [
                "m_i = lambda_nu * mhat_i",
                "Delta m^2_ij = lambda_nu^2 * Delta_hat_ij",
            ],
            "bridge_statement": (
                "Attach the internal D10 amplitude sector to the weighted-cycle scale-free normal "
                "form without reusing external oscillation anchors."
            ),
            "current_theorem_stack": bridge_candidate.get("bridge_interface_theorem_stack", []),
        },
        "theorem_object_context": {
            "status": theorem_object.get("status"),
            "theorem_status": theorem_object.get("theorem_status"),
            "name": candidate_law.get("name"),
            "D_nu_formula": candidate_law.get("D_nu_formula"),
            "p_nu_formula": candidate_law.get("p_nu_formula"),
        },
        "notes": [
            "Within the rejected candidate algebra, the residual absolute ambiguity is a positive rescaling orbit; this is not a statement that the physical neutrino lane is otherwise closed.",
            "Relative to the candidate residual-amplitude proxy, a near-unity correction scalar C_nu can be tracked for debugging only.",
            "Direct C_nu auditing yields a narrower measured-reference induced B_nu window than the old direct bridge corridor, but it remains compare-only and cannot be promoted.",
            "The first physical missing object is the source-closed operator, basis, charged-basis, and mass-label contract; an absolute-scale theorem is downstream of that gate.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the neutrino absolute-attachment scaffold.")
    parser.add_argument("--bridge", type=Path, default=BRIDGE_JSON)
    parser.add_argument("--bridge-candidate", type=Path, default=BRIDGE_CANDIDATE_JSON)
    parser.add_argument("--theorem-object", type=Path, default=THEOREM_OBJECT_JSON)
    parser.add_argument("--bridge-scalar-corridor", type=Path, default=BRIDGE_SCALAR_CORRIDOR_JSON)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    bridge = _load_json(args.bridge)
    bridge_candidate = _load_json(args.bridge_candidate)
    theorem_object = _load_json(args.theorem_object)
    bridge_scalar_corridor = _load_json(args.bridge_scalar_corridor) if args.bridge_scalar_corridor.exists() else None
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(build_artifact(bridge, bridge_candidate, theorem_object, bridge_scalar_corridor), indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
