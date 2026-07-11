import ObserverPatchHolography.AbstractRewriting
import ObserverPatchHolography.Primitives
import ObserverPatchHolography.Rule90
import ObserverPatchHolography.CollarClause
import ObservableNormalForms
import ObserverPatchHolography.Bridges.ObservableNormalForms

/-!
# Observer-Patch Holography — Lean 4 umbrella root

Re-exports Jonathan Hill's concrete carrier/dynamics modules, the neutral
observation-determined normal-forms proof package, and the explicit bridge
between them.

**Status: preliminary skeleton rather than theorem-grade formalisation of
Proposition 4.2** from *Paradise as Fixed-Point Consensus*. The `Primitives`
module now carries an admission-free construction of the OPH primitives
(Records, Repair, Patch, Obs, Φ, gauge equivalence, and the discharged
`repair_respects_gauge`); OPH-Confluence and the `NF`/`World` quotient
construction remain open — these structurally depend on the companion paper
*Reality as a Consensus Protocol*.

See `../README.md` and `../PROOF_INDEX.md` for scope and completion tracking.
-/
