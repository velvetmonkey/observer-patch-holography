#!/usr/bin/env python3
"""Emit a conditional bridge-correction reparameterization for the rejected candidate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
IRREDUCIBILITY_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_irreducibility_theorem.json"
CORRECTION_AUDIT_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_bridge_correction_candidate_audit.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_bridge_correction_invariant_scaffold.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(
    *,
    irreducibility: dict[str, Any],
    correction_audit: dict[str, Any],
) -> dict[str, Any]:
    reduced = dict(irreducibility["reduced_remaining_object"])
    proxy = dict(irreducibility["internal_positive_proxy_object"])
    correction_window = dict(correction_audit["primary_target_containing_correction_window"])
    induced_bridge_window = dict(correction_audit["induced_target_containing_bridge_scalar_window"])
    return {
        "artifact": "oph_neutrino_bridge_correction_invariant_scaffold",
        "generated_utc": _timestamp(),
        "status": "conditional_exact_reparameterization_on_rejected_candidate",
        "proof_grade": "exact_proxy_relative_reduction_conditional_on_declared_candidate",
        "public_promotion_allowed": False,
        "exact_missing_object": "source_closed_neutrino_operator_basis_and_mass_label_contract",
        "conditional_absolute_scale_missing_object": "oph_neutrino_bridge_correction_invariant",
        "conditional_parent_missing_object": "oph_neutrino_attachment_bridge_invariant",
        "residual_invariant_symbol": "C_nu",
        "parent_bridge_scalar_symbol": "B_nu",
        "current_attached_stack_irreducibility_theorem": {
            "artifact": irreducibility.get("artifact"),
            "status": irreducibility.get("status"),
            "reduced_sharpened_conclusion": irreducibility.get("theorem", {}).get("reduced_sharpened_conclusion"),
        },
        "internal_positive_proxy_object": proxy,
        "exact_reduction_theorem": {
            "definition": reduced.get("definition"),
            "bridge_reconstruction": reduced.get("bridge_reconstruction"),
            "equivalence_theorem": reduced.get("equivalence_theorem"),
            "exact_residual_moduli_space": reduced.get("exact_residual_moduli_space"),
        },
        "strongest_locally_justified_exact_theorem": {
            "name": "conditional_proxy_relative_single_coordinate_reduction",
            "statement": (
                "Inside the rejected weighted-cycle candidate, once the internal positive proxy P_nu is fixed, "
                "the conditional absolute-scale quotient is one positive coordinate C_nu. This is an exact "
                "reparameterization of that candidate only; it does not close a physical neutrino branch."
            ),
            "scope": "rejected_weighted_cycle_candidate_with_fixed_internal_positive_proxy",
            "exact_residual_moduli_space": reduced.get("exact_residual_moduli_space"),
            "equivalent_parent_object": {
                "artifact": "oph_neutrino_attachment_bridge_invariant",
                "symbol": "B_nu",
                "bridge_reconstruction": reduced.get("bridge_reconstruction"),
            },
            "local_justification": [
                "The conditional attachment algebra leaves one positive residual orbit on the declared candidate stack.",
                "The chosen proxy P_nu is internal to that candidate stack and strictly positive at the stored point.",
                "Dividing by P_nu is therefore an exact reparameterization of the same conditional orbit, not a physical theorem.",
            ],
            "non_claims": [
                "no_numeric_value_for_C_nu_is_emitted",
                "no_compare_only_window_or_proxy_search_is_promoted",
                "no_hidden_full_closure_of_the_absolute_scale_is_claimed",
            ],
        },
        "contract": {
            "must_emit": "a source-closed neutrino operator, physical basis placement, charged basis, and mass-label rule",
            "conditional_absolute_scale_must_emit": "one positive reduced bridge-correction scalar C_nu or an exactly equivalent reduced attachment invariant",
            "must_imply": [
                reduced.get("bridge_reconstruction"),
                f"lambda_nu = (m_star_eV / q_mean^p_nu) * ({proxy['formula']}) * C_nu",
            ],
            "must_not_use": [
                "external_oscillation_anchors",
                "PDG_target_backsolve",
                "PMNS_target_seed",
            ],
        },
        "strongest_compare_only_correction_window": correction_window,
        "induced_target_containing_bridge_scalar_window": induced_bridge_window,
        "notes": [
            "Inside the rejected candidate, factoring out P_nu leaves a smaller one-coordinate absolute-scale diagnostic.",
            "The first physical theorem burden remains the source-closed operator, basis, charged-basis, and mass-label contract, not C_nu.",
            "The correction window and its induced B_nu window are compare-only diagnostics and must not be promoted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the reduced neutrino bridge-correction scaffold.")
    parser.add_argument("--irreducibility", default=str(IRREDUCIBILITY_JSON))
    parser.add_argument("--correction-audit", default=str(CORRECTION_AUDIT_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(
        irreducibility=_load_json(Path(args.irreducibility)),
        correction_audit=_load_json(Path(args.correction_audit)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
