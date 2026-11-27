import Mathlib.Analysis.Matrix.Order
import Mathlib.Analysis.SpecialFunctions.ContinuousFunctionalCalculus.Rpow.Basic
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Tactic

/-!
# Finite complex PSD density bridge

The factor and trace identities concern nine complex coordinates. The bound
transfer assumes a bound for every factor. It supplies no numerical, analytic,
source-range or physical premise.
-/

namespace SourceLaw.ColourSingletGateway.DensityCore

open scoped Matrix ComplexOrder MatrixOrder ContinuousFunctionalCalculus
open Finset

noncomputable section

abbrev M := Matrix (Fin 9) (Fin 9) ℂ

local instance : ContinuousFunctionalCalculus ℝ M IsSelfAdjoint :=
  Matrix.IsHermitian.instContinuousFunctionalCalculus

local instance : NonUnitalContinuousFunctionalCalculus ℝ M IsSelfAdjoint :=
  ContinuousFunctionalCalculus.toNonUnital

local instance : NonnegSpectrumClass ℝ M := Matrix.instNonnegSpectrumClass

/-- Every PSD matrix has a factor, including zero and singular matrices. -/
theorem exists_factor (tau : M) (hTau : tau.PosSemidef) :
    ∃ B : M, tau = B * B.conjTranspose := by
  refine ⟨CFC.sqrt tau, ?_⟩
  have hs : (CFC.sqrt tau).IsHermitian :=
    (Matrix.nonneg_iff_posSemidef.mp (CFC.sqrt_nonneg tau)).1
  rw [hs.eq]
  exact (CFC.sqrt_mul_sqrt_self tau hTau.nonneg).symm

/-- The sum of the real column quadratic forms. -/
def columnEnergy (E B : M) : ℝ :=
  ∑ j, (∑ i, star (B i j) * (E.mulVec (fun k => B k j)) i).re

/-- The complex trace identity does not require Hermiticity of E. -/
theorem trace_factor (E B : M) :
    Matrix.trace (E * (B * B.conjTranspose)) =
      ∑ j, ∑ i, star (B i j) * (E.mulVec (fun k => B k j)) i := by
  rw [← Matrix.mul_assoc, Matrix.trace_mul_cycle]
  simp only [Matrix.trace, Matrix.diag, Matrix.mul_apply, Matrix.conjTranspose_apply,
    Matrix.mulVec, dotProduct, Finset.sum_mul, Finset.mul_sum, mul_assoc]
  exact Finset.sum_congr rfl (fun _ _ => Finset.sum_comm)

/-- Taking real parts gives the column energy identity. -/
theorem trace_factor_re (E B : M) :
    (Matrix.trace (E * (B * B.conjTranspose))).re = columnEnergy E B := by
  rw [trace_factor]
  simp [columnEnergy]

/-- Transfer an explicit factored bound to every PSD density with W normalization. -/
theorem bound_of_factored (W G A tau : M) (upper : ℝ)
    (H : ∀ B : M, columnEnergy W B = 1 →
      columnEnergy G B ≤ 1 / 1000 → columnEnergy A B ≤ upper)
    (hTau : tau.PosSemidef)
    (hW : (Matrix.trace (W * tau)).re = 1)
    (hG : (Matrix.trace (G * tau)).re ≤ 1 / 1000) :
    (Matrix.trace (A * tau)).re ≤ upper := by
  obtain ⟨B, rfl⟩ := exists_factor tau hTau
  simpa only [trace_factor_re] using H B
    (by simpa only [trace_factor_re] using hW)
    (by simpa only [trace_factor_re] using hG)

private def rankVector : Fin 9 → ℂ :=
  fun i => if i.val = 0 then 3 / 5 else if i.val = 1 then 4 * Complex.I / 5 else 0

private def rankFactor : M := fun i j => if j.val = 0 then rankVector i else 0

private def rankDensity : M := rankFactor * rankFactor.conjTranspose

private theorem zero_control : (0 : M).PosSemidef ∧
    (∃ B : M, (0 : M) = B * B.conjTranspose) ∧
    ∀ E : M, (Matrix.trace (E * (0 : M))).re = 0 := by
  refine ⟨?_, ?_, ?_⟩
  · simpa using Matrix.posSemidef_self_mul_conjTranspose (0 : M)
  · exact exists_factor 0 (by simpa using Matrix.posSemidef_self_mul_conjTranspose (0 : M))
  · intro E; simp

private theorem rank_control : rankDensity.PosSemidef ∧
    Matrix.trace rankDensity = 1 ∧
    rankDensity 0 1 = -(12 * Complex.I / 25) ∧
    rankDensity 1 0 = 12 * Complex.I / 25 ∧
    ∀ E : M, Matrix.trace (E * rankDensity) =
      ∑ i, star (rankVector i) * (E.mulVec rankVector) i := by
  refine ⟨Matrix.posSemidef_self_mul_conjTranspose rankFactor, ?_, ?_, ?_, ?_⟩
  · norm_num [rankDensity, rankFactor, rankVector, Matrix.trace, Matrix.diag,
      Matrix.mul_apply, Matrix.conjTranspose_apply, Fin.sum_univ_succ, map_ofNat, map_div₀, Complex.ext_iff, Complex.conj_ofNat]
  · norm_num [rankDensity, rankFactor, rankVector, Matrix.mul_apply,
      Matrix.conjTranspose_apply, Fin.sum_univ_succ, map_ofNat, map_div₀, Complex.ext_iff, Complex.conj_ofNat]
  · norm_num [rankDensity, rankFactor, rankVector, Matrix.mul_apply,
      Matrix.conjTranspose_apply, Fin.sum_univ_succ, map_ofNat, map_div₀, Complex.ext_iff, Complex.conj_ofNat]
  · intro E
    rw [rankDensity, trace_factor]
    simp [rankFactor, Fin.sum_univ_succ]

private def fullFactor : M := (1 / 3 : ℂ) • (1 : M)

private theorem full_control :
    fullFactor * fullFactor.conjTranspose = (1 / 9 : ℂ) • (1 : M) ∧
    ((1 / 9 : ℂ) • (1 : M)).PosSemidef ∧
    Matrix.trace ((1 / 9 : ℂ) • (1 : M)) = 1 := by
  have hf : fullFactor * fullFactor.conjTranspose = (1 / 9 : ℂ) • (1 : M) := by
    ext i j
    simp [fullFactor, Matrix.mul_apply,
      Matrix.one_apply, smul_eq_mul]
    split_ifs <;> norm_num
  refine ⟨hf, ?_, ?_⟩
  · rw [← hf]; exact Matrix.posSemidef_self_mul_conjTranspose fullFactor
  · norm_num [Matrix.trace, Matrix.diag, Fin.sum_univ_succ, Fin.val_succ]

private def indefinite : M := Matrix.diagonal
  (fun i => if i.val = 0 then -1 else if i.val = 1 then 2 else 0)

private theorem indefinite_not_psd : ¬ indefinite.PosSemidef := by
  intro h
  have h0 := (Matrix.posSemidef_diagonal_iff.mp h) 0
  norm_num [indefinite] at h0

private theorem hermitian_trace_insufficient : indefinite.IsHermitian ∧
    Matrix.trace indefinite = 1 ∧
    ¬ (∃ B : M, indefinite = B * B.conjTranspose) := by
  refine ⟨?_, ?_, ?_⟩
  · apply Matrix.isHermitian_diagonal_iff.mpr
    intro i
    dsimp
    split_ifs <;> simp [IsSelfAdjoint]
  · norm_num [indefinite, Matrix.trace, Matrix.diag, Fin.sum_univ_succ, Fin.val_succ]
  · rintro ⟨B, hB⟩
    exact indefinite_not_psd (hB ▸ Matrix.posSemidef_self_mul_conjTranspose B)

private theorem zero_not_normalized (W : M) :
    (Matrix.trace (W * (0 : M))).re ≠ 1 := by simp

private theorem rank_singular : rankDensity.mulVec (Pi.single 2 1) = 0 := by
  ext i
  simp [rankDensity, rankFactor, rankVector, Matrix.mulVec, dotProduct,
    Matrix.mul_apply, Matrix.conjTranspose_apply, Fin.sum_univ_succ]

private theorem full_trace_control (E : M) :
    Matrix.trace (E * ((1 / 9 : ℂ) • (1 : M))) = Matrix.trace E / 9 := by
  simp [Matrix.mul_smul, Matrix.trace_smul, div_eq_mul_inv, mul_comm]

private theorem full_inverse_control :
    ((1 / 9 : ℂ) • (1 : M)) * ((9 : ℂ) • (1 : M)) = 1 := by
  ext i j
  simp [Matrix.mul_apply, Matrix.one_apply, smul_eq_mul]

#print axioms zero_not_normalized
#print axioms rank_singular
#print axioms full_trace_control
#print axioms full_inverse_control
#print axioms exists_factor
#print axioms trace_factor
#print axioms trace_factor_re
#print axioms bound_of_factored
#print axioms zero_control
#print axioms rank_control
#print axioms full_control
#print axioms indefinite_not_psd
#print axioms hermitian_trace_insufficient

end

end SourceLaw.ColourSingletGateway.DensityCore
