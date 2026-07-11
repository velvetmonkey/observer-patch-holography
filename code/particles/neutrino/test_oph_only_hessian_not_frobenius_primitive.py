#!/usr/bin/env python3
"""Reject Frobenius/Hilbert-Schmidt primitivization on the OPH-only Hessian surface."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "particles" / "runs" / "neutrino" / "majorana_overlap_defect_hessian.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the OPH-only Hessian boundary.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    args = parser.parse_args()

    payload = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
    if str(payload.get("primitive_metric_source", "")).startswith("hilbert") or str(payload.get("primitive_metric_source", "")).startswith("frobenius"):
        print("OPH-only Hessian artifact illegally treats Hilbert-Schmidt/Frobenius geometry as primitive", file=sys.stderr)
        return 1
    if payload.get("oph_origin_status") == "closed" and payload.get("upstream_missing_object") == "oph_majorana_overlap_defect_scalar_evaluator":
        print("Hessian artifact claims OPH closure while the scalar evaluator is still missing", file=sys.stderr)
        return 1
    if payload.get("public_surface_candidate_allowed") is not False:
        print("conditional Hessian is incorrectly public-promotable", file=sys.stderr)
        return 1
    if bool((payload.get("source_closure_status") or {}).get("closed", False)):
        print("conditional Hessian incorrectly claims source closure", file=sys.stderr)
        return 1
    print("OPH-only Hessian provenance guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
