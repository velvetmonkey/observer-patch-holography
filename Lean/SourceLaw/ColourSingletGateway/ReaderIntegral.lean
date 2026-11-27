import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.MeasureTheory.Integral.Bochner.ContinuousLinearMap
import Mathlib.LinearAlgebra.Matrix.Hermitian
import Mathlib.Tactic.NormNum

/-!
# Continuous reader integrals

Finite complex matrices use the Euclidean operator norm. Integrals use real
Lebesgue volume. Continuity on the closed unit interval supplies the strong
measurability and integrability needed by the integral. These conditional
results assert no fixed certificate or physical transport.
-/

open scoped Matrix.Norms.L2Operator
open MeasureTheory

noncomputable section

set_option backward.isDefEq.respectTransparency false

namespace SourceLaw.ColourSingletGateway.ReaderIntegral

variable {n : Type*} [Fintype n] [DecidableEq n]

local instance matrixRealNormedSpace : NormedSpace ℝ (Matrix n n ℂ) :=
  { (inferInstance : Module ℝ (Matrix n n ℂ)) with
    norm_smul_le := fun r M => by
      have he : r • M = (r : ℂ) • M := by ext i j; rfl
      rw [he, norm_smul, Complex.norm_real] }

/-- Conjugate transpose is real linear and continuous in the matrix topology. -/
def conjTransposeRealCLM : Matrix n n ℂ →L[ℝ] Matrix n n ℂ where
  toFun := Matrix.conjTranspose
  map_add' := Matrix.conjTranspose_add
  map_smul' := by intros; simp
  cont := continuous_id.matrix_conjTranspose

/-- Continuity on the closed interval suffices for interval integrability. -/
theorem intervalIntegrable_reader (F : ℝ → Matrix n n ℂ)
    (hF : ContinuousOn F (Set.Icc 0 1)) : IntervalIntegrable F volume 0 1 :=
  hF.intervalIntegrable_of_Icc (by norm_num)

/-- Both readers and their difference have Bochner interval integrals. -/
theorem intervalIntegrable_readers (F Fp : ℝ → Matrix n n ℂ)
    (hF : ContinuousOn F (Set.Icc 0 1))
    (hFp : ContinuousOn Fp (Set.Icc 0 1)) :
    IntervalIntegrable F volume 0 1 ∧ IntervalIntegrable Fp volume 0 1 ∧
      IntervalIntegrable (fun t => F t - Fp t) volume 0 1 := by
  exact ⟨intervalIntegrable_reader F hF, intervalIntegrable_reader Fp hFp,
    (intervalIntegrable_reader F hF).sub (intervalIntegrable_reader Fp hFp)⟩

/-- The measurable domain for the oriented unit-interval integral is `(0,1]`. -/
theorem aestronglyMeasurable_reader (F : ℝ → Matrix n n ℂ)
    (hF : ContinuousOn F (Set.Icc 0 1)) :
    AEStronglyMeasurable F (volume.restrict (Set.Ioc 0 1)) :=
  (intervalIntegrable_reader F hF).aestronglyMeasurable

/-- A continuous real linear map commutes with the Bochner interval integral. -/
theorem integral_conjTranspose (F : ℝ → Matrix n n ℂ) (a b : ℝ)
    (hF : IntervalIntegrable F volume a b) :
    (∫ t in a..b, F t).conjTranspose = ∫ t in a..b, (F t).conjTranspose := by
  exact ((conjTransposeRealCLM (n := n)).intervalIntegral_comp_comm hF).symm

/-- Pointwise Hermiticity on the interval gives Hermiticity of its integral. -/
theorem isHermitian_integral (F : ℝ → Matrix n n ℂ)
    (hF : ContinuousOn F (Set.Icc 0 1))
    (hHerm : ∀ t ∈ Set.Icc (0 : ℝ) 1, (F t).IsHermitian) :
    (∫ t in 0..1, F t).IsHermitian := by
  rw [Matrix.IsHermitian, integral_conjTranspose F 0 1 (intervalIntegrable_reader F hF)]
  apply intervalIntegral.integral_congr
  intro t ht
  exact hHerm t (by simpa using ht)

/-- Integrate the pointwise error bound and use the exact interval length one. -/
theorem norm_integral_sub_le (F Fp : ℝ → Matrix n n ℂ)
    (hF : ContinuousOn F (Set.Icc 0 1))
    (hFp : ContinuousOn Fp (Set.Icc 0 1))
    (eta : ℝ) (_hEta : 0 ≤ eta)
    (hError : ∀ t ∈ Set.Icc (0 : ℝ) 1, ‖F t - Fp t‖ ≤ eta) :
    ‖(∫ t in 0..1, F t) - (∫ t in 0..1, Fp t)‖ ≤ eta := by
  rw [← intervalIntegral.integral_sub (intervalIntegrable_reader F hF)
    (intervalIntegrable_reader Fp hFp)]
  have hb : ∀ t ∈ Set.uIoc (0 : ℝ) 1, ‖F t - Fp t‖ ≤ eta := by
    intro t ht
    apply hError t
    rw [Set.uIoc_of_le (by norm_num : (0 : ℝ) ≤ 1)] at ht
    exact ⟨ht.1.le, ht.2⟩
  simpa using intervalIntegral.norm_integral_le_of_norm_le_const hb

/-- Each integral is Hermitian, with the same pointwise error budget. -/
theorem reader_integral_bounds (F Fp : ℝ → Matrix n n ℂ)
    (hF : ContinuousOn F (Set.Icc 0 1))
    (hFp : ContinuousOn Fp (Set.Icc 0 1))
    (hHerm : ∀ t ∈ Set.Icc (0 : ℝ) 1, (F t).IsHermitian)
    (hHermP : ∀ t ∈ Set.Icc (0 : ℝ) 1, (Fp t).IsHermitian)
    (eta : ℝ) (hEta : 0 ≤ eta)
    (hError : ∀ t ∈ Set.Icc (0 : ℝ) 1, ‖F t - Fp t‖ ≤ eta) :
    (∫ t in 0..1, F t).IsHermitian ∧ (∫ t in 0..1, Fp t).IsHermitian ∧
      ‖(∫ t in 0..1, F t) - (∫ t in 0..1, Fp t)‖ ≤ eta :=
  ⟨isHermitian_integral F hF hHerm, isHermitian_integral Fp hFp hHermP,
    norm_integral_sub_le F Fp hF hFp eta hEta hError⟩

/-- Zero readers have zero integral error. -/
theorem zero_readers :
    (∫ _t : ℝ in 0..1, (0 : Matrix (Fin 2) (Fin 2) ℂ)).IsHermitian ∧
      ‖(∫ _t : ℝ in 0..1, (0 : Matrix (Fin 2) (Fin 2) ℂ)) -
        (∫ _t : ℝ in 0..1, (0 : Matrix (Fin 2) (Fin 2) ℂ))‖ ≤ (0 : ℝ) := by
  have h := reader_integral_bounds (fun _ => (0 : Matrix (Fin 2) (Fin 2) ℂ))
    (fun _ => 0) continuous_const.continuousOn continuous_const.continuousOn
    (by intros; exact Matrix.isHermitian_zero)
    (by intros; exact Matrix.isHermitian_zero) 0 (by norm_num) (by intros; simp)
  exact ⟨h.1, h.2.2⟩

/-- A nonzero Hermitian diagonal reader. -/
def diagonalReader : Matrix (Fin 2) (Fin 2) ℂ := Matrix.diagonal ![1, 2]

theorem diagonalReader_isHermitian : diagonalReader.IsHermitian := by
  apply Matrix.ext
  intro i j
  fin_cases i <;> fin_cases j <;>
    simp [diagonalReader, Matrix.conjTranspose_apply, Matrix.diagonal]

/-- An exact real scalar shift attains its constant reader error budget. -/
theorem diagonal_shift :
    (∫ _t : ℝ in 0..1, diagonalReader) = diagonalReader ∧
    (∫ _t : ℝ in 0..1, diagonalReader + (1 / 4 : ℝ) • 1) =
      diagonalReader + (1 / 4 : ℝ) • 1 ∧
    ‖(∫ _t : ℝ in 0..1, diagonalReader) -
      (∫ _t : ℝ in 0..1, diagonalReader + (1 / 4 : ℝ) • 1)‖ = (1 / 4 : ℝ) := by
  constructor
  · simp
  constructor
  · simp
  simp only [intervalIntegral.integral_const, sub_zero, one_smul,
    sub_add_cancel_left, norm_neg]
  rw [norm_smul]
  norm_num

/-- Endpoint control: an interval of length two doubles a constant integral. -/
theorem endpoint_length_two :
    (∫ _t : ℝ in 0..2, (1 : Matrix (Fin 2) (Fin 2) ℂ)) = (2 : ℝ) • (1 : Matrix (Fin 2) (Fin 2) ℂ) ∧
      ‖∫ _t : ℝ in 0..2, (1 : Matrix (Fin 2) (Fin 2) ℂ)‖ = (2 : ℝ) := by
  constructor
  · simp only [intervalIntegral.integral_const, sub_zero]
  · rw [intervalIntegral.integral_const, norm_smul]
    norm_num

#print axioms matrixRealNormedSpace
#print axioms conjTransposeRealCLM
#print axioms intervalIntegrable_reader
#print axioms intervalIntegrable_readers
#print axioms aestronglyMeasurable_reader
#print axioms integral_conjTranspose
#print axioms isHermitian_integral
#print axioms norm_integral_sub_le
#print axioms reader_integral_bounds
#print axioms zero_readers
#print axioms diagonalReader
#print axioms diagonalReader_isHermitian
#print axioms diagonal_shift
#print axioms endpoint_length_two

end SourceLaw.ColourSingletGateway.ReaderIntegral
