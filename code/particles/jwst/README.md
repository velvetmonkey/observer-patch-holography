# JWST Compact-Object Source-Release Bridge

This directory mirrors the Question 3 JWST compact-object simulator contract
inside the paper-stack code tree. It is a receipt scaffold, not a particle
prediction and not evidence that JWST has confirmed OPH.

The production simulator implementation lives in `oph-physics-sim/oph_fpe/jwst`.
This local bridge keeps the paper-side code surface synchronized with the same
claim boundary:

- compactness is not assembly;
- red color is not age;
- luminosity is not stellar mass;
- broad lines are not black-hole mass;
- source release is not galaxy formation;
- JWST catalog counts, residuals, posteriors, anomaly labels, and likelihood
  values are forbidden source inputs.

From `reverse-engineering-reality/code/particles`:

```bash
python3 jwst/build_compact_object_source_release_receipts.py \
  --output runs/jwst/compact_object_source_release
```

The default emitted claim is `J0_DIAGNOSTIC_PROXY`. Any physical promotion
requires the downstream quotient, source-law, release, finite-parent,
degeneracy, forward-operator, abundance, and frozen-likelihood receipts.
