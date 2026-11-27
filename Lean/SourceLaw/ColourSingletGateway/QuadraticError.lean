import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.Analysis.Matrix.Hermitian
import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.Tactic

/-!
# Finite reader error bounds

All matrix norms use the induced Euclidean operator norm. The state and
reader norm bounds are explicit inputs. The result supplies no analytic
remainder or attachment to fixed reader data.
-/

open scoped Matrix.Norms.L2Operator ComplexOrder
open Matrix

namespace SourceLaw.ColourSingletGateway.QuadraticError

variable {m n : Type*} [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]

omit [DecidableEq m] in
/-- The approximate state norm follows from the exact state and error norms. -/
theorem approximate_norm_le (X Y : Matrix m n ℂ) (e : ℝ)
    (hX : ‖X‖ ≤ 1) (hXY : ‖X - Y‖ ≤ e) : ‖Y‖ ≤ 1 + e := by
  calc
    ‖Y‖ = ‖X + (Y - X)‖ := by congr 1; abel
    _ ≤ ‖X‖ + ‖Y - X‖ := norm_add_le _ _
    _ ≤ 1 + e := add_le_add hX (by simpa only [norm_sub_rev] using hXY)

/-- Rectangular states and a square contraction reader give a quadratic error bound. -/
theorem reader_quadratic_error (X Y : Matrix m n ℂ) (R : Matrix m m ℂ)
    (e : ℝ) (he : 0 ≤ e) (hX : ‖X‖ ≤ 1) (hXY : ‖X - Y‖ ≤ e)
    (hR : ‖R‖ ≤ 1) : ‖Xᴴ * R * X - Yᴴ * R * Y‖ ≤ 2 * e + e ^ 2 := by
  have hY := approximate_norm_le X Y e hX hXY
  have hexpand : Xᴴ * R * X - Yᴴ * R * Y =
      (X - Y)ᴴ * R * X + Yᴴ * R * (X - Y) := by
    simp only [conjTranspose_sub, Matrix.sub_mul, Matrix.mul_sub]
    abel
  rw [hexpand]
  calc
    _ ≤ ‖(X - Y)ᴴ * R * X‖ + ‖Yᴴ * R * (X - Y)‖ := norm_add_le _ _
    _ ≤ (‖(X - Y)ᴴ * R‖ * ‖X‖) + (‖Yᴴ * R‖ * ‖X - Y‖) :=
      add_le_add (Matrix.l2_opNorm_mul _ _) (Matrix.l2_opNorm_mul _ _)
    _ ≤ (‖(X - Y)ᴴ‖ * ‖R‖) * ‖X‖ + (‖Yᴴ‖ * ‖R‖) * ‖X - Y‖ :=
      add_le_add
        (mul_le_mul_of_nonneg_right (Matrix.l2_opNorm_mul _ _) (norm_nonneg _))
        (mul_le_mul_of_nonneg_right (Matrix.l2_opNorm_mul _ _) (norm_nonneg _))
    _ = (‖X - Y‖ * ‖R‖) * ‖X‖ + (‖Y‖ * ‖R‖) * ‖X - Y‖ := by
      rw [Matrix.l2_opNorm_conjTranspose, Matrix.l2_opNorm_conjTranspose]
    _ ≤ (e * 1) * 1 + ((1 + e) * 1) * e := by gcongr
    _ = 2 * e + e ^ 2 := by ring

private theorem quadratic_norm_le (D : Matrix n n ℂ) (z : n → ℂ) :
    ‖star z ⬝ᵥ (D *ᵥ z)‖ ≤ ‖D‖ * ‖(WithLp.toLp 2 z : EuclideanSpace ℂ n)‖ ^ 2 := by
  let v : EuclideanSpace ℂ n := WithLp.toLp 2 z
  have h := norm_inner_le_norm (𝕜 := ℂ) v ((EuclideanSpace.equiv n ℂ).symm (D *ᵥ z))
  have hmul := Matrix.l2_opNorm_mulVec D v
  calc
    _ ≤ ‖v‖ * ‖(EuclideanSpace.equiv n ℂ).symm (D *ᵥ z)‖ := by
      simpa [EuclideanSpace.inner_eq_star_dotProduct, dotProduct_comm, v] using h
    _ ≤ ‖v‖ * (‖D‖ * ‖v‖) := mul_le_mul_of_nonneg_left hmul (norm_nonneg _)
    _ = _ := by dsimp [v]; ring

/-- A Hermitian error within eta gives both positive semidefinite identity shifts. -/
theorem hermitian_norm_error_psd (D : Matrix n n ℂ) (eta : ℝ)
    (hD : D.IsHermitian) (_heta : 0 ≤ eta) (hnorm : ‖D‖ ≤ eta) :
    (eta • (1 : Matrix n n ℂ) + D).PosSemidef ∧
      (eta • (1 : Matrix n n ℂ) - D).PosSemidef := by
  have hshift : (eta • (1 : Matrix n n ℂ)).IsHermitian := by
    simp [Matrix.IsHermitian, conjTranspose_smul]
  have hbound (z : n → ℂ) :
      |(star z ⬝ᵥ (D *ᵥ z)).re| ≤ eta * ‖(WithLp.toLp 2 z : EuclideanSpace ℂ n)‖ ^ 2 :=
    (Complex.abs_re_le_norm _).trans ((quadratic_norm_le D z).trans
      (mul_le_mul_of_nonneg_right hnorm (sq_nonneg _)))
  have hself (z : n → ℂ) : (star z ⬝ᵥ z).re =
      ‖(WithLp.toLp 2 z : EuclideanSpace ℂ n)‖ ^ 2 := by
    simpa only [EuclideanSpace.inner_eq_star_dotProduct, WithLp.ofLp_toLp,
      dotProduct_comm] using
      (inner_self_eq_norm_sq (𝕜 := ℂ) (WithLp.toLp 2 z : EuclideanSpace ℂ n))
  have hidentity (z : n → ℂ) :
      (star z ⬝ᵥ ((eta • (1 : Matrix n n ℂ)) *ᵥ z)).re =
        eta * ‖(WithLp.toLp 2 z : EuclideanSpace ℂ n)‖ ^ 2 := by
    have hmul : ((eta • (1 : Matrix n n ℂ)) *ᵥ z) = eta • z := by
      simpa using Matrix.smul_mulVec eta (1 : Matrix n n ℂ) z
    rw [hmul]
    erw [dotProduct_smul eta (star z) z]
    erw [Complex.smul_re]
    rw [smul_eq_mul, hself]
  constructor
  · refine Matrix.PosSemidef.of_dotProduct_mulVec_nonneg (hshift.add hD) fun z => ?_
    apply Complex.nonneg_iff.mpr
    constructor
    · simp only [add_mulVec, dotProduct_add, Complex.add_re]
      change 0 ≤ (star z ⬝ᵥ ((eta • (1 : Matrix n n ℂ)) *ᵥ z)).re +
        (star z ⬝ᵥ (D *ᵥ z)).re
      rw [hidentity]
      have := (abs_le.mp (hbound z)).1
      linarith
    · exact ((hshift.add hD).im_star_dotProduct_mulVec_self z).symm
  · refine Matrix.PosSemidef.of_dotProduct_mulVec_nonneg (hshift.sub hD) fun z => ?_
    apply Complex.nonneg_iff.mpr
    constructor
    · simp only [sub_mulVec, dotProduct_sub, Complex.sub_re]
      change 0 ≤ (star z ⬝ᵥ ((eta • (1 : Matrix n n ℂ)) *ᵥ z)).re -
        (star z ⬝ᵥ (D *ᵥ z)).re
      rw [hidentity]
      have := (abs_le.mp (hbound z)).2
      linarith
    · exact ((hshift.sub hD).im_star_dotProduct_mulVec_self z).symm

end SourceLaw.ColourSingletGateway.QuadraticError
