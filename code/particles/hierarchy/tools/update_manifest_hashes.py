#!/usr/bin/env python3
"""Refresh hierarchy proof-bundle manifest hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def update_manifest(manifest_path: Path, includes: list[str]) -> dict[str, Any]:
    root = manifest_path.resolve().parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = {entry["path"]: dict(entry) for entry in manifest["files"]}
    for rel in includes:
        entries.setdefault(rel, {"path": rel})

    refreshed: list[dict[str, Any]] = []
    for entry in manifest["files"]:
        rel = entry["path"]
        path = root / rel
        refreshed.append({"path": rel, "sha256": _sha256(path), "bytes": path.stat().st_size})

    existing_paths = {entry["path"] for entry in refreshed}
    for rel in includes:
        if rel in existing_paths:
            continue
        path = root / rel
        refreshed.append({"path": rel, "sha256": _sha256(path), "bytes": path.stat().st_size})

    manifest["generated_utc"] = _now()
    manifest["files"] = refreshed
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh hierarchy manifest sha256/byte entries.")
    parser.add_argument("--manifest", default="manifest.json")
    parser.add_argument("--include", action="append", default=[], help="Additional bundle-relative file to include.")
    args = parser.parse_args()
    manifest = update_manifest(Path(args.manifest), list(args.include))
    print(json.dumps({"updated": args.manifest, "files": len(manifest["files"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
