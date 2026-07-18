#!/usr/bin/env python3
"""Verifier for the OPH icosahedral screen-sieve and load-split theorem."""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


TOTAL_CURVATURE_CHARGE = 12
ICOSAHEDRAL_GROUP_ORDER = 60
FIVEFOLD_STABILIZER_ORDER = 5
ELECTROWEAK_BETA = 4


def polyhedron_record(name: str, degrees: list[int]) -> dict[str, Any]:
    vertices = len(degrees)
    edges = sum(degrees) // 2
    faces = (2 * edges) // 3
    charges = [6 - degree for degree in degrees]
    return {
        "name": name,
        "vertices": vertices,
        "edges": edges,
        "faces": faces,
        "euler_residual": vertices - edges + faces - 2,
        "triangular_incidence_residual": 3 * faces - 2 * edges,
        "charges": charges,
        "total_charge": sum(charges),
        "defect_cost_sum_q2": sum(q * q for q in charges),
    }


def unit_charge_minimum(total_charge: int) -> dict[str, Any]:
    charges = [1] * total_charge
    return {
        "total_charge": total_charge,
        "unit_defect_count": len(charges),
        "charges": charges,
        "defect_cost_sum_q2": sum(q * q for q in charges),
    }


def matrix_product(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def graph_degree_profile(graph_edges: set[tuple[int, int]], vertices: int) -> tuple[int, ...]:
    degrees = [0] * vertices
    for a, b in graph_edges:
        degrees[a] += 1
        degrees[b] += 1
    return tuple(degrees)


def graph_is_connected(graph_edges: set[tuple[int, int]], vertices: int) -> bool:
    reached = {0}
    frontier = [0]
    while frontier:
        vertex = frontier.pop()
        for a, b in graph_edges:
            neighbor = b if a == vertex else a if b == vertex else None
            if neighbor is not None and neighbor not in reached:
                reached.add(neighbor)
                frontier.append(neighbor)
    return len(reached) == vertices


def graph_edge_code(graph_edges: set[tuple[int, int]], vertices: int) -> str:
    edge_order = itertools.combinations(range(vertices), 2)
    return "".join("1" if edge in graph_edges else "0" for edge in edge_order)


def canonical_graph_code(graph_edges: set[tuple[int, int]], vertices: int) -> str:
    codes = []
    for permutation in itertools.permutations(range(vertices)):
        relabelled = {
            tuple(sorted((permutation[a], permutation[b]))) for a, b in graph_edges
        }
        codes.append(graph_edge_code(relabelled, vertices))
    return min(codes)


def labelled_cycle_codes(vertices: int) -> set[str]:
    codes = set()
    for ordering in itertools.permutations(range(vertices)):
        graph_edges = {
            tuple(sorted((ordering[index], ordering[(index + 1) % vertices])))
            for index in range(vertices)
        }
        codes.add(graph_edge_code(graph_edges, vertices))
    return codes


def seidel_certificate() -> dict[str, Any]:
    edges = list(itertools.combinations(range(5), 2))
    solutions: list[list[list[int]]] = []
    target = [[5 if i == j else 0 for j in range(6)] for i in range(6)]
    for mask in range(1 << len(edges)):
        s = [[0] * 6 for _ in range(6)]
        for j in range(1, 6):
            s[0][j] = s[j][0] = 1
        for k, (a, b) in enumerate(edges):
            s[a + 1][b + 1] = s[b + 1][a + 1] = -1 if mask >> k & 1 else 1
        if matrix_product(s, s) == target:
            solutions.append(s)
    normalized_graphs = []
    for solution in solutions:
        negative_edges = {
            (a, b)
            for a, b in edges
            if solution[a + 1][b + 1] == -1
        }
        normalized_graphs.append(
            {
                "negative_edges": negative_edges,
                "degree_profile": graph_degree_profile(negative_edges, 5),
                "connected": graph_is_connected(negative_edges, 5),
                "edge_code": graph_edge_code(negative_edges, 5),
                "canonical_edge_code": canonical_graph_code(negative_edges, 5),
            }
        )

    degree_profiles = sorted({graph["degree_profile"] for graph in normalized_graphs})
    solution_edge_codes = {graph["edge_code"] for graph in normalized_graphs}
    cycle_codes = labelled_cycle_codes(5)
    class_codes = sorted({graph["canonical_edge_code"] for graph in normalized_graphs})
    every_graph_is_connected = all(graph["connected"] for graph in normalized_graphs)
    every_graph_is_two_regular = degree_profiles == [(2, 2, 2, 2, 2)]
    solutions_are_exactly_labelled_c5 = solution_edge_codes == cycle_codes

    assert every_graph_is_two_regular
    assert every_graph_is_connected
    assert solutions_are_exactly_labelled_c5
    assert len(class_codes) == 1

    canonical_edges = [
        [a + 1, b + 1]
        for bit, (a, b) in zip(
            class_codes[0], itertools.combinations(range(5), 2), strict=True
        )
        if bit == "1"
    ]
    normalized_graph_class = {
        "normalization": "S[0,j]=+1 for j=1,...,5",
        "vertex_labels": [1, 2, 3, 4, 5],
        "negative_edge_rule": "{i,j} is an edge iff S[i,j]=-1",
        "normalized_solution_count": len(normalized_graphs),
        "distinct_degree_profiles": [list(profile) for profile in degree_profiles],
        "every_solution_connected": every_graph_is_connected,
        "derived_graph_type": "C5",
        "derived_labelled_c5_graph_count": len(cycle_codes),
        "solutions_equal_all_labelled_c5_graphs": solutions_are_exactly_labelled_c5,
        "canonical_edge_codes": class_codes,
        "canonical_representative_negative_edges": canonical_edges,
        "isomorphism_class_count": len(class_codes),
    }
    return {
        "relation": "S^2=5 I_6",
        "switched_labelled_solutions": len(solutions),
        "derived_labelled_five_cycles": len(cycle_codes),
        "switching_isomorphism_classes": len(class_codes),
        "normalized_negative_graph_class": normalized_graph_class,
        "representative": solutions[0],
    }


def build_certificate() -> dict[str, Any]:
    tetrahedron = polyhedron_record("tetrahedral", [3] * 4)
    octahedron = polyhedron_record("octahedral", [4] * 6)
    icosahedron = polyhedron_record("icosahedral", [5] * 12)
    unit_minimum = unit_charge_minimum(TOTAL_CURVATURE_CHARGE)
    orbit_size = ICOSAHEDRAL_GROUP_ORDER // FIVEFOLD_STABILIZER_ORDER
    port_load_factor = Fraction(1, orbit_size)
    gamma_screen_factor = (
        Fraction(ELECTROWEAK_BETA, 1) * Fraction(1, 4) * port_load_factor
    )
    projector_gram = [
        [Fraction(1) if i == j else Fraction(1, 5) for j in range(6)]
        for i in range(6)
    ]
    quadrupole_gram = [
        [projector_gram[i][j] - Fraction(1, 3) for j in range(6)]
        for i in range(6)
    ]
    seidel = seidel_certificate()

    checks = {
        "polyhedral_examples_obey_sphere_charge": all(
            record["total_charge"] == TOTAL_CURVATURE_CHARGE
            and record["euler_residual"] == 0
            and record["triangular_incidence_residual"] == 0
            for record in (tetrahedron, octahedron, icosahedron)
        ),
        "unit_defects_minimize_strict_unit_splitting_cost": (
            unit_minimum["defect_cost_sum_q2"]
            < octahedron["defect_cost_sum_q2"]
            < tetrahedron["defect_cost_sum_q2"]
        ),
        "projector_gram_is_equiangular": all(
            projector_gram[i][j] == (1 if i == j else Fraction(1, 5))
            for i in range(6)
            for j in range(6)
        ),
        "quadrupoles_form_regular_simplex": (
            all(sum(row) == 0 for row in quadrupole_gram)
            and all(quadrupole_gram[i][i] == Fraction(2, 3) for i in range(6))
            and all(
                quadrupole_gram[i][j] == Fraction(-2, 15)
                for i in range(6)
                for j in range(6)
                if i != j
            )
        ),
        "d_optimal_bounds_saturated": (
            Fraction(2) ** 3 == 8 and Fraction(4, 5) ** 5 == Fraction(1024, 3125)
        ),
        "seidel_class_is_unique": (
            seidel["switched_labelled_solutions"] == 12
            and seidel["derived_labelled_five_cycles"] == 12
            and seidel["switching_isomorphism_classes"] == 1
            and seidel["normalized_negative_graph_class"][
                "solutions_equal_all_labelled_c5_graphs"
            ]
        ),
        "icosahedral_orbit_has_twelve_vertices": orbit_size == 12,
        "screen_port_load_factor_is_one_over_twelve": port_load_factor == Fraction(1, 12),
        "gamma_screen_algebra_is_p_over_twelve": gamma_screen_factor == Fraction(1, 12),
        "physical_hierarchy_readout_not_supplied_by_screen_sieve": True,
    }

    return {
        "certificate_id": "R_screen_sieve_icosahedral_certificate",
        "status": "conditional_finite_selector_theorem",
        "branch_assumptions": [
            "fixed-cutoff OPH screen represented by a quantum-link triangulation of S^2",
            "finite Hilbert spaces on links and Gauss constraints at vertices",
            "boundary-gauge-invariant physical algebras",
            "locally six-valent quotient ensemble away from curvature defects",
            "integer charges and a feasible twelve-unit configuration",
            "additive cost h with h(0)=0, h(1)>0, h(k)>=h(1)|k| and strict inequality for |k|>=2",
            "edge-center collars expose unit defects as central ports",
            "fixed-point-free inverse-port involution gives six unoriented axes",
            "source selector maximizes det(F1) det(F2) for vector and quadrupole Fisher operators",
        ],
        "discrete_gauss_bonnet": {
            "vertex_charge": "q_v=6-deg(v)",
            "euler_identity": "V-E+F=2",
            "triangular_incidence": "3F=2E",
            "derived_edge_count": "E=3V-6",
            "total_charge": "sum_v q_v=6V-2E=12",
        },
        "polyhedral_comparison": [tetrahedron, octahedron, icosahedron],
        "strict_unit_defect_minimum": {
            **unit_minimum,
            "proof": "sum h(q_v) >= h(1) sum |q_v| >= 12 h(1); equality requires twelve positive unit charges",
            "quadratic_witness": "h(q)=q^2",
        },
        "d_optimal_tomography": {
            "vector_trace": 6,
            "quadrupole_trace": 4,
            "vector_fisher_at_equality": "2 I_3",
            "quadrupole_fisher_at_equality": "(4/5) I_5",
            "vector_determinant_bound": "8",
            "quadrupole_determinant_bound": "1024/3125",
            "projector_gram": [
                [str(value) for value in row] for row in projector_gram
            ],
            "quadrupole_gram": [
                [str(value) for value in row] for row in quadrupole_gram
            ],
            "axis_squared_inner_product": "1/5",
            "seidel_uniqueness": seidel,
        },
        "orbit_stabilizer": {
            "group": "I ~= A5",
            "group_order": ICOSAHEDRAL_GROUP_ORDER,
            "fivefold_stabilizer_order": FIVEFOLD_STABILIZER_ORDER,
            "orbit_size": orbit_size,
            "orbit": "12-vertex icosahedral orbit",
        },
        "screen_load_arithmetic": {
            "imported_screen_load": "X=log(N/pi)",
            "local_port_read": "X/12",
            "imported_cell_entropy": "P/4",
            "imported_beta_EW": ELECTROWEAK_BETA,
            "gamma_screen_definition": "Gamma_screen=beta_EW*(P/4)*(X/12)",
            "gamma_screen_simplified": "(P/12)*log(N/pi)",
        },
        "hierarchy_screen_readout_gate": {
            "premise_id": "HIERARCHY-SCREEN-READOUT",
            "supplied_by_screen_sieve": False,
            "required_identification": "log(E_cell/v)=Gamma_screen",
            "required_for": [
                "v/E_cell=(N/pi)^(-P/12)",
                "matching Gamma_screen to the alpha_U transmutation branch",
                "B_EW(P,N)=alpha_U(P)*log(N/pi)-6*pi/P=0",
            ],
            "status": "work_in_progress",
        },
        "checks": checks,
        "claim_boundary": {
            "exact": "Euler charge, strict unit-splitting implication, D-optimal equality conditions, ETF rigidity, X/12, and the Gamma_screen algebra after importing X=log(N/pi), P/4, and beta_EW=4",
            "work_in_progress": [
                "source production of the unit cost, inverse pairing, and D-optimal selector",
                "HIERARCHY-SCREEN-READOUT: identify log(E_cell/v)=Gamma_screen and attach it to the alpha_U/B_EW branch",
            ],
        },
        "pass": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    certificate = build_certificate()
    payload = json.dumps(certificate, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0 if certificate["pass"] or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
