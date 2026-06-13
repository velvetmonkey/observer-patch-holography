#!/usr/bin/env python3
"""Validate the OPH issue #342 finite readback-resolution certificate."""

from __future__ import annotations

import json
import pathlib
import sys
from decimal import Decimal


def D(value: str | None, default: str = "0") -> Decimal:
    return Decimal(value if value is not None else default)


def main(path: str = "certificates/R_readback_resolution_certificate.json") -> int:
    cert_path = pathlib.Path(path)
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    reg = cert.get("capacity_register", {})
    atoms = [atom for atom in reg.get("atoms", []) if atom.get("selected") is True]
    obs = cert.get("observer_sector", {})
    nf = cert.get("normal_form", {})
    extractor = cert.get("extractor", {})
    readback = cert.get("readback_resolution", {})
    refinement = cert.get("refinement_certificate", {})
    ledger = cert.get("input_ledger", {})
    boundary = cert.get("claim_boundary", {})
    checks = cert.get("checks", {})
    used = set(ledger.get("used_inputs", []))
    forbidden = set(ledger.get("forbidden_inputs", []))

    selected_cap = D(atoms[0].get("capacity")) if len(atoms) == 1 else Decimal(0)
    validation = {
        "issue_is_342": cert.get("issue") == 342,
        "accepted": cert.get("accepted") is True,
        "status_closed_readback_resolution": (
            cert.get("status") == "closed_finite_readback_resolution_certificate"
        ),
        "normal_form_unique": nf.get("unique") is True
        and nf.get("finite_state") is True
        and nf.get("schedule_independent") is True,
        "observer_sector_central_nonzero": obs.get("nonzero") is True
        and obs.get("central_projector") is True
        and obs.get("stable_self_reading") is True,
        "register_is_central_positive": reg.get("central") is True
        and reg.get("positive_spectrum") is True,
        "one_selected_atom": len(atoms) == 1,
        "selected_atom_is_positive": selected_cap > 0,
        "selected_probability_one": len(atoms) == 1 and D(atoms[0].get("probability")) == 1,
        "selected_variance_zero": D(reg.get("selected_variance")) == 0,
        "positive_root_extractor": extractor.get("formula") == "rho_read = sqrt(pi / Cap_read)"
        and extractor.get("positive_root") is True,
        "rho_read_positive": D(readback.get("rho_read")) > 0,
        "display_marked_diagnostic": readback.get("display_only") is True,
        "refinement_bound_recorded": refinement.get("uniform_limit_declared") is True
        and refinement.get("positive_root_closure") is True
        and Decimal("0") <= D(refinement.get("contraction_kappa")) < Decimal("1"),
        "no_forbidden_inputs_used": not (used & forbidden),
        "no_remaining_boundary": boundary.get("not_closed_here", []) == [],
        "round_count_recorded_elsewhere": any(
            "R_m_rep_24_certificate" in item
            for item in boundary.get("closed_elsewhere", [])
        ),
        "exact_capacity_recorded_elsewhere": any(
            "R_EW_global_capacity_certificate" in item
            for item in boundary.get("closed_elsewhere", [])
        ),
        "verifier_checks_pass": all(checks.values()),
    }
    payload = {"checks": validation, "pass": all(validation.values())}
    print(json.dumps(payload, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    sys.exit(
        main(
            sys.argv[1]
            if len(sys.argv) > 1
            else "certificates/R_readback_resolution_certificate.json"
        )
    )
