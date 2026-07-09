#!/usr/bin/env python3
"""Build the compact-transient receipt scaffold.

This is a paper-stack mirror for the compact-transient simulator workbench. It
freezes the CR0-CR4 claim ladder and receipt files for FRBs, old-host compact
sources, and black-hole recycling, but it does not analyze transient catalogs
or promote any event class into an OPH confirmation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "particles" / "runs" / "compact_transients" / "receipt_scaffold"

CLAIM_TIERS = (
    "CR0_VOCABULARY_ONLY",
    "CR1_QUOTIENT_DIAGNOSTIC",
    "CR2_CONDITIONAL_PHENOMENOLOGY",
    "CR3_FROZEN_PHYSICAL_PREDICTION",
    "CR4_SOURCE_ONLY_OPH_PREDICTION",
)

FORBIDDEN_SOURCE_TOKENS = (
    "ringdown_residual",
    "ringdown_residuals",
    "postfit_repair_tail_amplitude",
    "post_fit_repair_tail_amplitude",
    "echo_score",
    "echo_scores",
    "waveform_template_tuned_after_residual_inspection",
)

REQUIRED_FILES = (
    "manifest.json",
    "compact_history.json",
    "compact_quotient.json",
    "source_law.json",
    "repair_emission_kernel.json",
    "packet_parent.json",
    "detector_thinning.json",
    "censoring.json",
    "point_process_likelihood.json",
    "frb_controls.json",
    "bh_recycling.json",
    "refinement_accuracy.json",
    "promotion_audit.json",
    "claim.md",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def target_leak_hits(config: Path | None) -> list[str]:
    if config is None or not config.is_file():
        return []
    text = config.read_text(encoding="utf-8")
    haystack = text.lower()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if parsed is not None:
        haystack = json.dumps(parsed, sort_keys=True).lower()
    return sorted(token for token in FORBIDDEN_SOURCE_TOKENS if token in haystack)


def default_receipts(*, leak_hits: list[str]) -> dict[str, bool]:
    no_generation_leak = not leak_hits
    return {
        "COMPACT_HISTORY_RECEIPT": True,
        "COMPACT_QUOTIENT_RECEIPT": True,
        "COMPACT_SOURCE_LAW_RECEIPT": True,
        "PACKETIZED_KERNEL_RECEIPT": True,
        "PHYSICAL_CLOCK_RECEIPT": True,
        "FINITE_PACKET_PARENT_RECEIPT": True,
        "PACKET_CONSERVATION_RECEIPT": True,
        "PROPAGATION_RECEIPT": True,
        "DETECTION_THINNING_RECEIPT": True,
        "CENSORING_AND_UPPER_LIMIT_RECEIPT": True,
        "POINT_PROCESS_LIKELIHOOD_RECEIPT": True,
        "REPEATER_HISTORY_LIKELIHOOD_RECEIPT": True,
        "FRB_SOURCE_IDENTITY_RECEIPT": True,
        "FRB_CADENCE_EXPOSURE_RECEIPT": True,
        "BH_GENEALOGY_DAG_RECEIPT": True,
        "NO_GENERATION_LEAKAGE_RECEIPT": no_generation_leak,
        "CONTROL_MODEL_RECEIPT": False,
        "REFINEMENT_STABILITY_RECEIPT": False,
        "SIMULATOR_ACCURACY_RECEIPT": False,
        "FROZEN_HASHES_RECEIPT": False,
        "HELDOUT_LIKELIHOOD_RECEIPT": True,
        "PROMOTION_AUDIT_RECEIPT": True,
        "COMPACT_SOURCE_ACTION_DERIVED_RECEIPT": False,
        "EMISSION_MICROPHYSICS_DERIVED_RECEIPT": False,
        "PHYSICAL_CLOCK_DERIVED_RECEIPT": False,
        "OLD_HOST_FRB_SOURCE_THEOREM_RECEIPT": False,
        "BH_GENEALOGY_PRIOR_THEOREM_RECEIPT": False,
    }


def strongest_claim(receipts: dict[str, bool], *, leak_hits: list[str]) -> tuple[str, str | None]:
    if leak_hits:
        return "CR1_QUOTIENT_DIAGNOSTIC", "NO_GENERATION_LEAKAGE_RECEIPT"
    cr2 = (
        "COMPACT_QUOTIENT_RECEIPT",
        "COMPACT_SOURCE_LAW_RECEIPT",
        "PACKETIZED_KERNEL_RECEIPT",
        "PHYSICAL_CLOCK_RECEIPT",
        "FINITE_PACKET_PARENT_RECEIPT",
        "PROPAGATION_RECEIPT",
        "DETECTION_THINNING_RECEIPT",
        "POINT_PROCESS_LIKELIHOOD_RECEIPT",
        "CENSORING_AND_UPPER_LIMIT_RECEIPT",
        "HELDOUT_LIKELIHOOD_RECEIPT",
    )
    for name in cr2:
        if not receipts.get(name, False):
            return "CR1_QUOTIENT_DIAGNOSTIC", name
    cr3_gate_labels = {
        "CONTROL_MODEL_RECEIPT": "CONTROLS",
        "REFINEMENT_STABILITY_RECEIPT": "REFINEMENT",
        "FROZEN_HASHES_RECEIPT": "FREEZE",
    }
    for name, gate_label in cr3_gate_labels.items():
        if not receipts.get(name, False):
            return "CR2_CONDITIONAL_PHENOMENOLOGY", gate_label
    for name in (
        "COMPACT_SOURCE_ACTION_DERIVED_RECEIPT",
        "EMISSION_MICROPHYSICS_DERIVED_RECEIPT",
        "PHYSICAL_CLOCK_DERIVED_RECEIPT",
        "OLD_HOST_FRB_SOURCE_THEOREM_RECEIPT",
        "BH_GENEALOGY_PRIOR_THEOREM_RECEIPT",
    ):
        if not receipts.get(name, False):
            return "CR3_FROZEN_PHYSICAL_PREDICTION", name
    return "CR4_SOURCE_ONLY_OPH_PREDICTION", None


def base_payload(name: str, receipts: dict[str, bool], claim: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "generated_utc": now_utc(),
        "claim": claim,
        "physical_claim": claim in {"CR3_FROZEN_PHYSICAL_PREDICTION", "CR4_SOURCE_ONLY_OPH_PREDICTION"},
        "readiness_gates": receipts,
    }


def build_payloads(*, config: Path | None) -> dict[str, str | dict[str, Any]]:
    leak_hits = target_leak_hits(config)
    receipts = default_receipts(leak_hits=leak_hits)
    claim, first_blocked = strongest_claim(receipts, leak_hits=leak_hits)
    return {
        "compact_history.json": {
            **base_payload("compact_transient_history", receipts, claim),
            "history_object": "Hist_r^CR",
            "requires_source_identity": True,
            "requires_genealogy_for_bh": True,
        },
        "compact_quotient.json": {
            **base_payload("compact_transient_quotient", receipts, claim),
            "quotient": "Q_r^CR = Sigma_r^CR/Gamma_r^CR",
            "likelihood_may_read_representative_labels": False,
        },
        "source_law.json": {
            **base_payload("compact_transient_source_law", receipts, claim),
            "law": "mu_r^CR plus packetized K_Gamma,r^hist",
            "normal_form_is_not_source_law": True,
        },
        "repair_emission_kernel.json": {
            **base_payload("repair_emission_kernel", receipts, claim),
            "kernel": "K_Gamma,r(dq',dPi,dell,dtau|q)",
            "independence_shortcuts_require_factorization_theorem": True,
        },
        "packet_parent.json": {
            **base_payload("finite_packet_parent", receipts, claim),
            "required_sectors": ["radio", "gamma", "GW", "optical", "neutrino", "environmental", "recipient"],
            "scalar_event_row_sufficient": False,
        },
        "detector_thinning.json": {
            **base_payload("detector_thinning", receipts, claim),
            "kernel": "Thin_c(dO|y,ObsWin_c)=p_det(y;ObsWin_c) R_det,c(dO|y)",
        },
        "censoring.json": {
            **base_payload("censoring_and_upper_limits", receipts, claim),
            "kernel": "Cens_c(dU|y,ObsWin_c)=(1-p_det)U_c(dU|y)",
            "score_nondetections": True,
        },
        "point_process_likelihood.json": {
            **base_payload("marked_catalog_likelihood", receipts, claim),
            "likelihood": "sum_i log Lambda(O_i)-integral_ObsWin Lambda(dO)",
            "compensator_required": True,
        },
        "frb_controls.json": {
            **base_payload("frb_repair_reload_controls", receipts, claim),
            "controls": {
                "M0": "young_only",
                "M1": "young_plus_old_gc_poisson_or_weibull_timing",
                "M2": "young_plus_old_gc_repair_reload_timing",
            },
            "first_prediction": "old/GC repeaters show fluence-conditioned recovery after cadence and exposure correction",
            "host_mixture_rank_required": True,
        },
        "bh_recycling.json": {
            **base_payload("black_hole_recycling", receipts, claim),
            "target_leak_hits": leak_hits,
            "genealogy_dag_required": True,
            "forbidden_path": "ringdown_residual -> generation_label -> claim_success",
            "repair_tail_template": "frozen damped sinusoid with independent generation prior",
        },
        "refinement_accuracy.json": {
            **base_payload("refinement_and_accuracy", receipts, claim),
            "accuracy_bound": (
                "epsilon_mu + E[N] epsilon_K + epsilon_E + epsilon_prop + "
                "epsilon_detector + epsilon_canon + epsilon_clock + epsilon_mc"
            ),
            "simulator_accuracy_receipt": receipts["SIMULATOR_ACCURACY_RECEIPT"],
        },
        "promotion_audit.json": {
            **base_payload("compact_transient_promotion_audit", receipts, claim),
            "claim_tiers": list(CLAIM_TIERS),
            "first_blocked_gate": first_blocked,
            "promotion_allowed": claim in {"CR3_FROZEN_PHYSICAL_PREDICTION", "CR4_SOURCE_ONLY_OPH_PREDICTION"},
            "target_leak_hits": leak_hits,
        },
        "claim.md": claim + "\n",
    }


def write_payload(path: Path, payload: str | dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def build_bundle(out_dir: Path, *, config: Path | None = None) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    payloads = build_payloads(config=config)
    file_hashes: dict[str, str] = {}
    for rel_path, payload in payloads.items():
        path = out_dir / rel_path
        write_payload(path, payload)
        file_hashes[rel_path] = sha256_bytes(path.read_bytes())
    claim = (out_dir / "claim.md").read_text(encoding="utf-8").strip()
    audit = json.loads((out_dir / "promotion_audit.json").read_text(encoding="utf-8"))
    missing = [
        rel_path
        for rel_path in REQUIRED_FILES
        if rel_path != "manifest.json" and not (out_dir / rel_path).is_file()
    ]
    manifest = {
        "artifact": "compact_transient_receipt_manifest",
        "generated_utc": now_utc(),
        "milestone": "COMPACT_TRANSIENT_RECEIPT_SCAFFOLD",
        "strongest_allowed_claim": claim,
        "first_blocked_gate": audit["first_blocked_gate"],
        "promotion_allowed": audit["promotion_allowed"],
        "physical_claim": audit["physical_claim"],
        "target_leak_hits": audit["target_leak_hits"],
        "required_files": list(REQUIRED_FILES),
        "missing_files": missing,
        "file_hashes": file_hashes,
    }
    write_payload(out_dir / "manifest.json", manifest)
    manifest["file_hashes"]["manifest.json"] = sha256_bytes((out_dir / "manifest.json").read_bytes())
    write_payload(out_dir / "manifest.json", manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=DEFAULT_OUT, type=Path)
    parser.add_argument("--config", default=None, type=Path)
    args = parser.parse_args(argv)
    manifest = build_bundle(args.output, config=args.config)
    print(json.dumps(manifest, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
