# The OPH Proof Spine

The end-to-end structure of the proof strategy, with the status of every step and a
complete register of open gaps. This is the master document of the docs/ set; the
companions carry the detail: [STRANGE_LOOP_PRINCIPLES.md](STRANGE_LOOP_PRINCIPLES.md)
(principles and claim rules), [STRANGE_LOOP.md](STRANGE_LOOP.md) (thesis and lineage),
[CONSISTENCY_STACK.md](CONSISTENCY_STACK.md) (forcing chain C1 to C10, lemmas, generator
table), [CLOSURE_LEDGER.md](CLOSURE_LEDGER.md) (the equations and their residuals),
[COMPRESSION_SCORECARD.md](COMPRESSION_SCORECARD.md) (dials, forward record, strict
accounting). Last updated 2026-07-15.

## The claim, in two parts

**Part A (the loop forces its constants).** A self-simulating universe that contains its
own simulation admits exactly one pixel constant P and one record capacity N, and those
values are the fine-structure and capacity readouts of the world inside it.

**Part B (the forced constants produce our universe).** Given (P, N) and the strange-loop
principles, the observed universe follows: its kinematics, its gauge structure, its
particle content, its gravity, its cosmology.

Part A closed by landed identification, plus Part B closed by discharged gates, is the
formal proof that our universe is the strange loop's unique solution. Nothing short of
that combination is claimed as proof anywhere in the corpus.

## Part A, step by step

| Step | Content | Status |
|---|---|---|
| A1 | Principles SL-0 to SL-5 stated once, with claim rules and the three-layer separation (theory, test, working) | done: STRANGE_LOOP_PRINCIPLES.md |
| A2 | The two closure equations defined with zero quantitative inputs: P = φ + √π/A_T(P); N = F(N) | done: theory layer |
| A3 | Uniqueness of P | PROVEN: exactly one fixed point per readout map on the declared physical domain (stage-2 interval Banach plus global subdivision certificate, both 2026-07-14) |
| A4 | Readback seed N₀ = π | PROVEN: D6 radius identity plus the CAP-P certificate |
| A5 | Tick-projection identity I1: Π_EW = 24π/(α_U·X) | PROVEN: discharged from the D10 transmutation step, the repair-tick theorem, and m_rep = 24 (G2-GAP-1 step S6) |
| A6 | Balance condition I2: Π_EW = β_EW·P | OPEN: premise CP-1, the one genuinely physical gap in Part A's mathematics (GAP-A2) |
| A7 | Readback form and dynamics | OPEN: premises CP-2 (inversion form; GAP-A3) and CP-3 (averaging carrier, dispensable for the fixed-point location; GAP-A4) |
| A8 | Conditional capacity theorem: under CP-1 to CP-3, N is forced to π·exp(6π/(P·α_U)), certified 3.5321315434×10¹²² at relative width 1.6×10⁻²⁵ | done as conditional theorem: G2-GAP-1, with its algebraic layer machine-checked in Lean |
| A9 | Identification with the measured α: the blind hadronic window | ARMED: first-principles bracket contains the required screening; window 2.1×10⁻⁸, frozen and timestamped; closing needs the hadronic moment at 4×10⁻⁹ relative (GAP-A1) |
| A10 | Identification with the measured Λ: the capacity comparison | STANDING AT 6.6%: becomes the live capacity test the moment CP-1 to CP-3 discharge (GAP-A5) |

## Part B, step by step

| Step | Content | Status |
|---|---|---|
| B1 | Consensus mechanics and the quantum event surface: quotient normal forms, Born rule, Lüders update, CHSH bound | theorem-grade on the declared branch; consensus core machine-checked (98 sorry-free Lean theorems) |
| B2 | Kinematics: Conf⁺(S²) ≅ SO⁺(3,1), 3+1 events, H³ observer space | theorem on the declared branch; realized-branch nonemptiness open (GAP-B1) |
| B3 | Gravity: Einstein equation from entropy stationarity, one global ambiguity +Λg | theorem on the declared five-axiom branch |
| B4 | Gauge structure and matter: compact group by reconstruction; SM quotient SU(3)×SU(2)×U(1)/Z₆, hypercharge lattice, N_c = 3, N_g = 3, one Higgs | theorem conditional on the compact-gauge receipt and declared MAR clause inputs (GAP-B9) |
| B5 | Electroweak masses and hierarchy: forward (M_W, M_Z), v/E★ transmutation law | forward record at 4.9 and 7.6 parts in 10⁴; hierarchy relation at 2.3×10⁻⁴; exact closure open (GAP-A6) |
| B6 | Strong sector: Λ_QCD by transmutation, nucleon mass via external lattice ratio | record at about 1×10⁻²; conditional tags in the scorecard |
| B7 | Cosmology: capacity Λ, dark sector as repair bookkeeping, screen tilt | record rows conditional; promotion gates open (GAP-B7) |
| B8 | Mass sector completion: flavor spreads, charged leptons, neutrinos | open (GAP-B3, GAP-B5, GAP-B4) |
| B9 | Machine formalization of the physics branches | program: consensus core plus coupling algebra done; branches open (GAP-B8) |

## The open-gap register

Every gap standing between the current state and the completed proof. Nothing is open
that is not on this list; anything removed from this list carries a dated verdict.

Part A gaps:

- **GAP-A1 (CL-1/CL-2, generator G1).** The blind hadronic window. The payload harness
  exists; the first-principles bracket contains the required screening; the pass needs
  the hadronic moment at 4×10⁻⁹ relative precision, beyond every current method with or
  without measured data. Discharged by: a non-perturbative method reaching the window,
  run under the frozen blind protocol.
- **GAP-A2 (CP-1).** The balance condition Π_EW = β_EW·P. Counting-theorem shape: one
  global repair tick per electroweak channel per pixel-area unit. Discharged by: a
  geometric counting theorem from declared screen structure. This is the highest-value
  open mathematics in the program.
- **GAP-A3 (CP-2).** Uniqueness of the port-load inversion form of Cap_read among
  readback families. Discharged by: a P4-coherence forcing argument extending the
  2026-07-14 exclusion run.
- **GAP-A4 (CP-3).** The averaging re-emission carrier. Dispensable for the fixed-point
  location; load-bearing only for the constructive contraction rate. Discharged by: a
  one-page lemma from the write/check orientation split, or any declared contraction
  toward balance.
- **GAP-A5 (CL-3/CL-4).** The 6.6% gap between the bridge capacity and the Λ readout.
  Becomes the live capacity test on discharge of CP-1 to CP-3: either a missing declared
  term is found on the Λ-readout chain, or the loop fails here, permanently.
- **GAP-A6 (CL-5, generator G3).** Forward electroweak structure beyond one loop. The
  96-entry preregistered menu is exhausted at certified pixels; the single landing at
  the rounded legacy carrier awaits its own frozen confirmation; the Z tension equals a
  3×10⁻⁵ pixel shift.
- **GAP-A7.** Uniqueness beyond the declared domain (α⁻¹ outside [100, 200]). Analytic
  refinement; no physical role at current standing.
- **GAP-A8.** P4 count-density coherence for the coupled readback (the argmax
  representation must agree with the fixed point). Recorded as an open obligation in
  G2-GAP-1.

Part B gaps:

- **GAP-B1.** Realized-branch nonemptiness for the Lorentz and compact-gauge branches.
- **GAP-B2.** Quantum pole receipts: the photon, gluon, and graviton zeros are classical
  action statements; the quantum pole constructions are open gates.
- **GAP-B3.** The flavor-orbit selector: the proven two-modulus non-identifiability names
  the missing object; twelve preregistered declared-structure candidates evaluated and
  excluded 2026-07-14.
- **GAP-B4.** The neutrino sector: no mixing matrix or absolute mass row is emitted; the
  weighted-cycle candidate is rejected by NuFIT 6.1 (permanent verdict).
- **GAP-B5.** Charged-lepton source completion: the MCPR triple is declared architecture;
  the A5/W5 orbit program is the open source-side derivation.
- **GAP-B6.** The Yang-Mills continuum certificate: the repair-gap identity is
  conditional on the declared multiresolution, reflection-positivity,
  transfer/intertwiner, and nontriviality receipts.
- **GAP-B7.** Cosmology promotion gates: the source-derived applicability rule the
  Cassini exclusion demands, the S8 tension, physical CMB promotion, and the κ_rep
  certificate for the tilt.
- **GAP-B8.** Lean formalization of the physics branches (the consensus core and the
  coupling algebra are done: 98 plus 13 sorry-free theorems).
- **GAP-B9.** The MAR clause inputs and compact-gauge receipt behind the SM quotient
  remain declared inputs; deriving them from the principles would move the gauge sector
  from conditional to forced.
- **GAP-B10.** Independent reproduction: named external parties re-running the mechanical
  claims from a fresh clone (pillar 5).

Cross-cutting:

- **GAP-X1.** Discrete structural selections not yet consistency-forced (the scorecard
  lists each with its menu size; the SM coefficient triple and β_EW = 4 graduated to
  forced on 2026-07-14; the remainder stand as counted selections).
- **GAP-X2.** CI regeneration of the ledger and scorecard from the claim registry
  (SLP-02, SLP-05), and builder-script patches so generated surfaces keep their
  supersession notes.

## Reading rule

The spine may only strengthen by dated artifact: a step moves to PROVEN when its
certificate or theorem lands, a gap leaves the register only with a verdict, and no
wording change ever substitutes for either. The compact proof presents this spine at
full strength; the ledger and scorecard price it; the frozen targets decide it.
