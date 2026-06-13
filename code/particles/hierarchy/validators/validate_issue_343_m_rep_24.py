#!/usr/bin/env python3
"""Validate the OPH issue #343 m_rep=24 certificate."""

from __future__ import annotations

import json
import pathlib
import sys


def main(path: str = "certificates/R_m_rep_24_certificate.json") -> int:
    cert_path = pathlib.Path(path)
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    rep = cert.get("representation_sector", {})
    result = cert.get("result", {})
    spectral = cert.get("spectral_object", {})
    controls = cert.get("negative_controls", [])
    checks = cert.get("verifier_checks", {})
    forbidden_used = cert.get("forbidden_inputs_used", [])
    dims = [component.get("dimension") for component in rep.get("components", [])]

    validation = {
        "issue_is_343": cert.get("issue") == 343,
        "accepted": cert.get("accepted") is True,
        "status_closed_round_count": (
            cert.get("status") == "closed_representation_to_spectrum_round_count"
        ),
        "component_dimensions_are_8_3_1": dims == [8, 3, 1],
        "unoriented_dimension_is_12": rep.get("unoriented_adjoint_dimension") == 12,
        "orientation_multiplier_is_2": rep.get("orientation_multiplier") == 2,
        "oriented_support_is_24": rep.get("oriented_support_dimension") == 24,
        "m_rep_is_24": result.get("m_rep") == 24,
        "exponent_is_minus_one_over_48": result.get("specialized_exponent") == "-1/48",
        "spectral_period_is_24": spectral.get("period") == 24,
        "su5_negative_control_recorded": any(
            item.get("name") == "single-orientation SU(5) adjoint"
            and item.get("status") == "reject_despite_same_integer"
            for item in controls
        ),
        "doubled_su5_rejected": any(
            item.get("name") == "doubled SU(5) adjoint" and item.get("status") == "reject"
            for item in controls
        ),
        "no_forbidden_inputs_used": forbidden_used == [],
        "verifier_checks_pass": all(checks.values()),
        "claim_boundary_closed": cert.get("claim_boundary", {}).get("not_closed_here") == [],
    }
    payload = {"checks": validation, "pass": all(validation.values())}
    print(json.dumps(payload, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    sys.exit(
        main(
            sys.argv[1]
            if len(sys.argv) > 1
            else "certificates/R_m_rep_24_certificate.json"
        )
    )
