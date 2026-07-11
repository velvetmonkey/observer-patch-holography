#!/usr/bin/env python3
"""Directory-wide guard against Koide-assisted charged-lepton fitting."""

from __future__ import annotations

import pathlib
import re


LANE = pathlib.Path(__file__).resolve().parent
IMPORT_OR_CALL = re.compile(r"(?:^\s*(?:from|import)\s+[^\n]*koide|\bkoide\s*\()", re.IGNORECASE | re.MULTILINE)


def _failures() -> list[str]:
    failures: list[str] = []
    for path in sorted(LANE.glob("*.py")):
        if path.name.startswith("test_"):
            continue
        if IMPORT_OR_CALL.search(path.read_text(encoding="utf-8")):
            failures.append(f"{path.name}: imports or calls Koide fitting code")
    return failures


def test_charged_lepton_directory_has_no_koide_import_or_call() -> None:
    assert _failures() == []


def main() -> int:
    failures = _failures()
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
