import ObservableNormalForms.Exact
import ObservableNormalForms.ObserverConfluence
import ObservableNormalForms.Stability
import ObservableNormalForms.Refinement
import ObservableNormalForms.Repair
import ObservableNormalForms.Functional
import ObservableNormalForms.Stochastic
import ObservableNormalForms.ConditionalResampling
import ObservableNormalForms.Scatter.Layout
import ObservableNormalForms.Scatter.Circuit
import ObservableNormalForms.Scatter.Canonical
import ObservableNormalForms.Scatter.Regression328
import ObservableNormalForms.Scatter.Controls
import ObservableNormalForms.Examples.Rule90

/-!
# Axiom audit

The build output of this module is the theorem-level axiom receipt for the
submission artifact.  None of the declarations below should report
`sorryAx`.
-/

open ObservableNormalForms

#print axioms observableDetermined_iff_unique_partialNormalizer
#print axioms reachable_normalForm_mem_fiber
#print axioms singleton_fiber_weakNormalization_confluent
#print axioms existsUnique_auditedTerminal
#print axioms ObservationLeakCounterexample.singleton_fiber_insufficient_without_observation_preservation
#print axioms boundaryIdentifiesModulo_iff_observerEndpointUniqueModulo
#print axioms exists_equivalent_observer_endpoints
#print axioms TwoBitRepair.observerEndpointUnique
#print axioms TwoBitRepair.coarse_confluent
#print axioms TwoBitRepair.coarse_observerEndpointUnique_fails
#print axioms heterogeneous_two_output_estimate
#print axioms approximate_schedule_independence
#print axioms one_step_approximate_naturality
#print axioms telescoping_refinement_bound
#print axioms same_level_implementation_agreement
#print axioms anchored_cross_level_metric_core
#print axioms nested_compatible_levels_metric_core
#print axioms two_implementations_bound_from_tower_receipts
#print axioms strongRepair_exists_iff_collarProjection_surjective
#print axioms empty_write_space_counterexample
#print axioms robust_no_repair_margin
#print axioms empty_relation_repairMargin_zero
#print axioms RankedSynchronousSystem.synchronous_depth_settling
#print axioms FiniteMarkovKernel.finite_markov_drift_iteration
#print axioms finite_markov_tail_bound
#print axioms FiniteWeightedObservation.resample_eq_self_iff_observationMeasurable
#print axioms FiniteWeightedObservation.resample_idempotent
#print axioms FiniteWeightedObservation.resample_weighted_self_adjoint
#print axioms FiniteWeightedObservation.resample_weighted_energy_identity
#print axioms FiniteWeightedObservation.resample_weighted_energy_le
#print axioms FiniteWeightedObservation.kernel_eq_conditionalResamplingKernel_iff_recognition
-- Issue #626: directional scatter-project compiler intertwiner
#print axioms Scatter.Layout.round_eq_synchronousStep
#print axioms Scatter.Layout.evolve_settles
#print axioms Scatter.Layout.round_solution
#print axioms Scatter.Layout.totalMismatch_eq_zero_iff
#print axioms Scatter.Layout.totalMismatch_solution
#print axioms Scatter.Layout.zeroMismatch_unique
#print axioms Scatter.Layout.noise_recovery
#print axioms Scatter.Layout.round_eq_canonical_outputOnly
#print axioms Scatter.Layout.outputOnlySelection_isAdmissible
#print axioms Scatter.Circuit.compile_intertwiner
#print axioms Scatter.Circuit.compile_solution_eq_eval
#print axioms Scatter.Circuit.compile_settles
#print axioms Scatter.Circuit.compile_settled_fixed
#print axioms Scatter.Circuit.compile_settled_mismatch
#print axioms Scatter.Circuit.compile_zeroMismatch_unique
#print axioms Scatter.Circuit.compile_regCount
#print axioms Scatter.Circuit.compile_patchCount
#print axioms Scatter.andChain_depthBound
#print axioms Scatter.andChain_gateCount
#print axioms Scatter.regression_settles
#print axioms Scatter.regression_reaches_target
#print axioms Scatter.regression_eval_target
#print axioms Scatter.regression_settled_fixed
#print axioms Scatter.regression_settled_mismatch
#print axioms Scatter.regression_unique_zero_mismatch
#print axioms Scatter.sel328_isAdmissible
#print axioms Scatter.canonical_orbit_even
#print axioms Scatter.canonical_orbit_odd
#print axioms Scatter.canonical_never_settles_328
#print axioms Scatter.canonical_scatter_project_not_settling_328
#print axioms Scatter.collide_no_cert
#print axioms Scatter.collide_order_dependent
#print axioms Scatter.latch_no_cert
#print axioms Scatter.latch_never_zero_mismatch
#print axioms Scatter.latch_no_fixed_point
#print axioms Scatter.selfLoop_no_cert
#print axioms Scatter.selfLoop_never_zero_mismatch
#print axioms Scatter.fanOut_depthBound
#print axioms Scatter.fanOut_settles
#print axioms Scatter.fanOut_settles_kernel
#print axioms Rule90.kernel_exact
#print axioms Rule90.image_exact
#print axioms Rule90.read01_injective_on_image
#print axioms Rule90.read02_not_injective_on_image
#print axioms Rule90.no_total_reverse_repair
