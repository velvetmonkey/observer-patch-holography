#!/usr/bin/env python3
"""Guard the canonical Majorana-phase readout candidate on the weighted-cycle surface."""

from __future__ import annotations

import importlib.util
import json
import pathlib

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_physical_majorana_phase_theorem.py"
REPRESENTATION_SCRIPT = ROOT / "particles" / "neutrino" / "derive_neutrino_weighted_cycle_shared_basis_representation.py"
WEIGHTED_CYCLE = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"
SHARED_CHARGED_LEFT = ROOT / "particles" / "runs" / "neutrino" / "shared_charged_lepton_left_basis.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("derive_neutrino_physical_majorana_phase_theorem", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_representation_module():
    spec = importlib.util.spec_from_file_location("derive_neutrino_weighted_cycle_shared_basis_representation", REPRESENTATION_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {REPRESENTATION_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _wrap_deg(angle_deg: float) -> float:
    wrapped = (angle_deg + 180.0) % 360.0 - 180.0
    if wrapped <= -180.0:
        return wrapped + 360.0
    return wrapped


def test_weighted_cycle_majorana_phase_candidate_is_stable_but_not_publicly_promoted() -> None:
    module = _load_module()
    payload = module.build_payload(
        json.loads(WEIGHTED_CYCLE.read_text(encoding="utf-8")),
        json.loads(SHARED_CHARGED_LEFT.read_text(encoding="utf-8")),
        weighted_cycle_path=WEIGHTED_CYCLE,
        shared_charged_left_path=SHARED_CHARGED_LEFT,
    )

    assert payload["status"] == "candidate_only"
    assert payload["public_surface_candidate_allowed"] is False
    assert payload["public_promotion_status"] == "blocked_rejected_candidate_and_missing_basis_placement"
    assert "historical shared-basis recovery is tautological" in payload["public_promotion_blocker"]
    assert "phase_parameterization" not in payload["readout_convention"]
    assert "majorana_readout_row_gauge" in payload["readout_convention"]
    assert payload["shared_basis_identity_checks"] is None
    assert payload["readout_checks"]["row_gauged_u_e1_imag_abs"] < 1.0e-12
    assert payload["readout_checks"]["row_gauged_u_e1_real"] > 0.0
    assert payload["takagi_congruence"]["diagonalized_offdiag_max_abs"] < 1.0e-12
    assert payload["takagi_congruence"]["diagonalized_imag_max_abs"] < 1.0e-12
    assert abs(payload["weighted_cycle_observables_match"]["delta_deg_abs_delta"]) < 1.0e-10
    assert abs(payload["candidate_parameters"]["alpha21_deg_0_to_360"] - 153.6185177794357) < 1.0e-9
    assert abs(payload["candidate_parameters"]["alpha31_deg_0_to_360"] - 257.0032408220805) < 1.0e-9


def test_weighted_cycle_majorana_pair_stays_unpromoted_with_basis_audit() -> None:
    module = _load_module()
    representation_module = _load_representation_module()
    representation_payload = representation_module.build_payload(
        json.loads(WEIGHTED_CYCLE.read_text(encoding="utf-8")),
        json.loads(SHARED_CHARGED_LEFT.read_text(encoding="utf-8")),
        weighted_cycle_path=WEIGHTED_CYCLE,
        shared_charged_left_path=SHARED_CHARGED_LEFT,
    )
    payload = module.build_payload(
        json.loads(WEIGHTED_CYCLE.read_text(encoding="utf-8")),
        json.loads(SHARED_CHARGED_LEFT.read_text(encoding="utf-8")),
        representation_payload,
        weighted_cycle_path=WEIGHTED_CYCLE,
        shared_charged_left_path=SHARED_CHARGED_LEFT,
        shared_basis_representation_path=ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_shared_basis_representation.json",
    )

    assert payload["status"] == "candidate_only"
    assert payload["public_surface_candidate_allowed"] is False
    assert payload["candidate_promotion_eligible"] is False
    assert payload["public_promotion_status"] == "blocked_rejected_candidate_and_missing_basis_placement"
    assert payload["public_promotion_blocker"] is not None
    assert payload["shared_basis_representation"] is not None
    assert payload["shared_basis_representation"]["source_path"] == "code/particles/runs/neutrino/neutrino_weighted_cycle_shared_basis_representation.json"
    assert payload["shared_basis_representation"]["promotion_use"] == "blocked"
    assert payload["shared_basis_representation"]["basis_placement_source_derived"] is False
    assert payload["source_artifacts"]["weighted_cycle_branch"] == "code/particles/runs/neutrino/neutrino_weighted_cycle_repair.json"
    assert payload["source_artifacts"]["shared_charged_left_basis"] == "code/particles/runs/neutrino/shared_charged_lepton_left_basis.json"
    assert payload["source_artifacts"]["shared_basis_representation"] == "code/particles/runs/neutrino/neutrino_weighted_cycle_shared_basis_representation.json"
    assert payload["shared_basis_identity_checks"] is None
    assert payload["emitted_parameters"] is None
    assert "phase_parameterization" not in payload["readout_convention"]
    assert "majorana_readout_row_gauge" in payload["readout_convention"]
    row_gauged = np.array(payload["row_gauged_pmns_matrix_real"], dtype=float) + 1j * np.array(
        payload["row_gauged_pmns_matrix_imag"], dtype=float
    )
    assert payload["readout_checks"]["row_gauged_u_e1_imag_abs"] < 1.0e-12
    assert payload["readout_checks"]["row_gauged_u_e1_real"] > 0.0
    assert abs(np.imag(row_gauged[0, 0])) < 1.0e-12
    assert np.real(row_gauged[0, 0]) > 0.0
    assert abs(payload["candidate_parameters"]["alpha21_deg_0_to_360"] - 153.6185177794357) < 1.0e-9
    assert abs(payload["candidate_parameters"]["alpha31_deg_0_to_360"] - 257.0032408220805) < 1.0e-9


def test_naive_pmns_only_majorana_readout_is_column_phase_dependent() -> None:
    module = _load_module()
    weighted_cycle = json.loads(WEIGHTED_CYCLE.read_text(encoding="utf-8"))
    pmns = np.array(weighted_cycle["pmns_real"], dtype=float) + 1j * np.array(weighted_cycle["pmns_imag"], dtype=float)
    shifted = pmns @ np.diag(np.exp(1j * np.array([0.3, -0.7, 1.1])))

    base_obs = module._standard_pmns_parameters(pmns)
    shifted_obs = module._standard_pmns_parameters(shifted)
    base_pair = module._majorana_pair_from_pmns(pmns, base_obs["delta_rad"])
    shifted_pair = module._majorana_pair_from_pmns(shifted, shifted_obs["delta_rad"])

    assert abs(base_obs["theta12_deg"] - shifted_obs["theta12_deg"]) < 1.0e-12
    assert abs(base_obs["theta23_deg"] - shifted_obs["theta23_deg"]) < 1.0e-12
    assert abs(base_obs["theta13_deg"] - shifted_obs["theta13_deg"]) < 1.0e-12
    assert abs(base_obs["J"] - shifted_obs["J"]) < 1.0e-12
    assert abs(_wrap_deg(base_obs["delta_deg"] - shifted_obs["delta_deg"])) < 1.0e-12

    alpha21_shift = abs(_wrap_deg(base_pair["alpha21_deg"] - shifted_pair["alpha21_deg"]))
    alpha31_shift = abs(_wrap_deg(base_pair["alpha31_deg"] - shifted_pair["alpha31_deg"]))
    assert alpha21_shift > 1.0
    assert alpha31_shift > 1.0
