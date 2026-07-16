#!/usr/bin/env python3
"""Vector-correlator / HVP diagnostic lane on the local lattice engine.

Chain role: computed-spectral-density path for the #425 hadronic closure.
The payload bracket (ward_projected_payload/PAYLOAD_STATUS.md) is wide
because the region below 2 GeV is bracketed by a free-parton versus
zero-support dichotomy; a computed correlator replaces that dichotomy with a
measured number carrying a quotable statistical error. This runner executes
the measurement at diagnostic scale.

Execution class: real_lattice_diagnostic_toy_scale. Output class:
diagnostic, non-promoting. row_class
``diagnostic_non_promoting_lattice_backend``, ``physical_claim`` false.

Pipeline: quenched SU(3) ensemble via the Cabibbo-Marinari heatbath
(``lattice_backend.core.sweep``), clover-Wilson point propagators, local
vector-current two-point contraction at zero spatial momentum, jackknife
errors over configurations, and the Bernecker-Meyer time-momentum moment
matched to the payload-contract kernel (see
``lattice_backend/vector_correlator.py`` for the exact correspondence and
the declared uncertified conversion factors).

Run:
    python3 code/particles/hadron/run_vector_correlator_diagnostic.py [--smoke]
writes code/particles/runs/hadron/lattice_vector_correlator_diagnostic.json.

The artifact hash covers the deterministic physics content only; wall-clock
and host fields live in a separate volatile block.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from lattice_backend.core import average_plaquette, cold_start, sweep  # noqa: E402
from lattice_backend.dirac import WilsonClover, point_propagator  # noqa: E402
from lattice_backend.vector_correlator import (  # noqa: E402
    fold_correlator,
    jackknife_correlator,
    jackknife_moment,
    vector_correlator,
)

OUT_PATH = HERE.parent / "runs" / "hadron" / "lattice_vector_correlator_diagnostic.json"

CHARGE_FACTOR_U1Q_LIGHT_DOUBLET = 5.0 / 9.0  # Q_u^2 + Q_d^2, N_c inside the trace

DEMO_PARAMS = {
    "shape": (16, 4, 4, 4),
    "beta": 5.7,
    "kappa": 0.150,
    "c_sw": 1.0,
    "n_therm": 40,
    "n_sep": 10,
    "n_cfg": 6,
    "n_or": 1,
    "cg_tol": 1e-8,
    "seed": 20260716,
    "amz_grid": [0.5, 1.0, 2.0, 5.0],
}

SMOKE_PARAMS = {
    "shape": (8, 2, 2, 2),
    "beta": 5.7,
    "kappa": 0.140,
    "c_sw": 1.0,
    "n_therm": 4,
    "n_sep": 2,
    "n_cfg": 2,
    "n_or": 1,
    "cg_tol": 1e-6,
    "seed": 77,
    "amz_grid": [1.0, 2.0],
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def measure_ensemble(params: dict, log) -> tuple[np.ndarray, list[float], list[dict]]:
    """Generate the quenched ensemble and measure G(t) per configuration."""
    rng = np.random.default_rng(params["seed"])
    u = cold_start(params["shape"])
    log(f"thermalizing {params['n_therm']} sweeps at beta={params['beta']}")
    for _ in range(params["n_therm"]):
        sweep(rng, u, params["beta"], n_or=params["n_or"])
    correlators = []
    plaquettes = []
    solver_info = []
    for i in range(params["n_cfg"]):
        for _ in range(params["n_sep"]):
            sweep(rng, u, params["beta"], n_or=params["n_or"])
        p = average_plaquette(u)
        op = WilsonClover(u, kappa=params["kappa"], c_sw=params["c_sw"])
        t0 = time.time()
        prop, info = point_propagator(op, params["shape"], tol=params["cg_tol"])
        g = vector_correlator(prop)
        correlators.append(g)
        plaquettes.append(float(p))
        solver_info.append({
            "max_cg_iterations": int(max(info["cg_iterations"])),
            "max_cg_relative_residual": float(max(info["cg_relative_residuals"])),
        })
        log(f"cfg {i:03d}: plaquette={p:.5f} propagator+contraction {time.time() - t0:.0f}s")
    return np.array(correlators), plaquettes, solver_info


def build_payload(params: dict, smoke: bool, log=print) -> dict[str, Any]:
    t_start = time.time()
    correlators, plaquettes, solver_info = measure_ensemble(params, log)

    g_mean, g_err = jackknife_correlator(correlators)
    folded_mean = fold_correlator(g_mean)

    moments: dict[str, Any] = {}
    center, err = jackknife_moment(correlators, amz=None)
    moments["t2_kernel_amz_infinity_limit"] = {
        "moment_raw_unit_charge": center,
        "jackknife_error": err,
        "relative_statistical_error": abs(err / center) if center != 0.0 else None,
        "u1q_light_doublet_weighted": center * CHARGE_FACTOR_U1Q_LIGHT_DOUBLET,
        "u1q_light_doublet_weighted_error": err * CHARGE_FACTOR_U1Q_LIGHT_DOUBLET,
    }
    amz_rows = []
    for amz in params["amz_grid"]:
        c_a, e_a = jackknife_moment(correlators, amz=float(amz))
        amz_rows.append({
            "amz": float(amz),
            "moment_raw_unit_charge": c_a,
            "jackknife_error": e_a,
        })
    moments["amz_grid"] = amz_rows

    rel_err = moments["t2_kernel_amz_infinity_limit"]["relative_statistical_error"]

    ensemble_id = "quenched_wilson_b{b}_L{sx}T{st}_vector_diag".format(
        b=str(params["beta"]).replace(".", "p"),
        sx=params["shape"][1], st=params["shape"][0])

    payload: dict[str, Any] = {
        "artifact": "oph_lattice_vector_correlator_diagnostic",
        "format_version": 1,
        "row_class": "diagnostic_non_promoting_lattice_backend",
        "physical_claim": False,
        "execution_class": "real_lattice_diagnostic_toy_scale",
        "smoke_mode": smoke,
        "guards": {
            "real_lattice_execution": True,
            "target_anchored": False,
            "production_execution_class": False,
            "promotion_allowed": False,
            "public_promotion_allowed": False,
            "satisfies_issue_425_closure": False,
        },
        "contract_correspondence": {
            "contract_file": "ward_projected_payload/payload_harness.py",
            "kernel_contract": "mZ^2/(3*pi*s*(s+mZ^2))",
            "scheme_id": "d10_ward_projected_once_subtracted_at_mZ2",
            "normalization_convention": "R_ratio_massless_parton_NcQ2",
            "tmr_identity": (
                "Delta_had = 4*pi*Pihat(mZ^2) = 4*pi*sum_t G(t)*K(t; a*mZ), "
                "K(t; Q) = t^2 - (4/Q^2)*sin^2(Q*t/2); exact algebra, "
                "verified in test_vector_correlator.py"
            ),
            "uncertified_conversion_factors": {
                "amz": (
                    "contract mZ in lattice units; source-emitted scale "
                    "setting is work in progress; the amz -> infinity kernel "
                    "t^2 approximates any coarse lattice (a^-1 << mZ) to "
                    "relative accuracy 4/(a*mZ)^2 for t >= 1"
                ),
                "z_v_squared": {
                    "declared_value": 1.0,
                    "status": "local vector current renormalization, uncertified",
                },
                "charge_factor_u1q_light_doublet": CHARGE_FACTOR_U1Q_LIGHT_DOUBLET,
                "quark_line_disconnected_contributions": "absent",
            },
        },
        "ensemble": {
            "ensemble_id": ensemble_id,
            "lattice_shape_TXYZ": list(params["shape"]),
            "beta": params["beta"],
            "kappa": params["kappa"],
            "c_sw": params["c_sw"],
            "n_therm_sweeps": params["n_therm"],
            "n_sep_sweeps": params["n_sep"],
            "n_configs": params["n_cfg"],
            "rng_seed": params["seed"],
            "cg_tol": params["cg_tol"],
            "plaquette_per_config": plaquettes,
            "plaquette_mean": float(np.mean(plaquettes)),
            "solver_per_config": solver_info,
        },
        "correlator": {
            "definition": (
                "G(t) = (1/3) sum_k sum_x Re Tr[gamma_k S(x,0) gamma_k "
                "gamma_5 S(x,0)^dag gamma_5], local current, zero spatial "
                "momentum, single flavor, unit charge, color trace included"
            ),
            "per_config": [row.tolist() for row in correlators],
            "ensemble_mean": g_mean.tolist(),
            "jackknife_error": g_err.tolist(),
            "folded_mean": folded_mean.tolist(),
        },
        "moments": moments,
        "precision_statement": {
            "statistical_relative_error_t2_moment": rel_err,
            "uncontrolled_systematics": [
                "quenched ensemble (no sea quarks)",
                "single coarse lattice spacing, no continuum limit",
                "unphysical (heavy) pion mass at the demo kappa",
                "finite volume, small spatial extent",
                "scale setting undefined without a source-emitted scale",
                "local current, Z_V renormalization declared 1",
                "finite-T truncation of the TMR sum at T/2",
                "quark-line disconnected contributions absent",
            ],
        },
    }
    payload["content_sha256"] = hashlib.sha256(
        _canonical_json(payload).encode("utf-8")).hexdigest()
    payload["volatile"] = {
        "generated_utc": _now_utc(),
        "runtime_seconds": round(time.time() - t_start, 1),
        "machine": f"{platform.node()} {platform.machine()} "
                   f"python{platform.python_version()}",
        "note": "excluded from content_sha256",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Vector-correlator diagnostic run.")
    parser.add_argument("--smoke", action="store_true", help="tiny fast run for tests")
    parser.add_argument("--output", default=str(OUT_PATH))
    args = parser.parse_args()
    params = SMOKE_PARAMS if args.smoke else DEMO_PARAMS

    payload = build_payload(params, smoke=args.smoke)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
        f.write("\n")
    print(f"\nwrote {out}")
    block = payload["moments"]["t2_kernel_amz_infinity_limit"]
    print(f"t^2-kernel moment (unit charge): {block['moment_raw_unit_charge']:.6f}"
          f" +- {block['jackknife_error']:.6f}"
          f" (rel {block['relative_statistical_error']:.3f})")
    for row in payload["moments"]["amz_grid"]:
        print(f"amz={row['amz']}: {row['moment_raw_unit_charge']:.6f}"
              f" +- {row['jackknife_error']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
