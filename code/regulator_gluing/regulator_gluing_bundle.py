"""Evidence bundle for the quantum regulator gluing gate (issue #529).

The gate implements the acceptance test of paper-audit finding 003:

  * every overlap recharting map must be displayed explicitly;
  * every displayed map must be verified as an invertible *-isomorphism on
    its declared chart-change domain;
  * every triple overlap must satisfy the composition law, either strictly
    or up to a verified central 2-cocycle;
  * a bare finite interface projection supplies none of these maps and must
    be rejected with structured reasons.

All matrix entries are exact Gaussian rationals (Fraction real and imaginary
parts). No floating point enters any check.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

SCHEMA = "oph.regulator_gluing.evidence_bundle/1"
ISSUE = "#529 (paper audit 003)"


# ---------------------------------------------------------------------------
# Exact Gaussian-rational scalars and matrices
# ---------------------------------------------------------------------------

class GQ:
    """A Gaussian rational a + b*i with exact Fraction components."""

    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = Fraction(re)
        self.im = Fraction(im)

    def __add__(self, other):
        return GQ(self.re + other.re, self.im + other.im)

    def __sub__(self, other):
        return GQ(self.re - other.re, self.im - other.im)

    def __mul__(self, other):
        return GQ(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re,
        )

    def __neg__(self):
        return GQ(-self.re, -self.im)

    def conj(self):
        return GQ(self.re, -self.im)

    def norm2(self):
        return self.re * self.re + self.im * self.im

    def inv(self):
        n = self.norm2()
        if n == 0:
            raise ZeroDivisionError("inverse of zero Gaussian rational")
        return GQ(self.re / n, -self.im / n)

    def __eq__(self, other):
        return self.re == other.re and self.im == other.im

    def is_zero(self):
        return self.re == 0 and self.im == 0

    def to_json(self):
        return [str(self.re), str(self.im)]

    @staticmethod
    def from_json(pair):
        return GQ(Fraction(pair[0]), Fraction(pair[1]))

    def __repr__(self):
        return f"GQ({self.re},{self.im})"


ZERO = GQ(0, 0)
ONE = GQ(1, 0)
I_UNIT = GQ(0, 1)


def mat(rows):
    """Build an exact matrix from a list of rows of (re, im) pairs or ints."""
    out = []
    for row in rows:
        new_row = []
        for entry in row:
            if isinstance(entry, GQ):
                new_row.append(entry)
            elif isinstance(entry, tuple):
                new_row.append(GQ(entry[0], entry[1]))
            else:
                new_row.append(GQ(entry, 0))
        out.append(new_row)
    return out


def mat_dim(m):
    return len(m)


def mat_mul(a, b):
    n, k, p = len(a), len(b), len(b[0])
    return [
        [
            sum((a[i][t] * b[t][j] for t in range(k)), ZERO)
            for j in range(p)
        ]
        for i in range(n)
    ]


def mat_add(a, b):
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def mat_scale(s, a):
    return [[s * a[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def dagger(a):
    n, p = len(a), len(a[0])
    return [[a[j][i].conj() for j in range(n)] for i in range(p)]


def identity(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def mat_eq(a, b):
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return False
    return all(a[i][j] == b[i][j] for i in range(len(a)) for j in range(len(a[0])))


def mat_to_json(a):
    return [[entry.to_json() for entry in row] for row in a]


def mat_from_json(rows):
    return [[GQ.from_json(entry) for entry in row] for row in rows]


def kron(a, b):
    na, nb = len(a), len(b)
    out = [[ZERO for _ in range(na * nb)] for _ in range(na * nb)]
    for i in range(na):
        for j in range(na):
            for k in range(nb):
                for l in range(nb):
                    out[i * nb + k][j * nb + l] = a[i][j] * b[k][l]
    return out


def flatten(a):
    return [entry for row in a for entry in row]


def solve_in_span(basis_vectors, target):
    """Solve sum_k c_k basis_k = target exactly over the Gaussian rationals.

    Returns the coefficient list, or None when the target is outside the span.
    """
    if not basis_vectors:
        return None
    n = len(basis_vectors[0])
    k = len(basis_vectors)
    # Augmented system: columns are basis vectors, last column the target.
    aug = [[basis_vectors[c][r] for c in range(k)] + [target[r]] for r in range(n)]
    pivot_cols = []
    row = 0
    for col in range(k):
        pivot = None
        for r in range(row, n):
            if not aug[r][col].is_zero():
                pivot = r
                break
        if pivot is None:
            continue
        aug[row], aug[pivot] = aug[pivot], aug[row]
        inv = aug[row][col].inv()
        aug[row] = [inv * x for x in aug[row]]
        for r in range(n):
            if r != row and not aug[r][col].is_zero():
                factor = aug[r][col]
                aug[r] = [aug[r][c] - factor * aug[row][c] for c in range(k + 1)]
        pivot_cols.append(col)
        row += 1
        if row == n:
            break
    # Consistency: rows with all-zero coefficients must have zero target entry.
    for r in range(n):
        if all(aug[r][c].is_zero() for c in range(k)) and not aug[r][k].is_zero():
            return None
    coeffs = [ZERO for _ in range(k)]
    for r, col in enumerate(pivot_cols):
        coeffs[col] = aug[r][k]
    return coeffs


def span_rank(vectors):
    """Exact rank of a list of vectors over the Gaussian rationals."""
    if not vectors:
        return 0
    work = [list(v) for v in vectors]
    n = len(work[0])
    rank = 0
    col = 0
    for col in range(n):
        pivot = None
        for r in range(rank, len(work)):
            if not work[r][col].is_zero():
                pivot = r
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inv = work[rank][col].inv()
        work[rank] = [inv * x for x in work[rank]]
        for r in range(len(work)):
            if r != rank and not work[r][col].is_zero():
                factor = work[r][col]
                work[r] = [work[r][c] - factor * work[rank][c] for c in range(n)]
        rank += 1
        if rank == len(work):
            break
    return rank


# ---------------------------------------------------------------------------
# Named exact 2x2 unitaries used by the witnesses
# ---------------------------------------------------------------------------

PAULI_X = mat([[0, 1], [1, 0]])
PAULI_Z = mat([[1, 0], [0, -1]])
XZ = mat_mul(PAULI_X, PAULI_Z)            # [[0,-1],[1,0]]
ZX = mat_mul(PAULI_Z, PAULI_X)            # [[0,1],[-1,0]]
MINUS_I_XZ = mat_scale(GQ(0, -1), XZ)     # [[0,i],[-i,0]]
I_ZX = mat_scale(GQ(0, 1), ZX)            # [[0,i],[-i,0]]


# ---------------------------------------------------------------------------
# Witness construction
# ---------------------------------------------------------------------------

def matrix_units(n):
    units = []
    for p in range(n):
        for q in range(n):
            m = [[ZERO for _ in range(n)] for _ in range(n)]
            m[p][q] = ONE
            units.append(m)
    return units


def build_strict_witness():
    """Three M_2(C) patches with a strict unitary cocycle, plus one M_4(C)
    patch glued through a declared proper subalgebra chart-change domain."""
    e2 = matrix_units(2)
    i2 = identity(2)
    sub_generators = [kron(u, i2) for u in e2]  # M_2 (x) 1 inside M_4
    return {
        "name": "strict_cocycle_witness",
        "model": "quantum_regulator_datum",
        "description": (
            "Patches A, B, C carry M_2(C); patch D carries M_4(C). "
            "Rechartings A<-B, B<-C, A<-C are Ad_X, Ad_Z, Ad_XZ with the "
            "strict law U_AB U_BC = U_AC. Recharting A<-D is the declared "
            "*-isomorphism from the subalgebra M_2 (x) 1 of M_4(C) onto "
            "M_2(C)."
        ),
        "patches": [
            {"id": "A", "hilbert_dim": 2},
            {"id": "B", "hilbert_dim": 2},
            {"id": "C", "hilbert_dim": 2},
            {"id": "D", "hilbert_dim": 4},
        ],
        "overlaps": [
            {
                "edge": ["A", "B"],
                "chart_change_domain": {"type": "full_matrix_algebra", "hilbert_dim": 2},
                "recharting": {
                    "type": "unitary",
                    "direction": ["A", "B"],
                    "matrix": mat_to_json(PAULI_X),
                },
            },
            {
                "edge": ["B", "C"],
                "chart_change_domain": {"type": "full_matrix_algebra", "hilbert_dim": 2},
                "recharting": {
                    "type": "unitary",
                    "direction": ["B", "C"],
                    "matrix": mat_to_json(PAULI_Z),
                },
            },
            {
                "edge": ["A", "C"],
                "chart_change_domain": {"type": "full_matrix_algebra", "hilbert_dim": 2},
                "recharting": {
                    "type": "unitary",
                    "direction": ["A", "C"],
                    "matrix": mat_to_json(XZ),
                },
            },
            {
                "edge": ["A", "D"],
                "chart_change_domain": {
                    "type": "generated_subalgebra",
                    "generators": [mat_to_json(g) for g in sub_generators],
                },
                "recharting": {
                    "type": "algebra_isomorphism",
                    "direction": ["A", "D"],
                    "generator_images": [mat_to_json(u) for u in e2],
                },
            },
        ],
        "triples": [
            {"patches": ["A", "B", "C"], "law": "strict"},
        ],
        "quadruples": [],
    }


def build_central_witness():
    """Four M_2(C) patches whose triple overlaps close only up to central
    scalars, with the Cech 2-cocycle identity verified on the quadruple."""
    return {
        "name": "central_defect_witness",
        "model": "quantum_regulator_datum",
        "description": (
            "Patches P, Q, R, S carry M_2(C). The pair rechartings compose "
            "up to central unit scalars z_PQR = i, z_QRS = -i, z_PQS = -i, "
            "z_PRS = i; the alternating product over the quadruple equals 1, "
            "which is the central-extension 2-cocycle identity."
        ),
        "patches": [
            {"id": "P", "hilbert_dim": 2},
            {"id": "Q", "hilbert_dim": 2},
            {"id": "R", "hilbert_dim": 2},
            {"id": "S", "hilbert_dim": 2},
        ],
        "overlaps": [
            {
                "edge": ["P", "Q"],
                "chart_change_domain": {"type": "full_matrix_algebra", "hilbert_dim": 2},
                "recharting": {"type": "unitary", "direction": ["P", "Q"], "matrix": mat_to_json(PAULI_X)},
            },
            {
                "edge": ["Q", "R"],
                "chart_change_domain": {"type": "full_matrix_algebra", "hilbert_dim": 2},
                "recharting": {"type": "unitary", "direction": ["Q", "R"], "matrix": mat_to_json(PAULI_Z)},
            },
            {
                "edge": ["P", "R"],
                "chart_change_domain": {"type": "full_matrix_algebra", "hilbert_dim": 2},
                "recharting": {"type": "unitary", "direction": ["P", "R"], "matrix": mat_to_json(MINUS_I_XZ)},
            },
            {
                "edge": ["R", "S"],
                "chart_change_domain": {"type": "full_matrix_algebra", "hilbert_dim": 2},
                "recharting": {"type": "unitary", "direction": ["R", "S"], "matrix": mat_to_json(PAULI_X)},
            },
            {
                "edge": ["Q", "S"],
                "chart_change_domain": {"type": "full_matrix_algebra", "hilbert_dim": 2},
                "recharting": {"type": "unitary", "direction": ["Q", "S"], "matrix": mat_to_json(I_ZX)},
            },
            {
                "edge": ["P", "S"],
                "chart_change_domain": {"type": "full_matrix_algebra", "hilbert_dim": 2},
                "recharting": {"type": "unitary", "direction": ["P", "S"], "matrix": mat_to_json(PAULI_Z)},
            },
        ],
        "triples": [
            {"patches": ["P", "Q", "R"], "law": "central", "expected_defect": GQ(0, 1).to_json()},
            {"patches": ["Q", "R", "S"], "law": "central", "expected_defect": GQ(0, -1).to_json()},
            {"patches": ["P", "Q", "S"], "law": "central", "expected_defect": GQ(0, -1).to_json()},
            {"patches": ["P", "R", "S"], "law": "central", "expected_defect": GQ(0, 1).to_json()},
        ],
        "quadruples": [["P", "Q", "R", "S"]],
    }


def build_countermodel():
    """The issue #529 bare-interface-projection countermodel."""
    return {
        "name": "bare_interface_projection_countermodel",
        "model": "classical_patch_net",
        "description": (
            "S_i = {0,1,2,3} and S_j = {0,1} both project onto the one-bit "
            "interface I_e = {0,1}; pi_i is many-to-one. The patch net is "
            "overlap consistent and supplies no recharting map."
        ),
        "patches": [
            {"id": "i", "states": [0, 1, 2, 3]},
            {"id": "j", "states": [0, 1]},
        ],
        "interfaces": [
            {
                "edge": ["i", "j"],
                "alphabet": [0, 1],
                "projections": {"i": [0, 1, 0, 1], "j": [0, 1]},
            }
        ],
        "expected": "reject",
    }


# ---------------------------------------------------------------------------
# The gate
# ---------------------------------------------------------------------------

def _fail(reasons, code, detail, **extra):
    entry = {"code": code, "detail": detail}
    entry.update(extra)
    reasons.append(entry)


def _domain_basis(domain_spec, patch_dim):
    """Return the exact matrix basis of the declared chart-change domain."""
    if domain_spec["type"] == "full_matrix_algebra":
        d = domain_spec["hilbert_dim"]
        return matrix_units(d), d
    if domain_spec["type"] == "generated_subalgebra":
        gens = [mat_from_json(g) for g in domain_spec["generators"]]
        return gens, len(gens[0]) if gens else 0
    raise ValueError(f"unknown chart-change domain type {domain_spec['type']!r}")


def _check_star_closure(basis, reasons, tag):
    """Verify that the span of basis is closed under product and adjoint and
    contains the identity; record structured reasons on failure."""
    ok = True
    vectors = [flatten(b) for b in basis]
    if span_rank(vectors) != len(vectors):
        _fail(reasons, "DOMAIN_GENERATORS_DEPENDENT",
              f"{tag}: declared generators are linearly dependent")
        return False
    n = len(basis[0])
    if solve_in_span(vectors, flatten(identity(n))) is None:
        _fail(reasons, "DOMAIN_MISSING_UNIT",
              f"{tag}: the identity is outside the declared domain span")
        ok = False
    for a in basis:
        if solve_in_span(vectors, flatten(dagger(a))) is None:
            _fail(reasons, "DOMAIN_NOT_ADJOINT_CLOSED",
                  f"{tag}: adjoint of a generator leaves the declared span")
            ok = False
            break
    for a in basis:
        for b in basis:
            if solve_in_span(vectors, flatten(mat_mul(a, b))) is None:
                _fail(reasons, "DOMAIN_NOT_PRODUCT_CLOSED",
                      f"{tag}: a generator product leaves the declared span")
                return False
    return ok


def _apply_iso(domain_basis_flat, images, m):
    """Apply the basis-defined linear map to matrix m; None if m is outside
    the domain span."""
    coeffs = solve_in_span(domain_basis_flat, flatten(m))
    if coeffs is None:
        return None
    out = None
    for c, img in zip(coeffs, images):
        term = mat_scale(c, img)
        out = term if out is None else mat_add(out, term)
    return out


def check_overlap(overlap, patch_dims):
    """Verify one displayed overlap map as an invertible *-isomorphism on its
    declared chart-change domain. Returns a structured report."""
    reasons = []
    edge = overlap.get("edge")
    tag = f"overlap {edge}"
    recharting = overlap.get("recharting")
    report = {"edge": edge, "checks": [], "reasons": reasons}

    if not recharting or "type" not in recharting:
        _fail(reasons, "NO_RECHARTING_MAP",
              f"{tag}: no algebra map is declared; interface projections by "
              "themselves supply none")
        report["passed"] = False
        return report

    report["displayed_map"] = recharting
    domain_spec = overlap["chart_change_domain"]
    src, dst = recharting["direction"][0], recharting["direction"][1]

    if recharting["type"] == "unitary":
        u = mat_from_json(recharting["matrix"])
        d = mat_dim(u)
        # Convention: direction [A, B] is the map onto patch A from patch B.
        d_dst, d_src = patch_dims[src], patch_dims[dst]
        if d_src != d_dst:
            _fail(reasons, "ALGEBRA_DIMENSION_MISMATCH",
                  f"{tag}: dim M_{d_src}(C) = {d_src**2} versus "
                  f"dim M_{d_dst}(C) = {d_dst**2}; no *-isomorphism exists")
        if d != d_dst:
            _fail(reasons, "UNITARY_DIMENSION_MISMATCH",
                  f"{tag}: unitary is {d}x{d}, patch Hilbert dimension is {d_dst}")
        udag = dagger(u)
        left = mat_eq(mat_mul(udag, u), identity(d))
        right = mat_eq(mat_mul(u, udag), identity(d))
        report["checks"].append({"name": "unitarity_U*U=I", "passed": left})
        report["checks"].append({"name": "unitarity_UU*=I", "passed": right})
        if not (left and right):
            _fail(reasons, "NOT_UNITARY", f"{tag}: U*U = I or UU* = I fails exactly")
        # Ad_U on the declared domain: bijection, product, adjoint, unit.
        basis, _ = _domain_basis(domain_spec, d)
        images = [mat_mul(mat_mul(u, b), udag) for b in basis]
        bij = span_rank([flatten(m) for m in images]) == len(images)
        report["checks"].append({"name": "Ad_U_linear_bijection_on_domain", "passed": bij})
        if not bij:
            _fail(reasons, "NOT_INJECTIVE", f"{tag}: Ad_U collapses the declared domain")
        prod_ok = all(
            mat_eq(
                mat_mul(mat_mul(u, mat_mul(a, b)), udag),
                mat_mul(mat_mul(mat_mul(u, a), udag), mat_mul(mat_mul(u, b), udag)),
            )
            for a in basis for b in basis
        )
        adj_ok = all(
            mat_eq(mat_mul(mat_mul(u, dagger(a)), udag), dagger(mat_mul(mat_mul(u, a), udag)))
            for a in basis
        )
        unit_ok = mat_eq(mat_mul(mat_mul(u, identity(d)), udag), identity(d))
        report["checks"].append({"name": "Ad_U_preserves_product", "passed": prod_ok})
        report["checks"].append({"name": "Ad_U_preserves_adjoint", "passed": adj_ok})
        report["checks"].append({"name": "Ad_U_preserves_unit", "passed": unit_ok})
        if not (prod_ok and adj_ok and unit_ok):
            _fail(reasons, "NOT_STAR_HOMOMORPHISM", f"{tag}: Ad_U fails a *-map identity")

    elif recharting["type"] == "algebra_isomorphism":
        basis, d_src_mat = _domain_basis(domain_spec, None)
        images = [mat_from_json(g) for g in recharting["generator_images"]]
        if len(images) != len(basis):
            _fail(reasons, "GENERATOR_IMAGE_COUNT_MISMATCH",
                  f"{tag}: {len(basis)} generators, {len(images)} images")
            report["passed"] = False
            return report
        dom_ok = _check_star_closure(basis, reasons, tag + " (domain)")
        img_ok = _check_star_closure(images, reasons, tag + " (image)")
        report["checks"].append({"name": "domain_is_star_subalgebra", "passed": dom_ok})
        report["checks"].append({"name": "image_is_star_subalgebra", "passed": img_ok})
        dom_flat = [flatten(b) for b in basis]
        img_flat = [flatten(m) for m in images]
        bij = (span_rank(dom_flat) == len(basis) == span_rank(img_flat))
        report["checks"].append({"name": "linear_bijection_on_domain", "passed": bij})
        if not bij:
            _fail(reasons, "NOT_INJECTIVE",
                  f"{tag}: the declared map is degenerate on its domain")
        prod_ok = True
        for a_idx, a in enumerate(basis):
            for b_idx, b in enumerate(basis):
                lhs = _apply_iso(dom_flat, images, mat_mul(a, b))
                rhs = mat_mul(images[a_idx], images[b_idx])
                if lhs is None or not mat_eq(lhs, rhs):
                    prod_ok = False
        adj_ok = True
        for a_idx, a in enumerate(basis):
            lhs = _apply_iso(dom_flat, images, dagger(a))
            if lhs is None or not mat_eq(lhs, dagger(images[a_idx])):
                adj_ok = False
        n_dom = len(basis[0])
        unit_img = _apply_iso(dom_flat, images, identity(n_dom))
        unit_ok = unit_img is not None and mat_eq(unit_img, identity(len(images[0])))
        report["checks"].append({"name": "preserves_product", "passed": prod_ok})
        report["checks"].append({"name": "preserves_adjoint", "passed": adj_ok})
        report["checks"].append({"name": "preserves_unit", "passed": unit_ok})
        if not (prod_ok and adj_ok and unit_ok):
            _fail(reasons, "NOT_STAR_HOMOMORPHISM",
                  f"{tag}: a *-map identity fails on the declared domain")

    else:
        _fail(reasons, "UNKNOWN_MAP_TYPE",
              f"{tag}: recharting type {recharting['type']!r} is outside the model")

    report["passed"] = not reasons
    return report


def _edge_unitary(witness, a, b):
    """The unitary implementing the map onto patch a from patch b, using the
    stored orientation and inverses. None when the edge is absent or the
    stored map is non-unitary."""
    for overlap in witness["overlaps"]:
        rech = overlap.get("recharting") or {}
        if rech.get("type") != "unitary":
            continue
        direction = rech.get("direction")
        if direction == [a, b]:
            return mat_from_json(rech["matrix"])
        if direction == [b, a]:
            return dagger(mat_from_json(rech["matrix"]))
    return None


def check_triple(witness, triple):
    """Verify the triple-overlap composition law, strict or central."""
    i, j, k = triple["patches"]
    reasons = []
    report = {"patches": triple["patches"], "law": triple["law"], "reasons": reasons}
    u_ij = _edge_unitary(witness, i, j)
    u_jk = _edge_unitary(witness, j, k)
    u_ik = _edge_unitary(witness, i, k)
    if u_ij is None or u_jk is None or u_ik is None:
        _fail(reasons, "MISSING_EDGE_MAP",
              f"triple {triple['patches']}: an edge map is undeclared")
        report["passed"] = False
        return report
    composite = mat_mul(u_ij, u_jk)
    if triple["law"] == "strict":
        ok = mat_eq(composite, u_ik)
        report["checks"] = [{"name": "strict_cocycle_UijUjk=Uik", "passed": ok}]
        if not ok:
            _fail(reasons, "COCYCLE_VIOLATION",
                  f"triple {triple['patches']}: U_ij U_jk differs from U_ik")
    elif triple["law"] == "central":
        defect = mat_mul(composite, dagger(u_ik))
        d = mat_dim(defect)
        scalar = defect[0][0]
        central = all(
            defect[r][c] == (scalar if r == c else ZERO)
            for r in range(d) for c in range(d)
        )
        unit_modulus = scalar.norm2() == 1
        expected = GQ.from_json(triple["expected_defect"])
        matches = scalar == expected
        report["checks"] = [
            {"name": "defect_is_central_scalar", "passed": central},
            {"name": "defect_has_unit_modulus", "passed": unit_modulus},
            {"name": "defect_matches_declared_cocycle", "passed": matches},
        ]
        report["measured_defect"] = scalar.to_json()
        if not (central and unit_modulus and matches):
            _fail(reasons, "CENTRAL_DEFECT_VIOLATION",
                  f"triple {triple['patches']}: defect is outside the declared "
                  "central 2-cocycle")
    else:
        _fail(reasons, "UNKNOWN_TRIPLE_LAW", f"law {triple['law']!r}")
    report["passed"] = not reasons
    return report


def _triple_defect(witness, i, j, k):
    u_ij = _edge_unitary(witness, i, j)
    u_jk = _edge_unitary(witness, j, k)
    u_ik = _edge_unitary(witness, i, k)
    defect = mat_mul(mat_mul(u_ij, u_jk), dagger(u_ik))
    return defect[0][0]


def check_quadruple(witness, quad):
    """Verify the Cech 2-cocycle identity
    z_jkl * z_ikl^{-1} * z_ijl * z_ijk^{-1} = 1 on a quadruple overlap."""
    i, j, k, l = quad
    z_jkl = _triple_defect(witness, j, k, l)
    z_ikl = _triple_defect(witness, i, k, l)
    z_ijl = _triple_defect(witness, i, j, l)
    z_ijk = _triple_defect(witness, i, j, k)
    product = z_jkl * z_ikl.inv() * z_ijl * z_ijk.inv()
    ok = product == ONE
    return {
        "patches": quad,
        "checks": [{"name": "cech_2cocycle_identity", "passed": ok}],
        "measured_product": product.to_json(),
        "passed": ok,
        "reasons": [] if ok else [{
            "code": "TWO_COCYCLE_VIOLATION",
            "detail": f"quadruple {quad}: the alternating defect product differs from 1",
        }],
    }


def reject_classical_patch_net(document):
    """Structured rejection of a bare classical patch net: interface
    projections supply no invertible algebra map."""
    reasons = []
    for interface in document.get("interfaces", []):
        edge = interface["edge"]
        _fail(reasons, "NO_RECHARTING_MAP",
              f"overlap {edge}: interface projections pi_{{i,e}}, pi_{{j,e}} "
              "supply no algebra map; the quantum regulator gluing datum is "
              "a declared input and is absent here", edge=edge)
        sizes = {p["id"]: len(p["states"]) for p in document["patches"]}
        a, b = edge
        if sizes[a] != sizes[b]:
            _fail(reasons, "STATE_SPACE_BIJECTION_IMPOSSIBLE",
                  f"overlap {edge}: |S_{a}| = {sizes[a]} versus "
                  f"|S_{b}| = {sizes[b]}; no invertible recharting exists",
                  edge=edge)
            _fail(reasons, "ALGEBRA_DIMENSION_MISMATCH",
                  f"overlap {edge}: dim M_{sizes[a]}(C) = {sizes[a]**2} versus "
                  f"dim M_{sizes[b]}(C) = {sizes[b]**2}; no *-isomorphism "
                  f"M_{sizes[a]}(C) -> M_{sizes[b]}(C) exists",
                  edge=edge)
        proj = interface["projections"]
        if len(set(proj[a])) < len(proj[a]):
            _fail(reasons, "MANY_TO_ONE_PROJECTION",
                  f"overlap {edge}: pi_{{{a},e}} = {proj[a]} is many-to-one, "
                  "so no chart-change inverse exists on the interface fibers",
                  edge=edge)
    return {"name": document.get("name"), "passed": False, "reasons": reasons}


def run_gate(document):
    """Run the full acceptance gate on one witness or countermodel document.

    A document passes only when it declares a quantum regulator datum whose
    displayed overlap maps are all invertible *-isomorphisms on their declared
    chart-change domains and whose triple and quadruple laws all verify.
    """
    if document.get("model") != "quantum_regulator_datum":
        return reject_classical_patch_net(document)

    patch_dims = {p["id"]: p["hilbert_dim"] for p in document["patches"]}
    overlap_reports = [check_overlap(o, patch_dims) for o in document["overlaps"]]
    triple_reports = [check_triple(document, t) for t in document.get("triples", [])]
    quad_reports = [check_quadruple(document, q) for q in document.get("quadruples", [])]
    all_reports = overlap_reports + triple_reports + quad_reports
    passed = all(r["passed"] for r in all_reports)
    return {
        "name": document.get("name"),
        "passed": passed,
        "overlaps": overlap_reports,
        "triples": triple_reports,
        "quadruples": quad_reports,
        "reasons": [r for rep in all_reports for r in rep["reasons"]],
    }


# ---------------------------------------------------------------------------
# Bundle assembly
# ---------------------------------------------------------------------------

def build_bundle():
    return {
        "schema": SCHEMA,
        "issue": ISSUE,
        "arithmetic": "gaussian_rational_exact",
        "gate": (
            "Every overlap map is displayed; each is verified as an "
            "invertible *-isomorphism on its declared chart-change domain; "
            "every triple-overlap composition law is verified, strictly or "
            "as a central 2-cocycle with the Cech identity on quadruples; a "
            "bare finite interface projection is rejected with structured "
            "reasons."
        ),
        "witnesses": [build_strict_witness(), build_central_witness()],
        "countermodel": build_countermodel(),
    }


def run_bundle(bundle):
    witness_reports = [run_gate(w) for w in bundle["witnesses"]]
    counter_report = run_gate(bundle["countermodel"])
    negative_gate_holds = counter_report["passed"] is False and bool(counter_report["reasons"])
    accepted = all(r["passed"] for r in witness_reports) and negative_gate_holds
    return {
        "schema": bundle["schema"],
        "issue": bundle["issue"],
        "accepted": accepted,
        "witness_reports": witness_reports,
        "countermodel_report": counter_report,
        "negative_gate_holds": negative_gate_holds,
    }


ARTIFACT_PATH = Path(__file__).parent / "runs" / "regulator_gluing_evidence_bundle_current.json"


def emit_artifact(path=ARTIFACT_PATH):
    bundle = build_bundle()
    report = run_bundle(bundle)
    artifact = {"bundle": bundle, "report": report}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2) + "\n")
    return artifact


if __name__ == "__main__":
    result = emit_artifact()
    print(json.dumps({
        "accepted": result["report"]["accepted"],
        "witnesses": {
            r["name"]: r["passed"] for r in result["report"]["witness_reports"]
        },
        "countermodel_rejected": result["report"]["negative_gate_holds"],
        "artifact": str(ARTIFACT_PATH),
    }, indent=2))
