import ObserverPatchHolography.CollarStates

/-!
# State-side collar states — T1: the reversal exhibit (#544)

T0 (`CollarStates.lean`) showed the paper's current admissible-channel
requirements cannot force the central-interface collar clause: the
identity channel keeps the non-central family `{uuC, XXC}` at closure
defect zero.  T1 sharpens the boundary from the other side: over ℂ the
ℤ-obstruction of `no_integral_flux_retraction` *reverses* — the
Hilbert–Schmidt-orthogonal conditional expectation

  `Eflux : m ↦ (tr m)/4 • 1 + (tr (uuC·m))/4 • uuC`

onto the flux subalgebra `span{1, uuC}` exists, is an admissible channel
(linear, positive, trace-preserving), fixes the flux sector pointwise,
and genuinely annihilates the coupling `XXC`.  And *even so*, coarse-
graining the realized MaxEnt branch of `{uuC, XXC}` by `Eflux` lands
inside the same exponential family with closure defect exactly zero:
the transport identity

  `Eflux (gibbsM ![uuC, XXC] lam) = gibbsM ![uuC, XXC] ![lam 0, 0]`

(coordinate erasure of the coupling multiplier) exhibits the coarse-
grained state as the central member at `lam' = ![lam 0, 0]`.  Possession
of the excluding map still does not *force* the clause — it merely
*deselects* the coupling on the coarse side.  This is the force-vs-select
gap: T1 re-characterizes #544, it does not close it; strengthening the
admissible class at the axiom level (T2) stays out of scope.

Everything here rides T0's banked spectral machinery (`specProjP`,
`gibbsM_spectral`, the family Klein inequality); no new analytic
machinery, no `Matrix.exp`, no Kubo–Mori.
-/

namespace OPH

open Matrix

/-! ## T1-S1 — the flux conditional expectation and the transport identity -/

/-- The flux conditional expectation as a raw linear map: the
    Hilbert–Schmidt-orthogonal projection of the collar algebra onto the
    flux subalgebra `span{1, uuC}` (the map whose ℤ-integral avatar was
    impossible by `no_integral_flux_retraction`). -/
noncomputable def EfluxL : CollarC →ₗ[ℂ] CollarC where
  toFun m := (m.trace / 4) • (1 : CollarC) + ((uuC * m).trace / 4) • uuC
  map_add' m n := by
    rw [Matrix.trace_add, mul_add, Matrix.trace_add, add_div, add_div,
      add_smul, add_smul]
    abel
  map_smul' c m := by
    simp only [Matrix.mul_smul, Matrix.trace_smul, smul_eq_mul,
      RingHom.id_apply, smul_add, smul_smul, mul_div_assoc]

@[simp] theorem EfluxL_apply (m : CollarC) :
    EfluxL m = (m.trace / 4) • (1 : CollarC) + ((uuC * m).trace / 4) • uuC :=
  rfl

/-- `uuC` acts by its sign on each joint spectral projection. -/
theorem uuC_mul_specProjP (p : Fin 2 × Fin 2) :
    uuC * specProjP p = ((sgnR p.1 : ℝ) : ℂ) • specProjP p := by
  rw [specProjP, ← mul_assoc, uuC_mul_quP, Matrix.smul_mul]

theorem uuC_mul_specProjP_trace (p : Fin 2 × Fin 2) :
    (uuC * specProjP p).trace = ((sgnR p.1 : ℝ) : ℂ) := by
  rw [uuC_mul_specProjP, Matrix.trace_smul, specProjP_trace, smul_eq_mul,
    mul_one]

/-- The action of the flux expectation on the joint spectral basis:
    each sector projection is sent to half the corresponding `uuC`
    half-projection — the coupling direction is forgotten, the charge
    direction is kept. -/
theorem Eflux_specProjP (p : Fin 2 × Fin 2) :
    EfluxL (specProjP p) = (2 : ℂ)⁻¹ • quP p.1 := by
  rw [EfluxL_apply, specProjP_trace, uuC_mul_specProjP_trace, quP,
    smul_smul, smul_add, smul_smul]
  congr 1
  · congr 1
    norm_num
  · congr 1
    rw [div_eq_mul_inv, mul_comm]
    norm_num [mul_comm]

/-- The `uuC` half-projections are the fibre sums of the joint spectral
    projections. -/
theorem sum_specProjP_fibre (s : Fin 2) :
    ∑ t : Fin 2, specProjP (s, t) = quP s := by
  simp only [specProjP]
  rw [← Finset.mul_sum, sum_qxP, mul_one]

/-- Coordinate erasure at the eigenvalue level: killing the second
    multiplier removes the coupling contribution to every sector
    eigenvalue. -/
theorem eigval_erase (lam : Fin 2 → ℝ) (p : Fin 2 × Fin 2) :
    eigval ![lam 0, 0] p = lam 0 * sgnR p.1 := by
  simp [eigval]

/-- The Gibbs weights of the erased family are constant along the
    coupling fibre. -/
theorem gibbsProb_erase (lam : Fin 2 → ℝ) (p : Fin 2 × Fin 2) :
    gibbsProb ![lam 0, 0] p
      = Real.exp (-(lam 0 * sgnR p.1)) / partitionZ ![lam 0, 0] := by
  rw [gibbsProb, eigval_erase]

/-- The partition function of the commuting family factorizes over the
    two spectral directions. -/
theorem partitionZ_factor (lam : Fin 2 → ℝ) :
    partitionZ lam
      = (∑ s : Fin 2, Real.exp (-(lam 0 * sgnR s)))
        * (∑ t : Fin 2, Real.exp (-(lam 1 * sgnR t))) := by
  rw [partitionZ, Fintype.sum_prod_type, Finset.sum_mul_sum]
  refine Finset.sum_congr rfl fun s _ => Finset.sum_congr rfl fun t _ => ?_
  rw [eigval, neg_add, Real.exp_add]

/-- **The marginal identity** — the scalar heart of the transport: the
    halved coupling-fibre marginal of the joint Gibbs weights equals the
    erased-family Gibbs weight.  Pure `Real.exp` arithmetic on the
    factorized partition functions. -/
theorem gibbsProb_marginal (lam : Fin 2 → ℝ) (s : Fin 2) :
    (∑ t : Fin 2, gibbsProb lam (s, t)) / 2
      = Real.exp (-(lam 0 * sgnR s)) / partitionZ ![lam 0, 0] := by
  have hZU : (0 : ℝ) < ∑ u : Fin 2, Real.exp (-(lam 0 * sgnR u)) :=
    Finset.sum_pos (fun _ _ => Real.exp_pos _) Finset.univ_nonempty
  have hZX : (0 : ℝ) < ∑ t : Fin 2, Real.exp (-(lam 1 * sgnR t)) :=
    Finset.sum_pos (fun _ _ => Real.exp_pos _) Finset.univ_nonempty
  have hterm : ∀ t : Fin 2, gibbsProb lam (s, t)
      = Real.exp (-(lam 0 * sgnR s)) * Real.exp (-(lam 1 * sgnR t))
        / partitionZ lam := by
    intro t
    rw [gibbsProb, eigval, neg_add, Real.exp_add]
  have hnum : ∑ t : Fin 2, gibbsProb lam (s, t)
      = Real.exp (-(lam 0 * sgnR s))
        * (∑ t : Fin 2, Real.exp (-(lam 1 * sgnR t))) / partitionZ lam := by
    rw [Finset.sum_congr rfl fun t _ => hterm t, ← Finset.sum_div,
      ← Finset.mul_sum]
  have hZ' : partitionZ ![lam 0, 0]
      = (∑ u : Fin 2, Real.exp (-(lam 0 * sgnR u))) * 2 := by
    rw [partitionZ_factor]
    norm_num [Fin.sum_univ_two, Matrix.cons_val_zero, Matrix.cons_val_one,
      Matrix.head_cons]
  rw [hnum, partitionZ_factor lam, hZ']
  field_simp [hZU.ne', hZX.ne']

/-- **T1 transport identity (the crux)**: coarse-graining the realized
    Gibbs state of the non-central family by the flux expectation lands
    exactly on the family member with the coupling multiplier erased,
    `lam' = ![lam 0, 0]`.  The I-projection infimum is therefore hit at
    an explicit central point — no optimization, no Kubo–Mori. -/
theorem Eflux_transport (lam : Fin 2 → ℝ) :
    EfluxL (gibbsM SFam lam) = gibbsM SFam ![lam 0, 0] := by
  rw [gibbsM_spectral lam, map_sum, gibbsM_spectral ![lam 0, 0],
    Fintype.sum_prod_type, Fintype.sum_prod_type]
  refine Finset.sum_congr rfl fun s _ => ?_
  have hL : ∑ t : Fin 2,
        EfluxL (((gibbsProb lam (s, t) : ℝ) : ℂ) • specProjP (s, t))
      = (((∑ t : Fin 2, gibbsProb lam (s, t)) / 2 : ℝ) : ℂ) • quP s := by
    have step : ∀ t : Fin 2,
        EfluxL (((gibbsProb lam (s, t) : ℝ) : ℂ) • specProjP (s, t))
          = ((gibbsProb lam (s, t) / 2 : ℝ) : ℂ) • quP s := by
      intro t
      rw [map_smul, Eflux_specProjP, smul_smul]
      congr 1
      rw [Complex.ofReal_div, div_eq_mul_inv]
      norm_num
    rw [Finset.sum_congr rfl fun t _ => step t, ← Finset.sum_smul]
    congr 1
    rw [← Complex.ofReal_sum]
    congr 1
    exact (Finset.sum_div _ _ _).symm
  have hR : ∑ t : Fin 2,
        ((gibbsProb ![lam 0, 0] (s, t) : ℝ) : ℂ) • specProjP (s, t)
      = ((Real.exp (-(lam 0 * sgnR s)) / partitionZ ![lam 0, 0] : ℝ) : ℂ)
          • quP s := by
    have step : ∀ t : Fin 2,
        ((gibbsProb ![lam 0, 0] (s, t) : ℝ) : ℂ) • specProjP (s, t)
          = ((Real.exp (-(lam 0 * sgnR s)) / partitionZ ![lam 0, 0] : ℝ) : ℂ)
              • specProjP (s, t) := by
      intro t
      rw [gibbsProb_erase]
    rw [Finset.sum_congr rfl fun t _ => step t, ← Finset.smul_sum,
      sum_specProjP_fibre]
  rw [hL, hR, gibbsProb_marginal]

end OPH
