# Artifact Status Ledger

| Artifact | Status | Meaning |
|---|---|---|
| `R_P_public_pixel_certificate.json` | conditional public endpoint | Public endpoint branch recorded; source-only endpoint transport required for a no-measured-Thomson claim. |
| `R_P_source_audit_pixel_certificate.json` | source-audit witness | Avoids upstream measured Thomson endpoint; does not close public endpoint without same-scheme hadronic transport. |
| `Pi_U_frozen_source_packet.json` | supplied | Records frozen D10 packet. |
| `DAG_U.json` | supplied / passes declared graph check | Excludes forbidden measured-data paths on the declared graph. |
| `R_U_interval_certificate.json` | supplied witness | Endpoint signs and derivative interval enclosure are included. |
| `R_U_krawczyk_certificate.json` | supplied witness | Krawczyk image lies inside `I_U` under the derivative interval. |
| `hierarchy_numeric_witness.json` | supplied | Public and source-audit branch computations. |
| `R_HT_declared_surface_certificate.json` | partial | Formula/output ledger supplied; raw interval input box missing. |
| `RG_Higgs_naturality_defect_certificate.json` | formal condition only | Defines `epsilon_H`; concrete defect bound missing. |
| `R_WZ_boundary_certificate.json` | compare-only | Prevents accidental promotion of `W/Z`. |
| `R_gamma_noG_DAG_certificate.json` | skeleton only | No-G rule and missing components are explicit. |
| `local_global_resonance_audit.json` | not used | Computes mismatch for rounded `N_CRC` and lists missing lemmas. |
