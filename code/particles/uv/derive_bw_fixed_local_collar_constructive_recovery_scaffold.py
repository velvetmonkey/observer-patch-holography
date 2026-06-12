#!/usr/bin/env python3
"""Emit the fixed-local-collar constructive recovery scaffold."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bw_collar_support import CONSTRUCTIVE_RECOVERY_FORMULA, build_schedule_term_frontier


ROOT = Path(__file__).resolve().parents[2]
RAW_DATUM = ROOT / "particles" / "runs" / "uv" / "bw_fixed_local_collar_markov_faithfulness_datum.json"
CARRIED_SCHEDULE = ROOT / "particles" / "runs" / "uv" / "bw_carried_collar_schedule_scaffold.json"
FAITHFUL_MODULAR_DEFECT = (
    ROOT / "particles" / "runs" / "uv" / "bw_fixed_local_collar_faithful_modular_defect_scaffold.json"
)
DEFAULT_OUT = ROOT / "particles" / "runs" / "uv" / "bw_fixed_local_collar_constructive_recovery_scaffold.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_ref(path: Path) -> str:
    return f"code/{path.relative_to(ROOT).as_posix()}"


def build_payload(raw_datum: dict[str, Any]) -> dict[str, Any]:
    cmi_component = raw_datum["contract"]["must_emit"][0]
    return {
        "artifact": "oph_bw_fixed_local_collar_constructive_recovery_scaffold",
        "generated_utc": _timestamp(),
        "status": "minimal_local_recovery_extension",
        "public_promotion_allowed": False,
        "exact_missing_object": "constructive_recovery_remainder_vanishing",
        "parent_raw_datum": raw_datum["exact_missing_object"],
        "parent_missing_witness": raw_datum["parent_missing_witness"],
        "parent_extraction_object": raw_datum["parent_extraction_object"],
        "role": (
            "Package the smaller constructive recovery witness on each fixed local collar model: "
            "the Fawzi-Renner recovery remainder vanishes along the realized refinement chain."
        ),
        "contract": {
            "for_fixed_models": raw_datum["contract"]["for_fixed_models"],
            "must_emit": CONSTRUCTIVE_RECOVERY_FORMULA,
            "derived_from_component": cmi_component,
            "theorem_basis": (
                "On one fixed finite-dimensional collar model, the Fawzi-Renner recovery bound is a "
                "continuous function of the collarwise conditional mutual information with value 0 at "
                "epsilon = 0, so epsilon_{n,m,delta} -> 0 forces the recovery remainder to vanish."
            ),
            "must_not_assume": raw_datum["contract"]["must_not_assume"],
        },
        "feeds_parent_schedule": {
            "artifact": _artifact_ref(CARRIED_SCHEDULE),
            "formula": raw_datum["implies_schedule"]["formula"],
            "other_term_still_needed_artifact": _artifact_ref(FAITHFUL_MODULAR_DEFECT),
            "other_term_still_needed": "fixed_local_collar_faithful_modular_defect_vanishing",
        },
        "joint_schedule_term_frontier": build_schedule_term_frontier(
            constructive_recovery_artifact=_artifact_ref(DEFAULT_OUT),
            faithful_modular_defect_artifact=_artifact_ref(FAITHFUL_MODULAR_DEFECT),
            carried_schedule_artifact=_artifact_ref(CARRIED_SCHEDULE),
        ),
        "already_packaged_below_this_witness": raw_datum["already_packaged_below_this_datum"],
        "why_this_is_smaller": [
            "This witness isolates the recovery-theoretic part of the carried-collar schedule before any spectral-faithfulness input is used.",
            "It is smaller than the carried schedule because it removes the separate faithful modular-defect term.",
            "It is independent of the exact-Markov comparison scaffold; both descend from the same collarwise Markov input but control different schedule terms.",
        ],
        "notes": [
            "This scaffold does not claim the constructive recovery witness is emitted on the live corpus.",
            "By itself it does not close the carried-collar schedule because the faithfulness-weighted modular defect term is separate.",
            "Together with the faithful modular-defect scaffold, it closes the two-term schedule contract consumed by cap-pair extraction.",
            "The actual solver frontier above this witness is recorded as the two-term pair, rather than as a separately targeted schedule object.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the fixed-local-collar constructive recovery scaffold.")
    parser.add_argument("--raw-datum", default=str(RAW_DATUM))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(_load_json(Path(args.raw_datum)))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
