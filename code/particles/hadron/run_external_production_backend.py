#!/usr/bin/env python3
"""Run an external hadron production backend and ingest its arrays.

This wrapper is the production handoff boundary. It does not know how to
generate QCD correlators itself. Instead it invokes a backend command with the
frozen OPH request paths in the environment, then validates/assembles the
resulting array files and runs the existing writeback pipeline.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from particles.hadron.assemble_backend_export_from_array_files import build_inline_export  # noqa: E402


DEFAULT_REQUEST_DIR = ROOT / "particles" / "runs" / "hadron" / "production_backend_bundle_request"
DEFAULT_SEQUENCE_POPULATION = ROOT / "particles" / "runs" / "hadron" / "stable_channel_sequence_population.json"
DEFAULT_RECEIPT = ROOT / "particles" / "runs" / "hadron" / "runtime_schedule_receipt_N_therm_and_N_sep.json"
DEFAULT_PAYLOAD = ROOT / "particles" / "runs" / "hadron" / "stable_channel_cfg_source_measure_payload.json"
DEFAULT_BACKEND_EXPORT = DEFAULT_REQUEST_DIR / "backend_export_inlined.json"
DEFAULT_DUMP = ROOT / "particles" / "runs" / "hadron" / "backend_correlator_dump.production.json"
DEFAULT_MANIFEST = ROOT / "particles" / "runs" / "hadron" / "oph_hadron_production_backend_manifest.json"
DEFAULT_EVALUATION = ROOT / "particles" / "runs" / "hadron" / "stable_channel_sequence_evaluation.json"
DEFAULT_CLOSURE = ROOT / "particles" / "runs" / "hadron" / "hadron_production_closure_validation_report.json"
DEFAULT_READINESS = ROOT / "particles" / "runs" / "hadron" / "hadron_production_readiness_report.json"


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _missing_array_files(request_dir: Path, dataset_index: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for item in dataset_index.get("datasets", []):
        array_file = item.get("array_file")
        if not array_file:
            missing.append(f"{item.get('path')}:missing_array_file_field")
            continue
        path = request_dir / str(array_file)
        if not path.exists():
            missing.append(str(path))
    return missing


def _copy_request(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("README.md", "backend_run_manifest.json", "dataset_index.json"):
        source = src / name
        if source.exists():
            shutil.copy2(source, dst / name)


def _run_writeback(args: argparse.Namespace, backend_export: Path) -> None:
    command = [
        sys.executable,
        str(ROOT / "particles" / "hadron" / "run_production_backend_writeback.py"),
        "--sequence-population",
        str(args.sequence_population),
        "--receipt",
        str(args.receipt),
        "--payload",
        str(args.payload),
        "--backend-bundle",
        str(backend_export),
        "--dump-output",
        str(args.dump_output),
        "--manifest-output",
        str(args.manifest_output),
        "--evaluation-output",
        str(args.evaluation_output),
        "--closure-output",
        str(args.closure_output),
        "--readiness-output",
        str(args.readiness_output),
        "--n-therm",
        str(args.n_therm),
        "--n-sep",
        str(args.n_sep),
        "--schedule-provenance",
        args.schedule_provenance,
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an external production backend and ingest its output.")
    parser.add_argument(
        "--backend-command",
        default=os.environ.get("OPH_HADRON_BACKEND_COMMAND"),
        help="Command that fills array files under the request directory. Also read from OPH_HADRON_BACKEND_COMMAND.",
    )
    parser.add_argument("--request-dir", default=str(DEFAULT_REQUEST_DIR))
    parser.add_argument(
        "--work-dir",
        default=None,
        help="Optional isolated work directory. The request files are copied there before invoking the backend.",
    )
    parser.add_argument("--backend-export-output", default=str(DEFAULT_BACKEND_EXPORT))
    parser.add_argument("--sequence-population", default=str(DEFAULT_SEQUENCE_POPULATION))
    parser.add_argument("--receipt", default=str(DEFAULT_RECEIPT))
    parser.add_argument("--payload", default=str(DEFAULT_PAYLOAD))
    parser.add_argument("--dump-output", default=str(DEFAULT_DUMP))
    parser.add_argument("--manifest-output", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--evaluation-output", default=str(DEFAULT_EVALUATION))
    parser.add_argument("--closure-output", default=str(DEFAULT_CLOSURE))
    parser.add_argument("--readiness-output", default=str(DEFAULT_READINESS))
    parser.add_argument("--n-therm", type=int, default=2048)
    parser.add_argument("--n-sep", type=int, default=512)
    parser.add_argument("--schedule-provenance", default="external_production_backend")
    parser.add_argument(
        "--skip-backend-command",
        action="store_true",
        help="Do not invoke a backend command; only validate/assemble existing array files.",
    )
    args = parser.parse_args()

    source_request_dir = Path(args.request_dir)
    request_dir = Path(args.work_dir) if args.work_dir else source_request_dir
    if args.work_dir:
        _copy_request(source_request_dir, request_dir)
    manifest_path = request_dir / "backend_run_manifest.json"
    dataset_index_path = request_dir / "dataset_index.json"
    if not manifest_path.exists() or not dataset_index_path.exists():
        raise FileNotFoundError("request directory must contain backend_run_manifest.json and dataset_index.json")

    if not args.skip_backend_command:
        if not args.backend_command:
            raise SystemExit(
                "No backend command supplied. Set OPH_HADRON_BACKEND_COMMAND or pass --backend-command. "
                "Refusing to synthesize production correlators."
            )
        env = os.environ.copy()
        env.update(
            {
                "OPH_HADRON_REQUEST_DIR": str(request_dir.resolve()),
                "OPH_HADRON_MANIFEST": str(manifest_path.resolve()),
                "OPH_HADRON_DATASET_INDEX": str(dataset_index_path.resolve()),
                "OPH_HADRON_ARRAY_DIR": str(request_dir.resolve()),
            }
        )
        subprocess.run(args.backend_command, cwd=request_dir, env=env, shell=True, check=True)

    dataset_index = _load_json(dataset_index_path)
    missing = _missing_array_files(request_dir, dataset_index)
    if missing:
        preview = "\n".join(missing[:12])
        raise SystemExit(
            f"Production backend did not write all required array files ({len(missing)} missing). "
            f"First missing entries:\n{preview}"
        )

    backend_export = build_inline_export(_load_json(manifest_path), dataset_index, array_dir=request_dir)
    backend_export_path = Path(args.backend_export_output)
    _write_json(backend_export_path, backend_export)
    _run_writeback(args, backend_export_path)
    print(f"wrote {backend_export_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
