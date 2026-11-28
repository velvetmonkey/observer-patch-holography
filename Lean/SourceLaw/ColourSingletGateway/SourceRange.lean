import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Trace
import Mathlib.Tactic

/-!
# Exact finite source range

Idempotence, exact rank three and source injectivity give unique coordinates
on the supported kernel. Exact Gram positive definiteness supplies injectivity.
The statements concern complex finite spaces and contain no numerical premise.
-/

namespace SourceLaw.ColourSingletGateway.SourceRange

open Matrix
open scoped ComplexOrder

noncomputable section

abbrev V9 := Fin 9 → ℂ
abbrev V12 := Fin 12 → ℂ
abbrev V240 := Fin 240 → ℂ
abbrev M12 := Matrix (Fin 12) (Fin 12) ℂ

/-- Include the first cell with its finite bound. -/
def firstCell (i : Fin 12) : Fin 240 := ⟨i.val, lt_trans i.isLt (by norm_num)⟩

/-- Read the first twelve coordinates. -/
def restrict : V240 →ₗ[ℂ] V12 where
  toFun y i := y (firstCell i)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

/-- Insert twelve coordinates and set all other rows to zero. -/
def padding : V12 →ₗ[ℂ] V240 where
  toFun x i := if h : i.val < 12 then x ⟨i.val, h⟩ else 0
  map_add' x y := by ext i; by_cases h : i.val < 12 <;> simp [h]
  map_smul' a x := by ext i; by_cases h : i.val < 12 <;> simp [h]

@[simp] theorem restrict_padding (x : V12) : restrict (padding x) = x := by
  ext i
  simp [restrict, padding, firstCell, i.isLt]

/-- The complete supported source domain. -/
def sourceSpace (P : M12) : Submodule ℂ V240 where
  carrier := {y | (∀ i : Fin 240, 12 ≤ i.val → y i = 0) ∧ P.mulVec (restrict y) = 0}
  zero_mem' := ⟨by simp, by change P.mulVecLin (restrict 0) = 0; rw [map_zero, map_zero]⟩
  add_mem' := by
    rintro x y ⟨hx, hxP⟩ ⟨hy, hyP⟩
    exact ⟨fun i hi => by simp [hx i hi, hy i hi], by
      change P.mulVecLin (restrict (x + y)) = 0
      rw [map_add, map_add]; change P.mulVec (restrict x) + P.mulVec (restrict y) = 0
      rw [hxP, hyP, add_zero]⟩
  smul_mem' := by
    rintro a x ⟨hx, hxP⟩
    exact ⟨fun i hi => by simp [hx i hi], by
      change P.mulVecLin (restrict (a • x)) = 0
      rw [map_smul, map_smul]; change a • P.mulVec (restrict x) = 0
      rw [hxP, smul_zero]⟩

/-- Padding and restriction identify the kernel and the supported kernel. -/
def kernelSourceEquiv (P : M12) : LinearMap.ker P.mulVecLin ≃ₗ[ℂ] sourceSpace P where
  toFun x := ⟨padding x, ⟨by
    intro i hi
    simp [padding, not_lt.mpr hi], by rw [restrict_padding]; exact x.property⟩⟩
  invFun y := ⟨restrict y, y.property.2⟩
  left_inv x := by apply Subtype.ext; exact restrict_padding x
  right_inv y := by
    apply Subtype.ext
    ext i
    by_cases hi : i.val < 12
    · simp [padding, restrict, firstCell, hi]
    · simpa [padding, hi] using (y.property.1 i (Nat.le_of_not_lt hi)).symm
  map_add' x y := by apply Subtype.ext; exact map_add padding (x : V12) (y : V12)
  map_smul' a x := by apply Subtype.ext; exact map_smul padding a (x : V12)

/-- Rank-nullity fixes the target dimension. -/
theorem sourceSpace_finrank (P : M12)
    (hRank : Module.finrank ℂ (LinearMap.range P.mulVecLin) = 3) :
    Module.finrank ℂ (sourceSpace P) = 9 := by
  have h := P.mulVecLin.finrank_range_add_finrank_ker
  rw [hRank, Module.finrank_fin_fun] at h
  have he := (kernelSourceEquiv P).finrank_eq
  omega

/-- Nine selected complement columns, with zero padding. -/
def source (P : M12) (c : Fin 9 → Fin 12) : Matrix (Fin 240) (Fin 9) ℂ :=
  fun i j => if h : i.val < 12 then (1 - P) ⟨i.val, h⟩ (c j) else 0

def gram (P : M12) (c : Fin 9 → Fin 12) : Matrix (Fin 9) (Fin 9) ℂ :=
  (source P c).conjTranspose * source P c

/-- Selection before application of the complement. -/
def selection (c : Fin 9 → Fin 12) : Matrix (Fin 12) (Fin 9) ℂ :=
  fun i j => if i = c j then 1 else 0

theorem source_apply (P : M12) (c : Fin 9 → Fin 12) (z : V9) :
    (source P c).mulVec z = padding ((1 - P).mulVec ((selection c).mulVec z)) := by
  ext i
  by_cases hi : i.val < 12
  · simp only [source, mulVec, dotProduct, hi, dite_true, padding, LinearMap.coe_mk,
      AddHom.coe_mk]
    simp only [selection, Finset.mul_sum]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro j _
    simp [mul_ite, ite_mul]
  · simp [source, mulVec, dotProduct, padding, hi]

/-- Idempotence supplies containment without a spanning premise. -/
theorem source_mem (P : M12) (c : Fin 9 → Fin 12) (hIdem : P * P = P) (z : V9) :
    (source P c).mulVec z ∈ sourceSpace P := by
  rw [source_apply]
  constructor
  · intro i hi
    simp [padding, not_lt.mpr hi]
  · rw [restrict_padding, Matrix.mulVec_mulVec, mul_sub, mul_one, hIdem, sub_self,
      zero_mulVec]

/-- A zero source output has zero Gram quadratic form. -/
theorem gram_posDef_injective (S : Matrix (Fin 240) (Fin 9) ℂ)
    (hW : (S.conjTranspose * S).PosDef) : Function.Injective S.mulVecLin := by
  apply (LinearMap.ker_eq_bot).mp
  apply LinearMap.ker_eq_bot'.mpr
  intro z hz
  by_contra hn
  have hp := hW.dotProduct_mulVec_pos hn
  change S.mulVec z = 0 at hz
  rw [← Matrix.mulVec_mulVec, hz, Matrix.mulVec_zero, dotProduct_zero] at hp
  exact (lt_irrefl 0) hp

/-- The finite source coordinates, with the exact source map as forward value. -/
def sourceRangeEquiv (P : M12) (c : Fin 9 → Fin 12) (hIdem : P * P = P)
    (hRank : Module.finrank ℂ (LinearMap.range P.mulVecLin) = 3)
    (hInj : Function.Injective (source P c).mulVecLin) : V9 ≃ₗ[ℂ] sourceSpace P :=
  LinearMap.linearEquivOfInjective
    ((source P c).mulVecLin.codRestrict (sourceSpace P) (source_mem P c hIdem))
    (fun x y h => hInj (congrArg Subtype.val h))
    (by rw [Module.finrank_fin_fun, sourceSpace_finrank P hRank])

@[simp] theorem sourceRangeEquiv_apply (P : M12) (c : Fin 9 → Fin 12)
    (hIdem : P * P = P) (hRank : Module.finrank ℂ (LinearMap.range P.mulVecLin) = 3)
    (hInj : Function.Injective (source P c).mulVecLin) (z : V9) :
    (sourceRangeEquiv P c hIdem hRank hInj z : V240) = (source P c).mulVec z := rfl

def sourceRangeEquiv_of_posDef (P : M12) (c : Fin 9 → Fin 12) (hIdem : P * P = P)
    (hRank : Module.finrank ℂ (LinearMap.range P.mulVecLin) = 3)
    (hW : (gram P c).PosDef) : V9 ≃ₗ[ℂ] sourceSpace P :=
  sourceRangeEquiv P c hIdem hRank (gram_posDef_injective _ hW)

@[simp] theorem sourceRangeEquiv_of_posDef_apply (P : M12) (c : Fin 9 → Fin 12)
    (hIdem : P * P = P) (hRank : Module.finrank ℂ (LinearMap.range P.mulVecLin) = 3)
    (hW : (gram P c).PosDef) (z : V9) :
    (sourceRangeEquiv_of_posDef P c hIdem hRank hW z : V240) =
      (source P c).mulVec z := rfl

theorem range_eq_sourceSpace (P : M12) (c : Fin 9 → Fin 12) (hIdem : P * P = P)
    (hRank : Module.finrank ℂ (LinearMap.range P.mulVecLin) = 3)
    (hW : (gram P c).PosDef) : LinearMap.range (source P c).mulVecLin = sourceSpace P := by
  apply le_antisymm
  · rintro y ⟨z, rfl⟩
    exact source_mem P c hIdem z
  · intro y hy
    obtain ⟨z, hz⟩ := (sourceRangeEquiv_of_posDef P c hIdem hRank hW).surjective ⟨y, hy⟩
    exact ⟨z, congrArg Subtype.val hz⟩

theorem unique_source_coordinates (P : M12) (c : Fin 9 → Fin 12) (hIdem : P * P = P)
    (hRank : Module.finrank ℂ (LinearMap.range P.mulVecLin) = 3)
    (hW : (gram P c).PosDef) (y : V240) (hy : y ∈ sourceSpace P) :
    ∃! z : V9, (source P c).mulVec z = y := by
  obtain ⟨z, hz⟩ := (sourceRangeEquiv_of_posDef P c hIdem hRank hW).surjective ⟨y, hy⟩
  refine ⟨z, congrArg Subtype.val hz, ?_⟩
  intro w hw
  exact gram_posDef_injective _ hW (hw.trans (congrArg Subtype.val hz).symm)


/-! Exact synthetic controls. These finite matrices have no physical attachment. -/
namespace Controls

set_option maxHeartbeats 1600000
set_option maxRecDepth 4096

/-- The first three coordinate directions. -/
def diagonalP : M12 := Matrix.diagonal (fun i => if i.val < 3 then 1 else 0)

def columns (j : Fin 9) : Fin 12 := ⟨j.val + 3, by omega⟩
def duplicate (j : Fin 9) : Fin 12 := if j = 1 then 3 else columns j
def distinctZero (j : Fin 9) : Fin 12 := if j = 0 then 0 else columns j

def place : V9 →ₗ[ℂ] V240 where
  toFun z i := if h : 3 ≤ i.val ∧ i.val < 12 then z ⟨i.val - 3, by omega⟩ else 0
  map_add' x y := by ext i; by_cases h : 3 ≤ i.val ∧ i.val < 12 <;> simp [h]
  map_smul' a x := by ext i; by_cases h : 3 ≤ i.val ∧ i.val < 12 <;> simp [h]

@[simp] theorem place_read (z : V9) (j : Fin 9) :
    place z (firstCell (columns j)) = z j := by
  simp [place, firstCell, columns, j.isLt]

theorem place_injective : Function.Injective place := by
  intro x y h
  ext j
  simpa using congrFun h (firstCell (columns j))

theorem diagonal_idempotent : diagonalP * diagonalP = diagonalP := by
  rw [diagonalP, Matrix.diagonal_mul_diagonal]
  congr 1
  ext i
  split_ifs <;> simp

theorem diagonal_rank : Module.finrank ℂ (LinearMap.range diagonalP.mulVecLin) = 3 := by
  change diagonalP.rank = 3
  rw [diagonalP, Matrix.rank_diagonal]
  norm_num [Fintype.card_subtype] <;> decide

theorem diagonal_dimension : Module.finrank ℂ (sourceSpace diagonalP) = 9 :=
  sourceSpace_finrank _ diagonal_rank

/-- A formula that exposes all nine coordinates. -/
theorem positive_apply (z : V9) : (source diagonalP columns).mulVec z = place z := by
  ext i
  by_cases hi : i.val < 12
  · let k : Fin 12 := ⟨i.val, hi⟩
    have hk : i = firstCell k := rfl
    rw [hk]
    generalize hk' : k = l
    clear hk' hk k hi i
    fin_cases l <;>
      simp [source, diagonalP, columns, firstCell, place, Matrix.mulVec, dotProduct,
        Matrix.one_apply, Matrix.diagonal_apply, Fin.sum_univ_succ, Fin.ext_iff, -Fin.val_eq_zero_iff]
  · have h3 : ¬ (3 ≤ i.val ∧ i.val < 12) := by omega
    simp [source, Matrix.mulVec, dotProduct, hi, place, h3]

theorem positive_injective : Function.Injective (source diagonalP columns).mulVecLin := by
  intro x y h
  apply place_injective
  simpa only [Matrix.mulVecLin_apply, positive_apply] using h

theorem positive_rank : Module.finrank ℂ
    (LinearMap.range (source diagonalP columns).mulVecLin) = 9 := by
  rw [LinearMap.finrank_range_of_inj positive_injective, Module.finrank_fin_fun]

/-- The explicit inverse reads rows three through eleven. -/
theorem positive_inverse (z : V9) (j : Fin 9) :
    (source diagonalP columns).mulVec z (firstCell (columns j)) = z j := by
  rw [positive_apply, place_read]

/-- A padded Gram sum reduces to twelve rows. -/
theorem gram_entry (P : M12) (c : Fin 9 → Fin 12) (j k : Fin 9) :
    gram P c j k = ∑ i : Fin 12, star ((1 - P) i (c j)) * (1 - P) i (c k) := by
  change (∑ i : Fin (12 + 228), star (source P c i j) * source P c i k) = _
  rw [Fin.sum_univ_add]
  have hz : ∀ i : Fin 228,
      star (source P c (Fin.natAdd 12 i) j) * source P c (Fin.natAdd 12 i) k = 0 := by
    intro i
    simp [source, show ¬ 12 + i.val < 12 by omega]
  simp only [hz, Finset.sum_const_zero, add_zero]
  apply Finset.sum_congr rfl
  intro i _
  simp [source, i.isLt]

theorem positive_gram : gram diagonalP columns = 1 := by
  ext j k
  rw [gram_entry]
  fin_cases j <;> fin_cases k <;>
    norm_num [diagonalP, columns, Matrix.one_apply, Matrix.diagonal_apply, Fin.sum_univ_succ, Fin.ext_iff, -Fin.val_eq_zero_iff]

theorem positive_coordinates (y : V240) (hy : y ∈ sourceSpace diagonalP) :
    ∃! z : V9, (source diagonalP columns).mulVec z = y := by
  apply unique_source_coordinates _ _ diagonal_idempotent diagonal_rank
  · rw [positive_gram]
    exact Matrix.PosDef.one
  · exact hy

theorem identity_rank : Module.finrank ℂ (LinearMap.range (1 : M12).mulVecLin) = 12 := by
  change (1 : M12).rank = 12
  simp [Matrix.rank_one]

theorem identity_source (c : Fin 9 → Fin 12) : source (1 : M12) c = 0 := by
  ext i j
  simp [source]

theorem identity_gram (c : Fin 9 → Fin 12) : gram (1 : M12) c = 0 := by
  simp [gram, identity_source]

def e9 (j : Fin 9) : V9 := Pi.single j 1
def e240 (i : Fin 240) : V240 := Pi.single i 1

theorem e9_nonzero (j : Fin 9) : e9 j ≠ 0 := by
  intro h
  have := congrFun h j
  simp [e9] at this

theorem identity_kills_e0 : (source (1 : M12) columns).mulVec (e9 0) = 0 := by
  rw [identity_source, Matrix.zero_mulVec]

def fold (z : V9) : V9 := fun j => if j = 0 then z 0 + z 1 else if j = 1 then 0 else z j
def drop (z : V9) : V9 := fun j => if j = 0 then 0 else z j

theorem duplicate_apply (z : V9) :
    (source diagonalP duplicate).mulVec z = place (fold z) := by
  ext i
  by_cases hi : i.val < 12
  · let k : Fin 12 := ⟨i.val, hi⟩
    have hk : i = firstCell k := rfl
    rw [hk]
    generalize hk' : k = l
    clear hk' hk k hi i
    fin_cases l <;>
      simp [source, diagonalP, duplicate, columns, firstCell, place, fold, Matrix.mulVec,
        dotProduct, Matrix.one_apply, Matrix.diagonal_apply, Fin.sum_univ_succ, Fin.ext_iff, -Fin.val_eq_zero_iff]
  · have h3 : ¬ (3 ≤ i.val ∧ i.val < 12) := by omega
    simp [source, Matrix.mulVec, dotProduct, hi, place, h3]

theorem distinctZero_apply (z : V9) :
    (source diagonalP distinctZero).mulVec z = place (drop z) := by
  ext i
  by_cases hi : i.val < 12
  · let k : Fin 12 := ⟨i.val, hi⟩
    have hk : i = firstCell k := rfl
    rw [hk]
    generalize hk' : k = l
    clear hk' hk k hi i
    fin_cases l <;>
      simp [source, diagonalP, distinctZero, columns, firstCell, place, drop, Matrix.mulVec,
        dotProduct, Matrix.one_apply, Matrix.diagonal_apply, Fin.sum_univ_succ, Fin.ext_iff, -Fin.val_eq_zero_iff]
  · have h3 : ¬ (3 ≤ i.val ∧ i.val < 12) := by omega
    simp [source, Matrix.mulVec, dotProduct, hi, place, h3]

theorem duplicate_vector_nonzero : e9 0 - e9 1 ≠ 0 := by
  intro h
  have := congrFun h 0
  norm_num [e9, Pi.single_apply] at this

theorem duplicate_kills :
    (source diagonalP duplicate).mulVec (e9 0 - e9 1) = 0 := by
  rw [duplicate_apply]
  have h : fold (e9 0 - e9 1) = 0 := by
    ext j; fin_cases j <;> norm_num [fold, e9, Pi.single_apply]
  rw [h, map_zero]

theorem distinctZero_kills : (source diagonalP distinctZero).mulVec (e9 0) = 0 := by
  rw [distinctZero_apply]
  have h : drop (e9 0) = 0 := by
    ext j; fin_cases j <;> norm_num [drop, e9, Pi.single_apply]
  rw [h, map_zero]

theorem distinct_indices : Function.Injective distinctZero := by
  intro i j h
  fin_cases i <;> fin_cases j <;> simp_all [distinctZero, columns, Fin.ext_iff, -Fin.val_eq_zero_iff]

theorem duplicate_missing_e4 : ¬ ∃ z : V9,
    (source diagonalP duplicate).mulVec z = e240 4 := by
  rintro ⟨z, h⟩
  have hh := congrFun h 4
  rw [duplicate_apply] at hh
  norm_num [place, fold, e240, Pi.single_apply] at hh

theorem distinctZero_missing_e3 : ¬ ∃ z : V9,
    (source diagonalP distinctZero).mulVec z = e240 3 := by
  rintro ⟨z, h⟩
  have hh := congrFun h 3
  rw [distinctZero_apply] at hh
  norm_num [place, drop, e240, Pi.single_apply] at hh

theorem e4_supported : e240 4 ∈ sourceSpace diagonalP := by
  have h := source_mem diagonalP columns diagonal_idempotent (e9 1)
  convert h using 1
  rw [positive_apply]
  ext i
  by_cases hi : i.val < 12
  · let k : Fin 12 := ⟨i.val, hi⟩
    have hk : i = firstCell k := rfl
    rw [hk]
    generalize hk' : k = l
    clear hk' hk k hi i
    fin_cases l <;> norm_num [place, firstCell, e9, e240, Pi.single_apply, Fin.ext_iff, -Fin.val_eq_zero_iff]
  · have h3 : ¬ (3 ≤ i.val ∧ i.val < 12) := by omega
    simp [place, h3, e240, Pi.single_apply, show i ≠ 4 by intro h; subst i; omega]

theorem e3_supported : e240 3 ∈ sourceSpace diagonalP := by
  have h := source_mem diagonalP columns diagonal_idempotent (e9 0)
  convert h using 1
  rw [positive_apply]
  ext i
  by_cases hi : i.val < 12
  · let k : Fin 12 := ⟨i.val, hi⟩
    have hk : i = firstCell k := rfl
    rw [hk]
    generalize hk' : k = l
    clear hk' hk k hi i
    fin_cases l <;> norm_num [place, firstCell, e9, e240, Pi.single_apply, Fin.ext_iff, -Fin.val_eq_zero_iff]
  · have h3 : ¬ (3 ≤ i.val ∧ i.val < 12) := by omega
    simp [place, h3, e240, Pi.single_apply, show i ≠ 3 by intro h; subst i; omega]

/-- The first forbidden ambient coordinate is outside the complete domain. -/
theorem ambient_e12_outside (P : M12) : e240 12 ∉ sourceSpace P := by
  intro h
  have hh := h.1 12 (by norm_num)
  norm_num [e240, Pi.single_apply] at hh

theorem source_row_zero (P : M12) (c : Fin 9 → Fin 12) (z : V9)
    (i : Fin 240) (hi : 12 ≤ i.val) : (source P c).mulVec z i = 0 := by
  simp [source, Matrix.mulVec, dotProduct, not_lt.mpr hi]

theorem support_boundary (z : V9) :
    (source diagonalP columns).mulVec z 11 = z 8 ∧
    (source diagonalP columns).mulVec z 12 = 0 ∧
    (source diagonalP columns).mulVec z 239 = 0 := by
  rw [positive_apply]
  simp [place]


theorem rank_eight_of_kernel (S : Matrix (Fin 240) (Fin 9) ℂ) (v : V9)
    (hv : v ≠ 0) (hk : LinearMap.ker S.mulVecLin = ℂ ∙ v) :
    Module.finrank ℂ (LinearMap.range S.mulVecLin) = 8 := by
  have hn := S.mulVecLin.finrank_range_add_finrank_ker
  rw [hk, finrank_span_singleton hv, Module.finrank_fin_fun] at hn
  omega

theorem duplicate_kernel :
    LinearMap.ker (source diagonalP duplicate).mulVecLin = ℂ ∙ (e9 0 - e9 1) := by
  ext z
  constructor
  · intro hz
    change (source diagonalP duplicate).mulVec z = 0 at hz
    rw [duplicate_apply] at hz
    have hf : fold z = 0 := place_injective (by simpa using hz)
    apply Submodule.mem_span_singleton.mpr
    refine ⟨z 0, ?_⟩
    ext j
    have h0 := congrFun hf 0
    have hj := congrFun hf j
    fin_cases j <;> simp_all [fold, e9, Pi.single_apply] <;> linear_combination -h0
  · intro hz
    obtain ⟨a, rfl⟩ := Submodule.mem_span_singleton.mp hz
    change (source diagonalP duplicate).mulVecLin (a • (e9 0 - e9 1)) = 0
    rw [map_smul]
    change a • (source diagonalP duplicate).mulVec (e9 0 - e9 1) = 0
    rw [duplicate_kills, smul_zero]

theorem duplicate_rank :
    Module.finrank ℂ (LinearMap.range (source diagonalP duplicate).mulVecLin) = 8 :=
  rank_eight_of_kernel _ _ duplicate_vector_nonzero duplicate_kernel

theorem distinctZero_kernel :
    LinearMap.ker (source diagonalP distinctZero).mulVecLin = ℂ ∙ e9 0 := by
  ext z
  constructor
  · intro hz
    change (source diagonalP distinctZero).mulVec z = 0 at hz
    rw [distinctZero_apply] at hz
    have hf : drop z = 0 := place_injective (by simpa using hz)
    apply Submodule.mem_span_singleton.mpr
    refine ⟨z 0, ?_⟩
    ext j
    have hj := congrFun hf j
    fin_cases j <;> simp_all [drop, e9, Pi.single_apply]
  · intro hz
    obtain ⟨a, rfl⟩ := Submodule.mem_span_singleton.mp hz
    change (source diagonalP distinctZero).mulVecLin (a • e9 0) = 0
    rw [map_smul]
    change a • (source diagonalP distinctZero).mulVec (e9 0) = 0
    rw [distinctZero_kills, smul_zero]

theorem distinctZero_rank :
    Module.finrank ℂ (LinearMap.range (source diagonalP distinctZero).mulVecLin) = 8 :=
  rank_eight_of_kernel _ _ (e9_nonzero 0) distinctZero_kernel

/-- A rational orthogonal projector with a nonidentity positive Gram matrix. -/
def rationalP : M12 := fun i j =>
  if i = 0 ∧ j = 0 then 9 / 25 else
  if (i = 0 ∧ j = 3) ∨ (i = 3 ∧ j = 0) then 12 / 25 else
  if i = 3 ∧ j = 3 then 16 / 25 else
  if (i = 1 ∧ j = 1) ∨ (i = 2 ∧ j = 2) then 1 else 0

theorem rational_idempotent : rationalP * rationalP = rationalP := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [rationalP, Matrix.mul_apply, Fin.sum_univ_succ, Fin.ext_iff, -Fin.val_eq_zero_iff]

theorem rational_hermitian : rationalP.IsHermitian := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [rationalP, Matrix.conjTranspose_apply, Fin.ext_iff, -Fin.val_eq_zero_iff]

theorem rational_gram : gram rationalP columns =
    Matrix.diagonal (fun j : Fin 9 => if j = 0 then (9 / 25 : ℂ) else 1) := by
  ext j k
  rw [gram_entry]
  fin_cases j <;> fin_cases k <;>
    norm_num [rationalP, columns, Matrix.one_apply, Matrix.diagonal_apply, Fin.sum_univ_succ, Fin.ext_iff, -Fin.val_eq_zero_iff, map_ofNat]

theorem rational_posDef : (gram rationalP columns).PosDef := by
  rw [rational_gram, Matrix.posDef_diagonal_iff]
  intro j
  split_ifs <;> norm_num

theorem rational_not_identity : gram rationalP columns ≠ 1 := by
  intro h
  have hh := congrFun (congrFun h 0) 0
  rw [rational_gram] at hh
  norm_num [Matrix.diagonal_apply, Matrix.one_apply] at hh

/-- An arbitrary ambient domain contains an impossible row twelve. -/
theorem ambient_e12_no_coordinates (P : M12) (c : Fin 9 → Fin 12) :
    ¬ ∃ z : V9, (source P c).mulVec z = e240 12 := by
  rintro ⟨z, h⟩
  have hh := congrFun h 12
  rw [source_row_zero P c z 12 (by norm_num)] at hh
  norm_num [e240, Pi.single_apply] at hh

/-- Rank cannot be dropped even when the nine source columns are independent. -/
theorem zero_projector_source : source (0 : M12) columns = source diagonalP columns := by
  ext i j
  by_cases hi : i.val < 12
  · let k : Fin 12 := ⟨i.val, hi⟩
    have hk : i = firstCell k := rfl
    rw [hk]
    generalize hk' : k = l
    clear hk' hk k hi i
    fin_cases l <;> fin_cases j <;>
      norm_num [source, diagonalP, columns, firstCell, Matrix.one_apply, Matrix.diagonal_apply, Fin.ext_iff, -Fin.val_eq_zero_iff]
  · simp [source, hi]

theorem zero_projector_injective : Function.Injective (source (0 : M12) columns).mulVecLin := by
  rw [zero_projector_source]
  exact positive_injective

theorem zero_projector_rank : Module.finrank ℂ (LinearMap.range (0 : M12).mulVecLin) = 0 := by
  simp

theorem zero_projector_missing : e240 0 ∈ sourceSpace (0 : M12) ∧
    ¬ ∃ z : V9, (source (0 : M12) columns).mulVec z = e240 0 := by
  constructor
  · constructor
    · intro i hi
      simp [e240, Pi.single_apply, show i ≠ 0 by intro h; subst i; omega]
    · simp
  · rintro ⟨z, h⟩
    have hh := congrFun h 0
    rw [zero_projector_source, positive_apply] at hh
    norm_num [place, e240, Pi.single_apply] at hh


theorem rational_rank : Module.finrank ℂ (LinearMap.range rationalP.mulVecLin) = 3 := by
  have hi : IsIdempotentElem rationalP.mulVecLin := by
    change rationalP.mulVecLin.comp rationalP.mulVecLin = rationalP.mulVecLin
    rw [← Matrix.mulVecLin_mul, rational_idempotent]
  have hp := (LinearMap.isProj_range_iff_isIdempotentElem rationalP.mulVecLin).mpr hi
  have h := hp.trace
  have ht : LinearMap.trace ℂ V12 rationalP.mulVecLin = 3 := by
    change LinearMap.trace ℂ V12 rationalP.toLin' = 3
    rw [Matrix.trace_toLin'_eq]
    norm_num [Matrix.trace, Matrix.diag, rationalP, Fin.sum_univ_succ, Fin.ext_iff, -Fin.val_eq_zero_iff]
  have hc : (Module.finrank ℂ (LinearMap.range rationalP.mulVecLin) : ℂ) = 3 :=
    h.symm.trans ht
  exact_mod_cast hc

theorem rational_dimension : Module.finrank ℂ (sourceSpace rationalP) = 9 :=
  sourceSpace_finrank _ rational_rank

theorem identity_source_rank : Module.finrank ℂ
    (LinearMap.range (source (1 : M12) columns).mulVecLin) = 0 := by
  rw [identity_source]
  simp

theorem identity_dimension : Module.finrank ℂ (sourceSpace (1 : M12)) = 0 := by
  have h := (1 : M12).mulVecLin.finrank_range_add_finrank_ker
  rw [identity_rank, Module.finrank_fin_fun] at h
  have he := (kernelSourceEquiv (1 : M12)).finrank_eq
  omega

theorem duplicate_not_posDef : ¬ (gram diagonalP duplicate).PosDef := by
  intro h
  have hi := gram_posDef_injective _ h
  apply duplicate_vector_nonzero
  apply hi
  simpa using duplicate_kills

theorem distinctZero_not_posDef : ¬ (gram diagonalP distinctZero).PosDef := by
  intro h
  have hi := gram_posDef_injective _ h
  apply e9_nonzero 0
  apply hi
  simpa using distinctZero_kills

/-- Exact counterexample to coverage with the rank premise omitted. -/
theorem omitted_rank_claim_false : ¬ (∀ (P : M12) (c : Fin 9 → Fin 12),
    P * P = P → Function.Injective (source P c).mulVecLin →
    LinearMap.range (source P c).mulVecLin = sourceSpace P) := by
  intro h
  have he := h 0 columns (by simp) zero_projector_injective
  have hm := zero_projector_missing.1
  rw [← he] at hm
  exact zero_projector_missing.2 hm

/-- Exact counterexample to coverage with source injectivity omitted. -/
theorem omitted_injectivity_claim_false : ¬ (∀ (P : M12) (c : Fin 9 → Fin 12),
    P * P = P → Module.finrank ℂ (LinearMap.range P.mulVecLin) = 3 →
    LinearMap.range (source P c).mulVecLin = sourceSpace P) := by
  intro h
  have he := h diagonalP duplicate diagonal_idempotent diagonal_rank
  have hm := e4_supported
  rw [← he] at hm
  exact duplicate_missing_e4 hm

end Controls

end
end SourceLaw.ColourSingletGateway.SourceRange
