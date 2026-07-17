# Icosahedral closure certificate (C19)

Exact representation-theoretic certificate for the icosahedral closure theorem:
the twelve-port screen module, the compact-Lie trichotomy, the rank-five
noncentral corollary, and the oriented face-phase multiplicities.

Referenced as **[C19]** in `extra/compact_proof_of_oph.tex` and as the
closure certificate in `paper/observers_are_all_you_need.tex` and
`paper/recovering_relativity_..._compact.tex`.

## Run

```bash
python3 a5_screen_sm_closure.py          # module identity, trichotomy, face phases, kinetic relation
python3 a5_selection_certificate.py      # sharpness data for Cohn-Kumar universal optimality
python3 a5_compact_lie_classifier.py     # compact-Lie enumeration
python3 a5_harmonic_decomposition.py     # angular multiplet sequence
python3 bh_log_correction.py             # conditional horizon log-coefficient decision tree
python3 independent_trichotomy_check.py  # independent re-derivation, trusts nothing above
python3 test_audit.py                    # regression suite
```

Requires Python 3.11+ and SymPy. Both scripts exit 0.

## What is certified (exact; no floating-point fit, no measured number)

| Object | Statement |
|---|---|
| Vertex module | `chi_P12 = (12,0,0,2,2)`, so `P12 = 1 + 3 + 3' + 5`, multiplicity-free |
| Adjacency spectrum | `det(xI-A) = (x-5)(x+1)^5(x^2-5)^3` → canonical ranks `1,3,3,5` |
| SM adjoint restriction | `ad su(3) = End_0(3') = 3' + 5`; with `su(2) → 3`, `u(1) → 1`, the total is `1 + 3 + 3' + 5` |
| Icosahedral selection | 3 distinct inner products `{-1, ±1/sqrt5}`, spherical 5-design ⇒ **sharp** (`m=3`, strength `2m-1=5`). By Cohn–Kumar (JAMS 20, 2007) it uniquely minimizes every strictly completely monotonic pair cost of squared distance, up to `O(3)`. |
| Compact-Lie trichotomy | Exactly three algebras: `u(1)^12`, `su(2)^2 + u(1)^6`, `su(3) + su(2) + u(1)` |
| **Inner-action closure** | If the `A5` action is **inner**: `dim Z(g) <= 1` (inner autos fix the center pointwise); `Z(g)=0` forces `su(2)^4` whose fixed-space dimension is a multiple of 3, contradicting `dim g^{A5}=1`; hence `dim Z(g)=1`, semisimple dim 11, and `11=8+3` uniquely ⇒ `su(3)+su(2)+u(1)`. **Needs no `W5-NONCENTRAL` receipt.** |
| Angular multiplets | `l=2: 5` (irreducible); `l=3: 3'+4`; `l=4: 4+5`; `l=5: 3+3'+5`; `l=6: 1+3+4+5`. First nonconstant invariant at `l=6`. |
| Horizon log coefficient | **Conditional decision tree, not a universal law.** Unconstrained `q`-state cells give `S=K log q` exactly, i.e. `c=0`. Exact 12-port balance: `c=11/2`. 24-slot balance: `c=23/2`. Nonabelian `SU(3)xSU(2)` singlet saddle: `c=11/2`. Full 12-dim gauge singlet incl. `U(1)`: `c=6`. The horizon measure must be derived before `c` is frozen. |
| Rank-five corollary | `W_5` noncentral ⇒ `su(3) + su(2) + u(1)` uniquely |
| Face-phase multiplicities | `m_w = (dim V - chi_V(3A))/3 = (0,1,1,1,2)` on `(1,3,3',4,5)`; minimal nontrivial extension has dimension 3 |
| Missing-four/Higgs no-go | **Rejected.** `End_{A5}(4) = R`, so no `A5`-invariant complex structure exists for a commuting hypercharge `U(1)`. The identity `1+3+3+4+5=16` is dimensional only. |

## Why the trichotomy holds (proof sketch)

A compact Lie algebra is reductive, `g = z + [g,g]`, and both summands are
characteristic, hence `A5`-stable. The identity component of the center is a
torus whose exponential kernel is an integral lattice preserved by every group
automorphism, so the `A5`-action on `z` is defined over `Q`. Because `3` and `3'`
are Galois conjugate over `Q(sqrt5)`, a rational submodule contains them with
equal multiplicity. Enumerating rational centers against compact semisimple
dimensions leaves exactly three cases; the other five die because no compact
semisimple algebra has dimension 1, 5, or 7, or because an `A1^4` / `A1^2`
adjoint cannot supply `5` (any homomorphism `A5 → S_4` is trivial, `A5` being
simple of order 60).

## Claim boundary — read before citing

This is a **receipt-conditional theorem**, not an empirical result.

- It emits the gauge **Lie algebra** on the screen branch **without** the
  realized matter package, so it is logically independent of the MAR clause
  inputs (GAP-B9). That independence is the point of the result.
- It does **not** emit the global `Z6` quotient, the hypercharge lattice, or the
  chiral content. Those remain on the MAR route.
- It **predicts no new measurement.** It is an explanatory closure of the
  `8+3+1` conjunction, not an observational discriminator. Do not list it in a
  forward-test or frozen-target table.

### Open receipts

- **RP-A5** — emit a strictly completely monotonic pair kernel from the finite
  collar mismatch/recovery cost **without inserting the target geometry**. With
  Cohn–Kumar this retires the icosahedral choice entirely.
- **PORT-CURRENT-INNER** — the single gate on the inner branch: construct a
  nonzero refinement-compatible map from port fluctuations to current
  generators and prove the geometric `A5` action is conjugation on its image.
- *(weaker group-level branch only)* **A5-COMMON-ACTION** + **W5-NONCENTRAL** —
  one group-level action shared by ports and gauge reconstruction, plus one
  source-derived repair composition with nonzero projected `W_5` commutator.
- **A5-FAMILY-ATTACHMENT** (family corollary only) — prove the chiral family
  fiber's local face-corner phase is the restriction of a global `3` or `3'`
  action, independent of port labels, worker IDs, chart choices, and refinement
  presentation.

## Prospective coupling relation (NOT present evidence)

If the physical quadratic gauge kinetic operator on the port module is an
adjacency polynomial `K = f(A)`, color coherence (the color triplet and quintet
sharing one kinetic coefficient) forces, at degree two,

```text
k1 = 3*k2 - 2*k3
```

independent of which inequivalent triplet carries color (both assignments
verified). At degree one it collapses to bare coupling unification. This is a
clean discriminator **only after** OPH derives the polynomial degree, the
kinetic normalization, the carrier scale, and the complete threshold/RG map.
**Choosing the degree after inspecting the couplings would invalidate the test**,
and it is therefore not registered as a forward test.

## Formal status

`Lean/.../A5Bridge.lean` verifies the character identities and the
bracket-multiplicity arithmetic without `sorry`. The compact-Lie trichotomy is
**not yet Lean-formalized**; it is certified here by exact representation
arithmetic plus the paper proof. A future Lean development should formalize:
rationality of the center-torus representation, the low-dimensional compact
semisimple classification step, and the rank-five noncentral corollary.

## Novelty boundary

Finite-group flavor models have long used triplet representations to organize
three generations, and the Standard Model's global quotients and line sectors
are established subjects. The narrower claim here is that the same icosahedral
screen supplies the exact **full** gauge-adjoint module, and that compactness
plus one rank-five dynamical receipt turns that module into a unique gauge Lie
algebra. A targeted arXiv/INSPIRE search on 17 July 2026 did not locate the
exact icosahedral-vertex / full-SM-adjoint identity combined with this
compact-Lie trichotomy. **This is not a proof of priority**; a specialist
representation-theory and particle-theory literature review is still required
before any formal novelty claim.
