#!/usr/bin/env python3
"""Regression test for strict particle non-circularity promotion boundaries."""

from __future__ import annotations

import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_non_circularity_policy import validate  # noqa: E402


def test_non_circularity_policy_passes_current_artifacts() -> None:
    payload = validate()
    assert payload["pass"], payload["failures"]
