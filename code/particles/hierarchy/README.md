# OPH Hierarchy Proof Artifacts Bundle

Bundle ID: `oph-hierarchy-proof-artifacts-r1473-2026-06-12`

Generated: `2026-06-12T04:17:17Z`

This bundle packages the proof-obligation artifacts for the OPH electroweak hierarchy lane:

```math
P_\star \to \alpha_U(P_\star) \to
\frac{v}{E_\star} =
P_\star^{-1/2}\exp\left[-\frac{2\pi}{4\alpha_U(P_\star)}\right].
```

## What is included

- `certificates/R_P_public_pixel_certificate.json`
- `certificates/R_P_source_audit_pixel_certificate.json`
- `certificates/Pi_U_frozen_source_packet.json`
- `certificates/DAG_U.json`
- `certificates/R_U_interval_certificate.json`
- `certificates/R_U_krawczyk_certificate.json`
- `computations/hierarchy_numeric_witness.json`
- `computations/hierarchy_recompute.py`
- `certificates/R_HT_declared_surface_certificate.json`
- `certificates/RG_Higgs_naturality_defect_certificate.json`
- `certificates/R_WZ_boundary_certificate.json`
- `certificates/R_gamma_noG_DAG_certificate.json`
- `certificates/local_global_resonance_audit.json`
- `validators/validate_bundle.py`

## Closure status

Closed inside this bundle:

1. The declared D10 source packet ledger.
2. The declared `DAG_U` forbidden-path check.
3. The `R_U` interval/Krawczyk inclusion witness.
4. The public and source-audit hierarchy computations.
5. The claim-tier boundary artifacts for `W/Z`, `R_HT`, `R_gamma`, and the local/global resonance.

External/source gates outside this bundle:

1. Source-only public Thomson endpoint transport `A_T(P)`.
2. Formal outward-rounded interval log from a certified interval stack.
3. Raw D10/D11 interval box for Higgs/top internals.
4. Concrete RG/Higgs naturality defect bound `epsilon_H`.
5. Full `R_gamma` stack for SI gravity/clock hierarchy.
6. Theorem-grade `W/Z` promotion.
7. Local/global resonance lemmas.

## Run validators

From this directory:

```bash
python3 validators/validate_bundle.py
python3 computations/hierarchy_recompute.py
```
