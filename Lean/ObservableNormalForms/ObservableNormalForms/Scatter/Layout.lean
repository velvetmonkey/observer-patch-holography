import Mathlib
import ObservableNormalForms.Functional

/-!
# Directional scatter-project layouts (issue #626, route 1)

This module freezes the **revised** production rule for issue #626: the
*directional, output-only* scatter-project update law (route 1 of the issue's
two offered routes).

A *layout* is a finite register file together with a finite list of *patches*.
Each patch is an observer-like unit with

* explicit read ports (`Patch.reads`),
* exactly **one** write port (`Patch.write`),
* a local table (`Patch.table`),
* a readback (`Patch.readback`), a computed output (`Patch.output`),
* a per-round mismatch record (`Patch.mismatchBit`, `Patch.record`), and
* a public evidence bundle (`Layout.evidence`), with total mismatch
  `Layout.totalMismatch`.

**The frozen rule** is `Layout.round`: in one synchronous round every patch
reads its ports and writes *only its own output register* with the value of
its table on the readback; registers with no writer are boundary registers
and are left untouched.  A patch can never rewrite a parent wire, because a
parent wire is not its write port.  This is precisely the repair route left
open by the closed negative baseline #328, where the *canonical* rule (a
downstream projection may rewrite a parent wire) has a period-two orbit with
nonzero mismatch on a satisfiable depth-two AND chain.

## Scope

Every theorem below about settling, mismatch, or uniqueness is proved **for
layouts equipped with a certificate** (`Layout.Cert`: single writer per
register, rank-descending reads, positive rank on written registers, rank
zero on unwritten registers).  Nothing here is claimed for arbitrary
scatter-project states or for uncertified layouts; the negative controls in
`ObservableNormalForms.Scatter.Controls` exhibit uncertifiable layouts whose
dynamics genuinely fail.

The target semantics is the existing `RankedSynchronousSystem` of
`ObservableNormalForms.Functional`; it is reused, not rebuilt.  The
intertwiner `Layout.round_eq_synchronousStep` says one directional
scatter-project round *is* one ranked synchronous step, on **every** register
state of a certified layout.
-/

namespace ObservableNormalForms
namespace Scatter

/-- A patch: an observer-like unit with explicit read ports, exactly one
write port, and a local Boolean table.  The single write port is what makes
the update law *directional*: the type does not even allow a patch to
scatter onto a parent wire. -/
structure Patch (n : ℕ) where
  /-- Read ports: the register addresses this patch observes. -/
  reads : List (Fin n)
  /-- The unique write port: the register this patch drives. -/
  write : Fin n
  /-- The local update table, applied to the readback. -/
  table : List Bool → Bool

/-- The public per-patch record emitted each round: the written port, the
observed readback, the computed value, and the mismatch bit. -/
structure PatchRecord (n : ℕ) where
  port : Fin n
  observed : List Bool
  computed : Bool
  mismatch : Bool
  deriving DecidableEq, Repr

namespace Patch

variable {n : ℕ} (p : Patch n) (x : Fin n → Bool)

/-- Readback: the values currently on the patch's read ports. -/
def readback : List Bool := p.reads.map x

/-- The value the patch's table computes from its readback. -/
def output : Bool := p.table (p.readback x)

/-- The local mismatch bit: the computed value disagrees with the register
currently on the write port. -/
def mismatchBit : Bool := p.output x != x p.write

/-- The public record this patch emits when it reads state `x`. -/
def record : PatchRecord n :=
  ⟨p.write, p.readback x, p.output x, p.mismatchBit x⟩

end Patch

/-- A layout: a finite register file and a finite list of patches. -/
structure Layout where
  regCount : ℕ
  patches : List (Patch regCount)

namespace Layout

variable (L : Layout)

/-- A register state of the layout. -/
abbrev RegState : Type := Fin L.regCount → Bool

/-- The (first, in patch order) patch whose write port is `a`, if any.
Certified layouts have at most one such patch. -/
def writer (a : Fin L.regCount) : Option (Patch L.regCount) :=
  L.patches.find? fun p => decide (p.write = a)

/-- **THE FROZEN RULE** (issue #626, route 1): the directional, output-only
scatter-project round.  Every patch reads its ports and scatters the value of
its table *onto its own write port only*; boundary registers (no writer) are
left untouched.  Parent wires are structurally read-only. -/
def round (x : L.RegState) : L.RegState :=
  fun a => (L.writer a).elim (x a) fun p => p.output x

/-- Iterated rounds, with the convention that round zero is the input. -/
def evolve : ℕ → L.RegState → L.RegState
  | 0, x => x
  | n + 1, x => L.round (evolve n x)

/-- The public evidence bundle emitted in one round from state `x`. -/
def evidence (x : L.RegState) : List (PatchRecord L.regCount) :=
  L.patches.map fun p => p.record x

/-- Total mismatch: the number of patches whose record carries a raised
mismatch bit. -/
def totalMismatch (x : L.RegState) : ℕ :=
  (L.evidence x).countP fun r => r.mismatch

theorem writer_mem {a : Fin L.regCount} {p : Patch L.regCount}
    (h : L.writer a = some p) : p ∈ L.patches :=
  List.mem_of_find?_eq_some h

theorem writer_write {a : Fin L.regCount} {p : Patch L.regCount}
    (h : L.writer a = some p) : p.write = a := by
  have h' : L.patches.find? (fun p => decide (p.write = a)) = some p := h
  have hpa := List.find?_some h'
  exact of_decide_eq_true hpa

/-- A well-formedness certificate for a layout: a rank function under which
reads strictly descend, each register has at most one writer, written
registers have positive rank, and unwritten (boundary) registers have rank
zero.  All settling results below are **scoped to certified layouts**. -/
structure Cert (L : Layout) where
  rank : Fin L.regCount → ℕ
  singleWriter : ∀ p ∈ L.patches, ∀ q ∈ L.patches, p.write = q.write → p = q
  descending : ∀ p ∈ L.patches, ∀ a ∈ p.reads, rank a < rank p.write
  writtenPos : ∀ p ∈ L.patches, 0 < rank p.write
  unwrittenZero : ∀ a, L.writer a = none → rank a = 0

theorem writer_of_mem (C : L.Cert) {p : Patch L.regCount}
    (hp : p ∈ L.patches) : L.writer p.write = some p := by
  have hsome : (L.writer p.write).isSome := by
    rw [writer, List.find?_isSome]
    exact ⟨p, hp, by simp⟩
  obtain ⟨q, hq⟩ := Option.isSome_iff_exists.mp hsome
  rw [hq]
  exact congrArg some (C.singleWriter q (L.writer_mem hq) p hp (L.writer_write hq))

theorem rank_pos_of_writer (C : L.Cert) {a : Fin L.regCount}
    {p : Patch L.regCount} (h : L.writer a = some p) : 0 < C.rank a := by
  have := C.writtenPos p (L.writer_mem h)
  rwa [L.writer_write h] at this

theorem writer_eq_none_of_rank_zero (C : L.Cert) {a : Fin L.regCount}
    (h : C.rank a = 0) : L.writer a = none := by
  cases hw : L.writer a with
  | none => rfl
  | some p => have := L.rank_pos_of_writer C hw; omega

/-- The ranked synchronous system a certified layout presents: sites are
registers, ranks come from the certificate, and the generator of a written
register is its patch's table on the readback.  This reuses
`RankedSynchronousSystem` from `ObservableNormalForms.Functional`. -/
def system (C : L.Cert) : RankedSynchronousSystem where
  Site := Fin L.regCount
  Value := fun _ => Bool
  rank := C.rank
  generate := fun a x => (L.writer a).elim false fun p => p.output x
  causal := by
    intro s x y h
    cases hw : L.writer s with
    | none => rfl
    | some p =>
      show p.output x = p.output y
      unfold Patch.output Patch.readback
      congr 1
      refine List.map_congr_left fun b hb => ?_
      refine h b ?_
      have := C.descending p (L.writer_mem hw) b hb
      rwa [L.writer_write hw] at this

/-- **The intertwiner, generic form**: on a certified layout, one directional
scatter-project round is exactly one synchronous step of the presented ranked
system, on every register state. -/
theorem round_eq_synchronousStep (C : L.Cert) (x : L.RegState) :
    L.round x = (L.system C).synchronousStep x := by
  funext a
  dsimp only [round, system, RankedSynchronousSystem.synchronousStep]
  by_cases h0 : C.rank a = 0
  · rw [dif_pos h0, L.writer_eq_none_of_rank_zero C h0]
    rfl
  · rw [dif_neg h0]
    cases hw : L.writer a with
    | none => exact absurd (C.unwrittenZero a hw) h0
    | some p => rfl

theorem evolve_eq_synchronousEvolve (C : L.Cert) (n : ℕ) (x : L.RegState) :
    L.evolve n x = (L.system C).synchronousEvolve n x := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [evolve, RankedSynchronousSystem.synchronousEvolve]
    rw [ih, L.round_eq_synchronousStep C]

/-- Fuelled solver for the layout's generated equations; `fuel` bounds the
rank of the register being solved.  Kernel-computable, so concrete instances
can be checked by `decide`. -/
def solveFuel (x : L.RegState) : ℕ → Fin L.regCount → Bool
  | 0, a => x a
  | fuel + 1, a =>
    (L.writer a).elim (x a) fun p => p.table (p.reads.map (solveFuel x fuel))

/-- The generated extension of a boundary state `x`: the unique state that
keeps the boundary of `x` and satisfies every patch equation. -/
def solution (C : L.Cert) (x : L.RegState) : L.RegState :=
  fun a => L.solveFuel x (C.rank a) a

theorem solveFuel_congr (C : L.Cert) (x : L.RegState) :
    ∀ f₁ f₂ (a : Fin L.regCount), C.rank a ≤ f₁ → C.rank a ≤ f₂ →
      L.solveFuel x f₁ a = L.solveFuel x f₂ a := by
  intro f₁
  induction f₁ with
  | zero =>
    intro f₂ a h1 _
    have hw : L.writer a = none :=
      L.writer_eq_none_of_rank_zero C (Nat.le_zero.mp h1)
    cases f₂ with
    | zero => rfl
    | succ g => simp [solveFuel, hw]
  | succ f ih =>
    intro f₂ a h1 h2
    cases f₂ with
    | zero =>
      have hw : L.writer a = none :=
        L.writer_eq_none_of_rank_zero C (Nat.le_zero.mp h2)
      simp [solveFuel, hw]
    | succ g =>
      show L.solveFuel x (f + 1) a = L.solveFuel x (g + 1) a
      simp only [solveFuel]
      cases hw : L.writer a with
      | none => rfl
      | some p =>
        show p.table (p.reads.map (L.solveFuel x f))
            = p.table (p.reads.map (L.solveFuel x g))
        congr 1
        refine List.map_congr_left fun b hb => ?_
        have hb' : C.rank b < C.rank a := by
          have := C.descending p (L.writer_mem hw) b hb
          rwa [L.writer_write hw] at this
        exact ih g b (by omega) (by omega)

theorem solution_rank_zero (C : L.Cert) (x : L.RegState)
    {a : Fin L.regCount} (h : C.rank a = 0) : L.solution C x a = x a := by
  simp [solution, h, solveFuel]

theorem solution_eq_output (C : L.Cert) (x : L.RegState)
    {a : Fin L.regCount} {p : Patch L.regCount} (hw : L.writer a = some p) :
    L.solution C x a = p.output (L.solution C x) := by
  have hpos : 0 < C.rank a := L.rank_pos_of_writer C hw
  obtain ⟨f, hf⟩ : ∃ f, C.rank a = f + 1 := ⟨C.rank a - 1, by omega⟩
  show L.solveFuel x (C.rank a) a = _
  rw [hf]
  simp only [solveFuel, hw]
  show p.table (p.reads.map (L.solveFuel x f))
      = p.table (p.reads.map fun b => L.solveFuel x (C.rank b) b)
  congr 1
  refine List.map_congr_left fun b hb => ?_
  have hb' : C.rank b < C.rank a := by
    have := C.descending p (L.writer_mem hw) b hb
    rwa [L.writer_write hw] at this
  exact L.solveFuel_congr C x f (C.rank b) b (by omega) le_rfl

theorem solution_isGeneratedExtension (C : L.Cert) (x : L.RegState) :
    (L.system C).IsGeneratedExtension (L.solution C x) := by
  intro s hs
  have hw : ∃ p, L.writer s = some p := by
    cases hw : L.writer s with
    | none => exact absurd (C.unwrittenZero s hw) hs
    | some p => exact ⟨p, rfl⟩
  obtain ⟨p, hw⟩ := hw
  show (L.writer s).elim false (fun q => q.output (L.solution C x))
      = L.solution C x s
  rw [hw, L.solution_eq_output C x hw]
  rfl

theorem solution_sameBoundary (C : L.Cert) (x : L.RegState) :
    (L.system C).SameBoundary x (L.solution C x) := by
  intro s hs
  exact (L.solution_rank_zero C x hs).symm

/-- **Settling** (scoped to certified layouts): if every register has rank at
most `d`, then `d` directional rounds from **any** register state reach the
generated extension of that state's boundary. -/
theorem evolve_settles (C : L.Cert) (x : L.RegState) {d : ℕ}
    (hd : ∀ a, C.rank a ≤ d) : L.evolve d x = L.solution C x := by
  rw [L.evolve_eq_synchronousEvolve C d x]
  exact (L.system C).synchronous_depth_settling (L.solution_sameBoundary C x)
    (L.solution_isGeneratedExtension C x) hd

/-- The settled state is a fixed point of the directional round. -/
theorem round_solution (C : L.Cert) (x : L.RegState) :
    L.round (L.solution C x) = L.solution C x := by
  rw [L.round_eq_synchronousStep C]
  exact (L.system C).synchronousStep_fixed (L.solution_isGeneratedExtension C x)

/-- Zero mismatch is exactly fixedness of the directional round, on certified
layouts. -/
theorem totalMismatch_eq_zero_iff (C : L.Cert) (x : L.RegState) :
    L.totalMismatch x = 0 ↔ L.round x = x := by
  unfold totalMismatch evidence
  rw [List.countP_eq_zero]
  constructor
  · intro h
    funext a
    cases hw : L.writer a with
    | none => simp [round, hw]
    | some p =>
      have hp := L.writer_mem hw
      have hrec := h (p.record x) (List.mem_map.mpr ⟨p, hp, rfl⟩)
      simp only [Patch.record, Patch.mismatchBit, bne_iff_ne, ne_eq] at hrec
      have hout : p.output x = x p.write := by
        by_contra hne
        exact hrec (by simpa using hne)
      simp only [round, hw, Option.elim_some]
      rw [hout, L.writer_write hw]
  · intro h r hr
    obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hr
    have hw := L.writer_of_mem C hp
    have hfix := congrFun h p.write
    simp only [round, hw, Option.elim_some] at hfix
    simp [Patch.record, Patch.mismatchBit, hfix]

/-- The settled state carries zero total mismatch. -/
theorem totalMismatch_solution (C : L.Cert) (x : L.RegState) :
    L.totalMismatch (L.solution C x) = 0 :=
  (L.totalMismatch_eq_zero_iff C _).mpr (L.round_solution C x)

/-- Uniqueness: on a certified layout of bounded rank, any zero-mismatch
state with the boundary of `x` **is** the generated extension of `x`. -/
theorem zeroMismatch_unique (C : L.Cert) {x e : L.RegState} {d : ℕ}
    (hd : ∀ a, C.rank a ≤ d)
    (hboundary : ∀ a, C.rank a = 0 → e a = x a)
    (hm : L.totalMismatch e = 0) : e = L.solution C x := by
  have hfix : L.round e = e := (L.totalMismatch_eq_zero_iff C e).mp hm
  have hext : (L.system C).IsGeneratedExtension e := by
    intro s hs
    have hw : ∃ p, L.writer s = some p := by
      cases hw : L.writer s with
      | none => exact absurd (C.unwrittenZero s hw) hs
      | some p => exact ⟨p, rfl⟩
    obtain ⟨p, hw⟩ := hw
    have hfixs := congrFun hfix s
    simp only [round, hw, Option.elim_some] at hfixs
    show (L.writer s).elim false (fun q => q.output e) = e s
    rw [hw]
    exact hfixs
  refine (L.system C).generatedExtension_unique hext
    (L.solution_isGeneratedExtension C x) ?_ hd
  intro s hs
  rw [hboundary s hs, L.solution_rank_zero C x hs]

/-- Noise recovery: from **any** register state (e.g. after arbitrary
register corruption), `d` directional rounds restore zero mismatch, where `d`
bounds the rank.  Corrupted boundary registers count as a new boundary. -/
theorem noise_recovery (C : L.Cert) (y : L.RegState) {d : ℕ}
    (hd : ∀ a, C.rank a ≤ d) : L.totalMismatch (L.evolve d y) = 0 := by
  rw [L.evolve_settles C y hd]
  exact L.totalMismatch_solution C y

end Layout

end Scatter
end ObservableNormalForms
