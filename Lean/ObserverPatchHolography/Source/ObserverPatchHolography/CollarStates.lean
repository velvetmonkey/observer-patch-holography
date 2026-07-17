import ObserverPatchHolography.CollarLayer

/-!
# #544 state-side layer: T0 — the identity-channel no-go with real states

This file crosses the rail that `CollarLayer.lean` deliberately does not:
it puts *states* (positive semidefinite, trace-one matrices), the matrix
logarithm (continuous functional calculus), Umegaki relative entropy, and
the closure defect of the paper's `def:closure-defect` on the ℂ-lift of
the model collar layer.  The HARD RAIL of `CollarLayer.lean` ("no
C*-analysis, no GNS/spectra/Hilbert spaces") remains true OF THAT FILE;
the analytic content lives here and only here.

Scope (T0 only, per the scoping report `oph-544-state-side-scoping-report-
2026-07-17.md` §1.1 and §4, bricks S1–S4):

* **S1** — ℂ-lift of the model layer: `CollarC`, `uuC`/`XXC`/`pPlusC`,
  the lifted layer `modelLayerC`, and the cross-cut/flux/invariance facts,
  transferred from the kernel-`decide`d ℤ facts through the entrywise
  cast ring hom (no re-proving over ℂ).
* **S2** — `DensityMatrix`, the spectral projections of the commuting
  pair `{uuC, XXC}`, and the Gibbs states of the retained family via
  `NormedSpace.exp`.
* **S3** — matrix log via the continuous functional calculus
  (`CFC.log = cfc Real.log`; Mathlib has no `Matrix.log`), Umegaki
  relative entropy, `relEntropy_self`, and the family Klein inequality
  (relative entropy is nonnegative *between Gibbs states of the retained
  family*) — the commuting family reduces it to the classical
  finite-probability Gibbs inequality; no Kubo–Mori machinery.
* **S4** — admissible channels (linear, positive, trace-preserving — the
  requirements named in `rem:msascope`, nothing more), the closure defect
  of `def:closure-defect`, and the T0 theorem
  `stateSide_currentAxioms_cannot_force`.

**Claim discipline (non-negotiable).**  T0 *sharpens* #544; it does NOT
close it.  It shows the paper's current admissible-channel requirements
cannot force the central-interface collar clause, because the identity
channel is admissible and discharges refinement closure with closure
defect exactly zero on a non-central family.  Forcing remains impossible
until the admissible class is strengthened at the axiom level (T2 —
explicitly out of scope here).

Anti-smuggling discipline (report §3): `AdmissibleChannel` is
witness-free — its definition mentions positivity and trace preservation
only, never `uuC`, `XXC`, the flux sector, or the clause.
-/

namespace OPH

open Kronecker Matrix

/-! ## S1 — the ℂ-lift of the model layer

Everything is transferred from the kernel-`decide`d ℤ-matrix facts of
`CollarLayer.lean` through the entrywise cast ring hom `liftC`; nothing
is re-proved entrywise over ℂ. -/

/-- The state-side collar algebra: `M₂(ℂ) ⊗ M₂(ℂ)`. -/
abbrev CollarC : Type := Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℂ

/-- Entrywise scalar lift `ℤ → ℂ` of the model collar ring, as a ring hom. -/
noncomputable def liftC : CollarM →+* CollarC :=
  (Int.castRingHom ℂ).mapMatrix

@[simp] theorem liftC_apply (m : CollarM) (i j : Fin 2 × Fin 2) :
    liftC m i j = (m i j : ℂ) := rfl

/-- The boundary charge `u ⊗ u` over ℂ. -/
noncomputable def uuC : CollarC := liftC uu

/-- The invariant-but-non-central cross coupling `X ⊗ X` over ℂ. -/
noncomputable def XXC : CollarC := liftC XX

/-- The sector projector `(1 + u⊗u)/2` — the element whose image was
    ℤ-impossible for any integral flux retraction
    (`no_integral_flux_retraction`); over ℂ it is an honest projection. -/
noncomputable def pPlusC : CollarC := (2 : ℂ)⁻¹ • (1 + uuC)

/-! ### ℤ-side kernel-`decide` facts (new ones needed by the state layer) -/

theorem uu_sq : uu * uu = 1 := by decide

theorem XX_sq : XX * XX = 1 := by decide

theorem uu_symm : ∀ i j, uu i j = uu j i := by decide

theorem XX_symm : ∀ i j, XX i j = XX j i := by decide

theorem uu_trace_eq : uu.trace = 0 := by decide

theorem XX_trace_eq : XX.trace = 0 := by decide

theorem uu_mul_XX_trace_eq : (uu * XX).trace = 0 := by decide

/-! ### Transferred ℂ facts -/

theorem uuC_sq : uuC * uuC = 1 := by
  rw [uuC, ← map_mul, uu_sq, map_one]

theorem XXC_sq : XXC * XXC = 1 := by
  rw [XXC, ← map_mul, XX_sq, map_one]

theorem uuC_comm_XXC : uuC * XXC = XXC * uuC := by
  rw [uuC, XXC, ← map_mul, ← map_mul, uu_comm_XX]

theorem liftC_trace (m : CollarM) : (liftC m).trace = (m.trace : ℂ) := by
  simp [Matrix.trace, Matrix.diag]

theorem uuC_trace : uuC.trace = 0 := by
  rw [uuC, liftC_trace, uu_trace_eq, Int.cast_zero]

theorem XXC_trace : XXC.trace = 0 := by
  rw [XXC, liftC_trace, XX_trace_eq, Int.cast_zero]

theorem uuC_mul_XXC_trace : (uuC * XXC).trace = 0 := by
  rw [uuC, XXC, ← map_mul, liftC_trace, uu_mul_XX_trace_eq, Int.cast_zero]

theorem liftC_isHermitian_of_symm {m : CollarM} (h : ∀ i j, m i j = m j i) :
    (liftC m).IsHermitian := by
  ext i j
  simp only [Matrix.conjTranspose_apply, liftC_apply]
  rw [h j i]
  exact star_intCast _

theorem uuC_isHermitian : uuC.IsHermitian := liftC_isHermitian_of_symm uu_symm

theorem XXC_isHermitian : XXC.IsHermitian := liftC_isHermitian_of_symm XX_symm

/-- The sector projector is idempotent over ℂ — the direct witness that
    the ℤ-integrality obstruction was a feature of the ring of scalars,
    not of the operator content. -/
theorem pPlusC_idem : pPlusC * pPlusC = pPlusC := by
  rw [pPlusC, Matrix.smul_mul, Matrix.mul_smul, smul_smul]
  rw [add_mul, one_mul, mul_add, mul_one, uuC_sq]
  rw [show (1 : CollarC) + uuC + (uuC + 1) = (2 : ℂ) • (1 + uuC) by
    rw [two_smul]
    abel]
  rw [smul_smul]
  norm_num

/-! ### The lifted collar layer -/

/-- Left half-collar embedding over ℂ. -/
noncomputable def kronLeftC : Matrix (Fin 2) (Fin 2) ℂ →+* CollarC where
  toFun m := m ⊗ₖ (1 : Matrix (Fin 2) (Fin 2) ℂ)
  map_one' := by rw [Matrix.one_kronecker_one]
  map_mul' m n := by rw [← Matrix.mul_kronecker_mul, one_mul]
  map_zero' := by rw [Matrix.zero_kronecker]
  map_add' m n := by rw [Matrix.add_kronecker]

/-- Right half-collar embedding over ℂ. -/
noncomputable def kronRightC : Matrix (Fin 2) (Fin 2) ℂ →+* CollarC where
  toFun n := (1 : Matrix (Fin 2) (Fin 2) ℂ) ⊗ₖ n
  map_one' := by rw [Matrix.one_kronecker_one]
  map_mul' m n := by rw [← Matrix.mul_kronecker_mul, one_mul]
  map_zero' := by rw [Matrix.kronecker_zero]
  map_add' m n := by rw [Matrix.kronecker_add]

/-- Entrywise lift commutes with the Kronecker product. -/
theorem liftC_kronecker (a b : Matrix (Fin 2) (Fin 2) ℤ) :
    liftC (a ⊗ₖ b) = (a.map (Int.cast : ℤ → ℂ)) ⊗ₖ (b.map (Int.cast : ℤ → ℂ)) := by
  ext ⟨i, i'⟩ ⟨j, j'⟩
  simp [Matrix.kroneckerMap_apply, Matrix.map_apply]

theorem uuC_eq_kron :
    uuC = (uMat.map (Int.cast : ℤ → ℂ)) ⊗ₖ (uMat.map (Int.cast : ℤ → ℂ)) := by
  rw [uuC, uu, liftC_kronecker]

theorem XXC_eq_kron :
    XXC = (xMat.map (Int.cast : ℤ → ℂ)) ⊗ₖ (xMat.map (Int.cast : ℤ → ℂ)) := by
  rw [XXC, XX, liftC_kronecker]

/-- The model collar layer over ℂ: same interface data as `modelLayer`,
    lifted scalars. -/
noncomputable def modelLayerC : CollarLayer where
  A := CollarC
  K := Subring.closure {uuC}
  ML := kronLeftC.range
  MR := kronRightC.range
  sides_commute := by
    rintro l ⟨m, rfl⟩ r ⟨n, rfl⟩
    show (m ⊗ₖ 1) * ((1 : Matrix (Fin 2) (Fin 2) ℂ) ⊗ₖ n)
      = ((1 : Matrix (Fin 2) (Fin 2) ℂ) ⊗ₖ n) * (m ⊗ₖ 1)
    rw [← Matrix.mul_kronecker_mul, ← Matrix.mul_kronecker_mul,
      mul_one, one_mul, one_mul, mul_one]
  K_le := by
    intro a ha
    refine Subring.closure_le.mpr ?_ ha
    intro g hg
    rw [Set.mem_singleton_iff] at hg
    subst hg
    have huu : uuC = kronLeftC (uMat.map (Int.cast : ℤ → ℂ))
        * kronRightC (uMat.map (Int.cast : ℤ → ℂ)) := by
      show uuC = (uMat.map (Int.cast : ℤ → ℂ) ⊗ₖ 1)
        * ((1 : Matrix (Fin 2) (Fin 2) ℂ) ⊗ₖ uMat.map (Int.cast : ℤ → ℂ))
      rw [← Matrix.mul_kronecker_mul, mul_one, one_mul, uuC_eq_kron]
    rw [huu]
    exact mul_mem
      (Subring.subset_closure (Or.inl ⟨_, rfl⟩))
      (Subring.subset_closure (Or.inr ⟨_, rfl⟩))

/-- Gauge invariance over ℂ (`K̂_Σ`-invariance on the state-side layer). -/
noncomputable abbrev GaugeInvariantC : CollarC → Prop := modelLayerC.Invariant

/-- Cross-cut over ℂ. -/
noncomputable abbrev CrossCutC : CollarC → Prop := modelLayerC.CrossCut

/-- The flux sector over ℂ. -/
noncomputable abbrev FluxC : Set CollarC := modelLayerC.Flux

/-- Anything commuting with the generator `uuC` is invariant (mirror of
    `invariant_of_comm_uu`; the proof is scalar-independent). -/
theorem invariant_of_comm_uuC {a : CollarC} (h : uuC * a = a * uuC) :
    GaugeInvariantC a := by
  intro k hk
  have hle : Subring.closure {uuC} ≤ Subring.centralizer {a} := by
    rw [Subring.closure_le]
    intro g hg
    rw [Set.mem_singleton_iff] at hg
    subst hg
    show uuC ∈ Subring.centralizer {a}
    rw [Subring.mem_centralizer_iff]
    intro m hm
    rw [Set.mem_singleton_iff] at hm
    subst hm
    exact h.symm
  have hk' := hle hk
  rw [Subring.mem_centralizer_iff] at hk'
  exact (hk' a rfl).symm

theorem uuC_invariant : GaugeInvariantC uuC := invariant_of_comm_uuC rfl

theorem XXC_invariant : GaugeInvariantC XXC :=
  invariant_of_comm_uuC uuC_comm_XXC

/-! ### Cross-cut and (non-)centrality over ℂ (mirrors of the ℤ proofs,
same entry choices; the closing numeric contradictions move from `omega`
and `decide` to `norm_num` / `one_ne_zero`). -/

theorem uuC_notMem_MLC : uuC ∉ modelLayerC.ML := by
  rintro ⟨m, hm⟩
  have h1 : m 0 0 * (1 : Matrix (Fin 2) (Fin 2) ℂ) 0 0 = uuC (0, 0) (0, 0) :=
    congrFun (congrFun hm ((0 : Fin 2), (0 : Fin 2))) ((0 : Fin 2), (0 : Fin 2))
  have h2 : m 0 0 * (1 : Matrix (Fin 2) (Fin 2) ℂ) 1 1 = uuC (0, 1) (0, 1) :=
    congrFun (congrFun hm ((0 : Fin 2), (1 : Fin 2))) ((0 : Fin 2), (1 : Fin 2))
  have e1 : uuC (0, 0) (0, 0) = (1 : ℂ) := by
    have h : uu (0, 0) (0, 0) = 1 := by decide
    simp [uuC, h]
  have e2 : uuC (0, 1) (0, 1) = (-1 : ℂ) := by
    have h : uu (0, 1) (0, 1) = -1 := by decide
    simp [uuC, h]
  rw [e1, Matrix.one_apply_eq, mul_one] at h1
  rw [e2, Matrix.one_apply_eq, mul_one] at h2
  rw [h1] at h2
  norm_num at h2

theorem uuC_notMem_MRC : uuC ∉ modelLayerC.MR := by
  rintro ⟨n, hn⟩
  have h1 : (1 : Matrix (Fin 2) (Fin 2) ℂ) 0 0 * n 0 0 = uuC (0, 0) (0, 0) :=
    congrFun (congrFun hn ((0 : Fin 2), (0 : Fin 2))) ((0 : Fin 2), (0 : Fin 2))
  have h2 : (1 : Matrix (Fin 2) (Fin 2) ℂ) 1 1 * n 0 0 = uuC (1, 0) (1, 0) :=
    congrFun (congrFun hn ((1 : Fin 2), (0 : Fin 2))) ((1 : Fin 2), (0 : Fin 2))
  have e1 : uuC (0, 0) (0, 0) = (1 : ℂ) := by
    have h : uu (0, 0) (0, 0) = 1 := by decide
    simp [uuC, h]
  have e2 : uuC (1, 0) (1, 0) = (-1 : ℂ) := by
    have h : uu (1, 0) (1, 0) = -1 := by decide
    simp [uuC, h]
  rw [e1, Matrix.one_apply_eq, one_mul] at h1
  rw [e2, Matrix.one_apply_eq, one_mul] at h2
  rw [h1] at h2
  norm_num at h2

theorem XXC_notMem_MLC : XXC ∉ modelLayerC.ML := by
  rintro ⟨m, hm⟩
  have h1 : m 0 1 * (1 : Matrix (Fin 2) (Fin 2) ℂ) 1 0 = XXC (0, 1) (1, 0) :=
    congrFun (congrFun hm ((0 : Fin 2), (1 : Fin 2))) ((1 : Fin 2), (0 : Fin 2))
  have e1 : XXC (0, 1) (1, 0) = (1 : ℂ) := by
    have h : XX (0, 1) (1, 0) = 1 := by decide
    simp [XXC, h]
  have e0 : (1 : Matrix (Fin 2) (Fin 2) ℂ) 1 0 = 0 :=
    Matrix.one_apply_ne (by decide)
  rw [e1, e0, mul_zero] at h1
  exact one_ne_zero h1.symm

theorem XXC_notMem_MRC : XXC ∉ modelLayerC.MR := by
  rintro ⟨n, hn⟩
  have h1 : (1 : Matrix (Fin 2) (Fin 2) ℂ) 0 1 * n 1 0 = XXC (0, 1) (1, 0) :=
    congrFun (congrFun hn ((0 : Fin 2), (1 : Fin 2))) ((1 : Fin 2), (0 : Fin 2))
  have e1 : XXC (0, 1) (1, 0) = (1 : ℂ) := by
    have h : XX (0, 1) (1, 0) = 1 := by decide
    simp [XXC, h]
  have e0 : (1 : Matrix (Fin 2) (Fin 2) ℂ) 0 1 = 0 :=
    Matrix.one_apply_ne (by decide)
  rw [e1, e0, zero_mul] at h1
  exact one_ne_zero h1.symm

/-- The boundary charge is cross-cut over ℂ. -/
theorem uuC_crossCut : CrossCutC uuC := by
  rintro (h | h)
  · exact uuC_notMem_MLC h
  · exact uuC_notMem_MRC h

/-- The coupling is cross-cut over ℂ. -/
theorem XXC_crossCut : CrossCutC XXC := by
  rintro (h | h)
  · exact XXC_notMem_MLC h
  · exact XXC_notMem_MRC h

/-- The boundary charge is a flux term over ℂ. -/
theorem uuC_mem_fluxC : uuC ∈ FluxC :=
  ⟨Subring.subset_closure rfl, uuC_invariant⟩

/-- Diagonal matrices form a subring of the ℂ collar ring. -/
def diagonalSubringC : Subring CollarC where
  carrier := {m | ∀ i j, i ≠ j → m i j = 0}
  zero_mem' := fun _ _ _ => Matrix.zero_apply _ _
  one_mem' := fun _ _ hij => Matrix.one_apply_ne hij
  add_mem' := fun ha hb i j hij => by
    rw [Matrix.add_apply, ha i j hij, hb i j hij, add_zero]
  neg_mem' := fun ha i j hij => by
    rw [Matrix.neg_apply, ha i j hij, neg_zero]
  mul_mem' := fun {a b} ha hb i j hij => by
    rw [Matrix.mul_apply]
    apply Finset.sum_eq_zero
    intro k _
    rcases eq_or_ne k i with hk | hk
    · rw [hk, hb i j hij, mul_zero]
    · rw [ha i k hk.symm, zero_mul]

theorem uuC_diagonal : ∀ i j : Fin 2 × Fin 2, i ≠ j → uuC i j = 0 := by
  intro i j hij
  show ((uu i j : ℤ) : ℂ) = 0
  rw [uu_diagonal i j hij, Int.cast_zero]

/-- The coupling is NOT a flux term over ℂ: `K = ⟨uuC⟩` is diagonal and
    `XXC` is not (mirror of `XX_notMem_flux`). -/
theorem XXC_notMem_fluxC : XXC ∉ FluxC := by
  rintro ⟨hK, -⟩
  have hle : Subring.closure {uuC} ≤ diagonalSubringC := by
    rw [Subring.closure_le]
    intro g hg
    rw [Set.mem_singleton_iff] at hg
    subst hg
    exact uuC_diagonal
  have hdiag := hle hK
  have h0 := hdiag ((0 : Fin 2), (1 : Fin 2)) ((1 : Fin 2), (0 : Fin 2)) (by decide)
  have h1 : XXC (0, 1) (1, 0) = (1 : ℂ) := by
    have h : XX (0, 1) (1, 0) = 1 := by decide
    simp [XXC, h]
  rw [h1] at h0
  exact one_ne_zero h0

end OPH
