import SourceLaw.ColourSingletGateway.DensityCore
import SourceLaw.ColourSingletGateway.UnitaryEvolution

/-!
# Exact evolution of a finite density

Unitary conjugation preserves PSD and the ordinary complex trace on nine
coordinates, including singular densities. A reader moves by the adjoint
conjugation in the trace identity. A fixed weighted normalization or a fixed
reader bound needs its own premise. Neither follows from ordinary trace one.
This module supplies no source range, fixed data or physical conclusion.
-/

namespace SourceLaw.ColourSingletGateway.DensityEvolution

open UnitaryEvolution
open scoped Matrix ComplexOrder

noncomputable section

abbrev M := DensityCore.M

/-- The exact evolved density on nine complex coordinates. -/
def evolvedDensity (H tau : M) (t : ℝ) : M :=
  U H t * tau * (U H t).conjTranspose

/-- Conjugation preserves PSD without a rank or inverse premise on tau. -/
theorem evolvedDensity_posSemidef (H tau : M) (hTau : tau.PosSemidef) (t : ℝ) :
    (evolvedDensity H tau t).PosSemidef :=
  hTau.mul_mul_conjTranspose_same (U H t)

/-- Hermitian exact evolution preserves the ordinary complex trace. -/
theorem trace_evolvedDensity (H tau : M) (hH : H.IsHermitian) (t : ℝ) :
    Matrix.trace (evolvedDensity H tau t) = Matrix.trace tau := by
  rw [evolvedDensity, Matrix.trace_mul_cycle,
    conjTranspose_mul_self H hH t, Matrix.one_mul]

/-- Ordinary trace one is preserved when it is supplied. -/
theorem trace_one_evolvedDensity (H tau : M) (hH : H.IsHermitian)
    (hTrace : Matrix.trace tau = 1) (t : ℝ) :
    Matrix.trace (evolvedDensity H tau t) = 1 := by
  rw [trace_evolvedDensity H tau hH t, hTrace]

/-- Every reader has this identity, without a Hermitian reader premise. -/
theorem reader_trace (H tau R : M) (t : ℝ) :
    Matrix.trace (R * evolvedDensity H tau t) =
      Matrix.trace (((U H t).conjTranspose * R * U H t) * tau) := by
  simp only [evolvedDensity, ← Matrix.mul_assoc]
  rw [Matrix.trace_mul_cycle]
  simp only [Matrix.mul_assoc]

/-- At zero time the density is unchanged. -/
theorem evolvedDensity_time_zero (H tau : M) : evolvedDensity H tau 0 = tau := by
  simp [evolvedDensity, U_time_zero]

/-- Zero density stays zero at every time. -/
theorem evolvedDensity_zero (H : M) (t : ℝ) : evolvedDensity H 0 t = 0 := by
  simp [evolvedDensity]

/-- A zero generator leaves every density fixed. -/
theorem evolvedDensity_zero_generator (tau : M) (t : ℝ) :
    evolvedDensity 0 tau t = tau := by
  simp [evolvedDensity, U_zero]

private def pureDensity : M := Matrix.diagonal (fun i => if i = 0 then 1 else 0)

private theorem pureDensity_psd : pureDensity.PosSemidef := by
  apply Matrix.posSemidef_diagonal_iff.mpr
  intro i
  split_ifs <;> simp

private theorem pureDensity_trace : Matrix.trace pureDensity = 1 := by
  simp [pureDensity, Matrix.trace_diagonal]

private theorem pureDensity_singular : pureDensity.mulVec (Pi.single 1 1) = 0 := by
  ext i
  simp [pureDensity, Matrix.mulVec_diagonal, Pi.single_apply]
  intro hi
  subst i
  decide

/-- A singular trace-one density stays PSD and trace one under a nonzero generator. -/
private theorem singular_control (t : ℝ) :
    (1 : M).IsHermitian ∧ (1 : M) ≠ 0 ∧
    pureDensity.PosSemidef ∧ Matrix.trace pureDensity = 1 ∧
    pureDensity.mulVec (Pi.single 1 1) = 0 ∧
    (Pi.single 1 1 : Fin 9 → ℂ) ≠ 0 ∧
    (evolvedDensity 1 pureDensity t).PosSemidef ∧
    Matrix.trace (evolvedDensity 1 pureDensity t) = 1 := by
  refine ⟨Matrix.isHermitian_one, one_ne_zero, pureDensity_psd, pureDensity_trace,
    pureDensity_singular, ?_, evolvedDensity_posSemidef 1 pureDensity pureDensity_psd t,
    trace_one_evolvedDensity 1 pureDensity Matrix.isHermitian_one pureDensity_trace t⟩
  intro h
  have h1 := congrFun h 1
  simp at h1

private theorem zero_control (H : M) (hH : H.IsHermitian) (t : ℝ) :
    (evolvedDensity H 0 t).PosSemidef ∧
    evolvedDensity H 0 t = 0 ∧ Matrix.trace (evolvedDensity H 0 t) = 0 := by
  refine ⟨evolvedDensity_posSemidef H 0 ?_ t, evolvedDensity_zero H t, ?_⟩
  · simpa using Matrix.posSemidef_self_mul_conjTranspose (0 : M)
  · rw [trace_evolvedDensity H 0 hH t]; simp

private def scale : M := (2 : ℂ) • (1 : M)

private theorem scale_conjugation :
    scale * pureDensity * scale.conjTranspose = (4 : ℂ) • pureDensity := by
  simp [scale, smul_smul]
  norm_num

/-- Arbitrary finite conjugation can change the trace of a PSD trace-one density. -/
private theorem nonunitary_control :
    scale ∉ unitary M ∧
    Matrix.trace (scale * pureDensity * scale.conjTranspose) = 4 ∧
    Matrix.trace (scale * pureDensity * scale.conjTranspose) ≠
      Matrix.trace pureDensity := by
  have ht : Matrix.trace (scale * pureDensity * scale.conjTranspose) = 4 := by
    rw [scale_conjugation, Matrix.trace_smul, pureDensity_trace]; simp
  refine ⟨?_, ht, ?_⟩
  · intro h
    have hi : scale.conjTranspose * scale = 1 := Unitary.star_mul_self_of_mem h
    have he := congrArg (fun A : M => A 0 0) hi
    norm_num [scale, Matrix.smul_mul, Matrix.mul_smul, smul_smul] at he
  · rw [ht, pureDensity_trace]; norm_num

#print axioms evolvedDensity_posSemidef
#print axioms trace_evolvedDensity
#print axioms trace_one_evolvedDensity
#print axioms reader_trace
#print axioms evolvedDensity_time_zero
#print axioms evolvedDensity_zero
#print axioms evolvedDensity_zero_generator
#print axioms pureDensity_psd
#print axioms pureDensity_trace
#print axioms pureDensity_singular
#print axioms singular_control
#print axioms zero_control
#print axioms scale_conjugation
#print axioms nonunitary_control

end

end SourceLaw.ColourSingletGateway.DensityEvolution
