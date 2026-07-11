#!/usr/bin/env python3
"""Emit the Borel-Weil one-Higgs carrier bridge artifact.

Chain role: identify the OPH one-Higgs slot with the minimal nontrivial
holomorphic section carrier on the local electroweak screen chart. This is a
representation and symmetry-breaking bridge only; the Higgs mass, quartic,
weak scale, and hierarchy/naturality closure remain in the D10/D11 and
hierarchy lanes.
"""

from __future__ import annotations

import argparse
import cmath
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "particles" / "runs" / "calibration" / "bw_higgs_carrier_bridge.json"
DEFAULT_ACCEPTANCE_PHASE = 0.731
TOLERANCE = 1e-12


def _scale(vector: tuple[complex, ...], scalar: complex) -> tuple[complex, ...]:
    return tuple(scalar * entry for entry in vector)


def _same_vector(left: tuple[complex, ...], right: tuple[complex, ...]) -> bool:
    return all(abs(lhs - rhs) <= TOLERANCE for lhs, rhs in zip(left, right, strict=True))


def _same_projective_ray(left: tuple[complex, ...], right: tuple[complex, ...]) -> bool:
    pivot = next((index for index, entry in enumerate(right) if abs(entry) > TOLERANCE), None)
    if pivot is None or abs(left[pivot]) <= TOLERANCE:
        return False
    scalar = left[pivot] / right[pivot]
    return all(
        abs(lhs - scalar * rhs) <= TOLERANCE
        for lhs, rhs in zip(left, right, strict=True)
    )


def _group_action_acceptance(beta: float) -> dict:
    """Exercise the ray and vector actions at an arbitrary nontrivial angle."""

    phi0 = (0.0j, 1.0 + 0.0j)
    hypercharge_phase = cmath.exp(0.5j * beta)
    lower_t3_phase = cmath.exp(-0.5j * beta)
    hypercharge_image = _scale(phi0, hypercharge_phase)
    t3_image = _scale(phi0, lower_t3_phase)
    diagonal_q_image = _scale(hypercharge_image, lower_t3_phase)
    return {
        "test_angle_beta_radians": beta,
        "hypercharge_phase_is_nontrivial": abs(hypercharge_phase - 1.0) > TOLERANCE,
        "pure_hypercharge_fixes_projective_ray": _same_projective_ray(hypercharge_image, phi0),
        "pure_hypercharge_fixes_vacuum_vector": _same_vector(hypercharge_image, phi0),
        "pure_T3_fixes_projective_ray": _same_projective_ray(t3_image, phi0),
        "pure_T3_fixes_vacuum_vector": _same_vector(t3_image, phi0),
        "diagonal_Q_fixes_vacuum_vector": _same_vector(diagonal_q_image, phi0),
    }


def build_artifact(acceptance_phase: float = DEFAULT_ACCEPTANCE_PHASE) -> dict:
    section_degree = 1
    complex_dim = section_degree + 1
    real_dof = 2 * complex_dim
    group_dim_su2_u1 = 4
    projective_stabilizer_dim = 2
    vector_stabilizer_dim = 1
    projective_orbit_dim = group_dim_su2_u1 - projective_stabilizer_dim
    goldstone_count = group_dim_su2_u1 - vector_stabilizer_dim
    radial_modes = real_dof - goldstone_count
    t3_lower = -0.5
    hypercharge = 0.5
    neutral_component_charge = t3_lower + hypercharge
    group_action_acceptance = _group_action_acceptance(acceptance_phase)
    receipt = bool(
        section_degree == 1
        and complex_dim == 2
        and real_dof == 4
        and projective_stabilizer_dim == 2
        and projective_orbit_dim == 2
        and vector_stabilizer_dim == 1
        and goldstone_count == 3
        and radial_modes == 1
        and neutral_component_charge == 0.0
        and group_action_acceptance["hypercharge_phase_is_nontrivial"]
        and group_action_acceptance["pure_hypercharge_fixes_projective_ray"]
        and not group_action_acceptance["pure_hypercharge_fixes_vacuum_vector"]
        and group_action_acceptance["pure_T3_fixes_projective_ray"]
        and not group_action_acceptance["pure_T3_fixes_vacuum_vector"]
        and group_action_acceptance["diagonal_Q_fixes_vacuum_vector"]
    )
    return {
        "artifact": "oph_bw_higgs_carrier_bridge",
        "theorem_id": "BorelWeilHiggsCarrierBridge",
        "proof_status": "closed_carrier_representation_bridge",
        "BOREL_WEIL_HIGGS_CARRIER_RECEIPT": receipt,
        "claim_tier": "carrier_representation_bridge",
        "carrier": {
            "screen_chart": "C_EW ~= CP1",
            "line_bundle": "O(1)",
            "section_space": "H^0(C_EW,O(1))",
            "identification": "H_OPH ~= C^2",
            "section_degree_n": section_degree,
            "complex_dimension": complex_dim,
            "real_degrees_of_freedom": real_dof,
        },
        "representation": {
            "su2_L_representation": "fundamental_doublet",
            "su2_L_dimension": complex_dim,
            "lorentz_role": "internal_scalar_0_form",
            "hypercharge_normalization": "OPH_Z6_plus_neutral_vev",
            "T3_lower_component": t3_lower,
            "Y_H": hypercharge,
            "Q_phi0": neutral_component_charge,
        },
        "symmetry_breaking_geometry": {
            "integer_hypercharge_normalization": "q = 6Y, q_H = 3",
            "cover_action": "(g,z).phi = z^3 g phi",
            "carrier_projective_space": "P(H_OPH) ~= CP1",
            "projective_ray_stabilizer_on_cover": "{(diag(a,a^-1),z): a,z in U(1)}",
            "projective_ray_stabilizer": "(U(1)_T3 x U(1)_Y)/finite_center",
            "projective_stabilizer_dimension": projective_stabilizer_dim,
            "projective_orbit_dimension": projective_orbit_dim,
            "projectivization_forgets_scalar_hypercharge_phase": True,
            "nonzero_vacuum_vector": "phi0 = (0,v/sqrt(2)), v != 0",
            "vector_stabilizer_on_cover": "{(diag(z^3,z^-3),z): z in U(1)}",
            "vector_stabilizer": "U(1)_Q",
            "vector_stabilizer_generator": "Q = T3 + Y",
            "vector_stabilizer_dimension": vector_stabilizer_dim,
            "broken_generator_count": goldstone_count,
            "goldstone_count": goldstone_count,
            "radial_higgs_modes": radial_modes,
            "dof_split": "4 = 3 + 1",
        },
        "group_action_acceptance": group_action_acceptance,
        "minimality": {
            "n_0": "H^0(CP1,O(0)) is a singlet and fails weak-doublet breaking",
            "n_1": "H^0(CP1,O(1)) is the first nontrivial section space and gives C^2",
            "n_ge_2": "higher O(n) produce larger SU(2) multiplets and fail one-Higgs minimality",
        },
        "explicit_nonclaims": [
            "Higgs mass m_H",
            "Higgs quartic lambda",
            "weak scale v",
            "Coleman-Weinberg breaking",
            "replacement of the epsilon_H=0 hierarchy/naturality lane",
        ],
        "claim_boundary": (
            "This artifact identifies the OPH one-Higgs carrier as the minimal "
            "Borel-Weil section object H^0(CP1,O(1)). It supplies representation, "
            "hypercharge-convention, projective-ray geometry, and nonzero-vector "
            "stabilizer geometry only. Projectivization forgets the scalar hypercharge "
            "phase; only the nonzero vacuum vector has stabilizer U(1)_Q."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the Borel-Weil OPH one-Higgs carrier bridge artifact.")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output JSON path.")
    parser.add_argument(
        "--acceptance-phase",
        type=float,
        default=DEFAULT_ACCEPTANCE_PHASE,
        help="Nontrivial hypercharge angle used for the ray-versus-vector acceptance check.",
    )
    args = parser.parse_args(argv)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_artifact(args.acceptance_phase), indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
