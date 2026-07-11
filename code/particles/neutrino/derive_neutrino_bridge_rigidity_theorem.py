#!/usr/bin/env python3
"""Audit the historical weighted-cycle bridge-rigidity candidate artifact.

Chain role: retain a historical optimizer and permit promotion only if a future
source-closed base and independent bridge audit pass every gate.

Mathematics:
1. The declared weighted-cycle matrix fixes a conditional scale-free PMNS/hierarchy shape.
2. The candidate proxy P_nu is internal and strictly positive on that branch.
3. The optimizer is retained as a diagnostic coordinate. It cannot be a
   physical reduced correction invariant unless both the weighted-cycle base
   and the bridge audit independently pass their source-only gates.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WEIGHTED_CYCLE_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"
IRREDUCIBILITY_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_irreducibility_theorem.json"
CORRECTION_AUDIT_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_bridge_correction_candidate_audit.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_bridge_rigidity_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(
    weighted_cycle: dict[str, Any],
    irreducibility: dict[str, Any],
    correction_audit: dict[str, Any],
) -> dict[str, Any]:
    proxy = correction_audit["emitted_proxy_route"]
    reduced_object = irreducibility["reduced_remaining_object"]
    pmns = weighted_cycle["pmns_observables"]
    ratio = float(weighted_cycle["dimensionless_ratio_dm21_over_dm32"])
    emitted_formula = "sum_gap^2 * prod_qbar * solar_response_over_mstar^-0.5"
    emitted_keys = ["sum_gap", "prod_qbar", "solar_response_over_mstar"]
    emitted_exponents = [2.0, 1.0, -0.5]
    display_value = 0.9994295999075177
    optimizer_relative_error = abs(
        display_value - float(correction_audit["current_compare_only_target"]["value"])
    ) / float(correction_audit["current_compare_only_target"]["value"])
    compare_only_audit = correction_audit.get("status") == "compare_only_reduced_bridge_correction_search"
    weighted_cycle_eligible = (
        weighted_cycle.get("source_only_prediction_eligible") is True
        and weighted_cycle.get("prediction_promotion_allowed") is True
        and weighted_cycle.get("historical_target_exposure") is False
        and (weighted_cycle.get("source_closure_status") or {}).get("closed") is True
    )
    correction_audit_eligible = (
        not compare_only_audit
        and correction_audit.get("must_not_feed_back") is False
    )
    promotion_allowed = weighted_cycle_eligible and correction_audit_eligible
    status = (
        "theorem_grade_emitted"
        if promotion_allowed
        else "candidate_from_compare_only_reduced_bridge_search"
    )

    return {
        "artifact": "oph_neutrino_bridge_rigidity_theorem",
        "generated_utc": _timestamp(),
        "status": status,
        "theorem_object": "C_nu",
        "proof_chain_role": "active_theorem_lane" if promotion_allowed else "candidate_display_lane",
        "public_surface_candidate_allowed": promotion_allowed,
        "display_allowed_as_compare_only": compare_only_audit,
        "prediction_promotion_allowed": promotion_allowed,
        "weighted_cycle_base_eligible": weighted_cycle_eligible,
        "correction_audit_eligible": correction_audit_eligible,
        "branch": "weighted_cycle_majorana_holonomy",
        "statement": (
            "The stored value is the distinguished optimizer on a declared family-assisted correction class. "
            "It is comparison-only because the weighted-cycle base is target-informed and source-open and the correction audit forbids feedback."
        ),
        "physical_selection_rules": [
            "bridge_external_above_P_nu",
            "neutral_under_exact_q_mean_factorization",
            "genuinely_family_assisted_on_the_first_solar_mover",
            "distinguished_exact_optimizer_on_the_declared_family_assisted_class",
        ],
        "emitted_proxy": {
            "symbol": "P_nu",
            "formula": proxy["formula"],
            "value": float(proxy["value"]),
        },
        "theorem_inputs": {
            "pmns_observables": pmns,
            "dimensionless_ratio_dm21_over_dm32": ratio,
            "reduced_object_definition": reduced_object["definition"],
            "bridge_reconstruction": reduced_object["bridge_reconstruction"],
        },
        "emitted_formula": emitted_formula,
        "emitted_keys": emitted_keys,
        "emitted_exponents": emitted_exponents,
        "emitted_value": display_value if promotion_allowed else None,
        "display_value": display_value,
        "optimizer_relative_error_in_emitted_class": optimizer_relative_error,
        "non_circularity_status": {
            "promotion_allowed": promotion_allowed,
            "weighted_cycle_base_eligible": weighted_cycle_eligible,
            "correction_audit_eligible": correction_audit_eligible,
            "compare_only_correction_audit_used": compare_only_audit,
            "correction_audit_status": correction_audit.get("status"),
            "must_not_feed_back": bool(correction_audit.get("must_not_feed_back", True)),
            "missing_source_object": None if promotion_allowed else "source_emitted_neutrino_operator_and_C_nu_no_compare_target",
            "missing_source_objects": []
            if promotion_allowed
            else [
                "source_closed_weighted_cycle_operator_basis_and_label_law",
                "source_emitted_neutrino_C_nu_no_compare_target",
            ],
            "strict_audit_label": "source_emitted_C_nu"
            if promotion_allowed
            else "compare_only_C_nu_candidate",
        },
        "depends_on": [
            "oph_neutrino_attachment_irreducibility_theorem",
            "oph_neutrino_bridge_correction_candidate_audit",
        ],
        "notes": [
            (
                "This theorem promotes the exact optimizer statement from an independently source-closed finite family-assisted class to the physical reduced bridge law."
                if promotion_allowed
                else "This artifact keeps the optimized C_nu display value but does not promote it because the correction audit is compare-only."
            ),
            "The compare-only adapter and corridor remain on disk only as diagnostic surfaces beneath this theorem.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the weighted-cycle bridge-rigidity candidate audit artifact.")
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(
        _load_json(WEIGHTED_CYCLE_JSON),
        _load_json(IRREDUCIBILITY_JSON),
        _load_json(CORRECTION_AUDIT_JSON),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
