from __future__ import annotations

import json
from pathlib import Path

import pytest

from calibration.derive_wzh_strict_branch_candidate_audit import build_artifact


ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_same_branch_candidate_is_numeric_and_fail_closed() -> None:
    report = build_artifact(
        _load(ROOT / "particles/hierarchy/certificates/R_P_source_audit_pixel_certificate.json"),
        _load(ROOT / "particles/hierarchy/certificates/R_gamma_noG_DAG_certificate.json"),
        _load(ROOT / "particles/runs/calibration/d11_declared_calibration_surface.json"),
    )

    values = report["same_branch_candidate_coordinates"]
    assert values["W_tree_chart_GeV"] == pytest.approx(80.3207786309, abs=1.0e-9)
    assert values["Z_tree_chart_GeV"] == pytest.approx(91.1241882025, abs=1.0e-9)
    assert values["H_running_chart_GeV"] == pytest.approx(125.1023215326, abs=1.0e-9)
    assert report["promotion_allowed"] is False
    assert report["tree_pole_control"]["status"].startswith("zero_width_tree_controls")
    assert "BRST_complete_W_Z_H_self_energies_missing" in report["blockers"]
