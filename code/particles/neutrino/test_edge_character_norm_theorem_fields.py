#!/usr/bin/env python3
"""Validate the sharpened edge-character / norm theorem fields."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "particles" / "runs" / "neutrino" / "majorana_overlap_defect_scalar_evaluator.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate sharpened Majorana norm-theorem fields.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    args = parser.parse_args()

    payload = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
    if payload.get("theorem_candidate_id") != "oph_majorana_scalar_from_centered_edge_norm":
        print("Majorana scalar evaluator is missing the sharpened theorem candidate id", file=sys.stderr)
        return 1
    if payload.get("sublemma_candidate_id") != "selector_centered_quadraticity_polarization_law_on_edge_bundle":
        print("Majorana scalar evaluator is missing the sharpened quadraticity sublemma id", file=sys.stderr)
        return 1
    if payload.get("smallest_exact_missing_clause") is not None:
        print("Majorana scalar evaluator still reports a smaller clause after scalar-side closure", file=sys.stderr)
        return 1
    if payload.get("remaining_theorem_object") is not None:
        print("Majorana scalar evaluator still reports a remaining theorem object after isotropic-branch closure", file=sys.stderr)
        return 1
    source_closed = bool((payload.get("source_closure_status") or {}).get("closed", False))
    expected_remaining = (
        "one positive residual bridge invariant above the closed normalizer"
        if source_closed
        else "source_closed_neutrino_operator_basis_and_mass_label_contract"
    )
    if payload.get("exact_remaining_ingredient") != expected_remaining:
        print("Majorana scalar evaluator does not expose the correct source-closure frontier", file=sys.stderr)
        return 1
    if payload.get("phase_cocycle_triviality_status") != "closed_from_normalized_lift_coboundary":
        print("Majorana scalar evaluator does not expose the closed phase-cocycle theorem status", file=sys.stderr)
        return 1
    if payload.get("bundle_descent_status") != "closed_from_normalized_common_refinement_unitary_transport":
        print("Majorana scalar evaluator does not expose the closed bundle-descent theorem status", file=sys.stderr)
        return 1
    print("edge-character norm theorem guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
