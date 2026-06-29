# Exact Non-Hadron Masses

Generated: `2026-06-29T06:58:53Z`

This bundle gives exact mass outputs for public non-hadron particle rows on declared OPH surfaces.
It records exact-output surfaces rather than one uniform theorem tier and excludes compare-only frozen-target adapters.
For quarks, the exact carrier-restricted witness surface matches the official PDG 2025 API running-quark target surface on `current_family_only`.
The same sextet is also realized on the restricted current-family common-refinement transport-frame carrier, which emits explicit exact forward Yukawas `Y_u` and `Y_d` on that declared carrier.
For charged leptons, this bundle records the exact same-family witness surface. The theorem surface also contains the live same-label `q_e` readback, a source-side determinant character for a fixed formal source multiplicity vector, a conditional determinant-line lift, and an algebraic charged-mass readout once theorem-grade `A_ch(P)` is given. Issue #201 is closed as a corpus-limited no-go: the available corpus does not attach that source-side character to the physical charged determinant line.
The top coordinate uses the PDG 2025 cross-section mass entry `Q007TP4`. The auxiliary direct-top entry `Q007TP` is compare-only; [#207](https://github.com/FloatingPragma/observer-patch-holography/issues/207) is closed as a corpus-limited no-go by `code/particles/runs/calibration/direct_top_bridge_contract.json`.

| Particle | Exact Mass | Kind | Scope | Source |
| --- | ---: | --- | --- | --- |
| Photon | `0.0 GeV` | `structural_zero` | `structural` | `structural_gauge_redundancy_surface` |
| Gluon | `0.0 GeV` | `structural_zero` | `structural` | `structural_color_gauge_surface` |
| Graviton | `0.0 GeV` | `structural_zero` | `structural` | `structural_diffeomorphism_redundancy_surface` |
| Higgs Boson | `125.1995304097179 GeV` | `conditional_declared_surface_higgs_top_candidate` | `declared_d10_d11_running_matching_threshold_surface_only` | `code/particles/runs/calibration/d11_live_exact_split_pair_theorem.json` |
| Electron | `0.0005109989499999994 GeV` | `exact_target_anchored_current_family_witness` | `current_family_only` | `code/particles/runs/leptons/lepton_current_family_exact_readout.json` |
| Muon | `0.10565837550000004 GeV` | `exact_target_anchored_current_family_witness` | `current_family_only` | `code/particles/runs/leptons/lepton_current_family_exact_readout.json` |
| Tau | `1.7769324651340912 GeV` | `exact_target_anchored_current_family_witness` | `current_family_only` | `code/particles/runs/leptons/lepton_current_family_exact_readout.json` |
| Up Quark | `0.0021600000000000005 GeV` | `selected_class_target_anchored_exact_witness` | `selected_public_physical_quark_frame_class_only_but_sigma_datum_target_derived` | `code/particles/runs/flavor/quark_public_exact_yukawa_end_to_end_theorem.json` |
| Charm Quark | `1.2729999999999992 GeV` | `selected_class_target_anchored_exact_witness` | `selected_public_physical_quark_frame_class_only_but_sigma_datum_target_derived` | `code/particles/runs/flavor/quark_public_exact_yukawa_end_to_end_theorem.json` |
| Top Quark | `172.35235532883115 GeV` | `selected_class_target_anchored_exact_witness` | `selected_public_physical_quark_frame_class_only_but_sigma_datum_target_derived` | `code/particles/runs/flavor/quark_public_exact_yukawa_end_to_end_theorem.json` |
| Down Quark | `0.004699999999999999 GeV` | `selected_class_target_anchored_exact_witness` | `selected_public_physical_quark_frame_class_only_but_sigma_datum_target_derived` | `code/particles/runs/flavor/quark_public_exact_yukawa_end_to_end_theorem.json` |
| Strange Quark | `0.09349999999999999 GeV` | `selected_class_target_anchored_exact_witness` | `selected_public_physical_quark_frame_class_only_but_sigma_datum_target_derived` | `code/particles/runs/flavor/quark_public_exact_yukawa_end_to_end_theorem.json` |
| Bottom Quark | `4.182999999999994 GeV` | `selected_class_target_anchored_exact_witness` | `selected_public_physical_quark_frame_class_only_but_sigma_datum_target_derived` | `code/particles/runs/flavor/quark_public_exact_yukawa_end_to_end_theorem.json` |
| Electron Neutrino | `0.017454720257976796 eV` | `scale_free_weighted_cycle_theorem_with_compare_only_absolute_attachment_candidate` | `weighted_cycle_bridge_rigid_absolute_family` | `code/particles/runs/neutrino/neutrino_absolute_attachment_theorem.json` |
| Muon Neutrino | `0.019481987935919015 eV` | `scale_free_weighted_cycle_theorem_with_compare_only_absolute_attachment_candidate` | `weighted_cycle_bridge_rigid_absolute_family` | `code/particles/runs/neutrino/neutrino_absolute_attachment_theorem.json` |
| Tau Neutrino | `0.05307522145074924 eV` | `scale_free_weighted_cycle_theorem_with_compare_only_absolute_attachment_candidate` | `weighted_cycle_bridge_rigid_absolute_family` | `code/particles/runs/neutrino/neutrino_absolute_attachment_theorem.json` |
