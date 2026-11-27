import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.Analysis.SpecialFunctions.Integrals.Basic
import Mathlib.LinearAlgebra.Matrix.Hermitian

/-!
# Finite polynomial reader integrals

All integrals are Bochner interval integrals over real volume. Matrix norms use
`Matrix.Norms.L2Operator`. The coefficient sum keeps every ordered pair.
-/

open scoped BigOperators Matrix.Norms.L2Operator
open MeasureTheory

noncomputable section

set_option backward.isDefEq.respectTransparency false

namespace SourceLaw.ColourSingletGateway.PolynomialIntegral

variable {m n ι : Type*} [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]

/-- A finite matrix polynomial with real monomials. -/
def finiteState (s : Finset ι) (p : ι → ℕ) (T : ι → Matrix m n ℂ) (t : ℝ) :
    Matrix m n ℂ := ∑ i ∈ s, (t ^ p i) • T i

/-- The polynomial reader integrand for a fixed reader. -/
def finiteReader (s : Finset ι) (p : ι → ℕ) (T : ι → Matrix m n ℂ)
    (Q : Matrix m m ℂ) (t : ℝ) : Matrix n n ℂ :=
  (finiteState s p T t).conjTranspose * Q * finiteState s p T t

omit [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n] in
theorem continuous_finiteState (s : Finset ι) (p : ι → ℕ) (T : ι → Matrix m n ℂ) :
    Continuous (finiteState s p T) := by
  exact continuous_finset_sum _ fun i _ => (continuous_id.pow (p i)).smul continuous_const

omit [Fintype n] [DecidableEq m] [DecidableEq n] in
theorem continuous_finiteReader (s : Finset ι) (p : ι → ℕ) (T : ι → Matrix m n ℂ)
    (Q : Matrix m m ℂ) : Continuous (finiteReader s p T Q) := by
  exact ((continuous_finiteState s p T).matrix_conjTranspose.matrix_mul
    continuous_const).matrix_mul (continuous_finiteState s p T)

omit [DecidableEq m] in
theorem intervalIntegrable_finiteReader (s : Finset ι) (p : ι → ℕ)
    (T : ι → Matrix m n ℂ) (Q : Matrix m m ℂ) (a b : ℝ) :
    IntervalIntegrable (finiteReader s p T Q) volume a b :=
  (continuous_finiteReader s p T Q).intervalIntegrable a b

/-- Conjugate transpose as a continuous real linear map. -/
def conjTransposeRealCLM : Matrix m n ℂ →L[ℝ] Matrix n m ℂ where
  toFun := Matrix.conjTranspose
  map_add' := Matrix.conjTranspose_add
  map_smul' := by intros; simp
  cont := continuous_id.matrix_conjTranspose

/-- Interchange uses a continuous real linear map on the Bochner integral. -/
theorem integral_conjTranspose (f : ℝ → Matrix m n ℂ) (a b : ℝ)
    (hf : IntervalIntegrable f volume a b) :
    (∫ t in a..b, f t).conjTranspose = ∫ t in a..b, (f t).conjTranspose := by
  exact ((conjTransposeRealCLM (m := m) (n := n)).intervalIntegral_comp_comm hf).symm

omit [Fintype n] [DecidableEq m] [DecidableEq n] in
theorem finiteReader_expansion (s : Finset ι) (p : ι → ℕ) (T : ι → Matrix m n ℂ)
    (Q : Matrix m m ℂ) (t : ℝ) :
    finiteReader s p T Q t = ∑ i ∈ s, ∑ j ∈ s,
      (t ^ (p i + p j)) • ((T i).conjTranspose * Q * T j) := by
  simp only [finiteReader, finiteState, Matrix.conjTranspose_sum,
    Matrix.conjTranspose_smul, star_trivial]
  rw [Matrix.sum_mul, Matrix.sum_mul]
  apply Finset.sum_congr rfl
  intro i hi
  rw [Matrix.mul_sum]
  apply Finset.sum_congr rfl
  intro j hj
  rw [Matrix.smul_mul, Matrix.smul_mul, Matrix.mul_smul, smul_smul, ← pow_add]

theorem integral_monomial (k : ℕ) (A : Matrix n n ℂ) :
    (∫ t : ℝ in 0..1, (t ^ k) • A) = ((1 : ℝ) / ((k + 1 : ℕ) : ℝ)) • A := by
  rw [intervalIntegral.integral_smul_const, integral_pow]
  simp

omit [DecidableEq m] in
/-- The exact identity includes every ordered pair of coefficients. -/
theorem integral_finiteReader (s : Finset ι) (p : ι → ℕ) (T : ι → Matrix m n ℂ)
    (Q : Matrix m m ℂ) :
    (∫ t : ℝ in 0..1, finiteReader s p T Q t) =
      ∑ i ∈ s, ∑ j ∈ s, ((1 : ℝ) / ((p i + p j + 1 : ℕ) : ℝ)) •
        ((T i).conjTranspose * Q * T j) := by
  simp_rw [finiteReader_expansion]
  rw [intervalIntegral.integral_finset_sum]
  · apply Finset.sum_congr rfl
    intro i hi
    rw [intervalIntegral.integral_finset_sum]
    · apply Finset.sum_congr rfl
      intro j hj
      exact integral_monomial _ _
    · intro j hj
      exact ((continuous_id.pow _).smul continuous_const).intervalIntegrable _ _
  · intro i hi
    exact (continuous_finset_sum _ fun j _ =>
      (continuous_id.pow _).smul continuous_const).intervalIntegrable _ _

omit [Fintype n] [DecidableEq m] [DecidableEq n] in
theorem isHermitian_finiteReader (s : Finset ι) (p : ι → ℕ) (T : ι → Matrix m n ℂ)
    {Q : Matrix m m ℂ} (hQ : Q.IsHermitian) (t : ℝ) :
    (finiteReader s p T Q t).IsHermitian :=
  Matrix.isHermitian_conjTranspose_mul_mul _ hQ

omit [DecidableEq m] in
theorem isHermitian_integral_finiteReader (s : Finset ι) (p : ι → ℕ)
    (T : ι → Matrix m n ℂ) {Q : Matrix m m ℂ} (hQ : Q.IsHermitian) :
    (∫ t : ℝ in 0..1, finiteReader s p T Q t).IsHermitian := by
  rw [Matrix.IsHermitian, integral_conjTranspose _ _ _
    (intervalIntegrable_finiteReader s p T Q 0 1)]
  congr 1
  funext t
  exact isHermitian_finiteReader s p T hQ t

omit [DecidableEq m] in
theorem isHermitian_coefficient_sum (s : Finset ι) (p : ι → ℕ)
    (T : ι → Matrix m n ℂ) {Q : Matrix m m ℂ} (hQ : Q.IsHermitian) :
    (∑ i ∈ s, ∑ j ∈ s, ((1 : ℝ) / ((p i + p j + 1 : ℕ) : ℝ)) •
      ((T i).conjTranspose * Q * T j)).IsHermitian := by
  rw [← integral_finiteReader]
  exact isHermitian_integral_finiteReader s p T hQ

/-- Coefficients indexed by natural degree, through degree `d`. -/
def polynomialState (d : ℕ) (T : ℕ → Matrix m n ℂ) : ℝ → Matrix m n ℂ :=
  finiteState (Finset.range (d + 1)) id T

omit [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n] in
theorem continuous_polynomialState (d : ℕ) (T : ℕ → Matrix m n ℂ) :
    Continuous (polynomialState d T) := continuous_finiteState _ _ _

omit [DecidableEq m] in
theorem integral_polynomialReader (d : ℕ) (T : ℕ → Matrix m n ℂ) (Q : Matrix m m ℂ) :
    (∫ t : ℝ in 0..1, (polynomialState d T t).conjTranspose * Q * polynomialState d T t) =
      ∑ i ∈ Finset.range (d + 1), ∑ j ∈ Finset.range (d + 1),
        ((1 : ℝ) / ((i + j + 1 : ℕ) : ℝ)) • ((T i).conjTranspose * Q * T j) :=
  integral_finiteReader _ _ _ _

omit [DecidableEq m] in
theorem integral_degree40 (T : ℕ → Matrix m n ℂ) (Q : Matrix m m ℂ) :
    (∫ t : ℝ in 0..1, (polynomialState 40 T t).conjTranspose * Q * polynomialState 40 T t) =
      ∑ i ∈ Finset.range 41, ∑ j ∈ Finset.range 41,
        ((1 : ℝ) / ((i + j + 1 : ℕ) : ℝ)) • ((T i).conjTranspose * Q * T j) :=
  integral_polynomialReader 40 T Q

omit [DecidableEq m] in
/-- The same degree40 identity for exactly 41 coefficients. -/
theorem integral_41_coefficients (T : Fin 41 → Matrix m n ℂ) (Q : Matrix m m ℂ) :
    (∫ t : ℝ in 0..1,
      (∑ i : Fin 41, (t ^ (i : ℕ)) • T i).conjTranspose * Q *
        (∑ i : Fin 41, (t ^ (i : ℕ)) • T i)) =
      ∑ i : Fin 41, ∑ j : Fin 41, ((1 : ℝ) / (((i : ℕ) + (j : ℕ) + 1 : ℕ) : ℝ)) •
        ((T i).conjTranspose * Q * T j) :=
  integral_finiteReader Finset.univ Fin.val T Q

private abbrev ScalarMatrix := Matrix (Fin 1) (Fin 1) ℂ

private def imaginaryCoefficients (k : ℕ) : ScalarMatrix :=
  fun _ _ => if k = 0 then 1 else Complex.I

private theorem degree0_control :
    (∫ t : ℝ in 0..1, (polynomialState 0 (fun _ => (1 : ScalarMatrix)) t).conjTranspose *
      (1 : ScalarMatrix) * polynomialState 0 (fun _ => (1 : ScalarMatrix)) t) = 1 := by
  rw [integral_polynomialReader]
  norm_num [Finset.sum_range_succ]

private theorem degree1_imaginary_control :
    (∫ t : ℝ in 0..1, (polynomialState 1 imaginaryCoefficients t).conjTranspose *
      (1 : ScalarMatrix) * polynomialState 1 imaginaryCoefficients t) =
      (4 / 3 : ℝ) • (1 : ScalarMatrix) := by
  rw [integral_polynomialReader]
  ext i j
  fin_cases i
  fin_cases j
  norm_num [Finset.sum_range_succ, imaginaryCoefficients, Matrix.mul_apply,
    Matrix.conjTranspose_apply, Matrix.smul_apply, Complex.ext_iff]

private theorem imaginary_cross_terms_cancel :
    (1 / 2 : ℝ) • ((imaginaryCoefficients 0).conjTranspose * (1 : ScalarMatrix) *
      imaginaryCoefficients 1) +
    (1 / 2 : ℝ) • ((imaginaryCoefficients 1).conjTranspose * (1 : ScalarMatrix) *
      imaginaryCoefficients 0) = 0 := by
  ext i j
  norm_num [imaginaryCoefficients, Matrix.mul_apply, Matrix.conjTranspose_apply,
    Matrix.smul_apply, Complex.ext_iff]

private theorem degree1_real_control :
    (∫ t : ℝ in 0..1, (polynomialState 1 (fun _ => (1 : ScalarMatrix)) t).conjTranspose *
      (1 : ScalarMatrix) * polynomialState 1 (fun _ => (1 : ScalarMatrix)) t) =
      (7 / 3 : ℝ) • (1 : ScalarMatrix) := by
  rw [integral_polynomialReader]
  ext i j
  fin_cases i
  fin_cases j
  norm_num [Finset.sum_range_succ, Matrix.mul_apply, Matrix.conjTranspose_apply,
    Matrix.smul_apply, Complex.ext_iff]

end SourceLaw.ColourSingletGateway.PolynomialIntegral
