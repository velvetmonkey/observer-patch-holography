#!/usr/bin/env python3
"""Build a canonical exact non-hadron mass bundle.

This bundle consolidates the strongest exact non-hadron mass outputs on the
declared local surfaces into one deduplicated view: structural zeros, exact
electroweak sidecar masses, exact Higgs readout, exact charged-lepton
`current_family_only` witness, exact quark `current_family_only` witness plus
restricted transport-frame completion, and the theorem-grade weighted-cycle
absolute neutrino family.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[2]
REFERENCE_JSON = ROOT / "particles" / "data" / "particle_reference_values.json"
EW_EXACT_JSON = ROOT / "particles" / "runs" / "calibration" / "d10_ew_w_anchor_neutral_shear_factorization_official_pdg_2025_update.json"
D11_EXACT_JSON = ROOT / "particles" / "runs" / "calibration" / "d11_reference_exact_adapter.json"
D11_EXACT_HIGGS_PROMOTION_JSON = ROOT / "particles" / "runs" / "calibration" / "d11_live_exact_higgs_promotion.json"
D11_EXACT_SPLIT_PAIR_JSON = ROOT / "particles" / "runs" / "calibration" / "d11_live_exact_split_pair_theorem.json"
CHARGED_JSON = ROOT / "particles" / "runs" / "leptons" / "lepton_current_family_exact_readout.json"
QUARK_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_exact_readout.json"
CHARGED_THEOREM_JSON = ROOT / "particles" / "runs" / "leptons" / "lepton_current_family_quadratic_readout_theorem.json"
QUARK_THEOREM_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_quadratic_readout_theorem.json"
CHARGED_AFFINE_JSON = ROOT / "particles" / "runs" / "leptons" / "lepton_current_family_affine_anchor_theorem.json"
QUARK_CLOSURE_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_selected_sheet_closure.json"
QUARK_TRANSPORT_LIFT_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_sector_attached_lift.json"
QUARK_TRANSPORT_COMPLETION_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_exact_pdg_completion.json"
QUARK_TRANSPORT_FORWARD_YUKAWAS_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_transport_frame_exact_forward_yukawas.json"
QUARK_END_TO_END_CHAIN_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_current_family_end_to_end_exact_pdg_derivation_chain.json"
QUARK_PUBLIC_YUKAWA_JSON = ROOT / "particles" / "runs" / "flavor" / "quark_public_exact_yukawa_end_to_end_theorem.json"
NEUTRINO_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_absolute_attachment_theorem.json"
NEUTRINO_BRIDGE_RIGIDITY_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_bridge_rigidity_theorem.json"
DEFAULT_MD_OUT = ROOT / "particles" / "EXACT_NONHADRON_MASSES.md"
DEFAULT_JSON_OUT = ROOT / "particles" / "exact_nonhadron_masses.json"
DEFAULT_FORWARD_OUT = ROOT / "particles" / "runs" / "status" / "exact_nonhadron_masses_current.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_optional_json(path: pathlib.Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _repo_ref(path: pathlib.Path) -> str:
    return str(path.relative_to(ROOT.parent))


def _non_circularity_promotable(payload: dict[str, Any] | None, default: bool = False) -> bool:
    if not payload:
        return False
    status = payload.get("non_circularity_status")
    if isinstance(status, dict):
        return status.get("promotion_allowed") is True
    return default


def _d11_split_promotable(payload: dict[str, Any] | None) -> bool:
    return (
        bool(payload)
        and payload.get("status") == "closed"
        and payload.get("proof_status") == "closed_source_only_live_exact_split_pair"
        and payload.get("public_surface_candidate_allowed") is True
        and _non_circularity_promotable(payload, default=True)
    )


def _quark_public_promotable(payload: dict[str, Any] | None) -> bool:
    return (
        bool(payload)
        and payload.get("public_promotion_allowed") is True
        and payload.get("proof_status") == "closed_target_free_public_exact_yukawa_end_to_end_theorem"
        and _non_circularity_promotable(payload, default=True)
    )


def _neutrino_absolute_promotable(payload: dict[str, Any] | None) -> bool:
    return (
        bool(payload)
        and payload.get("status") == "theorem_grade_emitted"
        and payload.get("public_surface_candidate_allowed") is True
        and _non_circularity_promotable(payload, default=True)
    )


def build_entries() -> list[dict[str, Any]]:
    references = _load_json(REFERENCE_JSON)["entries"]
    ew_exact = _load_json(EW_EXACT_JSON)
    d11_exact = _load_json(D11_EXACT_JSON)
    d11_exact_higgs = _load_optional_json(D11_EXACT_HIGGS_PROMOTION_JSON)
    d11_exact_pair = _load_optional_json(D11_EXACT_SPLIT_PAIR_JSON)
    charged = _load_json(CHARGED_JSON)
    quark = _load_json(QUARK_JSON)
    charged_affine = _load_optional_json(CHARGED_AFFINE_JSON)
    quark_closure = _load_optional_json(QUARK_CLOSURE_JSON)
    quark_transport_lift = _load_optional_json(QUARK_TRANSPORT_LIFT_JSON)
    quark_transport_completion = _load_optional_json(QUARK_TRANSPORT_COMPLETION_JSON)
    quark_transport_forward_yukawas = _load_optional_json(QUARK_TRANSPORT_FORWARD_YUKAWAS_JSON)
    quark_end_to_end_chain = _load_optional_json(QUARK_END_TO_END_CHAIN_JSON)
    quark_public_exact_yukawa = _load_optional_json(QUARK_PUBLIC_YUKAWA_JSON)
    neutrino = _load_json(NEUTRINO_JSON)
    neutrino_bridge_rigidity = _load_json(NEUTRINO_BRIDGE_RIGIDITY_JSON)
    quark_exact_values = (
        dict(quark_public_exact_yukawa["public_exact_outputs"]["exact_running_values_gev"])
        if quark_public_exact_yukawa
        else {
            "u": quark["predicted_singular_values_u"][0],
            "c": quark["predicted_singular_values_u"][1],
            "t": quark["predicted_singular_values_u"][2],
            "d": quark["predicted_singular_values_d"][0],
            "s": quark["predicted_singular_values_d"][1],
            "b": quark["predicted_singular_values_d"][2],
        }
    )
    quark_exact_promotable = _quark_public_promotable(quark_public_exact_yukawa)
    quark_exact_kind = (
        "selected_class_theorem_grade_exact_forward_quark_closure"
        if quark_exact_promotable
        else (
            "selected_class_target_anchored_exact_witness"
            if quark_public_exact_yukawa
            else "exact_target_anchored_current_family_witness"
        )
    )
    quark_exact_scope = (
        (
            "selected_public_physical_quark_frame_class_only_but_sigma_datum_target_derived"
            if quark_public_exact_yukawa and not quark_exact_promotable
            else quark_public_exact_yukawa["theorem_scope"]
        )
        if quark_public_exact_yukawa
        else quark["theorem_scope"]
    )
    quark_exact_source = _repo_ref(QUARK_PUBLIC_YUKAWA_JSON) if quark_public_exact_yukawa else _repo_ref(QUARK_JSON)
    quark_public_note_prefix = (
        "Theorem-grade exact quark output on the selected public physical quark frame class chosen by `P`, "
        if quark_exact_promotable
        else "Selected-class exact quark witness on the public physical quark frame class chosen by `P`, "
    )
    quark_public_nonpromotion_note = (
        ""
        if quark_exact_promotable
        else "Under the strict non-circularity audit it is not promotable because the public sigma datum is target-derived. "
    )
    quark_exact_note = (
        (
            quark_public_note_prefix
            +
            f"emitted by `{quark_public_exact_yukawa['artifact']}`. The exact sextet matches the official PDG 2025 "
            "API running-quark target surface, and the theorem emits explicit exact forward Yukawas `Y_u` and `Y_d`. "
            + quark_public_nonpromotion_note
        )
        if quark_public_exact_yukawa
        else (
            "Exact current-family quark witness on `current_family_only`. The exact sextet matches the official "
            "PDG 2025 API running-quark target surface on that declared carrier. "
        )
    ) + (
        "The top coordinate uses PDG "
        f"summary `{references['top_quark']['source']['summary_id']}`. The auxiliary direct-top "
        f"entry `{references['top_quark_direct_aux']['source']['summary_id']}` is compare-only; "
        "[#207](https://github.com/FloatingPragma/observer-patch-holography/issues/207) is closed as a corpus-limited no-go by "
        "`code/particles/runs/calibration/direct_top_bridge_contract.json`. The same exact sextet is also "
        "realized on `current_family_only`. A separate restricted theorem "
        "surface emits a sector-attached `Sigma_ud^phys` element on "
        f"`{(quark_transport_lift or {}).get('theorem_scope', 'current_family_common_refinement_transport_frame_only')}`, "
        "the merged transport-frame completion closes the same "
        f"running sextet on `{(quark_transport_completion or {}).get('theorem_scope', 'current_family_common_refinement_transport_frame_only')}`, and the declared transport-frame "
        "chain emits explicit exact forward Yukawas `Y_u` and `Y_d` with certification status "
        f"`{(quark_transport_forward_yukawas or {}).get('certification_status', 'forward_matrix_certified')}`. The full declared-carrier chain is "
        f"recorded in `{(quark_end_to_end_chain or {}).get('artifact', 'oph_quark_current_family_end_to_end_exact_pdg_derivation_chain')}`. The target-free mass bridge closes separately "
        "on the emitted D12 ray. "
        + (
            "This theorem is selected-class closure only. It does not claim a global classification of all quark frame classes."
            if quark_public_exact_yukawa
            else "This entry is carrier-restricted and does not replace the selected-class public theorem."
        )
    )
    d11_split_promotable = _d11_split_promotable(d11_exact_pair)
    higgs_promotable = d11_split_promotable
    if d11_exact_pair:
        higgs_exact_kind = (
            "exact_source_only_higgs_top_split_calibration_theorem"
            if d11_split_promotable
            else "conditional_declared_surface_higgs_top_candidate"
        )
    elif d11_exact_higgs:
        higgs_exact_kind = "exact_target_anchored_higgs_calibration_theorem"
    else:
        higgs_exact_kind = "exact_target_anchored_compare_only_inverse_slice"
    neutrino_promotable = _neutrino_absolute_promotable(neutrino)
    neutrino_exact_kind = (
        "theorem_grade_weighted_cycle_absolute_attachment"
        if neutrino_promotable
        else "scale_free_weighted_cycle_theorem_with_compare_only_absolute_attachment_candidate"
    )
    neutrino_note_prefix = (
        "Theorem-grade weighted-cycle absolute neutrino mass from the emitted bridge-rigidity and absolute-attachment pair, "
        if neutrino_promotable
        else "Scale-free weighted-cycle neutrino branch with compare-only absolute attachment candidate, "
    )
    c_nu_display = neutrino_bridge_rigidity.get("emitted_value")
    if c_nu_display is None:
        c_nu_display = neutrino_bridge_rigidity.get("display_value")

    return [
        {
            "particle_id": "photon",
            "label": "Photon",
            "mass_gev": 0.0,
            "exact_kind": "structural_zero",
            "scope": "structural",
            "promotable": True,
            "depends_on_quantitative_particle_pipeline": False,
            "source_artifact": "structural_gauge_redundancy_surface",
            "note": "Exact structural zero from the nonbroken U(1) overlap-gluing redundancy.",
        },
        {
            "particle_id": "gluon",
            "label": "Gluon",
            "mass_gev": 0.0,
            "exact_kind": "structural_zero",
            "scope": "structural",
            "promotable": True,
            "depends_on_quantitative_particle_pipeline": False,
            "source_artifact": "structural_color_gauge_surface",
            "note": "Exact structural zero for the color gauge sector.",
        },
        {
            "particle_id": "graviton",
            "label": "Graviton",
            "mass_gev": 0.0,
            "exact_kind": "structural_zero",
            "scope": "structural",
            "promotable": True,
            "depends_on_quantitative_particle_pipeline": False,
            "source_artifact": "structural_diffeomorphism_redundancy_surface",
            "note": "Exact structural zero from bulk diffeomorphism redundancy.",
        },
        {
            "particle_id": "w_boson",
            "label": "W Boson",
            "mass_gev": ew_exact["coherent_repaired_quintet"]["MW_pole"],
            "exact_kind": "exact_frozen_target_compare_only_adapter",
            "scope": "frozen_authoritative_target_surface",
            "promotable": False,
            "source_artifact": _repo_ref(EW_EXACT_JSON),
            "note": "Exact on the frozen D10 repair surface.",
        },
        {
            "particle_id": "z_boson",
            "label": "Z Boson",
            "mass_gev": ew_exact["coherent_repaired_quintet"]["MZ_pole"],
            "exact_kind": "exact_frozen_target_compare_only_adapter",
            "scope": "frozen_authoritative_target_surface",
            "promotable": False,
            "source_artifact": _repo_ref(EW_EXACT_JSON),
            "note": "Exact on the frozen D10 repair surface.",
        },
        {
            "particle_id": "higgs",
            "label": "Higgs Boson",
            "mass_gev": (
                d11_exact_pair["exact_split_pair"]["mH_gev"]
                if d11_exact_pair
                else (
                d11_exact_higgs["mass_readout"]["mH_gev"]
                if d11_exact_higgs
                else d11_exact["predicted_outputs"]["mH_gev"]
                )
            ),
            "exact_kind": higgs_exact_kind,
            "scope": (
                d11_exact_pair["theorem_scope"]
                if d11_exact_pair
                else (
                d11_exact_higgs["theorem_scope"]
                if d11_exact_higgs
                else d11_exact["scope"]
                )
            ),
            "promotable": higgs_promotable,
            "source_artifact": (
                _repo_ref(D11_EXACT_SPLIT_PAIR_JSON)
                if d11_exact_pair
                else (
                _repo_ref(D11_EXACT_HIGGS_PROMOTION_JSON)
                if d11_exact_higgs
                else _repo_ref(D11_EXACT_JSON)
                )
            ),
            "note": (
                (
                "Exact source-only Higgs theorem on the declared D10/D11 surface. "
                "The same theorem emits the exact Higgs row together with a companion top coordinate by direct Jacobian readout from the live D10 repair tuple. "
                "At PDG quoting precision the Higgs row lands on the 2025 Higgs average. "
                "The exact public running-top row uses the PDG 2025 cross-section entry `Q007TP4`. "
                "The auxiliary direct-top average `Q007TP` is compare-only; "
                "[#207](https://github.com/FloatingPragma/observer-patch-holography/issues/207) is closed as a corpus-limited no-go by "
                "`code/particles/runs/calibration/direct_top_bridge_contract.json`."
                if d11_split_promotable
                else
                "Conditional Higgs/top split candidate on the declared D10/D11 surface. It emits the same numeric split pair, but strict promotion is blocked until the upstream D10 target-free repair law is closed and promotable."
                )
                if d11_exact_pair
                else (
                "Exact target-anchored Higgs calibration theorem on the declared D10/D11 surface."
                if d11_exact_higgs
                else "Exact compare-only inverse slice on the D11 Jacobian."
                )
            ),
        },
        {
            "particle_id": "electron",
            "label": "Electron",
            "mass_gev": charged["predicted_singular_values_abs"][0],
            "exact_kind": "exact_target_anchored_current_family_witness",
            "scope": charged["theorem_scope"],
            "promotable": False,
            "source_artifact": _repo_ref(CHARGED_JSON),
            "supporting_theorem_artifact": _repo_ref(CHARGED_THEOREM_JSON),
            "supporting_scope_closure_artifact": _repo_ref(CHARGED_AFFINE_JSON),
            "note": "Exact `current_family_only` charged-lepton witness on a closed ordered-three-point readout chain, with the scoped affine coordinate `A_ch_current_family` closed on the same exact family.",
        },
        {
            "particle_id": "muon",
            "label": "Muon",
            "mass_gev": charged["predicted_singular_values_abs"][1],
            "exact_kind": "exact_target_anchored_current_family_witness",
            "scope": charged["theorem_scope"],
            "promotable": False,
            "source_artifact": _repo_ref(CHARGED_JSON),
            "supporting_theorem_artifact": _repo_ref(CHARGED_THEOREM_JSON),
            "supporting_scope_closure_artifact": _repo_ref(CHARGED_AFFINE_JSON),
            "note": "Exact `current_family_only` charged-lepton witness on a closed ordered-three-point readout chain, with the scoped affine coordinate `A_ch_current_family` closed on the same exact family.",
        },
        {
            "particle_id": "tau",
            "label": "Tau",
            "mass_gev": charged["predicted_singular_values_abs"][2],
            "exact_kind": "exact_target_anchored_current_family_witness",
            "scope": charged["theorem_scope"],
            "promotable": False,
            "source_artifact": _repo_ref(CHARGED_JSON),
            "supporting_theorem_artifact": _repo_ref(CHARGED_THEOREM_JSON),
            "supporting_scope_closure_artifact": _repo_ref(CHARGED_AFFINE_JSON),
            "note": "Exact `current_family_only` charged-lepton witness on a closed ordered-three-point readout chain, with the scoped affine coordinate `A_ch_current_family` closed on the same exact family.",
        },
        {
            "particle_id": "up_quark",
            "label": "Up Quark",
            "mass_gev": quark_exact_values["u"],
            "exact_kind": quark_exact_kind,
            "scope": quark_exact_scope,
            "promotable": quark_exact_promotable,
            "source_artifact": quark_exact_source,
            "supporting_theorem_artifact": _repo_ref(QUARK_THEOREM_JSON),
            "supporting_scope_closure_artifact": _repo_ref(QUARK_CLOSURE_JSON),
            "supporting_transport_frame_artifact": _repo_ref(QUARK_TRANSPORT_LIFT_JSON),
            "supporting_transport_frame_completion_artifact": _repo_ref(QUARK_TRANSPORT_COMPLETION_JSON),
            "supporting_transport_frame_forward_yukawas_artifact": _repo_ref(QUARK_TRANSPORT_FORWARD_YUKAWAS_JSON),
            "supporting_end_to_end_chain_artifact": _repo_ref(QUARK_END_TO_END_CHAIN_JSON),
            "note": quark_exact_note,
        },
        {
            "particle_id": "charm_quark",
            "label": "Charm Quark",
            "mass_gev": quark_exact_values["c"],
            "exact_kind": quark_exact_kind,
            "scope": quark_exact_scope,
            "promotable": quark_exact_promotable,
            "source_artifact": quark_exact_source,
            "supporting_theorem_artifact": _repo_ref(QUARK_THEOREM_JSON),
            "supporting_scope_closure_artifact": _repo_ref(QUARK_CLOSURE_JSON),
            "supporting_transport_frame_artifact": _repo_ref(QUARK_TRANSPORT_LIFT_JSON),
            "supporting_transport_frame_completion_artifact": _repo_ref(QUARK_TRANSPORT_COMPLETION_JSON),
            "supporting_transport_frame_forward_yukawas_artifact": _repo_ref(QUARK_TRANSPORT_FORWARD_YUKAWAS_JSON),
            "supporting_end_to_end_chain_artifact": _repo_ref(QUARK_END_TO_END_CHAIN_JSON),
            "note": quark_exact_note,
        },
        {
            "particle_id": "top_quark",
            "label": "Top Quark",
            "mass_gev": quark_exact_values["t"],
            "exact_kind": quark_exact_kind,
            "scope": quark_exact_scope,
            "promotable": quark_exact_promotable,
            "source_artifact": quark_exact_source,
            "supporting_theorem_artifact": _repo_ref(QUARK_THEOREM_JSON),
            "supporting_scope_closure_artifact": _repo_ref(QUARK_CLOSURE_JSON),
            "supporting_transport_frame_artifact": _repo_ref(QUARK_TRANSPORT_LIFT_JSON),
            "supporting_transport_frame_completion_artifact": _repo_ref(QUARK_TRANSPORT_COMPLETION_JSON),
            "supporting_transport_frame_forward_yukawas_artifact": _repo_ref(QUARK_TRANSPORT_FORWARD_YUKAWAS_JSON),
            "supporting_end_to_end_chain_artifact": _repo_ref(QUARK_END_TO_END_CHAIN_JSON),
            "note": quark_exact_note,
        },
        {
            "particle_id": "down_quark",
            "label": "Down Quark",
            "mass_gev": quark_exact_values["d"],
            "exact_kind": quark_exact_kind,
            "scope": quark_exact_scope,
            "promotable": quark_exact_promotable,
            "source_artifact": quark_exact_source,
            "supporting_theorem_artifact": _repo_ref(QUARK_THEOREM_JSON),
            "supporting_scope_closure_artifact": _repo_ref(QUARK_CLOSURE_JSON),
            "supporting_transport_frame_artifact": _repo_ref(QUARK_TRANSPORT_LIFT_JSON),
            "supporting_transport_frame_completion_artifact": _repo_ref(QUARK_TRANSPORT_COMPLETION_JSON),
            "supporting_transport_frame_forward_yukawas_artifact": _repo_ref(QUARK_TRANSPORT_FORWARD_YUKAWAS_JSON),
            "supporting_end_to_end_chain_artifact": _repo_ref(QUARK_END_TO_END_CHAIN_JSON),
            "note": quark_exact_note,
        },
        {
            "particle_id": "strange_quark",
            "label": "Strange Quark",
            "mass_gev": quark_exact_values["s"],
            "exact_kind": quark_exact_kind,
            "scope": quark_exact_scope,
            "promotable": quark_exact_promotable,
            "source_artifact": quark_exact_source,
            "supporting_theorem_artifact": _repo_ref(QUARK_THEOREM_JSON),
            "supporting_scope_closure_artifact": _repo_ref(QUARK_CLOSURE_JSON),
            "supporting_transport_frame_artifact": _repo_ref(QUARK_TRANSPORT_LIFT_JSON),
            "supporting_transport_frame_completion_artifact": _repo_ref(QUARK_TRANSPORT_COMPLETION_JSON),
            "supporting_transport_frame_forward_yukawas_artifact": _repo_ref(QUARK_TRANSPORT_FORWARD_YUKAWAS_JSON),
            "supporting_end_to_end_chain_artifact": _repo_ref(QUARK_END_TO_END_CHAIN_JSON),
            "note": quark_exact_note,
        },
        {
            "particle_id": "bottom_quark",
            "label": "Bottom Quark",
            "mass_gev": quark_exact_values["b"],
            "exact_kind": quark_exact_kind,
            "scope": quark_exact_scope,
            "promotable": quark_exact_promotable,
            "source_artifact": quark_exact_source,
            "supporting_theorem_artifact": _repo_ref(QUARK_THEOREM_JSON),
            "supporting_scope_closure_artifact": _repo_ref(QUARK_CLOSURE_JSON),
            "supporting_transport_frame_artifact": _repo_ref(QUARK_TRANSPORT_LIFT_JSON),
            "supporting_transport_frame_completion_artifact": _repo_ref(QUARK_TRANSPORT_COMPLETION_JSON),
            "supporting_transport_frame_forward_yukawas_artifact": _repo_ref(QUARK_TRANSPORT_FORWARD_YUKAWAS_JSON),
            "supporting_end_to_end_chain_artifact": _repo_ref(QUARK_END_TO_END_CHAIN_JSON),
            "note": quark_exact_note,
        },
        {
            "particle_id": "electron_neutrino",
            "label": "Electron Neutrino",
            "mass_eV": neutrino["outputs"]["masses_eV"][0],
            "exact_kind": neutrino_exact_kind,
            "scope": "weighted_cycle_bridge_rigid_absolute_family",
            "promotable": neutrino_promotable,
            "source_artifact": _repo_ref(NEUTRINO_JSON),
            "supporting_bridge_rigidity_artifact": _repo_ref(NEUTRINO_BRIDGE_RIGIDITY_JSON),
            "note": (
                neutrino_note_prefix
                +
                f"with `C_nu = {float(c_nu_display):.16f}`, "
                f"`P_nu = {neutrino_bridge_rigidity['emitted_proxy']['value']:.15f}`, and "
                f"`B_nu = {neutrino['outputs']['B_nu']:.15f}`."
            ),
        },
        {
            "particle_id": "muon_neutrino",
            "label": "Muon Neutrino",
            "mass_eV": neutrino["outputs"]["masses_eV"][1],
            "exact_kind": neutrino_exact_kind,
            "scope": "weighted_cycle_bridge_rigid_absolute_family",
            "promotable": neutrino_promotable,
            "source_artifact": _repo_ref(NEUTRINO_JSON),
            "supporting_bridge_rigidity_artifact": _repo_ref(NEUTRINO_BRIDGE_RIGIDITY_JSON),
            "note": (
                neutrino_note_prefix
                +
                f"with `C_nu = {float(c_nu_display):.16f}`, "
                f"`P_nu = {neutrino_bridge_rigidity['emitted_proxy']['value']:.15f}`, and "
                f"`B_nu = {neutrino['outputs']['B_nu']:.15f}`."
            ),
        },
        {
            "particle_id": "tau_neutrino",
            "label": "Tau Neutrino",
            "mass_eV": neutrino["outputs"]["masses_eV"][2],
            "exact_kind": neutrino_exact_kind,
            "scope": "weighted_cycle_bridge_rigid_absolute_family",
            "promotable": neutrino_promotable,
            "source_artifact": _repo_ref(NEUTRINO_JSON),
            "supporting_bridge_rigidity_artifact": _repo_ref(NEUTRINO_BRIDGE_RIGIDITY_JSON),
            "note": (
                neutrino_note_prefix
                +
                f"with `C_nu = {float(c_nu_display):.16f}`, "
                f"`P_nu = {neutrino_bridge_rigidity['emitted_proxy']['value']:.15f}`, and "
                f"`B_nu = {neutrino['outputs']['B_nu']:.15f}`."
            ),
        },
    ]


def build_markdown(generated_utc: str, entries: list[dict[str, Any]]) -> str:
    quark_selected_class = any(
        entry["particle_id"] == "up_quark"
        and entry["exact_kind"] == "selected_class_theorem_grade_exact_forward_quark_closure"
        for entry in entries
    )
    lines = [
        "# Exact Non-Hadron Masses",
        "",
        f"Generated: `{generated_utc}`",
        "",
        "This bundle gives one exact mass output for every non-hadron particle on the declared OPH surfaces.",
        "It records exact-output surfaces rather than one uniform theorem tier.",
        (
            "For quarks, the exact theorem surface matches the official PDG 2025 API running-quark target surface on the selected public physical quark frame class chosen by `P`."
            if quark_selected_class
            else "For quarks, the exact carrier-restricted witness surface matches the official PDG 2025 API running-quark target surface on `current_family_only`."
        ),
        (
            "The same selected-class theorem emits explicit exact forward Yukawas `Y_u` and `Y_d`, and the same sextet is also realized on `current_family_only` and on the restricted current-family common-refinement transport-frame carrier."
            if quark_selected_class
            else "The same sextet is also realized on the restricted current-family common-refinement transport-frame carrier, which emits explicit exact forward Yukawas `Y_u` and `Y_d` on that declared carrier."
        ),
        "For charged leptons, this bundle records the exact same-family witness surface. The theorem surface also contains the live same-label `q_e` readback, a source-side determinant character for a fixed formal source multiplicity vector, a conditional determinant-line lift, and an algebraic charged-mass readout once theorem-grade `A_ch(P)` is given. Issue #201 is closed as a corpus-limited no-go: the available corpus does not attach that source-side character to the physical charged determinant line.",
        "The top coordinate uses the PDG 2025 cross-section mass entry `Q007TP4`. The auxiliary direct-top entry `Q007TP` is compare-only; [#207](https://github.com/FloatingPragma/observer-patch-holography/issues/207) is closed as a corpus-limited no-go by `code/particles/runs/calibration/direct_top_bridge_contract.json`.",
        "",
        "| Particle | Exact Mass | Kind | Scope | Source |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for entry in entries:
        if "mass_gev" in entry:
            value = f"`{entry['mass_gev']} GeV`"
        else:
            value = f"`{entry['mass_eV']} eV`"
        lines.append(
            f"| {entry['label']} | {value} | `{entry['exact_kind']}` | `{entry['scope']}` | `{entry['source_artifact']}` |"
        )
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the exact non-hadron mass bundle.")
    parser.add_argument("--markdown-out", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--forward-out", default=str(DEFAULT_FORWARD_OUT))
    args = parser.parse_args()

    generated_utc = _timestamp()
    entries = build_entries()
    payload = {
        "artifact": "oph_exact_nonhadron_mass_bundle",
        "generated_utc": generated_utc,
        "status": "exact_output_lane_closed_nonhadron_only",
        "entries": entries,
        "excluded_lane": "hadrons_compute_bound",
    }

    markdown_out = pathlib.Path(args.markdown_out)
    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.write_text(build_markdown(generated_utc, entries) + "\n", encoding="utf-8")

    json_out = pathlib.Path(args.json_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    forward_out = pathlib.Path(args.forward_out)
    forward_out.parent.mkdir(parents=True, exist_ok=True)
    forward_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"saved: {markdown_out}")
    print(f"saved: {json_out}")
    print(f"saved: {forward_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
