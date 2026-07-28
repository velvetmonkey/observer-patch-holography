import Mathlib
import ObservableNormalForms.Scatter.Layout

/-!
# The canonical (non-directional) scatter-project family

This module models the *canonical* synchronous scatter-project rule — the one
that issue #328 closed negatively — as a family of update laws parameterized
by a *projection selection*.  Under the canonical rule an invalid patch
projects its **whole incident block** (read ports and write port) onto its
constraint set; in particular a downstream patch may rewrite a parent wire.
The projection is a nearest-point map, so a selection is *admissible*
(`IsAdmissible`) when it

* touches only incident, writer-owned (non-boundary) registers,
* fixes already-valid patches,
* lands on the patch's constraint set, and
* moves by at most the Hamming distance of any admissible satisfying
  alternative (nearest-point property, via Mathlib's `hammingDist`).

Ties between equally-near satisfying assignments are *not* resolved by the
family: every admissible tie-break is a member.  The source-pinned rule of
#328 (ophminer `afdd1af1491d5bc293595343128c3730637c2a8d`,
`crates/fls-settle/src/lib.rs`, SHA-256
`154abda8798f0ab9c8a95f7f6b74005285d662669768e0fd08d5c74635aa8d21`,
`LazySettler` with `UpdateLaw::Synchronous`) is one such member on the #328
circuit: its documented step rewrites the parent wire on the tie it meets.

Synchronous write collisions are resolved deterministically by first-patch
order (`Layout.canonicalRound`); on the #328 orbit at most one patch is
invalid per round, so the resolution is never exercised there.

`Layout.round_eq_canonical_outputOnly` shows the **frozen directional rule
is itself a member of this family** — the output-only projection choice —
so the #328 separation in `ObservableNormalForms.Scatter.Regression328` is a
genuine same-interface separation between two admissible members: one
oscillates forever with nonzero mismatch, the other settles.
-/

namespace ObservableNormalForms
namespace Scatter

/-- A projection selection: for each patch and observed register state, the
partial rewrite (register ↦ proposed value) the patch's projection chooses.
`none` means the register is left alone. -/
abbrev Selection (L : Layout) :=
  Patch L.regCount → L.RegState → Fin L.regCount → Option Bool

namespace Layout

variable (L : Layout)

/-- Apply a partial rewrite to a register state. -/
def applyProposal (pr : Fin L.regCount → Option Bool) (x : L.RegState) :
    L.RegState :=
  fun a => (pr a).getD (x a)

/-- One synchronous round of the canonical scatter-project rule under a
selection: every register takes the first proposal (in patch order) that
targets it, if any. -/
def canonicalRound (sel : Selection L) (x : L.RegState) : L.RegState :=
  fun a => ((L.patches.filterMap fun p => sel p x a).head?).getD (x a)

/-- Iterated canonical rounds. -/
def canonicalEvolve (sel : Selection L) : ℕ → L.RegState → L.RegState
  | 0, x => x
  | n + 1, x => L.canonicalRound sel (canonicalEvolve sel n x)

/-- Admissibility: the conditions any nearest-point projection selection of
the canonical scatter-project rule satisfies.  The mismatch/validity test is
the patch's own record (`Patch.output` versus the write-port register). -/
structure IsAdmissible (sel : Selection L) : Prop where
  /-- Proposals only touch the patch's incident block. -/
  localized : ∀ p ∈ L.patches, ∀ (x : L.RegState) (a : Fin L.regCount),
    (sel p x a).isSome → a ∈ p.reads ∨ a = p.write
  /-- Proposals never touch boundary (writer-less) registers: pinned inputs
  stay pinned. -/
  boundaryProtected : ∀ p ∈ L.patches, ∀ (x : L.RegState) (a : Fin L.regCount),
    (sel p x a).isSome → (L.writer a).isSome
  /-- A projection fixes states that already satisfy the patch. -/
  fixesValid : ∀ p ∈ L.patches, ∀ x : L.RegState,
    p.output x = x p.write → ∀ a, sel p x a = none
  /-- The projected state satisfies the patch's constraint. -/
  repairs : ∀ p ∈ L.patches, ∀ x : L.RegState, p.output x ≠ x p.write →
    p.output (L.applyProposal (sel p x) x)
      = L.applyProposal (sel p x) x p.write
  /-- Nearest-point property: no admissible satisfying alternative is
  strictly closer in Hamming distance. -/
  minimal : ∀ p ∈ L.patches, ∀ x y : L.RegState,
    p.output y = y p.write →
    (∀ a : Fin L.regCount, ¬(a ∈ p.reads ∨ a = p.write) → y a = x a) →
    (∀ a : Fin L.regCount, L.writer a = none → y a = x a) →
    hammingDist x (L.applyProposal (sel p x) x) ≤ hammingDist x y

/-- The output-only projection choice: an invalid patch rewrites exactly its
own write port to its computed output.  This is the directional rule seen as
a member of the canonical family. -/
def outputOnlySelection : Selection L := fun p x a =>
  if p.output x = x p.write then none
  else if a = p.write then some (p.output x) else none

section HeadFilterMap

theorem head?_filterMap_getD {α β : Type*} {l : List α} {f : α → Option β}
    {p : α} (hp : p ∈ l) (h : ∀ q ∈ l, f q = none ∨ f q = f p) (d : β) :
    ((l.filterMap f).head?).getD d = (f p).getD d := by
  induction l with
  | nil => cases hp
  | cons hd tl ih =>
    rw [List.filterMap_cons]
    cases hf : f hd with
    | none =>
      rcases List.mem_cons.mp hp with rfl | hp'
      · have hall : ∀ q ∈ tl, f q = none := by
          intro q hq
          rcases h q (List.mem_cons_of_mem _ hq) with hq' | hq'
          · exact hq'
          · rw [hq', hf]
        rw [List.filterMap_eq_nil_iff.mpr hall, hf]
        rfl
      · exact ih hp' fun q hq => h q (List.mem_cons_of_mem _ hq)
    | some v =>
      have hfp : f p = some v := by
        rcases h hd List.mem_cons_self with hhd | hhd
        · rw [hf] at hhd; cases hhd
        · rw [← hhd, hf]
      rw [hfp]
      rfl

end HeadFilterMap

theorem writer_eq_none_iff {a : Fin L.regCount} :
    L.writer a = none ↔ ∀ p ∈ L.patches, p.write ≠ a := by
  rw [writer, List.find?_eq_none]
  simp

/-- **The directional rule is a member of the canonical family**: on a
certified layout, one round of the canonical rule under the output-only
projection choice is exactly one directional round. -/
theorem round_eq_canonical_outputOnly (C : L.Cert) (x : L.RegState) :
    L.canonicalRound L.outputOnlySelection x = L.round x := by
  funext a
  cases hw : L.writer a with
  | none =>
    have hnone : ∀ q ∈ L.patches, L.outputOnlySelection q x a = none := by
      intro q hq
      unfold outputOnlySelection
      by_cases hv : q.output x = x q.write
      · rw [if_pos hv]
      · rw [if_neg hv, if_neg]
        intro hqa
        exact (L.writer_eq_none_iff.mp hw q hq) (hqa ▸ rfl)
    show ((L.patches.filterMap fun p => L.outputOnlySelection p x a).head?).getD
        (x a) = (L.writer a).elim (x a) fun p => p.output x
    rw [List.filterMap_eq_nil_iff.mpr hnone, hw]
    rfl
  | some p =>
    have hp := L.writer_mem hw
    have hpa := L.writer_write hw
    have huniq : ∀ q ∈ L.patches, L.outputOnlySelection q x a = none ∨
        L.outputOnlySelection q x a = L.outputOnlySelection p x a := by
      intro q hq
      by_cases hqa : q.write = a
      · right
        have : q = p := C.singleWriter q hq p hp (hqa.trans hpa.symm)
        rw [this]
      · left
        unfold outputOnlySelection
        by_cases hv : q.output x = x q.write
        · rw [if_pos hv]
        · rw [if_neg hv, if_neg (fun h : a = q.write => hqa h.symm)]
    show ((L.patches.filterMap fun q => L.outputOnlySelection q x a).head?).getD
        (x a) = (L.writer a).elim (x a) fun p => p.output x
    rw [head?_filterMap_getD hp huniq (x a), hw]
    unfold outputOnlySelection
    by_cases hv : p.output x = x p.write
    · rw [if_pos hv]
      show x a = p.output x
      rw [hv, hpa]
    · rw [if_neg hv, if_pos hpa.symm]
      rfl

/-- The output-only projection choice is admissible on every certified
layout: it is localized, boundary-protecting, fixes valid patches, lands on
the constraint set, and is nearest-point. -/
theorem outputOnlySelection_isAdmissible (C : L.Cert) :
    L.IsAdmissible L.outputOnlySelection where
  localized := by
    intro p _ x a hsome
    unfold outputOnlySelection at hsome
    by_cases hv : p.output x = x p.write
    · rw [if_pos hv] at hsome; cases hsome
    · rw [if_neg hv] at hsome
      by_cases ha : a = p.write
      · exact Or.inr ha
      · rw [if_neg ha] at hsome; cases hsome
  boundaryProtected := by
    intro p hp x a hsome
    unfold outputOnlySelection at hsome
    by_cases hv : p.output x = x p.write
    · rw [if_pos hv] at hsome; cases hsome
    · rw [if_neg hv] at hsome
      by_cases ha : a = p.write
      · subst ha
        rw [L.writer_of_mem C hp]
        rfl
      · rw [if_neg ha] at hsome; cases hsome
  fixesValid := by
    intro p _ x hv a
    unfold outputOnlySelection
    rw [if_pos hv]
  repairs := by
    intro p hp x hv
    have hwr : p.write ∉ p.reads := by
      intro hmem
      have := C.descending p hp p.write hmem
      omega
    have hx' : ∀ b ∈ p.reads,
        L.applyProposal (L.outputOnlySelection p x) x b = x b := by
      intro b hb
      unfold applyProposal outputOnlySelection
      rw [if_neg hv, if_neg (fun h : b = p.write => hwr (h ▸ hb))]
      rfl
    have hout : p.output (L.applyProposal (L.outputOnlySelection p x) x)
        = p.output x := by
      unfold Patch.output Patch.readback
      congr 1
      exact List.map_congr_left hx'
    rw [hout]
    show p.output x
        = (L.outputOnlySelection p x p.write).getD (x p.write)
    unfold outputOnlySelection
    rw [if_neg hv, if_pos rfl]
    rfl
  minimal := by
    intro p _ x y hy _ _
    by_cases hv : p.output x = x p.write
    · have hfix : L.applyProposal (L.outputOnlySelection p x) x = x := by
        funext a
        unfold applyProposal outputOnlySelection
        rw [if_pos hv]
        rfl
      rw [hfix, hammingDist_self]
      exact Nat.zero_le _
    · have hxy : x ≠ y := fun h => hv (by rw [h]; exact hy)
      have h1 : 1 ≤ hammingDist x y := hammingDist_pos.mpr hxy
      have hupd : L.applyProposal (L.outputOnlySelection p x) x
          = Function.update x p.write (p.output x) := by
        funext a
        unfold applyProposal outputOnlySelection
        rw [if_neg hv]
        by_cases ha : a = p.write
        · subst ha
          rw [if_pos rfl, Function.update_self]
          rfl
        · rw [if_neg ha, Function.update_of_ne ha]
          rfl
      have hle : hammingDist x (Function.update x p.write (p.output x)) ≤ 1 := by
        unfold hammingDist
        refine le_trans (Finset.card_le_card (t := {p.write})
          (fun i hi => ?_)) (by simp)
        simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hi
        simp only [Finset.mem_singleton]
        by_contra hne
        exact hi (by rw [Function.update_of_ne hne])
      rw [hupd]
      omega

end Layout

end Scatter
end ObservableNormalForms
