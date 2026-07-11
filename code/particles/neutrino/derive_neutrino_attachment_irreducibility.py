#!/usr/bin/env python3
"""Prove a conditional algebraic scale no-go on the rejected candidate stack.

This script sharpens the conditional algebraic frontier without promoting the
target-informed weighted-cycle matrix to a physical OPH branch.

Main theorem proved from the live artifacts:
1. The weighted-cycle matrix factors exactly through q_e = q_mean * qbar_e.
2. Therefore C(q,psi) = q_mean**p * C(qbar,psi).
3. Hence mhat_i(q,psi) = q_mean**p * mtilde_i(qbar,psi) and
   Delta_hat_ij(q,psi) = q_mean**(2p) * Deltatilde_ij(qbar,psi).
4. The attached normalizer + scalar stack fixes qbar, the centered phase data,
   and the centered scalar evaluator, but it leaves one free positive amplitude
   orbit A_nu in
       m_i = A_nu * mtilde_i,
       Delta m^2_ij = A_nu**2 * Deltatilde_ij.
5. Since the current attached stack is identical on that whole orbit, no
   theorem-grade collapse to a function of the present attached stack exists.
   One positive bridge invariant remains irreducible on the current corpus.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
REPAIR_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_repair.json"
THEOREM_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_weighted_cycle_theorem_object.json"
NORMALIZER_JSON = ROOT / "particles" / "runs" / "neutrino" / "same_label_overlap_defect_weight_normalizer.json"
SCALAR_JSON = ROOT / "particles" / "runs" / "neutrino" / "majorana_overlap_defect_scalar_evaluator.json"
COMPARE_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_compare_only_scale_fit.json"
ABSOLUTE_SCAFFOLD_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_absolute_attachment_scaffold.json"
CORRECTION_AUDIT_JSON = ROOT / "particles" / "runs" / "neutrino" / "neutrino_bridge_correction_candidate_audit.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "neutrino" / "neutrino_attachment_irreducibility_theorem.json"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _cycle_matrix(*, weights: dict[str, float], chi: float, phase: dict[str, float]) -> np.ndarray:
    return np.array(
        [
            [
                -chi * weights["psi31"],
                weights["psi31"] * np.exp(1j * phase["psi31"]),
                weights["psi23"] * np.exp(1j * phase["psi23"]),
            ],
            [
                weights["psi31"] * np.exp(1j * phase["psi31"]),
                -chi * weights["psi12"],
                weights["psi12"] * np.exp(1j * phase["psi12"]),
            ],
            [
                weights["psi23"] * np.exp(1j * phase["psi23"]),
                weights["psi12"] * np.exp(1j * phase["psi12"]),
                -chi * weights["psi23"],
            ],
        ],
        dtype=complex,
    )


def _standardize_columns(unitary: np.ndarray) -> np.ndarray:
    out = unitary.copy()
    for j in range(out.shape[1]):
        ph = float(np.angle(out[0, j]))
        out[:, j] *= np.exp(-1j * ph)
        if float(np.real(out[0, j])) < 0.0:
            out[:, j] *= -1.0
    return out


def _spectral_data(cycle_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict[str, float], float]:
    hermitian = cycle_matrix.conjugate().T @ cycle_matrix
    evals, unitary = np.linalg.eigh(hermitian)
    evals = np.asarray(np.real_if_close(evals), dtype=float)
    masses = np.sqrt(np.maximum(evals, 0.0))
    dm = {
        "21": float(evals[1] - evals[0]),
        "31": float(evals[2] - evals[0]),
        "32": float(evals[2] - evals[1]),
    }
    ratio = dm["21"] / dm["32"]
    return masses, _standardize_columns(unitary), dm, ratio


def build_payload(
    *,
    repair: dict[str, Any],
    theorem: dict[str, Any],
    normalizer: dict[str, Any],
    scalar: dict[str, Any],
    compare: dict[str, Any],
    absolute_scaffold: dict[str, Any],
    correction_audit: dict[str, Any] | None,
) -> dict[str, Any]:
    q = {key: float(val) for key, val in normalizer["q_e"].items()}
    qbar = {key: float(val) for key, val in normalizer["qbar_e"].items()}
    q_mean = float(normalizer["q_mean"])
    p = float(theorem["live_inputs"]["p_nu"])
    chi = float(theorem["live_inputs"]["chi_nu"])
    psi = {key: float(val) for key, val in repair["selector_phases_absolute"].items()}
    phase = {key: -float(val) for key, val in psi.items()}
    q_scale = q_mean**p

    weights_raw = {key: float(val) ** p for key, val in q.items()}
    weights_bar = {key: float(val) ** p for key, val in qbar.items()}

    cycle_raw = _cycle_matrix(weights=weights_raw, chi=chi, phase=phase)
    cycle_bar = _cycle_matrix(weights=weights_bar, chi=chi, phase=phase)

    masses_raw, unitary_raw, dm_raw, ratio_raw = _spectral_data(cycle_raw)
    masses_bar, unitary_bar, dm_bar, ratio_bar = _spectral_data(cycle_bar)

    # centered scalar evaluated at the weighted-cycle selector point
    mu_nu = float(scalar["mu_nu"])
    center = scalar["selector_point_absolute"]
    u = float(psi["psi12"] - center["psi12"])
    v = float(psi["psi23"] - center["psi23"])
    w = float(psi["psi31"] - center["psi31"])
    current_centered_scalar = mu_nu * (
        3.0 - math.cos(u + v) - math.cos(u) - math.cos(v)
    )

    scale_orbit_checks = []
    for c in [0.5, 2.0, 10.0]:
        weights_c = {key: (c * float(q[key])) ** p for key in q}
        cycle_c = _cycle_matrix(weights=weights_c, chi=chi, phase=phase)
        _, unitary_c, dm_c, ratio_c = _spectral_data(cycle_c)
        # predicted scaling on the squared masses / splittings is c^(2p)
        predicted = c ** (2.0 * p)
        max_rel_dm_error = max(
            abs(dm_c[key] / (predicted * dm_raw[key]) - 1.0) for key in dm_raw
        )
        max_abs_unitary_abs_error = float(
            np.max(np.abs(np.abs(unitary_c) - np.abs(unitary_raw)))
        )
        scale_orbit_checks.append(
            {
                "common_q_rescaling": c,
                "expected_dm_scaling": predicted,
                "ratio_21_over_32": ratio_c,
                "max_relative_dm_scaling_error": float(max_rel_dm_error),
                "max_abs_difference_in_abs_unitary": max_abs_unitary_abs_error,
            }
        )

    lambda_samples = [
        {
            "name": "direct_m_star_attachment_diagnostic",
            "lambda_value": float(
                absolute_scaffold["current_no_go"]["direct_attachment_diagnostic"]["m_star_eV"]
            ),
        },
        {"name": "unit_representative", "lambda_value": 1.0},
        {
            "name": "compare_only_weighted_least_squares",
            "lambda_value": float(compare["fits"]["weighted_least_squares"]["lambda_nu"]),
        },
        {"name": "two_times_unit_representative", "lambda_value": 2.0},
    ]
    for item in lambda_samples:
        lam = float(item["lambda_value"])
        item["absolute_masses"] = [float(lam * x) for x in masses_raw]
        item["absolute_dm2"] = {key: float(lam**2 * val) for key, val in dm_raw.items()}
        item["fixed_stack_invariants"] = {
            "pmns_observables": dict(repair["pmns_observables"]),
            "ratio_21_over_32": ratio_raw,
            "current_centered_scalar": current_centered_scalar,
            "qbar_e": qbar,
        }

    compare_bridge_factor = float(compare["fits"]["weighted_least_squares"]["lambda_nu"]) / float(
        absolute_scaffold["current_no_go"]["direct_attachment_diagnostic"]["m_star_eV"]
    )
    reduced_proxy_object = (
        None
        if correction_audit is None
        else {
            "artifact": correction_audit.get("artifact"),
            **(correction_audit.get("emitted_proxy_route") or {}),
        }
    )
    reduced_remaining_object = (
        {
            "name": "one_positive_neutrino_bridge_correction_invariant",
            "symbol": "C_nu",
            "status": "conditionally_irreducible_on_declared_candidate_stack",
            "definition": None if correction_audit is None else (correction_audit.get("exact_target_scalar") or {}).get("definition"),
            "bridge_reconstruction": None
            if correction_audit is None
            else (correction_audit.get("exact_target_scalar") or {}).get("bridge_reconstruction"),
            "exact_residual_moduli_space": "R_{>0}",
            "equivalence_theorem": (
                "Because the proxy P_nu is internal to the declared candidate stack and strictly positive at the stored point, "
                "that conditional stack fixes B_nu if and only if it fixes C_nu := B_nu / P_nu."
            ),
            "must_break": "the remaining positive correction orbit above the internal emitted proxy P_nu",
            "compare_only_target": None
            if correction_audit is None
            else (correction_audit.get("current_compare_only_target") or {}).get("value"),
        }
        if correction_audit is not None
        else None
    )

    return {
        "artifact": "oph_neutrino_attachment_irreducibility_theorem",
        "generated_utc": _timestamp(),
        "status": "conditional_algebraic_no_go_on_rejected_candidate_stack",
        "proof_grade": "exact_factorization_plus_one_orbit_underdetermination_conditional_on_declared_candidate",
        "public_surface_candidate_allowed": False,
        "prediction_promotion_allowed": False,
        "theorem": {
            "name": "weighted_cycle_attachment_irreducibility_after_full_attached_stack",
            "statement": (
                "With the declared normalizer, weighted-cycle candidate law, and centered-edge-norm scalar stack fixed, "
                "the neutrino branch factors exactly through q_e = q_mean * qbar_e and retains one free positive amplitude orbit. "
                "Hence no theorem-grade absolute attachment law can be derived from the current attached stack alone; "
                "one positive bridge invariant remains irreducible."
            ),
            "exact_factorization": [
                "q_e = q_mean * qbar_e",
                "w_e = q_e^p = q_mean^p * qbar_e^p",
                "C(q,psi) = q_mean^p * C(qbar,psi)",
                "mhat_i(q,psi) = q_mean^p * mtilde_i(qbar,psi)",
                "Delta_hat_ij(q,psi) = q_mean^(2p) * Deltatilde_ij(qbar,psi)",
                "m_i = lambda_nu * mhat_i = A_nu * mtilde_i, with A_nu := lambda_nu * q_mean^p",
                "Delta m^2_ij = lambda_nu^2 * Delta_hat_ij = A_nu^2 * Deltatilde_ij",
            ],
            "sharpened_conclusion": (
                "The collapse alternative F_nu = F_nu(qbar) is not derivable from the present attached stack, "
                "because the entire current stack is constant on the exact one-parameter family A_nu in R_{>0}."
            ),
            "reduced_exact_factorization": (
                None
                if correction_audit is None
                else [
                    (correction_audit.get("exact_target_scalar") or {}).get("bridge_reconstruction"),
                    "P_nu is a positive scalar internal to the declared candidate stack.",
                    "Therefore that conditional stack fixes B_nu if and only if it fixes C_nu.",
                ]
            ),
            "reduced_sharpened_conclusion": (
                None
                if correction_audit is None
                else "After factoring out the internal positive proxy P_nu, one positive reduced bridge correction invariant C_nu remains conditionally irreducible on the declared candidate stack."
            ),
        },
        "inputs_used": {
            "repair_artifact": repair["artifact"],
            "theorem_artifact": theorem["artifact"],
            "normalizer_artifact": normalizer["artifact"],
            "scalar_artifact": scalar["artifact"],
            "compare_artifact": compare["artifact"],
            "absolute_scaffold_artifact": absolute_scaffold["artifact"],
        },
        "current_attached_stack_summary": {
            "q_mean": q_mean,
            "p_nu": p,
            "chi_nu": chi,
            "q_mean_to_p": q_scale,
            "qbar_e": qbar,
            "qbar_weights_p": weights_bar,
            "centered_phase_residuals": {
                "u": u,
                "v": v,
                "w": w,
                "sum": float(u + v + w),
            },
            "current_centered_scalar": current_centered_scalar,
            "current_centered_scalar_bound": scalar["bounded_scalar_range_if_closed"],
            "compare_only_bridge_factor_required_by_weighted_fit": compare_bridge_factor,
        },
        "internal_positive_proxy_object": reduced_proxy_object,
        "factorization_validation": {
            "raw_vs_factored_cycle_matrix_max_abs_error": float(
                np.max(np.abs(cycle_raw - q_scale * cycle_bar))
            ),
            "raw_vs_factored_mass_max_abs_error": float(
                np.max(np.abs(masses_raw - q_scale * masses_bar))
            ),
            "raw_vs_factored_dm_max_abs_error": max(
                abs(dm_raw[key] - (q_scale**2) * dm_bar[key]) for key in dm_raw
            ),
            "raw_ratio_21_over_32": ratio_raw,
            "factored_ratio_21_over_32": ratio_bar,
            "raw_pmns_abs": np.abs(unitary_raw).tolist(),
            "factored_pmns_abs": np.abs(unitary_bar).tolist(),
            "raw_vs_factored_pmns_abs_max_abs_error": float(
                np.max(np.abs(np.abs(unitary_raw) - np.abs(unitary_bar)))
            ),
            "q_rescaling_orbit_checks": scale_orbit_checks,
        },
        "qbar_only_normal_form": {
            "mass_coefficients": [float(x) for x in masses_bar],
            "dm2_coefficients": dm_bar,
            "ratio_21_over_32": ratio_bar,
        },
        "exact_extension_family": {
            "parameter": "A_nu in R_{>0}",
            "family_law": {
                "masses": ["m_i = A_nu * mtilde_i(qbar,psi)"],
                "splittings": ["Delta m^2_ij = A_nu^2 * Deltatilde_ij(qbar,psi)"],
            },
            "sample_extensions": lambda_samples,
        },
        "remaining_object": {
            "name": "one_positive_neutrino_attachment_bridge_invariant",
            "status": "conditionally_irreducible_on_declared_candidate_stack",
            "equivalent_parameterizations": [
                "I_nu above the attached stack in lambda_nu = m_star * F_nu(qbar, I_nu)",
                "A_nu = lambda_nu * q_mean^p",
            ],
            "must_break": "the current positive common-homogeneity between the D10 amplitude anchor and the weighted-cycle normal form",
        },
        "reduced_remaining_object": reduced_remaining_object,
        "notes": [
            "This result is exact conditional algebra and does not promote the rejected weighted-cycle matrix or compare-only neutrino masses.",
            "It sharpens the frontier by proving that the present attached stack itself cannot collapse the remaining one-dimensional amplitude orbit.",
            "Because the residual-amplitude proxy P_nu is already internal to the current stack, the same irreducibility transfers exactly to the reduced correction invariant C_nu = B_nu / P_nu.",
            "Any supported closure must adjoin one new positive non-homogeneous bridge invariant, or a new theorem external to the current attached stack that fixes the same parameter exactly.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prove irreducibility of the remaining neutrino attachment scalar.")
    parser.add_argument("--repair", type=Path, default=REPAIR_JSON)
    parser.add_argument("--theorem", type=Path, default=THEOREM_JSON)
    parser.add_argument("--normalizer", type=Path, default=NORMALIZER_JSON)
    parser.add_argument("--scalar", type=Path, default=SCALAR_JSON)
    parser.add_argument("--compare", type=Path, default=COMPARE_JSON)
    parser.add_argument("--absolute-scaffold", type=Path, default=ABSOLUTE_SCAFFOLD_JSON)
    parser.add_argument("--correction-audit", type=Path, default=CORRECTION_AUDIT_JSON)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    payload = build_payload(
        repair=_load_json(args.repair),
        theorem=_load_json(args.theorem),
        normalizer=_load_json(args.normalizer),
        scalar=_load_json(args.scalar),
        compare=_load_json(args.compare),
        absolute_scaffold=_load_json(args.absolute_scaffold),
        correction_audit=_load_json(args.correction_audit) if args.correction_audit.exists() else None,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
