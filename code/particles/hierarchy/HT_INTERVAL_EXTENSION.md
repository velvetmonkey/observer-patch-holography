# Interval Extension of the Higgs/Top Declared Surface

Issue #333. This note defines how each equation node of the frozen
Higgs/top declared-surface map (`certificates/R_HT_declared_surface_certificate.json`)
is evaluated in the directed-rounding interval backend. The same definition
ships machine-readably in the `interval_extension` block of
`certificates/R_HT_interval_input_box_log.json` and executes in
`tools/ht_formula_stack.py`.

## Backend

`tools/outward_interval.py`: IEEE-754 binary64, correctly rounded
`+, -, *, /, sqrt` stepped one ulp outward per bound, in-module `exp`/`log`
with explicit series remainder pads, constants bracketed from exact
rationals and recorded decimal strings, `float.hex` serialization. The
Higgs/top stack adds no backend function.

## Node-by-node extension

| Node | Evaluation |
|---|---|
| `A_T = 3/2 + beta_EW/4`, `B_H = 4/3 - beta_EW/54` | outward interval `+, -, *` with `3/2, 1/4, 4/3, 1/54` bracketed from exact fractions |
| `rho_HT = log(1 + tau2_tree_exact)` | in-module interval `log` on the strictly positive interval `1 + tau2` (frexp reduction, atanh series, remainder pad `1e-25`; no libm log) |
| `eta_source^k`, `k = 2,4,5,6,8,9` | fixed chain of outward interval products: `eta^2`, `eta^4 = eta^2*eta^2`, `eta^5 = eta^4*eta`, `eta^6 = eta^5*eta`, `eta^8 = eta^4*eta^4`, `eta^9 = eta^8*eta` |
| `R_T`, `R_H` | outward interval polynomial combination of the power nodes with bracketed rational coefficients; the `eta^8/(2*beta_EW)` term uses outward interval division |
| `pi_y`, `pi_lambda` | outward interval `+, -, *` then division by `sqrt(pi)`, where `sqrt(pi)` is the correctly rounded `sqrt` of the bracketed `pi` decimal string, one ulp outward per side |
| `delta_y_t_mt`, `delta_lambda_mt`, `m_t_D11_GeV`, `m_H_GeV` | outward interval `*`, `+` against the declared D11 core and Jacobian input intervals |
| `Sigma_HT`, `w_HT`, `c_T_live`, `c_H_live` | same primitives; the exactifier divisions by `delta_n_tree_exact` use outward interval division on a zero-free box |
| Jacobian | forward-mode interval automatic differentiation in all eleven inputs with the same primitives, evaluated over the full input box |

## Input box

Each of the eleven declared branch inputs enters as a decimal string; the
certification box is the outward binary64 bracket of the exact rational
interval `[c - |c|*h, c + |c|*h]` with declared relative half width
`h = 1e-9`. Per-input roles, units or dimensionless normalization, and
provenance tags (candidate D10 tuple; declared D11 surface constants) are
recorded in the log. No measured particle mass value appears numerically
in the input box; the historical target-anchored selection of the declared
surface is recorded as a declared-branch provenance note, and source
derivation of the inputs stays an open upstream gate.

## Certified conditions

`validators/verify_ht_interval_box.py` recomputes every serialized bound
bit-exactly, checks the declared output decimals against the box
enclosures by exact rational comparison, certifies the diagonal chart
block `d(m_t, m_H)/d(pi_y, pi_lambda)` with both diagonal signs fixed and
the determinant bounded away from zero over the whole box, checks the
uniqueness scope (single-valued declared-surface arithmetic, injective
diagonal readout, no criticality-system existence or uniqueness claim),
enforces the input allowlist and provenance classes, and scans the verify
path for measured-constant markers.
