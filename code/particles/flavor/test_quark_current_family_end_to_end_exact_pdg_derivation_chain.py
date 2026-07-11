#!/usr/bin/env python3
"""Tests for the full current-family exact-PDG derivation chain artifact."""

from __future__ import annotations

import json
from pathlib import Path

from derive_quark_current_family_end_to_end_exact_pdg_derivation_chain import build_artifact


ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "particles" / "runs" / "flavor"


def _load(name: str) -> dict:
    return json.loads((RUNS / name).read_text(encoding="utf-8"))


def test_current_family_end_to_end_exact_pdg_chain_closes() -> None:
    payload = build_artifact(
        _load("quark_target_free_bridge_theorem.json"),
        _load("quark_current_family_transport_frame_strengthened_physical_sigma_lift_theorem.json"),
        _load("quark_current_family_transport_frame_absolute_sector_readout_theorem.json"),
        _load("quark_current_family_transport_frame_exact_pdg_completion.json"),
        _load("quark_current_family_transport_frame_exact_forward_yukawas.json"),
    )

    assert payload["proof_status"] == "closed_current_family_end_to_end_exact_pdg_chain"
    assert payload["theorem_scope"] == "current_family_common_refinement_transport_frame_only"
    assert [item["step"] for item in payload["lemma_chain"]] == [1, 2, 3, 4, 5]
    assert payload["lemma_chain"][1]["artifact"] == "oph_quark_current_family_transport_frame_strengthened_physical_sigma_lift_theorem"
    assert payload["exact_forward_yukawas_artifact"]["artifact"] == "oph_quark_current_family_transport_frame_exact_forward_yukawas"
    masses = payload["exact_running_values_gev"]
    assert abs(float(masses["u"]) - 0.00216) < 1.0e-12
    assert abs(float(masses["d"]) - 0.0047) < 1.0e-12
    assert abs(float(masses["b"]) - 4.186) < 1.0e-12
