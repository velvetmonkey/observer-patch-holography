import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.LinearAlgebra.Matrix.Hermitian
import Mathlib.Data.Matrix.Block
import Mathlib.Logic.Equiv.Fin.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

/-!
Exact arrival and block projector readers with Euclidean operator norms.
Projector entries and their equality to producer data are explicit inputs.
-/

namespace SourceLaw.ColourSingletGateway.FixedReaders

open scoped Matrix Matrix.Norms.L2Operator BigOperators

noncomputable section

/-- Row k selects port k + 12. -/
def arrivalPort (k : Fin 228) : Fin 240 := ⟨k.val + 12, by omega⟩

/-- The 228 by 240 arrival selector. -/
def L : Matrix (Fin 228) (Fin 240) ℂ :=
  fun k j => if j = arrivalPort k then 1 else 0

/-- The square arrival reader. -/
def R : Matrix (Fin 240) (Fin 240) ℂ := L.conjTranspose * L

/-- Exact diagonal entries of the arrival reader. -/
def arrivalDiagonal (i : Fin 240) : ℂ := if i.val < 12 then 0 else 1

private theorem arrivalPort_injective : Function.Injective arrivalPort := by
  intro a b h
  apply Fin.ext
  have := congrArg Fin.val h
  dsimp [arrivalPort] at this
  omega

/-- Exact selector algebra at every pair of ports. -/
theorem R_eq_diagonal : R = Matrix.diagonal arrivalDiagonal := by
  ext i j
  by_cases hi : 12 ≤ i.val
  · let k : Fin 228 := ⟨i.val - 12, by omega⟩
    have hk : arrivalPort k = i := by apply Fin.ext; dsimp [arrivalPort, k]; omega
    rw [R, Matrix.mul_apply, Finset.sum_eq_single k]
    · simp [Matrix.conjTranspose_apply, L, hk, Matrix.diagonal_apply,
        arrivalDiagonal, show ¬i.val < 12 by omega, eq_comm]
    · intro b _ hb
      have hbi : i ≠ arrivalPort b := by
        intro h
        have := arrivalPort_injective (hk.trans h)
        exact hb this.symm
      simp [Matrix.conjTranspose_apply, L, hbi]
    · simp
  · have hall (b : Fin 228) : i ≠ arrivalPort b := by
      intro h
      have := congrArg Fin.val h
      dsimp [arrivalPort] at this
      omega
    simp [R, Matrix.mul_apply, Matrix.conjTranspose_apply, L, hall,
      Matrix.diagonal_apply, arrivalDiagonal, show i.val < 12 by omega]

/-- The arrival reader is Hermitian. -/
theorem R_hermitian : R.IsHermitian := by
  rw [R_eq_diagonal, Matrix.isHermitian_diagonal_iff]
  intro i
  by_cases h : i.val < 12 <;> simp [arrivalDiagonal, h, isSelfAdjoint_iff]

/-- The arrival reader is idempotent. -/
theorem R_idempotent : R * R = R := by
  rw [R_eq_diagonal, Matrix.diagonal_mul_diagonal]
  congr 1
  funext i
  by_cases h : i.val < 12 <;> simp [arrivalDiagonal, h]

/-- A finite Hermitian idempotent is a Euclidean operator contraction. -/
theorem hermitian_idempotent_norm_le_one {ι : Type*} [Fintype ι] [DecidableEq ι]
    (A : Matrix ι ι ℂ) (hA : A.IsHermitian) (hAA : A * A = A) : ‖A‖ ≤ 1 := by
  have hs := hA.isSelfAdjoint.norm_mul_self
  rw [hAA] at hs
  have hn := norm_nonneg A
  nlinarith

/-- The arrival reader has Euclidean operator norm at most one. -/
theorem R_norm_le_one : ‖R‖ ≤ 1 :=
  hermitian_idempotent_norm_le_one R R_hermitian R_idempotent

/-- Twenty identical blocks on the cell and local-port index. -/
def Q (P : Matrix (Fin 12) (Fin 12) ℂ) :
    Matrix (Fin 20 × Fin 12) (Fin 20 × Fin 12) ℂ :=
  (Matrix.blockDiagonal (fun _ : Fin 20 => P)).submatrix
    (Equiv.prodComm (Fin 20) (Fin 12)) (Equiv.prodComm (Fin 20) (Fin 12))

/-- Distinct cells have zero coupling. -/
theorem Q_apply (P : Matrix (Fin 12) (Fin 12) ℂ) (a b : Fin 20 × Fin 12) :
    Q P a b = if a.1 = b.1 then P a.2 b.2 else 0 := rfl

/-- A Hermitian projector gives a Hermitian block reader. -/
theorem Q_hermitian (P : Matrix (Fin 12) (Fin 12) ℂ) (hP : P.IsHermitian) :
    (Q P).IsHermitian := by
  have h : (Matrix.blockDiagonal (fun _ : Fin 20 => P)).IsHermitian := by
    change (Matrix.blockDiagonal (fun _ : Fin 20 => P)).conjTranspose = _
    simp only [Matrix.blockDiagonal_conjTranspose, hP.eq]
  exact h.submatrix _

/-- Exact block multiplication preserves idempotence. -/
theorem Q_idempotent (P : Matrix (Fin 12) (Fin 12) ℂ) (hPP : P * P = P) :
    Q P * Q P = Q P := by
  unfold Q
  rw [Matrix.submatrix_mul_equiv, ← Matrix.blockDiagonal_mul]
  simp only [hPP]

/-- The local projector bound follows from its exact algebra. -/
theorem P_norm_le_one (P : Matrix (Fin 12) (Fin 12) ℂ)
    (hP : P.IsHermitian) (hPP : P * P = P) : ‖P‖ ≤ 1 :=
  hermitian_idempotent_norm_le_one P hP hPP

/-- The block reader bound has no norm premise. -/
theorem Q_norm_le_one (P : Matrix (Fin 12) (Fin 12) ℂ)
    (hP : P.IsHermitian) (hPP : P * P = P) : ‖Q P‖ ≤ 1 :=
  hermitian_idempotent_norm_le_one (Q P) (Q_hermitian P hP) (Q_idempotent P hPP)

/-- Cell c and local port p correspond to the global port 12*c+p. -/
def portEquiv : Fin 20 × Fin 12 ≃ Fin 240 := finProdFinEquiv

/-- Transport the block reader to the global port index. -/
def Q240 (P : Matrix (Fin 12) (Fin 12) ℂ) : Matrix (Fin 240) (Fin 240) ℂ :=
  (Q P).submatrix portEquiv.symm portEquiv.symm

/-- Transport maps each diagonal block to its stated global ports. -/
theorem Q240_apply (P : Matrix (Fin 12) (Fin 12) ℂ) (a b : Fin 20 × Fin 12) :
    Q240 P (portEquiv a) (portEquiv b) =
      if a.1 = b.1 then P a.2 b.2 else 0 := by
  simp only [Q240, Matrix.submatrix_apply, Equiv.symm_apply_apply, Q_apply]

/-- Hermiticity is preserved by the explicit port transport. -/
theorem Q240_hermitian (P : Matrix (Fin 12) (Fin 12) ℂ) (hP : P.IsHermitian) :
    (Q240 P).IsHermitian := (Q_hermitian P hP).submatrix _

/-- Idempotence is preserved by the bijective port transport. -/
theorem Q240_idempotent (P : Matrix (Fin 12) (Fin 12) ℂ) (hPP : P * P = P) :
    Q240 P * Q240 P = Q240 P := by
  unfold Q240
  rw [Matrix.submatrix_mul_equiv, Q_idempotent P hPP]

/-- The transported reader is a Euclidean operator contraction. -/
theorem Q240_norm_le_one (P : Matrix (Fin 12) (Fin 12) ℂ)
    (hP : P.IsHermitian) (hPP : P * P = P) : ‖Q240 P‖ ≤ 1 :=
  hermitian_idempotent_norm_le_one (Q240 P) (Q240_hermitian P hP)
    (Q240_idempotent P hPP)

/-- Equality to the producer projector is a separate, unproved input boundary. -/
def ProducerProjectorBinding (P producerProjector : Matrix (Fin 12) (Fin 12) ℂ) : Prop :=
  P = producerProjector

/-- Reader facts attach to producer data through an explicit equality input. -/
theorem producer_reader (P producerProjector : Matrix (Fin 12) (Fin 12) ℂ)
    (hBinding : ProducerProjectorBinding P producerProjector)
    (hP : P.IsHermitian) (hPP : P * P = P) :
    (Q240 producerProjector).IsHermitian ∧
      Q240 producerProjector * Q240 producerProjector = Q240 producerProjector ∧
      ‖Q240 producerProjector‖ ≤ 1 := by
  change P = producerProjector at hBinding
  subst producerProjector
  exact ⟨Q240_hermitian P hP, Q240_idempotent P hPP, Q240_norm_le_one P hP hPP⟩

/-- Boundary port 11 is excluded. -/
theorem R_port_11 : R 11 11 = 0 := by rw [R_eq_diagonal]; norm_num [arrivalDiagonal]

/-- Boundary port 12 is selected. -/
theorem R_port_12 : R 12 12 = 1 := by rw [R_eq_diagonal]; norm_num [arrivalDiagonal]

/-- Boundary port 239 is selected. -/
theorem R_port_239 : R 239 239 = 1 := by rw [R_eq_diagonal]; norm_num [arrivalDiagonal]

/-- The zero projector meets the reader bound. -/
theorem zero_projector_control : ‖Q240 (0 : Matrix (Fin 12) (Fin 12) ℂ)‖ ≤ 1 := by
  apply Q240_norm_le_one
  · exact Matrix.isHermitian_zero
  · simp

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

/-- A nonzero coordinate projector meets the reader bound. -/
theorem coordinate_projector_control : ‖Q240 coordinateProjector‖ ≤ 1 :=
  Q240_norm_le_one coordinateProjector coordinateProjector_hermitian
    coordinateProjector_idempotent

/-- A changed reader with only port 12 raised from one to two. -/
private def changedArrival : Matrix (Fin 240) (Fin 240) ℂ :=
  Matrix.diagonal (fun i => if i = 12 then 2 else arrivalDiagonal i)

private theorem changedArrival_only (i j : Fin 240) (h : i ≠ 12 ∨ j ≠ 12) :
    changedArrival i j = R i j := by
  rw [R_eq_diagonal]
  by_cases hij : i = j
  · subst j
    have hi : i ≠ 12 := h.elim id id
    simp [changedArrival, hi]
  · simp [changedArrival, hij]

private theorem changedArrival_coordinate :
    (changedArrival *ᵥ Pi.single 12 1) 12 = 2 := by
  simp [changedArrival]

private theorem changedArrival_norm_gt_one : 1 < ‖changedArrival‖ := by
  rw [changedArrival, Matrix.l2_opNorm_diagonal]
  have h := norm_le_pi_norm (fun i : Fin 240 =>
    if i = 12 then (2 : ℂ) else arrivalDiagonal i) 12
  norm_num at h
  linarith

private theorem doubled_identity_not_idempotent :
    ((2 : ℂ) • (1 : Matrix (Fin 12) (Fin 12) ℂ)) * ((2 : ℂ) • (1 : Matrix (Fin 12) (Fin 12) ℂ)) ≠
      (2 : ℂ) • (1 : Matrix (Fin 12) (Fin 12) ℂ) := by
  intro h
  rw [Matrix.mul_smul, Matrix.smul_mul, Matrix.one_mul] at h
  have he := congrFun (congrFun h 0) 0
  simp only [Matrix.smul_apply, Matrix.one_apply] at he
  norm_num at he

#print axioms changedArrival_only
#print axioms changedArrival_coordinate
#print axioms changedArrival_norm_gt_one
#print axioms doubled_identity_not_idempotent

#print axioms R_eq_diagonal
#print axioms R_hermitian
#print axioms R_idempotent
#print axioms hermitian_idempotent_norm_le_one
#print axioms R_norm_le_one
#print axioms P_norm_le_one
#print axioms Q_hermitian
#print axioms Q_idempotent
#print axioms Q_norm_le_one
#print axioms Q240_apply
#print axioms Q240_hermitian
#print axioms Q240_idempotent
#print axioms Q240_norm_le_one
#print axioms producer_reader
#print axioms R_port_11
#print axioms R_port_12
#print axioms R_port_239
#print axioms zero_projector_control
#print axioms coordinateProjector_hermitian
#print axioms coordinateProjector_idempotent
#print axioms coordinateProjector_nonzero
#print axioms coordinate_projector_control

#print axioms arrivalPort
#print axioms L
#print axioms R
#print axioms arrivalDiagonal
#print axioms Q
#print axioms Q_apply
#print axioms portEquiv
#print axioms Q240
#print axioms ProducerProjectorBinding
#print axioms coordinateProjector

end

end SourceLaw.ColourSingletGateway.FixedReaders
