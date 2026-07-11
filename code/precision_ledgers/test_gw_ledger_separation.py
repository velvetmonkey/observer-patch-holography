"""Pytest coverage for the Section 5.14 two-ledger verification (issue #537)."""

from gw_ledger_separation import (
    run_bridge_lemma,
    run_counterexample,
    run_dual_norm_check,
    run_suite,
)


def test_trace_distance_does_not_bound_dispersion():
    """Ledger separation: zero trace distance, nonzero fractional speed error."""
    result = run_counterexample(seed=7, gamma=0.05)
    assert result["max_trace_distance"] < 1e-10
    assert result["max_bounded_observable_gap"] < 1e-10
    assert abs(result["fractional_speed_error"] - 0.05) < 1e-6


def test_bridge_lemma_bounds_hold():
    """Davis--Kahan projector, L_B = 1 + 4 M_B speed, and group-delay bounds."""
    for seed in (1, 2, 3, 4):
        for strength in (0.002, 0.01, 0.05):
            case = run_bridge_lemma(seed=seed, strength=strength)
            assert case["eta_below_quarter"], case
            assert case["projector_ok"], case
            assert case["speed_ok"], case
            assert case["group_delay_ok"], case


def test_bridge_lemma_bound_is_not_vacuous():
    """The certified speed bound scales down with the perturbation strength."""
    weak = run_bridge_lemma(seed=1, strength=0.002)
    strong = run_bridge_lemma(seed=1, strength=0.05)
    assert weak["speed_bound"] < strong["speed_bound"]
    assert weak["speed_error"] <= weak["speed_bound"]
    assert weak["speed_bound"] < 0.25 * strong["speed_bound"]


def test_dual_norm_inequality():
    result = run_dual_norm_check(seed=11, trials=100)
    assert result["dual_norm_ok"]


def test_suite_receipt_asserts_all_gates():
    receipt = run_suite()
    assert receipt["counterexample_separates_ledgers"]
    assert receipt["bridge_lemma_all_ok"]
    assert receipt["dual_norm"]["dual_norm_ok"]
