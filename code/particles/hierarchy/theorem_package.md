# Publication-Grade Theorem Package

## Theorem A — Conditional OPH electroweak hierarchy

Assume:

1. `R_P`: pixel closure branch, either public endpoint or source-audit branch with status label.
2. `Pi_U`: frozen D10 source packet.
3. `DAG_U`: no forbidden measurement path into `Phi_U`, `alpha_U`, or `v/E_star`.
4. `R_U#`: interval/Krawczyk proof record.

Then the source-side weak hierarchy is:

```math
\frac{v}{E_\star}
=
P_\star^{-1/2}
\exp\left[-\frac{2\pi}{4\alpha_U(P_\star)}\right].
```

On the public endpoint branch:

```math
v/E_\star = 2.0199803239725553\times10^{-17}.
```

On the source-audit branch:

```math
v(P_{cand})/E_\star = 2.0198114150099223\times10^{-17}.
```

## Theorem B — Higgs D10/D11 declared surface

Assume the D10/D11 input interval box `I_HT`, interval extension `F_HT#`, D11 Jacobian interval map, and `DAG_HT`.

Then:

```math
m_H=125.1995304097179\,\mathrm{GeV},\qquad
m_t^{D11}=172.3523553288312\,\mathrm{GeV}.
```

This bundle records the formula/output surface but does not include the raw interval input box.

## Corollary — OPH Higgs naturalness

If the RG/coarse-graining Higgs readout defect

```math
\epsilon_H =
\sup_x |H_r(\rho_{sr}n_s(x))-H_r(n_r\rho_{sr}(x))|
```

is zero, or interval-bounded within the declared Higgs output interval, then the bare/counterterm split is a regulator-coordinate split, not an observer-facing fine-tuning datum.

This bundle defines the defect but does not prove its numerical bound.

## Boundary theorem — SI gravity/clock hierarchy

The electroweak hierarchy theorem supplies `R_U`, not the full clock bridge. SI gravity requires:

```math
R_\gamma =
R_U + R_\alpha + R_e^{abs} + R_{QCD/nuc}^{133Cs} + R_{atom}^{133Cs}.
```

Only after those components are source-side and no-G DAG-certified may one use:

```math
G_{SI} =
\frac{c^5}{4\pi^2\hbar\nu_{Cs}^2}\epsilon_{Cs}^2.
```
