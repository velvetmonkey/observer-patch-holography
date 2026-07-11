#!/usr/bin/env python3
"""Export the realized same-label gap/defect readback artifact.

Chain role: bridge the flavor-side same-label transport/readback data into the
builder-facing neutrino pullback payload that the scalar certificate consumes.

Mathematics: use the realized same-label overlap certificate on the common
refinement together with the emitted family spectral gaps to form
`same_label_overlap_sq`, `defect_e = 1 - overlap_sq`, `g_e`, and the derived
`q_e -> eta_e -> mu_e` family on the ordered arrows `(psi12, psi23, psi31)`.

Declared inputs: the defect-weighted neutrino family shell, family-transport
kernel eigenvalue data, and overlap-edge line-lift certificate. Their source
closure is propagated rather than inferred from numerical completeness.

Output: either a complete realized-arrow pullback payload or, if the required
flavor-side data are still missing, the strict smallest-object shell.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "particles" / "runs" / "neutrino" / "defect_weighted_mu_e_family.json"
DEFAULT_FAMILY_KERNEL = ROOT / "particles" / "runs" / "flavor" / "family_transport_kernel.json"
DEFAULT_LINE_LIFT = ROOT / "particles" / "runs" / "flavor" / "overlap_edge_line_lift.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "realized_same_label_gap_defect_readback.json"
EDGE_ORDER = ("psi12", "psi23", "psi31")
EDGE_TO_LABEL = {"psi12": "f1", "psi23": "f2", "psi31": "f3"}
LABEL_TO_INDEX = {"f1": 0, "f2": 1, "f3": 2}


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _shell(payload: dict, arrows: list[str]) -> dict:
    null_map = {arrow: None for arrow in arrows}
    strict_missing = "realized_arrow_pullback_from_flavor_gap_and_defect_certificates"
    return {
        "artifact": "oph_realized_same_label_gap_defect_readback",
        "generated_utc": _timestamp(),
        "proof_status": "candidate_only",
        "payload_status": "reduced_to_strict_smallest_missing_object",
        "source_only_physical_input_eligible": False,
        "source_closure_status": {
            "closed": False,
            "missing_objects": [
                "source_emitted_family_transport_kernel",
                "theorem_grade_overlap_edge_line_lift",
            ],
        },
        "upstream_exact_clause": payload.get("upstream_exact_clause"),
        "same_label_readback_origin": payload.get("same_label_readback_origin"),
        "selector_center": payload.get("selector_center"),
        "kernel_choice": payload.get("kernel_choice"),
        "realized_same_label_arrows": arrows,
        "same_label": dict(null_map),
        "rank_e": dict(null_map),
        "same_label_overlap_sq": dict(null_map),
        "gap_e": dict(null_map),
        "defect_e": dict(null_map),
        "same_label_gap_witness": dict(null_map),
        "same_label_defect_witness": dict(null_map),
        "same_label_defect_rule": payload.get("same_label_defect_rule"),
        "q_e_rule": payload.get("raw_edge_score_rule"),
        "eta_e_rule": payload.get("centered_log_rule"),
        "base_mu_nu": payload.get("base_mu_nu"),
        "mu_e_rule": payload.get("weight_rule"),
        "derived_q_e": dict(null_map),
        "q_mean": None,
        "q_spread": None,
        "q_e": dict(null_map),
        "eta_e": dict(null_map),
        "mu_e": dict(null_map),
        "neutrino_only_isotropy_obstruction": payload.get("neutrino_only_isotropy_obstruction"),
        "smallest_constructive_missing_object": strict_missing,
        "strict_smallest_exact_missing_object": strict_missing,
        "missing_fields_by_arrow": {arrow: ["gap_e", "defect_e"] for arrow in arrows},
        "complete_by_arrow": {arrow: False for arrow in arrows},
        "metadata": {
            "note": "This artifact is now the exact builder-facing shell for the realized-arrow pullback bundle. The downstream neutrino chain is fixed once builder-grade gap_e and defect_e values are populated on the realized same-label arrows.",
        },
    }


def _gap_for_index(eigenvalues: list[float], index: int) -> float:
    anchor = float(eigenvalues[index])
    return min(abs(anchor - float(value)) for idx, value in enumerate(eigenvalues) if idx != index)


def _complete_from_flavor(payload: dict, family_kernel: dict, line_lift: dict) -> dict | None:
    diagonal_entries = {
        str(item["label"]): item for item in line_lift.get("same_label_overlap_by_label_and_refinement_pair", [])
    }
    transport_entries = {
        str(item["label"]): item for item in line_lift.get("transport_partial_isometry_by_label_and_refinement_pair", [])
    }
    refinements = {
        int(item["level"]): item for item in family_kernel.get("refinements", [])
    }
    if not diagonal_entries or not transport_entries or not refinements:
        return None

    base_mu = float(payload.get("base_mu_nu", 0.0))
    same_label: dict[str, str] = {}
    rank_e: dict[str, float] = {}
    overlap_sq: dict[str, float] = {}
    gap_e: dict[str, float] = {}
    defect_e: dict[str, float] = {}
    gap_witness: dict[str, dict] = {}
    defect_witness: dict[str, dict] = {}

    for edge in EDGE_ORDER:
        label = EDGE_TO_LABEL[edge]
        index = LABEL_TO_INDEX[label]
        diagonal = diagonal_entries.get(label)
        transport = transport_entries.get(label)
        if diagonal is None or transport is None:
            return None
        tail_level = int(diagonal["left_refinement_level"])
        head_level = int(diagonal["right_refinement_level"])
        tail_refinement = refinements.get(tail_level)
        head_refinement = refinements.get(head_level)
        if tail_refinement is None or head_refinement is None:
            return None

        tail_eigs = list(tail_refinement.get("eigenvalues", []))
        head_eigs = list(head_refinement.get("eigenvalues", []))
        if len(tail_eigs) != 3 or len(head_eigs) != 3:
            return None

        source_projector = transport.get("source_projector") or {}
        rank_trace = sum(
            float(source_projector.get("real", [[0.0]])[idx][idx])
            for idx in range(min(3, len(source_projector.get("real", []))))
        )
        overlap_value = float(diagonal["chi_diagonal_trace"]["amplitude"])
        defect_value = max(0.0, 1.0 - overlap_value)
        tail_gap = _gap_for_index(tail_eigs, index)
        head_gap = _gap_for_index(head_eigs, index)
        combined_gap = float((tail_gap * head_gap) ** 0.5)

        same_label[edge] = label
        rank_e[edge] = rank_trace if rank_trace > 0.0 else 1.0
        overlap_sq[edge] = overlap_value
        defect_e[edge] = defect_value
        gap_e[edge] = combined_gap
        gap_witness[edge] = {
            "same_label": label,
            "tail_refinement_level": tail_level,
            "head_refinement_level": head_level,
            "tail_eigenvalue": float(tail_eigs[index]),
            "head_eigenvalue": float(head_eigs[index]),
            "tail_gap": float(tail_gap),
            "head_gap": float(head_gap),
            "gap_rule": "g_e = sqrt(gap_tail * gap_head)",
            "source_artifacts": {
                "family_transport_kernel": "oph_family_transport_kernel",
                "overlap_edge_line_lift": "oph_overlap_edge_line_lift",
            },
        }
        defect_witness[edge] = {
            "same_label": label,
            "tail_refinement_level": tail_level,
            "head_refinement_level": head_level,
            "rank_e": rank_e[edge],
            "chi_diagonal_trace": dict(diagonal["chi_diagonal_trace"]),
            "defect_rule": "d_e = 1 - overlap_sq_e",
            "source_artifacts": {
                "overlap_edge_line_lift": "oph_overlap_edge_line_lift",
                "transport_partial_isometry": "same_label_projective_polar_riesz_lift",
            },
        }

    derived_q = {edge: float((gap_e[edge] * defect_e[edge]) ** 0.5) for edge in EDGE_ORDER}
    log_q = {edge: float(math.log(derived_q[edge])) for edge in EDGE_ORDER}
    mean_log_q = sum(log_q.values()) / len(EDGE_ORDER)
    eta_e = {edge: float(log_q[edge] - mean_log_q) for edge in EDGE_ORDER}
    exp_eta = {edge: float(math.exp(eta_e[edge])) for edge in EDGE_ORDER}
    mean_exp_eta = sum(exp_eta.values()) / len(EDGE_ORDER)
    mu_e = {edge: float(base_mu * exp_eta[edge] / mean_exp_eta) for edge in EDGE_ORDER}
    family_kernel_closed = family_kernel.get("source_closure_closed") is True
    line_lift_closed = line_lift.get("source_closure_closed") is True
    source_closed = family_kernel_closed and line_lift_closed
    missing_source_objects = []
    if not family_kernel_closed:
        missing_source_objects.append("source_emitted_family_transport_kernel")
    if not line_lift_closed:
        missing_source_objects.append("theorem_grade_overlap_edge_line_lift")

    return {
        "artifact": "oph_realized_same_label_gap_defect_readback",
        "generated_utc": _timestamp(),
        "proof_status": (
            "derived_from_source_closed_flavor_overlap_and_gap_certificates"
            if source_closed
            else "conditional_numeric_readback_from_template_flavor_artifacts"
        ),
        "payload_status": (
            "complete_from_source_closed_flavor_artifacts"
            if source_closed
            else "complete_numeric_values_source_open"
        ),
        "source_only_physical_input_eligible": source_closed,
        "source_closure_status": {
            "closed": source_closed,
            "family_transport_kernel_status": family_kernel.get("status"),
            "family_transport_kernel_proof_status": family_kernel.get("proof_status"),
            "family_transport_kernel_explicit_source_closure": family_kernel_closed,
            "overlap_edge_line_lift_proof_status": line_lift.get("proof_status"),
            "overlap_edge_line_lift_explicit_source_closure": line_lift_closed,
            "missing_objects": missing_source_objects,
        },
        "upstream_exact_clause": payload.get("upstream_exact_clause"),
        "same_label_readback_origin": "realized_arrow_pullback_from_flavor_gap_and_defect_certificates",
        "selector_center": payload.get("selector_center"),
        "kernel_choice": payload.get("kernel_choice"),
        "realized_same_label_arrows": list(EDGE_ORDER),
        "same_label": same_label,
        "rank_e": rank_e,
        "same_label_overlap_sq": overlap_sq,
        "gap_e": gap_e,
        "defect_e": defect_e,
        "same_label_gap_witness": gap_witness,
        "same_label_defect_witness": defect_witness,
        "same_label_defect_rule": payload.get("same_label_defect_rule"),
        "q_e_rule": payload.get("raw_edge_score_rule"),
        "eta_e_rule": payload.get("centered_log_rule"),
        "base_mu_nu": base_mu,
        "mu_e_rule": payload.get("weight_rule"),
        "derived_q_e": derived_q,
        "q_mean": float(sum(derived_q.values()) / len(EDGE_ORDER)),
        "q_spread": float(max(derived_q.values()) - min(derived_q.values())),
        "q_e": derived_q,
        "eta_e": eta_e,
        "mu_e": mu_e,
        "neutrino_only_isotropy_obstruction": False,
        "smallest_constructive_missing_object": None,
        "strict_smallest_exact_missing_object": None,
        "missing_fields_by_arrow": {edge: [] for edge in EDGE_ORDER},
        "complete_by_arrow": {edge: True for edge in EDGE_ORDER},
        "metadata": {
            "note": (
                "The same-label pullback is numerically complete on ordered labels f1,f2,f3, but physical source closure follows the family-kernel and line-lift gates."
            ),
            "source_artifacts": [
                "oph_defect_weighted_majorana_edge_weight_family",
                "oph_family_transport_kernel",
                "oph_overlap_edge_line_lift",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the realized same-label gap/defect readback artifact.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--family-kernel", default=str(DEFAULT_FAMILY_KERNEL))
    parser.add_argument("--line-lift", default=str(DEFAULT_LINE_LIFT))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = _load_json(Path(args.input))
    arrows = list(payload.get("realized_same_label_arrows", EDGE_ORDER))

    artifact = None
    family_kernel_path = Path(args.family_kernel)
    line_lift_path = Path(args.line_lift)
    if family_kernel_path.exists() and line_lift_path.exists():
        artifact = _complete_from_flavor(
            payload,
            _load_json(family_kernel_path),
            _load_json(line_lift_path),
        )
    if artifact is None:
        artifact = _shell(payload, arrows)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
