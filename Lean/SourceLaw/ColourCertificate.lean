import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Tactic

/-! Conditional bounds for nine complex source coordinates. Numerical matrix
premises and the witness inequalities require separate proofs. -/
noncomputable section
namespace SourceLaw.ColourCertificate
open Matrix Complex
open scoped BigOperators ComplexOrder
abbrev N := Fin 9
abbrev M := Matrix N N ℂ

def q (C : M) (z : N → ℂ) : ℝ :=
  (∑ i, star (z i) * (C.mulVec z) i).re

def rho (B : M) : M := B * B.conjTranspose

def E (C B : M) : ℝ := (Matrix.trace (C * rho B)).re

private lemma q_add (C D : M) (z : N → ℂ) :
    q (C + D) z = q C z + q D z := by
  simp [q, Matrix.add_mulVec, mul_add, Finset.sum_add_distrib]

private lemma q_sub (C D : M) (z : N → ℂ) :
    q (C - D) z = q C z - q D z := by
  simp [q, Matrix.sub_mulVec, mul_sub, Finset.sum_sub_distrib]

private lemma q_smul (a : ℝ) (C : M) (z : N → ℂ) :
    q (a • C) z = a * q C z := by
  unfold q
  have h : (∑ i, star (z i) * ((a • C).mulVec z) i) =
      (a : ℂ) * ∑ i, star (z i) * (C.mulVec z) i := by
    simp only [Matrix.mulVec, dotProduct, Matrix.smul_apply, Complex.real_smul,
      Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i _
    apply Finset.sum_congr rfl
    intro j _
    ring
  rw [h]
  simp [Complex.mul_re]

private lemma q_nonneg {C : M} (h : C.PosSemidef) (z : N → ℂ) :
    0 ≤ q C z := by
  exact (h.dotProduct_mulVec_nonneg z).1

/-- Trace energy is the sum of the full complex column forms. -/
private lemma E_eq_sum (C B : M) :
    E C B = ∑ j, q C (fun i => B i j) := by
  unfold E rho
  rw [← Matrix.mul_assoc, Matrix.trace_mul_cycle]
  rw [Matrix.mul_assoc]
  simp only [Matrix.trace, Matrix.diag, Matrix.mul_apply, Matrix.conjTranspose_apply,
    q, Matrix.mulVec, dotProduct, Finset.mul_sum]
  exact map_sum Complex.reAddGroupHom
    (fun j : N => ∑ i : N, ∑ k : N, star (B i j) * (C i k * B k j)) Finset.univ

private lemma E_nonneg {C : M} (h : C.PosSemidef) (B : M) :
    0 ≤ E C B := by
  rw [E_eq_sum]
  exact Finset.sum_nonneg fun j _ => q_nonneg h _

private lemma E_add (C D B : M) : E (C + D) B = E C B + E D B := by
  simp [E_eq_sum, q_add, Finset.sum_add_distrib]

private lemma E_sub (C D B : M) : E (C - D) B = E C B - E D B := by
  simp [E_eq_sum, q_sub, Finset.sum_sub_distrib]

private lemma E_smul (a : ℝ) (C B : M) : E (a • C) B = a * E C B := by
  simp [E_eq_sum, q_smul, Finset.mul_sum]

/-- Error bounds give witness bounds and an upper bound for each factored
 density, including singular factors and imaginary coherences. -/
theorem robust_certificate
    (W A G Ap Gp : M) (v : N → ℂ)
    (eta mu lambda lower upper : ℝ)
    (hW : W.IsHermitian) (hA : A.IsHermitian) (hG : G.IsHermitian)
    (hAp : Ap.IsHermitian) (hGp : Gp.IsHermitian)
    (hEta : 0 ≤ eta) (hMu : 0 ≤ mu)
    (hAminus : (eta • (1 : M) + A - Ap).PosSemidef)
    (hAplus : (eta • (1 : M) + Ap - A).PosSemidef)
    (hGminus : (eta • (1 : M) + G - Gp).PosSemidef)
    (hGplus : (eta • (1 : M) + Gp - G).PosSemidef)
    (hDual : (lambda • W + mu • Gp - Ap - ((1 + mu) * eta) • (1 : M)).PosSemidef)
    (hObjective : lambda + mu / 1000 ≤ upper)
    (hn : 0 < q W v)
    (hWitnessLeak : q Gp v + eta * q (1 : M) v ≤ q W v / 1000)
    (hWitnessArrival : lower * q W v ≤ q Ap v - eta * q (1 : M) v)
    (hWidth : upper - lower ≤ 1 / 1000) :
    q G v / q W v ≤ 1 / 1000 ∧ lower ≤ q A v / q W v ∧
    (∀ B : M, E W B = 1 → E G B ≤ 1 / 1000 → E A B ≤ upper) ∧
    upper - lower ≤ 1 / 1000 := by
  have hg := q_nonneg hGplus v
  have ha := q_nonneg hAminus v
  simp only [q_sub, q_add, q_smul] at hg ha
  have hd : (lambda • W + mu • G - A).PosSemidef := by
    have hs : (mu • (eta • (1 : M) + G - Gp)).PosSemidef := by
      convert hGminus.smul (show (0 : ℂ) ≤ (mu : ℂ) from ⟨hMu, rfl⟩) using 1
    convert (hDual.add hs).add hAplus using 1
    module
  refine ⟨(div_le_iff₀ hn).2 (by linarith),
    (le_div_iff₀ hn).2 (by linarith), ?_, hWidth⟩
  intro B hw hgB
  have he := E_nonneg hd B
  simp only [E_sub, E_add, E_smul, hw, mul_one] at he
  have hm := mul_le_mul_of_nonneg_left hgB hMu
  linarith

/-- Exact rational objective comparison, checked by kernel arithmetic. -/
theorem certificate_objective :
    ((8899180536 / 1000000000000 : ℚ) : ℝ) +
      ((22078616150472 / 1000000000000 : ℚ) : ℝ) / 1000 ≤
      ((3872224598309 / 125000000000000 : ℚ) : ℝ) := by
  norm_num
end SourceLaw.ColourCertificate
#print axioms SourceLaw.ColourCertificate.robust_certificate

#print axioms SourceLaw.ColourCertificate.certificate_objective
