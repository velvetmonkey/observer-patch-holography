from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "programs"
    / "generative_repair_kernel.py"
)
SPEC = importlib.util.spec_from_file_location("generative_repair_kernel", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
kernel = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = kernel
SPEC.loader.exec_module(kernel)


def test_builtin_kernel_is_stochastic_stationary_and_detailed_balanced() -> None:
    for spectrum in kernel.builtin_spectra().values():
        target = kernel.target_distribution(spectrum, kernel.DEFAULT_BETA, kernel.OPH_KAPPA)
        transition = kernel.metropolis_hastings_kernel(
            spectrum,
            kernel.DEFAULT_BETA,
            kernel.OPH_KAPPA,
        )
        assert np.all(transition >= 0.0)
        assert np.allclose(transition.sum(axis=1), 1.0, atol=1e-12)
        assert kernel.stationary_residual(target, transition) < 1e-12
        assert kernel.detailed_balance_error(target, transition) < 1e-12
        recovered = kernel.stationary_distribution_from_kernel(transition)
        assert np.allclose(recovered, target, atol=1e-10)


def test_nonabelian_dimension_exponent_is_identifiable() -> None:
    spectra = kernel.builtin_spectra()
    for name in ("s3_primary", "a4_nonabelian_decoy", "random_seeded_decoy"):
        receipt = kernel.identifiability_certificate(spectra[name], kernel.DEFAULT_BETA)
        assert receipt["dimension_exponent_identifiable"] is True
        assert receipt["kl_rate_oph_vs_unweighted"] > 0.0
        assert receipt["kl_rate_oph_vs_plancherel"] > 0.0


def test_abelian_controls_are_exactly_nonidentifying_for_kappa() -> None:
    spectra = kernel.builtin_spectra()
    for name in ("z3_cyclic_control", "z5_cyclic_control"):
        spectrum = spectra[name]
        k0 = kernel.metropolis_hastings_kernel(spectrum, kernel.DEFAULT_BETA, 0.0)
        k1 = kernel.metropolis_hastings_kernel(spectrum, kernel.DEFAULT_BETA, 1.0)
        k2 = kernel.metropolis_hastings_kernel(spectrum, kernel.DEFAULT_BETA, 2.0)
        assert np.array_equal(k0, k1)
        assert np.array_equal(k1, k2)
        receipt = kernel.identifiability_certificate(spectrum, kernel.DEFAULT_BETA)
        assert receipt["dimension_exponent_identifiable"] is False
        assert receipt["kl_rate_oph_vs_unweighted"] == 0.0
        assert receipt["kl_rate_oph_vs_plancherel"] == 0.0


def test_label_permutation_is_equivariant() -> None:
    spectrum = kernel.builtin_spectra()["s3_primary"]
    permutation = [2, 0, 1]
    relabeled = kernel.permute_spectrum(spectrum, permutation)
    original_kernel = kernel.metropolis_hastings_kernel(
        spectrum,
        kernel.DEFAULT_BETA,
        kernel.OPH_KAPPA,
    )
    relabeled_kernel = kernel.metropolis_hastings_kernel(
        relabeled,
        kernel.DEFAULT_BETA,
        kernel.OPH_KAPPA,
    )
    expected = original_kernel[np.ix_(permutation, permutation)]
    assert np.allclose(relabeled_kernel, expected, atol=1e-12)


def test_simulated_nonabelian_receipt_recovers_oph_kappa() -> None:
    spectrum = kernel.builtin_spectra()["s3_primary"]
    true_kernel = kernel.metropolis_hastings_kernel(
        spectrum,
        kernel.DEFAULT_BETA,
        kernel.OPH_KAPPA,
    )
    counts = kernel.simulate_transition_counts(
        true_kernel,
        shots_per_source=16384,
        seed=509,
    )
    comparison = kernel.compare_kappa_hypotheses(spectrum, kernel.DEFAULT_BETA, counts)
    assert comparison["winner"] == "kappa_1"
    assert comparison["oph_log_bayes_factor_vs_best_equal_prior_null"] > math.log(100.0)


def test_simulated_abelian_receipt_cannot_claim_oph_identification() -> None:
    spectrum = kernel.builtin_spectra()["z3_cyclic_control"]
    true_kernel = kernel.metropolis_hastings_kernel(
        spectrum,
        kernel.DEFAULT_BETA,
        kernel.OPH_KAPPA,
    )
    counts = kernel.simulate_transition_counts(true_kernel, shots_per_source=2048, seed=510)
    comparison = kernel.compare_kappa_hypotheses(spectrum, kernel.DEFAULT_BETA, counts)
    assert comparison["oph_log_bayes_factor_vs_best_equal_prior_null"] == 0.0


def test_validation_bundle_hash_is_deterministic() -> None:
    first = kernel.build_validation_bundle(beta=0.6, shots_per_source=2048, seed=511)
    second = kernel.build_validation_bundle(beta=0.6, shots_per_source=2048, seed=511)
    assert first == second
    claimed_hash = first["bundle_sha256"]
    unhashed = dict(first)
    unhashed.pop("bundle_sha256")
    assert claimed_hash == kernel.sha256_json(unhashed)
