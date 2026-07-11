#!/usr/bin/env python3
"""Emit the no-hidden-discrete-branch / positive-scale-orbit neutrino audit."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPAIR_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"
BLOCKERS_JSON = ROOT / "particles" / "runs" / "neutrino" / "exact_blocking_items.json"
CERTIFICATE_JSON = ROOT / "particles" / "runs" / "neutrino" / "same_label_scalar_certificate.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_absolute_scale_orbit_audit.json"
THEOREM_NAME = "repaired_weighted_cycle_no_hidden_discrete_branch_and_positive_scale_orbit"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build_audit(repair: dict[str, Any], blockers: dict[str, Any], certificate: dict[str, Any] | None = None) -> dict[str, Any]:
    _require(repair.get("artifact") == "oph_neutrino_weighted_cycle_repair", "repair artifact mismatch")
    _require(blockers.get("artifact") == "oph_exact_neutrino_blocker_audit_v8", "blocker artifact mismatch")
    live = dict(blockers.get("live_continuation_branch_status") or {})
    compare_only = dict(live.get("compare_only_atmospheric_anchor") or {})
    _require(compare_only.get("status") == "compare_only", "compare-only anchor status mismatch")
    exact_blockers = list(blockers.get("exact_blockers") or [])
    source_missing = list((repair.get("source_closure_status") or {}).get("missing_objects") or [])
    blocker_names = [str(item.get("name")) for item in exact_blockers]
    certificate_summary: dict[str, Any] = {}
    if certificate is not None:
        _require(certificate.get("artifact") == "oph_neutrino_same_label_scalar_certificate", "certificate artifact mismatch")
        certificate_summary = {
            "artifact": certificate.get("artifact"),
            "proof_status": certificate.get("proof_status"),
            "source_only_physical_input_eligible": certificate.get("source_only_physical_input_eligible"),
            "source_closure_status": certificate.get("source_closure_status"),
            "exact_downstream_factorization_object": certificate.get("exact_downstream_factorization_object"),
            "builder_facing_exact_object": certificate.get("builder_facing_exact_object"),
            "smallest_constructive_missing_object": certificate.get("smallest_constructive_missing_object"),
        }
    return {
        "artifact": "oph_neutrino_absolute_scale_orbit_audit",
        "generated_utc": _timestamp(),
        "status": "rejected_candidate_scale_audit",
        "proof_chain_role": "nonpromoting_diagnostic",
        "must_not_feed_back": True,
        "theorem": None,
        "historical_theorem_name": THEOREM_NAME,
        "theorem_status": "not_established",
        "theorem_statement": (
            "The declared weighted-cycle matrix has a conditional positive-rescaling family, but it is not a physical residual "
            "orbit of OPH because the operator, basis placement, charged basis, and mass labels are not source-closed."
        ),
        "proof_primitives": {
            "repair_artifact": {
                "artifact": repair.get("artifact"),
                "cycle_basis_order": repair.get("cycle_basis_order"),
                "holonomy_orientation": repair.get("holonomy_orientation"),
                "physical_window_status": repair.get("physical_window_status"),
                "absolute_normalization_status": repair.get("absolute_normalization_status"),
                "source_closure_status": repair.get("source_closure_status"),
                "historical_target_exposure": repair.get("historical_target_exposure"),
                "prediction_promotion_allowed": repair.get("prediction_promotion_allowed"),
                "symbolic_absolute_family": repair.get("symbolic_absolute_family"),
            },
            "blocker_audit": {
                "artifact": blockers.get("artifact"),
                "closed_theorem_chain": list(blockers.get("closed_theorem_chain") or []),
                "exact_blockers": exact_blockers,
                "compare_only_atmospheric_anchor": compare_only,
            },
            "same_label_scalar_certificate": certificate_summary,
        },
        "no_hidden_discrete_branch": {
            "status": "not_established",
            "open_discrete_blockers": sorted(set(source_missing + blocker_names)),
            "closed_discrete_witnesses": [],
            "statement": "Declared cycle labels and orientation are candidate inputs, not source-derived physical branch selectors.",
        },
        "remaining_positive_scale_orbit": {
            "status": "conditional_candidate_family_only",
            "group": "R_{>0}",
            "family_parameter": "lambda_nu > 0",
            "action_on_lambda_nu": "lambda_nu -> s * lambda_nu, s > 0",
            "action_on_masses": "m_i -> s * m_i",
            "action_on_splittings": "Delta m^2_ij -> s^2 * Delta m^2_ij",
            "scale_free_mass_normal_form": repair.get("scale_free_mass_normal_form"),
            "scale_free_dm2_normal_form_eV2": (repair.get("scale_free_dm2_normal_form") or {}).get("dm2"),
            "proof_obstruction": "base_operator_and_physical_basis_not_source_closed",
        },
        "remaining_object": "source_closed_neutrino_operator_basis_and_mass_label_contract",
        "remaining_object_kind": "physical_neutrino_branch_definition",
        "remaining_object_contract": "derive_operator_basis_charged_basis_and_mass_labels_before_absolute_scale",
        "next_breaking_contract": "source_closed_neutrino_operator_basis_and_mass_label_contract",
        "compare_only_anchor_separation": {
            "current_compare_only_anchor": compare_only,
            "status": "hard_separated_compare_only",
        },
        "solver_output_contract": {
            "emit_now": [
                "rejected_candidate_comparison_coordinates",
                "conditional_scale_family_for_debugging",
            ],
            "must_not_emit_without_new_theorem": [
                "physical_pmns",
                "physical_mass_ordering",
                "lambda_nu",
                "absolute_neutrino_masses",
                "absolute_delta_m2_values",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the neutrino positive-scale orbit audit.")
    parser.add_argument("--repair", default=str(REPAIR_JSON))
    parser.add_argument("--blockers", default=str(BLOCKERS_JSON))
    parser.add_argument("--certificate", default=str(CERTIFICATE_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    repair = _load_json(Path(args.repair))
    blockers = _load_json(Path(args.blockers))
    certificate = _load_json(Path(args.certificate)) if args.certificate else None
    audit = build_audit(repair, blockers, certificate)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
