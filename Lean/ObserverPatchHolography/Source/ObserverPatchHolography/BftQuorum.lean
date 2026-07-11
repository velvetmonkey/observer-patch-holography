import Mathlib

/-!
# Issue #517.3 — BFT same-view safety, as a clean Lean theorem

Obligation 3 of issue #517: the appendix's P1–P3 argument proves same-view
non-conflict only; either add a prepared/locked-certificate view-change rule
(P4) with proof, or **restrict the theorem**. This module delivers the
restricted theorem, machine-checked:

* `quorum_overlap_honest` — the finite counting core (appendix clause
  "OPH quorum overlap" with the classical exact sizing `q = 2f+1`,
  `n ≤ 3f+1`): any two quorums of size `≥ 2f+1` over at most `3f+1` nodes
  with at most `f` faults share an honest member. Inclusion–exclusion plus
  a pigeonhole step; nothing else.
* `same_view_agreement` — the abstract safety core: if an honest node votes
  for at most one value (P1, stated for honest nodes only — Byzantine nodes
  may equivocate freely) and two quorum certificates (P2) share an honest
  member, the certified values coincide.
* `same_view_safety` — the two combined: under the exact sizing, two
  same-view quorum certificates cannot certify different values.

## Faithfulness notes

* Votes are modelled as a relation `voted : Node → Value → Prop`, so faulty
  nodes CAN sign contradictory votes — `P1` constrains honest nodes only.
  Modelling votes as a function would smuggle one-vote-per-view for
  Byzantine nodes too, silently strengthening the theorem.
* The appendix's strong-quorum-connectivity clause (A4) concerns vote
  *propagation* (message reachability inside a quorum); safety as stated
  here takes the two certificates as given, so A4 does not enter. It is a
  liveness/collection assumption, not part of the same-view safety core.

## Honest stop (cross-view, P4)

Cross-view safety is **not** claimed. It genuinely requires a
prepared/locked-certificate view-change rule (P4) that the paper has not
yet adopted; formalising a rule of our own choosing and proving it safe
would be protocol *design* on the paper's behalf, not an audit receipt —
the theorem statement itself (which P4? locking on prepare or on commit?
unlock on higher certificate?) is the open editorial decision flagged by
#517. Until the paper states P4, the machine-checked story is exactly the
restricted theorem below.

No `sorry`, no `native_decide`, no new axiom.
-/

namespace OPH
namespace BftQuorum

variable {Node Value : Type}

/-- **Quorum-overlap counting core** (classical exact sizing). Over at most
    `3f+1` nodes with at most `f` faulty, any two quorums of size at least
    `2f+1` share a non-faulty member. -/
theorem quorum_overlap_honest [Fintype Node] [DecidableEq Node]
    (Faulty : Finset Node) {f : ℕ}
    (hf : Faulty.card ≤ f) (hn : Fintype.card Node ≤ 3 * f + 1)
    {Q₁ Q₂ : Finset Node}
    (h₁ : 2 * f + 1 ≤ Q₁.card) (h₂ : 2 * f + 1 ≤ Q₂.card) :
    ∃ n ∈ Q₁ ∩ Q₂, n ∉ Faulty := by
  by_contra hno
  push_neg at hno
  have hsub : Q₁ ∩ Q₂ ⊆ Faulty := fun n hn' => hno n hn'
  have hle : (Q₁ ∩ Q₂).card ≤ Faulty.card := Finset.card_le_card hsub
  have hue : (Q₁ ∪ Q₂).card + (Q₁ ∩ Q₂).card = Q₁.card + Q₂.card :=
    Finset.card_union_add_card_inter Q₁ Q₂
  have hu : (Q₁ ∪ Q₂).card ≤ Fintype.card Node := Finset.card_le_univ _
  omega

/-- **Abstract same-view agreement.** `P1` (one vote per view, for honest
    nodes only — Byzantine nodes may equivocate) plus two `P2`-style quorum
    certificates sharing an honest member force equal certified values. -/
theorem same_view_agreement [DecidableEq Node]
    (voted : Node → Value → Prop) (Honest : Node → Prop)
    (P1 : ∀ n, Honest n → ∀ v w, voted n v → voted n w → v = w)
    {Q₁ Q₂ : Finset Node} {s₁ s₂ : Value}
    (hoverlap : ∃ n ∈ Q₁ ∩ Q₂, Honest n)
    (hc₁ : ∀ n ∈ Q₁, voted n s₁) (hc₂ : ∀ n ∈ Q₂, voted n s₂) :
    s₁ = s₂ := by
  obtain ⟨n, hmem, hh⟩ := hoverlap
  rw [Finset.mem_inter] at hmem
  exact P1 n hh s₁ s₂ (hc₁ n hmem.1) (hc₂ n hmem.2)

/-- **THEOREM (#517.3, restricted form) — same-view safety.** Under the
    classical exact sizing (`n ≤ 3f+1`, quorums of size `≥ 2f+1`, at most
    `f` faults), two same-view quorum certificates cannot certify different
    values. This is the machine-checked content of the appendix's P1–P3
    safety argument; cross-view safety needs a P4 view-change rule the
    paper has not yet stated (see module header). -/
theorem same_view_safety [Fintype Node] [DecidableEq Node]
    (voted : Node → Value → Prop) (Faulty : Finset Node) {f : ℕ}
    (hf : Faulty.card ≤ f) (hn : Fintype.card Node ≤ 3 * f + 1)
    (P1 : ∀ n, n ∉ Faulty → ∀ v w, voted n v → voted n w → v = w)
    {Q₁ Q₂ : Finset Node} {s₁ s₂ : Value}
    (h₁ : 2 * f + 1 ≤ Q₁.card) (h₂ : 2 * f + 1 ≤ Q₂.card)
    (hc₁ : ∀ n ∈ Q₁, voted n s₁) (hc₂ : ∀ n ∈ Q₂, voted n s₂) :
    s₁ = s₂ := by
  obtain ⟨n, hmem, hh⟩ := quorum_overlap_honest Faulty hf hn h₁ h₂
  rw [Finset.mem_inter] at hmem
  exact P1 n hh s₁ s₂ (hc₁ n hmem.1) (hc₂ n hmem.2)

/-- **Sharpness of the sizing** (the counting really is needed): with quorum
    threshold `2f` instead of `2f+1` the overlap can be all-faulty. Witness:
    `f = 1`, four nodes `Fin 4`, quorums `{0,1}` and `{1,2}`, faulty `{1}` —
    both quorums have size `2f = 2`, their overlap is exactly the faulty
    node. So the honest-overlap conclusion fails for the weakened threshold,
    and equivocation by the shared faulty node can then certify two values
    in one view. -/
theorem quorum_overlap_honest_sharp :
    ∃ (Faulty Q₁ Q₂ : Finset (Fin 4)),
      Faulty.card ≤ 1 ∧
      2 * 1 ≤ Q₁.card ∧ 2 * 1 ≤ Q₂.card ∧
      ¬ ∃ n ∈ Q₁ ∩ Q₂, n ∉ Faulty := by
  refine ⟨{1}, {0, 1}, {1, 2}, ?_, ?_, ?_, ?_⟩
  · decide
  · decide
  · decide
  · decide

/-! ### Axiom audit — the restricted BFT safety layer is admission-free. -/
#print axioms quorum_overlap_honest
#print axioms same_view_agreement
#print axioms same_view_safety
#print axioms quorum_overlap_honest_sharp

end BftQuorum
end OPH
