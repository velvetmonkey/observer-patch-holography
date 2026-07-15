import EventAlgebra.Lueders

/-!
# Conditional expectation onto a commutative center

A finite family of pairwise-orthogonal events summing to the identity (a
`CenterPartition`) generates a distinguished commutative subalgebra — the
**center** of the measurement context. This module constructs the
conditional expectation onto (the commutant of) that center, the *pinching*
map

  `centerExpectation part X = ∑ i, Pᵢ X Pᵢ`,

and proves, in the finite quantum setting, the same package that
characterises a classical conditional expectation:

* **existence** — the pinching lands in the commutant of the partition,
  fixes the commutant pointwise, and is idempotent (a projector);
* **state preservation** — it maps states to states;
* **selfadjointness and contractivity** — it is selfadjoint for the trace
  inner product `⟨X, Y⟩ = Tr(Xᴴ Y)`, satisfies the Pythagorean identity,
  and is a squared-`L²` contraction;
* **uniqueness** — it is the only commutant-valued map compatible with the
  trace against every element of the commutant;
* **compatibility with conditioning** — for an event `P` in the center,
  Lüders conditioning commutes with the center expectation (conditioning
  on central events is classical conditioning).

## Tagging convention

As in `EventAlgebra.Basic`: each lemma is tagged **algebra-only** or
**consumes a tracial state** according to whether its content passes
through the trace pairing.
-/

namespace EventAlgebra

open Matrix
open scoped ComplexOrder

variable {n k : ℕ}

/-- A **center partition**: a finite family of pairwise-orthogonal events
summing to the identity. The family generates a commutative subalgebra
(see `CenterPartition.proj_commute`), the distinguished center. -/
structure CenterPartition (n k : ℕ) where
  /-- The orthogonal projections constituting the partition. -/
  proj : Fin k → Matrix (Fin n) (Fin n) ℂ
  /-- Every member of the partition is an event. -/
  isEvent : ∀ i, IsEvent (proj i)
  /-- Distinct members are orthogonal. -/
  orthogonal : ∀ i j, i ≠ j → proj i * proj j = 0
  /-- The partition is complete: the members sum to the sure event. -/
  complete : ∑ i, proj i = 1

namespace CenterPartition

variable (part : CenterPartition n k)

/-- **Algebra-only.** Product formula for partition members:
`Pᵢ Pⱼ = δᵢⱼ Pᵢ`. -/
theorem proj_mul_proj (i j : Fin k) :
    part.proj i * part.proj j = if i = j then part.proj i else 0 := by
  by_cases h : i = j
  · subst h
    simp [(part.isEvent i).2]
  · simp [h, part.orthogonal i j h]

/-- **Algebra-only.** Partition members commute pairwise: the partition
generates a commutative subalgebra (the center). -/
theorem proj_commute (i j : Fin k) :
    part.proj i * part.proj j = part.proj j * part.proj i := by
  by_cases h : i = j
  · rw [h]
  · rw [part.orthogonal i j h, part.orthogonal j i (Ne.symm h)]

end CenterPartition

/-- The **conditional expectation onto the center** determined by a
partition: the pinching map `X ↦ ∑ i, Pᵢ X Pᵢ`. -/
noncomputable def centerExpectation (part : CenterPartition n k)
    (X : Matrix (Fin n) (Fin n) ℂ) : Matrix (Fin n) (Fin n) ℂ :=
  ∑ i, part.proj i * X * part.proj i

variable (part : CenterPartition n k)

/-- **Algebra-only.** Absorption on the right: multiplying the pinching by
a partition member selects the corresponding block. -/
theorem centerExpectation_mul_proj (X : Matrix (Fin n) (Fin n) ℂ)
    (i : Fin k) :
    centerExpectation part X * part.proj i = part.proj i * X * part.proj i := by
  rw [centerExpectation, Finset.sum_mul]
  rw [Finset.sum_eq_single i
    (fun j _ hji => by
      rw [mul_assoc, part.orthogonal j i hji, mul_zero])
    (fun h => absurd (Finset.mem_univ i) h)]
  rw [mul_assoc, (part.isEvent i).2]

/-- **Algebra-only.** Absorption on the left. -/
theorem proj_mul_centerExpectation (X : Matrix (Fin n) (Fin n) ℂ)
    (i : Fin k) :
    part.proj i * centerExpectation part X = part.proj i * X * part.proj i := by
  rw [centerExpectation, Finset.mul_sum]
  rw [Finset.sum_eq_single i
    (fun j _ hji => by
      rw [← mul_assoc, ← mul_assoc, part.orthogonal i j (Ne.symm hji),
        zero_mul, zero_mul])
    (fun h => absurd (Finset.mem_univ i) h)]
  rw [← mul_assoc, ← mul_assoc, (part.isEvent i).2]

/-- **Algebra-only.** The pinching lands in the commutant of the partition:
its output commutes with every partition member. -/
theorem proj_commute_centerExpectation (X : Matrix (Fin n) (Fin n) ℂ)
    (i : Fin k) :
    part.proj i * centerExpectation part X = centerExpectation part X * part.proj i := by
  rw [proj_mul_centerExpectation, centerExpectation_mul_proj]

/-- **Algebra-only.** The pinching fixes the commutant pointwise: any `X`
commuting with every partition member is left unchanged. -/
theorem centerExpectation_fixes {X : Matrix (Fin n) (Fin n) ℂ}
    (h : ∀ i, X * part.proj i = part.proj i * X) :
    centerExpectation part X = X := by
  calc centerExpectation part X = ∑ i, X * part.proj i :=
        Finset.sum_congr rfl fun i _ => by
          rw [← h i, mul_assoc, (part.isEvent i).2]
    _ = X * ∑ i, part.proj i := (Finset.mul_sum _ _ _).symm
    _ = X := by rw [part.complete, mul_one]

/-- **Algebra-only.** The pinching is idempotent: it is a projector onto
the commutant of the center. -/
theorem centerExpectation_idem (X : Matrix (Fin n) (Fin n) ℂ) :
    centerExpectation part (centerExpectation part X) = centerExpectation part X :=
  centerExpectation_fixes part fun i =>
    (proj_commute_centerExpectation part X i).symm

/-- **Algebra-only.** The pinching commutes with conjugate transposition. -/
theorem conjTranspose_centerExpectation (X : Matrix (Fin n) (Fin n) ℂ) :
    (centerExpectation part X)ᴴ = centerExpectation part Xᴴ := by
  rw [centerExpectation, centerExpectation, conjTranspose_sum]
  exact Finset.sum_congr rfl fun i _ => by
    simp only [conjTranspose_mul, (part.isEvent i).1.eq, mul_assoc]

/-- **Consumes a tracial state.** The pinching maps states to states: the
conditional expectation of a density matrix onto the center is a density
matrix. -/
theorem centerExpectation_isState {ρ : Matrix (Fin n) (Fin n) ℂ}
    (hρ : IsState ρ) : IsState (centerExpectation part ρ) := by
  constructor
  · exact posSemidef_sum _ fun i _ => by
      have := hρ.1.mul_mul_conjTranspose_same (part.proj i)
      rwa [(part.isEvent i).1.eq] at this
  · rw [centerExpectation, trace_sum]
    calc ∑ i, (part.proj i * ρ * part.proj i).trace
        = ∑ i, bornWeight ρ (part.proj i) :=
          Finset.sum_congr rfl fun i _ => trace_sandwich (part.isEvent i).2 ρ
      _ = bornWeight ρ (∑ i, part.proj i) := (bornWeight_sum ρ _ _).symm
      _ = 1 := by rw [part.complete, bornWeight_one hρ]

/-- **Consumes a tracial state.** Selfadjointness of the pinching for the
trace inner product `⟨X, Y⟩ = Tr(Xᴴ Y)`. -/
theorem trace_conjTranspose_centerExpectation_mul
    (X Y : Matrix (Fin n) (Fin n) ℂ) :
    ((centerExpectation part X)ᴴ * Y).trace =
      (Xᴴ * centerExpectation part Y).trace := by
  have hterm : ∀ i : Fin k,
      (part.proj i * Xᴴ * part.proj i * Y).trace =
        (Xᴴ * (part.proj i * Y * part.proj i)).trace := by
    intro i
    rw [trace_mul_comm (part.proj i * Xᴴ * part.proj i) Y,
      trace_mul_comm Xᴴ (part.proj i * Y * part.proj i),
      show Y * (part.proj i * Xᴴ * part.proj i) =
        (Y * part.proj i * Xᴴ) * part.proj i by simp only [mul_assoc],
      trace_mul_comm (Y * part.proj i * Xᴴ) (part.proj i)]
    simp only [mul_assoc]
  rw [conjTranspose_centerExpectation, centerExpectation, centerExpectation,
    Finset.sum_mul, Finset.mul_sum, trace_sum, trace_sum]
  exact Finset.sum_congr rfl fun i _ => hterm i

/-- **Consumes a tracial state.** The Pythagorean identity for the
pinching: the squared trace norm splits into the squared norm of the
conditional expectation plus the squared norm of the residual. This is the
quantum counterpart of the classical `L²` energy identity for conditional
expectations. -/
theorem trace_centerExpectation_pythagoras (X : Matrix (Fin n) (Fin n) ℂ) :
    (Xᴴ * X).trace =
      ((centerExpectation part X)ᴴ * centerExpectation part X).trace +
      ((X - centerExpectation part X)ᴴ * (X - centerExpectation part X)).trace := by
  have hTX : ((centerExpectation part X)ᴴ * X).trace =
      (Xᴴ * centerExpectation part X).trace :=
    trace_conjTranspose_centerExpectation_mul part X X
  have hTT : ((centerExpectation part X)ᴴ * centerExpectation part X).trace =
      (Xᴴ * centerExpectation part X).trace := by
    have := trace_conjTranspose_centerExpectation_mul part X
      (centerExpectation part X)
    rwa [centerExpectation_idem part X] at this
  simp only [conjTranspose_sub, sub_mul, mul_sub, trace_sub]
  rw [hTX, hTT]
  ring

/-- **Consumes a tracial state.** Squared-`L²` contractivity of the
pinching for the trace norm: `Tr((𝔼X)ᴴ (𝔼X)) ≤ Tr(Xᴴ X)` in the partial
order of `ℂ`. -/
theorem trace_centerExpectation_contraction (X : Matrix (Fin n) (Fin n) ℂ) :
    ((centerExpectation part X)ᴴ * centerExpectation part X).trace ≤
      (Xᴴ * X).trace := by
  rw [trace_centerExpectation_pythagoras part X]
  exact le_add_of_nonneg_right
    (posSemidef_conjTranspose_mul_self _).trace_nonneg

/-- **Consumes a tracial state.** Trace compatibility: against any element
`C` of the commutant of the partition, the pinching is invisible to the
trace pairing. This is the defining property of a conditional
expectation. -/
theorem trace_centerExpectation_mul_central (X C : Matrix (Fin n) (Fin n) ℂ)
    (hC : ∀ i, C * part.proj i = part.proj i * C) :
    (centerExpectation part X * C).trace = (X * C).trace := by
  have hterm : ∀ i : Fin k,
      ((part.proj i * X * part.proj i) * C).trace =
        (X * (C * part.proj i)).trace := by
    intro i
    rw [trace_mul_comm (part.proj i * X * part.proj i) C,
      show C * (part.proj i * X * part.proj i) =
        (C * part.proj i) * X * part.proj i by simp only [mul_assoc],
      trace_mul_comm ((C * part.proj i) * X) (part.proj i),
      show part.proj i * ((C * part.proj i) * X) =
        ((part.proj i * C) * part.proj i) * X by simp only [mul_assoc],
      ← hC i,
      show ((C * part.proj i) * part.proj i) * X =
        (C * (part.proj i * part.proj i)) * X by simp only [mul_assoc],
      (part.isEvent i).2, trace_mul_comm (C * part.proj i) X]
  have hsum : ∑ i, ((part.proj i * X * part.proj i) * C).trace =
      ∑ i, (X * (C * part.proj i)).trace :=
    Finset.sum_congr rfl fun i _ => hterm i
  rw [centerExpectation, Finset.sum_mul, trace_sum, hsum, ← trace_sum,
    ← Finset.mul_sum, ← Finset.mul_sum, part.complete, mul_one]

/-- **Consumes a tracial state.** Uniqueness of the conditional
expectation: any commutant-valued matrix `Y` that is trace-compatible with
`X` against the whole commutant equals the pinching of `X`. The proof
tests against `C = (Y - 𝔼X)ᴴ` and uses faithfulness of the trace. -/
theorem centerExpectation_unique {X Y : Matrix (Fin n) (Fin n) ℂ}
    (hYcomm : ∀ i, Y * part.proj i = part.proj i * Y)
    (hYtr : ∀ C : Matrix (Fin n) (Fin n) ℂ,
      (∀ i, C * part.proj i = part.proj i * C) → (Y * C).trace = (X * C).trace) :
    Y = centerExpectation part X := by
  set D := Y - centerExpectation part X with hD
  have hDcomm : ∀ i, D * part.proj i = part.proj i * D := by
    intro i
    rw [hD, sub_mul, mul_sub, hYcomm i,
      ← proj_commute_centerExpectation part X i]
  have hDHcomm : ∀ i, Dᴴ * part.proj i = part.proj i * Dᴴ := by
    intro i
    have := congrArg conjTranspose (hDcomm i)
    rw [conjTranspose_mul, conjTranspose_mul, (part.isEvent i).1.eq] at this
    exact this.symm
  have htr0 : (D * Dᴴ).trace = 0 := by
    have h1 : (Y * Dᴴ).trace = (X * Dᴴ).trace := hYtr Dᴴ hDHcomm
    have h2 : (centerExpectation part X * Dᴴ).trace = (X * Dᴴ).trace :=
      trace_centerExpectation_mul_central part X Dᴴ hDHcomm
    rw [hD, sub_mul, trace_sub, h1, h2, sub_self]
  have hD0 : D = 0 := trace_mul_conjTranspose_self_eq_zero_iff.mp htr0
  rw [← sub_eq_zero]
  exact hD0

/-- **Consumes a tracial state.** For an event `P` in the commutant of the
partition, the Born weight is invariant under the center expectation. -/
theorem bornWeight_centerExpectation (ρ P : Matrix (Fin n) (Fin n) ℂ)
    (hPc : ∀ i, P * part.proj i = part.proj i * P) :
    bornWeight (centerExpectation part ρ) P = bornWeight ρ P :=
  trace_centerExpectation_mul_central part ρ P hPc

/-- **Consumes a tracial state.** **Classical conditioning**: for an event
`P` in the commutant of the partition, Lüders conditioning commutes with
the center expectation. Conditioning on central events interacts with the
center exactly as classical conditional probability does. -/
theorem centerExpectation_luedersUpdate (ρ P : Matrix (Fin n) (Fin n) ℂ)
    (hPc : ∀ i, P * part.proj i = part.proj i * P) :
    centerExpectation part (luedersUpdate ρ P) =
      luedersUpdate (centerExpectation part ρ) P := by
  have hsand : ∀ i : Fin k,
      part.proj i * (P * ρ * P) * part.proj i =
        P * (part.proj i * ρ * part.proj i) * P := by
    intro i
    have h1 : part.proj i * (P * ρ * P) * part.proj i =
        (part.proj i * P) * ρ * (P * part.proj i) := by simp only [mul_assoc]
    have h2 : P * (part.proj i * ρ * part.proj i) * P =
        (P * part.proj i) * ρ * (part.proj i * P) := by simp only [mul_assoc]
    rw [h1, h2, hPc i]
  rw [luedersUpdate, luedersUpdate, bornWeight_centerExpectation part ρ P hPc,
    centerExpectation, centerExpectation]
  simp only [mul_smul_comm, smul_mul_assoc]
  rw [← Finset.smul_sum]
  congr 1
  rw [Finset.mul_sum, Finset.sum_mul]
  exact Finset.sum_congr rfl fun i _ => hsand i

-- Axiom audit: each must report only `[propext, Classical.choice, Quot.sound]`.
#print axioms CenterPartition.proj_mul_proj
#print axioms CenterPartition.proj_commute
#print axioms centerExpectation_mul_proj
#print axioms proj_mul_centerExpectation
#print axioms proj_commute_centerExpectation
#print axioms centerExpectation_fixes
#print axioms centerExpectation_idem
#print axioms conjTranspose_centerExpectation
#print axioms centerExpectation_isState
#print axioms trace_conjTranspose_centerExpectation_mul
#print axioms trace_centerExpectation_pythagoras
#print axioms trace_centerExpectation_contraction
#print axioms trace_centerExpectation_mul_central
#print axioms centerExpectation_unique
#print axioms bornWeight_centerExpectation
#print axioms centerExpectation_luedersUpdate

end EventAlgebra
