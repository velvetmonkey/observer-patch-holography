import Mathlib
import ObserverPatchHolography.Primitives

/-!
# Issue #517.1 — the repair diamond, made conditional and machine-checked

Obligation 1 of issue #517: the `K ≠ L` diamond argument of *Reality as a
Consensus Protocol* ignores conflict-component merging after the first
repair — "prove stability/joinability for the enlarged aggregate, or make
the theorem conditional".

This module makes the diamond **conditional, with both the condition and its
sharpness machine-checked**, for the constructed repair operator of
`Primitives.lean`:

* `localRepair_comm_of_nonadjacent` — the diamond **holds** for
  non-interacting repair sites: if no edge is incident to both `i` and `j`
  (`Nonadjacent`), the two constructed local moves commute on the nose,
  `localRepair i (localRepair j x) = localRepair j (localRepair i x)`.
  This is the honest content of the paper's `K ≠ L` case: disjoint conflict
  components do not merge — each site's trigger, solvability predicate and
  classically chosen repair are untouched by the other's move
  (`localRepair_update_of_nonadjacent`, the pointwise commutation engine).
* The **adjacent (merging) case provably fails**, and the failure is already
  in the library: `demoCarrier_repairs_dont_commute` (two sites sharing an
  edge whose moves disagree) and `demoCarrier_not_confluent` (two distinct
  normal forms from one record). The enlarged-aggregate case is not an
  omitted lemma — it is a genuine counterexample class, so the diamond
  cannot be unconditional.

Together: the repair rewriting system satisfies the diamond exactly on
non-interacting site pairs; joinability for interacting pairs requires
extra hypotheses (e.g. the global commutation law `H4` of the
`LocalRepairDynamics` layer, whose sufficiency is `confluence_of_commute`),
and any route through the generic ONF theorem must carry those hypotheses
explicitly — which is precisely what #517 demands.

Scope note (#517.2, refinement moduli): the stagewise `η`/`ω` composition
question concerns the paper's analytic refinement tower, which has no
counterpart in this Lean core; it is out of scope for this module and is
reported as an honest stop, not silently absorbed.

No `sorry`, no `native_decide`, no new axiom.
-/

namespace OPH

/-- Two repair sites are **non-adjacent** when no edge is incident to both:
    their conflict components are disjoint, so neither move can touch an
    overlap the other one reads or repairs. -/
def Nonadjacent (C : OPHCarrier) (i j : C.Patch) : Prop :=
  ∀ e : C.Edge, ¬ ((C.src e = i ∨ C.tgt e = i) ∧ (C.src e = j ∨ C.tgt e = j))

theorem Nonadjacent.symm {C : OPHCarrier} {i j : C.Patch}
    (h : Nonadjacent C i j) : Nonadjacent C j i :=
  fun e hc => h e ⟨hc.2, hc.1⟩

/-- Endpoints of an edge incident to `j` avoid the non-adjacent site `i`. -/
theorem Nonadjacent.not_endpoint {C : OPHCarrier} {i j : C.Patch}
    (hna : Nonadjacent C i j) {e : C.Edge}
    (hinc : C.src e = j ∨ C.tgt e = j) :
    C.src e ≠ i ∧ C.tgt e ≠ i :=
  ⟨fun hsrc => hna e ⟨Or.inl hsrc, hinc⟩, fun htgt => hna e ⟨Or.inr htgt, hinc⟩⟩

section Diamond

variable {C : OPHCarrier}

/-- An edge whose endpoints avoid `i` keeps its consistency status when
    patch `i` is overwritten. -/
theorem edgeConsistentAt_update_of_not_incident {e : C.Edge} {i : C.Patch}
    (hs : C.src e ≠ i) (ht : C.tgt e ≠ i) (x : Records C) (s : C.State i) :
    edgeConsistentAt e (Function.update x i s) ↔ edgeConsistentAt e x := by
  unfold edgeConsistentAt
  rw [Function.update_of_ne hs, Function.update_of_ne ht]

/-- The trigger at `j` is untouched by overwriting the non-adjacent `i`. -/
theorem localTrigger_update_of_nonadjacent {i j : C.Patch}
    (hna : Nonadjacent C i j) (x : Records C) (s : C.State i) :
    LocalTrigger j (Function.update x i s) ↔ LocalTrigger j x := by
  refine exists_congr fun e => and_congr_right fun hinc => not_congr ?_
  obtain ⟨hs, ht⟩ := hna.not_endpoint hinc
  exact edgeConsistentAt_update_of_not_incident hs ht x s

/-- The transactional-repair predicate at `j` is untouched, pointwise in the
    candidate state, by overwriting the non-adjacent `i`. -/
theorem solvesAt_update_of_nonadjacent {i j : C.Patch} (hij : i ≠ j)
    (hna : Nonadjacent C i j) (x : Records C) (s : C.State i) (t : C.State j) :
    SolvesAt j (Function.update x i s) t ↔ SolvesAt j x t := by
  refine forall_congr' fun e => imp_congr_right fun hinc => ?_
  obtain ⟨hs, ht⟩ := hna.not_endpoint hinc
  rw [Function.update_comm hij s t x]
  exact edgeConsistentAt_update_of_not_incident hs ht (Function.update x j t) s

/-- Local solvability at `j` is untouched by overwriting the non-adjacent
    `i`. -/
theorem locallySolvable_update_of_nonadjacent {i j : C.Patch} (hij : i ≠ j)
    (hna : Nonadjacent C i j) (x : Records C) (s : C.State i) :
    LocallySolvable j (Function.update x i s) ↔ LocallySolvable j x :=
  exists_congr fun t => solvesAt_update_of_nonadjacent hij hna x s t

private theorem choose_eq_of_pred_iff' {α : Sort*} {p q : α → Prop}
    (hpq : ∀ a, p a ↔ q a) (hp : ∃ a, p a) (hq : ∃ a, q a) :
    Classical.choose hp = Classical.choose hq := by
  have hh : p = q := funext fun a => propext (hpq a)
  subst hh
  rfl

/-- **Pointwise commutation engine.** The full firing condition at `j`, and
    — when it fires — the classically chosen repaired state, are untouched
    by overwriting the non-adjacent `i`: the move at `j` commutes with any
    update at `i`. -/
theorem localRepair_update_of_nonadjacent {i j : C.Patch} (hij : i ≠ j)
    (hna : Nonadjacent C i j) (x : Records C) (s : C.State i) :
    localRepair C j (Function.update x i s) =
      Function.update (localRepair C j x) i s := by
  by_cases hj : LocalTrigger j x ∧ LocallySolvable j x
  · have hj' : LocalTrigger j (Function.update x i s) ∧
        LocallySolvable j (Function.update x i s) :=
      ⟨(localTrigger_update_of_nonadjacent hna x s).mpr hj.1,
        (locallySolvable_update_of_nonadjacent hij hna x s).mpr hj.2⟩
    rw [localRepair_of_fire C j _ hj', localRepair_of_fire C j x hj]
    have hchoose : Classical.choose hj'.2 = Classical.choose hj.2 :=
      choose_eq_of_pred_iff' (solvesAt_update_of_nonadjacent hij hna x s) hj'.2 hj.2
    rw [hchoose, Function.update_comm hij]
  · have hj' : ¬ (LocalTrigger j (Function.update x i s) ∧
        LocallySolvable j (Function.update x i s)) := fun hc =>
      hj ⟨(localTrigger_update_of_nonadjacent hna x s).mp hc.1,
        (locallySolvable_update_of_nonadjacent hij hna x s).mp hc.2⟩
    rw [localRepair_of_quiescent C j _ hj', localRepair_of_quiescent C j x hj]

/-- **THEOREM (#517.1, the conditional diamond).** Non-adjacent repair sites
    commute on the nose for the constructed operator. Adjacent sites
    provably need not (`demoCarrier_repairs_dont_commute`), so this
    condition is sharp: the paper's `K ≠ L` diamond is exactly the
    non-interacting-component case, and conflict-component merging is a
    genuine additional hypothesis, not a bookkeeping detail. -/
theorem localRepair_comm_of_nonadjacent {i j : C.Patch} (hij : i ≠ j)
    (hna : Nonadjacent C i j) (x : Records C) :
    localRepair C i (localRepair C j x) = localRepair C j (localRepair C i x) := by
  by_cases hj : LocalTrigger j x ∧ LocallySolvable j x
  · rw [localRepair_of_fire C j x hj,
      localRepair_update_of_nonadjacent (Ne.symm hij) hna.symm x (Classical.choose hj.2)]
    by_cases hi : LocalTrigger i x ∧ LocallySolvable i x
    · rw [localRepair_of_fire C i x hi,
        localRepair_update_of_nonadjacent hij hna x (Classical.choose hi.2),
        localRepair_of_fire C j x hj,
        Function.update_comm hij]
    · rw [localRepair_of_quiescent C i x hi, localRepair_of_fire C j x hj]
  · rw [localRepair_of_quiescent C j x hj]
    by_cases hi : LocalTrigger i x ∧ LocallySolvable i x
    · rw [localRepair_of_fire C i x hi,
        localRepair_update_of_nonadjacent hij hna x (Classical.choose hi.2),
        localRepair_of_quiescent C j x hj]
    · rw [localRepair_of_quiescent C i x hi, localRepair_of_quiescent C j x hj]

/-- The one-step diamond, packaged as joinability of the two orders from a
    common record: both interleavings of two non-adjacent moves land on the
    same aggregate record. -/
theorem diamond_of_nonadjacent {i j : C.Patch} (hij : i ≠ j)
    (hna : Nonadjacent C i j) (x : Records C) :
    ∃ w : Records C,
      w = localRepair C i (localRepair C j x) ∧
      w = localRepair C j (localRepair C i x) :=
  ⟨localRepair C i (localRepair C j x), rfl,
    localRepair_comm_of_nonadjacent hij hna x⟩

end Diamond

/-! ### Axiom audit — the conditional diamond is admission-free. -/
#print axioms localRepair_comm_of_nonadjacent
#print axioms diamond_of_nonadjacent
#print axioms localRepair_update_of_nonadjacent

end OPH
