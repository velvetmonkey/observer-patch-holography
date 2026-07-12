#!/usr/bin/env python3
"""Fifth K1 execution: population-transfer kernel from timeline dynamics (#377).

Readouts #1, #2, and #4 probed static or spatial structure and landed on
nulls; the worldline jump chain (#3) is blocked because the realized
dynamics resolves no deaths or contacts. This module executes the first
genuinely temporal readout: the lag-one transfer operator of the realized
class-population dynamics, in the vacuum-inclusive three-channel basis
where the two-species cap of the defect sector does not apply.

Predeclaration (fixed before computation):

  data         the dense defect-timeline report of a universe run with
               per-cycle snapshots (the sample count equals the cycle
               count). Populations are measured on the sim's own
               fixed-size triangle sample per snapshot, so units are
               consistent across cycles.
  channels     the population 3-vector p(t) = (n_identity, n_transposition,
               n_threecycle) in triangle units per snapshot: n_identity is
               triangle_count minus defect_triangle_count; the defect
               split is defect_triangle_count apportioned by the class
               shares of cluster support nodes (declared estimator; a
               snapshot with no defect nodes gets zero for both defect
               channels). The vacuum channel is included deliberately:
               class functions on the two defect species alone span two
               dimensions, and only the vacuum-inclusive basis can host a
               three-dimensional carrier. The identification of these
               channels with the generation carrier is a CANDIDATE CLAIM.
  series       primary: componentwise log of p(t) (multiplicative
               population dynamics, and the flavor lane lives in log
               space); if any component is nonpositive anywhere the
               declared fallback is the raw series, recorded in the
               artifact. Raw is the predeclared robustness alternate.
  transfer     centered fluctuations delta(t); the VAR(1) least-squares
               transfer operator A = C1 C0^{-1} with C0 the equal-time
               and C1 the lag-one second moment; the condition number of
               C0 is reported.
  descendant   D = A A^t, the schema's T T-dagger rule.
  levels       level 0 = the estimate on the first half of the snapshots,
               level 1 = the full-series estimate (estimator refinement;
               the branch-generator convention reads the spectrum from
               the latest level).
  nulls        time shuffles of the snapshot order (seeds 1, 2, 3), which
               keep the marginal distribution and destroy the dynamics;
               the physical-versus-shuffle contrast in both the operator
               norm of A and the shape invariants carries the evidential
               weight. Context row: white noise has A = 0 exactly.
  verdict      level-1 rho_ord of D against the quoted-convention band,
               plus the acceptance-harness record (G4 blocking stays the
               expected fail-closed outcome; no K2 clause exists).

No quark mass, fitted spread, or flavor template enters any step.

Run:
    python3 code/particles/flavor/derive_family_transport_kernel_from_sim_population_transfer.py \
        --run-dir <sim run dir> [--out-suffix _4k]
writes code/particles/runs/flavor/family_transport_kernel_sim_population_computed<suffix>.json
and    code/particles/runs/flavor/family_transport_kernel_sim_population_verdict<suffix>.json.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
RER_ROOT = HERE.parents[2]
SIM_ROOT = HERE.parents[3] / "oph-physics-sim"
RUNS = RER_ROOT / "code" / "particles" / "runs" / "flavor"
SCAN_PATH = RUNS / "quark_common_scheme_shape_law_scan.json"
DEFAULT_RUN_DIR = SIM_ROOT / "runs" / "k1_population_transfer_4k_dense_20260712"

SHUFFLE_SEEDS = (1, 2, 3)

sys.path.insert(0, str(HERE))
from derive_generation_bundle_branch_generator import (  # noqa: E402
    build_artifact as build_generator,
)
from derive_quark_kernel_normalization_acceptance_harness import (  # noqa: E402
    evaluate as harness_evaluate,
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _encode(matrix: np.ndarray) -> dict:
    m = matrix.astype(complex)
    return {"real": np.real(m).tolist(), "imag": np.imag(m).tolist()}


def load_population_series(run_dir: pathlib.Path) -> dict:
    report = json.loads((run_dir / "defect_timeline_report.json")
                        .read_text(encoding="utf-8"))
    rows = []
    for snap in report["snapshots"]:
        total = float(snap["triangle_count"])
        defect = float(snap["defect_triangle_count"])
        nodes = {"transposition": 0.0, "threecycle": 0.0}
        for cluster in snap["clusters"]:
            label = cluster["class"]
            if label in nodes:
                nodes[label] += float(cluster["support_node_count"])
        node_sum = nodes["transposition"] + nodes["threecycle"]
        if node_sum > 0.0:
            n_t = defect * nodes["transposition"] / node_sum
            n_3 = defect * nodes["threecycle"] / node_sum
        else:
            n_t = n_3 = 0.0
        rows.append((int(snap["cycle"]), total - defect, n_t, n_3))
    rows.sort()
    cycles = [r[0] for r in rows]
    series = np.asarray([[r[1], r[2], r[3]] for r in rows], dtype=float)
    return {"cycles": cycles, "series": series,
            "snapshot_count": len(rows),
            "timeline_mode": report.get("mode")}


def var1_transfer(series: np.ndarray) -> dict:
    centered = series - series.mean(axis=0, keepdims=True)
    x0 = centered[:-1]
    x1 = centered[1:]
    c0 = x0.T @ x0
    c1 = x1.T @ x0
    cond = float(np.linalg.cond(c0))
    a = c1 @ np.linalg.inv(c0)
    residual = x1 - x0 @ a.T
    r2 = 1.0 - float((residual ** 2).sum()) / float((x1 ** 2).sum())
    return {"A": a, "cond_C0": cond, "operator_norm_A": float(
        np.linalg.norm(a, ord=2)), "lag1_r2": r2}


def readout(d: np.ndarray) -> dict:
    centered = d - (np.trace(d) / 3.0) * np.eye(3)
    evals = np.linalg.eigvalsh(centered)
    g21 = float(evals[1] - evals[0])
    g32 = float(evals[2] - evals[1])
    r = g21 / g32 if g32 > 0 else float("inf")
    return {
        "eigenvalues_centered": [float(x) for x in evals],
        "g21": g21, "g32": g32,
        "raw_gap_ratio_r": r,
        "rho_ord": 3.0 * g32 / (2.0 * g32 + g21) if (2.0 * g32 + g21) > 0
                   else float("nan"),
        "x2": (r - 1.0) / (r + 1.0) if np.isfinite(r) else float("nan"),
        "span": float(evals[2] - evals[0]),
    }


def transfer_block(series: np.ndarray) -> dict:
    fit = var1_transfer(series)
    d = fit["A"] @ fit["A"].T
    return {**{k: v for k, v in fit.items() if k != "A"},
            "A": fit["A"].tolist(),
            "descendant": d,
            "readout": readout(d)}


def build(run_dir: pathlib.Path) -> tuple[dict, dict, dict]:
    state = load_population_series(run_dir)
    series_raw = state["series"]
    if series_raw.shape[0] < 24:
        raise SystemExit(f"only {series_raw.shape[0]} snapshots; the dense "
                         "timeline is required for this readout")
    log_ok = bool((series_raw > 0.0).all())
    primary = np.log(series_raw) if log_ok else series_raw

    half = series_raw.shape[0] // 2
    level0 = transfer_block(primary[:half])
    level1 = transfer_block(primary)

    nulls = {}
    for seed in SHUFFLE_SEEDS:
        rng = np.random.default_rng(seed)
        shuffled = primary[rng.permutation(primary.shape[0])]
        block = transfer_block(shuffled)
        nulls[f"time_shuffle_seed{seed}"] = {
            "operator_norm_A": block["operator_norm_A"],
            "lag1_r2": block["lag1_r2"],
            **block["readout"]}
    robustness = transfer_block(series_raw)

    scan = json.loads(SCAN_PATH.read_text(encoding="utf-8"))
    band = scan["findings"]["a2_band_by_convention"]["quoted_mixed"]
    template_rho = float(scan["template_rho_ord"])
    phys = level1["readout"]

    run_id = run_dir.name
    payload = {
        "artifact": "oph_family_transport_kernel",
        "generated_utc": _timestamp(),
        "status": "computed_sim_population_transfer_candidate",
        "transport_kind": "vacuum_inclusive_class_population_var1_transfer",
        "proof_status": "computed_candidate_carrier_identification_open",
        "carrier_identification": {
            "claim": "the vacuum-inclusive class-population channels are "
                     "the same-label generation carrier",
            "status": "candidate_claim_not_theorem",
            "dimensional_note": "the vacuum channel is included because "
                                "class functions on the two defect "
                                "species alone span two dimensions",
        },
        "refinements": [
            {"level": 0, "run_id": run_id,
             "snapshots_used": half,
             "hermitian_descendant": _encode(np.asarray(level0["descendant"]))},
            {"level": 1, "run_id": run_id,
             "snapshots_used": int(series_raw.shape[0]),
             "hermitian_descendant": _encode(np.asarray(level1["descendant"]))},
        ],
        "refinement_intertwiners": [
            {"from_level": 0, "to_level": 1,
             "intertwiner": _encode(np.eye(3)),
             "justification": "canonical channel frame across estimator "
                              "refinement"},
        ],
        "ancestry": {
            "artifacts": [f"defect_timeline_report({run_id})"],
            "attestations": {
                "quark_reference_values_consumed": False,
                "fitted_spreads_consumed": False,
                "numerical_flavor_template_consumed": False,
            },
        },
        "metadata": {
            "note": "Readout #5 of the issue-377 K1 program: the VAR(1) "
                    "transfer operator of the realized vacuum-inclusive "
                    "class-population dynamics on a dense timeline. "
                    "Carrier identification and the K2 scale clause stay "
                    "open.",
        },
    }

    generator = build_generator(payload)
    gates = harness_evaluate({
        "candidate_id": f"sim_population_transfer_kernel({run_id})",
        "kernel": {"refinements": payload["refinements"]},
        "ancestry": payload["ancestry"],
    })

    verdict = {
        "artifact": "oph_family_transport_kernel_sim_population_verdict",
        "generated_utc": _timestamp(),
        "github_issues": [377, 379, 380],
        "row_class": "computed_candidate_shape_milestone",
        "run_id": run_id,
        "guards": {
            "quark_reference_values_consumed": False,
            "fitted_spreads_consumed": False,
            "numerical_flavor_template_consumed": False,
            "public_promotion_allowed": False,
            "post_hoc_construction_changes": "none; predeclared in the "
                                             "module docstring",
        },
        "series_summary": {
            "snapshot_count": state["snapshot_count"],
            "log_series_used": log_ok,
            "population_means": series_raw.mean(axis=0).tolist(),
            "population_stds": series_raw.std(axis=0).tolist(),
        },
        "levels": {
            "level0_first_half": {
                "snapshots": half,
                "operator_norm_A": level0["operator_norm_A"],
                "lag1_r2": level0["lag1_r2"],
                "cond_C0": level0["cond_C0"],
                **level0["readout"]},
            "level1_full": {
                "snapshots": int(series_raw.shape[0]),
                "operator_norm_A": level1["operator_norm_A"],
                "lag1_r2": level1["lag1_r2"],
                "cond_C0": level1["cond_C0"],
                **level1["readout"]},
        },
        "nulls": nulls,
        "robustness_raw_series": {
            "operator_norm_A": robustness["operator_norm_A"],
            "lag1_r2": robustness["lag1_r2"],
            **robustness["readout"]},
        "band_check": {
            "declared_convention_band": band,
            "template_rho_ord": template_rho,
            "computed_rho_ord_level1": phys["rho_ord"],
            "inside_band": bool(band[0] <= phys["rho_ord"] <= band[1]),
            "physical_minus_template": phys["rho_ord"] - template_rho,
        },
        "harness_gates": gates,
        "generator_proof_status": generator.get("proof_status"),
    }
    return payload, verdict, generator


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute the population-transfer kernel from a dense "
                    "sim timeline.")
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    parser.add_argument("--out-suffix", default="")
    args = parser.parse_args()

    run_dir = pathlib.Path(args.run_dir)
    if not (run_dir / "defect_timeline_report.json").exists():
        raise SystemExit(f"missing defect_timeline_report.json in {run_dir}")

    payload, verdict, generator = build(run_dir)
    suffix = args.out_suffix
    paths = {
        "payload": RUNS / f"family_transport_kernel_sim_population_computed{suffix}.json",
        "verdict": RUNS / f"family_transport_kernel_sim_population_verdict{suffix}.json",
        "generator": RUNS / f"generation_bundle_branch_generator_sim_population{suffix}.json",
    }
    for key, blob in (("payload", payload), ("verdict", verdict),
                      ("generator", generator)):
        paths[key].parent.mkdir(parents=True, exist_ok=True)
        paths[key].write_text(json.dumps(blob, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")

    ss = verdict["series_summary"]
    print(f"run: {verdict['run_id']}  snapshots: {ss['snapshot_count']}  "
          f"log_series: {ss['log_series_used']}")
    print(f"population means (e, t, 3): {['%.1f' % v for v in ss['population_means']]}")
    for name, row in verdict["levels"].items():
        print(f"{name}: ||A|| = {row['operator_norm_A']:.4f}  R2 = {row['lag1_r2']:.4f}  "
              f"r = {row['raw_gap_ratio_r']:.6f}  rho_ord = {row['rho_ord']:.6f}")
    bc = verdict["band_check"]
    print(f"band {bc['declared_convention_band']}  template {bc['template_rho_ord']:.6f}")
    print(f"COMPUTED rho_ord = {bc['computed_rho_ord_level1']:.6f}  "
          f"inside_band = {bc['inside_band']}")
    print("nulls:")
    for name, row in verdict["nulls"].items():
        print(f"  {name:24s} ||A|| = {row['operator_norm_A']:.4f}  "
              f"rho_ord = {row['rho_ord']:.6f}")
    print(f"raw-series robustness: rho_ord = "
          f"{verdict['robustness_raw_series']['rho_ord']:.6f}")
    print(f"harness: first_failed_gate = {verdict['harness_gates']['first_failed_gate']}  "
          f"status = {verdict['harness_gates']['status']}")
    for key, path in paths.items():
        print(f"saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
