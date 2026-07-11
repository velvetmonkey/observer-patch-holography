#!/usr/bin/env python3
"""Emit the normalized same-label overlap-defect weight section."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCALAR_CERTIFICATE = ROOT / "particles" / "runs" / "neutrino" / "same_label_scalar_certificate.json"
READBACK = ROOT / "particles" / "runs" / "neutrino" / "realized_same_label_gap_defect_readback.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "same_label_overlap_defect_weight_normalizer.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(values: dict[str, float]) -> tuple[dict[str, float], float]:
    mean = sum(values.values()) / float(len(values))
    return ({key: float(val) / mean for key, val in values.items()}, mean)


def build_payload(certificate: dict[str, Any], readback: dict[str, Any]) -> dict[str, Any]:
    q_e = {key: float(val) for key, val in certificate["q_e"].items()}
    eta_e = {key: float(val) for key, val in certificate["eta_e"].items()}
    mu_e = {key: float(val) for key, val in certificate["mu_e"].items()}
    qbar_e, q_mean = _normalized(q_e)
    exp_eta = {key: float(math.exp(val)) for key, val in eta_e.items()}
    exp_eta_bar, exp_eta_mean = _normalized(exp_eta)
    base_mu_nu = float(certificate["base_mu_nu"])
    mu_ratio = {key: float(val) / base_mu_nu for key, val in mu_e.items()}
    source_closed = (
        certificate.get("source_only_physical_input_eligible") is True
        and (certificate.get("source_closure_status") or {}).get("closed") is True
        and readback.get("source_only_physical_input_eligible") is True
        and (readback.get("source_closure_status") or {}).get("closed") is True
    )

    return {
        "artifact": "oph_same_label_overlap_defect_weight_normalizer",
        "generated_utc": _timestamp(),
        "status": (
            "closed_from_source_closed_same_label_scalar_certificate"
            if source_closed
            else "conditional_normalizer_from_source_open_scalar_certificate"
        ),
        "public_promotion_allowed": False,
        "source_only_physical_input_eligible": source_closed,
        "source_closure_status": dict(certificate.get("source_closure_status") or {"closed": False}),
        "source_artifacts": [
            "oph_neutrino_same_label_scalar_certificate",
            "oph_realized_same_label_gap_defect_readback",
        ],
        "proof_status": "exact_normalization_identity_conditional_on_certificate",
        "same_label": dict(certificate.get("same_label") or {}),
        "realized_same_label_arrows": list(certificate.get("realized_same_label_arrows") or []),
        "raw_edge_score_rule": certificate["rules"]["q_rule"],
        "normalized_attachment_section_rule": "qbar_e = q_e / mean_f(q_f)",
        "equivalence_theorem": "qbar_e = exp(eta_e) / mean_f(exp(eta_f))",
        "weight_rule": "mu_e = base_mu_nu * qbar_e",
        "base_mu_nu": base_mu_nu,
        "q_e": q_e,
        "q_mean": q_mean,
        "qbar_e": qbar_e,
        "exp_eta_e": exp_eta,
        "exp_eta_mean": exp_eta_mean,
        "exp_eta_bar_e": exp_eta_bar,
        "eta_e": eta_e,
        "mu_e": mu_e,
        "mu_e_over_base_mu_nu": mu_ratio,
        "same_label_overlap_sq": dict(readback.get("same_label_overlap_sq") or {}),
        "gap_e": dict(readback.get("gap_e") or {}),
        "defect_e": dict(readback.get("defect_e") or {}),
        "identities_verified": {
            "qbar_matches_exp_eta_bar": all(
                abs(qbar_e[key] - exp_eta_bar[key]) < 1.0e-15 for key in qbar_e
            ),
            "mu_e_matches_base_times_qbar": all(
                abs(mu_e[key] - base_mu_nu * qbar_e[key]) < 1.0e-15 for key in qbar_e
            ),
        },
        "next_exact_object": {
            "artifact": (
                "oph_neutrino_attachment_bridge_invariant"
                if source_closed
                else "source_closed_neutrino_operator_basis_and_mass_label_contract"
            ),
            "status": "open",
            "bridge_law": "lambda_nu = m_star_eV * F_nu(qbar, I_nu)",
            "minimal_alternative": "prove_collapse_theorem_F_nu_equals_F_nu(qbar)",
        },
        "notes": [
            "The normalization identities are exact once the same-label scalar certificate is supplied.",
            (
                "The certificate passes its physical source-closure gate."
                if source_closed
                else "The current certificate is numerically complete but inherits a template family kernel and candidate overlap-line lift."
            ),
            "A physical operator, basis, and mass-label contract must close before any absolute-scale attachment can be promoted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the same-label overlap-defect weight normalizer artifact.")
    parser.add_argument("--scalar-certificate", default=str(SCALAR_CERTIFICATE))
    parser.add_argument("--readback", default=str(READBACK))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    payload = build_payload(
        certificate=_load_json(Path(args.scalar_certificate)),
        readback=_load_json(Path(args.readback)),
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
