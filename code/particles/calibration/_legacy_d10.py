"""Loader for the pinned D10/D11 basis, with an opt-in external fallback."""

from __future__ import annotations

import os
import sys
from pathlib import Path


LEGACY_ENV = "OPH_RUN_LEGACY_D10"
LEGACY_DIR_ENV = "OPH_LEGACY_PARTICLE_DIR"
VENDORED_DIR = Path(__file__).resolve().parent / "legacy_d10"


def _default_legacy_dir() -> Path | None:
    for base in Path(__file__).resolve().parents:
        candidate = base / "arXiv" / "RC1" / "ancillary" / "code" / "particles"
        if candidate.exists():
            return candidate
    return None


def legacy_enabled() -> bool:
    return VENDORED_DIR.exists() or os.environ.get(LEGACY_ENV) == "1"


def maybe_add_legacy_d10_path() -> Path | None:
    if not legacy_enabled():
        return None
    configured = os.environ.get(LEGACY_DIR_ENV)
    if configured:
        path = Path(configured).expanduser().resolve()
    elif VENDORED_DIR.exists():
        path = VENDORED_DIR
    else:
        path = _default_legacy_dir()
    if path is None or not path.exists():
        return None
    for candidate in (path / "core", path):
        if candidate.exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
    return path


def require_legacy_d10_path() -> Path:
    path = maybe_add_legacy_d10_path()
    if path is None:
        raise SystemExit(
            "Pinned D10 helper unavailable. Restore calibration/legacy_d10 or set "
            "OPH_RUN_LEGACY_D10=1 and, if needed, "
            "OPH_LEGACY_PARTICLE_DIR=/path/to/arXiv/RC1/ancillary/code/particles."
        )
    return path
