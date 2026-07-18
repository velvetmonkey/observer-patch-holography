#!/usr/bin/env python3
"""Compare the emitted source-only D10 transport to the required common transport.

Chain role: diagnose whether the current source-only nonzero D10 transport law
actually reproduces the unique common transport needed to match the benchmark
W/Z pair for a given pixel constant `P`.

Mathematics: build the exact D10 running family from `P`, lift it to the
current two-scalar source pair, emit the current source-only transport law, and
compare it against the unique reference-fitted common transport that would hit the
benchmark `W/Z` pair on the same family.

OPH-derived inputs: `P` and the D10 running family. The benchmark pair is used
only as a compare-only diagnostic to reveal the common transport gap.

Output: one machine-readable gap report between the emitted source-only common
transport candidate and the benchmark-required common transport.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from derive_d10_ew_observable_family import P_DEFAULT, build_artifact as build_observable_family
from derive_d10_ew_source_transport_pair import build_artifact as build_source_pair
from derive_d10_ew_target_free_repair_value_law import build_artifact as build_target_free_repair
from derive_d10_ew_w_anchor_neutral_shear_factorization import (
    _load_basis,
    build_factorization_report,
)


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_JSON = ROOT / "particles" / "data" / "particle_reference_values.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "calibration" / "d10_ew_common_transport_gap_report.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_references(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["entries"]


def build_artifact(p_value: float, references: dict) -> dict[str, object]:
    family = build_observable_family(p_value)
    source_pair = build_source_pair(family)
    basis = _load_basis(source_pair)
    required_transport = build_factorization_report(references, basis)
    emitted_transport = build_target_free_repair(source_pair, references)

    required_point = dict(required_transport["central_target_point"])
    emitted_chart = dict(emitted_transport["repair_chart"])
    emitted_couplings = dict(emitted_transport["repaired_couplings"])
    emitted_quintet = dict(emitted_transport["coherent_emitted_quintet"])
    benchmark = dict(emitted_transport["compare_only_validation_against_frozen_surface"])
    running = dict(family["reported_outputs"])

    required_alpha2 = float(required_point["alpha2_dagger"])
    required_alphaY = float(required_point["alphaY_dagger"])
    emitted_alpha2 = float(emitted_couplings["alpha2_prime"])
    emitted_alphaY = float(emitted_couplings["alphaY_prime"])
    chart_gap_tau2 = float(emitted_chart["tau2_tree_exact"]) - float(required_point["tau2_w_anchor"])
    chart_gap_delta_n = float(emitted_chart["delta_n_tree_exact"]) - float(required_point["delta_n_tree_exact"])
    mass_gap_w = float(benchmark["delta_MW_gev"])
    mass_gap_z = float(benchmark["delta_MZ_gev"])

    max_chart_gap = max(abs(chart_gap_tau2), abs(chart_gap_delta_n))
    max_mass_gap_mev = 1000.0 * max(abs(mass_gap_w), abs(mass_gap_z))
    if max_chart_gap < 1.0e-9 and max_mass_gap_mev < 1.0e-3:
        verdict = "matches_required_benchmark_transport"
    elif max_mass_gap_mev < 1.0:
        verdict = "near_match_but_not_exact"
    else:
        verdict = "fails_required_benchmark_transport"

    return {
        "artifact": "oph_d10_ew_common_transport_gap_report",
        "generated_utc": _timestamp(),
        "status": "compare_only_diagnostic",
        "p": p_value,
        "family_source_id": family["observable_family_id"],
        "benchmark_reference_surface": {
            "MW_pole_gev": float(benchmark["MW_reference_gev"]),
            "MZ_pole_gev": float(benchmark["MZ_reference_gev"]),
            "source_label": references["w_boson"]["source"]["label"],
            "w_summary_id": references["w_boson"]["source"]["summary_id"],
            "z_summary_id": references["z_boson"]["source"]["summary_id"],
        },
        "running_family": {
            "MW_run_gev": float(running["m_w_run"]),
            "MZ_run_gev": float(running["m_z_run"]),
            "alpha_em_inv_mz": float(running["alpha_em_inv_mz"]),
            "sin2w_mz": float(running["sin2w_mz"]),
            "v_report_gev": float(running["v"]),
        },
        "required_common_transport": {
            "chart_coordinates": {
                "tau2_tree_exact": float(required_point["tau2_w_anchor"]),
                "delta_n_tree_exact": float(required_point["delta_n_tree_exact"]),
            },
            "repaired_couplings": {
                "alpha2_prime": required_alpha2,
                "alphaY_prime": required_alphaY,
            },
            "coherent_output_quintet": {
                "MW_pole": float(required_transport["coherent_repaired_quintet"]["MW_pole"]),
                "MZ_pole": float(required_transport["coherent_repaired_quintet"]["MZ_pole"]),
                "alpha_em_eff_inv": float(required_transport["coherent_repaired_quintet"]["alpha_em_eff_inv"]),
                "sin2w_eff": float(required_transport["coherent_repaired_quintet"]["sin2w_eff"]),
                "v_report": float(required_transport["coherent_repaired_quintet"]["v_report"]),
            },
            "kind": "freeze_once_compare_only_required_transport",
        },
        "emitted_source_only_transport": {
            "chart_coordinates": {
                "tau2_tree_exact": float(emitted_chart["tau2_tree_exact"]),
                "delta_n_tree_exact": float(emitted_chart["delta_n_tree_exact"]),
            },
            "repaired_couplings": {
                "alpha2_prime": emitted_alpha2,
                "alphaY_prime": emitted_alphaY,
            },
            "coherent_output_quintet": {
                "MW_pole": float(emitted_quintet["MW_pole"]),
                "MZ_pole": float(emitted_quintet["MZ_pole"]),
                "alpha_em_eff_inv": float(emitted_quintet["alpha_em_eff_inv"]),
                "sin2w_eff": float(emitted_quintet["sin2w_eff"]),
                "v_report": float(emitted_quintet["v_report"]),
            },
            "kind": "current_source_only_transport_candidate",
        },
        "transport_gap": {
            "tau2_tree_exact": chart_gap_tau2,
            "delta_n_tree_exact": chart_gap_delta_n,
            "alpha2_prime": emitted_alpha2 - required_alpha2,
            "alphaY_prime": emitted_alphaY - required_alphaY,
        },
        "observable_gap_to_benchmark": {
            "MW_pole_gev": mass_gap_w,
            "MZ_pole_gev": mass_gap_z,
            "alpha_em_eff_inv": float(benchmark["delta_alpha_em_eff_inv"]),
            "sin2w_eff": float(benchmark["delta_sin2w_eff"]),
            "max_mass_gap_mev": max_mass_gap_mev,
        },
        "verdict": {
            "classification": verdict,
            "max_chart_gap": max_chart_gap,
            "max_mass_gap_mev": max_mass_gap_mev,
            "default_p_behavior_note": (
                "At the repo default P the current source-only law nearly reproduces the benchmark-required transport."
                if verdict == "matches_required_benchmark_transport"
                else "At this P the current source-only law does not reproduce the benchmark-required transport."
            ),
        },
        "notes": [
            "This artifact is compare-only: the required common transport uses benchmark W/Z values as inputs and is not a source-only OPH prediction.",
            "The current source-only transport is supported only to the extent that it is emitted from the D10 source basis with no frozen benchmark input.",
            "A robust common transport law should keep this gap small for the physically derived P; if the gap grows materially, the source-only transport formulas are not yet the right running-to-pole map.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the D10 common-transport gap report.")
    parser.add_argument("--p", type=float, default=P_DEFAULT)
    parser.add_argument("--references", default=str(REFERENCE_JSON))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    artifact = build_artifact(args.p, _load_references(Path(args.references)))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
