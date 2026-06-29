# Blind Prediction Provenance

Generated: `2026-06-29T06:58:53Z`

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
| `electron` | `0.0005109989499999994 GeV` | `target_anchored_witness` | `not_blind` | target_values_used_to_anchor_current_family_witness | `False` | not_promotable_until_source_attachment_closes |
| `muon` | `0.10565837550000004 GeV` | `target_anchored_witness` | `not_blind` | target_values_used_to_anchor_current_family_witness | `False` | not_promotable_until_source_attachment_closes |
| `tau` | `1.7769324651340912 GeV` | `target_anchored_witness` | `not_blind` | target_values_used_to_anchor_current_family_witness | `False` | not_promotable_until_source_attachment_closes |
| `up_quark` | `0.0021600000000000005 GeV` | `selected_class_target_anchored_witness` | `selected_class_target_anchored_not_blind` | target_derived_sigma_datum_used_for_selected_class_exact_witness | `False` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `charm_quark` | `1.2729999999999992 GeV` | `selected_class_target_anchored_witness` | `selected_class_target_anchored_not_blind` | target_derived_sigma_datum_used_for_selected_class_exact_witness | `False` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `top_quark` | `172.35235532883115 GeV` | `selected_class_target_anchored_witness` | `selected_class_target_anchored_not_blind` | target_derived_sigma_datum_used_for_selected_class_exact_witness | `False` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `down_quark` | `0.004699999999999999 GeV` | `selected_class_target_anchored_witness` | `selected_class_target_anchored_not_blind` | target_derived_sigma_datum_used_for_selected_class_exact_witness | `False` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `strange_quark` | `0.09349999999999999 GeV` | `selected_class_target_anchored_witness` | `selected_class_target_anchored_not_blind` | target_derived_sigma_datum_used_for_selected_class_exact_witness | `False` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `bottom_quark` | `4.182999999999994 GeV` | `selected_class_target_anchored_witness` | `selected_class_target_anchored_not_blind` | target_derived_sigma_datum_used_for_selected_class_exact_witness | `False` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `electron_neutrino` | `0.017454720257976796 eV` | `scale_free_theorem_with_compare_only_absolute_attachment_candidate` | `scale_free_blind_absolute_scale_not_promoted` | compare_only_C_nu_used_for_absolute_attachment_candidate | `False` | pmns_comparison_tension_reported_separately |
| `muon_neutrino` | `0.019481987935919015 eV` | `scale_free_theorem_with_compare_only_absolute_attachment_candidate` | `scale_free_blind_absolute_scale_not_promoted` | compare_only_C_nu_used_for_absolute_attachment_candidate | `False` | pmns_comparison_tension_reported_separately |
| `tau_neutrino` | `0.05307522145074924 eV` | `scale_free_theorem_with_compare_only_absolute_attachment_candidate` | `scale_free_blind_absolute_scale_not_promoted` | compare_only_C_nu_used_for_absolute_attachment_candidate | `False` | pmns_comparison_tension_reported_separately |

## Preregistered Workflows

- `new_quantity_pre_reference_lock`: `protocol_emitted_unexercised`. For any quantitative row outside construction inputs, freeze the source artifacts, hash the runtime bundle, record allowed conventions, then fetch or reveal the external reference. Required evidence: `source_artifact_hashes`, `forbidden_target_inputs`, `convention_set`, `pre_reference_runtime_output`, `post_reference_comparison_only_delta`.
- `convention_sensitivity_sweep`: `declared_taxonomy_emitted_numeric_sweep_stage_gated`. Vary only declared scheme, matching, and threshold choices inside certified intervals; report induced intervals for every public quantitative row. Required evidence: `scheme_lock`, `threshold_map`, `matching_interval_composition_certificate`, `rowwise_sensitivity_intervals`.

## Convention Sensitivity

- Status: `declared_taxonomy_emitted_numeric_sweep_stage_gated`
- RG contract status: `closed_declared_convention_contract_not_rg_matching_theorem`
- Endpoint contract status: `closed_blocker_isolated_not_endpoint_theorem`
- Endpoint package status: `endpoint_package_computed_blocker_isolated`
- Next artifact: interval composition certificates after the populated source spectral measure payload exists
