# OPH Cosmology Papers

This directory holds OPH cosmology papers inside the public core repository.

These cosmology papers are very early, work-in-progress, unpublished research
drafts. They are not part of the OPH release paper bundle. They should be read
as staging documents for source, transfer, likelihood, and falsification gates,
not as completed OPH cosmology results.

## Public-Data Status

The dark-sector paper proposes a repair-charge condensate action. Its dilute
normal phase has pressureless background scaling. Its cubic condensed link
energy gives the spherical deep radial-acceleration law and baryonic
Tully--Fisher scaling. The same action supplies repair current, stress, and a
coherent-source coupling weighted by $\chi_\nu^{\rm can}$.

The canonical repair pair, source maps, dimensional calibrations, full
constitutive law, relativistic limit, abundance, lensing, CMB, clusters,
Solar-System response, and laboratory receipts are work in progress. The
paper supplies no closed physical dark-matter prediction. The
analytic tilt and CAMB rows are conditional comparison diagnostics, not an
OPH-native cosmology result. Reproducibility details and commands are in
The companion code under [`../code/dark_matter/`](../code/dark_matter/) contains
empirical and numerical diagnostics with no prediction status.

## Release Status

- `oph_dark_matter_paper.tex`
  - conditional repair-charge condensate action, repair-current balance,
    dust-like normal phase, cubic deep-galaxy branch, and coherent-source force

## Companion Papers

These files are public technical companions outside the release bundle.

- `oph_cosmology_finite_source_cmb_program.tex`
  - finite-source cosmology, physical CMB boundaries, scale bridge, simulator
    evidence, the conditional analytic $P_\star/48$ tilt comparison, and claim
    boundaries
- `oph_inflation_without_inflaton_observer_screen_synchronization.tex`
  - inflation-free branch: flatness, horizon coherence, geometric screen
    spectrum, screen release amplitude, radial lift, and hot source data
- `oph_cosmological_vacuum_and_structure_formation.tex`
  - OPH-native vacuum boundary, fluctuation ensembles, proto-object/worldline
    formation, and structure-seed checks
- `oph_cosmology_data_likelihood_contracts.tex`
  - source-provenance artifacts, no-data-use checks, pooled reducers, Boltzmann
    transfer, the public-data comparison ledger, and official likelihood
    comparisons
- simulator reference: https://github.com/muellerberndt/oph-physics-sim
- visualization companion: https://simulation.floatingpragma.io

The CMB companion distinguishes diagnostic proxies, conditional physical
artifacts using a declared imported FLRW packet, and OPH-native physical artifacts
derived from the quotient carrier.
Flat-sector work is likewise split: spatial Levi--Civita holonomy identifies the $\kappa=0$
branch, while direct theorem, conditional CMH, or explicit-assumption labels select it.

## Paper Split

Two cosmology papers would be too compressed. The split is five papers:

1. **Dark sector and structure**: the repair-charge condensate action and its conditional normal, condensed, and coherent-source branches; OPH derivation and physical evidence are work in progress.
2. **Finite-source CMB prediction program**: source-only inputs, scale calibration, Boltzmann transfer, declared likelihoods, and simulator checks.
3. **Inflation without inflaton**: observer-screen synchronization, flatness, horizon coherence, geometric screen spectrum, screen release amplitude, radial lift, and hot source data.
4. **Cosmological vacuum and structure formation**: OPH-native vacuum boundary, fluctuation ensembles, proto-object/worldline formation, and visualization-facing checks.
5. **Data and likelihood contracts**: CMB/LSS/BAO/SN/WL/growth comparison protocols.

All five cosmology papers are outside the release bundle and contain diagnostic
outputs only. Their physical source, transfer, and likelihood boundaries are
work in progress.
