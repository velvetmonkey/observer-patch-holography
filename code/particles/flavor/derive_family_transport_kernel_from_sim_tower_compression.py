#!/usr/bin/env python3
"""Fourth K1 execution: tower-compression kernel from one realized state (#377).

Carrier readouts #1 and #2 probed single-level final-state statistics and
died on a conservation null and an exact Haar null. This module executes
readout #4, the first construction that measures the DEFINED object:
transport between refinement levels. Both levels come from one realized
state, coarse-grained by the faithful state-preserving conditional
expectation of the multiresolution tower (the commutative cell sector of
oph_fpe/scale/reference_tower.py semantics, with the two defining
identities executed as receipts instead of imported dense-matrix code,
which is infeasible at 65536 dimensions).

Predeclaration (fixed before computation):

  state        one realized universe run carrying both the S3 gauge state
               export (left, right, gauge, points) and the freezeout cell
               fields (cumulative_repair_load, points). The verdict-bearing
               state is the finest such run available at execution time;
               every coarser run is a robustness row.
  cell sector  each cell's label is the majority S3 conjugacy class among
               its incident edges (classes via the sim's own S3_CLASS
               table, loaded from the sim source to prevent drift), ties
               broken toward the smaller class id; the tie fraction is
               reported. The identification of the three cell sectors
               with the generation carrier is a CANDIDATE CLAIM.
  density      declared primary was cumulative_repair_load; the exported
               field turned out to be a signed zero-mean standardized
               fluctuation (54.5 percent negative mass), which is not a
               state weight, so the documented pre-spectrum fallback is
               the geometric state measure cell_area_planck (nonnegative
               by construction). Uniform density is the predeclared
               robustness alternate. Blocks whose total mu vanishes fall
               back to uniform weights inside that block and are counted
               in the artifact.
  levels       two block coarsenings of the same state at predeclared
               ratios: level 0 with N/64 blocks, level 1 with N/16
               blocks. Block centers are the cells with index divisible
               by the ratio in the sim's own cell enumeration; every cell
               joins its nearest center in the run's point geometry. The
               branch-generator convention reads the spectrum from the
               latest level (N/16).
  channel      E = mu-weighted block averaging, the faithful conditional
               expectation onto the block algebra. Receipts executed per
               level: idempotence E(E f) = E f and state preservation
               mu(E f) = mu(f) to 1e-10.
  kernel       K[a,b] = <P_a, E P_b>_mu / mu(total), the sector block of
               the coarse-graining channel. E is self-adjoint and
               idempotent for mu, so K is the Gram matrix of the
               coarse-grained sector indicators: symmetric, positive
               semidefinite, with no forced sum-to-zero null. K is the
               hermitian descendant directly.
  nulls        (a) cell-label shuffles (three fixed seeds): kill sector
               geometry, keep marginals and density; (b) uniform-density
               variant; (c) closed-form context rows: the fully mixed
               limit K = w w^t (rank one) and the fully clustered limit
               K = diag(w), whose spectra bracket the mixing range.
  verdict      level-1 rho_ord against the quoted-convention band of the
               common-scheme scan plus the acceptance-harness record.
               G4 blocking stays the expected fail-closed outcome (no K2
               clause exists). Band membership alone stays weak evidence;
               the physical-versus-shuffle contrast carries the weight.

No quark mass, fitted spread, or flavor template enters any step.

Run:
    python3 code/particles/flavor/derive_family_transport_kernel_from_sim_tower_compression.py \
        --run-dir <sim run dir> [--out-suffix _4k]
writes code/particles/runs/flavor/family_transport_kernel_sim_tower_computed<suffix>.json
and    code/particles/runs/flavor/family_transport_kernel_sim_tower_verdict<suffix>.json.
"""

from __future__ import annotations

import argparse
import importlib.util
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
DEFAULT_RUN_DIR = SIM_ROOT / "runs" / "k1_fusion_universe_64k_20260712"

BLOCK_RATIOS = (64, 16)          # level 0, level 1
SHUFFLE_SEEDS = (1, 2, 3)
RECEIPT_TOL = 1.0e-10

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


def _load_s3_class_table() -> np.ndarray:
    spec = importlib.util.spec_from_file_location(
        "array_s3_holonomy", SIM_ROOT / "oph_fpe" / "defects" / "array_s3_holonomy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return np.asarray(module.S3_CLASS, dtype=np.int64)


def load_state(run_dir: pathlib.Path) -> dict:
    gauge_state = np.load(run_dir / "s3_gauge_state.npz")
    fields = np.load(run_dir / "freezeout_fields.npz")
    points = np.asarray(gauge_state["points"], dtype=float)
    fpoints = np.asarray(fields["points"], dtype=float)
    if points.shape != fpoints.shape or not np.allclose(points, fpoints, atol=1.0e-4):
        raise AssertionError("gauge-state and freezeout cell enumerations disagree")
    s3_class = _load_s3_class_table()
    left = np.asarray(gauge_state["left"], dtype=np.int64)
    right = np.asarray(gauge_state["right"], dtype=np.int64)
    edge_class = s3_class[np.asarray(gauge_state["gauge"], dtype=np.int64)]

    n = points.shape[0]
    counts = np.zeros((n, 3), dtype=np.int64)
    for endpoint in (left, right):
        np.add.at(counts, (endpoint, edge_class), 1)
    top = counts.max(axis=1, keepdims=True)
    ties = (counts == top).sum(axis=1) > 1
    cell_class = counts.argmax(axis=1)          # argmax takes the smaller id on ties
    mu = np.asarray(fields["cell_area_planck"], dtype=float)
    if mu.min() < 0.0:
        raise AssertionError("cell area measure has negative entries")
    return {
        "n_cells": n,
        "points": points,
        "cell_class": cell_class,
        "tie_fraction": float(ties.mean()),
        "mu": mu,
        "class_weights_mu": [
            float(mu[cell_class == a].sum() / mu.sum()) for a in range(3)],
    }


def block_assignment(points: np.ndarray, ratio: int) -> np.ndarray:
    centers = points[::ratio]
    labels = np.empty(points.shape[0], dtype=np.int64)
    chunk = 4096
    for start in range(0, points.shape[0], chunk):
        block = points[start:start + chunk]
        d2 = ((block[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels[start:start + chunk] = d2.argmin(axis=1)
    return labels


def conditional_expectation(values: np.ndarray, labels: np.ndarray,
                            mu: np.ndarray, n_blocks: int) -> tuple[np.ndarray, int]:
    wsum = np.bincount(labels, weights=mu, minlength=n_blocks)
    fallback = int((wsum <= 0.0).sum())
    vsum = np.bincount(labels, weights=mu * values, minlength=n_blocks)
    csum = np.bincount(labels, weights=values, minlength=n_blocks)
    cnum = np.bincount(labels, minlength=n_blocks).astype(float)
    block_mean = np.where(wsum > 0.0, vsum / np.where(wsum > 0.0, wsum, 1.0),
                          csum / np.where(cnum > 0.0, cnum, 1.0))
    return block_mean[labels], fallback


def sector_kernel(state: dict, ratio: int, mu: np.ndarray) -> dict:
    labels = block_assignment(state["points"], ratio)
    n_blocks = int(labels.max()) + 1
    total = float(mu.sum())
    e_p = []
    fallbacks = 0
    for a in range(3):
        indicator = (state["cell_class"] == a).astype(float)
        expected, fb = conditional_expectation(indicator, labels, mu, n_blocks)
        fallbacks = max(fallbacks, fb)
        e_p.append(expected)
        twice, _ = conditional_expectation(expected, labels, mu, n_blocks)
        if np.max(np.abs(twice - expected)) > RECEIPT_TOL:
            raise AssertionError("conditional expectation is not idempotent")
        if abs(float((mu * expected).sum() - (mu * indicator).sum())) > RECEIPT_TOL * total:
            raise AssertionError("conditional expectation does not preserve the state")
    kernel = np.empty((3, 3))
    for a in range(3):
        indicator = (state["cell_class"] == a).astype(float)
        for b in range(3):
            kernel[a, b] = float((mu * indicator * e_p[b]).sum() / total)
    if not np.allclose(kernel, kernel.T, atol=1.0e-9):
        raise AssertionError("sector kernel is not symmetric")
    return {"kernel": kernel, "n_blocks": n_blocks,
            "zero_weight_block_fallbacks": fallbacks}


def readout(kernel: np.ndarray) -> dict:
    centered = kernel - (np.trace(kernel) / 3.0) * np.eye(3)
    evals = np.linalg.eigvalsh(centered)
    g21 = float(evals[1] - evals[0])
    g32 = float(evals[2] - evals[1])
    r = g21 / g32 if g32 > 0 else float("inf")
    return {
        "kernel": kernel.tolist(),
        "eigenvalues_centered": [float(x) for x in evals],
        "g21": g21,
        "g32": g32,
        "raw_gap_ratio_r": r,
        "rho_ord": 3.0 * g32 / (2.0 * g32 + g21) if (2.0 * g32 + g21) > 0
                   else float("nan"),
        "x2": (r - 1.0) / (r + 1.0) if np.isfinite(r) else float("nan"),
        "span": float(evals[2] - evals[0]),
    }


def build(run_dir: pathlib.Path) -> tuple[dict, dict, dict]:
    state = load_state(run_dir)
    run_id = run_dir.name

    levels = {}
    for level, ratio in enumerate(BLOCK_RATIOS):
        block = sector_kernel(state, ratio, state["mu"])
        levels[level] = {"ratio": ratio, **block, "readout": readout(block["kernel"])}

    verdict_ratio = BLOCK_RATIOS[-1]
    nulls = {}
    for seed in SHUFFLE_SEEDS:
        rng = np.random.default_rng(seed)
        shuffled = dict(state)
        shuffled["cell_class"] = rng.permutation(state["cell_class"])
        block = sector_kernel(shuffled, verdict_ratio, state["mu"])
        nulls[f"label_shuffle_seed{seed}"] = readout(block["kernel"])
    uniform_mu = np.ones_like(state["mu"])
    block = sector_kernel(state, verdict_ratio, uniform_mu)
    nulls["uniform_density"] = readout(block["kernel"])
    w = np.asarray(state["class_weights_mu"])
    nulls["context_fully_mixed_rank_one"] = readout(np.outer(w, w))
    nulls["context_fully_clustered_diag"] = readout(np.diag(w))

    scan = json.loads(SCAN_PATH.read_text(encoding="utf-8"))
    band = scan["findings"]["a2_band_by_convention"]["quoted_mixed"]
    template_rho = float(scan["template_rho_ord"])
    phys = levels[len(BLOCK_RATIOS) - 1]["readout"]

    payload = {
        "artifact": "oph_family_transport_kernel",
        "generated_utc": _timestamp(),
        "status": "computed_sim_tower_compression_candidate",
        "transport_kind": "sector_block_of_refinement_conditional_expectation",
        "proof_status": "computed_candidate_carrier_identification_open",
        "carrier_identification": {
            "claim": "majority-incident-edge S3 class cells are the "
                     "same-label generation carrier",
            "status": "candidate_claim_not_theorem",
        },
        "refinements": [
            {"level": level, "run_id": run_id,
             "block_ratio": row["ratio"], "block_count": row["n_blocks"],
             "zero_weight_block_fallbacks": row["zero_weight_block_fallbacks"],
             "hermitian_descendant": _encode(np.asarray(row["kernel"]))}
            for level, row in levels.items()
        ],
        "refinement_intertwiners": [
            {"from_level": 0, "to_level": 1,
             "intertwiner": _encode(np.eye(3)),
             "justification": "canonical class frame across block scales"},
        ],
        "ancestry": {
            "artifacts": [f"s3_gauge_state({run_id})",
                          f"freezeout_fields({run_id})"],
            "attestations": {
                "quark_reference_values_consumed": False,
                "fitted_spreads_consumed": False,
                "numerical_flavor_template_consumed": False,
            },
        },
        "metadata": {
            "note": "Readout #4 of the issue-377 K1 program: the sector "
                    "block of the realized coarse-graining channel at two "
                    "block scales of one state, with executed conditional-"
                    "expectation receipts. Carrier identification and the "
                    "K2 scale clause stay open.",
        },
    }

    generator = build_generator(payload)
    gates = harness_evaluate({
        "candidate_id": f"sim_tower_compression_kernel({run_id})",
        "kernel": {"refinements": payload["refinements"]},
        "ancestry": payload["ancestry"],
    })

    verdict = {
        "artifact": "oph_family_transport_kernel_sim_tower_verdict",
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
        "state_summary": {
            "n_cells": state["n_cells"],
            "cell_class_tie_fraction": state["tie_fraction"],
            "class_weights_mu": state["class_weights_mu"],
        },
        "levels": {f"level{level}": {"block_ratio": row["ratio"],
                                     "block_count": row["n_blocks"],
                                     **row["readout"]}
                   for level, row in levels.items()},
        "nulls_and_context": nulls,
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
        description="Compute the tower-compression kernel from a realized "
                    "sim state.")
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    parser.add_argument("--out-suffix", default="")
    args = parser.parse_args()

    run_dir = pathlib.Path(args.run_dir)
    for name in ("s3_gauge_state.npz", "freezeout_fields.npz"):
        if not (run_dir / name).exists():
            raise SystemExit(f"missing {name} in {run_dir}")

    payload, verdict, generator = build(run_dir)
    suffix = args.out_suffix
    paths = {
        "payload": RUNS / f"family_transport_kernel_sim_tower_computed{suffix}.json",
        "verdict": RUNS / f"family_transport_kernel_sim_tower_verdict{suffix}.json",
        "generator": RUNS / f"generation_bundle_branch_generator_sim_tower{suffix}.json",
    }
    for key, blob in (("payload", payload), ("verdict", verdict),
                      ("generator", generator)):
        paths[key].parent.mkdir(parents=True, exist_ok=True)
        paths[key].write_text(json.dumps(blob, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")

    print(f"run: {verdict['run_id']}  cells: {verdict['state_summary']['n_cells']}  "
          f"tie fraction: {verdict['state_summary']['cell_class_tie_fraction']:.4f}")
    print(f"class weights (mu): "
          f"{['%.4f' % v for v in verdict['state_summary']['class_weights_mu']]}")
    for name, row in verdict["levels"].items():
        print(f"{name} (ratio {row['block_ratio']}, {row['block_count']} blocks): "
              f"r = {row['raw_gap_ratio_r']:.6f}  rho_ord = {row['rho_ord']:.6f}  "
              f"x2 = {row['x2']:+.6f}")
    bc = verdict["band_check"]
    print(f"band {bc['declared_convention_band']}  template {bc['template_rho_ord']:.6f}")
    print(f"COMPUTED rho_ord = {bc['computed_rho_ord_level1']:.6f}  "
          f"inside_band = {bc['inside_band']}")
    print("nulls and context:")
    for name, row in verdict["nulls_and_context"].items():
        print(f"  {name:32s} rho_ord = {row['rho_ord']:.6f}  r = {row['raw_gap_ratio_r']:.6f}")
    print(f"harness: first_failed_gate = {verdict['harness_gates']['first_failed_gate']}  "
          f"status = {verdict['harness_gates']['status']}")
    for key, path in paths.items():
        print(f"saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
