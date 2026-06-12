#!/usr/bin/env python3
"""Emit the exact current-family quark PDG reconstruction theorem artifact."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AFFINE_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_affine_anchor_theorem.json"
EXACT_READOUT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_readout.json"
LANE_CONTRACT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_lane_closure_contract.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_pdg_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_artifact(affine: dict, exact_readout: dict, lane_contract: dict) -> dict:
    anchor = float(affine["current_family_affine_anchor"]["value"])
    split = float(affine["current_family_sector_split"]["value"])
    exact_u = [float(value) for value in exact_readout["E_u_log_exact"]]
    exact_d = [float(value) for value in exact_readout["E_d_log_exact"]]
    masses_u = [math.exp(anchor + split + value) for value in exact_u]
    masses_d = [math.exp(anchor - split + value) for value in exact_d]
    target_frontier = lane_contract["exact_missing_theorems"]
    target_frontier_ids = [item["id"] for item in target_frontier]
    if target_frontier_ids:
        frontier_note = (
            "This theorem is exact only on the target-anchored current-family witness. "
            "Promotion to a target-free theorem-grade OPH derivation requires the listed public frontier."
        )
    else:
        frontier_note = (
            "This theorem is exact only on the target-anchored current-family witness. "
            "The target-free selected-public-class closure is carried by the public physical-sigma and "
            "exact-Yukawa theorem artifacts, so this current-family witness is not the promotion surface."
        )

    return {
        "artifact": "oph_quark_current_family_exact_pdg_theorem",
        "generated_utc": _timestamp(),
        "proof_status": "closed_current_family_exact_pdg_reconstruction",
        "theorem_scope": "current_family_only",
        "public_promotion_allowed": False,
        "supporting_artifacts": {
            "affine_anchor_theorem": affine["artifact"],
            "exact_readout": exact_readout["artifact"],
            "lane_closure_contract": lane_contract["artifact"],
        },
        "theorem_statement": (
            "On the fixed exact current-family quark witness, the exact six running values are reconstructed by the "
            "ordered centered shapes and the affine sector data: "
            "m_u,m_c,m_t = exp(A_q^(cf) + delta_q^(cf) + E_u^log), "
            "m_d,m_s,m_b = exp(A_q^(cf) - delta_q^(cf) + E_d^log). "
            "Hence the current-family quark sextet is exact on this witness."
        ),
        "current_family_affine_data": {
            "A_q_current_family": anchor,
            "delta_q_current_family": split,
        },
        "centered_log_shapes": {
            "E_u_log_exact": exact_u,
            "E_d_log_exact": exact_d,
        },
        "reconstructed_current_family_running_values_gev": {
            "u": masses_u[0],
            "c": masses_u[1],
            "t": masses_u[2],
            "d": masses_d[0],
            "s": masses_d[1],
            "b": masses_d[2],
        },
        "reference_current_family_running_values_gev": {
            "u": float(exact_readout["predicted_singular_values_u"][0]),
            "c": float(exact_readout["predicted_singular_values_u"][1]),
            "t": float(exact_readout["predicted_singular_values_u"][2]),
            "d": float(exact_readout["predicted_singular_values_d"][0]),
            "s": float(exact_readout["predicted_singular_values_d"][1]),
            "b": float(exact_readout["predicted_singular_values_d"][2]),
        },
        "exact_fit_residuals_gev": {
            "u": masses_u[0] - float(exact_readout["predicted_singular_values_u"][0]),
            "c": masses_u[1] - float(exact_readout["predicted_singular_values_u"][1]),
            "t": masses_u[2] - float(exact_readout["predicted_singular_values_u"][2]),
            "d": masses_d[0] - float(exact_readout["predicted_singular_values_d"][0]),
            "s": masses_d[1] - float(exact_readout["predicted_singular_values_d"][1]),
            "b": masses_d[2] - float(exact_readout["predicted_singular_values_d"][2]),
        },
        "next_target_free_bridge": {
            "remaining_public_frontier": target_frontier_ids,
            "note": frontier_note,
        },
        "notes": [
            "This closes the exact current-family PDG-matched running-value reconstruction on the current-family witness.",
            "It does not by itself prove the stronger target-free physical-sheet quark lane.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the exact current-family quark PDG reconstruction theorem artifact.")
    parser.add_argument("--affine", default=str(AFFINE_JSON))
    parser.add_argument("--exact-readout", default=str(EXACT_READOUT_JSON))
    parser.add_argument("--lane-contract", default=str(LANE_CONTRACT_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(
        json.loads(Path(args.affine).read_text(encoding="utf-8")),
        json.loads(Path(args.exact_readout).read_text(encoding="utf-8")),
        json.loads(Path(args.lane_contract).read_text(encoding="utf-8")),
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
