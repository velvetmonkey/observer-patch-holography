# Hadronic Precision Endpoint

## Motivating Result

This note entered the queue because several precision results kept pointing at
the same hadronic boundary. The immediate trigger was the Fermilab muon `g-2`
result, which reported the positive muon anomalous magnetic moment at 0.20 ppm
precision in 2023
([Muon g-2 Collaboration PDF](https://muon-g-2.fnal.gov/result2023.pdf)).
The same hadronic boundary also appears in rare-decay audits: LHCb reported the
rare `Sigma+ -> p mu+ mu-` observation in 2024
([CERN](https://home.cern/lhcb-investigates-rare-s-pmm-decay/)), while updated
rare `B`-decay lepton-universality measurements showed how earlier anomaly
claims can move when the full dataset and calibration change
([CERN](https://home.cern/lhcb-brings-leptons-line/)). The OPH question is
whether these apparently separate tensions share one missing source object: a
same-scheme hadronic precision backend.

Date: 2026-07-08

## Origin

This note records the OPH hadronic-precision audit prompted by the motivating
precision results. It asks whether the fine-structure endpoint, muon \(g-2\),
rare \(B\) decays, and rare \(\Sigma\) decays share one OPH bottleneck.

They do. The shared bottleneck is not a single informal
`rho_had(s)`. The required source object is the OPH hadronic precision backend:

```math
\mathscr H_{\rm had}^{\rm OPH}(P)
=
\left(
\mathfrak Q_r^{\rm QCD}(P),
\mathfrak S_r^{E,{\rm QCD}}(P),
\mathcal H_{\rm had}(P),
J_Q^{W,R,\mu}(P),
d\rho_Q^{(2)}(s;P),
d\rho_{QQQQ}^{(4)}(P),
d\rho_{\rm tr}^{B,\Sigma}(P),
\Xi_Q(P),
\mathcal E_{\rm sys}(P)
\right).
```

The status is source-open, simulation-buildable, empirical-closable, and
comparison-ready. It is not final physical closure.

## Why This Is One Problem

The two-current spectral measure \(d\rho_Q^{(2)}(s;P)\) is enough for the
fine-structure hadronic endpoint and hadronic vacuum polarization in muon
\(g-2\). It is not enough for hadronic light-by-light or rare-decay
long-distance amplitudes. Those require four-current and transition spectral
data:

```math
d\rho_{QQQQ}^{(4)}(P),
\qquad
d\rho_{\rm tr}^{B,\Sigma}(P).
```

The scalar two-point measure is therefore one marginal of a larger hadronic
precision functor, not the whole backend.

## OPH-QCD Quotient Ensemble

For regulator \(r\), the source QCD ensemble is

```math
\mathfrak Q_r^{\rm QCD}(P)
=
\left(
\Sigma_r^{\rm QCD},
\Gamma_r^{\rm QCD},
Q_r^{\rm QCD},
m_r^{\rm QCD},
S_r^{\rm QCD}(P),
c_{sr},
\mathcal A_r^{\rm phys},
\mathcal O_r^{\rm QCD}
\right),
\qquad
Q_r^{\rm QCD}=\Sigma_r^{\rm QCD}/\Gamma_r^{\rm QCD}.
```

\(\Sigma_r^{\rm QCD}\) contains finite gauge links, quark fields, boundary
conditions, source masses, couplings, current insertions, operator basis,
regulator metadata, and current-normalization metadata.
\(\Gamma_r^{\rm QCD}\) removes gauge representatives, mesh labels, port labels,
hidden carrier coordinates, worker IDs, repair schedule IDs, random-seed
presentation artifacts, and inert ancillas.

The source law is

```math
\mu_r^{\rm QCD}(q;P)
=
Z_r^{-1}m_r^{\rm QCD}(q)\exp[-S_r^{\rm QCD}(q;P)].
```

This law must be declared before precision comparison. A normal form is not a
probability law.

## Source-Law Non-Substitution Theorem

**Statement.** A simulator output cannot be promoted to a source-only OPH
hadronic prediction unless it is sampled from, or deterministically approximates,
a declared quotient-intrinsic law \(\mu_r^{\rm QCD}\) with refinement maps
\(c_{sr}\), current definitions, scheme metadata, and no-target-leakage
receipts.

**Proof sketch.** The normal-form map \(n_r:Q_r\to N_r\) is idempotent, but it
does not determine a probability law. Every law already supported on \(N_r\) is
fixed by the canonicalizer. Therefore settled or canonical status can classify
candidate hadronic sectors, but cannot choose the physical QCD law. If the law
is inferred from \(\alpha(0)\), \(g-2\), \(e^+e^-\to{\rm hadrons}\), hadron
masses, rare-decay data, or PDG QCD fits, the result is empirical closure or
calibration, not source-only OPH.

## Source QCD Parameter Map

The missing source map is

```math
\mathcal P_{\rm QCD}^{\rm src}:
P
\mapsto
\left(
g_3(P),
\theta_{\rm QCD}(P),
m_u(P),m_d(P),m_s(P),m_c(P),m_b(P),m_t(P),
Z_{\rm scheme}(P)
\right).
```

Without this map, a lattice or simulator backend can be a high-quality
Standard Model/QCD comparison engine, but not a fully OPH-native source theorem.
If quark masses or \(\Lambda_{\overline{\rm MS}}\) are imported from PDG or
hadron spectroscopy, the row is not source-only.

## Euclidean QCD Slab And Vacuum Transfer

The finite Euclidean QCD slab is

```math
\mathfrak S_r^{E,{\rm QCD}}(P)
=
\left(
Q_r^{\rm QCD},
m_r^0,
J_r,
V_r,
a_{t,r},
\Theta_r^{\rm RP}
\right).
```

With \(J_r(q,q')=J_r(q',q)\ge0\), the finite Euclidean Hamiltonian has form

```math
(H_r^E f)(q)
=
\frac{1}{m_r^0(q)}
\sum_{q'}J_r(q,q')\bigl(f(q)-f(q')\bigr)
+
V_r(q)f(q).
```

If \(J_r\) is symmetric nonnegative, the event graph is connected, \(H_r^E\)
is self-adjoint and bounded below on \(L^2(Q_r,m_r^0)\), and the transfer
family is reflection-positive and refinement-compatible, then the finite vacuum
law is

```math
\mu_r^{\rm vac}(q;P)=|\Omega_r(q;P)|^2m_r^0(q),
```

and the transfer operator is

```math
T_r=e^{-a_{t,r}(H_r^E-E_{0,r})}.
```

An HMC stationary distribution is not automatically an OPH vacuum. Vacuum
promotion requires the Euclidean slab and transfer receipts.

## Confined Hadronic Hilbert Quotient

Assuming an OPH-QCD continuum certificate, define

```math
\mathcal H_{\rm had}(P)
=
\overline{
\Pi_{\rm singlet}
\Pi_{\rm conf}
\Pi_{\rm Ward}
\mathcal H_{\rm QCD}(P)
}.
```

This is conditional on unquenched QCD with quarks, confinement, physical
currents, and spectral matrix elements. The current Yang-Mills continuum route
is not enough by itself.

Required continuum certificates include:

- `QCD_CONTINUUM_CERTIFICATE`
- `REFLECTION_POSITIVITY_CERTIFICATE`
- `TRANSFER_CONVERGENCE_CERTIFICATE`
- `CONFINEMENT_SINGLET_CERTIFICATE`

## Ward-Projected Renormalized Current

The electromagnetic current must be the conserved renormalized current on the
same \(U(1)_Q\) branch as the Maxwell endpoint:

```math
J_Q^{W,R,\mu}(x;P)
=
Z_V(P),
\Pi_{\rm Ward}
\Pi_{\rm singlet}
\Pi_{\rm conf}
\left[
\sum_q Q_q,\bar q(x)\gamma^\mu q(x)
\right]
+
J_{\rm contact}^{\mu}(x;P).
```

It must satisfy

```math
\partial_\mu J_Q^{W,R,\mu}=0,
\qquad
q_\mu\Pi_Q^{\mu\nu}(q;P)=0.
```

The current-normalization ledger is

```math
\mathcal N_Q(P)
=
\left(
Z_V,
J_{\rm conserved},
J_{\rm local},
J_{\rm contact},
\Pi_{\rm Ward},
\Omega_Q,
\text{scheme}
\right).
```

Without this ledger, the spectral measure has an arbitrary normalization
ambiguity.

## Two-Point Spectral Measure

The source two-current electromagnetic marginal is

```math
d\rho_Q^{(2)}(s;P)
=
\frac13\sum_{\lambda=1}^{3}
\left|
E_{\rm had}(ds;P)
J_Q^{W,R,\lambda}(0;P)\Omega_P
\right|^2.
```

If \(\mathcal H_{\rm had}(P)\) exists and
\(J_Q^{W,R,\mu}\Omega_P\in\mathcal H_{\rm had}(P)\), then
\(d\rho_Q^{(2)}\) is a positive locally finite measure supported on the
confined hadronic spectrum.

## Stieltjes/Jacobi Export

The simulator should not fit a free continuous spectrum as the primary object.
It should export a positive Stieltjes representation. For moments

```math
\mu_n(P)=\int s^n\,d\rho_Q^{(2)}(s;P),
```

the Hankel matrices \(H^{(k)}_{ij}=\mu_{i+j+k}\) must be positive semidefinite.
The endpoint export is

```math
\left(
J_{24,Q}(P),
\omega_Q(P),
\Xi_Q(P)
\right).
```

\(J_{24,Q}\) must come from the moment sequence or a Lanczos/Stieltjes
procedure. If its nodes and weights are chosen after seeing \(\alpha(0)\), the
object is a back-solve.

## Same-Scheme Endpoint Remainder

The remainder is

```math
\Xi_Q(P)
=
\Xi_{\rm sub}
+
\Xi_{\rm EW}
+
\Xi_{\rm QED}
+
\Xi_{\rm isospin}
+
\Xi_{\rm heavy}
+
\Xi_{\rm FV}
+
\Xi_{\rm cont}
+
\Xi_{\rm contact}.
```

All terms must be in the same electromagnetic convention as \(A_Z(P)\) and
\(A_{\rm Th}(P)\).

## Fine-Structure Endpoint Closure

If OPH emits \(d\rho_Q^{(2)}(s;P)\) and \(\Xi_Q(P)\), then

```math
\Delta_{\rm had}(P)
=
\frac{m_Z(P)^2}{3\pi}
\int_{s_{\rm th}}^\infty
\frac{d\rho_Q^{(2)}(s;P)}
{s[s+m_Z(P)^2]}
+
\Xi_Q(P)
```

is source-side. If

```math
A_{\rm Th}(P)
=
A_Z(P)
+
\Delta_{\rm lep}(P)
+
\Delta_{\rm had}(P)
+
\Delta_{\rm EW}(P)
```

and \(G(P)=\varphi+\sqrt\pi/A_{\rm Th}(P)\) is a contraction on the declared
interval, then the pixel fixed point \(P_\star\) is unique and
\(\alpha(0)=1/A_{\rm Th}(P_\star)\).

## Full Hadronic Precision Functor

Define

```math
\mathscr R_{\rm had}^{\rm OPH}
:
(J_1,\ldots,J_n;\mathcal O_i;H_i\to H_f)
\mapsto
\left(
d\rho_{J_1\cdots J_n},
d\rho^{\rm tr}_{H_i\to H_f;i},
\Xi
\right).
```

Required special cases:

```math
\mathscr R_{\rm had}^{\rm OPH}(J_Q,J_Q)=d\rho_Q^{(2)},
```

```math
\mathscr R_{\rm had}^{\rm OPH}(J_Q,J_Q,J_Q,J_Q)=d\rho_{QQQQ}^{(4)},
```

```math
\mathscr R_{\rm had}^{\rm OPH}(\mathcal O_i^{b\to s},J_Q;B\to K^{(*)})
=d\rho_{B\to K^{(*)};i}^{\rm tr},
```

```math
\mathscr R_{\rm had}^{\rm OPH}(\mathcal O_i^{\Delta S=1},J_Q;\Sigma\to p)
=d\rho_{\Sigma\to p;i}^{\rm tr}.
```

The scalar insufficiency theorem is immediate: the two-current measure is
sufficient for running-\(\alpha\) hadronic transport and HVP \(g-2\), but it is
insufficient for HLbL \(g-2\) and rare-decay long-distance amplitudes.

## Simulator Claim Tiers

| Tier | Meaning |
| --- | --- |
| H0 | raw diagnostic run, no physical claim |
| H1 | conventional QCD reference ensemble |
| H2 | OPH-native quotient ensemble declared |
| H3 | OPH finite vacuum promoted |
| H4 | continuum/confined QCD certificate candidate |
| H5 | Ward two-point spectral source interval |
| H6 | full hadronic precision functor interval |
| H7 | source-only precision prediction beating direct comparison interval |

The first implementation milestone is `HVP_ALPHA_SOURCE_PROTOTYPE`, not rare
decays. It should output \(C_{QQ}(t)\), \(d\rho_Q^{(2)}\) or Stieltjes bounds,
\(J_{24,Q}(P)\), \(\omega_Q(P)\), \(\Xi_Q(P)\), and \(\Delta_{\rm had}(P)\),
then compare only after freezing.

## Minimum Receipt Bundle

The simulator backend must emit a directory with:

- `manifest.json`
- `source_dag.json`
- `qcd_ensemble/quotient_schema.json`
- `qcd_ensemble/gamma_groupoid.json`
- `qcd_ensemble/base_measure.json`
- `qcd_ensemble/source_action.json`
- `qcd_ensemble/source_parameter_map.json`
- `qcd_ensemble/coarse_maps.json`
- `vacuum/euclidean_slab.json`
- `vacuum/transfer_operator.json`
- `vacuum/reflection_positivity.json`
- `vacuum/vacuum_promotion.json`
- `currents/ward_current_definition.json`
- `currents/current_normalization_ZV.json`
- `currents/contact_terms.json`
- `currents/ward_residuals.csv`
- `correlators/vector_current_2pt_raw.json`
- `correlators/vector_current_2pt_covariance.json`
- `correlators/disconnected_diagrams.json`
- `correlators/autocorrelation_report.json`
- `spectral/moments.json`
- `spectral/hankel_positivity.json`
- `spectral/stieltjes_bounds.json`
- `spectral/J24Q.json`
- `spectral/omegaQ.json`
- `spectral/spectral_interval.json`
- `endpoint/kernel_definition.json`
- `endpoint/Xi_same_scheme.json`
- `endpoint/Delta_had_interval.json`
- `endpoint/ATh_interval.json`
- `endpoint/pixel_contraction_interval.json`
- `higher_point/Q4_HLbL_receipt.json`
- `higher_point/transition_B_to_K_receipt.json`
- `higher_point/transition_Sigma_to_p_receipt.json`
- `controls/no_target_leak_dag.json`
- `controls/empirical_data_exclusion_manifest.json`
- `controls/frozen_code_hashes.json`
- `controls/replay_receipts.json`
- `controls/comparison_data_manifest.json`
- `claim.md`

`claim.md` must say exactly one of:

- `CONVENTIONAL_QCD_REFERENCE`
- `SOURCE_PROTOTYPE_NOT_PROMOTED`
- `SOURCE_INTERVAL_PROMOTED`
- `EMPIRICAL_CLOSURE_ONLY`
- `COMPARISON_ONLY`

## Forbidden Source Inputs

The source lane must exclude:

- `CODATA_ALPHA`
- `MUON_G_MINUS_2`
- `EE_TO_HADRONS`
- `RARE_DECAY_DATA`
- `HADRON_MASS_TARGETS`
- `PDG_QCD_FITS`

If any forbidden target enters the source DAG, the claim must fail closed as
`TARGET_LEAK_DETECTED`.

## Open Theorem

Construct, from OPH source data alone, a refinement-compatible family

```math
\left(
\mathfrak Q_r^{\rm QCD}(P),
\mathfrak S_r^{E,{\rm QCD}}(P),
J_{Q,r}^{W,R,\mu}(P),
c_{sr}
\right)
```

such that the quotient ensemble law is declared, the QCD parameter map is
source-emitted, the Euclidean slab promotes to a physical vacuum, the continuum
limit gives an unquenched confined QCD Hilbert quotient, the electromagnetic
current is Ward-projected and endpoint-normalized, \(d\rho_Q^{(2)}\) and
\(\Xi_Q\) are emitted with computable errors, \(J_{24,Q}\) is derived from
source correlators rather than fitted to \(\alpha(0)\), the higher-point and
transition extensions are emitted, and the no-target-leak DAG has no path from
the forbidden comparison data.

Until this theorem is proved or constructively certified, the hadronic
precision endpoint remains source-open.
