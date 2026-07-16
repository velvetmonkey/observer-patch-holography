# Hybrid IR bracket diagnostic, 2026-07-16

Label: compare_only_non_blind. row_class diagnostic_non_promoting,
physical_claim false. The frozen v2 target, the payload grid, and
the protocol artifacts are unmodified; every analysis choice was
declared and hashed in the envelope spec before evaluation
(sha256 ab0951c593a68f104aa531d27c972dded2ee245e3260d74f461bd740a590e97d).

## Measurement

- Ensemble A (hybrid_A_quenched_b5p7_16x4c3): 64 cfgs, plaquette 0.55514, a*m_V = 1.4313, Z_V = 0.7557, moment stat. 14.2%, S_IR = 0.9587 +- 1.5201.

Central ensemble: A.
Envelope (quadrature, declared first): E_total = 1.6791;
S_IR interval [0.0000, 2.5685].

## Bracket

- Old S_eff bracket: [0.557779, 1.054347], width 0.496568.
- Hybrid S_eff bracket: [0.557779, 1.767874], width 1.210095 (wider than old by factor 2.437).
- S_required = 0.895400132648: inside the hybrid bracket; distance to nearest edge 0.3376.

## Distance to the pass tolerance

The hybrid bracket width in Delta_source units is 5.9716 alpha^-1 against the 2.1e-08 pass tolerance: a factor 2.844e+08, i.e. 8.5 orders of magnitude remain to the 4e-9 relative pass tolerance on Delta_had.

## Deviations and dominant limitation

- ensemble B (24x6^3, declared n_cfg 20, seed 716002) did not complete inside the wall-clock budget: the first attempt was restarted with a declared budget truncation to 10 configurations and the restarted process died at configuration 8 of 10 before its cache was written; no durable B data exists, so per the spec central rule ensemble A is central and B is absent from this artifact
- spec amendment hybrid_ir_bracket_envelope_spec_amendment_2026-07-16.json (sha256 382596e828b7bb259a253418d5ffc8bc611e0a06b61ebd693f666a03721f50ba): cosh effective mass in place of the plain log ratio, fixed from the free-field anchor before any interacting evaluation

The TMR moment itself reached 14.2% statistical precision (demo lane: 21.6% on the diluted contraction).
The S_IR statistical error is instead dominated by the vector-mass
matching jitter (a*m_V = 1.431 +- 0.658, with the vector channel entering noise at t >= 6 on this volume) and by the
Z_V window contamination, both propagated through the declared
jackknife. At this diagnostic scale the envelope clamps S_IR_lo at
zero, so the hybrid lower edge coincides with the old zero-support
edge and the upper edge exceeds the old free-parton edge: the
measured IR treatment is currently WIDER than the dichotomy it
replaces. The declared route to a narrower interval is a longer
time extent and larger spatial volume (the abandoned ensemble B
geometry) plus a smeared vector source for an earlier plateau.
