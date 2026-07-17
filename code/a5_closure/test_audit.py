#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import math
import pathlib
import sys
import unittest

# Layout note: this repo keeps the certificates flat alongside the suite,
# rather than the upstream bundle's code/ + tests/ split.
ROOT = pathlib.Path(__file__).resolve().parent


def load(name: str):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


class AuditTests(unittest.TestCase):
    def test_gravity_units(self):
        m = load("gravity_units_corrected")
        p = m.evaluate(m.ARCHIVED_G_N)
        self.assertAlmostEqual(p.acceleration_boost_nu, 1.725381227058617, places=12)
        self.assertAlmostEqual(p.velocity_boost_sqrt_nu, 1.3135376762996245, places=12)
        self.assertAlmostEqual(p.gamma_log10_velocity_boost, 0.11844253420192026, places=12)

    def test_a5_decompositions(self):
        m = load("a5_harmonic_decomposition")
        self.assertEqual(m.decompose(3), {"3prime": 1, "4": 1})
        self.assertEqual(m.decompose(5), {"3": 1, "3prime": 1, "5": 1})
        self.assertEqual(m.decompose(6), {"1": 1, "3": 1, "4": 1, "5": 1})
        self.assertTrue(m.payload(15)["port_equals_restriction_H0_plus_H5"])

    def test_a5_selection_certificate(self):
        m = load("a5_selection_certificate")
        p = m.payload()
        self.assertEqual(p["number_of_distances"], 3)
        self.assertEqual(p["spherical_design_strength"], 5)
        self.assertTrue(p["fourth_moment_matches_uniform_S2"])

    def test_compact_dimensions(self):
        m = load("a5_compact_lie_classifier")
        self.assertEqual(m.partitions(11), [(3, 8)])
        self.assertEqual(m.partitions(12), [(3, 3, 3, 3)])

    def test_log_coefficients(self):
        m = load("bh_log_correction")
        p = m.payload()
        self.assertAlmostEqual(p["candidate_coefficients"]["12_port_exact_balance"], 5.5)
        self.assertLess(abs(p["numerical_stirling_checks"]["q12_effective_c_12000_to_120000"] - 5.5), 0.01)

    def test_jacobi_scaling(self):
        m = load("hysteresis_scaling_guard")
        p = m.payload()["worked_ratio_50_to_100_kpc"]
        self.assertAlmostEqual(p["Gamma_50_over_Gamma_100"], 2 ** 1.5, places=12)
        self.assertAlmostEqual(p["Gamma2_50_over_Gamma2_100"], 8.0, places=12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
