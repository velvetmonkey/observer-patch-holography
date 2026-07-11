import Mathlib
import ObserverPatchHolography.CollarClause

/-!
# Issue #544, operator layer: the collar clause made expressible — and proved
# independent of the algebraic core of the stated laws

The previous module (`CollarClause.lean`) proved the central-interface collar
clause is invisible to the overlap-consistency layer: repair factors through
the constraint family, which cannot express centrality. This module supplies
the **minimal abstract algebraic interface** on which the clause *is*
expressible, states it, and settles force-or-independence at that level.

## The interface (what the clause quantifies over — nothing else)

The clause (compact paper, `par:cicclause`, stated with Axiom 3
`ax:maxent`): *for every collar cut `Σ`, every retained density whose
support meets both half-collars acts through the boundary-charge (flux)
functions in `π_L(Z(C*(K̂_Σ)))`, while all remaining terms are one-sided
`K̂_Σ`-invariant operators.* Its ingredients, abstracted to pure ring
algebra (HARD RAIL: no C*-analysis, no GNS/spectra/Hilbert spaces):

* `A` — the pre-quotient collar operators, an abstract (noncommutative)
  ring;
* `K : Subring A` — the realized image of the boundary-symmetry algebra
  `C*(K̂_Σ)` (`prop:regulatedrealization`);
* `ML, MR : Subring A` — the one-sided algebras of `thm:msaderivation`'s
  interface normal form (`A ∪ B_L` side, `B_R ∪ D` side), commuting
  elementwise (screen-net locality, `ax:screen`), with `K` inside the
  collar algebra they generate;
* `Invariant a` — `K̂_Σ`-invariance, i.e. membership in the commutant of
  `K`; `Flux` — the center `Z(K) = K ∩ K′`; `CrossCut a` — support meets
  both half-collars, i.e. `a ∉ ML ∪ MR`.

A `RetainedFamily` packages exactly the algebraic stipulations Axiom 3
places on the retained constraint list (`ax:maxent`): a **finite** list of
**gauge-invariant** (= `K̂`-invariant) **collar-supported** densities,
together with a family of admissible refinement channels (additive maps —
CP coarse-graining maps are *not* multiplicative, so `RingHom` would be
unfaithful strength) under which the list is **refinement-closed** (the
operator-level shadow of the refinement-closure clause: coarse-graining
generates nothing outside the retained span).

## Faithfulness notes (scope, stated up front)

1. `Flux = Z(K)` is in general a *superset* of the paper's
   `π_L(Z(C*(K̂_Σ)))` (image-of-center ⊆ center-of-image). Refuting
   membership in the superset therefore refutes the paper's form, and the
   positive witness below lands in the smaller set too (its `K` is
   commutative, so the two coincide). No overclaim in either direction.
2. Only the **algebraic core** of Axiom 3 is shadowed. The state-side /
   analytic content (MaxEnt selection, closure-defect trace norms,
   realized-branch persistence) is *not* formalised here, and every claim
   below is scoped accordingly.
3. The representation-theoretic descent of `lem:onesideddescent` (Schur)
   and the MSA derivation of `thm:msaderivation` are **not** re-derived —
   that is #543, already done, and out of bounds for #544.

## The verdict: INDEPENDENCE (machine-checked two-model exhibit)

Two retained families over **one** collar layer `modelLayer` — the
algebraic double of the pinned failure mode in
`code/collar_alignment/test_msa_characterizations.py`
(`test_descent_invariant_but_noncentral_interface_breaks_alignment`:
"invariance alone is not the clause; centrality is"), over integer
matrices `M₂(ℤ) ⊗ M₂(ℤ)`:

* `posFamily` (= the paper's *lattice-gauge-type regulator*, which
  "satisfies the clause manifestly"): its single cross-cut density is the
  boundary charge `uu = u ⊗ₖ u ∈ Z(K)` — a genuine cross-cut **flux**
  term, so `CollarClause` holds non-degenerately
  (`collarClause_posFamily`).
* `negFamily` (= the paper's failure boundary, the Bell-pair-type
  coupling): adds `XX = X ⊗ₖ X`, which **satisfies every stated law** —
  it is `K̂`-invariant (`uu * XX = XX * uu`: the coupling respects the
  boundary symmetry, exactly the pinned test's group-averaged cross term)
  and collar-supported — yet is cross-cut and **not** in `Z(K)`; so
  `CollarClause` fails (`not_collarClause_negFamily`).

Hence (`collarClause_independent_of_axiom3_core`): the stated algebraic
laws admit both a central-interface and a non-central-interface retained
family — the collar clause is **not a consequence of the algebraic core of
the stated laws** and stays exactly what the paper declares it to be: a
named axiom-level input of the declared branch. Sharper
(`collarClause_not_layer_determined`): the two families share one layer,
so *no predicate of the layer data whatsoever* — in particular nothing
derivable from overlap-consistent repair, which by `CollarClause.lean`
reads only constraint data — can express the clause.

## Refinement-closure scoping (required honesty)

Axiom 3 calls the closure clause "a *substantive* renormalization
condition on the realized branch" and simultaneously stipulates "choose
**any** family of refinement channels compatible with the axiom"
(`ax:maxent`, and the channel choice in the refinement lemma). Both
witnesses below discharge closure with the identity channel, which the
"choose any channels" clause admits — a *legal* choice, so the
independence is valid. But this must not be read as "closure is
toothless": the correct reading is that **the collar clause is not forced
by the stated laws when the channel family is a free choice**. Forcing it
would require additional content the algebraic core lacks — either fixed
nontrivial coarse-graining channels under which closure bites, or
state-side/analytic content. That localisation of the missing force is the
result; the paper's open derivation target (`rem:msascope`) is thereby
narrowed, not closed. Issue #544 is NOT closed by this module.

No `sorry`, no `native_decide`, no new axiom.
-/

namespace OPH

/-! ## The collar layer interface -/

/-- The minimal algebraic layer the central-interface collar clause
    quantifies over: the pre-quotient collar ring, the realized
    boundary-symmetry subring `K` (shadow of `C*(K̂_Σ)`), and the two
    one-sided subrings of the interface normal form, commuting elementwise
    (screen-net locality) with `K` inside the collar algebra they
    generate. -/
structure CollarLayer where
  /-- Pre-quotient collar operators (abstract ring; no analytic structure). -/
  A : Type
  [ringA : Ring A]
  /-- Realized image of the boundary-symmetry algebra `C*(K̂_Σ)`. -/
  K : Subring A
  /-- One-sided algebra of the `A ∪ B_L` half-collar. -/
  ML : Subring A
  /-- One-sided algebra of the `B_R ∪ D` half-collar. -/
  MR : Subring A
  /-- Screen-net locality shadow: the half-collars commute elementwise. -/
  sides_commute : ∀ l ∈ ML, ∀ r ∈ MR, Commute l r
  /-- The boundary algebra lives in the collar algebra. -/
  K_le : (K : Set A) ⊆ Subring.closure ((ML : Set A) ∪ (MR : Set A))

attribute [instance] CollarLayer.ringA

namespace CollarLayer

variable (Λ : CollarLayer)

/-- `K̂_Σ`-invariance, abstracted: membership in the commutant of the
    realized boundary algebra. -/
def Invariant (a : Λ.A) : Prop := ∀ k ∈ Λ.K, Commute k a

/-- The flux sector: the center `Z(K)` of the boundary algebra inside the
    collar ring — the abstract shadow of the boundary-charge functions
    `π_L(Z(C*(K̂_Σ)))` (a superset thereof in general; see module
    header). -/
def Flux : Set Λ.A := {z | z ∈ Λ.K ∧ Λ.Invariant z}

/-- One-sided: supported on a single half-collar. -/
def OneSided (a : Λ.A) : Prop := a ∈ Λ.ML ∨ a ∈ Λ.MR

/-- Cross-cut: the support meets both half-collars. -/
def CrossCut (a : Λ.A) : Prop := ¬ Λ.OneSided a

end CollarLayer

/-- The algebraic stipulations Axiom 3 (`ax:maxent`) places on the retained
    constraint family — exactly these, no more: a finite list of
    gauge-invariant, collar-supported densities, refinement-closed under an
    admissible family of (additive) coarse-graining channels. -/
structure RetainedFamily (Λ : CollarLayer) where
  /-- The retained densities `O_a` ("a finite list"). -/
  densities : Finset Λ.A
  /-- "Gauge-invariant local densities": each retained density respects the
      boundary symmetry. This is the law that makes the
      invariant-but-non-central coupling *admissible*. -/
  gauge_invariant : ∀ d ∈ densities, Λ.Invariant d
  /-- Locality: each density is supported in the collar net. -/
  local_support : ∀ d ∈ densities,
    d ∈ Subring.closure ((Λ.ML : Set Λ.A) ∪ (Λ.MR : Set Λ.A))
  /-- The admissible refinement channels. Additive maps only: CP
      coarse-graining maps are not multiplicative, so demanding `RingHom`
      would smuggle unstated strength. -/
  refineChannels : Set (Λ.A →+ Λ.A)
  /-- The refinement-closure clause, operator-level shadow: coarse-graining
      generates nothing outside the retained span. -/
  refinement_closure : ∀ Φ ∈ refineChannels, ∀ d ∈ densities,
    Φ d ∈ AddSubgroup.closure (densities : Set Λ.A)

/-- **The central-interface collar clause** (`par:cicclause`), expressed
    over the layer: every retained cross-cut density acts through the flux
    sector, and every remaining density is a one-sided invariant. -/
def CollarClause (Λ : CollarLayer) (F : RetainedFamily Λ) : Prop :=
  ∀ d ∈ F.densities,
    (Λ.CrossCut d → d ∈ Λ.Flux) ∧
    (¬ Λ.CrossCut d → Λ.Invariant d ∧ Λ.OneSided d)

/-- Under the family laws the clause reduces to its cross-cut half — the
    formal counterpart of `cor:msareduction`'s "deriving MSA is equivalent
    to proving that all cross-cut terms are central". -/
theorem collarClause_iff (Λ : CollarLayer) (F : RetainedFamily Λ) :
    CollarClause Λ F ↔ ∀ d ∈ F.densities, Λ.CrossCut d → d ∈ Λ.Flux := by
  constructor
  · intro h d hd hc
    exact (h d hd).1 hc
  · intro h d hd
    exact ⟨h d hd, fun hnc => ⟨F.gauge_invariant d hd, not_not.mp hnc⟩⟩

/-! ## The model layer: the pinned failure mode, algebraically

Integer-matrix double of the python test: `u = diag(1,-1)` is the
boundary-charge generator, `uu = u ⊗ₖ u` generates the boundary algebra
`K`, and `XX = X ⊗ₖ X` is the `K`-invariant, non-central cross-cut
coupling (the group-averaged cross term of the test). Pure algebra over
`ℤ`; `decide` is kernel `decide`, never `native_decide`. -/

open Kronecker

/-- 2×2 building blocks. -/
def uMat : Matrix (Fin 2) (Fin 2) ℤ := !![1, 0; 0, -1]

def xMat : Matrix (Fin 2) (Fin 2) ℤ := !![0, 1; 1, 0]

/-- The ambient collar ring of the model: `M₂(ℤ) ⊗ M₂(ℤ)`. -/
abbrev CollarM : Type := Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℤ

/-- The boundary charge `u ⊗ u` (diagonal, cross-cut, central in `K`). -/
def uu : CollarM := uMat ⊗ₖ uMat

/-- The invariant-but-non-central cross coupling `X ⊗ X`. -/
def XX : CollarM := xMat ⊗ₖ xMat

/-- Left half-collar embedding `m ↦ m ⊗ₖ 1`, as a ring hom. -/
def kronLeft : Matrix (Fin 2) (Fin 2) ℤ →+* CollarM where
  toFun m := m ⊗ₖ (1 : Matrix (Fin 2) (Fin 2) ℤ)
  map_one' := by rw [Matrix.one_kronecker_one]
  map_mul' m n := by rw [← Matrix.mul_kronecker_mul, one_mul]
  map_zero' := by rw [Matrix.zero_kronecker]
  map_add' m n := by rw [Matrix.add_kronecker]

/-- Right half-collar embedding `n ↦ 1 ⊗ₖ n`, as a ring hom. -/
def kronRight : Matrix (Fin 2) (Fin 2) ℤ →+* CollarM where
  toFun n := (1 : Matrix (Fin 2) (Fin 2) ℤ) ⊗ₖ n
  map_one' := by rw [Matrix.one_kronecker_one]
  map_mul' m n := by rw [← Matrix.mul_kronecker_mul, one_mul]
  map_zero' := by rw [Matrix.kronecker_zero]
  map_add' m n := by rw [Matrix.kronecker_add]

/-- Diagonal matrices form a subring of the model collar ring. Used to
    bound `K = ⟨uu⟩` from above and exclude `XX` from it. -/
def diagonalSubring : Subring CollarM where
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

theorem uu_diagonal : ∀ i j : Fin 2 × Fin 2, i ≠ j → uu i j = 0 := by decide

theorem uu_comm_XX : uu * XX = XX * uu := by decide

/-- The model collar layer `Λ★`: both witnesses live over this ONE layer. -/
@[reducible] def modelLayer : CollarLayer where
  A := CollarM
  K := Subring.closure {uu}
  ML := kronLeft.range
  MR := kronRight.range
  sides_commute := by
    rintro l ⟨m, rfl⟩ r ⟨n, rfl⟩
    show (m ⊗ₖ 1) * ((1 : Matrix (Fin 2) (Fin 2) ℤ) ⊗ₖ n)
      = ((1 : Matrix (Fin 2) (Fin 2) ℤ) ⊗ₖ n) * (m ⊗ₖ 1)
    rw [← Matrix.mul_kronecker_mul, ← Matrix.mul_kronecker_mul,
      mul_one, one_mul, one_mul, mul_one]
  K_le := by
    intro a ha
    refine Subring.closure_le.mpr ?_ ha
    intro g hg
    rw [Set.mem_singleton_iff] at hg
    subst hg
    have huu : uu = kronLeft uMat * kronRight uMat := by
      show uu = (uMat ⊗ₖ 1) * ((1 : Matrix (Fin 2) (Fin 2) ℤ) ⊗ₖ uMat)
      rw [← Matrix.mul_kronecker_mul, mul_one, one_mul]
      rfl
    rw [huu]
    exact mul_mem
      (Subring.subset_closure (Or.inl ⟨uMat, rfl⟩))
      (Subring.subset_closure (Or.inr ⟨uMat, rfl⟩))

/-- Anything commuting with the generator `uu` is `K̂`-invariant. -/
theorem invariant_of_comm_uu {a : CollarM} (h : uu * a = a * uu) :
    modelLayer.Invariant a := by
  intro k hk
  have hle : Subring.closure {uu} ≤ Subring.centralizer {a} := by
    rw [Subring.closure_le]
    intro g hg
    rw [Set.mem_singleton_iff] at hg
    subst hg
    show uu ∈ Subring.centralizer {a}
    rw [Subring.mem_centralizer_iff]
    intro m hm
    rw [Set.mem_singleton_iff] at hm
    subst hm
    exact h.symm
  have hk' := hle hk
  rw [Subring.mem_centralizer_iff] at hk'
  exact (hk' a rfl).symm

/-! ### Cross-cut and (non-)centrality facts for the two densities -/

theorem uu_notMem_ML : uu ∉ modelLayer.ML := by
  rintro ⟨m, hm⟩
  have h1 : m 0 0 * 1 = 1 :=
    congrFun (congrFun hm ((0 : Fin 2), (0 : Fin 2))) ((0 : Fin 2), (0 : Fin 2))
  have h2 : m 0 0 * 1 = -1 :=
    congrFun (congrFun hm ((0 : Fin 2), (1 : Fin 2))) ((0 : Fin 2), (1 : Fin 2))
  rw [mul_one] at h1 h2
  omega

theorem uu_notMem_MR : uu ∉ modelLayer.MR := by
  rintro ⟨n, hn⟩
  have h1 : 1 * n 0 0 = 1 :=
    congrFun (congrFun hn ((0 : Fin 2), (0 : Fin 2))) ((0 : Fin 2), (0 : Fin 2))
  have h2 : 1 * n 0 0 = -1 :=
    congrFun (congrFun hn ((1 : Fin 2), (0 : Fin 2))) ((1 : Fin 2), (0 : Fin 2))
  rw [one_mul] at h1 h2
  omega

theorem XX_notMem_ML : XX ∉ modelLayer.ML := by
  rintro ⟨m, hm⟩
  have h1 : m 0 1 * 0 = 1 :=
    congrFun (congrFun hm ((0 : Fin 2), (1 : Fin 2))) ((1 : Fin 2), (0 : Fin 2))
  rw [mul_zero] at h1
  exact absurd h1 (by decide)

theorem XX_notMem_MR : XX ∉ modelLayer.MR := by
  rintro ⟨n, hn⟩
  have h1 : 0 * n 1 0 = 1 :=
    congrFun (congrFun hn ((0 : Fin 2), (1 : Fin 2))) ((1 : Fin 2), (0 : Fin 2))
  rw [zero_mul] at h1
  exact absurd h1 (by decide)

/-- The boundary charge is genuinely cross-cut. -/
theorem uu_crossCut : modelLayer.CrossCut uu := by
  rintro (h | h)
  · exact uu_notMem_ML h
  · exact uu_notMem_MR h

/-- The coupling is genuinely cross-cut. -/
theorem XX_crossCut : modelLayer.CrossCut XX := by
  rintro (h | h)
  · exact XX_notMem_ML h
  · exact XX_notMem_MR h

/-- The boundary charge is a flux term: it lies in `Z(K)`. -/
theorem uu_mem_flux : uu ∈ modelLayer.Flux :=
  ⟨Subring.subset_closure rfl, invariant_of_comm_uu rfl⟩

/-- The coupling is NOT a flux term: `K = ⟨uu⟩` consists of diagonal
    matrices, and `XX` is not diagonal. -/
theorem XX_notMem_flux : XX ∉ modelLayer.Flux := by
  rintro ⟨hK, -⟩
  have hle : Subring.closure {uu} ≤ diagonalSubring := by
    rw [Subring.closure_le]
    intro g hg
    rw [Set.mem_singleton_iff] at hg
    subst hg
    exact uu_diagonal
  have hdiag := hle hK
  have h0 := hdiag ((0 : Fin 2), (1 : Fin 2)) ((1 : Fin 2), (0 : Fin 2)) (by decide)
  exact absurd h0 (by decide)

/-! ### The two retained families over the one layer -/

/-- Collar support of the boundary charge. -/
theorem uu_local :
    uu ∈ Subring.closure ((modelLayer.ML : Set CollarM) ∪ (modelLayer.MR : Set CollarM)) := by
  have huu : uu = kronLeft uMat * kronRight uMat := by
    show uu = (uMat ⊗ₖ 1) * ((1 : Matrix (Fin 2) (Fin 2) ℤ) ⊗ₖ uMat)
    rw [← Matrix.mul_kronecker_mul, mul_one, one_mul]
    rfl
  rw [huu]
  exact mul_mem
    (Subring.subset_closure (Or.inl ⟨uMat, rfl⟩))
    (Subring.subset_closure (Or.inr ⟨uMat, rfl⟩))

/-- Collar support of the coupling. -/
theorem XX_local :
    XX ∈ Subring.closure ((modelLayer.ML : Set CollarM) ∪ (modelLayer.MR : Set CollarM)) := by
  have hXX : XX = kronLeft xMat * kronRight xMat := by
    show XX = (xMat ⊗ₖ 1) * ((1 : Matrix (Fin 2) (Fin 2) ℤ) ⊗ₖ xMat)
    rw [← Matrix.mul_kronecker_mul, mul_one, one_mul]
    rfl
  rw [hXX]
  exact mul_mem
    (Subring.subset_closure (Or.inl ⟨xMat, rfl⟩))
    (Subring.subset_closure (Or.inr ⟨xMat, rfl⟩))

/-- **The lattice-gauge-type witness** (`par:cicclause`: "lattice-gauge-type
    regulators satisfy the clause manifestly, their interface energy being a
    function of the conserved flux"): the single retained density is the
    boundary charge itself. Refinement closure is discharged by the identity
    channel — a legal choice under the "choose any channels" stipulation;
    see the module header for the required scoping of that fact. -/
def posFamily : RetainedFamily modelLayer where
  densities := {uu}
  gauge_invariant := by
    intro d hd
    rw [Finset.mem_singleton] at hd
    subst hd
    exact invariant_of_comm_uu rfl
  local_support := by
    intro d hd
    rw [Finset.mem_singleton] at hd
    subst hd
    exact uu_local
  refineChannels := {AddMonoidHom.id CollarM}
  refinement_closure := by
    intro Φ hΦ d hd
    rw [Set.mem_singleton_iff] at hΦ
    subst hΦ
    exact AddSubgroup.subset_closure hd

/-- **The failure-boundary witness**: adds the invariant-but-non-central
    cross coupling `XX` — the algebraic double of the pinned python test's
    group-averaged cross term. Every stated Axiom-3 law holds. -/
def negFamily : RetainedFamily modelLayer where
  densities := {uu, XX}
  gauge_invariant := by
    intro d hd
    rw [Finset.mem_insert, Finset.mem_singleton] at hd
    rcases hd with rfl | rfl
    · exact invariant_of_comm_uu rfl
    · exact invariant_of_comm_uu uu_comm_XX
  local_support := by
    intro d hd
    rw [Finset.mem_insert, Finset.mem_singleton] at hd
    rcases hd with rfl | rfl
    · exact uu_local
    · exact XX_local
  refineChannels := {AddMonoidHom.id CollarM}
  refinement_closure := by
    intro Φ hΦ d hd
    rw [Set.mem_singleton_iff] at hΦ
    subst hΦ
    exact AddSubgroup.subset_closure hd

/-- The clause HOLDS for the lattice-gauge-type witness — non-degenerately:
    its density is genuinely cross-cut and genuinely central. -/
theorem collarClause_posFamily : CollarClause modelLayer posFamily := by
  rw [collarClause_iff]
  intro d hd _
  have : d = uu := Finset.mem_singleton.mp hd
  subst this
  exact uu_mem_flux

/-- The clause FAILS for the failure-boundary witness: `XX` is a retained,
    admissible (invariant, collar-supported) cross-cut density outside the
    flux sector. -/
theorem not_collarClause_negFamily : ¬ CollarClause modelLayer negFamily := by
  intro h
  have hmem : XX ∈ negFamily.densities := by
    show XX ∈ ({uu, XX} : Finset CollarM)
    exact Finset.mem_insert.mpr (Or.inr (Finset.mem_singleton.mpr rfl))
  exact XX_notMem_flux ((h XX hmem).1 XX_crossCut)

/-! ## The verdict -/

/-- **INDEPENDENCE (issue #544, interface level).** The algebraic core of
    the stated laws — screen-net locality, gauge-invariance of the retained
    densities, finiteness, collar support, and the refinement-closure
    clause discharged by the identity channel that the "choose any
    channels" stipulation admits — is satisfied both by a retained family
    satisfying the collar clause and by one refuting it. The clause is
    therefore not a consequence of that algebraic core and remains exactly
    what the paper declares: a named axiom-level input of the declared
    branch. Any derivation must add content the core lacks — fixed
    nontrivial coarse-graining channels under which closure bites, or
    state-side/analytic content. -/
theorem collarClause_independent_of_axiom3_core :
    (∃ (Λ : CollarLayer) (F : RetainedFamily Λ), CollarClause Λ F) ∧
    (∃ (Λ : CollarLayer) (F : RetainedFamily Λ), ¬ CollarClause Λ F) :=
  ⟨⟨modelLayer, posFamily, collarClause_posFamily⟩,
    ⟨modelLayer, negFamily, not_collarClause_negFamily⟩⟩

/-- **The sharp force-refutation.** The two witnesses live over ONE layer,
    so no predicate of the layer data whatsoever can express the collar
    clause — in particular nothing derivable from overlap-consistent
    repair, which (by the layer-separation theorems of `CollarClause.lean`)
    reads only constraint data. This upgrades "repair does not select
    against non-central couplings" to "no property of the collar layer can
    even state the selection". -/
theorem collarClause_not_layer_determined :
    ∀ P : CollarLayer → Prop,
      ¬ (∀ (Λ : CollarLayer) (F : RetainedFamily Λ), CollarClause Λ F ↔ P Λ) := by
  intro P h
  exact not_collarClause_negFamily
    ((h modelLayer negFamily).mpr ((h modelLayer posFamily).mp collarClause_posFamily))

/-! ### Axiom audit — the operator-layer verdict is admission-free. -/
#print axioms CollarClause
#print axioms collarClause_iff
#print axioms uu_comm_XX
#print axioms uu_crossCut
#print axioms XX_crossCut
#print axioms uu_mem_flux
#print axioms XX_notMem_flux
#print axioms collarClause_posFamily
#print axioms not_collarClause_negFamily
#print axioms collarClause_independent_of_axiom3_core
#print axioms collarClause_not_layer_determined

end OPH
