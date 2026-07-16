# Vector Correlator / HVP Diagnostic Lane: Status

Output class: diagnostic, non-promoting. row_class
`diagnostic_non_promoting_lattice_backend`, `physical_claim` false. This
lane is the registered #425 computed-spectral-density path at diagnostic
scale; nothing in it carries promotion weight.

## What the module computes

`lattice_backend/vector_correlator.py` measures, on quenched configurations
from the existing heatbath generator and clover-Wilson point propagators,

    G(t) = (1/3) sum_k sum_x Re Tr[gamma_k S(x,0) gamma_k
                                   gamma_5 S(x,0)^dag gamma_5],

the zero-momentum local-vector two-point correlator for one flavor of unit
charge (color trace included, so the spectral density sits in the R-ratio
normalization `N_c Q^2` of the payload contract). From the folded
correlator it computes the Bernecker-Meyer time-momentum moment

    4*pi * sum_t G(t) * K(t; a*mZ),   K(t; Q) = t^2 - (4/Q^2) sin^2(Q t/2).

## Correspondence to the payload contract

The contract (`ward_projected_payload/payload_harness.py`) emits
`Delta_had = mZ^2/(3*pi) * int ds rho_R(s)/(s*(s+mZ^2))` with `rho_R` in
R-ratio normalization. With the spectral representation
`G(t) = int domega omega^2 rho(omega^2) exp(-omega t)` and
`rho = rho_R/(12*pi^2)`, exact algebra gives

    Delta_had = 4*pi * Pihat(mZ^2) = 4*pi * int dt G(t) K(t; mZ),

so the TMR moment above is the contract moment in lattice units. The
identity is verified in `test_vector_correlator.py` against the exact
discrete-time geometric-series sum and against the contract-side closed
form `kernel_moment_atom`. Conversion factors the lane cannot certify are
emitted as separate declared fields in the artifact:

- `a*mZ` (the contract mZ in lattice units): a source-emitted scale setting
  is work in progress. The artifact reports the moment on a declared
  `a*mZ` grid and in the `a*mZ -> infinity` limit `K(t) = t^2`; any coarse
  lattice (`a^-1 << mZ`) sits in that limit to relative accuracy
  `4/(a*mZ)^2` for `t >= 1` (about 2e-3 at `a^-1 = 2 GeV`).
- `Z_V^2`: local-current renormalization, declared 1, uncertified.
- charge factor `Q_u^2 + Q_d^2 = 5/9` for the U(1)_Q light connected
  doublet; quark-line disconnected contributions are absent.

## Demo run

`run_vector_correlator_diagnostic.py` (seed 20260716) generates a quenched
ensemble at beta 5.7 on 16 x 4^3 (Cabibbo-Marinari heatbath, 40
thermalization sweeps, 10 separation sweeps, 6 configurations), measures
G(t) at kappa 0.150, c_SW 1.0, and writes
`code/particles/runs/hadron/lattice_vector_correlator_diagnostic.json`
(deterministic content hash over the physics block; wall-clock fields live
in a separate volatile block). Wall time is about five minutes single-core
(307 s measured).

Measured at the demo scale (t^2 kernel, unit-charge single flavor, lattice
units):

- moment = 38.03 +- 8.23 (jackknife over configurations), relative
  statistical error 0.216.
- U(1)_Q light-doublet weighted (charge factor 5/9): 21.13 +- 4.57.
- plaquette mean 0.5545 at beta 5.7 (literature large-volume value 0.549).
- G(t) is positive on all timeslices and symmetric about T/2 within errors.

The statistical error is dominated by the large-t tail, where the t^2
kernel weights the noisiest region of the correlator; this is the standard
TMR long-distance problem and scales with the ensemble as described below.

## 2026-07-16 update: statistics run, corrected contraction, Z_V, hybrid bracket

Same-day extension for the hybrid IR bracket diagnostic
(`run_hybrid_ir_bracket_diagnostic.py`, artifact
`code/particles/runs/hadron/hybrid_ir_bracket_diagnostic_2026-07-16.json`,
envelope spec declared and hashed before evaluation, plus one recorded
amendment fixed from the free-field anchor).

- Polarization correction: the engine pairs direction mu with GAMMA[mu]
  and site axis mu; the correlator time axis is axis 0, so GAMMA[0] is the
  temporal polarization. Its zero-momentum channel is a small flat remnant
  (local-current O(a) non-conservation), verified on the free field. The
  demo contraction above averages GAMMA[0..2] and therefore carries a
  factor 2/3 dilution relative to the per-polarization transverse
  correlator, and its apparent large-t plateau (about 0.55) is partly the
  temporal constant. New measurements use
  `lattice_backend/conserved_vector.py::transverse_vector_correlator`
  (GAMMA[1..3]). The demo artifact and this file's demo-run numbers are
  left as recorded; they are the diluted contraction.
- Statistics (ensemble A, `hybrid_A_quenched_b5p7_16x4c3`): 16 x 4^3,
  beta 5.7, kappa 0.150, seed 716001, 100 thermalization sweeps
  (plaquette history stored; thermalization check passed), 64
  configurations at 10-sweep separation. tau_int(plaquette) = 0.91,
  tau_int(moment) = 0.5 (no error inflation triggered). Transverse t^2
  TMR moment, physical normalization: 330.2 +- 46.8, relative statistical
  error 14.2% (demo lane: 21.6% at 6 configurations on the diluted
  contraction).
- Conserved current: exact point-split Noether current implemented
  (`conserved_local_correlator`), backward-difference Ward identity
  verified off-source to 1e-12 relative on a rough background; free-field
  estimator anchor Z_V^eff = C_CL/(2 kappa C_LL) = 1 to 5e-3. Measured
  Z_V (windowed) = 0.76 +- 0.42 on ensemble A; one window point flagged
  outside (0.2, 1.2) by noise contamination.
- Hybrid IR bracket outcome (compare-only, non-blind, diagnostic,
  non-promoting): S_IR = 0.96 +- 1.52 (stat); the statistical error is
  dominated by the vector-mass matching jitter (a*m_V = 1.43 +- 0.66,
  vector channel in noise from t = 6 on this volume), the moment itself
  sits at 14.2%. With the declared quadrature envelope E_total = 1.68 the
  interval clamps at zero: S_IR in [0, 2.57]. Hybrid s_effective bracket
  [0.5578, 1.7679], WIDER than the frozen dichotomy bracket
  [0.5578, 1.0543] by factor 2.44; S_required = 0.8954 (compare-only)
  stays inside, 0.34 from the nearest edge. Width in Delta_source units:
  5.97 alpha^-1 against the 2.1e-8 pass tolerance, 8.5 orders of
  magnitude remaining.
- Ensemble B (24 x 6^3, beta 5.7, seed 716002) did not survive the
  wall-clock budget (declared truncation to 10 configurations, process
  died at configuration 8 before the cache was written); the larger
  geometry plus a smeared vector source (earlier plateau, stable m_V
  matching) is the declared next step for a hybrid interval narrower than
  the dichotomy it replaces.

## Ensemble scale for 10% and 1% on the IR contribution

The target quantity is the IR part (sqrt(s) below about 2 GeV) of the
contract moment, the region the payload bracket spans with the
free-parton versus zero-support dichotomy. Scaling from the demo point:

- Statistics: the jackknife error scales as 1/sqrt(N_meas) with
  N_meas = n_cfg x n_sources. The demo has 6 measurements (one point source
  each) at relative error 0.216; reaching 10% statistical needs N_meas of
  order 6 x (0.216/0.10)^2 = 28 measurements, i.e. about 30 configurations
  at one source each (or 7 configurations at 4 sources) on the demo volume,
  about 25 minutes at the demo cost. Reaching 1% statistical at fixed
  volume needs 6 x (0.216/0.01)^2 = 2800 measurements. Statistical error at
  fixed N_meas also drops with spatial volume (self-averaging,
  proportional to 1/sqrt(V3)); a 16^3 spatial volume gives a factor 8 in
  effective statistics over 4^3.
- Physics floor: a 10% IR number additionally requires the rho region to be
  resolved: a^-1 of at least 2 GeV (beta about 6.0 quenched) and
  m_pi L of at least 3-4 with a pion light enough to sit below the rho,
  which forces L of at least 24-32 sites. A concrete 10% quenched target:
  24^3 x 48, beta 6.0, O(100) configurations, O(4) sources. Cost relative
  to the demo: site factor (24^3 x 48)/(4^3 x 16) = 648, times O(10) for
  lighter-quark CG iteration growth, times O(60) in measurements, about
  4e5 x the five-minute demo, order 10^4 core-hours. This is
  HPC-batch scale, outside a laptop budget, and it carries the
  quenching and Z_V systematics as floors of order 10% themselves, which is
  why 10% is the ceiling of the quenched lane.
- 1%: requires 2+1 dynamical flavors at or near physical pion mass,
  three or more lattice spacings for a continuum limit, physical volumes
  m_pi L above 4 (48^3 x 96 scale at a = 0.06-0.09 fm), O(10^3)
  configurations, nonperturbative Z_V (or the conserved current),
  disconnected diagrams, and isospin/QED corrections at the percent level.
  This is the published BMW/Mainz HVP program scale, order 10^7-10^8
  core-hours, and in this repo it additionally requires the seeded 2+1
  family of `derive_full_unquenched_correlator.py` executed on an external
  production backend.

## What stays open for #425

- Unquenching: the demo ensemble is pure gauge; the dynamical branch of the
  engine (two-flavor pseudofermion HMC) is validated on small chains and
  ensemble production with it is work in progress.
- Continuum limit: single coarse lattice spacing; no a -> 0 extrapolation.
- Source-emitted scale setting: `a*mZ` is undefined without a scale emitted
  by the source chain; the artifact carries the moment on a declared grid
  plus the t^2-kernel limit instead of a single certified value.
- Current renormalization: local current with Z_V declared 1; the conserved
  (point-split) current is work in progress.
- Disconnected contributions, finite volume, unphysical pion mass, and the
  strange/charm valence sector are all uncontrolled at demo scale and are
  listed in the artifact's systematics block.
- The #425 pass tolerance (4e-9 relative on Delta_had, per
  `ward_projected_payload/PAYLOAD_STATUS.md`) sits about six orders of
  magnitude beyond the 1% program above; this lane replaces the IR
  dichotomy with a computed density at 10-30% class precision and does not
  approach the pass tolerance.

## Files

- `lattice_backend/vector_correlator.py`: correlator contraction, folding,
  TMR kernel and moment, jackknife, analytic references.
- `run_vector_correlator_diagnostic.py`: seeded demo run and artifact
  emission.
- `test_vector_correlator.py`: synthetic round trip (discrete-exact and
  contract closed form), free-field anchor, determinism, non-promotion
  gates (8 tests).
- `code/particles/runs/hadron/lattice_vector_correlator_diagnostic.json`:
  demo artifact.
