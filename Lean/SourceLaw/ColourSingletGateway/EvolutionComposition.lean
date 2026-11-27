import SourceLaw.ColourSingletGateway.UnitaryEvolution

/-!
Exact time composition for one fixed finite complex matrix. Hermiticity is
required only to identify reverse time with conjugate transpose. These results
include empty index types. They assert no time-dependent or physical model.
-/

namespace SourceLaw.ColourSingletGateway.EvolutionComposition

open UnitaryEvolution
open scoped Matrix.Norms.L2Operator

noncomputable section

variable {n m : Type*} [Fintype n] [DecidableEq n]

/-- The time-scaled generators commute because both are scalar multiples of H. -/
theorem commute_Z (H : Matrix n n ℂ) (s t : ℝ) : Commute (Z H s) (Z H t) := by
  exact ((Commute.refl H).smul_left _).smul_right _

/-- Exact evolution adds real time intervals for one fixed generator. -/
theorem U_add (H : Matrix n n ℂ) (s t : ℝ) : U H (s + t) = U H s * U H t := by
  letI : NormedAlgebra ℚ (Matrix n n ℂ) := .restrictScalars ℚ ℂ _
  have hz : Z H (s + t) = Z H s + Z H t := by
    simp [Z, Complex.ofReal_add, mul_add, add_smul]
  unfold U
  rw [hz]
  exact NormedSpace.exp_add_of_commute (commute_Z H s t)

/-- Reverse time is a left inverse without a Hermitian premise. -/
theorem U_neg_mul (H : Matrix n n ℂ) (t : ℝ) : U H (-t) * U H t = 1 := by
  rw [← U_add, neg_add_cancel, U_time_zero]

/-- Reverse time is a right inverse without a Hermitian premise. -/
theorem U_mul_neg (H : Matrix n n ℂ) (t : ℝ) : U H t * U H (-t) = 1 := by
  rw [← U_add, add_neg_cancel, U_time_zero]

/-- For a Hermitian generator, reverse time is conjugate transpose. -/
theorem U_neg_eq_conjTranspose (H : Matrix n n ℂ) (hH : H.IsHermitian) (t : ℝ) :
    U H (-t) = (U H t).conjTranspose := by
  calc
    U H (-t) = (U H t).conjTranspose * (U H t * U H (-t)) := by
      rw [← Matrix.mul_assoc, conjTranspose_mul_self H hH t, Matrix.one_mul]
    _ = (U H t).conjTranspose := by rw [U_mul_neg, Matrix.mul_one]

/-- Two successive intervals act on every rectangular state by their sum. -/
theorem successive_state (H : Matrix n n ℂ) (S : Matrix n m ℂ) (s t : ℝ) :
    U H s * (U H t * S) = U H (s + t) * S := by
  rw [← Matrix.mul_assoc, ← U_add]

/-- Reverse time restores every rectangular state. -/
theorem reverse_time_state (H : Matrix n n ℂ) (S : Matrix n m ℂ) (t : ℝ) :
    U H (-t) * (U H t * S) = S := by
  rw [← Matrix.mul_assoc, U_neg_mul, Matrix.one_mul]

/-- The other order also restores every rectangular state. -/
theorem forward_time_state (H : Matrix n n ℂ) (S : Matrix n m ℂ) (t : ℝ) :
    U H t * (U H (-t) * S) = S := by
  rw [← Matrix.mul_assoc, U_mul_neg, Matrix.one_mul]

/- Kernel-checked finite cases. -/
example (H : Matrix (Fin 2) (Fin 2) ℂ) (S : Matrix (Fin 2) (Fin 1) ℂ) :
    U H 0 * (U H 0 * S) = S := by
  simp [U_time_zero]

example (H : Matrix (Fin 2) (Fin 2) ℂ) (S : Matrix (Fin 2) (Fin 1) ℂ) :
    U H (-3) * (U H 3 * S) = S := reverse_time_state H S 3

example (s t : ℝ) (S : Matrix (Fin 2) (Fin 1) ℂ) :
    U (0 : Matrix (Fin 2) (Fin 2) ℂ) s * (U 0 t * S) = S := by
  simp [U_zero]

example (H : Matrix (Fin 0) (Fin 0) ℂ) (s t : ℝ) :
    U H (s + t) = U H s * U H t := U_add H s t

private def diagonalH : Matrix (Fin 2) (Fin 2) ℂ := Matrix.diagonal ![1, 2]

private theorem diagonalH_hermitian : diagonalH.IsHermitian := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [diagonalH, Matrix.conjTranspose_apply]

private theorem diagonalH_nonzero : diagonalH ≠ 0 := by
  intro h
  have h00 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℂ => M 0 0) h
  norm_num [diagonalH] at h00

-- The unchanged acceptance also checks interval order and the sum sign.
example (S : Matrix (Fin 2) (Fin 1) ℂ) :
    U diagonalH 2 * (U diagonalH 3 * S) = U diagonalH (2 + 3) * S :=
  successive_state diagonalH S 2 3

example : U diagonalH (-3) = (U diagonalH 3).conjTranspose :=
  U_neg_eq_conjTranspose diagonalH diagonalH_hermitian 3

-- A second Hermitian generator need not commute with the first.
private def swapH : Matrix (Fin 2) (Fin 2) ℂ := !![0, 1; 1, 0]

private theorem swapH_hermitian : swapH.IsHermitian := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [swapH, Matrix.conjTranspose_apply]

/-- Two finite Hermitian matrices can fail the one-generator commutation step. -/
theorem two_generator_noncommute : ¬ Commute diagonalH swapH := by
  intro h
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℂ => M 0 1) h.eq
  norm_num [diagonalH, swapH, Matrix.mul_apply, Fin.sum_univ_two] at h01

/-- The sum with a distinct generator need not commute with its first term. -/
theorem sum_generator_noncommute : ¬ Commute diagonalH (diagonalH + swapH) := by
  intro h
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℂ => M 0 1) h.eq
  norm_num [diagonalH, swapH, Matrix.mul_apply, Fin.sum_univ_two] at h01

end

#print axioms commute_Z
#print axioms U_add
#print axioms U_neg_mul
#print axioms U_mul_neg
#print axioms U_neg_eq_conjTranspose
#print axioms successive_state
#print axioms reverse_time_state
#print axioms forward_time_state
#print axioms diagonalH_hermitian
#print axioms diagonalH_nonzero
#print axioms swapH_hermitian
#print axioms two_generator_noncommute
#print axioms sum_generator_noncommute

end SourceLaw.ColourSingletGateway.EvolutionComposition
