# Blind Prediction Provenance

Generated: `2026-06-29T07:33:23Z`

This ledger records target-use and convention-sensitivity status for the public quantitative particle rows.

## Closure Gate

- Status: `closed_provenance_ledger_and_declared_sensitivity_taxonomy`
- Closable: `True`
- Reason: The row provenance ledger, blind workflow protocol, and declared convention-sensitivity taxonomy are emitted. Numeric sensitivity intervals remain tied to the populated source spectral measure payload and interval certificate.

## Rows

| Particle | Value | Class | Blind status | Target use | Promotable | Convention sensitivity |
| --- | ---: | --- | --- | --- | --- | --- |
| `photon` | `0.0 GeV` | `structural_blind_zero` | `blind_structural` | no_mass_target_used | `True` | none_for_mass_zero |
| `gluon` | `0.0 GeV` | `structural_blind_zero` | `blind_structural` | no_mass_target_used | `True` | none_for_mass_zero |
| `graviton` | `0.0 GeV` | `structural_blind_zero` | `blind_structural` | no_mass_target_used | `True` | none_for_mass_zero |
| `higgs` | `125.1995304097179 GeV` | `conditional_declared_surface_candidate` | `conditionally_blind_on_declared_surface` | candidate_upstream_d10_repair_not_source_promoted | `False` | depends_on_declared_D10_D11_running_matching_threshold_surface |

## Withheld Non-Prediction Rows

These rows have audit artifacts but no public prediction value in the output tables.

| Particle | Claim label | Blind status | Target use | Reason |
| --- | --- | --- | --- | --- |
| `electron` | `exact_target_anchored_current_family_witness` | `withheld_not_blind` | target_values_or_target_derived_datum_used | target_anchored_witness_kept_in_exact_fit_audit_not_public_prediction |
| `muon` | `exact_target_anchored_current_family_witness` | `withheld_not_blind` | target_values_or_target_derived_datum_used | target_anchored_witness_kept_in_exact_fit_audit_not_public_prediction |
| `tau` | `exact_target_anchored_current_family_witness` | `withheld_not_blind` | target_values_or_target_derived_datum_used | target_anchored_witness_kept_in_exact_fit_audit_not_public_prediction |
| `up_quark` | `selected_class_target_anchored_exact_witness` | `withheld_not_blind` | target_values_or_target_derived_datum_used | target_anchored_witness_kept_in_exact_fit_audit_not_public_prediction |
| `charm_quark` | `selected_class_target_anchored_exact_witness` | `withheld_not_blind` | target_values_or_target_derived_datum_used | target_anchored_witness_kept_in_exact_fit_audit_not_public_prediction |
| `top_quark` | `selected_class_target_anchored_exact_witness` | `withheld_not_blind` | target_values_or_target_derived_datum_used | target_anchored_witness_kept_in_exact_fit_audit_not_public_prediction |
| `down_quark` | `selected_class_target_anchored_exact_witness` | `withheld_not_blind` | target_values_or_target_derived_datum_used | target_anchored_witness_kept_in_exact_fit_audit_not_public_prediction |
| `strange_quark` | `selected_class_target_anchored_exact_witness` | `withheld_not_blind` | target_values_or_target_derived_datum_used | target_anchored_witness_kept_in_exact_fit_audit_not_public_prediction |
| `bottom_quark` | `selected_class_target_anchored_exact_witness` | `withheld_not_blind` | target_values_or_target_derived_datum_used | target_anchored_witness_kept_in_exact_fit_audit_not_public_prediction |
| `electron_neutrino` | `scale_free_weighted_cycle_theorem_with_compare_only_absolute_attachment_candidate` | `withheld_compare_only` | compare_only_reference_or_absolute_attachment_used | compare_only_absolute_or_adapter_surface_kept_out_of_public_prediction_table |
| `muon_neutrino` | `scale_free_weighted_cycle_theorem_with_compare_only_absolute_attachment_candidate` | `withheld_compare_only` | compare_only_reference_or_absolute_attachment_used | compare_only_absolute_or_adapter_surface_kept_out_of_public_prediction_table |
| `tau_neutrino` | `scale_free_weighted_cycle_theorem_with_compare_only_absolute_attachment_candidate` | `withheld_compare_only` | compare_only_reference_or_absolute_attachment_used | compare_only_absolute_or_adapter_surface_kept_out_of_public_prediction_table |

## Preregistered Workflows

- `new_quantity_pre_reference_lock`: `protocol_emitted_unexercised`. For any quantitative row outside construction inputs, freeze the source artifacts, hash the runtime bundle, record allowed conventions, then fetch or reveal the external reference. Required evidence: `source_artifact_hashes`, `forbidden_target_inputs`, `convention_set`, `pre_reference_runtime_output`, `post_reference_comparison_only_delta`.
- `convention_sensitivity_sweep`: `declared_taxonomy_emitted_numeric_sweep_stage_gated`. Vary only declared scheme, matching, and threshold choices inside certified intervals; report induced intervals for every public quantitative row. Required evidence: `scheme_lock`, `threshold_map`, `matching_interval_composition_certificate`, `rowwise_sensitivity_intervals`.

## Convention Sensitivity

- Status: `declared_taxonomy_emitted_numeric_sweep_stage_gated`
- RG contract status: `closed_declared_convention_contract_not_rg_matching_theorem`
- Endpoint contract status: `closed_blocker_isolated_not_endpoint_theorem`
- Endpoint package status: `endpoint_package_computed_blocker_isolated`
- Next artifact: interval composition certificates after the populated source spectral measure payload exists
