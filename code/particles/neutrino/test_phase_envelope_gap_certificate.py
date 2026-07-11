#!/usr/bin/env python3
"""Check that phase stability never substitutes for a physical mass-label rule."""

from __future__ import annotations

import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
ENVELOPE = ROOT / "particles" / "runs" / "neutrino" / "majorana_phase_envelope.json"
SPLITTINGS = ROOT / "particles" / "runs" / "neutrino" / "forward_splittings.json"


def main() -> int:
    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    splittings = json.loads(SPLITTINGS.read_text(encoding="utf-8"))
    certificate = envelope.get("gap_vs_radius_certificate") or {}
    if not certificate:
        print("missing gap_vs_radius_certificate", file=sys.stderr)
        return 1
    if splittings.get("ordering_phase_certified") is not None:
        print("phase stability was incorrectly promoted to a physical ordering", file=sys.stderr)
        return 1
    if splittings.get("physical_mass_label_assignment") is not None:
        print("physical mass labels were assigned without a source label rule", file=sys.stderr)
        return 1
    if any(splittings.get(key) is not None for key in ("delta_m21_sq_gev2", "delta_m31_sq_gev2", "delta_m32_sq_gev2")):
        print("physical delta-m labels were emitted without a source label rule", file=sys.stderr)
        return 1
    if splittings.get("ordering_theorem_status") != "not_established_mass_label_rule_absent":
        print("ordering theorem status is not fail-closed", file=sys.stderr)
        return 1
    if bool((splittings.get("source_closure_status") or {}).get("closed", False)):
        print("source-open declared matrix family was incorrectly promoted", file=sys.stderr)
        return 1
    if splittings.get("public_surface_candidate_allowed") is not False:
        print("conditional ascending spectrum is incorrectly public-promotable", file=sys.stderr)
        return 1
    print("phase stability remains separate from physical mass labeling")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
