# Formal receipt classification (issue #518, Lean surface)

Issue #518's first acceptance criterion asks that receipts be classified —
identity, schema, producer attestation, numerical recomputation, independent
prediction, or empirical comparison — because "a tautology can validate
plumbing, but it cannot support theorem-grade or predictive language."

This document applies that discipline to the **formal Lean surface**
(`Lean/ObserverPatchHolography/Source/`). The empirical-pipeline receipts
named in #518 (`N_CRC^EW`, Krawczyk intervals, Thomson promotion, consensus
benchmark, dark-matter anchors) live in `code/` and are **out of scope
here** — they are physics-surface artifacts and need the issue's own
recomputation/negative-control machinery, not a Lean pass.

Base for this classification: branch `fix/primitives-admission-free`
(Primitives with the constructed repair layer), plus the unchanged
`AbstractRewriting`, `Rule90`, and `Bridges` modules. The neutral
`Proofs/ObservableNormalForms` artifact is deliberately not reclassified
here: it is the protected submission artifact with its own axiom audit
(`AxiomAudit.lean`), and its receipts are hypothesis-bearing theorems, not
producer attestations.

## Classification buckets (formal analogues of #518's list)

| Bucket | Formal meaning | #518 analogue |
|---|---|---|
| **A — definitional/identity** | true by unfolding; validates encoding plumbing only | identity |
| **B — hypothesis-bearing theorem** | conditional mathematical content; hypotheses explicit | (theorem-grade, conditional) |
| **C — concrete positive witness** | a real instance discharging hypotheses non-vacuously | independent recomputation |
| **D — counterexample / negative control** | machine-checked failure when a hypothesis is dropped | executable negative control |
| **E — axiom-audit receipt** | `#print axioms` output pinning the axiom footprint | schema/audit |

Promotion discipline (matching #518's claim boundary): **bucket-A receipts
never carry theorem-grade language on their own** — each must be paired
with a bucket-C witness and, where a hypothesis can fail, a bucket-D
control.

## Inventory — Source/ObserverPatchHolography

### Bucket A (definitional; flagged in-file, none promoted as evidence)

| Receipt | In-file label | Paired non-degenerate counterpart |
|---|---|---|
| `demoCarrier_Hfib_holds_finerB` (`Primitives`) | "this endpoint therefore CANNOT fail and is NOT independent evidence — recorded only for completeness" | C: `demoCarrier_Hfib_holds_seed` (genuinely consumes both `Consistent` premises); D: `demoCarrier_Hfib_fails` |
| `demoBoundary_HB` (`Primitives`) | "trivially" (constant boundary) | D: `demoCarrier_Hfib_fails` shows the trivial boundary cannot pin the fiber |
| `rule90t_outer_eq` (`Rule90`) | "Helper" | consumed by the bucket-B/D theorems `rule90_no_frustrationFree_repair`, `rule90_Hfib_good` |

Audit verdict: all three definitional receipts are already labeled as
plumbing in their docstrings and none is cited as standalone evidence. No
replacement is required; this table pins them so future promotions cannot
silently upgrade them.

### Bucket B (hypothesis-bearing theorems, hypotheses explicit)

`consistent_iff_edgeConsistent`, `gaugeEquiv_equivalence`,
`repair_respects_gauge`, `termination`, `completeness`,
`confluence_of_commute`, `boundary_fiber_observer_unique`,
`lyapunovDescent_holds`, `termination_holds`, `Repair_normalForm`,
`Repair_reachable`, `Repair_eq_self_of_consistent`, Newman-lemma layer
(`AbstractRewriting`), bridge equivalence
(`boundaryIdentifiesModulo_iff_observerEndpointUniqueModuloLR`).

### Bucket C (concrete positive witnesses — the anti-vacuity layer)

`demoCarrier` + `obsMap_demoCarrier_nonconstant`, `demoLR_H1/H2/H3` +
`demoLR_has_step`, `demoCarrier_terminates`,
`acceptedStep_demoCarrier_nonempty`, `localRepair_demoCarrier_fires`,
`demoCarrier_Hfib_holds_seed`, `rule90_Hfib_good`,
`rule90_gauge_nontrivial`.

### Bucket D (counterexamples / negative controls)

`demoCarrier_repairs_dont_commute`, `demoCarrier_not_confluent`,
`demoCarrier_Hfib_fails`, `demoCarrier_dir_not_observer_unique`,
`rule90_Hfib_bad_fails`, `rule90_no_frustrationFree_repair`.

### Bucket E (axiom-audit receipts)

The `#print axioms` blocks in `Primitives.lean`, `Rule90.lean`,
`Bridges/ObservableNormalForms.lean`, and
`Proofs/.../AxiomAudit.lean` — all pinned at
`[propext, Classical.choice, Quot.sound]` or fewer, no `sorryAx`, no
`native_decide`, no new axiom.

## Verdict for #518 on the Lean surface

No tautological certificate on the formal surface is promoted as evidence;
each bucket-A receipt is labeled and paired per the discipline above. The
defects #518 enumerates are exclusively empirical-pipeline receipts in
`code/`, which this pass intentionally does not touch (physics surface,
separate recomputation/negative-control machinery required — see the
issue's remaining acceptance criteria).
