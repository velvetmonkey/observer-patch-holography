import SourceLaw.ColourSingletGateway.TaylorError
import SourceLaw.ColourSingletGateway.UnitaryEvolution
import SourceLaw.ColourSingletGateway.QuadraticError

/-!
Uniform degree-40 state and reader error bounds for finite complex matrices.
All matrix norms are induced Euclidean operator norms. The hypotheses concern
an arbitrary Hermitian generator, rectangular source and contraction reader.
No fixed certificate data or physical transport premise is attached.
-/

namespace SourceLaw.ColourSingletGateway.StateApproximation

open scoped Matrix.Norms.L2Operator
open Matrix
open UnitaryEvolution

noncomputable section

variable {n m : Type*} [Fintype n] [DecidableEq n] [Nonempty n]
  [Fintype m] [DecidableEq m] [Nonempty m]

/-- The explicit degree-40 exponential polynomial. -/
def P40 (H : Matrix n n ℂ) (t : ℝ) : Matrix n n ℂ :=
  ∑ k ∈ Finset.range 41, ((k.factorial : ℂ)⁻¹) • Z H t ^ k

/-- The exact rectangular state. -/
def X (H : Matrix n n ℂ) (S : Matrix n m ℂ) (t : ℝ) : Matrix n m ℂ :=
  U H t * S

/-- The polynomial rectangular state. -/
def Y (H : Matrix n n ℂ) (S : Matrix n m ℂ) (t : ℝ) : Matrix n m ℂ :=
  P40 H t * S

/-- The uniform state remainder majorant. -/
def e : ℝ := ((3 : ℝ) ^ 41 / ((41 : ℕ).factorial : ℝ)) / (1 - (3 : ℝ) / 42)

/-- The reader error budget. -/
def eta : ℝ := 2 * e + e ^ 2

theorem e_nonneg : 0 ≤ e := by unfold e; positivity

theorem eta_nonneg : 0 ≤ eta := by
  exact add_nonneg (mul_nonneg (by norm_num) e_nonneg) (sq_nonneg e)

omit [Nonempty n] in
/-- The time interval and generator norm give the Taylor theorem's input bound. -/
theorem norm_Z_le_three (H : Matrix n n ℂ) (hHnorm : ‖H‖ ≤ 3)
    (t : ℝ) (ht : t ∈ Set.Icc (0 : ℝ) 1) : ‖Z H t‖ ≤ 3 := by
  have hscalar : ‖(-Complex.I) * (t : ℂ)‖ = t := by
    simp [abs_of_nonneg ht.1]
  rw [Z, norm_smul, hscalar]
  calc
    t * ‖H‖ ≤ 1 * 3 := mul_le_mul ht.2 hHnorm (norm_nonneg _) (by norm_num)
    _ = 3 := by ring

omit [Nonempty m] in
/-- Submultiplicativity transports the analytic tail to a rectangular source. -/
theorem state_error (H : Matrix n n ℂ) (hHnorm : ‖H‖ ≤ 3)
    (S : Matrix n m ℂ) (hS : ‖S‖ ≤ 1)
    (t : ℝ) (ht : t ∈ Set.Icc (0 : ℝ) 1) : ‖X H S t - Y H S t‖ ≤ e := by
  have htail := TaylorError.uniform_exp_tail40 (Z H t) (norm_Z_le_three H hHnorm t ht)
  change ‖U H t * S - P40 H t * S‖ ≤ e
  rw [← Matrix.sub_mul]
  calc
    _ ≤ ‖U H t - P40 H t‖ * ‖S‖ := Matrix.l2_opNorm_mul _ _
    _ ≤ e * 1 := mul_le_mul htail hS (norm_nonneg _) e_nonneg
    _ = e := mul_one e

omit [Nonempty m] in
/-- Hermiticity and the source contraction bound control the exact state. -/
theorem exact_state_contraction (H : Matrix n n ℂ) (hH : H.IsHermitian)
    (S : Matrix n m ℂ) (hS : ‖S‖ ≤ 1) (t : ℝ) : ‖X H S t‖ ≤ 1 :=
  norm_U_mul_le_one H hH S hS t

/-- Combined analytic state and reader bounds with explicit source hypotheses. -/
theorem state_reader_error (H : Matrix n n ℂ) (hH : H.IsHermitian)
    (hHnorm : ‖H‖ ≤ 3) (S : Matrix n m ℂ) (hS : ‖S‖ ≤ 1)
    (R : Matrix n n ℂ) (hR : ‖R‖ ≤ 1)
    (t : ℝ) (ht : t ∈ Set.Icc (0 : ℝ) 1) :
    ‖Z H t‖ ≤ 3 ∧ ‖X H S t - Y H S t‖ ≤ e ∧ ‖X H S t‖ ≤ 1 ∧
      ‖(X H S t)ᴴ * R * X H S t - (Y H S t)ᴴ * R * Y H S t‖ ≤ eta := by
  have hXY := state_error H hHnorm S hS t ht
  have hX := exact_state_contraction H hH S hS t
  exact ⟨norm_Z_le_three H hHnorm t ht, hXY, hX,
    QuadraticError.reader_quadratic_error _ _ R e e_nonneg hX hXY hR⟩

/-- A nonzero source with two rows and one column. -/
def source2 : Matrix (Fin 2) (Fin 1) ℂ := !![1; 0]

theorem source2_norm : ‖source2‖ = 1 := by
  have hgram : source2ᴴ * source2 = 1 := by
    ext i j
    fin_cases i
    fin_cases j
    norm_num [source2, Matrix.mul_apply, Fin.sum_univ_two]
  have hnorm := Matrix.l2_opNorm_conjTranspose_mul_self source2
  rw [hgram, norm_one] at hnorm
  have := norm_nonneg source2
  nlinarith

/-- The zero generator obeys the assembled theorem at both endpoints. -/
theorem zero_endpoints (t : ℝ) (ht : t = 0 ∨ t = 1) :
    ‖X (0 : Matrix (Fin 2) (Fin 2) ℂ) source2 t - Y 0 source2 t‖ ≤ e ∧
    ‖(X 0 source2 t)ᴴ * (1 : Matrix (Fin 2) (Fin 2) ℂ) * X 0 source2 t -
      (Y 0 source2 t)ᴴ * (1 : Matrix (Fin 2) (Fin 2) ℂ) * Y 0 source2 t‖ ≤ eta := by
  have h := state_reader_error (0 : Matrix (Fin 2) (Fin 2) ℂ)
    Matrix.isHermitian_zero (by simp) source2 (by rw [source2_norm])
    1 (by simp) t (by rcases ht with rfl | rfl <;> constructor <;> norm_num)
  exact ⟨h.2.1, h.2.2.2⟩

/-- A nonzero Hermitian generator and rectangular source at both endpoints. -/
theorem nonzero_endpoints (t : ℝ) (ht : t = 0 ∨ t = 1) :
    ‖X (1 : Matrix (Fin 2) (Fin 2) ℂ) source2 t - Y 1 source2 t‖ ≤ e ∧
    ‖(X 1 source2 t)ᴴ * (1 : Matrix (Fin 2) (Fin 2) ℂ) * X 1 source2 t -
      (Y 1 source2 t)ᴴ * (1 : Matrix (Fin 2) (Fin 2) ℂ) * Y 1 source2 t‖ ≤ eta := by
  have h := state_reader_error (1 : Matrix (Fin 2) (Fin 2) ℂ)
    Matrix.isHermitian_one (by simp) source2 (by rw [source2_norm])
    1 (by simp) t (by rcases ht with rfl | rfl <;> constructor <;> norm_num)
  exact ⟨h.2.1, h.2.2.2⟩

/-- Omitting the source contraction premise allows an exact norm of two. -/
theorem source_contraction_control (t : ℝ) :
    ¬ ‖X (0 : Matrix (Fin 2) (Fin 2) ℂ) ((2 : ℂ) • (1 : Matrix (Fin 2) (Fin 2) ℂ)) t‖ ≤ 1 := by
  norm_num [X, U_zero, norm_smul]

/-- A Hermitian generator of norm four is outside the assembled theorem's domain. -/
theorem generator_norm_control :
    ¬ ‖((4 : ℂ) • (1 : Matrix (Fin 2) (Fin 2) ℂ))‖ ≤ 3 := by
  norm_num [norm_smul]

end

#print axioms SourceLaw.ColourSingletGateway.StateApproximation.e_nonneg
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.eta_nonneg
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.norm_Z_le_three
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.state_error
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.exact_state_contraction
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.state_reader_error
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.source2_norm
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.zero_endpoints
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.nonzero_endpoints
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.source_contraction_control
#print axioms SourceLaw.ColourSingletGateway.StateApproximation.generator_norm_control

end SourceLaw.ColourSingletGateway.StateApproximation
