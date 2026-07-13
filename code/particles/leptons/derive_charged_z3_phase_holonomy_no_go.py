#!/usr/bin/env python3
"""Certify that the current OPH data do not select the Stage-5 phase 2/9."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "leptons"
    / "charged_z3_phase_holonomy_no_go.json"
)


def roots(delta: float) -> list[float]:
    return sorted(
        1.0 + math.sqrt(2.0) * math.cos(delta + 2.0 * math.pi * k / 3.0)
        for k in range(3)
    )


def trace_invariants(delta: float) -> tuple[float, float]:
    values = roots(delta)
    return sum(values), sum(value * value for value in values)


def physical_koide(delta: float) -> float:
    """Koide invariant for m_i=r_i^2, with physical roots sqrt(m_i)=|r_i|."""

    values = roots(delta)
    return sum(value * value for value in values) / sum(abs(value) for value in values) ** 2


def positive_chamber(delta: float, tolerance: float = 1.0e-14) -> bool:
    """Balanced-circulant positivity: |delta|<=pi/12 modulo 2*pi/3."""

    period = 2.0 * math.pi / 3.0
    representative = (delta + period / 2.0) % period - period / 2.0
    return abs(representative) <= math.pi / 12.0 + tolerance


def build_artifact() -> dict[str, Any]:
    controls = {}
    for label, delta in (("identity_transport", 0.0), ("stage5", 2.0 / 9.0)):
        values = roots(delta)
        trace_one, trace_two = trace_invariants(delta)
        controls[label] = {
            "delta_radians": delta,
            "positive_roots": all(value > 0.0 for value in values),
            "ordered_roots": values,
            "trace": trace_one,
            "trace_square": trace_two,
            "signed_trace_Q": trace_two / (trace_one * trace_one),
            "physical_Q": physical_koide(delta),
            "inside_positive_chamber": positive_chamber(delta),
        }
    outside_delta = 0.4
    outside_values = roots(outside_delta)
    stage5_delta = 2.0 / 9.0
    c3_character_phases = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)
    return {
        "artifact": "oph_charged_z3_phase_holonomy_no_go",
        "status": "CLOSED_NO_GO_CURRENT_OPH_DATA_LEAVE_PHASE_CONTINUOUS",
        "public_phase_promotion_allowed": False,
        "countermodels": controls,
        "theorem": {
            "statement": (
                "The balanced Hermitian Z3 circulant has signed trace 3 and squared trace 6 "
                "for every phase delta. On the positive-root chamber |delta|<=pi/12 modulo "
                "2*pi/3, this is the physical Koide relation Q=2/3. A continuum of positive "
                "phases remains, so balance, Z3 symmetry, positivity, and the current invariant "
                "counts do not select delta=2/9."
            ),
            "positive_root_chamber": "|delta| <= pi/12 modulo 2*pi/3",
            "physical_loop_invariant": "arg(C_12 C_23 C_31)=3 delta mod 2 pi",
            "family_gauge_boundary": (
                "Hypercharge acts on three generation copies as exp(i Y theta) I_3 and supplies "
                "a common phase, not the cyclic family shift."
            ),
        },
        "signed_root_boundary": {
            "delta_outside_positive_chamber": outside_delta,
            "signed_roots": outside_values,
            "signed_trace_Q": trace_invariants(outside_delta)[1]
            / trace_invariants(outside_delta)[0] ** 2,
            "physical_Q": physical_koide(outside_delta),
            "statement": (
                "Outside the positive chamber, sqrt(m_i)=|r_i|. The signed trace identity "
                "therefore ceases to equal the physical Koide invariant."
            ),
        },
        "finite_geometry_phase_no_go": {
            "A5_abelianization": "trivial",
            "A5_consequence": "A5 has no nontrivial U(1) character",
            "C3_character_phases_mod_2pi": list(c3_character_phases),
            "stage5_phase": stage5_delta,
            "stage5_equal_link_phase_is_C3_character": any(
                math.isclose(
                    stage5_delta % (2.0 * math.pi),
                    phase,
                    rel_tol=0.0,
                    abs_tol=1.0e-14,
                )
                for phase in c3_character_phases
            ),
            "stage5_loop_phase": 3.0 * stage5_delta,
            "statement": (
                "Pure A5/C3 finite geometry cannot emit delta=2/9 as a character holonomy. "
                "A5 has trivial abelianization, while a C3 character gives only cube-root "
                "phases. A continuous U(1) family connection can carry delta, but then its "
                "action or flux selector is new source data."
            ),
        },
        "missing_source_objects": [
            "a physical C3 generation bundle",
            "a source-emitted oriented U(1) flavor connection and declared loop",
            "a gauge-invariant law fixing the total loop holonomy",
            "an equal-link gauge convention and orientation rule",
            "an attachment of the resulting roots to physical charged-family lines",
        ],
        "claim_boundary": (
            "The arithmetic identity (N_c+1)/(2 N_c N_g)=2/9 is not a phase-transport theorem."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build_artifact()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(artifact["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
