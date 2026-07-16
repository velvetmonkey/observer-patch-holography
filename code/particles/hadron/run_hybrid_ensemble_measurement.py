#!/usr/bin/env python3
"""Ensemble generation and measurement stage for the hybrid IR bracket.

Output class: diagnostic, non-promoting. Generates a seeded quenched
ensemble, measures per configuration the transverse local-local vector
correlator, the conserved-local vector correlator, and the pion
correlator, and stores everything in a .npz cache consumed by
``run_hybrid_ir_bracket_diagnostic.py``. Thermalization plaquette history
and per-measurement plaquettes are stored so thermalization and
autocorrelation are measurable from the cache.

Run:
    python3 run_hybrid_ensemble_measurement.py --ensemble A
    python3 run_hybrid_ensemble_measurement.py --ensemble B
    python3 run_hybrid_ensemble_measurement.py --free --shape 16,4,4,4 \
        --kappa 0.1158 --output <path>

Ensemble parameters are declared in
``code/particles/runs/hadron/hybrid_ir_bracket_envelope_spec_2026-07-16.json``
before any evaluation; the dicts below mirror that spec.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from lattice_backend.core import average_plaquette, cold_start, sweep  # noqa: E402
from lattice_backend.dirac import WilsonClover, point_propagator  # noqa: E402
from lattice_backend.conserved_vector import (  # noqa: E402
    conserved_local_correlator,
    temporal_vector_correlator,
    transverse_vector_correlator,
)
from lattice_backend.spectroscopy import pion_correlator  # noqa: E402

RUNS_DIR = HERE.parent / "runs" / "hadron"

ENSEMBLES = {
    "A": {
        "ensemble_id": "hybrid_A_quenched_b5p7_16x4c3",
        "shape": (16, 4, 4, 4),
        "beta": 5.7,
        "kappa": 0.150,
        "c_sw": 1.0,
        "n_therm": 100,
        "n_sep": 10,
        "n_cfg": 64,
        "n_or": 1,
        "cg_tol": 1e-8,
        "seed": 716001,
    },
    "B": {
        "ensemble_id": "hybrid_B_quenched_b5p7_24x6c3",
        "shape": (24, 6, 6, 6),
        "beta": 5.7,
        "kappa": 0.150,
        "c_sw": 1.0,
        "n_therm": 100,
        "n_sep": 10,
        "n_cfg": 20,
        "n_or": 1,
        "cg_tol": 1e-8,
        "seed": 716002,
    },
    "SMOKE": {
        "ensemble_id": "hybrid_smoke_quenched_b5p7_8x2c3",
        "shape": (8, 2, 2, 2),
        "beta": 5.7,
        "kappa": 0.140,
        "c_sw": 1.0,
        "n_therm": 4,
        "n_sep": 2,
        "n_cfg": 3,
        "n_or": 1,
        "cg_tol": 1e-7,
        "seed": 716099,
    },
}


def measure_interacting(params: dict, out_path: Path, log=print) -> None:
    t_start = time.time()
    rng = np.random.default_rng(params["seed"])
    u = cold_start(params["shape"])
    therm_plaquettes = []
    log(f"[{params['ensemble_id']}] thermalizing {params['n_therm']} sweeps")
    for i in range(params["n_therm"]):
        sweep(rng, u, params["beta"], n_or=params["n_or"])
        therm_plaquettes.append(average_plaquette(u))
        if (i + 1) % 20 == 0:
            log(f"  therm sweep {i + 1}: plaquette {therm_plaquettes[-1]:.5f}")
    g_ll, g_cl, g_temporal, g_pion = [], [], [], []
    plaquettes, cg_iters, cg_resid = [], [], []
    for i in range(params["n_cfg"]):
        for _ in range(params["n_sep"]):
            sweep(rng, u, params["beta"], n_or=params["n_or"])
        plaquettes.append(average_plaquette(u))
        op = WilsonClover(u, kappa=params["kappa"], c_sw=params["c_sw"])
        t0 = time.time()
        prop, info = point_propagator(op, params["shape"], tol=params["cg_tol"])
        g_ll.append(transverse_vector_correlator(prop))
        g_cl.append(conserved_local_correlator(prop, op.ubc, params["kappa"]))
        g_temporal.append(temporal_vector_correlator(prop))
        g_pion.append(pion_correlator(prop))
        cg_iters.append(int(max(info["cg_iterations"])))
        cg_resid.append(float(max(info["cg_relative_residuals"])))
        log(f"  cfg {i:03d}: plaquette {plaquettes[-1]:.5f}"
            f" cg_it {cg_iters[-1]} {time.time() - t0:.0f}s")
    np.savez_compressed(
        out_path,
        kind="interacting",
        ensemble_id=params["ensemble_id"],
        shape=np.array(params["shape"]),
        beta=params["beta"],
        kappa=params["kappa"],
        c_sw=params["c_sw"],
        n_therm=params["n_therm"],
        n_sep=params["n_sep"],
        n_cfg=params["n_cfg"],
        n_or=params["n_or"],
        cg_tol=params["cg_tol"],
        seed=params["seed"],
        therm_plaquettes=np.array(therm_plaquettes),
        plaquettes=np.array(plaquettes),
        cg_iterations=np.array(cg_iters),
        cg_residuals=np.array(cg_resid),
        g_ll=np.array(g_ll),
        g_cl=np.array(g_cl),
        g_temporal=np.array(g_temporal),
        g_pion=np.array(g_pion),
        budget_truncation=params.get("budget_truncation", ""),
        wall_seconds=time.time() - t_start,
    )
    log(f"[{params['ensemble_id']}] wrote {out_path}"
        f" ({time.time() - t_start:.0f}s)")


def measure_free(shape: tuple[int, ...], kappa: float, c_sw: float,
                 out_path: Path, cg_tol: float = 1e-10, log=print) -> np.ndarray:
    """Free-field (cold gauge) reference measurement at the given kappa."""
    u = cold_start(shape)
    op = WilsonClover(u, kappa=kappa, c_sw=c_sw)
    prop, info = point_propagator(op, shape, tol=cg_tol)
    g_ll = transverse_vector_correlator(prop)
    if out_path is not None:
        np.savez_compressed(
            out_path, kind="free", shape=np.array(shape), kappa=kappa,
            c_sw=c_sw, cg_tol=cg_tol, g_ll=g_ll,
            cg_iterations=np.array(info["cg_iterations"]))
        log(f"[free kappa={kappa}] wrote {out_path}")
    return g_ll


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ensemble", choices=sorted(ENSEMBLES))
    parser.add_argument(
        "--n-cfg", type=int, default=0,
        help="truncate the seeded chain to the first n configurations "
             "(wall-clock budget truncation; recorded in the cache)")
    parser.add_argument("--free", action="store_true")
    parser.add_argument("--shape", default="")
    parser.add_argument("--kappa", type=float, default=0.0)
    parser.add_argument("--c-sw", type=float, default=1.0)
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    if args.free:
        shape = tuple(int(v) for v in args.shape.split(","))
        out = Path(args.output) if args.output else (
            RUNS_DIR / f"hybrid_ir_free_reference_{args.kappa:.6f}.npz")
        measure_free(shape, args.kappa, args.c_sw, out)
        return 0
    if not args.ensemble:
        parser.error("--ensemble or --free required")
    params = dict(ENSEMBLES[args.ensemble])
    if args.n_cfg:
        params["n_cfg"] = args.n_cfg
        params["budget_truncation"] = (
            f"first {args.n_cfg} configurations of the declared seeded "
            f"chain (declared n_cfg {ENSEMBLES[args.ensemble]['n_cfg']}); "
            "wall-clock budget truncation")
    out = Path(args.output) if args.output else (
        RUNS_DIR / f"hybrid_ir_ensemble{args.ensemble}_2026-07-16.npz")
    measure_interacting(params, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
