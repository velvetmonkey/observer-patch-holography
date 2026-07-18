#!/usr/bin/env python3
"""Prove that invariant screen and product-adjoint counts cannot split families."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HIERARCHY = (
    ROOT / "particles" / "hierarchy" / "certificates"
    / "R_local_global_hierarchy_resonance_closeout_335.json"
)
SCALARS = (
    ROOT / "particles" / "runs" / "leptons"
    / "charged_sector_local_support_extension_source_scalar_pair_readback.json"
)
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "leptons"
    / "charged_12_24_singlet_no_go.json"
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def centered(values: list[float]) -> list[float]:
    mean = sum(values) / len(values)
    return [value - mean for value in values]


def build_artifact(hierarchy: dict[str, Any], scalars: dict[str, Any]) -> dict[str, Any]:
    sieve = hierarchy["screen_sieve_certificate"]
    round_count = hierarchy["round_count_certificate"]
    ports = int(sieve["orbit_size"])
    screen_slots = 2 * ports
    m_rep = int(round_count["m_rep"])
    if ports != 12 or screen_slots != 24 or m_rep != 24:
        raise ValueError("the declared branches must carry the independent 12/24 counts")

    # A transitive invariant load has one value on every port. Any family-blind
    # equivariant readout therefore gives the same value on all three families.
    test_family_image = [1.0, 1.0, 1.0]
    centered_image = centered(test_family_image)
    return {
        "artifact": "oph_charged_12_24_singlet_no_go",
        "status": "CLOSED_NO_GO_INVARIANT_COUNTS_INSUFFICIENT",
        "public_charged_mass_promotion_allowed": False,
        "hierarchy_inputs": {
            "screen_ports": ports,
            "screen_oriented_slots": screen_slots,
            "screen_register_source": "paper/screen_microphysics_and_observer_synchronization.tex#def:oriented-24-slot-register",
            "product_adjoint_rounds_m_rep": m_rep,
            "product_adjoint_source": "particles/hierarchy/certificates/R_m_rep_24_certificate.json",
            "screen_action": "transitive_A5_over_C5_orbit",
            "load_rule": "invariant_scalar_X_maps_to_X_over_12_per_port",
            "count_relation": "equal_cardinalities_without_physical_identification",
            "hierarchy_readout": "conditional_on_HIERARCHY-SCREEN-READOUT",
        },
        "theorem": {
            "id": "invariant_12_24_singlet_cannot_emit_charged_family_shape",
            "statement": (
                "Let the twelve screen ports carry the transitive A5/C5 action used by "
                "the screen sieve, and let its oriented 24-slot register remain count-only. "
                "Let the independently derived product-adjoint round count m_rep=24 remain "
                "family-blind. Any equivariant readout of these invariant data into a transitive three-family carrier has "
                "image proportional to (1,1,1). Its centered projection is zero. Hence the "
                "counts emit no charged-family shape scalar. Their common electroweak-scale "
                "interpretation is conditional on HIERARCHY-SCREEN-READOUT."
            ),
            "proof": [
                "Transitivity makes the invariant subspace of the twelve-port permutation representation one-dimensional, spanned by the all-ones vector.",
                "The declared screen sieve retains exactly this invariant component through X -> X/12.",
                "The screen's oriented 24-slot register supplies no family-labelled non-singlet record.",
                "The independent product-adjoint m_rep=24 count fixes a conditional tick exponent but supplies no family attachment.",
                "Equality of the two 24-counts supplies no map between their carriers.",
                "Equivariance and absence of a marked family force the three-family image to be proportional to (1,1,1).",
                "Centering removes that image, so both independent coordinates of the three-family sum-zero plane vanish.",
            ],
            "centered_equal_family_image": centered_image,
            "forced_shape_on_invariant_branch": {
                "eta_source_support_extension_log_per_side": 0.0,
                "sigma_source_support_extension_total_log_per_side": 0.0,
                "mass_ratio_class": "1:1:1",
            },
        },
        "comparison_with_live_gap": {
            "eta_live": scalars.get("eta_source_support_extension_log_per_side"),
            "sigma_live": scalars.get("sigma_source_support_extension_total_log_per_side"),
            "scalar_slot_status": "work_in_progress",
            "conclusion": "the invariant screen and product-adjoint counts do not populate the two scalar slots",
        },
        "required_completion_theorem": {
            "id": "charged_family_non_singlet_port_attachment",
            "required_objects": [
                "a refinement-stable non-singlet moment of the twelve-port or oriented-repair record",
                "an ID-independent equivariant attachment from that moment to three physical charged-family lines",
                "two independent centered readouts spanning the charged-family sum-zero plane",
                "a no-target-leak receipt proving the attachment was fixed before charged-mass comparison",
            ],
            "unselected_representation_options": ["A5 irrep 3", "A5 irrep 3-prime", "other derived three-family carrier"],
            "warning": "choosing an irrep or attachment because it reproduces lepton masses would be target fitting",
        },
        "claim_boundary": (
            "The screen and product-adjoint counts are independent invariant data. A derived "
            "non-singlet family attachment is work in progress. Conditional on "
            "HIERARCHY-SCREEN-READOUT, the common scale remains family-blind and does not emit "
            "the charged-lepton hierarchy."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hierarchy", type=Path, default=HIERARCHY)
    parser.add_argument("--scalars", type=Path, default=SCALARS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build_artifact(_load(args.hierarchy), _load(args.scalars))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(artifact["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
