#!/usr/bin/env python3
"""Validate the global repair-tick lemma certificate."""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction


FORBIDDEN_EW_INPUTS = {
    "alpha_U",
    "v/E_star",
    "D10 transmutation exponent",
    "observed electroweak hierarchy",
}


def _fraction_from_payload(payload: dict) -> Fraction:
    return Fraction(int(payload["numerator"]), int(payload["denominator"]))


def main(cert_path: str = "certificates/R_N_global_repair_tick_certificate.json") -> int:
    cert = json.loads(pathlib.Path(cert_path).read_text(encoding="utf-8"))
    one_tick = _fraction_from_payload(cert["normalization"]["one_tick_exponent"])
    full_cycle = _fraction_from_payload(cert["normalization"]["full_cycle_exponent"])
    rounds = int(cert["normalization"]["full_repair_rounds"])
    derived_uses = set(cert["source_side_dependency_audit"]["derived_uses"])
    does_not_use = set(cert["source_side_dependency_audit"]["does_not_use"])
    derived_premises = cert["premises"]["derived"]
    declared_inputs = cert["premises"]["declared_branch_inputs"]
    acceptance = cert["acceptance_criteria_status"]

    checks = {
        "status_is_closed_lemma_on_declared_rounds": (
            cert["status"] == "closed_global_repair_tick_lemma_on_declared_round_structure"
        ),
        "theorem_kind_is_lemma_on_declared_branch": cert["theorem_kind"] == "lemma_on_declared_branch",
        "object_id_matches": cert["object_id"] == "GlobalRepairTickLemma_R_N",
        "twenty_four_rounds": rounds == 24,
        "tick_exponent_is_minus_one_over_48": one_tick == Fraction(-1, 48),
        "full_cycle_exponent_is_minus_one_half": full_cycle == Fraction(-1, 2),
        "tick_times_rounds_is_full_cycle": one_tick * rounds == full_cycle,
        "parametric_exponent_law_recorded": (
            cert["exponent_law"]["per_tick_exponent_for_m_ticks"] == "-1/(2m)"
        ),
        "derivative_formula_recorded": cert["normalization"]["abs_g_star_prime"] == "(N_CRC/pi)^(-1/48)",
        "full_cycle_multiplier_is_derived_from_closure": any(
            premise["id"] == "full_cycle_closure_multiplier" and premise["discharged_here"] is True
            for premise in derived_premises
        ),
        "f_interface_equivalence_derived": any(
            premise["id"] == "f_interface_realization_equivalence" and premise["discharged_here"] is True
            for premise in derived_premises
        ),
        "round_count_is_declared_not_derived": any(
            premise["id"] == "global_repair_round_count" and premise["discharged_here"] is False
            for premise in declared_inputs
        ),
        "round_count_honesty_flag_set": acceptance["round_count_derived_from_first_principles"] is False,
        "closure_transport_derived_from_f_interface": (
            acceptance.get("closure_transport_derived_from_F_interface") is True
        ),
        "counting_model_flagged_as_identification": (
            acceptance.get("readback_counting_model_is_modeling_identification") is True
            and any(
                "modeling identification" in item
                for item in cert["claim_boundary"]["declared_not_derived"]
            )
        ),
        "concrete_machinery_verification_listed_open": (
            acceptance.get("concrete_finite_machinery_verification_open") is True
            and any(
                "finite repair machinery" in item
                for item in cert["claim_boundary"]["not_closed_by_certificate"]
            )
        ),
        "fixed_point_emits_tick_contraction_on_declared_branch": (
            acceptance["proves_declared_screen_capacity_fixed_point_emits_tick_contraction"] is True
        ),
        "open_round_count_derivation_listed": any(
            "round count" in item or "24-round" in item
            for item in cert["claim_boundary"]["not_closed_by_certificate"]
        ),
        "ew_inputs_excluded_from_derived_uses": not (derived_uses & FORBIDDEN_EW_INPUTS),
        "ew_inputs_explicitly_excluded": FORBIDDEN_EW_INPUTS <= does_not_use,
    }
    out = {**checks, "pass": all(checks.values())}
    print(json.dumps(out, indent=2))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "certificates/R_N_global_repair_tick_certificate.json"))
