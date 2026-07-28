import Mathlib
import ObservableNormalForms.Scatter.Circuit
import ObservableNormalForms.Scatter.Canonical

/-!
# The #328 depth-two AND chain: regression and same-interface separation

Issue #328 (closed 2026-07-27 as the negative baseline) pins the circuit

* `AND(a, b, w)`, `AND(w, c, out)` with inputs `a = 0`, `b = 0`, `c = 1`,

at ophminer commit `afdd1af1491d5bc293595343128c3730637c2a8d`
(`crates/fls-settle/src/lib.rs`, SHA-256
`154abda8798f0ab9c8a95f7f6b74005285d662669768e0fd08d5c74635aa8d21`,
`LazySettler` with `UpdateLaw::Synchronous`).  Starting from
`(w, out) = (0, 1)` the source rule has the exact period-two orbit
`(0,1) → (1,1) → (0,1)`: on the first step the downstream AND rewrites its
unpinned parent wire `w`.  The unique zero-mismatch extension is
`(w, out) = (0, 0)`.

This module machine-checks both halves on the compiled circuit
(`andChain`, wires `0 = a`, `1 = b`, `2 = c`, `3 = w`, `4 = out`):

* **Regression (issue #626 acceptance)**: under the frozen directional rule
  the same start state settles to the unique zero-mismatch state in
  `depthBound = 2` rounds — `regression_settles` is a *pure instantiation*
  of the generic `Circuit.compile_settles`; nothing in the rule or the
  compiler mentions this circuit.  `regression_reaches_target` re-checks the
  same trajectory by raw kernel computation, and
  `regression_unique_zero_mismatch` instantiates the generic uniqueness
  theorem.

* **Separation (the #328 baseline, kept as its own result)**:
  `sel328` is a projection selection for the *canonical* (parent-writable)
  family that reproduces the source-pinned step: on the tie it meets at
  `(w, c, out) = (0, 1, 1)` it rewrites the parent `w`, exactly as the
  pinned Rust rule does.  `sel328_isAdmissible` machine-checks that this
  selection is a nearest-point projection (so the orbit is not an artifact
  of an inadmissible choice), and `canonical_never_settles_328` proves the
  orbit never reaches zero mismatch.  Together with
  `directional_settles_328`, this is a same-interface separation: an
  admissible member of the canonical family oscillates forever on a
  satisfiable circuit, while the directional member (also admissible, by
  `Layout.outputOnlySelection_isAdmissible`) settles in two rounds.

The separation does **not** claim the canonical rule always fails, only
that settling is not forced for every admissible member; that is exactly
the #328 no-go restated over the compiled layout.
-/

namespace ObservableNormalForms
namespace Scatter

open Layout

/-- The #328 circuit: wires `0 = a`, `1 = b`, `2 = c` are inputs,
`3 = w = AND(a, b)`, `4 = out = AND(w, c)`. -/
@[reducible] def andChain : Circuit where
  wires := 5
  node := fun w =>
    match w with
    | ⟨0, _⟩ => .input
    | ⟨1, _⟩ => .input
    | ⟨2, _⟩ => .input
    | ⟨3, _⟩ => .gate and 0 1
    | ⟨4, _⟩ => .gate and 3 2
    | ⟨n + 5, h⟩ => absurd h (by omega)
  topo := by decide

/-- The #328 start state: `a = 0`, `b = 0`, `c = 1`, `(w, out) = (0, 1)`. -/
def x328 : Fin 5 → Bool := fun a =>
  match a with
  | ⟨0, _⟩ => false
  | ⟨1, _⟩ => false
  | ⟨2, _⟩ => true
  | ⟨3, _⟩ => false
  | ⟨4, _⟩ => true
  | ⟨n + 5, h⟩ => absurd h (by omega)

/-- The unique zero-mismatch extension: `(w, out) = (0, 0)`. -/
def t328 : Fin 5 → Bool := fun a =>
  match a with
  | ⟨0, _⟩ => false
  | ⟨1, _⟩ => false
  | ⟨2, _⟩ => true
  | ⟨3, _⟩ => false
  | ⟨4, _⟩ => false
  | ⟨n + 5, h⟩ => absurd h (by omega)

/-- The other state on the #328 orbit: `(w, out) = (1, 1)`. -/
def s328 : Fin 5 → Bool := fun a =>
  match a with
  | ⟨0, _⟩ => false
  | ⟨1, _⟩ => false
  | ⟨2, _⟩ => true
  | ⟨3, _⟩ => true
  | ⟨4, _⟩ => true
  | ⟨n + 5, h⟩ => absurd h (by omega)

/-! ### Directional regression -/

theorem andChain_depthBound : andChain.depthBound = 2 := by decide

theorem andChain_gateCount : andChain.gateCount = 2 := by decide

theorem andChain_regCount : andChain.compile.regCount = 5 := rfl

/-- **#626 regression, generic route**: the #328 start settles in
`depthBound` rounds to the circuit evaluation.  This is a pure instantiation
of `Circuit.compile_settles`; the rule and compiler never inspect which
circuit they run. -/
theorem regression_settles :
    andChain.compile.evolve andChain.depthBound x328 = andChain.eval x328 :=
  andChain.compile_settles x328

/-- **#626 regression, kernel route**: two directional rounds from the #328
start reach `(w, out) = (0, 0)`, checked by raw computation. -/
theorem regression_reaches_target :
    ∀ a, andChain.compile.evolve 2 x328 a = t328 a := by decide

/-- The circuit evaluation of the #328 boundary is the #328 target. -/
theorem regression_eval_target : ∀ a, andChain.eval x328 a = t328 a := by
  decide

/-- The settled state is fixed with zero mismatch (instantiations). -/
theorem regression_settled_fixed :
    andChain.compile.round (andChain.eval x328) = andChain.eval x328 :=
  andChain.compile_settled_fixed x328

theorem regression_settled_mismatch :
    andChain.compile.totalMismatch (andChain.eval x328) = 0 :=
  andChain.compile_settled_mismatch x328

/-- Uniqueness of the zero-mismatch state over the #328 boundary
(instantiation of the generic theorem). -/
theorem regression_unique_zero_mismatch {e : andChain.compile.RegState}
    (hboundary : ∀ a, andChain.depth a = 0 → e a = x328 a)
    (hm : andChain.compile.totalMismatch e = 0) : e = andChain.eval x328 :=
  andChain.compile_zeroMismatch_unique hboundary hm

/-! ### The canonical-family separation -/

/-- The source-step selection: gate `w = AND(a, b)` repairs output-only; the
downstream gate `out = AND(w, c)` repairs output-only *except* on the
observed block `(w, c, out) = (0, 1, 1)`, where — matching the pinned #328
step — it rewrites the parent wire `w` to `1`.  Both moves are Hamming-
minimal projections (`sel328_isAdmissible`). -/
def sel328 : Selection andChain.compile := fun p x a =>
  if p.write = (3 : Fin 5) then
    if p.output x = x 3 then none
    else if a = (3 : Fin 5) then some (p.output x) else none
  else if p.write = (4 : Fin 5) then
    if p.output x = x 4 then none
    else if x 3 = false ∧ x 2 = true ∧ x 4 = true then
      if a = (3 : Fin 5) then some true else none
    else if a = (4 : Fin 5) then some (p.output x) else none
  else none

/-- The parent-rewriting selection is an admissible (nearest-point)
projection for the canonical family on the compiled #328 circuit. -/
theorem sel328_isAdmissible : andChain.compile.IsAdmissible sel328 where
  localized := by decide
  boundaryProtected := by decide
  fixesValid := by decide
  repairs := by decide
  minimal := by decide

theorem canonical_step_x : ∀ a,
    andChain.compile.canonicalRound sel328 x328 a = s328 a := by decide

theorem canonical_step_s : ∀ a,
    andChain.compile.canonicalRound sel328 s328 a = x328 a := by decide

theorem canonical_orbit_even (n : ℕ) :
    andChain.compile.canonicalEvolve sel328 (2 * n) x328 = x328 := by
  induction n with
  | zero => rfl
  | succ k ih =>
    have h2 : 2 * (k + 1) = 2 * k + 1 + 1 := by ring
    rw [h2]
    show andChain.compile.canonicalRound sel328
        (andChain.compile.canonicalEvolve sel328 (2 * k + 1) x328) = x328
    have hodd : andChain.compile.canonicalEvolve sel328 (2 * k + 1) x328
        = s328 := by
      show andChain.compile.canonicalRound sel328
          (andChain.compile.canonicalEvolve sel328 (2 * k) x328) = s328
      rw [ih]
      exact funext canonical_step_x
    rw [hodd]
    exact funext canonical_step_s

theorem canonical_orbit_odd (k : ℕ) :
    andChain.compile.canonicalEvolve sel328 (2 * k + 1) x328 = s328 := by
  show andChain.compile.canonicalRound sel328
      (andChain.compile.canonicalEvolve sel328 (2 * k) x328) = s328
  rw [canonical_orbit_even]
  exact funext canonical_step_x

/-- **The #328 no-go, machine-checked**: under the admissible
parent-rewriting selection, the canonical scatter-project evolution from the
#328 start never reaches zero mismatch. -/
theorem canonical_never_settles_328 (n : ℕ) :
    0 < andChain.compile.totalMismatch
      (andChain.compile.canonicalEvolve sel328 n x328) := by
  rcases Nat.even_or_odd n with he | ho
  · obtain ⟨k, hk⟩ := he
    have h2 : n = 2 * k := by omega
    rw [h2, canonical_orbit_even]
    decide
  · obtain ⟨k, hk⟩ := ho
    rw [hk, canonical_orbit_odd]
    decide

/-- **Headline separation**: on the compiled #328 circuit there is an
admissible member of the canonical scatter-project family that never
settles, while the frozen directional rule settles the same start to the
unique zero-mismatch state in two rounds.  The same-interface intertwiner
for the canonical family is therefore not forced; the directional rule is
the repair. -/
theorem canonical_scatter_project_not_settling_328 :
    (∃ sel : Selection andChain.compile,
      andChain.compile.IsAdmissible sel ∧
        ∀ n, 0 < andChain.compile.totalMismatch
          (andChain.compile.canonicalEvolve sel n x328)) ∧
    andChain.compile.evolve 2 x328 = andChain.eval x328 ∧
    andChain.compile.totalMismatch (andChain.eval x328) = 0 :=
  ⟨⟨sel328, sel328_isAdmissible, canonical_never_settles_328⟩,
    by rw [← andChain_depthBound]; exact regression_settles,
    regression_settled_mismatch⟩

end Scatter
end ObservableNormalForms
