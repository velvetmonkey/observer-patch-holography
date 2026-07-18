# Observer Patch Holography

> Reality is the stable public world reconstructed by finite, self-reading observers that compare their overlaps and repair disagreement.

[Read in French](README_FR.md) · [OPH website](https://floatingpragma.io/oph/) · [Book](https://oph-book.floatingpragma.io/) · [Guided study](https://learn.floatingpragma.io/) · [Simulation](https://simulation.floatingpragma.io/) · [OMEGA](https://omega.floatingpragma.io/)

Observer Patch Holography (OPH) is an observer-first reconstruction program for fundamental physics. It begins with finite patches carrying local state, boundaries, records, readback, and repair moves. A public fact is one that survives when overlapping patches compare what they can see and settle into a common normal form.

The organizing equation is simple:

$$
T(\mathfrak U_{\mathrm{OPH}})=\mathfrak U_{\mathrm{OPH}}.
$$

The universe is modeled as a fixed point of its own observer-accessible readback and repair process.

## Why OPH Is Interesting

OPH uses one mathematical architecture across subjects that are normally introduced separately:

- finite consensus gives stable public records and quotient normal forms;
- central record algebras give quantum event probabilities and conditional update;
- the conformal geometry of an observer screen gives the connected Lorentz group and a three-dimensional observer-frame space;
- modular flow, null transport, entropy stationarity, and small-ball geometry compose into the Einstein relation on the recovered branch;
- transportable charges and compact reconstruction give the Standard Model gauge structure;
- a finite twelve-port $A_5$ construction produces the Lie algebra
  $\mathfrak u(1)\oplus\mathfrak{su}(2)\oplus\mathfrak{su}(3)$;
- trace balance integrates this algebra to
  $S(U(3)\times U(2))\cong(SU(3)\times SU(2)\times U(1))/\mathbb Z_6$;
- the Minimal Admissible Realization branch selects the Standard Model charge lattice, three colors, three generations, and one Higgs doublet;
- public Lean, exact-arithmetic certificates, simulations, and executable receipts check the finite mathematical core.

The significance is the convergence. OPH does not introduce a separate mechanism for measurement, spacetime, gravity, and gauge structure. It asks how much of all four follows from the same requirement: finite observers must be able to form one stable public world.

## The Strongest Finite Result

On the declared twelve-port icosahedral branch, the permutation module splits as

$$
P_{12}\cong_{A_5}\mathbf1\oplus\mathbf3\oplus\mathbf3'\oplus\mathbf5.
$$

An explicit equivariant pullback of the block commutator then constructs

$$
(P_{12},[\ ,\ ]_\Theta)
\cong
\mathfrak u(1)\oplus\mathfrak{su}(3)\oplus\mathfrak{su}(2).
$$

This is the local Lie algebra of the Standard Model gauge forces. It is obtained from the finite coefficient geometry rather than inserted as the starting symmetry.

The same construction gives two independent appearances of the number $24$:

$$
m_{\mathrm{rep}}=2(8+3+1)=24,
$$

while the twelve screen ports have $24$ oriented slots. One count comes from the recovered gauge algebra; the other comes from the screen geometry.

## One Reconstruction Chain

```text
self-reading patches
        ↓
records, overlap comparison, repair
        ↓
public quotient normal forms
        ↓
screen conformal geometry and modular flow
        ↓
Lorentz kinematics, observer time, Einstein dynamics
        ↓
transportable charges and compact reconstruction
        ↓
SU(3) × SU(2) × U(1) / Z6 and Standard Model matter
        ↓
quantitative fixed-point and physical-readout programs
```

The detailed hypotheses and receipt types are stated in the papers. The repository front page is intentionally a map of the positive result, not a substitute for those theorem statements.

## Results At A Glance

| Result | What OPH contributes | Main source |
| --- | --- | --- |
| Finite observer consensus | Terminating repair, protected readout, schedule-independent quotient normal forms, and central records | [Reality as a Consensus Protocol](paper/reality_as_consensus_protocol.pdf) |
| Quantum event surface | Born probabilities, Lüders conditioning, and the Tsirelson bound on the finite central record surface | [Observers Are All You Need](paper/observers_are_all_you_need.pdf) |
| Relativity | $\mathrm{Conf}^+(S^2)\cong\mathrm{SO}^+(3,1)$ and $H^3\cong\mathrm{SO}^+(3,1)/\mathrm{SO}(3)$ | [Compact recovery paper](paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf) |
| Einstein dynamics | A typed chain from modular/null transport and entropy stationarity to $G_{ab}+\Lambda g_{ab}=8\pi G\langle T_{ab}\rangle$ | [Compact recovery paper](paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf) |
| Finite $A_5$ gauge algebra | Exact twelve-port construction of $\mathfrak u(1)\oplus\mathfrak{su}(2)\oplus\mathfrak{su}(3)$ | [Compact recovery paper](paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf) |
| Standard Model global form | $S(U(3)\times U(2))$ and the shared-center $\mathbb Z_6$ quotient | [Compact recovery paper](paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf) |
| Matter structure | Hypercharge lattice, three colors, three generations, and one Higgs doublet on the realized MAR branch | [Compact recovery paper](paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf) |
| Exact verification | Lean theorem subset, interval certificates, finite receipts, and reproducible simulations | [`Lean/`](Lean) and [`code/`](code) |

## How To Read The Project

For the shortest route through the theory:

1. Read [the compact case for OPH](extra/compact_proof_of_oph.pdf) for the informal argument and the main results.
2. Read [the compact recovery paper](paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf) for the theorem-level relativity, gravity, gauge, and matter construction.
3. Read [Observers Are All You Need](paper/observers_are_all_you_need.pdf) for the broad synthesis.
4. Inspect [`Lean/`](Lean), [`code/`](code), and the [closure ledger](docs/CLOSURE_LEDGER.md) for executable evidence and provenance.

## Core Papers

- **[Recovering Relativity and Standard Model Structure from Observer Overlap Consistency](paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf)** is the technical center of the repository. It composes the recovered spacetime, Einstein, compact-gauge, Standard Model matter, and finite $A_5$ results.
- **[Observers Are All You Need](paper/observers_are_all_you_need.pdf)** presents the full observer-first program, from records and measurement to geometry, particles, and observer continuation.
- **[Deriving the Particle Zoo from Observer Consistency](paper/deriving_the_particle_zoo_from_observer_consistency.pdf)** develops the particle carriers, flavor structures, scale maps, and executable particle pipeline.
- **[Reality as a Consensus Protocol](paper/reality_as_consensus_protocol.pdf)** develops the finite patch-net mechanics: overlap comparison, repair, protected observations, and normal forms.
- **[Federated Echosahedral Screen Microphysics](paper/screen_microphysics_and_observer_synchronization.pdf)** develops the twelve-port finite screen, $A_5$ carrier, central records, and synchronization architecture.
- **[Paradise as Fixed-Point Consensus](paper/paradise_as_fixed_point_consensus.pdf)** explores the observer-continuation and metaphysical interpretation of the same fixed-point architecture.

## Compact Mathematical Spine

The OPH construction can be read as four layers.

### 1. Observer consensus

A patch has accessible state, ports, records, and repair moves. Compatible patches exchange only overlap-visible information. Under the finite termination and diamond conditions, repair produces a shared quotient normal form. That is the mathematical core of public reality in OPH.

### 2. Geometry and gravity

The oriented conformal two-sphere supplies the connected Lorentz group. Its observer-frame homogeneous space has dimension three. Modular flow supplies the relative clock, null translations supply directional transport, and generalized-entropy stationarity supplies the local gravitational relation.

### 3. Gauge structure and matter

Transportable internal charges form a tensor category. Compact reconstruction reads off the gauge group. Minimal admissible realization, anomaly cancellation, Yukawa invariance, and the shared central kernel select the Standard Model matter package. The independent $A_5$ coefficient construction reaches the same local gauge algebra from finite screen geometry.

### 4. Fixed points and physical readout

The quantitative program studies self-consistent coordinates such as the local pixel $P_\star$, record capacity $N_{\mathrm{CRC}}$, and scale ratio $\gamma_\star$. Exact map roots, source provenance, transport, and physical comparison are kept in machine-readable ledgers so the structural theory and its quantitative continuations remain auditable.

## Proof And Evidence

The repository contains several complementary forms of evidence:

- hand proofs in the TeX papers;
- a sorry-free 111-theorem Lean subset covering finite observer consensus and related algebraic results;
- interval and uniqueness certificates for declared numerical maps;
- finite carrier and hierarchy receipts;
- particle, geometry, dark-sector, and quantum-hardware code;
- simulations reaching more than one million patches;
- a claim registry and closure ledger connecting prose claims to artifacts.

The broader Lean development contains three explicitly isolated asynchronous-repair signatures outside the 111-theorem subset. They do not enter the advertised machine-checked count.

## Research Frontier

OPH’s structural core now supports several active continuations:

- quantitative particle readout and flavor transport;
- neutrino susceptibility and mixing geometry;
- record-capacity cosmology;
- dark gravity as a repair-charge condensate with dust-like and deep-galaxy regimes;
- finite Yang–Mills transfer and repair-gap constructions;
- observer-like hardware and software systems with local state, boundaries, readback, records, and repair.

These programs share the same design principle as the core theory: every proposed physical system must be represented as a bounded, self-reading patch with a public evidence bundle.

The [OPH Falsification Program](docs/OPH_FALSIFICATION_PROGRAM.md) is deliberately limited to mature mathematical and realized-branch claims. It is a verification index, not the organizing narrative of the repository.

## Dependency Map

<p align="center">
  <a href="assets/prediction-chain.svg" target="_blank" rel="noopener noreferrer">
    <img src="assets/prediction-chain.svg" alt="OPH reconstruction chain" width="92%">
  </a>
</p>

<p align="center"><sub>The OPH line from observer consistency to public records, spacetime, gravity, gauge structure, matter, and quantitative readout.</sub></p>

## Repository Guide

- [`paper/`](paper): core papers, TeX sources, PDFs, and release metadata.
- [`extra/`](extra): compact proof and focused mathematical supplements.
- [`Lean/`](Lean): machine-checked theorem development.
- [`code/`](code): certificates, simulations, particle calculations, and experiments.
- [`book/`](book): the book source and downloadable PDF.
- [`cosmology/`](cosmology): dark-sector and cosmology research.
- [`docs/`](docs): closure ledger, claim policy, and technical audit material.
- [`assets/`](assets): diagrams and public figures.

## Explore OPH

- [Theory explainer](https://floatingpragma.io/oph/theory-of-everything)
- [Interactive simulation](https://simulation.floatingpragma.io)
- [OMEGA applications and hardware](https://omega.floatingpragma.io)
- [Book](https://oph-book.floatingpragma.io)
- [Guided study](https://learn.floatingpragma.io)
- [Blog](https://blog.floatingpragma.io/)
- OPH Sage on [Telegram](https://t.me/HoloObserverBot) and [X](https://x.com/OphSage)

## License

The authored material is licensed under [CC BY-NC-SA 4.0](LICENSE). The repository-wide [OPH Open Use and Anti-Patent Covenant](PATENTS.md) keeps OPH-derived ideas, software, methods, devices, simulations, and hardware open to study, implementation, modification, and sharing without private patent monopolies.
