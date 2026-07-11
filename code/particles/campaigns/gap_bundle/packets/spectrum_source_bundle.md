# Spectrum Source Bundle Packet

Search for one shared OPH excitation/trace-lift source beneath charged leptons,
quarks, and neutrinos.

Return `shared_source_candidate` only if one source object projects cleanly to
the charged affine anchor, quark selected-class boundary, and neutrino PMNS
surface. Otherwise return `blocked` with distinct lane boundaries.

Do not hide selected-class scope or PMNS tension behind exact mass rows.

## Worker Result

`constructive_trace_lift_schema_emitted`.

The first worker pass identified a reusable schema but did not close the shared
source theorem.  That is not accepted as an endpoint result; the constructive
artifact to implement next is the source-normalized trace-lift descent.

The reusable schema is a source-normalized trace-lift descent:

```text
S -> trace/excitation lift Xi_sector -> sector readout O_sector.
```

A shared theorem would need one source-normalized lift whose restrictions are
simultaneously:

- the charged determinant/affine anchor;
- the selected public quark sigma datum on `f_P`;
- the neutrino weighted-cycle bridge/Majorana-holonomy surface.

The current corpus does not emit that common normalization identity.  The
schema is therefore a useful proof template, not a promotable shared source
theorem.

## Lane Boundaries

- Charged leptons remain blocked on the determinant normalization identity
  `3 mu(r) = sum_e M_e^ch log q_e(r)`, equivalently
  `N_det(P) = 0`.
- Quarks remain closed only as a selected-class theorem on the public frame
  class `f_P`; no global frame-class classification is claimed.
- Neutrinos are open at source level. The weighted-cycle point is a rejected,
  target-informed comparison candidate; its historical basis transport is
  tautological, and neither physical PMNS nor absolute masses are emitted.

## Direct-Use Conclusion

Keep `SourceNormalizedTraceLiftDescent` as the implementation target.  The next
worker or local patch must instantiate at least one sector restriction of the
schema, preferably the charged determinant normalization surface
`N_det(P) = 0`, or emit a machine-readable certificate interface for that
restriction.  Do not use the schema to promote charged-lepton rows, globalize
the quark theorem, or promote the rejected neutrino candidate.

Obstruction-only output is not an accepted result.
