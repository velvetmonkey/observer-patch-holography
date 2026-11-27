import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.Analysis.Complex.Order
import Mathlib.Tactic

/-!
# Real coordinates for complex colour forms

The block matrix has real part on its diagonal blocks and imaginary part
with signs minus and plus on its upper and lower off-diagonal blocks.
The results apply to every finite size, with no invertibility premise.
They supply no positivity certificate for a particular colour matrix.
-/

namespace SourceLaw.ColourRealification

noncomputable section

open scoped Matrix ComplexOrder

/-- Real and imaginary coordinates, in that order. -/
def realifyVector {n : ℕ} (v : Fin n → ℂ) : Fin n ⊕ Fin n → ℝ :=
  Sum.elim (fun i => (v i).re) (fun i => (v i).im)

/-- The real block matrix `[[Re M, -Im M], [Im M, Re M]]`. -/
def realifyMatrix {n : ℕ} (M : Matrix (Fin n) (Fin n) ℂ) :
    Matrix (Fin n ⊕ Fin n) (Fin n ⊕ Fin n) ℝ :=
  Matrix.fromBlocks (fun i j => (M i j).re) (fun i j => -(M i j).im)
    (fun i j => (M i j).im) (fun i j => (M i j).re)

/-- The inverse coordinate map uses every real block vector. -/
def vectorEquiv (n : ℕ) : (Fin n → ℂ) ≃ (Fin n ⊕ Fin n → ℝ) where
  toFun := realifyVector
  invFun := fun x i => ⟨x (.inl i), x (.inr i)⟩
  left_inv v := by funext i; rfl
  right_inv x := by funext i; cases i <;> rfl

/-- The complex quadratic form before taking its real part. -/
def complexForm {n : ℕ} (M : Matrix (Fin n) (Fin n) ℂ) (v : Fin n → ℂ) : ℂ :=
  ∑ i, ∑ j, star (v i) * M i j * v j

/-- The quadratic form of a real matrix. -/
def realForm {ι : Type*} [Fintype ι] (A : Matrix ι ι ℝ) (x : ι → ℝ) : ℝ :=
  ∑ i, ∑ j, x i * A i j * x j

/-- The coordinate map preserves the real quadratic value for every matrix. -/
theorem quadratic_eq {n : ℕ} (M : Matrix (Fin n) (Fin n) ℂ) (v : Fin n → ℂ) :
    realForm (realifyMatrix M) (realifyVector v) = (complexForm M v).re := by
  simp only [realForm, realifyMatrix, realifyVector, Fintype.sum_sum_type,
    Matrix.fromBlocks_apply₁₁, Matrix.fromBlocks_apply₁₂,
    Matrix.fromBlocks_apply₂₁, Matrix.fromBlocks_apply₂₂, Sum.elim_inl, Sum.elim_inr,
    complexForm, Complex.re_sum]
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i _
  simp only [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro j _
  simp [Complex.mul_re, Complex.mul_im]
  ring

/-- Hermitian matrices give symmetric real block matrices. -/
theorem realify_symmetric {n : ℕ} {M : Matrix (Fin n) (Fin n) ℂ}
    (hM : M.IsHermitian) : (realifyMatrix M).IsSymm := by
  apply Matrix.IsSymm.ext
  intro i j
  have hre (a b : Fin n) := congrArg Complex.re (hM.apply a b)
  have him (a b : Fin n) := congrArg Complex.im (hM.apply a b)
  cases i <;> cases j <;>
    simp_all [realifyMatrix, Complex.conj_re, Complex.conj_im]

/-- A Hermitian quadratic value is real, including at singular matrices. -/
theorem complexForm_im_zero {n : ℕ} {M : Matrix (Fin n) (Fin n) ℂ}
    (hM : M.IsHermitian) (v : Fin n → ℂ) : (complexForm M v).im = 0 := by
  have hs : star (complexForm M v) = complexForm M v := by
    simp only [complexForm, star_sum, star_mul, star_star]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro i _
    apply Finset.sum_congr rfl
    intro j _
    rw [hM.apply]
    ring
  have hi := congrArg Complex.im hs
  simp at hi
  linarith

private theorem complexForm_eq_dot {n : ℕ} (M : Matrix (Fin n) (Fin n) ℂ)
    (v : Fin n → ℂ) : complexForm M v = star v ⬝ᵥ (M *ᵥ v) := by
  simp [complexForm, dotProduct, Matrix.mulVec, Finset.mul_sum, mul_assoc]

private theorem realForm_eq_dot {ι : Type*} [Fintype ι]
    (A : Matrix ι ι ℝ) (x : ι → ℝ) : realForm A x = star x ⬝ᵥ (A *ᵥ x) := by
  simp [realForm, dotProduct, Matrix.mulVec, Finset.mul_sum, mul_assoc]

/-- Complex and real positive semidefiniteness agree under the coordinate
bijection. The only matrix premise is Hermiticity. -/
theorem posSemidef_iff {n : ℕ} {M : Matrix (Fin n) (Fin n) ℂ}
    (hM : M.IsHermitian) : M.PosSemidef ↔ (realifyMatrix M).PosSemidef := by
  have hr : (realifyMatrix M).IsHermitian := by
    simpa [Matrix.IsHermitian, Matrix.conjTranspose] using realify_symmetric hM
  rw [Matrix.posSemidef_iff_dotProduct_mulVec,
    Matrix.posSemidef_iff_dotProduct_mulVec]
  constructor
  · intro h
    refine ⟨hr, fun x => ?_⟩
    let v := (vectorEquiv n).symm x
    have hx : realifyVector v = x := (vectorEquiv n).apply_symm_apply x
    rw [← realForm_eq_dot, ← hx, quadratic_eq]
    exact (Complex.nonneg_iff.mp (by simpa [complexForm_eq_dot] using h.2 v)).1
  · intro h
    refine ⟨hM, fun v => ?_⟩
    rw [← complexForm_eq_dot, Complex.nonneg_iff]
    refine ⟨?_, (complexForm_im_zero hM v).symm⟩
    rw [← quadratic_eq, realForm_eq_dot]
    exact h.2 (realifyVector v)

/-- Nine complex coordinates correspond to eighteen real coordinates.
This implication requires a supplied PSD premise. -/
theorem colour_nine_posSemidef_iff {M : Matrix (Fin 9) (Fin 9) ℂ}
    (hM : M.IsHermitian) : M.PosSemidef ↔ (realifyMatrix M).PosSemidef :=
  posSemidef_iff hM

/-- The size-nine quadratic identity does not require Hermiticity. -/
theorem colour_nine_quadratic_eq (M : Matrix (Fin 9) (Fin 9) ℂ) (v : Fin 9 → ℂ) :
    realForm (realifyMatrix M) (realifyVector v) = (complexForm M v).re :=
  quadratic_eq M v

private def controlMatrix : Matrix (Fin 2) (Fin 2) ℂ := !![0, Complex.I; -Complex.I, 0]

private def controlVector : Fin 2 → ℂ := ![1, Complex.I]

private theorem control_hermitian : controlMatrix.IsHermitian := by
  apply Matrix.IsHermitian.ext
  intro i j
  fin_cases i <;> fin_cases j <;> norm_num [controlMatrix]

private theorem control_imaginary : (controlMatrix 0 1).im = 1 := by
  norm_num [controlMatrix]

private theorem control_quadratic :
    realForm (realifyMatrix controlMatrix) (realifyVector controlVector) =
      (complexForm controlMatrix controlVector).re := by
  norm_num [realForm, realifyMatrix, realifyVector, complexForm, controlMatrix,
    controlVector, Fintype.sum_sum_type, Fin.sum_univ_two, Complex.mul_re, Complex.mul_im]

#print axioms quadratic_eq
#print axioms realify_symmetric
#print axioms complexForm_im_zero
#print axioms posSemidef_iff
#print axioms colour_nine_posSemidef_iff
#print axioms colour_nine_quadratic_eq

end

end SourceLaw.ColourRealification
