# OPH Cosmology Data and Likelihood Contracts

This paper states the minimum data and likelihood information required for an OPH cosmology comparison. A curve overlay or reduced residual is a diagnostic. A physical result requires a source-derived model, compatible transfer system, declared datasets and covariance, and a complete nuisance treatment. The OPH cosmology sources do not meet that boundary. Cosmology carries no falsification target or verdict.

## Comparison classes

Every reported number belongs to one of four classes:

1. **Source-derived:** all physical inputs follow from the declared OPH construction without using the comparison data.
2. **Imported:** established background or microphysical inputs are declared explicitly.
3. **Fit:** one or more parameters are inferred from the same data.
4. **Diagnostic:** the calculation tests shape, scale, code behavior, or an interface without supporting a physical OPH claim.

The current cosmology comparisons are diagnostic or imported. No source-derived joint cosmology likelihood exists.

## Required model information

A physical comparison must state the covariant action and source map, background solution and species content, gauge-invariant initial conditions, perturbation and exchange equations, observable projection, numerical tolerances, external inputs, and fitted parameters.

For the repair-charge dark-sector proposal, the dilute dust-like equation of state is a conditional action consequence. The abundance, relativistic stress, initial perturbations, lensing map, clusters, and nonlinear structure equations are work in progress.

## Required data information

A comparison must identify the data release, selection, masks, covariance, calibration model, nuisance parameters, priors, and combination rule. Dataset overlap and shared calibration must be included. A diagonal sum is not a joint likelihood when the covariance is non-diagonal.

Measured values that select a source formula, normalization, branch, or applicability domain are inputs to that comparison rather than OPH outputs.

## Observable contracts

| Observable family | Required theory output | Required comparison object |
|---|---|---|
| CMB | $C_\ell^{TT}$, $C_\ell^{TE}$, $C_\ell^{EE}$, lensing, foreground model | Map or band-power likelihood with covariance and nuisance model |
| BAO and supernovae | $H(z)$, $D_A(z)$, luminosity distance, sound horizon | Survey likelihood with calibration covariance |
| Weak lensing | Metric potentials, nonlinear matter power, intrinsic alignments | Tomographic likelihood with masks and covariance |
| Growth and RSD | $P_m(k,z)$ and $f\sigma_8(z)$ | Windowed survey likelihood with cross-bin covariance |
| Clusters | Mass function, selection, observable--mass map, lensing calibration | Count and calibration likelihood |
| Galaxies | Disk dynamics, gas and stellar nuisances, external environment | Galaxy-level likelihood with selection and covariance |

## Diagnostic results

The repository contains CMB overlays, compressed background comparisons, and galaxy scaling checks. Their formulas or inputs are selected with knowledge of the comparison data, omit required covariance or nuisance structure, or lack a physical source map. They test numerical paths and conditional formulas. They do not establish a cosmological prediction.

## No-data-use boundary

A source-derived calculation must expose its dependency graph. The source side may use mathematical constants, declared OPH finite artifacts, and explicitly imported physical inputs. It may not use the observed quantity being claimed as an output, a fit to that quantity, or a proxy calibrated from the same dataset.

This provenance rule is enforced through the declared dependency graph and data-use classification.

The physical primordial source, radial lift, repair-charge cosmological source, Boltzmann bridge, and joint likelihood are work in progress. All cosmological data products remain diagnostic. Cosmology is outside the OPH falsification program.
