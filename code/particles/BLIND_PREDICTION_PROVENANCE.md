# Blind Prediction Provenance

Generated: `2026-06-17T03:22:30Z`

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
| `w_boson` | `80.377 GeV` | `compare_only_reproduction` | `not_blind` | target_used_as_frozen_reference | `False` | inherits_declared_electroweak_surface |
| `z_boson` | `91.18797809193725 GeV` | `compare_only_reproduction` | `not_blind` | target_used_as_frozen_reference | `False` | inherits_declared_electroweak_surface |
| `higgs` | `125.1995304097179 GeV` | `source_only_declared_surface_theorem` | `conditionally_blind_on_declared_surface` | no_direct_row_target_input_recorded_in_the_forward_split_readout | `True` | depends_on_declared_D10_D11_running_matching_threshold_surface |
| `electron` | `0.0005109989499999994 GeV` | `target_anchored_witness` | `not_blind` | target_values_used_to_anchor_current_family_witness | `False` | not_promotable_until_source_attachment_closes |
| `muon` | `0.10565837550000004 GeV` | `target_anchored_witness` | `not_blind` | target_values_used_to_anchor_current_family_witness | `False` | not_promotable_until_source_attachment_closes |
| `tau` | `1.7769324651340912 GeV` | `target_anchored_witness` | `not_blind` | target_values_used_to_anchor_current_family_witness | `False` | not_promotable_until_source_attachment_closes |
| `up_quark` | `0.0021600000000000005 GeV` | `selected_class_exact_theorem` | `selected_class_not_global_blind` | reference_codomain_matched_after_selected_class_theorem | `True` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `charm_quark` | `1.2729999999999992 GeV` | `selected_class_exact_theorem` | `selected_class_not_global_blind` | reference_codomain_matched_after_selected_class_theorem | `True` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `top_quark` | `172.35235532883115 GeV` | `selected_class_exact_theorem` | `selected_class_not_global_blind` | reference_codomain_matched_after_selected_class_theorem | `True` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `down_quark` | `0.004699999999999999 GeV` | `selected_class_exact_theorem` | `selected_class_not_global_blind` | reference_codomain_matched_after_selected_class_theorem | `True` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `strange_quark` | `0.09349999999999999 GeV` | `selected_class_exact_theorem` | `selected_class_not_global_blind` | reference_codomain_matched_after_selected_class_theorem | `True` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `bottom_quark` | `4.182999999999994 GeV` | `selected_class_exact_theorem` | `selected_class_not_global_blind` | reference_codomain_matched_after_selected_class_theorem | `True` | quark_scheme_and_frame_class_scope_must_remain_visible |
| `electron_neutrino` | `0.017454720257976796 eV` | `theorem_branch_no_direct_mass_target` | `blind_absolute_mass_branch` | no_absolute_mass_target_input | `True` | pmns_comparison_tension_reported_separately |
| `muon_neutrino` | `0.019481987935919015 eV` | `theorem_branch_no_direct_mass_target` | `blind_absolute_mass_branch` | no_absolute_mass_target_input | `True` | pmns_comparison_tension_reported_separately |
| `tau_neutrino` | `0.05307522145074924 eV` | `theorem_branch_no_direct_mass_target` | `blind_absolute_mass_branch` | no_absolute_mass_target_input | `True` | pmns_comparison_tension_reported_separately |

## Preregistered Workflows

- `new_quantity_pre_reference_lock`: `protocol_emitted_unexercised`. For any quantitative row outside construction inputs, freeze the source artifacts, hash the runtime bundle, record allowed conventions, then fetch or reveal the external reference. Required evidence: `source_artifact_hashes`, `forbidden_target_inputs`, `convention_set`, `pre_reference_runtime_output`, `post_reference_comparison_only_delta`.
- `convention_sensitivity_sweep`: `declared_taxonomy_emitted_numeric_sweep_stage_gated`. Vary only declared scheme, matching, and threshold choices inside certified intervals; report induced intervals for every public quantitative row. Required evidence: `scheme_lock`, `threshold_map`, `matching_interval_composition_certificate`, `rowwise_sensitivity_intervals`.

## Convention Sensitivity

- Status: `declared_taxonomy_emitted_numeric_sweep_stage_gated`
- RG contract status: `closed_declared_convention_contract_not_rg_matching_theorem`
- Endpoint contract status: `closed_blocker_isolated_not_endpoint_theorem`
- Endpoint package status: `endpoint_package_computed_blocker_isolated`
- Next artifact: interval composition certificates after the populated source spectral measure payload exists
