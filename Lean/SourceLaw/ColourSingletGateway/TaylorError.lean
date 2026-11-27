import Mathlib.Analysis.Normed.Algebra.Exponential
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Tactic

/-!
The degree-40 exponential tail in a complete complex normed algebra.
The norm is submultiplicative and the unit has norm one. For matrices, the caller
must select a normed algebra instance, such as the Euclidean operator norm.
-/

namespace SourceLaw.ColourSingletGateway.TaylorError

private noncomputable def termBound (n : ℕ) : ℝ := (3 : ℝ) ^ n / (n.factorial : ℝ)

private lemma termBound_nonneg (n : ℕ) : 0 ≤ termBound n := by
  unfold termBound
  positivity

private lemma termBound_step (n : ℕ) :
    termBound (n + 1) = termBound n * 3 / (n + 1 : ℝ) := by
  unfold termBound
  rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one, pow_succ]
  field_simp

private lemma shifted_majorant (n : ℕ) :
    termBound (n + 41) ≤ termBound 41 * ((3 : ℝ) / 42) ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
    have hn : (42 : ℝ) ≤ (n + 41 : ℕ) + 1 := by norm_cast; omega
    calc
      termBound (n + 1 + 41) = termBound (n + 41) * 3 / ((n + 41 : ℕ) + 1 : ℝ) := by
        rw [show n + 1 + 41 = (n + 41) + 1 by omega, termBound_step]
      _ ≤ termBound (n + 41) * 3 / 42 := by
        exact div_le_div_of_nonneg_left (mul_nonneg (termBound_nonneg _) (by norm_num))
          (by norm_num) hn
      _ ≤ (termBound 41 * ((3 : ℝ) / 42) ^ n) * 3 / 42 := by
        gcongr
      _ = termBound 41 * ((3 : ℝ) / 42) ^ (n + 1) := by rw [pow_succ]; ring

/-- Uniform tail bound. No Hermitian or commutative multiplication premise is needed. -/
theorem uniform_exp_tail40 {A : Type*} [NormedRing A] [NormOneClass A] [NormedAlgebra ℂ A]
    [CompleteSpace A] (Z : A) (hZ : ‖Z‖ ≤ 3) :
    ‖NormedSpace.exp Z - ∑ k ∈ Finset.range 41, ((k.factorial : ℂ)⁻¹) • Z ^ k‖ ≤
      ((3 : ℝ) ^ 41 / ((41 : ℕ).factorial : ℝ)) / (1 - (3 : ℝ) / 42) := by
  let f : ℕ → A := fun k => ((k.factorial : ℂ)⁻¹) • Z ^ k
  have hf : Summable f := NormedSpace.expSeries_summable' Z
  have hexp : (∑' k, f k) = NormedSpace.exp Z :=
    (NormedSpace.exp_series_hasSum_exp' Z).tsum_eq
  have hterm (k : ℕ) : ‖f k‖ ≤ termBound k := by
    dsimp [f, termBound]
    rw [norm_smul, norm_inv, Complex.norm_natCast]
    calc
      (↑k.factorial : ℝ)⁻¹ * ‖Z ^ k‖ ≤ (↑k.factorial : ℝ)⁻¹ * ‖Z‖ ^ k := by
        gcongr
        exact norm_pow_le Z k
      _ ≤ (↑k.factorial : ℝ)⁻¹ * 3 ^ k := by gcongr
      _ = 3 ^ k / (↑k.factorial : ℝ) := by ring
  have htail : HasSum (fun n => f (n + 41)) (∑' n, f (n + 41)) :=
    (hf.comp_injective (fun _ _ h => Nat.add_right_cancel h)).hasSum
  have hbound := norm_sub_le_of_geometric_bound_of_hasSum
    (by norm_num : (3 : ℝ) / 42 < 1)
    (fun n => (hterm (n + 41)).trans (shifted_majorant n)) htail 0
  have hsplit := hf.sum_add_tsum_nat_add 41
  rw [hexp] at hsplit
  have heq : NormedSpace.exp Z - ∑ k ∈ Finset.range 41, f k = ∑' n, f (n + 41) := by
    rw [← hsplit]
    abel
  rw [heq]
  simpa [termBound] using hbound

end SourceLaw.ColourSingletGateway.TaylorError
