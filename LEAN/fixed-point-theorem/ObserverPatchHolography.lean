import Mathlib

/-!
# Fixed-Point Reality and Observer Repair (Observer-Patch Holography)

We formalize claims about repair operators, fixed points, and confluence
in the context of observer-record configurations.

## Setup

Let `X` be a type representing observer-record configurations. We fix:
- A repair operator `T : X → X`
- A mismatch potential `Φ : X → ℝ≥0` measuring overlap inconsistencies
- `T` satisfies a descent contract: `Φ(T x) ≤ Φ x`

The **public world** `W` is the terminal normal form under accepted repair,
quotiented by gauge equivalence. We show:

1. **Claim 1**: The normal form is a fixed point of `T`.
2. **Claim 2 (Newman's Lemma)**: Local confluence + termination ⟹ confluence,
   giving uniqueness of normal forms (schedule-independence).
3. **Corollary**: A stable world cannot carry unresolved contradictions.

The repair operator `T` can be understood as a Frobenius projection onto the
convex set `C` of consistent configurations, where `T` is idempotent on `C`
and contractive outside it.
-/

open Function Relation

variable {X : Type*}

/-! ## Abstract Rewriting System -/

/-- A relation `r` is terminating if there are no infinite forward chains
    `x₀ → x₁ → x₂ → ⋯`. Formally, `WellFounded (flip r)` where `r x y`
    means "`x` rewrites to `y`". -/
def Terminating (r : X → X → Prop) : Prop := WellFounded (flip r)

/-- A relation is locally confluent if any two one-step rewrites from the same source
    can be joined by multi-step rewrites. -/
def LocallyConfluent (r : X → X → Prop) : Prop :=
  ∀ x y z, r x y → r x z → ∃ w, ReflTransGen r y w ∧ ReflTransGen r z w

/-- A relation is confluent (Church–Rosser) if any two multi-step rewrites from the
    same source can be joined. -/
def Confluent (r : X → X → Prop) : Prop :=
  ∀ x y z, ReflTransGen r x y → ReflTransGen r x z →
    ∃ w, ReflTransGen r y w ∧ ReflTransGen r z w

/-- A normal form is an element with no successors under `r`. -/
def IsNormalForm (r : X → X → Prop) (x : X) : Prop := ∀ y, ¬r x y

/-- `x` reduces to normal form `y`: `x →* y` and `y` is a normal form. -/
def ReducesToNF (r : X → X → Prop) (x y : X) : Prop :=
  ReflTransGen r x y ∧ IsNormalForm r y

/-! ## Claim 2: Newman's Lemma (Confluence) -/

/-
**Newman's Lemma**: A terminating, locally confluent relation is confluent.
This is the key result ensuring that the fixed point / normal form is independent
of the order in which repairs are applied.
-/
theorem newman_lemma (r : X → X → Prop)
    (hterm : Terminating r) (hlc : LocallyConfluent r) :
    Confluent r := by
      -- By well-founded induction on $x$ using $hterm$.
      have h_wf_ind : ∀ x, ∀ y z, ReflTransGen r x y → ReflTransGen r x z → ∃ w, ReflTransGen r y w ∧ ReflTransGen r z w := by
        intro x;
        induction' x using hterm.induction with x ih;
        intro y z hy hz
        by_cases hxy : y = x;
        · aesop;
        · by_cases hxz : z = x;
          · exact ⟨ y, by aesop ⟩;
          · -- Since $y \neq x$ and $z \neq x$, we can apply the induction hypothesis to $y$ and $z$.
            obtain ⟨y', hy'⟩ : ∃ y', r x y' ∧ ReflTransGen r y' y := by
              have := hy.cases_head;
              tauto
            obtain ⟨z', hz'⟩ : ∃ z', r x z' ∧ ReflTransGen r z' z := by
              have := hz.cases_head; aesop;
            obtain ⟨ w, hw₁, hw₂ ⟩ := hlc x y' z' hy'.1 hz'.1;
            obtain ⟨ u, hu₁, hu₂ ⟩ := ih y' hy'.1 y w hy'.2 hw₁;
            obtain ⟨ v, hv₁, hv₂ ⟩ := ih z' hz'.1 z u hz'.2 ( hw₂.trans hu₂ );
            exact ⟨ v, hu₁.trans hv₂, hv₁ ⟩;
      exact h_wf_ind

/-
Uniqueness of normal forms follows from confluence: if `x` reduces to
    normal forms `y` and `z`, then `y = z`.
-/
theorem unique_normal_form (r : X → X → Prop) (hconf : Confluent r)
    {x y z : X} (hy : ReducesToNF r x y) (hz : ReducesToNF r x z) : y = z := by
      obtain ⟨ w, hw₁, hw₂ ⟩ := hconf x y z hy.1 hz.1;
      -- Since $y$ is a normal form, any rewrite of $y$ must be $y$ itself.
      have hy_normal : ∀ w, ReflTransGen r y w → y = w := by
        intro w hw; induction hw <;> simp_all +decide [ ReducesToNF ] ;
        exact False.elim ( hy.2 _ ‹_› );
      have hz_normal : ∀ w, ReflTransGen r z w → z = w := by
        intro w hw; induction hw <;> simp_all +decide [ ReducesToNF ] ;
        exact False.elim ( hz.2 _ ‹_› );
      rw [ hy_normal w hw₁, hz_normal w hw₂ ]

/-- **Claim 2 (full)**: In a terminating, locally confluent system,
    normal forms are unique (schedule-independent). -/
theorem claim2_newman_unique_nf (r : X → X → Prop)
    (hterm : Terminating r) (hlc : LocallyConfluent r)
    {x y z : X} (hy : ReducesToNF r x y) (hz : ReducesToNF r x z) : y = z :=
  unique_normal_form r (newman_lemma r hterm hlc) hy hz

/-! ## Deterministic Repair Operator -/

section DeterministicRepair

variable (T : X → X)

/-- The one-step rewriting relation induced by `T`:
    `x` steps to `T x` precisely when `x` is not already a fixed point. -/
def stepRel (T : X → X) (x y : X) : Prop := y = T x ∧ T x ≠ x

/-! ### Claim 1: Fixed-point reading of reality -/

/-
**Claim 1**: A normal form of the `T`-induced rewriting is a fixed point of `T`.
-/
theorem claim1_nf_is_fixedPt (w : X) (hnf : IsNormalForm (stepRel T) w) :
    IsFixedPt T w := by
      exact Classical.not_not.1 fun h => hnf _ ⟨ rfl, h ⟩

/-
If `T` has a descent potential `Φ : X → ℕ` that strictly decreases on non-fixed-points,
    then the induced rewriting relation is terminating.
-/
theorem descent_terminating
    (Φ : X → ℕ)
    (hdesc : ∀ x, T x ≠ x → Φ (T x) < Φ x) :
    Terminating (stepRel T) := by
      refine' ⟨ fun x => _ ⟩;
      have h_wf : WellFounded (fun x y : X => stepRel T y x) := by
        refine' ⟨ fun x => _ ⟩;
        induction' n : Φ x using Nat.strong_induction_on with n ih generalizing x;
        refine' Acc.intro x fun y hy => _;
        cases hy ; aesop;
      exact h_wf.apply x

/-
Local confluence is automatic for a deterministic operator:
    there is at most one successor, so the diamond condition is trivially satisfied.
-/
theorem deterministic_locally_confluent :
    LocallyConfluent (stepRel T) := by
      intro x y z hxy hxz;
      cases hxy ; cases hxz ; aesop

/-- **Claim 1 (full)**: For a terminating deterministic repair operator,
    the normal form is a fixed point of `T` and is unique (schedule-independent). -/
theorem claim1_full
    (Φ : X → ℕ)
    (hdesc : ∀ x, T x ≠ x → Φ (T x) < Φ x)
    {x y z : X}
    (hy : ReducesToNF (stepRel T) x y)
    (hz : ReducesToNF (stepRel T) x z) :
    y = z ∧ IsFixedPt T y :=
  ⟨claim2_newman_unique_nf _ (descent_terminating T Φ hdesc) (deterministic_locally_confluent T) hy hz,
   claim1_nf_is_fixedPt T y hy.2⟩

end DeterministicRepair

/-! ## Corollary: Stability requires complete repair -/

/-
**Corollary**: A fixed point of `T` must have zero mismatch potential.
If `Φ x > 0` implies `T x ≠ x` (positive mismatch triggers repair),
then any fixed point `w` satisfies `Φ w = 0`.

A world cannot be finally stable while its observers carry unresolved
contradictions or permanently falsified records.
-/
theorem corollary_complete_repair
    (T : X → X) (Φ : X → NNReal)
    (hrepair : ∀ x, Φ x > 0 → T x ≠ x)
    (w : X) (hfp : IsFixedPt T w) :
    Φ w = 0 := by
      exact le_antisymm ( le_of_not_gt fun h => hrepair w h hfp ) ( zero_le _ )