import Mathlib.Data.Nat.Factorial.Basic
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum

/-!
# Fixed colour certificate scalar bounds

These rational constants are the four scalar fields of
`model/experiments/interval_echo_gauge/singlet_leakage_bound/certificate.json`.
The lemmas check these fixed values. They do not read certificate bytes or
check a changed input. The finite error expression has no analytic bound
attached to it.
-/

namespace SourceLaw.ColourScalarBounds

/-- Fixed certificate multiplier for the leakage constraint. -/
def mu : ℚ := 2759827018809 / 125000000000

/-- Fixed certificate multiplier for normalization. -/
def lambda : ℚ := 1112397567 / 125000000000

/-- Fixed certificate lower endpoint. -/
def lower : ℚ := 1936098413 / 62500000000

/-- Fixed certificate upper endpoint. -/
def upper : ℚ := 3872224598309 / 125000000000000

theorem mu_nonneg : 0 ≤ mu := by
  norm_num [mu]

theorem objective_exact : lambda + mu / 1000 = 3872224585809 / 125000000000000 := by
  norm_num [lambda, mu]

theorem objective_le_upper : lambda + mu / 1000 ≤ upper := by
  norm_num [lambda, mu, upper]

theorem bracket_width : 0 < upper - lower ∧ upper - lower ≤ 1 / 1000 := by
  norm_num [upper, lower]

/-- The same fixed objective strictly exceeds the planted upper endpoint. -/
theorem planted_objective_failure : lower - 1 / 10000 < lambda + mu / 1000 := by
  norm_num [lower, lambda, mu]

/-- Denominator in the finite geometric error expression. -/
def errorDenominator : ℚ := 1 - 3 / 42

/-- Exact rational tail expression for degree forty. -/
def e : ℚ := ((3 : ℚ) ^ 41 / (Nat.factorial 41 : ℚ)) / errorDenominator

/-- Exact rational expression for the quadratic error. -/
def eta : ℚ := 2 * e + e ^ 2

theorem error_denominator_pos : 0 < errorDenominator := by
  norm_num [errorDenominator]

theorem factorial_denominator_pos : (0 : ℚ) < (Nat.factorial 41 : ℚ) := by
  norm_num [Nat.factorial]

theorem e_nonneg : 0 ≤ e := by
  norm_num [e, errorDenominator, Nat.factorial]

theorem eta_nonneg : 0 ≤ eta := by
  exact add_nonneg (mul_nonneg (by norm_num) e_nonneg) (sq_nonneg e)

end SourceLaw.ColourScalarBounds

#print axioms SourceLaw.ColourScalarBounds.mu_nonneg
#print axioms SourceLaw.ColourScalarBounds.objective_exact
#print axioms SourceLaw.ColourScalarBounds.objective_le_upper
#print axioms SourceLaw.ColourScalarBounds.bracket_width
#print axioms SourceLaw.ColourScalarBounds.planted_objective_failure
#print axioms SourceLaw.ColourScalarBounds.error_denominator_pos
#print axioms SourceLaw.ColourScalarBounds.factorial_denominator_pos
#print axioms SourceLaw.ColourScalarBounds.e_nonneg
#print axioms SourceLaw.ColourScalarBounds.eta_nonneg
