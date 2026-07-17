# OPH #544 state-side meta-boundary — feasibility scoping report

**Date:** 2026-07-17
**Branch:** `feat/oph-544-state-side-scoping` @ parent `bfea4244` (equivariant-universal no-go tip), NOT pushed.
**Scope:** feasibility only. Zero `.lean` proof changes. One scratch import-frisk file (scratchpad, uncommitted) compiled clean against the pinned Mathlib.
**Provenance baseline:** repo `observer-patch-holography`, toolchain `leanprover/lean4:v4.29.1`, Mathlib pin `5e932f97dd25535344f80f9dd8da3aab83df0fe6` (2026-04-17), vendored at `Lean/.lake/packages/mathlib`. Algebraic chain on `fix/oph-544-equivariant-nogo`: `e3eabcf1` (layer separation) → `96fab664` (operator layer) → `a0eb0699` (no-go addendum) → `bfea4244` (equivariant-universal no-go). Council `440cbdca` verdict: NEEDS-STATE-SIDE-CONTENT.

---

## Executive verdict

**Split verdict, by target:**

| Target | Verdict |
|---|---|
| **T0** — state-side no-go under the paper's *current* admissible-channel axioms (identity-channel escape, now with real states and real relative entropy) | **Formalizable now.** ~4–6 working days incl. foundations. Genuinely new content over the algebraic chain; sharpens #544 but does not close it. |
| **T1** — state-side reversal exhibit: the flux conditional expectation *exists* over ℂ (the ℤ-obstruction does not extend) and *still* does not force the clause | **Formalizable now.** ~5–8 additional days. Kills the last "the algebraic obstruction will extend" hope honestly. |
| **T2** — forcing (or its refutation) over a *genuinely coarse-graining* channel class — the thing that would actually CLOSE #544 | **Blocked — but on physics/mathematics, not on Mathlib.** The channel class is not pinned in the paper; the mathematical truth of forcing over any candidate class is unknown. Needs a paper-level axiom decision (Ben) + a paper-level proof sketch before any Lean work is meaningful. |
| Operator-algebraic (type III / infinite-dim) formulation of any of the above | **Blocked on Mathlib foundations** (no trace-class, no operator-algebraic conditional expectation, no modular theory beyond a scaffold). Do not attempt. |

The load-bearing discovery: **the finite-dimensional state-side toolbox is buildable from current Mathlib** — density matrices, matrix log via CFC, Umegaki relative entropy, Gibbs families, I-projections all assemble from verified-present pieces, with ~4 foundational bricks to write (§4). Nothing in T0/T1 is blocked on Mathlib. What is *not* buildable today is the theorem that closes #544, because that theorem does not yet exist as mathematics: its quantifier domain (the admissible channel class) is a free parameter the paper has not fixed, and #544's answer provably depends on how it is fixed (§1.3, §3 trap iii).

---

## 0. Honesty flags (read first)

1. **The goal's target sentence is not in the paper.** The tasking quotes rem:msascope as claiming "non-central families admit no refinement-stable realized MaxEnt branch." That sentence appears nowhere in the paper (verified by grep on the branch). What `rem:msascope` (paper L2197–2199) actually leaves open is: *"whether overlap-consistent repair forces that clause, i.e. whether non-central cross-cut couplings are excluded rather than merely not selected"*, with the state-side meta-boundary named as *"the universal claim over all admissible coarse-graining channels (positivity, trace preservation, branch selection)"*. This report scopes against the actual remark text. Note the quoted sentence, taken literally, is **false under the paper's current axioms** — see T0 — which is itself a scoping result.
2. **The ℤ-integrality obstruction reverses over ℂ.** `no_integral_flux_retraction` (CollarLayer.lean:690) is explicitly labeled an "algebraic shadow of the division-by-dimension" (L541–543). Over ℂ, division by dimension exists: the trace-preserving conditional expectation onto the flux *-subalgebra span{1, u⊗u} is a genuine unital CP trace-preserving map that annihilates X⊗X. The state-side layer therefore does not *extend* the integrality obstruction — it dissolves it, and the honest question becomes whether the now-existing excluding map (or any admissible channel) *forces* anything. It does not (T1, and already `killing_XX_preserves_spanClosure` at the span level). Any report or paper text implying the ℤ obstruction has a state-side continuation would be a false receipt.
3. **No decidability escape hatch state-side.** The algebraic chain closed goals by `decide`/`omega` on integer matrix entries. State-side objects (exp, log, ε-infima) are transcendental; nothing is decidable, and `native_decide` stays banned. Every state-side lemma is real analysis. Effort estimates below price that in.

---

## 1. Honest theorem statements

### 1.0 Common formal setting (all candidates)

Finite-dimensional ℂ-lift of the existing model layer. The algebraic chain lives on `CollarM := Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℤ` (CollarLayer.lean:217); the state layer lifts scalars to ℂ:

```lean
abbrev CollarC := Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℂ   -- M₂(ℂ) ⊗ M₂(ℂ)

open scoped ComplexOrder   -- REQUIRED: Matrix.PosSemidef over ℂ needs the scoped order (frisk-verified)

structure DensityMatrix where
  ρ : CollarC
  posSemidef : ρ.PosSemidef
  trace_one : ρ.trace = 1

/-- Umegaki relative entropy, via Hermitian functional calculus.
    `Matrix.IsHermitian.cfc Real.log` is the matrix log (Mathlib has no `Matrix.log`). -/
noncomputable def relEntropy (ρ σ : DensityMatrix) : ℝ := ...
  -- (ρ.ρ * (hρ.cfc Real.log - hσ.cfc Real.log)).trace.re, guarded by faithfulness of σ

/-- Gibbs / exponential family over a retained constraint list. -/
noncomputable def gibbsState (S : Fin k → CollarC) (lam : Fin k → ℝ) : DensityMatrix := ...
  -- NormedSpace.exp ℂ (-(∑ a, lam a • S a)) normalized by its trace; no `Matrix.exp` def exists

/-- Admissible channel, paper's named requirements only (rem:msascope):
    positivity, trace preservation. CP is the optional strengthening
    (Mathlib carries `CompletelyPositiveMap` if wanted). Witness-free by
    construction — references no family, no K, no coupling (anti-smuggling, §3). -/
structure AdmissibleChannel where
  Φ : CollarC →ₗ[ℂ] CollarC
  pos : ∀ m : CollarC, m.PosSemidef → (Φ m).PosSemidef
  tracePreserving : ∀ m, (Φ m).trace = m.trace

/-- Closure defect of def:closure-defect (paper L1051–1057), same-scale form. -/
noncomputable def closureDefect (S : Fin k → CollarC) (C : AdmissibleChannel)
    (lam : Fin k → ℝ) : ℝ := ⨅ lam', relEntropy (C.apply (gibbsState S lam)) (gibbsState S lam')
```

The retained-family and clause vocabulary (`RetainedFamily`, `CollarClause`, `CrossCut`, `Flux`) lifts from `CollarLayer.lean` verbatim with ℤ → ℂ scalars; the witnesses `uu = u⊗u` and `XX = X⊗X` and the facts `uu_comm_XX`, `XX_notMem_flux`, `E0110_crossCut` all re-prove over ℂ by the same entry computations (`decide` becomes `norm_num`/`ext`-level work, still mechanical).

**Feasibility-critical structural fact:** in this model the natural non-central retained list {uu, XX} is *commuting* (`uu_comm_XX`, CollarLayer.lean:261). For commuting constraint families, strict convexity of `log Z` reduces to the classical (scalar, simultaneous-eigenbasis) argument and the Duhamel/Kubo–Mori Hessian machinery of the paper's `lem:closure-residual` proof is **not needed**. This is the single biggest effort reducer found in this scoping pass. The general noncommuting-family lemma is where the paper's proof (L1066–1073) invokes Kubo–Mori; Mathlib has nothing for that (§2), and T0/T1 do not need it.

### 1.1 T0 — the identity-channel no-go, now with real states (formalizable now)

**Statement (prose).** Under the paper's current admissible-channel requirements (positivity + trace preservation, with the "choose any family of refinement channels" free choice of ax:maxent's internal refinement notion, paper L1043–1049): there exists a legal retained family containing a non-central cross-cut density (the ℂ-lift of `negFamily`) whose realized MaxEnt branch is refinement-stable — closure defect identically zero — under an admissible channel family. Witness: the identity channel, which is positive and trace-preserving, hence admissible under the stated requirements.

**Candidate signature.**

```lean
theorem stateSide_currentAxioms_cannot_force :
    ∃ (S : Fin 2 → CollarC),                    -- the {uu, XX} retained list
      (∀ a, GaugeInvariant (S a)) ∧ (∃ a, CrossCutC (S a) ∧ S a ∉ FluxC) ∧
      ∃ C : AdmissibleChannel,                   -- := identity
        ∀ lam, closureDefect S C lam = 0 := ...
```

with the defect-zero step factored through the two genuinely new lemmas
`relEntropy_self (h : faithful ρ) : relEntropy ρ ρ = 0` and
`closureDefect_le_relEntropy_apply : closureDefect S C lam ≤ relEntropy (C.apply (gibbsState S lam)) (gibbsState S lam)`.

**What it does and does not do.** This is the state-side twin of the algebraic identity-channel discharge already conceded in par:cicclause ("with the refinement-closure clause discharged there by the identity channel that the 'choose any channels' stipulation admits"). New content over the algebra: the branch, the MaxEnt states, and ε are now the *real* objects of def:closure-defect (positivity, trace, log — no ℤ-ring shadow), so the discharge now happens at the layer the council demanded, and it proves the goal's quoted target sentence **false as stated**: non-central families *do* admit a refinement-stable realized MaxEnt branch under the current axioms. It does **not** close #544 — it sharpens it to: *forcing is impossible until the paper strengthens the admissible class to exclude the identity escape* (an axiom-level edit; Ben decision — §3 trap iii).

### 1.2 T1 — the reversal exhibit: the excluding map exists and still does not force (formalizable now)

**Statement (prose).** Over ℂ the obstruction of `no_integral_flux_retraction` reverses: the Hilbert–Schmidt-orthogonal conditional expectation `E_flux : m ↦ (tr m)/4 • 1 + (tr (uu·m))/4 • uu` onto the flux *-subalgebra span{1, uu} is unital, trace-preserving, positive (indeed CP, as a conditional expectation onto a *-subalgebra in finite dimension), fixes 1 and uu, maps `pPlus = (1+uu)/2` to itself, and annihilates XX. And *even so*, adding `E_flux` to the channel set does not force the clause: the non-central family remains refinement-closed (span-closure: `killing_XX_preserves_spanClosure` lifts verbatim), and its E_flux-coarse-grained realized state lands inside the *central* exponential subfamily with closure defect zero — i.e. coarse-graining by the genuine excluding map merely *deselects* the coupling on the coarse side; it does not *exclude* the non-central family as a branch. Exactly the force-vs-select gap rem:msascope names.

**Candidate signatures.**

```lean
noncomputable def Eflux : AdmissibleChannel := ...          -- explicit 2-term formula above

theorem Eflux_unital : Eflux.Φ 1 = 1 := ...
theorem Eflux_fixes_uu : Eflux.Φ uuC = uuC := ...
theorem Eflux_maps_pPlus : Eflux.Φ pPlusC = pPlusC := ...   -- the ℤ-impossible value, now legal
theorem Eflux_kills_XX : Eflux.Φ XXC = 0 := ...

theorem flux_expectation_exists_over_C :                    -- the reversal, stated as the ℂ-negation
    ∃ E : AdmissibleChannel, (∀ m ∈ FluxC, E.Φ m = m) ∧ E.Φ 1 = 1 ∧ E.Φ XXC = 0 := ...

theorem Eflux_does_not_force :
    ∀ lam, closureDefect ![uuC, XXC] Eflux lam = 0 := ...
```

The last theorem is the analytically hardest of the pair: it needs `E_flux (gibbsState ![uu,XX] lam) = gibbsState-central (some lam')` — tractable here because uu and XX commute, so `exp(-λ₁uu - λ₂XX)` diagonalizes in the common eigenbasis and both sides are explicit 4×4 diagonal-in-that-basis matrices; the I-projection infimum is then hit at an explicit λ' by moment matching in a 1-parameter commutative family. Concrete, closed-form, no Kubo–Mori.

**What it does.** Honestly terminates the "extend the algebraic obstruction" route (flag 2): proves on-machine that the obstruction was ℤ-artifact by design and that possession of the excluding map still does not force. Re-characterizes the boundary; does not close #544.

### 1.3 T2 — what would actually CLOSE #544, and why it cannot be stated yet

Closing #544 means resolving, over a *genuinely coarse-graining* admissible class 𝒞 (the class rem:msascope gestures at with "positivity, trace preservation, branch selection"), one of:

- **T2-FORCE:** every legal retained family containing a non-central cross-cut density has, for every realized branch point, some channel in 𝒞 with strictly positive closure defect — while some central family has defect zero throughout. (Non-central families are *excluded*, deriving the clause.)
- **T2-NOGO:** some legal non-central family has closure defect zero along a realized branch for *all* channels in 𝒞 simultaneously. (The clause is unforcable even state-side; the meta-boundary is a wall, and par:cicclause stays a permanent declared input.)

```lean
-- schematic only; 𝒞 is the unfixed parameter
theorem T2_force (𝒞 : Set AdmissibleChannel) (h𝒞 : GenuinelyCoarseGraining 𝒞) :
    ∀ S, LegalFamily S → (∃ a, CrossCutC (S a) ∧ S a ∉ FluxC) →
      ∀ lam, ∃ C ∈ 𝒞, 0 < closureDefect S C lam
```

**Why it is not stateable today.** `GenuinelyCoarseGraining` has no definition. The paper's free-choice clause admits the identity channel, and T0 shows that any 𝒞 containing it makes T2-FORCE false. So T2's truth value is a function of a definition that does not exist in the paper: candidate ingredients (strict scale decrease ℓ→L with dimension reduction, partial-trace-type structure, locality) each change the answer — e.g. under the two-site partial trace both uu = u⊗u *and* XX = X⊗X map to 0 (both factors traceless), so that channel is blind to the central/non-central distinction entirely and cannot force either way. Fixing 𝒞 is an axiom-level paper decision (Ben), and once fixed, T2 needs a *paper-level proof or refutation first* — this is open research mathematics, not a formalization backlog. Any Lean work "on T2" before that is scope theater.

**Closure criterion (for future adjudication):** a result closes #544 iff its channel quantifier is over a class (a) defined witness-free by properties stated before any family is mentioned, (b) proven nonempty with physically mandatory members, and (c) endorsed in the paper as *the* admissible class of ax:maxent. Anything quantifying over a hand-chosen channel set re-characterizes the boundary (as T0/T1 and the whole algebraic chain do — valuable, but not closure).

---

## 2. Mathlib support / gap map

All PRESENT claims verified twice: on-disk grep of `Lean/.lake/packages/mathlib` @ `5e932f97`, plus a scratch file (`StateSideFrisk.lean`, scratchpad, uncommitted) that imports every load-bearing module and `#check`s every load-bearing declaration — **compiled clean** via `lake env lean` against the project's cached oleans. Frisk commands in Appendix A.

### PRESENT (verified on disk + compiled)

| Need | Mathlib declaration | File (under `Mathlib/`) |
|---|---|---|
| Matrix trace | `Matrix.trace` | `LinearAlgebra/Matrix/Trace.lean` |
| PSD matrices | `Matrix.PosSemidef`, `Matrix.PosDef`, `Matrix.PosSemidef.trace_nonneg` | `LinearAlgebra/Matrix/PosDef.lean` |
| Matrix functional calculus | `Matrix.IsHermitian.cfc : (ℝ → ℝ) → Matrix n n 𝕜` | `Analysis/Matrix/HermitianFunctionalCalculus.lean:132` |
| Operator log | `CFC.log := cfc Real.log`, `CFC.log_exp`, `CFC.exp_log` | `Analysis/SpecialFunctions/ContinuousFunctionalCalculus/ExpLog/Basic.lean:121` |
| Operator monotone log | `CFC.log_monotoneOn`, `CFC.log_le_log` | `.../ExpLog/Order.lean` |
| Matrix/operator exp | `NormedSpace.exp` + `Matrix.exp_*` lemma suite (`exp_add_of_commute`, `exp_conjTranspose`, …) | `Analysis/Normed/Algebra/MatrixExponential.lean` |
| General CFC framework | `cfc`, `cfcₙ`, `cfcHom` | `Analysis/CStarAlgebra/ContinuousFunctionalCalculus/` (18 files) |
| Positive linear maps | `PositiveLinearMap` (`→ₚ`), `PositiveLinearMap.exists_norm_apply_le` | `Analysis/CStarAlgebra/PositiveLinearMap.lean`, `Algebra/Order/Module/PositiveLinearMap.lean` |
| Completely positive maps | `CompletelyPositiveMap` | `Analysis/CStarAlgebra/CompletelyPositiveMap.lean` |
| GNS | `PreGNS`, `GNS`, `gnsStarAlgHom` | `Analysis/CStarAlgebra/GelfandNaimarkSegal.lean` |
| von Neumann algebras | `WStarAlgebra`, `VonNeumannAlgebra`, `commutant`, `commutant_commutant` | `Analysis/VonNeumannAlgebra/Basic.lean` |
| Classical KL | `InformationTheory.klDiv`, Gibbs inequality + converse, `klDiv_eq_zero_iff`, chain rule `klDiv_compProd_eq_add`, `klFun`, `strictConvexOn_klFun` | `InformationTheory/KullbackLeibler/{Basic,ChainRule,KLFun}.lean` |
| x log x | `Real.negMulLog`; `binEntropy`, `qaryEntropy` | `Analysis/SpecialFunctions/Log/NegMulLog.lean:142`, `.../BinaryEntropy.lean` |
| Exponential tilting (classical exponential family) | `Measure.tilted` | `MeasureTheory/Measure/Tilted.lean` |
| Measure-theoretic cond. expectation | `MeasureTheory.condExp` (`μ[f|m]`) | `MeasureTheory/Function/ConditionalExpectation/` |
| Loewner order | `instLoewnerPartialOrder` | `Analysis/InnerProductSpace/Positive.lean` |
| Tomita scaffold only | `StandardSubspace`, `symplComp` (+ explicit TODO: "Define the Tomita conjugation, prove Tomita's theorem, prove the KMS condition") | `Analysis/InnerProductSpace/StandardSubspace.lean` |

**Frisk corrections to folklore** (both hit during compile, both would have been false receipts if cited untested):
- There is **no `Matrix.exp`** declaration; the matrix exponential is `NormedSpace.exp` at the matrix algebra, with lemmas in the `Matrix` namespace. Cite it that way.
- `Matrix.PosSemidef` over ℂ requires `open scoped ComplexOrder` (the `PartialOrder ℂ` instance is scoped); without it the density-matrix definition does not elaborate.

### ABSENT (verified by grep; would be OPH-built, not Mathlib-provided)

| Need | Status | T0/T1 impact |
|---|---|---|
| Density matrix / quantum state type | ABSENT (no `densityMatrix`, no quantum-info dir) | Build (small; frisk shows the definition elaborates from present pieces) |
| von Neumann entropy, Umegaki relative entropy | ABSENT (no `vonNeumannEntropy`, `quantumRelativeEntropy`; "quantum" hits are prose/citations only) | Build (core brick) |
| Klein inequality (D ≥ 0, = 0 iff equal) | ABSENT | Build — needed for T1's defect-zero characterization; hardest analysis brick |
| Quantum (or even classical) Pinsker | ABSENT (no `Pinsker` anywhere) | Skip — only needed for lem:closure-residual (ii), not for T0/T1 |
| Duhamel / Kubo–Mori covariance | ABSENT (no `Duhamel`, `Kubo`) | Skip for T0/T1 (commuting family); wall for general noncommuting lem:closure-residual (i) |
| I-projection / MaxEnt / Gibbs-state framework | ABSENT (`IProj`, `maxEnt`, Gibbs-as-object all absent; only the *name* "Gibbs' inequality" on `klDiv`) | Build (medium; finite-dim, strict convexity + compactness) |
| Shannon entropy of a finite distribution | ABSENT (only `binEntropy`/`qaryEntropy`) | Not needed |
| Operator-algebraic conditional expectation onto a subalgebra | ABSENT | Build explicitly for T1 (2-term formula; do NOT need the general theory) |
| Trace-class / Schatten / operator Hilbert–Schmidt | ABSENT (matrix Frobenius norm only) | Blocks infinite-dim only |
| Tomita conjugation / modular flow / KMS | ABSENT (TODO stub only) | Blocks type-III track only (§5) |
| Operator convexity/monotonicity framework, Golden–Thompson | ABSENT (isolated CFC lemmas only: `CFC.log_monotoneOn`, `CFC.monotone_rpow`) | Not needed for T0/T1 |
| f-divergences | ABSENT | Not needed |

**Load-bearing answer:** for the finite-dimensional T0/T1 program, Mathlib is *sufficient as a substrate* — every gap is a buildable OPH brick with no foundational hole underneath. For the operator-algebraic formulation, Mathlib is missing entire theories (trace-class, conditional expectations, modular theory); that formulation is blocked-on-foundations and out of scope.

---

## 3. Trap catalogue

The pure-algebra failure mode: smuggling the clause into a hand-picked projection Φ (a conditional expectation onto the center chosen because it annihilates XX), then reading its output as a derivation. State-side analogues, and the structural exclusions a sound build must carry:

| # | Trap | State-side form | Structural exclusion |
|---|---|---|---|
| i | **Smuggled projection** | Defining the admissible class *by extension* — 𝒞 := {E_flux}, or any class whose definition mentions K, uu, XX, or "central" — then announcing that closure under 𝒞 forces the clause. Same false receipt, new coat: the conclusion was typed into the quantifier domain. | Channel classes must be **witness-free**: defined only by properties (linearity, positivity, trace preservation, scale/locality structure) quantified *before* any family or generator is mentioned — the discipline `IsEquivariantChannel` (CollarLayer.lean:837) already follows ("references only `uu`; never the refuting coupling"). Lint: the class definition must not name `XX`, `FluxC`, or `CollarClause`. |
| ii | **Vacuous class** | Strengthening 𝒞 until it is empty (or until no channel connects the scales), making T2-FORCE vacuously true. The HTTP-proxy lesson: vacuous, not false. | Mandatory nonemptiness receipts: every class definition ships `∃ C ∈ 𝒞, …` witnesses, including physically mandatory members, before any force theorem quantifies over it. |
| iii | **Identity-channel escape** (the live one) | The paper's "choose any family of refinement channels" admits the identity; T0 shows any 𝒞 containing it cannot force. A build that silently *drops* identity from 𝒞 without an axiom-level paper edit has smuggled exclusion into the class the other way. | Forcing claims must cite the axiom text that excludes the escape. Until ax:maxent is strengthened (Ben decision), the only honest theorems are T0/T1-shaped. |
| iv | **ℤ-shadow relapse** | Re-proving the integrality obstruction where it is false: over ℂ the flux conditional expectation exists (T1), so any state-side claim that "no expectation onto flux exists, hence non-central families are excluded" is wrong in the premise; conversely, claiming the ℤ no-go "extends" to states is a false receipt. | T1 formalizes the reversal on-machine as a first-class theorem (`flux_expectation_exists_over_C`), so the repo itself certifies the obstruction's boundary. |
| v | **Branch presupposition** | Defining "realized branch" as *the central family's* branch (or building centrality into `LegalFamily`/the MaxEnt constraint set), then observing non-central couplings are absent from it. Circularity: selection presented as exclusion. | `LegalFamily` lifts exactly the four algebraic stipulations already in `RetainedFamily` (finite, gauge-invariant, collar-supported, refinement-closed) and nothing else; the branch is defined uniformly for every legal family via its own MaxEnt data. |
| vi | **Force/select conflation at ε = 0** | Showing a channel *maps* the non-central branch into the central family (defect zero, coupling "gone") and reading that as exclusion. T1's `Eflux_does_not_force` shows this is *selection* — the non-central family itself remains a legal, refinement-stable branch. Exclusion means: *no* defect-zero branch exists for the family (positive defect for all λ, all channels of 𝒞 — the T2-FORCE shape). | The defect predicate is always stated with its quantifier prefix explicit; no theorem named `…_forces_…` may have an ∃-channel or ∃-λ where T2-FORCE has ∀. |
| vii | **Fake-decidability receipts** | Porting the chain's `decide`-culture to transcendental objects: `#eval`-style numeric checks of ε, or `native_decide`, standing in for proofs. | Admission-free discipline unchanged: `#print axioms` blocks per section, `native_decide` banned, numeric sanity checks live in `code/maxent/` (Python — already exists, paper L1074) and are never cited as Lean receipts. |

---

## 4. Build plan + effort (T0 + T1; T2 explicitly not planned)

Brick sequence, each admission-free with `#print axioms` audit, new file `Lean/ObserverPatchHolography/Source/ObserverPatchHolography/CollarStates.lean` (imports CollarLayer; the HARD RAIL comment at CollarLayer.lean:21 stays true of *that* file — the rail moves, it is not breached: state content lives only in the new file):

| Brick | Content | Est. days | Risk |
|---|---|---|---|
| S1 | ℂ-lift of model layer: `CollarC`, `uuC/XXC/pPlusC`, re-prove `uu_comm_XX`, `XX_notMem_flux`, cross-cut/flux predicates over ℂ (entry-level `ext`/`norm_num` work) | 1 | low |
| S2 | `DensityMatrix` + API (faithful, PSD facts, `ComplexOrder` plumbing); `gibbsState` via `NormedSpace.exp`, positivity + trace-one (uses `Matrix.exp_*` suite; commuting case only) | 1.5 | low-med |
| S3 | Matrix log via `IsHermitian.cfc Real.log`; `relEntropy`; `relEntropy_self = 0`; **Klein inequality** (≥ 0, = 0 iff equal, faithful case; spectral two-basis argument on 4×4, may specialize to commuting pairs where it degenerates to classical Gibbs inequality — Mathlib's `klDiv` converse Gibbs is the model) | 2–3 | **highest** |
| S4 | `AdmissibleChannel`; identity instance; `closureDefect`; **T0 theorem** | 1 | low (given S3) |
| S5 | `Eflux` + five T1 lemmas incl. CP (Choi on 16×16 or direct 2-term positivity argument); `Eflux_does_not_force` via common-eigenbasis closed form + 1-parameter moment matching | 3–4 | med-high |
| S6 | Paper edit: rem:msascope one-sentence update citing the state-side exhibit; axiom audit blocks; report + memory | 0.5 | low |

**Total: ~9–11 working days** for T0+T1 (T0 alone: S1–S4 ≈ 5.5–6.5 days). **Riskiest step: S3 Klein inequality** — first genuinely analytic matrix-inequality proof in the repo, no Mathlib precedent to lean on; fallback if it stalls: state T0/T1 defect-zero results via an explicit-minimizer formulation (exhibit λ' with `relEntropy … = 0` by direct computation, using only `relEntropy_self`), deferring full Klein to a later brick and shaving ~2 days at the cost of a weaker `closureDefect_eq_zero_iff` API. Second risk: S5 CP-ness of `Eflux` — droppable without loss (positivity + trace preservation suffice for admissibility as the paper states it; CP becomes a bonus lemma).

**T2: no build plan on purpose.** Prerequisites in order: (1) Ben fixes the admissible class in ax:maxent (axiom edit — the identity-escape decision); (2) paper-level proof or refutation over that class; (3) only then Lean scoping. Premature Lean here is the scope-theater trap.

---

## 5. Tomita–Takesaki boundary (flag only, no scope creep)

**Not a dependency of T0/T1/T2 in finite dimension.** The branch-selection argument uses positivity, trace, log, exp, and convexity only. The modular flow of a faithful density matrix (σ_t(a) = ρ^{it} a ρ^{-it}) is expressible via the same CFC toolbox if ever wanted, but no candidate theorem in §1 mentions it.

**A dependency only for the type-III / infinite-dimensional formulation** — the paper's D4 chain (half-sided modular inclusions, Borchers–Wiesbrock, thm:bw) and the Mini-Universe sim's modular observer-time. There Mathlib has exactly one scaffold: `StandardSubspace` (`Analysis/InnerProductSpace/StandardSubspace.lean`) with its TODO explicitly listing Tomita conjugation, Tomita's theorem, and KMS as future work. That is a separate, large, upstream-Mathlib-shaped track. This report flags the boundary and stops.

---

## Appendix A — frisk receipts (for Monkey's on-disk check)

Mathlib checkout: `Lean/.lake/packages/mathlib` @ `5e932f97dd25535344f80f9dd8da3aab83df0fe6`.

```sh
# PRESENT spot-checks (each must hit):
grep -n "def cfc "            Mathlib/Analysis/CStarAlgebra/ContinuousFunctionalCalculus/Unital.lean
grep -n "noncomputable def log" Mathlib/Analysis/SpecialFunctions/ContinuousFunctionalCalculus/ExpLog/Basic.lean
grep -n "protected noncomputable def cfc" Mathlib/Analysis/Matrix/HermitianFunctionalCalculus.lean
grep -n "irreducible_def klDiv" Mathlib/InformationTheory/KullbackLeibler/Basic.lean
grep -n "structure VonNeumannAlgebra\|class WStarAlgebra" Mathlib/Analysis/VonNeumannAlgebra/Basic.lean
grep -n "def PosSemidef"      Mathlib/LinearAlgebra/Matrix/PosDef.lean
grep -rn "StandardSubspace"   Mathlib/Analysis/InnerProductSpace/StandardSubspace.lean | head -3
# ABSENT spot-checks (each must return nothing):
grep -rn "vonNeumannEntropy\|quantumRelativeEntropy" Mathlib/ --include="*.lean"
grep -rn "Pinsker" Mathlib/ --include="*.lean"
grep -rn "Duhamel\|Kubo" Mathlib/ --include="*.lean"
grep -rn "def Matrix.exp\b" Mathlib/ --include="*.lean"
grep -rn "Schatten\|traceClass" Mathlib/Analysis/ --include="*.lean"
```

Scratch compile: `cd Lean && lake env lean <scratchpad>/StateSideFrisk.lean` → clean (imports of GNS, CP-maps, VonNeumannAlgebra, KL, ExpLog, HermitianFunctionalCalculus, MatrixExponential, PosDef, Tilted, StandardSubspace; `#check`s of all Table-2 decls; density-matrix `Prop` elaborates under `open scoped ComplexOrder`).

Paper anchors on branch: `ax:maxent` L984, `def:closure-defect` L1051, `lem:closure-residual` L1059, `par:cicclause` L1076, `rem:msascope` L2197. Lean anchors: `no_integral_flux_retraction` CollarLayer.lean:690, `collarClause_not_channel_determined` :768, `IsEquivariantChannel` :837, `equivariant_closure_cannot_force` :1074, honest-scope block :815–831.
