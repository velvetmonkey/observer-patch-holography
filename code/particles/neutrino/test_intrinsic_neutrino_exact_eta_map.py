#!/usr/bin/env python3
"""Validate the intrinsic neutrino exact eta-map artifact."""

from __future__ import annotations

import json
import importlib.util
import pathlib
import subprocess
import sys

import numpy as np
import pytest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_intrinsic_neutrino_exact_eta_map.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "intrinsic_neutrino_exact_eta_map.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("derive_intrinsic_neutrino_exact_eta_map", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_intrinsic_eta_map_is_exact_once_eta_is_given() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_intrinsic_neutrino_exact_eta_map"
    assert payload["theorem_surface_status"] == "intrinsic_builder_exact_conditional_on_source_open_inputs"
    assert payload["source_only_physical_input_eligible"] is False
    assert payload["selector_common_scale_invariant"] is True
    assert payload["selector_domain"]["satisfied"] is True
    assert payload["selector_domain"]["margin_rad"] > 0.0
    assert payload["pmns_status"] == "not_formed_here"
    assert payload["ordering_phase_certified"] is None
    assert payload["ordering_status"] == "unresolved_without_mass_eigenstate_label_rule"
    assert payload["physical_ordering_assignments"]["selected"] is None
    assert payload["takagi_congruence_max_offdiag_gev"] < 1.0e-24
    assert len(payload["masses_gev_sorted"]) == 3
    assert payload["cubic_root_audit_max_abs_gev2"] < 1.0e-30


def test_principal_selector_rejects_cycle_sum_outside_unequal_weight_domain() -> None:
    module = _load_module()
    mu = np.array([1.5, 1.0, 0.5], dtype=float)
    f_max = module._principal_selector_domain(mu)
    assert f_max < 1.5 * np.pi
    with pytest.raises(ValueError, match="principal selector requires"):
        module._solve_principal_selector(mu, f_max + 1.0e-6)
