#!/usr/bin/env python3
"""Emit a local diagnostic hadron backend export.

This is an executable backend-shaped adapter for the OPH stable-channel
pipeline. It intentionally emits target-anchored diagnostic correlators, not
production RHMC/HMC arrays. Its purpose is to keep the backend/writeback path
continuously runnable while the real nonperturbative backend is being wired in.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from particles.hadron.production_execution_support import (  # noqa: E402
    LAMBDA_MSBAR_3_GEV,
    fill_runtime_receipt,
    normalize_source_id,
)


DEFAULT_RECEIPT = ROOT / "particles" / "runs" / "hadron" / "runtime_schedule_receipt_N_therm_and_N_sep.json"
DEFAULT_PAYLOAD = ROOT / "particles" / "runs" / "hadron" / "stable_channel_cfg_source_measure_payload.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "hadron" / "local_diagnostic_backend_export.json"
DEFAULT_PI_ISO_GEV = 0.13503938383599978
DEFAULT_N_ISO_GEV = 0.9389602105777344


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=ROOT.parents[1],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _stable_correlator(*, am_ground: float, amplitude: float, t_extent: int) -> list[float]:
    return [
        float(amplitude * math.exp(-am_ground * t_idx))
        for t_idx in range(t_extent)
    ]


def _source_amplitude(ensemble_id: str, cfg_id: str, src_id: str, *, base: float) -> float:
    material = f"{ensemble_id}|{cfg_id}|{src_id}|{base:.17g}".encode("utf-8")
    digest = hashlib.sha256(material).hexdigest()
    offset = int(digest[:8], 16) / float(0xFFFFFFFF)
    return base * (0.985 + 0.03 * offset)


def _backend_metadata(
    *,
    run_id: str,
    pi_mass_gev: float,
    n_mass_gev: float,
    lambda_msbar_3_gev: float,
) -> dict[str, Any]:
    return {
        "execution_class": "diagnostic_surrogate",
        "claim_tier": "target_anchored_backend_pipeline_diagnostic_not_production",
        "public_promotion_allowed": False,
        "profile_id": "oph_local_diagnostic_backend_v1",
        "backend": {
            "family": "diagnostic_correlator_generator",
            "name": "oph_local_diagnostic_hadron_backend",
            "version": "0.1.0",
            "git_commit": _git_commit(),
            "run_id": run_id,
            "build_id": f"python-{platform.python_version()}",
            "machine": platform.node() or platform.platform(),
            "execution_class": "diagnostic_surrogate",
        },
        "physics": {
            "branch": "seeded_2p1_qed_off",
            "target_channels": ["pi_iso", "N_iso"],
            "source_only": False,
            "target_anchored": True,
            "pi_iso_mass_gev_input": pi_mass_gev,
            "N_iso_mass_gev_input": n_mass_gev,
            "lambda_msbar_3_gev": lambda_msbar_3_gev,
            "notes": [
                "Closed-form exponential correlators are generated from explicit mass inputs.",
                "Use this backend only to test the OPH writeback/evaluation/systematics stack.",
                "Replace it with production RHMC/HMC or OPH hardware correlators before any public hadron promotion.",
            ],
        },
        "solvers": {
            "diagnostic": {
                "id": "closed_form_exponential_correlator",
                "dirac_solves_performed": False,
            },
            "rhmc_strange": {
                "rational_coefficients": [
                    {
                        "diagnostic_placeholder": True,
                        "reason": "No RHMC strange solve is performed by the local diagnostic backend.",
                    }
                ]
            },
        },
        "integrator": {
            "id": "closed_form_diagnostic_generator",
            "trajectory_length": 0.0,
            "n_steps": 0,
            "metropolis_accept_reject": False,
        },
        "boundary_conditions": {
            "gauge": {"x": "periodic", "y": "periodic", "z": "periodic", "t": "periodic"},
            "fermion": {"x": "periodic", "y": "periodic", "z": "periodic", "t": "anti_periodic"},
        },
        "sources": {
            "construction": "local_point_from_payload",
            "gauge_fixing": "none",
            "source_smearing": "none",
            "sink_smearing": "none",
            "stochastic_noise": "none",
        },
        "contractions": {
            "pion": {
                "operator": "diagnostic_pi_iso_exponential",
                "export_channel": "pi_iso",
                "zero_momentum_projection": True,
                "real_projection": True,
            },
            "nucleon": {
                "operator": "diagnostic_N_iso_direct_minus_exchange",
                "export_channels": ["N_iso_direct", "N_iso_exchange"],
                "subtraction_in_repo": "N_iso_direct - N_iso_exchange",
                "zero_momentum_projection": True,
                "real_projection": True,
            },
        },
    }


def build_backend_export(
    receipt: dict[str, Any],
    payload: dict[str, Any],
    *,
    pi_mass_gev: float,
    n_mass_gev: float,
    lambda_msbar_3_gev: float,
    run_id: str,
) -> dict[str, Any]:
    payload_by_ensemble = {
        str(entry["ensemble_id"]): entry
        for entry in payload.get("ensemble_payloads", [])
    }
    metadata = _backend_metadata(
        run_id=run_id,
        pi_mass_gev=pi_mass_gev,
        n_mass_gev=n_mass_gev,
        lambda_msbar_3_gev=lambda_msbar_3_gev,
    )
    out: dict[str, Any] = {
        "artifact": "oph_hadron_backend_raw_export_inlined",
        "format_version": 1,
        **metadata,
        "raw_export_provenance": {
            "manifest_artifact": "oph_hadron_backend_raw_export",
            "manifest_path": None,
            "correlators_hdf5": None,
            **metadata,
        },
        "ensembles": {},
    }
    for sched in (receipt.get("execution_contract") or {}).get("ensemble_schedule", []):
        ensemble_id = str(sched["ensemble_id"])
        payload_entry = payload_by_ensemble.get(ensemble_id)
        if payload_entry is None:
            raise ValueError(f"payload missing ensemble {ensemble_id!r}")
        a_lambda = float(payload_entry["aLambda_msbar3"])
        t_extent = int(payload_entry["T"])
        am_pi = (float(pi_mass_gev) / float(lambda_msbar_3_gev)) * a_lambda
        am_n = (float(n_mass_gev) / float(lambda_msbar_3_gev)) * a_lambda
        cfgs: dict[str, Any] = {}
        for cfg_id in sched.get("cfg_ids", []):
            cfg_id = str(cfg_id)
            sources: dict[str, Any] = {}
            for src_desc in (payload_entry.get("source_descriptors_by_cfg") or {}).get(cfg_id, []):
                src_id = normalize_source_id(str(src_desc["src_id"]))
                pi_amp = _source_amplitude(ensemble_id, cfg_id, src_id, base=1.0)
                n_amp = _source_amplitude(ensemble_id, cfg_id, src_id, base=1.4)
                ex_amp = _source_amplitude(ensemble_id, cfg_id, src_id, base=0.16)
                pi_corr = _stable_correlator(am_ground=am_pi, amplitude=pi_amp, t_extent=t_extent)
                n_corr = _stable_correlator(am_ground=am_n, amplitude=n_amp, t_extent=t_extent)
                n_exchange = _stable_correlator(
                    am_ground=am_n + max(0.25 * a_lambda, 1.0e-6),
                    amplitude=ex_amp,
                    t_extent=t_extent,
                )
                n_direct = [
                    float(total + exchange)
                    for total, exchange in zip(n_corr, n_exchange)
                ]
                sources[src_id] = {
                    "coord": list(src_desc.get("coords") or src_desc.get("coord") or []),
                    "pi_iso": pi_corr,
                    "N_iso_direct": n_direct,
                    "N_iso_exchange": n_exchange,
                }
            cfgs[cfg_id] = {
                "trajectory_stop": (sched.get("trajectory_stop_by_cfg") or {}).get(cfg_id),
                "sources": sources,
            }
        out["ensembles"][ensemble_id] = {
            "ensemble_id": ensemble_id,
            "cfgs": cfgs,
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a local diagnostic hadron backend export.")
    parser.add_argument("--receipt", default=str(DEFAULT_RECEIPT))
    parser.add_argument("--payload", default=str(DEFAULT_PAYLOAD))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    parser.add_argument("--n-therm", type=int, default=None)
    parser.add_argument("--n-sep", type=int, default=None)
    parser.add_argument("--pi-mass-gev", type=float, default=DEFAULT_PI_ISO_GEV)
    parser.add_argument("--n-mass-gev", type=float, default=DEFAULT_N_ISO_GEV)
    parser.add_argument("--lambda-msbar-3-gev", type=float, default=LAMBDA_MSBAR_3_GEV)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    receipt = _load_json(args.receipt)
    payload = _load_json(args.payload)
    receipt = fill_runtime_receipt(
        receipt,
        n_therm=args.n_therm,
        n_sep=args.n_sep,
        schedule_provenance="local_diagnostic_backend_cli" if args.n_therm is not None or args.n_sep is not None else None,
    )
    run_id = args.run_id or f"local-diagnostic-{_timestamp()}"
    export = build_backend_export(
        receipt,
        payload,
        pi_mass_gev=args.pi_mass_gev,
        n_mass_gev=args.n_mass_gev,
        lambda_msbar_3_gev=args.lambda_msbar_3_gev,
        run_id=run_id,
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(export, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
