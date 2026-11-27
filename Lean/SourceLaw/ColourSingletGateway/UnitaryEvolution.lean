import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.Analysis.Normed.Algebra.Exponential
import Mathlib.LinearAlgebra.Matrix.Hermitian

/-!
Exact evolution for a finite Hermitian complex matrix. Matrix norms are induced
Euclidean operator norms. The time parameter is any real number.
-/

namespace SourceLaw.ColourSingletGateway.UnitaryEvolution

open scoped Matrix.Norms.L2Operator

noncomputable section

variable {n m : Type*} [Fintype n] [DecidableEq n] [Fintype m] [DecidableEq m]

/-- The skew adjoint generator at real time t. -/
def Z (H : Matrix n n ℂ) (t : ℝ) : Matrix n n ℂ :=
  ((-Complex.I) * (t : ℂ)) • H

/-- Exact matrix evolution. -/
def U (H : Matrix n n ℂ) (t : ℝ) : Matrix n n ℂ :=
  NormedSpace.exp (Z H t)

omit [Fintype n] [DecidableEq n] in
/-- Hermiticity makes the generator skew adjoint for every real time. -/
theorem skewAdjoint_Z (H : Matrix n n ℂ) (hH : H.IsHermitian) (t : ℝ) :
    Z H t ∈ skewAdjoint (Matrix n n ℂ) := by
  rw [skewAdjoint.mem_iff]
  simp [Z, star_smul, hH.isSelfAdjoint.star_eq, neg_smul]

/-- Exact Hermitian evolution is unitary, including in dimension zero. -/
theorem unitary_exact (H : Matrix n n ℂ) (hH : H.IsHermitian) (t : ℝ) :
    U H t ∈ unitary (Matrix n n ℂ) := by
  letI : NormedAlgebra ℚ (Matrix n n ℂ) := .restrictScalars ℚ ℂ _
  exact NormedSpace.exp_mem_unitary_of_mem_skewAdjoint (skewAdjoint_Z H hH t)

/-- Conjugate transpose is a left inverse of the exact evolution. -/
theorem conjTranspose_mul_self (H : Matrix n n ℂ) (hH : H.IsHermitian) (t : ℝ) :
    (U H t).conjTranspose * U H t = 1 :=
  Unitary.star_mul_self_of_mem (unitary_exact H hH t)

/-- A unitary matrix has operator norm one on a nonempty index type. -/
theorem norm_U [Nonempty n] (H : Matrix n n ℂ) (hH : H.IsHermitian) (t : ℝ) :
    ‖U H t‖ = 1 :=
  CStarRing.norm_of_mem_unitary (unitary_exact H hH t)

/-- Left multiplication preserves the norm of every rectangular state. -/
theorem norm_U_mul [Nonempty n] (H : Matrix n n ℂ) (hH : H.IsHermitian)
    (S : Matrix n m ℂ) (t : ℝ) : ‖U H t * S‖ = ‖S‖ := by
  have hi : (U H t).conjTranspose * (U H t * S) = S := by
    rw [← Matrix.mul_assoc, conjTranspose_mul_self H hH t, Matrix.one_mul]
  apply le_antisymm
  · calc
      _ ≤ ‖U H t‖ * ‖S‖ := Matrix.l2_opNorm_mul _ _
      _ = ‖S‖ := by rw [norm_U H hH t, one_mul]
  · calc
      ‖S‖ = ‖(U H t).conjTranspose * (U H t * S)‖ := congrArg norm hi.symm
      _ ≤ ‖(U H t).conjTranspose‖ * ‖U H t * S‖ := Matrix.l2_opNorm_mul _ _
      _ = ‖U H t * S‖ := by
        rw [Matrix.l2_opNorm_conjTranspose, norm_U H hH t, one_mul]

/-- A rectangular state contraction stays a contraction at every real time. -/
theorem norm_U_mul_le_one [Nonempty n] (H : Matrix n n ℂ) (hH : H.IsHermitian)
    (S : Matrix n m ℂ) (hS : ‖S‖ ≤ 1) (t : ℝ) : ‖U H t * S‖ ≤ 1 := by
  rw [norm_U_mul H hH S t]
  exact hS

/-- Exact evolution depends continuously on real time. -/
theorem continuous_U (H : Matrix n n ℂ) : Continuous (U H) := by
  letI : NormedAlgebra ℚ (Matrix n n ℂ) := .restrictScalars ℚ ℂ _
  apply NormedSpace.exp_continuous.comp
  exact (continuous_const.mul Complex.continuous_ofReal).smul continuous_const

omit [Fintype m] [DecidableEq m] in
/-- A fixed rectangular state evolves continuously. -/
theorem continuous_U_mul (H : Matrix n n ℂ) (S : Matrix n m ℂ) :
    Continuous (fun t : ℝ => U H t * S) := by
  exact (continuous_U H).matrix_mul continuous_const

/-- The zero generator gives the identity at every real time. -/
theorem U_zero (t : ℝ) : U (0 : Matrix n n ℂ) t = 1 := by
  simp [U, Z]

/-- Evolution starts at the identity. -/
theorem U_time_zero (H : Matrix n n ℂ) : U H 0 = 1 := by
  simp [U, Z]

/-- Matrices with no rows have norm zero. -/
theorem norm_U_of_isEmpty [IsEmpty n] (H : Matrix n n ℂ) (t : ℝ) :
    ‖U H t‖ = 0 := by
  have h : U H t = 0 := Subsingleton.elim _ _
  rw [h, norm_zero]

end

end SourceLaw.ColourSingletGateway.UnitaryEvolution
