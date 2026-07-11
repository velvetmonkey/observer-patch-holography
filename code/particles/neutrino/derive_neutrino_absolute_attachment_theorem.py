#!/usr/bin/env python3
"""Audit the historical absolute neutrino attachment candidate artifact.

Chain role: preserve the historical absolute family as a compare-only
coordinate while enforcing transitive source and non-circularity gates.

Mathematics:
1. The bridge artifact supplies a candidate C_nu coordinate.
2. The internal candidate proxy P_nu reconstructs B_nu = P_nu * C_nu.
3. Conditional bridge coordinates reconstruct lambda_nu and therefore candidate absolute
   masses and absolute splittings from the scale-free weighted-cycle family.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_RIGIDITY_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_bridge_rigidity_theorem.json"
WEIGHTED_CYCLE_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"
ATTACHMENT_IRREDUCIBILITY_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_irreducibility_theorem.json"
ABSOLUTE_ATTACHMENT_SCAFFOLD_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_absolute_attachment_scaffold.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_absolute_attachment_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(
    bridge_rigidity: dict[str, Any],
    weighted_cycle: dict[str, Any],
    irreducibility: dict[str, Any],
    scaffold: dict[str, Any],
) -> dict[str, Any]:
    bridge_non_circularity = dict(bridge_rigidity.get("non_circularity_status") or {})
    weighted_cycle_eligible = (
        weighted_cycle.get("source_only_prediction_eligible") is True
        and weighted_cycle.get("prediction_promotion_allowed") is True
        and weighted_cycle.get("historical_target_exposure") is False
        and (weighted_cycle.get("source_closure_status") or {}).get("closed") is True
    )
    bridge_promotion_allowed = (
        weighted_cycle_eligible
        and
        bridge_rigidity.get("status") == "theorem_grade_emitted"
        and bridge_rigidity.get("public_surface_candidate_allowed") is True
        and bridge_non_circularity.get("promotion_allowed", False) is True
    )
    c_nu = float(
        bridge_rigidity["emitted_value"]
        if bridge_rigidity.get("emitted_value") is not None
        else bridge_rigidity["display_value"]
    )
    p_nu = float(bridge_rigidity["emitted_proxy"]["value"])
    b_nu = p_nu * c_nu
    m_star_eV = float(scaffold["current_no_go"]["direct_attachment_diagnostic"]["m_star_eV"])
    q_mean_to_p_nu = float(
        irreducibility["current_attached_stack_summary"].get(
            "q_mean_to_p",
            scaffold["current_no_go"]["residual_amplitude_parameterization"]["q_mean_to_p_nu"],
        )
    )
    p_nu_exponent = float(scaffold["current_no_go"]["residual_amplitude_parameterization"]["p_nu"])
    q_mean = float(scaffold["current_no_go"]["residual_amplitude_parameterization"]["q_mean"])
    lambda_nu = (m_star_eV / q_mean_to_p_nu) * b_nu

    dimensionless_masses = [float(x) for x in weighted_cycle["dimensionless_masses"]]
    dimensionless_dm2 = {key: float(value) for key, value in weighted_cycle["dimensionless_dm2"].items()}
    masses_eV = [lambda_nu * value for value in dimensionless_masses]
    delta_m_sq_eV2 = {key: (lambda_nu * lambda_nu) * value for key, value in dimensionless_dm2.items()}
    status = (
        "theorem_grade_emitted"
        if bridge_promotion_allowed
        else "conditional_absolute_family_blocked_by_compare_only_C_nu"
    )

    return {
        "artifact": "oph_neutrino_absolute_attachment_theorem",
        "generated_utc": _timestamp(),
        "status": status,
        "proof_chain_role": "active_theorem_lane" if bridge_promotion_allowed else "candidate_display_lane",
        "public_surface_candidate_allowed": bridge_promotion_allowed,
        "display_allowed_as_compare_only_absolute_attachment": not bridge_promotion_allowed,
        "prediction_promotion_allowed": bridge_promotion_allowed,
        "weighted_cycle_base_eligible": weighted_cycle_eligible,
        "theorem_object": "absolute_weighted_cycle_neutrino_family",
        "non_circularity_status": {
            "promotion_allowed": bridge_promotion_allowed,
            "weighted_cycle_base_eligible": weighted_cycle_eligible,
            "bridge_status": bridge_rigidity.get("status"),
            "bridge_public_surface_candidate_allowed": bridge_rigidity.get("public_surface_candidate_allowed"),
            "compare_only_C_nu_used": not bridge_promotion_allowed,
            "missing_source_object": None if bridge_promotion_allowed else "source_closed_neutrino_operator_basis_ordering_and_absolute_scale",
            "missing_source_objects": []
            if bridge_promotion_allowed
            else [
                "source_closed_weighted_cycle_operator_basis_and_label_law",
                "source_emitted_neutrino_C_nu_no_compare_target",
                "source_derived_absolute_neutrino_scale",
            ],
            "strict_audit_label": "source_absolute_neutrino_family"
            if bridge_promotion_allowed
            else "compare_only_absolute_attachment_candidate",
        },
        "inputs": {
            "P_nu": p_nu,
            "C_nu": c_nu,
            "m_star_eV": m_star_eV,
            "q_mean": q_mean,
            "q_mean_to_p_nu": q_mean_to_p_nu,
            "p_nu": p_nu_exponent,
            "dimensionless_masses": dimensionless_masses,
            "dimensionless_delta_m_sq_eV2": dimensionless_dm2,
        },
        "outputs": {
            "B_nu": b_nu,
            "bridge_reconstruction": "B_nu = P_nu * C_nu",
            "lambda_reconstruction": "lambda_nu = (m_star_eV / q_mean^p_nu) * P_nu * C_nu",
            "lambda_nu": lambda_nu,
            "masses_eV": masses_eV,
            "mass_basis_semantics": "ascending_weighted_cycle_candidate_mass_eigenstates_not_flavor_neutrino_masses",
            "physical_mass_ordering_status": weighted_cycle.get("mass_ordering_status", "unresolved"),
            "delta_m_sq_eV2": delta_m_sq_eV2,
            "absolute_family": {
                "masses": [
                    f"m1 = lambda_nu * {dimensionless_masses[0]}",
                    f"m2 = lambda_nu * {dimensionless_masses[1]}",
                    f"m3 = lambda_nu * {dimensionless_masses[2]}",
                ],
                "dm2": {
                    key: f"Delta m{key}^2 = lambda_nu^2 * {value}"
                    for key, value in dimensionless_dm2.items()
                },
            },
        },
        "depends_on": [
            "oph_neutrino_bridge_rigidity_theorem",
            "oph_neutrino_weighted_cycle_theorem_object",
        ],
        "notes": [
            "The exact segment adapter, bridge value, and absolute family are comparison-only coordinates.",
            "No absolute mass, splitting, or flavor-labelled neutrino row can be promoted from the rejected source-open weighted-cycle base.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the absolute neutrino attachment candidate audit artifact.")
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(
        _load_json(BRIDGE_RIGIDITY_JSON),
        _load_json(WEIGHTED_CYCLE_JSON),
        _load_json(ATTACHMENT_IRREDUCIBILITY_JSON),
        _load_json(ABSOLUTE_ATTACHMENT_SCAFFOLD_JSON),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
