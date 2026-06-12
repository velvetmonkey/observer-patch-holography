#!/usr/bin/env python3
"""Guard the frozen OPH hierarchy proof bundle."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def test_hierarchy_bundle_validators_pass() -> None:
    result = _run("validators/validate_bundle.py")
    payload = json.loads(result.stdout)

    assert len(payload) == 2
    assert all(entry["returncode"] == 0 for entry in payload)
    assert json.loads(payload[0]["stdout"])["pass"] is True
    assert json.loads(payload[1]["stdout"])["pass"] is True


def test_ru_krawczyk_certificate_is_unique_root_witness() -> None:
    result = _run(
        "validators/validate_ru_interval_certificate.py",
        "certificates/R_U_krawczyk_certificate.json",
    )
    payload = json.loads(result.stdout)

    assert payload["K_subset_interior_I"] is True
    assert payload["derivative_excludes_zero"] is True
    assert payload["pass"] is True

    cert = json.loads((ROOT / "certificates/R_U_krawczyk_certificate.json").read_text())
    assert cert["status"] == "krawczyk_inclusion_witness_supplied"
    assert cert["center_c"] == "0.041124336195630495"
    assert cert["inclusion"]["K_I_subset_interior_I_U"] is True


def test_hierarchy_numeric_witness_keeps_public_and_source_audit_branches_separate() -> None:
    witness = json.loads((ROOT / "computations/hierarchy_numeric_witness.json").read_text())

    public = witness["public_endpoint_branch"]
    source_audit = witness["source_audit_branch"]
    assert public["P_C"] == "1.630968209403959324879279847782648941"
    assert public["alpha_U_display"] == "0.041124336195630495"
    assert public["v_over_E_star"] == "2.0199803239725553e-17"
    assert source_audit["P_cand"] == "1.63097209569432901817967892561191884270169"
    assert source_audit["alpha_U"] == "0.04112424744557487"
    assert source_audit["v_over_E_star"] == "2.0198114150099223e-17"
