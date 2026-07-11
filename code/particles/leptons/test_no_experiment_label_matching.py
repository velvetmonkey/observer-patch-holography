#!/usr/bin/env python3
"""Guard the forward charged-lepton directory against experiment-label matching."""

from __future__ import annotations

import pathlib
import re


LANE = pathlib.Path(__file__).resolve().parent
COMPARE_ONLY = {
    "derive_charged_d12_continuation_followup.py",
    "derive_lepton_current_family_exact_readout.py",
    "derive_lepton_current_family_exactness_audit.py",
    "derive_lepton_current_family_quadratic_readout_theorem.py",
}
EXECUTABLE_PATTERNS = (
    re.compile(r"references\s*\[\s*[\"'](?:electron|muon|tau)[\"']\s*\]"),
    re.compile(r"\bbest_[A-Za-z0-9_]*fit\b", re.IGNORECASE),
    re.compile(r"\bclosest_[A-Za-z0-9_]*\b", re.IGNORECASE),
)


def _failures() -> list[str]:
    failures: list[str] = []
    for path in sorted(LANE.glob("*.py")):
        if path.name.startswith("test_") or path.name in COMPARE_ONLY:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in EXECUTABLE_PATTERNS:
            if pattern.search(text):
                failures.append(f"{path.name}: matched {pattern.pattern!r}")
    audit = (LANE / "derive_lepton_current_family_exactness_audit.py").read_text(encoding="utf-8")
    if '"public_promotion_allowed": False' not in audit:
        failures.append("derive_lepton_current_family_exactness_audit.py: missing fail-closed promotion label")
    return failures


def test_forward_lepton_directory_does_not_match_experimental_labels() -> None:
    assert _failures() == []


def main() -> int:
    failures = _failures()
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
