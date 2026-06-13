#!/usr/bin/env python3
"""Validate the OPH issue #337 electroweak tick-projection certificate."""

from __future__ import annotations

import json
import pathlib
import sys
from decimal import Decimal


def D(value: str) -> Decimal:
    return Decimal(value)


def main(path: str = "certificates/R_EW_tick_projection_certificate.json") -> int:
    cert_path = pathlib.Path(path)
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    exact = cert.get("exact_bridge", {})
    rounded = cert.get("rounded_capacity_diagnostic", {})
    forbidden = cert.get("forbidden_calibrations", [])
    boundary = cert.get("claim_boundary", {})
    checks = {
        "issue_is_337": cert.get("issue") == 337,
        "accepted": cert.get("accepted") is True,
        "status_closed_projection": cert.get("status") == "closed_projection_map_with_exact_bridge_condition",
        "bridge_residual_zero": D(exact.get("bridge_residual", "1")) == 0,
        "projection_exponent_matches_4P": abs(D(exact.get("projection_exponent_error", "1"))) <= Decimal("1e-40"),
        "v_bridge_matches_source": abs(D(exact.get("v_bridge_error", "1"))) <= Decimal("1e-40"),
        "rounded_N_is_diagnostic": rounded.get("status") == "diagnostic_only_not_exact_bridge_certificate",
        "rounded_N_fails_exact_bridge": abs(D(rounded.get("bridge_residual", "0"))) > Decimal("1e-6"),
        "weak_scale_forbidden": any("measured weak scale" in item for item in forbidden),
        "rounded_display_forbidden": any("rounded N_CRC" in item for item in forbidden),
        "exact_source_boundary_recorded": "B_EW" in boundary.get("source_certificate_required", ""),
    }
    payload = {"checks": checks, "pass": all(checks.values())}
    print(json.dumps(payload, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "certificates/R_EW_tick_projection_certificate.json"))
