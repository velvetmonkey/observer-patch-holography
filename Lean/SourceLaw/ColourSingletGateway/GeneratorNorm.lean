import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.Analysis.Complex.Norm
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.Positivity

/-!
Finite Euclidean operator bounds for the graph generator. The graph premises concern
typed matrices. They do not attach runtime bytes or imply a physical conclusion.
-/

namespace SourceLaw.ColourSingletGateway.GeneratorNorm

open scoped BigOperators Matrix

noncomputable section

/-- Absolute row and column sums bound the Euclidean operator norm. -/
theorem row_col_sum_le_three {ι : Type*} [Fintype ι] [DecidableEq ι]
    {𝕜 : Type*} [RCLike 𝕜] (A : Matrix ι ι 𝕜)
    (hrow : ∀ i, ∑ j, ‖A i j‖ ≤ (3 : ℝ))
    (hcol : ∀ j, ∑ i, ‖A i j‖ ≤ (3 : ℝ)) :
    ‖Matrix.toEuclideanCLM (𝕜 := 𝕜) A‖ ≤ 3 := by
  classical
  apply ContinuousLinearMap.opNorm_le_bound _ (by norm_num)
  intro x
  apply (sq_le_sq₀ (norm_nonneg _) (by positivity)).mp
  have hr (i : ι) : ‖(A *ᵥ WithLp.ofLp x) i‖ ^ 2 ≤
      3 * ∑ j, ‖A i j‖ * ‖x j‖ ^ 2 := by
    have ht : ‖(A *ᵥ WithLp.ofLp x) i‖ ≤ ∑ j, ‖A i j‖ * ‖x j‖ := by
      simpa only [Matrix.mulVec, dotProduct, norm_mul] using
        (norm_sum_le Finset.univ (fun j => A i j * x j))
    have hc := Finset.sum_sq_le_sum_mul_sum_of_sq_eq_mul Finset.univ
      (r := fun j => ‖A i j‖ * ‖x j‖)
      (f := fun j => ‖A i j‖) (g := fun j => ‖A i j‖ * ‖x j‖ ^ 2)
      (fun j _ => norm_nonneg _) (fun j _ => by positivity)
      (fun j _ => by ring)
    calc
      _ ≤ (∑ j, ‖A i j‖ * ‖x j‖) ^ 2 :=
        (sq_le_sq₀ (norm_nonneg _) (by positivity)).mpr ht
      _ ≤ (∑ j, ‖A i j‖) * ∑ j, ‖A i j‖ * ‖x j‖ ^ 2 := hc
      _ ≤ _ := mul_le_mul_of_nonneg_right (hrow i) (by positivity)
  calc
    _ = ∑ i, ‖(A *ᵥ WithLp.ofLp x) i‖ ^ 2 := by
      rw [EuclideanSpace.norm_sq_eq]; rfl
    _ ≤ ∑ i, 3 * ∑ j, ‖A i j‖ * ‖x j‖ ^ 2 := Finset.sum_le_sum fun i _ => hr i
    _ = 3 * ∑ j, (∑ i, ‖A i j‖) * ‖x j‖ ^ 2 := by
      rw [← Finset.mul_sum, Finset.sum_comm]
      simp only [Finset.sum_mul]
    _ ≤ 3 * ∑ j, 3 * ‖x j‖ ^ 2 := by
      gcongr with j
      exact hcol j
    _ = (3 * ‖x‖) ^ 2 := by
      simp only [mul_pow, EuclideanSpace.norm_sq_eq, ← Finset.mul_sum]
      ring

/-- Real symmetry supplies the column bound, also for the complex embedding. -/
theorem symmetric_row_sum_le_three {ι : Type*} [Fintype ι] [DecidableEq ι]
    (H : Matrix ι ι ℝ) (hsymm : ∀ i j, H i j = H j i)
    (hrow : ∀ i, ∑ j, |H i j| ≤ (3 : ℝ)) :
    ‖Matrix.toEuclideanCLM (𝕜 := ℝ) H‖ ≤ 3 ∧
    ‖Matrix.toEuclideanCLM (𝕜 := ℂ) (H.map (algebraMap ℝ ℂ))‖ ≤ 3 := by
  have hc (j) : ∑ i, |H i j| ≤ (3 : ℝ) := by
    simpa only [hsymm] using hrow j
  constructor
  · exact row_col_sum_le_three H (by simpa only [Real.norm_eq_abs] using hrow)
      (by simpa only [Real.norm_eq_abs] using hc)
  · apply row_col_sum_le_three
    · simpa only [Matrix.map_apply, Complex.coe_algebraMap, Complex.norm_real,
        Real.norm_eq_abs] using hrow
    · simpa only [Matrix.map_apply, Complex.coe_algebraMap, Complex.norm_real,
        Real.norm_eq_abs] using hc

/-- The degree counts adjacent vertices, including a loop if one is supplied. -/
def degree (adj : Fin 240 → Fin 240 → Bool) (i : Fin 240) : ℕ :=
  ∑ j, if adj i j then 1 else 0

/-- Exact entries of one half of the graph Laplacian minus three times the identity. -/
def generator (adj : Fin 240 → Fin 240 → Bool) : Matrix (Fin 240) (Fin 240) ℝ :=
  fun i j => if i = j then (degree adj i : ℝ) / 2 - 3
    else if adj i j then -1 / 2 else 0

/-- Each absolute row sum is exactly three under the finite degree premise. -/
theorem generator_row_sum (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hdegree : ∀ i, degree adj i ≤ 6) (i) :
    ∑ j, |generator adj i j| = (3 : ℝ) := by
  have hd : (degree adj i : ℝ) ≤ 6 := by exact_mod_cast hdegree i
  have he (j) : |generator adj i j| =
      (if i = j then 3 - (degree adj i : ℝ) / 2 else 0) +
      (if adj i j then (1 : ℝ) / 2 else 0) := by
    by_cases hij : i = j
    · subst j
      simp only [generator, hloop, Bool.false_eq_true, ↓reduceIte, add_zero]
      rw [abs_of_nonpos (by linarith)]
      ring
    · simp only [generator, if_neg hij, zero_add]
      split <;> norm_num
  have hcount : (∑ j, if adj i j then (1 : ℝ) else 0) = degree adj i := by
    simp only [degree, Nat.cast_sum, Nat.cast_ite, Nat.cast_one, Nat.cast_zero]
  simp_rw [he]
  rw [Finset.sum_add_distrib]
  have hh : (∑ j, if adj i j then (1 : ℝ) / 2 else 0) = (degree adj i : ℝ) / 2 := by
    rw [← hcount, Finset.sum_div]
    apply Finset.sum_congr rfl
    intro j _
    split <;> norm_num
  rw [hh, Finset.sum_ite_eq, if_pos (Finset.mem_univ i)]
  ring

/-- Typed graph premises give both real and complex Euclidean bounds. -/
theorem fin240_generator_norm_le_three (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hsymm : ∀ i j, adj i j = adj j i)
    (hdegree : ∀ i, degree adj i ≤ 6) (H : Matrix (Fin 240) (Fin 240) ℝ)
    (hentry : ∀ i j, H i j = if i = j then (degree adj i : ℝ) / 2 - 3
      else if adj i j then -1 / 2 else 0) :
    ‖Matrix.toEuclideanCLM (𝕜 := ℝ) H‖ ≤ 3 ∧
    ‖Matrix.toEuclideanCLM (𝕜 := ℂ) (H.map (algebraMap ℝ ℂ))‖ ≤ 3 := by
  apply symmetric_row_sum_le_three
  · intro i j
    rw [hentry, hentry]
    by_cases h : i = j
    · subst j; rfl
    · simp [h, Ne.symm h, hsymm i j]
  · have he : H = generator adj := Matrix.ext hentry
    rw [he]
    intro i
    exact (generator_row_sum adj hloop hdegree i).le


/-- Add 9/2 to entry (0,0). All other entries retain the graph value. -/
def changedGenerator (adj : Fin 240 → Fin 240 → Bool) : Matrix (Fin 240) (Fin 240) ℝ :=
  fun i j => generator adj i j + if i = 0 ∧ j = 0 then 9 / 2 else 0

theorem changed_entry_only (adj : Fin 240 → Fin 240 → Bool) (i j : Fin 240)
    (h : ¬ (i = 0 ∧ j = 0)) : changedGenerator adj i j = generator adj i j := by
  simp only [changedGenerator, if_neg h, add_zero]

/-- The change preserves real symmetry. -/
theorem changed_generator_symmetric (adj : Fin 240 → Fin 240 → Bool)
    (hsymm : ∀ i j, adj i j = adj j i) :
    ∀ i j, changedGenerator adj i j = changedGenerator adj j i := by
  intro i j
  unfold changedGenerator
  congr 1
  · unfold generator
    by_cases h : i = j
    · subst j; rfl
    · simp only [if_neg h, if_neg (Ne.symm h), hsymm i j]
  · simp only [and_comm]

/-- The original and changed diagonal entries differ by exactly 9/2. -/
theorem changed_diagonal (adj : Fin 240 → Fin 240 → Bool)
    (hd : degree adj 0 = 5) :
    generator adj 0 0 = -(1 / 2 : ℝ) ∧ changedGenerator adj 0 0 = 4 := by
  norm_num [generator, changedGenerator, hd]

/-- The changed column gives a squared unit-vector output of 69/4. -/
theorem changed_column_sq (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hsymm : ∀ i j, adj i j = adj j i)
    (hd : degree adj 0 = 5) :
    ∑ i, |changedGenerator adj i 0| ^ 2 = (69 : ℝ) / 4 := by
  have he (i : Fin 240) : |changedGenerator adj i 0| ^ 2 =
      (if i = 0 then (16 : ℝ) else 0) + (if adj 0 i then (1 : ℝ) / 4 else 0) := by
    by_cases hi : i = 0
    · subst i
      norm_num [changedGenerator, generator, hd, hloop]
    · simp only [changedGenerator, generator, hi, false_and,
        ↓reduceIte, add_zero, zero_add, hsymm i 0]
      split <;> norm_num
  have hc : (∑ i, if adj 0 i then (1 : ℝ) else 0) = 5 := by
    have h : (∑ i, if adj 0 i then (1 : ℝ) else 0) = degree adj 0 := by
      simp only [degree, Nat.cast_sum, Nat.cast_ite, Nat.cast_one, Nat.cast_zero]
    rw [h, hd]; norm_num
  have hh : (∑ i, if adj 0 i then (1 : ℝ) / 4 else 0) = 5 / 4 := by
    rw [← hc, Finset.sum_div]
    apply Finset.sum_congr rfl
    intro i _
    split <;> norm_num
  simp_rw [he]
  rw [Finset.sum_add_distrib, hh, Finset.sum_ite_eq', if_pos (Finset.mem_univ 0)]
  norm_num

/-- Row zero fails the sufficient row condition. This fact alone is no norm lower bound. -/
theorem changed_row_sum (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hd : degree adj 0 = 5) :
    ∑ j, |changedGenerator adj 0 j| = (13 : ℝ) / 2 := by
  have he (j : Fin 240) : |changedGenerator adj 0 j| =
      (if j = 0 then (4 : ℝ) else 0) + (if adj 0 j then (1 : ℝ) / 2 else 0) := by
    by_cases hj : j = 0
    · subst j; norm_num [changedGenerator, generator, hd, hloop]
    · simp only [changedGenerator, generator, if_neg (Ne.symm hj), hj, and_false,
        ↓reduceIte, add_zero, zero_add]
      split <;> norm_num
  have hc : (∑ j, if adj 0 j then (1 : ℝ) else 0) = 5 := by
    have h : (∑ j, if adj 0 j then (1 : ℝ) else 0) = degree adj 0 := by
      simp only [degree, Nat.cast_sum, Nat.cast_ite, Nat.cast_one, Nat.cast_zero]
    rw [h, hd]; norm_num
  have hh : (∑ j, if adj 0 j then (1 : ℝ) / 2 else 0) = 5 / 2 := by
    rw [← hc, Finset.sum_div]
    apply Finset.sum_congr rfl
    intro j _
    split <;> norm_num
  simp_rw [he]
  rw [Finset.sum_add_distrib, hh, Finset.sum_ite_eq', if_pos (Finset.mem_univ 0)]
  norm_num

/-- The false row premise cannot be supplied to the generic norm theorem. -/
theorem changed_row_bound_false (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hd : degree adj 0 = 5) :
    ¬ (∀ i, ∑ j, |changedGenerator adj i j| ≤ (3 : ℝ)) := by
  intro h
  have h0 := h 0
  rw [changed_row_sum adj hloop hd] at h0
  norm_num at h0

/-- The real unit vector detects actual norm failure, separately from row failure. -/
theorem changed_unit_vector (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hsymm : ∀ i j, adj i j = adj j i)
    (hd : degree adj 0 = 5) :
    let e : EuclideanSpace ℝ (Fin 240) := WithLp.toLp 2 (Pi.single 0 1)
    ‖e‖ = 1 ∧
      ‖Matrix.toEuclideanCLM (𝕜 := ℝ) (changedGenerator adj) e‖ ^ 2 = 69 / 4 ∧
      (9 : ℝ) < 69 / 4 := by
  dsimp only
  refine ⟨by simp, ?_, by norm_num⟩
  rw [EuclideanSpace.norm_sq_eq]
  simpa only [Matrix.toEuclideanCLM_toLp, WithLp.ofLp_toLp,
    Matrix.mulVec_single_one, Matrix.col_apply, Real.norm_eq_abs] using
    changed_column_sq adj hloop hsymm hd

/-- The same changed column detects norm failure over the complex scalars. -/
theorem changed_complex_unit_vector (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hsymm : ∀ i j, adj i j = adj j i)
    (hd : degree adj 0 = 5) :
    let e : EuclideanSpace ℂ (Fin 240) := WithLp.toLp 2 (Pi.single 0 1)
    ‖e‖ = 1 ∧
      ‖Matrix.toEuclideanCLM (𝕜 := ℂ)
        ((changedGenerator adj).map (algebraMap ℝ ℂ)) e‖ ^ 2 = 69 / 4 := by
  dsimp only
  refine ⟨by simp, ?_⟩
  rw [EuclideanSpace.norm_sq_eq]
  simpa only [Matrix.toEuclideanCLM_toLp, WithLp.ofLp_toLp,
    Matrix.mulVec_single_one, Matrix.col_apply, Matrix.map_apply,
    Complex.coe_algebraMap, Complex.norm_real, Real.norm_eq_abs] using
    changed_column_sq adj hloop hsymm hd

private theorem norm_gt_three_of_unit_sq {𝕜 E : Type*} [RCLike 𝕜]
    [NormedAddCommGroup E] [NormedSpace 𝕜 E]
      (T : E →L[𝕜] E)
      (e : E) (hu : ‖e‖ = 1)
      (he : ‖T e‖ ^ 2 = 69 / 4) : 3 < ‖T‖ := by
  have ht := T.le_opNorm e
  rw [hu, mul_one] at ht
  by_contra h
  have hb : ‖T e‖ ≤ 3 := ht.trans (le_of_not_gt h)
  have hs := (sq_le_sq₀ (norm_nonneg (T e)) (show (0 : ℝ) ≤ 3 by norm_num)).mpr hb
  rw [he] at hs
  norm_num at hs

/-- Both Euclidean operator norms exceed three for the changed generator. -/
theorem changed_norm_gt_three (adj : Fin 240 → Fin 240 → Bool)
    (hloop : ∀ i, adj i i = false) (hsymm : ∀ i j, adj i j = adj j i)
    (hd : degree adj 0 = 5) :
    3 < ‖Matrix.toEuclideanCLM (𝕜 := ℝ) (changedGenerator adj)‖ ∧
    3 < ‖Matrix.toEuclideanCLM (𝕜 := ℂ)
      ((changedGenerator adj).map (algebraMap ℝ ℂ))‖ := by
  constructor
  · obtain ⟨hu, he, _⟩ := changed_unit_vector adj hloop hsymm hd
    exact norm_gt_three_of_unit_sq (Matrix.toEuclideanCLM (𝕜 := ℝ) (changedGenerator adj))
      (WithLp.toLp 2 (Pi.single 0 1)) hu he
  · obtain ⟨hu, he⟩ := changed_complex_unit_vector adj hloop hsymm hd
    exact norm_gt_three_of_unit_sq (Matrix.toEuclideanCLM (𝕜 := ℂ)
      ((changedGenerator adj).map (algebraMap ℝ ℂ)))
      (WithLp.toLp 2 (Pi.single 0 1)) hu he

/-
A failed row condition alone does not imply a failed Euclidean norm bound.
The symmetric block [[2,2],[2,-2]], padded by zeros, has absolute row sum 4.
Its square is 8 times the identity on its support, so its operator norm is sqrt(8) < 3.
The changed unit-vector theorems supply a separate lower bound for the changed generator.
-/

#print axioms row_col_sum_le_three
#print axioms symmetric_row_sum_le_three
#print axioms generator_row_sum
#print axioms fin240_generator_norm_le_three
#print axioms changed_entry_only
#print axioms changed_generator_symmetric
#print axioms changed_diagonal
#print axioms changed_column_sq
#print axioms changed_row_sum
#print axioms changed_row_bound_false
#print axioms changed_unit_vector
#print axioms changed_complex_unit_vector
#print axioms changed_norm_gt_three

end

end SourceLaw.ColourSingletGateway.GeneratorNorm
