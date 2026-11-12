"""Count the simple rational phases whose circulant muon/electron ratio lies as close to the measured ratio as 2/9.

The circulant and the assignment are the ones of model/lepton_register_round: square-root masses are
proportional to 1 + sqrt2 cos(theta + 2 pi k/3), with electron, muon and tau on the characters k = 1, 2, 0.
The candidate family is every reduced fraction p/q with 1 <= q <= Q and 0 < p/q < pi/12, the positive chamber.
A candidate passes when its relative deviation from the CODATA 2022 ratio is at most the deviation of 2/9.
The control measures how much freedom the choice of a simple rational phase leaves. It does not test the
register construction or any physical claim.
"""
from fractions import Fraction
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER_RECEIPT = ROOT / 'model/lepton_register_round/results.json'
# CODATA 2022 muon to electron mass ratio and its standard uncertainty.
CODATA_2022_MU_OVER_E = 206.7682827
CODATA_2022_MU_OVER_E_SIGMA = 0.0000046
PLANTED = Fraction(2, 9)
CHAMBER = math.pi / 12
DENOMINATOR_BOUNDS = (9, 12, 30, 100)
DEFAULT_BOUND = 100


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def mu_over_e(theta):
    """Squared eigenvalue ratio of the balanced circulant, characters w^2 over w^1."""
    lam = [1 + math.sqrt(2) * math.cos(theta + 2 * math.pi * k / 3) for k in range(3)]
    return (lam[2] / lam[1]) ** 2


def deviation(theta):
    return mu_over_e(theta) / CODATA_2022_MU_OVER_E - 1


def candidates(bound):
    """Every reduced fraction p/q with 1 <= q <= bound inside the open positive chamber (0, pi/12)."""
    return sorted({Fraction(p, q) for q in range(1, bound + 1)
                   for p in range(1, math.ceil(CHAMBER * q) + 1)
                   if math.gcd(p, q) == 1 and 0 < p / q < CHAMBER})


def solve(target, low=0.2, high=0.24, steps=200):
    """Bisection for mu_over_e(theta) = target on [low, high], where the ratio increases."""
    require(mu_over_e(low) < target < mu_over_e(high), 'target ratio outside the bisection bracket')
    for _ in range(steps):
        mid = (low + high) / 2
        if mu_over_e(mid) < target:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def result():
    receipt = json.loads(REGISTER_RECEIPT.read_text())['register']['register_outputs']
    require(receipt['theta'] == str(PLANTED), 'register receipt phase differs from 2/9')
    planted_ratio = mu_over_e(float(PLANTED))
    require(abs(planted_ratio / float(receipt['mu_over_e']) - 1) < 1e-12,
            'this circulant differs from the register receipt at 2/9')
    gap = abs(deviation(float(PLANTED)))
    # Monotone ratio on the bracket, checked on a fine grid, so the window in theta is one interval.
    grid = [0.2 + 0.04 * i / 4000 for i in range(4001)]
    require(all(mu_over_e(a) < mu_over_e(b) for a, b in zip(grid, grid[1:])), 'ratio not increasing on bracket')
    low = solve(CODATA_2022_MU_OVER_E * (1 - gap))
    high = solve(CODATA_2022_MU_OVER_E * (1 + gap))
    fitted = solve(CODATA_2022_MU_OVER_E)
    width = high - low
    single = width / CHAMBER
    rows = {}
    for bound in DENOMINATOR_BOUNDS:
        family = candidates(bound)
        hits = [x for x in family if abs(deviation(float(x))) <= gap]
        # Planted control: 2/9 is in every listed family and must be reported as a hit.
        require(PLANTED in family, f'planted phase 2/9 missing from the family q <= {bound}')
        require(PLANTED in hits, f'planted phase 2/9 not reported as a hit for q <= {bound}')
        others = [x for x in family if x != PLANTED]
        nearest = min(others, key=lambda x: abs(deviation(float(x))))
        rows[str(bound)] = {
            'candidates': len(family),
            'hits': [str(x) for x in hits],
            'expected_hits_uniform_phase': f'{len(family) * single:.6e}',
            'probability_at_least_one_hit_uniform_phase': f'{1 - (1 - single) ** len(family):.6e}',
            'nearest_other_candidate': str(nearest),
            'nearest_other_deviation_ppm': f'{deviation(float(nearest)) * 1e6:.3f}',
        }
    return {
        'family': 'reduced p/q, 1 <= q <= Q, 0 < p/q < pi/12',
        'circulant': 'sqrt(m_k) proportional to 1 + sqrt2 cos(theta + 2 pi k/3); e, mu, tau = k 1, 2, 0',
        'reference': {'codata_2022_mu_over_e': str(CODATA_2022_MU_OVER_E),
                      'standard_uncertainty': str(CODATA_2022_MU_OVER_E_SIGMA)},
        'planted_phase': str(PLANTED),
        'planted_mu_over_e': f'{planted_ratio:.9f}',
        'register_receipt_mu_over_e': receipt['mu_over_e'],
        'window_relative_deviation_ppm': f'{gap * 1e6:.6f}',
        'window_in_standard_uncertainties': f'{gap * CODATA_2022_MU_OVER_E / CODATA_2022_MU_OVER_E_SIGMA:.2f}',
        'theta_window': [f'{low:.12f}', f'{high:.12f}'],
        'theta_window_width': f'{width:.6e}',
        'theta_fitted_to_codata': f'{fitted:.12f}',
        'planted_minus_fitted': f'{float(PLANTED) - fitted:.6e}',
        'single_uniform_phase_hit_probability': f'{single:.6e}',
        'by_denominator_bound': rows,
        'scope': 'Counts rational phases near the measured ratio. Tests no construction and no physical claim.',
    }


def summary(value, bound=DEFAULT_BOUND):
    row = value['by_denominator_bound'][str(bound)]
    return (f"PASS: q <= {bound}: {len(row['hits'])} of {row['candidates']} rational phases in (0, pi/12) "
            f"within {value['window_relative_deviation_ppm']} ppm of CODATA 2022 m_mu/m_e: "
            f"{', '.join(row['hits'])}; planted 2/9 reported; expected under a uniform phase "
            f"{row['expected_hits_uniform_phase']}")
