# OPH Paper Index

This directory is the canonical publication surface for the main OPH papers. Each paper is kept as a TeX source beside its built PDF.

| Paper | Role |
| --- | --- |
| [Recovering Relativity and the Standard Model](recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf) ([source](recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.tex)) | Technical center: observer consensus to relativity, Einstein dynamics, gauge structure, and matter |
| [Observers Are All You Need](observers_are_all_you_need.pdf) ([source](observers_are_all_you_need.tex)) | Broad observer-first synthesis and main conceptual paper |
| [Reality as a Consensus Protocol](reality_as_consensus_protocol.pdf) ([source](reality_as_consensus_protocol.tex)) | Finite repair, protected records, and quotient normal forms |
| [Deriving the Particle Zoo](deriving_the_particle_zoo_from_observer_consistency.pdf) ([source](deriving_the_particle_zoo_from_observer_consistency.tex)) | Particle carriers, flavor structures, scale maps, and executable pipeline |
| [Federated Echosahedral Screen Microphysics](screen_microphysics_and_observer_synchronization.pdf) ([source](screen_microphysics_and_observer_synchronization.tex)) | Twelve-port screen, central records, and observer synchronization |
| [Paradise as Fixed-Point Consensus](paradise_as_fixed_point_consensus.pdf) ([source](paradise_as_fixed_point_consensus.tex)) | Observer continuation and interpretation |

The shortest informal introduction is [A Compact Case for OPH](../extra/compact_proof_of_oph.pdf). Focused papers are listed in the [supplement index](../extra/).

Shared TeX lives in [`tex_fragments/`](tex_fragments/). The [BFT/QECC appendix](appendix_B_bft_qecc_extensions.tex) is included by *Reality as a Consensus Protocol*.

## Reproducibility

The shared release identifier lives in [`release_info.tex`](release_info.tex). [`paper_release_manifest.json`](paper_release_manifest.json) records the release artifacts and hashes.

From the repository root:

```bash
python3 tools/build_tex_papers.py --release-only
python3 tools/generate_paper_release_manifest.py
```
