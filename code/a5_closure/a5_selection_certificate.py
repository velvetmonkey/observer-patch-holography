#!/usr/bin/env python3
"""Exact certificate that the normalized icosahedron is a sharp 12-point code.

The geometric checks needed for the Cohn--Kumar universal-optimality theorem
are verified symbolically:
  * exactly three inner products among distinct vertices;
  * spherical moments through degree five equal the uniform S^2 moments.
Because the configuration is antipodal, odd moments vanish.  Degree 2 and 4
are checked exactly, which is sufficient for the spherical 5-design claim.

External theorem: a sharp configuration with m distances and strength 2m-1
is universally optimal; for the icosahedron the strictly completely monotonic
minimum is unique up to O(3).
"""
from __future__ import annotations

import json
import sympy as sp

SQRT5 = sp.sqrt(5)
PHI = (1 + SQRT5) / 2
NORM2 = sp.simplify(1 + PHI**2)


def vertices() -> list[sp.Matrix]:
    out: list[sp.Matrix] = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            out.append(sp.Matrix([0, s1, s2 * PHI]) / sp.sqrt(NORM2))
            out.append(sp.Matrix([s1, s2 * PHI, 0]) / sp.sqrt(NORM2))
            out.append(sp.Matrix([s1 * PHI, 0, s2]) / sp.sqrt(NORM2))
    return out


def delta(i: int, j: int) -> int:
    return 1 if i == j else 0


def payload() -> dict:
    vs = vertices()
    assert len(vs) == 12
    norms = [sp.simplify(v.dot(v)) for v in vs]
    assert all(v == 1 for v in norms)

    ips = sorted({sp.simplify(vs[i].dot(vs[j])) for i in range(12) for j in range(i + 1, 12)}, key=float)
    expected_ips = [-sp.Integer(1), -1 / SQRT5, 1 / SQRT5]
    assert all(sp.simplify(a - b) == 0 for a, b in zip(ips, expected_ips))

    mean = sp.simplify(sum(vs, sp.zeros(3, 1)) / 12)
    assert mean == sp.zeros(3, 1)

    m2 = sp.simplify(sum((v * v.T for v in vs), sp.zeros(3, 3)) / 12)
    assert m2 == sp.eye(3) / 3

    fourth_bad = []
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    actual = sp.simplify(sum(v[i] * v[j] * v[k] * v[l] for v in vs) / 12)
                    expected = sp.Rational(1, 15) * (
                        delta(i, j) * delta(k, l)
                        + delta(i, k) * delta(j, l)
                        + delta(i, l) * delta(j, k)
                    )
                    if sp.simplify(actual - expected) != 0:
                        fourth_bad.append((i, j, k, l, actual, expected))
    assert not fourth_bad

    # Antipodality makes every odd moment vanish exactly.
    antipodal = all(any(sp.simplify(v + w) == sp.zeros(3, 1) for w in vs) for v in vs)
    assert antipodal

    return {
        "schema": "A5 icosahedral selection certificate v1",
        "n_vertices": 12,
        "unit_norms": True,
        "distinct_inner_products": [str(sp.simplify(x)) for x in ips],
        "number_of_distances": 3,
        "mean_zero": True,
        "second_moment": [[str(x) for x in row] for row in m2.tolist()],
        "fourth_moment_matches_uniform_S2": True,
        "odd_moments_through_degree_5_vanish_by_antipodality": True,
        "spherical_design_strength": 5,
        "sharp_condition": "m=3 distances and t=2m-1=5",
        "external_theorem": "Cohn--Kumar: sharp configurations are universally optimal; strict completely monotonic energy gives the icosahedron uniquely up to O(3)",
        "oph_consequence": "If the 12 unit screen defects interact through a source-derived strictly completely monotonic pair potential of squared chordal distance, the icosahedral A5 orbit is selected rather than invoked.",
        "open_physical_gate": "derive that pair potential from OPH repair/collar dynamics without choosing it after the fact",
    }


if __name__ == "__main__":
    print(json.dumps(payload(), indent=2))
