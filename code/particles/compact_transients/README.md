# Compact-Transient Receipts

This folder mirrors the compact-record transient simulator contract inside the
paper-stack code tree. It is a receipt scaffold, not a particle-spectrum
prediction and not an OPH confirmation of any transient catalog.

Run:

```bash
python3 particles/compact_transients/build_compact_transient_receipts.py \
  --output particles/runs/compact_transients/receipt_scaffold
```

The generated bundle freezes the CR0-CR4 claim ladder, history schema,
quotient/source/kernel/packet/detector/censoring receipts, FRB control family,
black-hole genealogy and no-generation-leakage guard, refinement/accuracy
contract, and promotion audit.

The default claim is `CR2_CONDITIONAL_PHENOMENOLOGY`. Promotion to
`CR3_FROZEN_PHYSICAL_PREDICTION` requires frozen controls, refinement, hashes,
and held-out likelihood receipts. Promotion to `CR4_SOURCE_ONLY_OPH_PREDICTION`
remains blocked until the compact source action, emission microphysics,
physical clock, old-host FRB source theorem, and black-hole genealogy prior are
OPH-derived without target leakage.
