"""Check conditional arithmetic, input dependence and domain refusal."""

import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

from acceleration_normalization import C, G, HBAR, DEFAULT_N_SCR, DEFAULT_P, compute


class AccelerationNormalizationTests(unittest.TestCase):
    def test_recovered_values(self):
        readings = compute()["readings"]
        # Comparison outputs only, at half the last printed FZ01 digit.
        self.assertAlmostEqual(readings["a_eff_presence"], 1.184737388e-10, delta=5e-20)
        self.assertAlmostEqual(readings["a_eff_poisson"], 1.179018696e-10, delta=5e-20)

    def test_capacity_sensitivity(self):
        base = compute()["readings"]
        changed = compute(DEFAULT_N_SCR * 1.01)["readings"]
        for key in base:
            self.assertAlmostEqual(changed[key] / base[key], 1 / math.sqrt(1.01), delta=2e-15)

    def test_reserve_sensitivity(self):
        base = compute()
        p = DEFAULT_P * 1.1
        changed = compute(p=p)
        expected = {
            "a_eff_presence": ((1 - DEFAULT_P / 24) / (1 - p / 24))**2,
            "a_eff_poisson": math.exp(2 * (p - DEFAULT_P) / 24),
        }
        for key, ratio in expected.items():
            self.assertGreater(changed["readings"][key], base["readings"][key])
            self.assertAlmostEqual(changed["readings"][key] / base["readings"][key], ratio, delta=2e-15)

    def test_si_constant_sensitivity(self):
        base = compute()["readings"]
        # a_OPH scales as c^(7/2) / sqrt(hbar*G) with N_scr fixed.
        for overrides, ratio in (({"c": C * 1.01}, 1.01**3.5),
                                 ({"g": G * 1.01}, 1 / math.sqrt(1.01)),
                                 ({"hbar": HBAR * 1.01}, 1 / math.sqrt(1.01))):
            with self.subTest(overrides=overrides):
                changed = compute(**overrides)["readings"]
                for key in base:
                    self.assertAlmostEqual(changed[key] / base[key], ratio, delta=2e-15)

    def test_zero_reserve(self):
        result = compute(p=0)
        for value in result["readings"].values():
            self.assertEqual(value, result["intermediates"]["a_OPH"])

    def test_invalid_domains(self):
        for name in ("n_scr", "p", "c", "g", "hbar"):
            invalid = [-1, math.nan, math.inf, -math.inf, True, "1", None]
            if name != "p":
                invalid.append(0)
            for value in invalid:
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    compute(**{name: value})
        for p in (24, 25, 1e308):
            with self.subTest(p=p), self.assertRaises(ValueError):
                compute(p=p)

    def test_arithmetic_range_refusal(self):
        for overrides in ({"c": 1e308}, {"c": 1e-300}, {"hbar": 1e-300},
                          {"n_scr": 1e-300}, {"g": 1e308}, {"n_scr": 10**1000}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                compute(**overrides)

    def test_cli_and_provenance(self):
        script = Path(__file__).with_name("acceleration_normalization.py")
        run = subprocess.run([sys.executable, str(script), "--p", "2"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["inputs"], {"N_scr": DEFAULT_N_SCR, "P": 2.0,
                                           "c": C, "G": G, "hbar": HBAR})
        self.assertEqual(result["readings"], compute(p=2)["readings"])
        self.assertEqual(result["status"], "RECOVERED CONDITIONAL BENCHMARK ARITHMETIC")
        self.assertEqual(result["physical_normalization"], "UNPROVED")
        self.assertEqual(result["external_capacity_attachment"], "UNPROVED")
        self.assertEqual(result["units"]["a_eff_presence"], "m s^-2")
        self.assertEqual(result["provenance"]["commit"], "3b09f6b26655606b144a526a1b246d1d865f04a7")
        self.assertEqual(len(result["provenance"]["sources"]), 4)
        invalid = subprocess.run([sys.executable, str(script), "--p", "24"],
                                 capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, "")
        self.assertIn("positive presence survival", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
