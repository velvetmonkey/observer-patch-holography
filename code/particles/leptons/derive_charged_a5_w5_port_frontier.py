#!/usr/bin/env python3
"""Derive the exact A5 representation frontier of the 12/24 lepton route.

The twelve icosahedral ports carry the A5 vertex permutation representation

    R^12 = 1 + 3 + 3' + 5.

The centered first moment sees the geometric 3, while the traceless second
moment sees exactly the 5.  Consequently a charged-family quadrupole requires
a source-emitted W5 record.  Uniform twelve-port data and the count-only
write/check orientation bit contain only A5 singlets and have zero W5 image.

This is a source-only representation theorem.  It reads no charged mass.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from derive_charged_family_non_singlet_port_attachment import icosahedron_vertices


ROOT = Path(__file__).resolve().parents[2]
SCREEN = (
    ROOT / "particles" / "hierarchy" / "certificates"
    / "R_screen_sieve_icosahedral_certificate.json"
)
ROUND_COUNT = (
    ROOT / "particles" / "hierarchy" / "certificates"
    / "R_m_rep_24_certificate.json"
)
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "leptons"
    / "charged_a5_w5_port_frontier.json"
)


A5_CLASS_LABELS = ("1A", "2A", "3A", "5A", "5B")
A5_CLASS_SIZES = (1, 15, 20, 12, 12)


def a5_characters() -> dict[str, tuple[float, ...]]:
    """Real A5 character table in the class order above."""

    phi = (1.0 + math.sqrt(5.0)) / 2.0
    phi_bar = (1.0 - math.sqrt(5.0)) / 2.0
    return {
        "1": (1.0, 1.0, 1.0, 1.0, 1.0),
        "3": (3.0, -1.0, 0.0, phi, phi_bar),
        "3_prime": (3.0, -1.0, 0.0, phi_bar, phi),
        "4": (4.0, 0.0, 1.0, -1.0, -1.0),
        "5": (5.0, 1.0, -1.0, 0.0, 0.0),
    }


def character_inner_product(left: Iterable[float], right: Iterable[float]) -> float:
    return sum(
        size * float(a) * float(b)
        for size, a, b in zip(A5_CLASS_SIZES, left, right, strict=True)
    ) / 60.0


def vertex_representation_multiplicities() -> dict[str, int]:
    # An order-five rotation fixes the two vertices on its axis.  The order-two
    # and order-three axes pass through edge and face centers, respectively.
    vertex_character = (12.0, 0.0, 0.0, 2.0, 2.0)
    return {
        name: int(round(character_inner_product(vertex_character, character)))
        for name, character in a5_characters().items()
    }


def _quadrupole_coordinates(point: np.ndarray) -> np.ndarray:
    """Five independent coordinates of pp^T-I/3."""

    tensor = np.outer(point, point) - np.eye(3) / 3.0
    return np.asarray(
        [tensor[0, 0], tensor[1, 1], tensor[0, 1], tensor[0, 2], tensor[1, 2]],
        dtype=float,
    )


def w5_projector_checks() -> dict[str, Any]:
    """Verify the exact antipodal W5 projector and moment normalizations."""

    points = icosahedron_vertices()
    count = len(points)
    antipode = np.zeros((count, count), dtype=float)
    for index, point in enumerate(points):
        partner = int(np.argmin(np.linalg.norm(points + point, axis=1)))
        antipode[partner, index] = 1.0

    identity = np.eye(count)
    singlet = np.ones((count, count), dtype=float) / count
    p5 = (identity + antipode) / 2.0 - singlet

    # Full vectorization uses the Frobenius inner product on Sym^2_0(R^3).
    quadrupole_map = np.stack(
        [(np.outer(point, point) - np.eye(3) / 3.0).reshape(-1) for point in points],
        axis=1,
    )
    q_star_q = quadrupole_map.T @ quadrupole_map

    first_map = points.T
    m_star_m = first_map.T @ first_map
    p3 = m_star_m / 4.0

    odd_test = points[:, 0]
    even_test = points[:, 0] ** 2 - np.mean(points[:, 0] ** 2)
    return {
        "antipode_is_involution_residual": float(np.linalg.norm(antipode @ antipode - identity)),
        "P5_rank": int(np.linalg.matrix_rank(p5)),
        "P5_projector_residual": float(np.linalg.norm(p5 @ p5 - p5)),
        "Q_star_Q_minus_8_over_5_P5_norm": float(np.linalg.norm(q_star_q - (8.0 / 5.0) * p5)),
        "P3_rank": int(np.linalg.matrix_rank(p3)),
        "P3_projector_residual": float(np.linalg.norm(p3 @ p3 - p3)),
        "first_star_first_minus_4P3_norm": float(np.linalg.norm(m_star_m - 4.0 * p3)),
        "antipodal_odd_nonuniform_Q_norm": float(np.linalg.norm(quadrupole_map @ odd_test)),
        "example_even_W5_norm": float(np.linalg.norm(p5 @ even_test)),
        "example_even_quadrupole_norm": float(np.linalg.norm(quadrupole_map @ even_test)),
    }


def moment_map_checks() -> dict[str, Any]:
    points = icosahedron_vertices()
    first_map = points.T
    quadrupole_map = np.stack([_quadrupole_coordinates(point) for point in points], axis=1)
    invariant_row = np.ones((1, 12), dtype=float)
    joint_map = np.vstack((invariant_row, first_map, quadrupole_map))

    uniform = np.ones(12, dtype=float)
    oriented_even = np.concatenate((uniform, uniform))
    oriented_odd = np.concatenate((uniform, -uniform))

    # A count-only oriented register has the form 1_12 tensor (a,b).  Summing
    # or differencing orientations still returns a uniform twelve-port vector.
    even_contraction = oriented_even[:12] + oriented_even[12:]
    odd_contraction = oriented_odd[:12] - oriented_odd[12:]

    return {
        "first_moment_map_rank": int(np.linalg.matrix_rank(first_map)),
        "quadrupole_map_rank": int(np.linalg.matrix_rank(quadrupole_map)),
        "singlet_plus_first_plus_quadrupole_rank": int(np.linalg.matrix_rank(joint_map)),
        "unseen_complement_dimension": 12 - int(np.linalg.matrix_rank(joint_map)),
        "uniform_first_moment_norm": float(np.linalg.norm(first_map @ uniform)),
        "uniform_quadrupole_norm": float(np.linalg.norm(quadrupole_map @ uniform)),
        "orientation_even_quadrupole_norm": float(np.linalg.norm(quadrupole_map @ even_contraction)),
        "orientation_odd_quadrupole_norm": float(np.linalg.norm(quadrupole_map @ odd_contraction)),
    }


def traceless_cubic_discriminant(eigenvalues: Iterable[float]) -> float:
    values = np.asarray(tuple(float(value) for value in eigenvalues), dtype=float)
    if values.shape != (3,) or not math.isclose(float(np.sum(values)), 0.0, abs_tol=1.0e-12):
        raise ValueError("expected three traceless eigenvalues")
    trace_q2 = float(values @ values)
    det_q = float(np.prod(values))
    return 0.5 * trace_q2**3 - 27.0 * det_q**2


def build_artifact(screen: dict[str, Any], round_count: dict[str, Any]) -> dict[str, Any]:
    port_count = int(screen["orbit_stabilizer"]["orbit_size"])
    oriented_count = int(round_count["result"]["m_rep"])
    if port_count != 12 or oriented_count != 24:
        raise ValueError("the A5/W5 frontier requires the declared 12/24 branch")

    multiplicities = vertex_representation_multiplicities()
    checks = moment_map_checks()
    projector_checks = w5_projector_checks()
    decomposition_closed = multiplicities == {
        "1": 1,
        "3": 1,
        "3_prime": 1,
        "4": 0,
        "5": 1,
    }
    ranks_closed = (
        checks["first_moment_map_rank"] == 3
        and checks["quadrupole_map_rank"] == 5
        and checks["singlet_plus_first_plus_quadrupole_rank"] == 9
        and checks["unseen_complement_dimension"] == 3
    )
    current_w5_zero = all(
        checks[key] < 1.0e-12
        for key in (
            "uniform_quadrupole_norm",
            "orientation_even_quadrupole_norm",
            "orientation_odd_quadrupole_norm",
        )
    )
    projector_closed = (
        projector_checks["P5_rank"] == 5
        and projector_checks["P3_rank"] == 3
        and projector_checks["P5_projector_residual"] < 1.0e-12
        and projector_checks["Q_star_Q_minus_8_over_5_P5_norm"] < 1.0e-12
        and projector_checks["antipodal_odd_nonuniform_Q_norm"] < 1.0e-12
        and projector_checks["example_even_W5_norm"] > 1.0e-6
        and projector_checks["example_even_quadrupole_norm"] > 1.0e-6
    )

    return {
        "artifact": "oph_charged_a5_w5_port_frontier",
        "status": "CLOSED_A5_REPRESENTATION_FRONTIER_W5_REQUIRED_AND_ABSENT",
        "source_only": True,
        "charged_reference_data_consumed": False,
        "public_charged_mass_promotion_allowed": False,
        "declared_branch": {
            "port_orbit": "A5/C5",
            "port_count": port_count,
            "oriented_register_count": oriented_count,
            "current_port_record": "twelve equal unit curvature defects",
            "current_oriented_record": "count-only reversible write/check bookkeeping",
        },
        "representation_theorem": {
            "class_order": list(A5_CLASS_LABELS),
            "class_sizes": list(A5_CLASS_SIZES),
            "vertex_permutation_character": [12, 0, 0, 2, 2],
            "multiplicities": multiplicities,
            "decomposition": "R^12 = W1 direct_sum W3 direct_sum W3_prime direct_sum W5",
            "decomposition_check": decomposition_closed,
            "first_moment": (
                "The A5-equivariant map w -> sum_i w_i p_i has rank 3 and sees "
                "the geometric W3 summand."
            ),
            "quadrupole": (
                "The A5-equivariant map w -> sum_i w_i(p_i p_i^T-I/3) has rank 5. "
                "Since Sym^2_0(R^3) is the irreducible W5, this map sees exactly W5."
            ),
            "antipodal_split": "W_even=W1+W5 and W_odd=W3+W3_prime",
            "exact_W5_projector": "P5=(I+A_antipode)/2-(1/12)11^T",
            "exact_factorization": [
                "Q=Q P5",
                "ker(Q)=W1+W3+W3_prime",
                "Q^* Q=(8/5)P5",
                "||Q(w)||_F^2=(8/5)||P5 w||^2",
                "(P5 w)_i=(5/8) p_i^T Q(w) p_i",
            ],
            "nonuniformity_boundary": (
                "A nonuniform record is not sufficient: antipodal-odd nonuniform records lie "
                "in W3+W3_prime and still have zero quadrupole. The six antipodal pair sums "
                "must have a nonzero centered component."
            ),
            "joint_kernel": (
                "The singlet, first moment, and quadrupole have joint rank 1+3+5=9; "
                "the remaining three-dimensional kernel is W3_prime."
            ),
            "checks": checks,
            "projector_checks": projector_checks,
        },
        "orientation_doubling_theorem": {
            "decomposition": (
                "R^24 = R^12 tensor (orientation-even direct_sum orientation-odd); "
                "as an A5 module it contains two copies of 1+3+3_prime+5."
            ),
            "count_only_subspace": "W1 tensor R^2_orientation",
            "conclusion": (
                "The orientation sign is an A5 singlet.  Orientation doubling can carry a "
                "W5 only if the source already emits a port-resolved non-singlet pattern. "
                "The present total count and write/check sign do not do so."
            ),
            "current_W5_projection_zero": current_w5_zero,
            "semantic_map_boundary": (
                "The numerical equality 12=8+3+1 does not itself construct an "
                "A5-equivariant bijection between geometric ports and product-adjoint gauge "
                "channels. Any use of gauge-slot histories as port records requires that map "
                "as an additional source receipt."
            ),
        },
        "simple_spectrum_gate": {
            "quadrupole_properties": "Q=Q^T and tr(Q)=0",
            "characteristic_polynomial": "lambda^3-(tr(Q^2)/2)lambda-det(Q)",
            "discriminant": "Delta_Q=(tr(Q^2)^3)/2-27*det(Q)^2",
            "equivalent_discriminant": "Delta_Q=(tr(Q^2)^3)/2-3*(tr(Q^3))^2",
            "vandermonde_form": "Delta_Q=product_{a<b}(lambda_a-lambda_b)^2",
            "criterion": "Delta_Q>0 iff the three real eigenvalues are distinct",
            "simple_example_check": traceless_cubic_discriminant((-2.0, -0.5, 2.5)),
            "repeated_example_check": traceless_cubic_discriminant((-1.0, -1.0, 2.0)),
            "shape_readout": (
                "For Delta_Q>0, the ordered eigenvalues have two adjacent gaps.  These "
                "span the two-dimensional centered three-family shape plane."
            ),
            "gap_reconstruction": [
                "lambda_1=-(2*d1+d2)/3",
                "lambda_2=(d1-d2)/3",
                "lambda_3=(d1+2*d2)/3",
            ],
        },
        "no_natural_nonzero_section": {
            "statement": (
                "An A5-equivariant deterministic rule fed only A5-invariant source data must "
                "land in the fixed subspace W5^A5={0}.  Therefore the homogeneous current "
                "branch cannot canonically emit the required nonzero W5 record."
            ),
            "implication": (
                "A nonzero record requires a source non-singlet, an observer-conditioned "
                "branch, or a separately proved spontaneous-symmetry-breaking selector."
            ),
        },
        "minimal_positive_extension": {
            "source_shape_object": (
                "a quotient-visible, refinement-stable w5 in W5 with Delta_Q>0, frozen "
                "before charged-mass comparison"
            ),
            "physical_attachment": (
                "a source-defined A5 action on the physical charged generation space and "
                "an equivariant intertwiner J: R^3_geom -> F_ch, or a direct physical "
                "charged response operator that bypasses this geometric attachment"
            ),
            "readout_law": (
                "a theorem mapping the two ordered quadrupole gaps to the two centered log "
                "singular-value gaps of the physical charged response"
            ),
            "normalization_and_sign": (
                "A5 equivariance fixes a W5-to-Sym^2_0(F_ch) intertwiner only up to an "
                "overall scale and sign; both must be fixed by source dynamics."
            ),
            "still_independent": [
                "a normalized determinant-line section for the common charged scale",
                "a declared running-mass coordinate and RG/threshold/pole map",
            ],
        },
        "existing_data_verdict": (
            "The declared equal defect vector has w5=0.  The 24-slot count-only register "
            "adds no port-resolved W5 datum.  Cardinalities such as 12, 24, or 12+2 do not "
            "by themselves define a charged determinant character or a power of Z6."
        ),
        "why_12_24_does_not_derive_the_stage5_determinant": {
            "derived_six_scope": (
                "The hierarchy lane derives 6=m_rep/beta_EW=24/4 inside its electroweak "
                "bridge normalization. No current theorem turns that ratio into one Yukawa "
                "suppression factor per charged defect."
            ),
            "fourteen_is_not_the_register_dimension": (
                "The oriented register is the tensor-product set P12 x {+,-}, whose "
                "cardinality is 24. The number 14=12+2 is the dimension of a different "
                "direct-sum construction; no such charged determinant object is declared."
            ),
            "orientation_normalization_ambiguous": (
                "Two orientations could contribute a normalized singlet factor 1, an "
                "incoherent multiplicity 2, or a coherent unnormalized amplitude sqrt(2). "
                "The count alone selects none of these readout conventions."
            ),
            "z6_projector_check": {
                "normalized_trivial_character_average": sum([1.0] * 6) / 6.0,
                "conclusion": (
                    "The normalized Z6 group average acts as 1 on the invariant channel, "
                    "not as a universal 1/6 suppression. A dynamical transition or defect "
                    "amplitude theorem would be additional input."
                ),
            },
            "stage5_boundary": (
                "Therefore sqrt(2)/6^14 is not a consequence of the present 12/24 "
                "representation theorem. Interpreting sqrt(2), 6, and 14 that way would be "
                "a new determinant ansatz unless the missing amplitude and attachment laws "
                "are independently proved."
            ),
        },
        "claim_boundary": (
            "This theorem identifies the unique port-representation carrier capable of "
            "supplying both family-shape coordinates.  It does not assert that such a W5 "
            "record, its physical charged-family intertwiner, or its determinant scale is "
            "present in current OPH."
        ),
        "checks_pass": decomposition_closed and ranks_closed and projector_closed and current_w5_zero,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screen", type=Path, default=SCREEN)
    parser.add_argument("--round-count", type=Path, default=ROUND_COUNT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build_artifact(
        json.loads(args.screen.read_text(encoding="utf-8")),
        json.loads(args.round_count.read_text(encoding="utf-8")),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "checks_pass": artifact["checks_pass"]}, indent=2))
    return 0 if artifact["checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
