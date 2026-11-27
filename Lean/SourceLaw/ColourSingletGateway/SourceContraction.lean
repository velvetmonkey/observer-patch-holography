import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.Analysis.Complex.Order
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

/-! Finite projector-complement sources with Euclidean operator norms.
Certificate projector, column and source byte equalities are input boundaries. -/
namespace SourceLaw.ColourSingletGateway.SourceContraction
open scoped Matrix Matrix.Norms.L2Operator BigOperators ComplexOrder
noncomputable section

/-- Insert coordinates at specified positions. -/
def insertion {m n : ℕ} (e : Fin m → Fin n) : Matrix (Fin n) (Fin m) ℂ :=
  fun i j => if i = e j then 1 else 0

theorem insertion_gram {m n : ℕ} (e : Fin m → Fin n) (he : Function.Injective e) :
    (insertion e).conjTranspose * insertion e = 1 := by
  ext i j
  rw [Matrix.mul_apply, Finset.sum_eq_single (e i)]
  · simp [insertion, Matrix.conjTranspose_apply, Matrix.one_apply, he.eq_iff]
  · intro b _ hb
    simp [insertion, Matrix.conjTranspose_apply, hb]
  · simp

theorem gram_norm_map {m n : ℕ} (A : Matrix (Fin n) (Fin m) ℂ)
    (hA : A.conjTranspose * A = 1) (x : EuclideanSpace ℂ (Fin m)) :
    ‖A.toEuclideanLin x‖ = ‖x‖ := by
  apply (LinearMap.norm_map_iff_inner_map_map A.toEuclideanLin).mpr ?_ x
  intro u v
  rw [← LinearMap.adjoint_inner_left,
    ← Matrix.toEuclideanLin_conjTranspose_eq_adjoint]
  have h : A.conjTranspose.toEuclideanLin (A.toEuclideanLin u) = u := by
    simp only [Matrix.toLpLin_apply]
    rw [Matrix.mulVec_mulVec, hA, Matrix.one_mulVec, WithLp.toLp_ofLp]
  rw [h]

theorem insertion_isometry {m n : ℕ} (e : Fin m → Fin n) (he : Function.Injective e) :
    Isometry (insertion e).toEuclideanLin := by
  apply (AddMonoidHomClass.isometry_iff_norm _).mpr
  exact gram_norm_map _ (insertion_gram e he)

theorem insertion_norm_le_one {m n : ℕ} [NeZero m] (e : Fin m → Fin n)
    (he : Function.Injective e) : ‖insertion e‖ ≤ 1 := by
  have h := Matrix.l2_opNorm_conjTranspose_mul_self (insertion e)
  rw [insertion_gram e he] at h
  have h1 : ‖(1 : Matrix (Fin m) (Fin m) ℂ)‖ ≤ 1 := le_of_eq norm_one
  have hn := norm_nonneg (insertion e)
  nlinarith

/-- Distinct-column selection from nine to twelve coordinates. -/
def selection (c : Fin 9 → Fin 12) := insertion c

/-- Checked first-cell inclusion. -/
def firstCell (i : Fin 12) : Fin 240 := ⟨i.val, by omega⟩

theorem firstCell_injective : Function.Injective firstCell := by
  intro a b h
  apply Fin.ext
  exact congrArg (fun z => z.val) h

/-- Zero padding from twelve to 240 coordinates. -/
def padding := insertion firstCell

theorem selection_isometry (c : Fin 9 → Fin 12) (hc : Function.Injective c) :
    Isometry (selection c).toEuclideanLin := insertion_isometry c hc

theorem padding_isometry : Isometry padding.toEuclideanLin :=
  insertion_isometry firstCell firstCell_injective

def complement (P : Matrix (Fin 12) (Fin 12) ℂ) := 1 - P

theorem complement_hermitian (P : Matrix (Fin 12) (Fin 12) ℂ)
    (hP : P.IsHermitian) : (complement P).IsHermitian :=
  Matrix.isHermitian_one.sub hP

theorem complement_idempotent (P : Matrix (Fin 12) (Fin 12) ℂ)
    (hPP : P * P = P) : complement P * complement P = complement P := by
  simp [complement, sub_mul, mul_sub, hPP]

theorem complement_norm_le_one (P : Matrix (Fin 12) (Fin 12) ℂ)
    (hP : P.IsHermitian) (hPP : P * P = P) : ‖complement P‖ ≤ 1 := by
  have h := (complement_hermitian P hP).isSelfAdjoint.norm_mul_self
  rw [complement_idempotent P hPP] at h
  have hn := norm_nonneg (complement P)
  nlinarith

/-- Exact source entries, with a checked cast below row twelve. -/
def S (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12) :
    Matrix (Fin 240) (Fin 9) ℂ := fun i j =>
  if h : i.val < 12 then complement P ⟨i.val, h⟩ (c j) else 0

theorem source_factorisation (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12) :
    S P c = padding * complement P * selection c := by
  ext i j
  rw [Matrix.mul_assoc, Matrix.mul_apply]
  by_cases hi : i.val < 12
  · let k : Fin 12 := ⟨i.val, hi⟩
    have hk : firstCell k = i := Fin.ext rfl
    rw [Finset.sum_eq_single k]
    · simp [padding, insertion, hk, Matrix.mul_apply, selection, S, hi, k]
    · intro b _ hb
      have hib : i ≠ firstCell b := by
        intro h
        exact hb (firstCell_injective (h.symm.trans hk))
      simp [padding, insertion, hib]
    · simp
  · have hall (b : Fin 12) : i ≠ firstCell b := by
      intro h
      have := congrArg Fin.val h
      dsimp [firstCell] at this
      omega
    simp [padding, insertion, hall, S, hi]

theorem source_norm_le_one (P : Matrix (Fin 12) (Fin 12) ℂ)
    (hP : P.IsHermitian) (hPP : P * P = P)
    (c : Fin 9 → Fin 12) (hc : Function.Injective c) : ‖S P c‖ ≤ 1 := by
  rw [source_factorisation]
  have hpad : ‖padding‖ ≤ 1 := insertion_norm_le_one firstCell firstCell_injective
  have hsel : ‖selection c‖ ≤ 1 := insertion_norm_le_one c hc
  calc
    ‖padding * complement P * selection c‖ ≤
        ‖padding‖ * ‖complement P‖ * ‖selection c‖ :=
      (Matrix.l2_opNorm_mul _ _).trans
        (mul_le_mul_of_nonneg_right (Matrix.l2_opNorm_mul _ _) (norm_nonneg _))
    _ ≤ 1 * 1 * 1 := mul_le_mul
      (mul_le_mul hpad (complement_norm_le_one P hP hPP) (norm_nonneg _) (by norm_num))
      hsel (norm_nonneg _) (by norm_num)
    _ = 1 := by norm_num

theorem source_supported (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12)
    (i : Fin 240) (hi : 12 ≤ i.val) (j : Fin 9) : S P c i j = 0 := by
  simp [S, show ¬i.val < 12 by omega]

theorem source_first_cell (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12)
    (i : Fin 12) (j : Fin 9) : S P c (firstCell i) j = complement P i (c j) := by
  simp [S, firstCell, i.isLt]

theorem projector_source_zero (P : Matrix (Fin 12) (Fin 12) ℂ)
    (hPP : P * P = P) (c : Fin 9 → Fin 12) :
    P * (S P c).submatrix firstCell id = 0 := by
  have he : (S P c).submatrix firstCell id = complement P * selection c := by
    ext i j
    simp [Matrix.submatrix_apply, source_first_cell, Matrix.mul_apply, selection, insertion]
  rw [he, ← Matrix.mul_assoc]
  simp [complement, mul_sub, hPP]

/-- The source Gram matrix; no rank or invertibility is asserted. -/
def W (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12) :=
  (S P c).conjTranspose * S P c

theorem W_hermitian (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12) :
    (W P c).IsHermitian := Matrix.isHermitian_conjTranspose_mul_self _

theorem W_posSemidef (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12) :
    (W P c).PosSemidef := Matrix.posSemidef_conjTranspose_mul_self _

/-- Equality inputs attach the generic construction to supplied certificate data. -/
def CertificateBinding (P actualP : Matrix (Fin 12) (Fin 12) ℂ)
    (c actualC : Fin 9 → Fin 12) (actualS : Matrix (Fin 240) (Fin 9) ℂ) : Prop :=
  P = actualP ∧ c = actualC ∧ S actualP actualC = actualS

theorem bound_source (P actualP : Matrix (Fin 12) (Fin 12) ℂ)
    (c actualC : Fin 9 → Fin 12) (actualS : Matrix (Fin 240) (Fin 9) ℂ)
    (hbind : CertificateBinding P actualP c actualC actualS)
    (hP : P.IsHermitian) (hPP : P * P = P) (hc : Function.Injective c) :
    ‖actualS‖ ≤ 1 := by
  rcases hbind with ⟨rfl, rfl, rfl⟩
  exact source_norm_le_one P hP hPP c hc

/-- With zero projector the source is coordinate insertion. -/
theorem zero_source (c : Fin 9 → Fin 12) :
    S 0 c = insertion (firstCell ∘ c) := by
  ext i j
  by_cases hi : i.val < 12
  · simp only [S, hi, dite_true, complement, sub_zero, Matrix.one_apply,
      insertion, Function.comp_apply]
    congr 1
    apply propext
    simp only [Fin.ext_iff, firstCell]
  · have hne : i ≠ firstCell (c j) := by
      intro h
      have := congrArg Fin.val h
      dsimp [firstCell] at this
      omega
    simp [S, hi, insertion, hne]

theorem zero_source_norm_map (c : Fin 9 → Fin 12) (hc : Function.Injective c)
    (x : EuclideanSpace ℂ (Fin 9)) : ‖(S 0 c).toEuclideanLin x‖ = ‖x‖ := by
  rw [zero_source]
  exact gram_norm_map _ (insertion_gram _ (firstCell_injective.comp hc)) x

theorem identity_source (c : Fin 9 → Fin 12) :
    S (1 : Matrix (Fin 12) (Fin 12) ℂ) c = 0 := by
  ext i j
  simp [S, complement]

def canonicalSelection (j : Fin 9) : Fin 12 := ⟨j.val, by omega⟩

theorem canonicalSelection_injective : Function.Injective canonicalSelection := by
  intro a b h
  apply Fin.ext
  exact congrArg (fun z => z.val) h

theorem zero_projector_control : ‖S 0 canonicalSelection‖ ≤ 1 :=
  source_norm_le_one 0 Matrix.isHermitian_zero (by simp)
    canonicalSelection canonicalSelection_injective

theorem identity_projector_control : ‖S 1 canonicalSelection‖ = 0 := by
  rw [identity_source, norm_zero]

/-- A nonzero coordinate projector. -/
def coordinateProjector : Matrix (Fin 12) (Fin 12) ℂ :=
  Matrix.diagonal (fun i => if i = 0 then 1 else 0)

theorem coordinateProjector_hermitian : coordinateProjector.IsHermitian := by
  apply Matrix.isHermitian_diagonal_iff.mpr
  intro i
  by_cases h : i = 0 <;> simp [h, isSelfAdjoint_iff]

theorem coordinateProjector_idempotent : coordinateProjector * coordinateProjector =
    coordinateProjector := by
  unfold coordinateProjector
  rw [Matrix.diagonal_mul_diagonal]
  congr 1
  funext i
  by_cases h : i = 0 <;> simp [h]

theorem coordinateProjector_nonzero : coordinateProjector ≠ 0 := by
  intro h
  have := congrFun (congrFun h 0) 0
  norm_num [coordinateProjector] at this

theorem coordinate_projector_control : ‖S coordinateProjector canonicalSelection‖ ≤ 1 :=
  source_norm_le_one coordinateProjector coordinateProjector_hermitian
    coordinateProjector_idempotent canonicalSelection canonicalSelection_injective

theorem boundary_11 (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12)
    (j : Fin 9) : S P c 11 j = complement P 11 (c j) := by
  simpa only [firstCell] using source_first_cell P c 11 j

theorem boundary_12 (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12)
    (j : Fin 9) : S P c 12 j = 0 := source_supported P c 12 (by norm_num) j

theorem boundary_239 (P : Matrix (Fin 12) (Fin 12) ℂ) (c : Fin 9 → Fin 12)
    (j : Fin 9) : S P c 239 j = 0 := source_supported P c 239 (by norm_num) j

/-- Repeating the same coordinate violates the selection premise. -/
def repeatedSelection : Fin 9 → Fin 12 := fun _ => 0

theorem repeated_not_injective : ¬ Function.Injective repeatedSelection := by
  intro h
  have he : (0 : Fin 9) = 1 := h rfl
  norm_num at he

/-- Two unit coefficients in the repeated-column control. -/
def twoCoefficients : EuclideanSpace ℂ (Fin 9) :=
  WithLp.toLp 2 (fun j => if j.val = 0 ∨ j.val = 1 then 1 else 0)

theorem twoCoefficients_norm_sq : ‖twoCoefficients‖ ^ 2 = 2 := by
  rw [EuclideanSpace.norm_sq_eq]
  norm_num [twoCoefficients, Fin.sum_univ_succ]

theorem repeated_output : (S 0 repeatedSelection).toEuclideanLin twoCoefficients =
    WithLp.toLp 2 (Pi.single (0 : Fin 240) (2 : ℂ)) := by
  apply WithLp.ofLp_injective
  funext i
  simp only [Matrix.toLpLin_apply]
  by_cases hi : i = 0
  · subst i
    norm_num [Matrix.mulVec, dotProduct, S, complement, repeatedSelection,
      twoCoefficients, Fin.sum_univ_succ]
    exact_mod_cast (show (Finset.univ.filter
      (fun x : Fin 9 => x = 0 ∨ x.val = 1)).card = 2 by decide)
  · have hne : i ≠ firstCell 0 := by simpa [firstCell] using hi
    rw [zero_source]
    simp [Matrix.mulVec, dotProduct, insertion, repeatedSelection, firstCell,
      hi]

theorem repeated_output_norm_sq :
    ‖(S 0 repeatedSelection).toEuclideanLin twoCoefficients‖ ^ 2 = 4 := by
  rw [repeated_output, EuclideanSpace.norm_sq_eq]
  simp only [Pi.single_apply]
  rw [Finset.sum_eq_single (0 : Fin 240)]
  · norm_num
  · intro b _ hb
    simp [hb]
  · simp

/-- The repeated-column matrix fails contraction on these two coefficients. -/
theorem repeated_source_not_contraction : ¬ ‖S 0 repeatedSelection‖ ≤ 1 := by
  intro h
  have hm := Matrix.l2_opNorm_mulVec (S 0 repeatedSelection) twoCoefficients
  change ‖(S 0 repeatedSelection).toEuclideanLin twoCoefficients‖ ≤
    ‖S 0 repeatedSelection‖ * ‖twoCoefficients‖ at hm
  have hb := hm.trans (mul_le_mul_of_nonneg_right h (norm_nonneg twoCoefficients))
  rw [one_mul] at hb
  have hi := twoCoefficients_norm_sq
  have ho := repeated_output_norm_sq
  have hn := norm_nonneg ((S 0 repeatedSelection).toEuclideanLin twoCoefficients)
  have hx := norm_nonneg twoCoefficients
  nlinarith

theorem doubled_identity_not_idempotent :
    ((2 : ℂ) • (1 : Matrix (Fin 12) (Fin 12) ℂ)) * ((2 : ℂ) • 1) ≠ (2 : ℂ) • 1 := by
  intro h
  rw [Matrix.mul_smul, Matrix.smul_mul, Matrix.one_mul] at h
  have he := congrFun (congrFun h 0) 0
  simp only [Matrix.smul_apply, Matrix.one_apply] at he
  norm_num at he

/-- The coordinate-projector source has a nonzero allowed coordinate. -/
theorem coordinate_source_entry : S coordinateProjector canonicalSelection 1 1 = 1 := by
  change (1 : ℂ) - (if (1 : Fin 12) = 0 then 1 else 0) = 1
  norm_num

#print axioms insertion
#print axioms insertion_gram
#print axioms gram_norm_map
#print axioms insertion_isometry
#print axioms insertion_norm_le_one
#print axioms selection
#print axioms firstCell
#print axioms firstCell_injective
#print axioms padding
#print axioms selection_isometry
#print axioms padding_isometry
#print axioms complement
#print axioms complement_hermitian
#print axioms complement_idempotent
#print axioms complement_norm_le_one
#print axioms S
#print axioms source_factorisation
#print axioms source_norm_le_one
#print axioms source_supported
#print axioms source_first_cell
#print axioms projector_source_zero
#print axioms W
#print axioms W_hermitian
#print axioms W_posSemidef
#print axioms CertificateBinding
#print axioms bound_source
#print axioms zero_source
#print axioms zero_source_norm_map
#print axioms identity_source
#print axioms canonicalSelection
#print axioms canonicalSelection_injective
#print axioms zero_projector_control
#print axioms identity_projector_control
#print axioms coordinateProjector
#print axioms coordinateProjector_hermitian
#print axioms coordinateProjector_idempotent
#print axioms coordinateProjector_nonzero
#print axioms coordinate_projector_control
#print axioms boundary_11
#print axioms boundary_12
#print axioms boundary_239
#print axioms repeatedSelection
#print axioms repeated_not_injective
#print axioms twoCoefficients
#print axioms twoCoefficients_norm_sq
#print axioms repeated_output
#print axioms repeated_output_norm_sq
#print axioms repeated_source_not_contraction
#print axioms doubled_identity_not_idempotent
#print axioms coordinate_source_entry

end
end SourceLaw.ColourSingletGateway.SourceContraction
