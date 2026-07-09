# CMB Simulation Promotion to a Physical Prediction

## Motivating Result

This note entered the queue after the public OPH mini-universe simulator began
showing an all-sky observer-boundary record view that looked CMB-like enough to
be scientifically tempting:
[simulation.floatingpragma.io](https://simulation.floatingpragma.io). The
relevant external precision surface is the real CMB likelihood problem, for
example Planck's final cosmological-parameter analysis:
[Planck 2018 VI](https://www.aanda.org/articles/aa/full_html/2020/09/aa33910-18/aa33910-18.html).

The issue is not that ordinary CMB physics has a mystery called "visual
promotion." Standard cosmology treats a pretty CMB-like map as insufficient for
a prediction: physical claims require an initial source model, a background
geometry, transfer through a Boltzmann solver, instrument/noise treatment, and a
likelihood comparison. The OPH-specific problem is sharper: OPH simulations
produce bounded self-reading observer patches, overlap records, repair moves,
and emergent screen data. That makes a CMB-like output conceptually important,
but it also makes overpromotion easy unless the source, geometry, transfer, and
data-use boundaries are theorem-level objects.

**Status:** solved as a promotion-ladder theorem package and simulator
contract. Visual and spectrum outputs remain diagnostics until source,
geometry, transfer, no-data-use, freeze, and likelihood receipts close.

Date: 2026-07-08

## OPH Answer

The OPH answer is a promotion ladder:

| Tier | Claim | Required Meaning |
|---|---|---|
| `VISUAL_DIAGNOSTIC` | the simulator emits a CMB-like all-sky record field | useful visual evidence only |
| `SPECTRUM_DIAGNOSTIC` | reproducible spectrum or residual diagnostics exist | measurement-facing comparison only |
| `SOURCE_ONLY_FINITE_ARTIFACT` | the field is generated from frozen OPH source artifacts | no CMB, BAO, SN, WL, RSD, cluster, posterior, residual, or likelihood path enters the source DAG |
| `CONDITIONAL_PHYSICAL_CMB_SOURCE` | the source is promoted through a physical scale/freezeout bridge using imported frozen FLRW geometry | a conditional physical pipeline, not an OPH-native geometry derivation |
| `OPH_NATIVE_PHYSICAL_CMB_SOURCE` | the same source is promoted through quotient-derived `CosmoGeomRead_r` | native OPH cosmological geometry |
| `LIKELIHOOD_EVALUATED_PHYSICAL_CMB_PREDICTION` | frozen source, transfer, solver, and likelihood receipts pass | a real physical CMB prediction |

The simulator can supply finite witnesses, values, residuals, hashes, and
failure receipts. The paper stack supplies the semantic objects and theorem
arrows that decide what those values are allowed to mean.

## No Visual Shortcut Theorem

**Theorem 1** (no visual shortcut to physical CMB prediction). A simulator
output that visually resembles the CMB, or even fits a CMB-like spectrum, is not
a physical CMB prediction unless its terminal prediction artifact is reached
through a typed dependency DAG whose source, geometry, transfer, no-data-use,
freeze, and likelihood predicates all verify from their own artifacts and
parent hashes.

*Proof sketch.* Let every artifact node carry its value, units, semantic type,
parent list, data ledger, code/build hash, theorem hash, witness hash, and
error envelope. A terminal `PHYSICAL_CMB_PREDICTION_RECEIPT` verifies by
recomputing its predicate from those fields, not by trusting a caller-supplied
Boolean. Induct over the dependency DAG. Each passed node implies its parent
predicates. Therefore a passed terminal prediction implies that the source
artifact was frozen before evaluation, that forbidden observational data did
not enter the source path, that scale and freezeout were physically typed, that
the Boltzmann transfer was fixed, and that the likelihood rule was declared in
advance. Visual similarity has no edge in this DAG, so it cannot promote the
claim.

## Finite Source Object

At regulator \(r\), the CMB branch object is:

\[
\mathfrak C_r=
(\mathcal F_r,\Gamma_r,Q_r,\mu_r,\mathfrak S^{\rm scr}_r,
\mathfrak S^{\rm prim}_r,\mathcal S_{{\rm OPH},r},
\mathfrak I_{\star,r},\mathfrak B_r,\mathcal L_D,\mathsf{DAG}_r).
\]

Here \(\mathcal F_r\) is the early OPH screen federation: bounded
observer-like patches with local state, ports or overlap boundaries, readback,
records, feedback or repair moves, and public evidence receipts. The quotient
\(Q_r=\Sigma_r/\Gamma_r\) removes gauge representatives, port relabelings, mesh
labels, worker IDs, retry counters, hidden carrier coordinates, and inert
ancillary data.

The source law is not the settled state. It must be a law on the quotient:

\[
\mu_r(q)=Z_r^{-1}m_r(q)e^{-S_r(q)}.
\]

Normal forms classify representatives; they do not select the probability law.
The simulator therefore needs `source/quotient_ensemble.json` with quotient
schema hashes, base measure, action terms, zero-mode policy, sampler hash,
detailed-balance or stationarity checks, and partition-invariance receipts.

## Gate Package

The full readiness predicate is:

\[
\begin{aligned}
\mathsf{CMB\_READY}_r={}&
R_Q \wedge R_\mu \wedge R_{\rm DAG} \wedge R_{\rm no\ data}
\wedge R_q \wedge R_K \wedge R_A \wedge R_{\rm screen}\\
&\wedge R_{\rm coh} \wedge R_{\rm radial} \wedge R_{\rm prim}
\wedge R_{\rm scale} \wedge R_{\Sigma_\star} \wedge R_{\rm init}\\
&\wedge R_{\rm parent}^{\rm opt} \wedge R_{\rm kernel}^{\rm opt}
\wedge R_{\rm transfer} \wedge R_{\rm freeze}
\wedge R_{\rm like} \wedge R_{\rm fals}.
\end{aligned}
\]

The optional dark/stress terms are optional only when the declared run has
`dark_continuation: OFF`. If the claim includes OPH dark/anomaly cosmology,
then the finite covariant parent and kernel receipts become mandatory.

The important semantic split is:

- `CONDITIONAL_PHYSICAL` may use an imported, frozen FLRW geometry packet while
  still testing OPH-native source artifacts through physical scale, clock,
  freezeout, and transfer gates.
- `OPH_NATIVE_PHYSICAL` additionally requires quotient-derived
  `CosmoGeomRead_r`, source embedding, and geometry-origin receipts.

Imported FLRW geometry may exercise the physical pipeline. It must not be
renamed as OPH-native geometry.

## No-Data-Use Firewall

A source artifact is source-only iff no transitive parent, cache, config,
environment variable, dependency version, random stream, network read, file
read, model-selection rule, or human branch choice has a path from forbidden
observational data. Forbidden data include CMB maps, spectra, residuals,
likelihoods, and posteriors; BAO; supernovae; weak lensing; RSD; SPARC;
clusters; \(H_0/S_8\) target values; diagnostic overlays; and residual plots.

This forbids common quiet shortcuts:

- choosing the scale bridge by CMB peak alignment;
- fitting \(A_\zeta\), \(q_{\rm IR}\), \(\ell_{\rm IR}\), or kernels from a
  Planck residual;
- using a cached posterior or trained emulator that saw the target spectra;
- exposing a human branch choice to CMB overlays before source freeze;
- silently importing LambdaCDM best-fit parameters as OPH source parameters.

## Simulation Contract

The simulator should emit a promotion ledger in addition to plots:

```bash
python3 -m oph_fpe.cli cmb-promotion-ledger \
  --run-dir runs/<run_id> \
  --out runs/<run_id>/cmb_promotion_ledger
```

The ledger reports:

- current claim tier;
- conditional imported-FLRW scale-bridge status;
- OPH-native `CosmoGeomRead_r` status;
- source-only finite artifact status;
- geometric screen scalar, radial-lift, freezeout, transfer, likelihood, and
  prediction receipts;
- forbidden input classes and semantic type boundaries;
- blockers and the fail-closed outcome.

The measurement pack carries `cmb_promotion_ledger_report.json`,
`cmb_promotion_ledger_report.md`, and summary flags in `claims.json`, so OPH
Sage and public reviewers ingest the claim tier rather than inferring it from
images.

## Outcome

This problem closes at theorem-package level. The public simulator result is
important because it points to a concrete OPH finite-source CMB branch, not
because visual resemblance proves the branch. OPH solves the overpromotion risk
by forcing every CMB-like output through typed source, geometry, scale,
freezeout, transfer, no-data-use, and likelihood receipts. Until those receipts
pass in the same bundle, the correct label remains diagnostic or conditional,
not a likelihood-evaluated physical CMB prediction.
