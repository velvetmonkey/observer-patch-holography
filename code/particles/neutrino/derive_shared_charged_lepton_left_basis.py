#!/usr/bin/env python3
"""Audit and, when justified, derive the shared charged-lepton left basis.

Chain role: expose the charged-lepton left singular basis that PMNS needs on
the same ordered family labels used by the flavor and neutrino continuation
lanes.

Mathematics: the charged shape surface fixes the left singular vectors up to an
overall positive scale. Since `Y_e = g * Y_e_shape` with `g > 0`, the left
eigenspaces of `Y_e Y_e^dagger` are unchanged by the unresolved absolute scale.

Declared input: the blind charged-lepton forward artifact carrying `Y_e_shape`,
`U_e_left`, and ordered family labels. The current artifact is source-open and
nearly degenerate, so those stored vectors are diagnostic only.

The source must close its charged shape and have a nondegenerate singular
spectrum.  A matrix carried by an open or nearly degenerate template remains a
diagnostic candidate and cannot define a physical PMNS basis.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "particles" / "runs" / "leptons" / "blind_forward_artifact.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "shared_charged_lepton_left_basis.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _minimum_relative_gap(values: list[float]) -> float | None:
    if len(values) != 3:
        return None
    ordered = sorted(abs(float(value)) for value in values)
    scale = max(ordered[-1], 1.0e-30)
    return min(ordered[index + 1] - ordered[index] for index in range(2)) / scale


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the shared charged-lepton left basis artifact.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--minimum-relative-gap", type=float, default=1.0e-8)
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = _load_json(Path(args.input))
    labels = list(payload.get("labels") or [])
    u_e_left = payload.get("U_e_left")
    if labels != ["f1", "f2", "f3"] or not isinstance(u_e_left, dict):
        raise ValueError("blind charged forward artifact must expose ordered labels [f1, f2, f3] and U_e_left")

    singular_values_shape = [float(value) for value in (payload.get("singular_values_shape") or [])]
    minimum_relative_gap = _minimum_relative_gap(singular_values_shape)
    source_closure_state = str(payload.get("closure_state") or "missing")
    source_shape_closed = source_closure_state == "closed"
    spectrum_nondegenerate = (
        minimum_relative_gap is not None
        and minimum_relative_gap >= float(args.minimum_relative_gap)
    )
    closed = source_shape_closed and spectrum_nondegenerate

    result = {
        "artifact": "oph_shared_charged_lepton_left_basis",
        "generated_utc": _timestamp(),
        "status": "closed" if closed else "open_upstream_charged_basis_not_identified",
        "theorem_status": "shape_closed_scale_invariant_left_basis" if closed else "not_established",
        "pmns_use_allowed": closed,
        "public_surface_candidate_allowed": closed,
        "source_closure_state": source_closure_state,
        "source_shape_closed": source_shape_closed,
        "basis_spectrum": {
            "singular_values_shape": singular_values_shape,
            "minimum_relative_gap": minimum_relative_gap,
            "required_minimum_relative_gap": float(args.minimum_relative_gap),
            "nondegenerate": spectrum_nondegenerate,
        },
        "source_artifacts": [
            payload.get("artifact"),
            payload.get("metadata", {}).get("observable_artifact"),
        ],
        "labels": labels,
        "basis_contract": {
            "labels": labels,
            "orientation_preserved": True,
            "physical_identification_closed": closed,
        },
        "U_e_left": u_e_left,
        "scale_invariance_rule": "U_e_left(g * Y_e_shape) = U_e_left(Y_e_shape) for every real g > 0",
        "notes": (
            [
                "Derived from a closed charged shape with a nondegenerate singular spectrum.",
                "Independent of the unresolved charged absolute scale.",
                "Eligible for use by a downstream PMNS builder subject to the neutrino-side basis contract.",
            ]
            if closed
            else [
                "The input charged artifact does not close a stable physical left basis.",
                "The stored U_e_left matrix is retained as a diagnostic candidate only.",
                "A closed source-side charged shape with a nondegenerate singular spectrum is required before PMNS can be formed.",
            ]
        ),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
