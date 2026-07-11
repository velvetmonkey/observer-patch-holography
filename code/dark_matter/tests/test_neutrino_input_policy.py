from __future__ import annotations

import argparse
import math
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import camb_fixed_neutrino_compare  # noqa: E402
import d6_capacity_calculator  # noqa: E402
import dark_cmb_bao_growth_s8_likelihood  # noqa: E402
import dark_empirical_scorecard  # noqa: E402
import dark_homogeneous_state_selection  # noqa: E402
import dark_parent_collar_grid  # noqa: E402


class NeutrinoInputPolicyTests(unittest.TestCase):
    def test_default_is_external_minimal_normal_reference(self) -> None:
        default = d6_capacity_calculator.DEFAULT_COSMOLOGY_SUM_MNU_EV
        self.assertTrue(
            math.isclose(
                default,
                d6_capacity_calculator.MINIMAL_NORMAL_REFERENCE_SUM_MNU_EV,
                rel_tol=0.0,
                abs_tol=1.0e-15,
            )
        )
        provenance = d6_capacity_calculator.neutrino_mass_input_provenance(default)
        self.assertEqual(provenance["status"], "external_minimal_normal_reference")
        self.assertFalse(provenance["oph_prediction"])
        self.assertFalse(provenance["source_closed_oph_input"])
        self.assertFalse(provenance["public_promotion_allowed"])

    def test_rejected_weighted_cycle_sum_fails_closed(self) -> None:
        rejected = d6_capacity_calculator.REJECTED_WEIGHTED_CYCLE_SUM_MNU_EV
        provenance = d6_capacity_calculator.neutrino_mass_input_provenance(rejected)
        self.assertEqual(
            provenance["status"],
            "rejected_target_informed_weighted_cycle_compare_only",
        )
        self.assertTrue(provenance["rejected_candidate"])
        self.assertFalse(provenance["oph_prediction"])
        self.assertFalse(provenance["public_promotion_allowed"])

        payload = dark_homogeneous_state_selection.compute(
            argparse.Namespace(
                n_scr=d6_capacity_calculator.DEFAULT_N_SCR,
                H0_km_s_Mpc=67.4,
                ombh2=0.02237,
                sum_mnu_eV=rejected,
                omega_r=9.17e-5,
            )
        )
        self.assertFalse(payload["status"]["public_promotion_allowed"])
        self.assertEqual(
            payload["status"]["neutrino_input_status"],
            "rejected_target_informed_weighted_cycle_compare_only",
        )

    def test_rejected_camb_scenario_is_explicitly_compare_only(self) -> None:
        scenario = next(
            item
            for item in camb_fixed_neutrino_compare.SCENARIOS
            if item.name == "rejected_weighted_cycle_compare_only"
        )
        self.assertEqual(scenario.scientific_status, "rejected_target_informed_compare_only")
        self.assertFalse(scenario.oph_prediction)
        self.assertFalse(scenario.public_promotion_allowed)
        self.assertEqual(
            scenario.exact_masses_eV,
            d6_capacity_calculator.REJECTED_WEIGHTED_CYCLE_MASSES_EV,
        )

    def test_blocked_cmb_payload_carries_fail_closed_provenance(self) -> None:
        rejected = d6_capacity_calculator.REJECTED_WEIGHTED_CYCLE_SUM_MNU_EV
        payload = dark_cmb_bao_growth_s8_likelihood.compute(
            argparse.Namespace(parent_grid=None, sum_mnu_eV=rejected)
        )
        self.assertFalse(payload["status"]["ready"])
        self.assertFalse(payload["status"]["public_promotion_allowed"])
        self.assertTrue(
            payload["neutrino_mass_input_provenance"]["rejected_candidate"]
        )

    def test_scorecard_derives_ratio_and_invalidates_rejected_input(self) -> None:
        rejected = d6_capacity_calculator.REJECTED_WEIGHTED_CYCLE_SUM_MNU_EV
        homogeneous = {
            "density_fractions": {
                "Omega_A": 0.26411440128712577,
                "Omega_b": 0.04924319136384048,
            }
        }
        captured: dict[str, float] = {}

        def parent_stub(args: argparse.Namespace) -> dict[str, float]:
            captured["mu_eq"] = args.mu_eq
            return {"rho_A_over_rho_b": args.mu_eq}

        args = argparse.Namespace(
            sum_mnu_eV=rejected,
            mu_eq=None,
            n_scr=d6_capacity_calculator.DEFAULT_N_SCR,
            B_A=1.0,
            H0=67.4,
            ombh2_cmb=0.0224,
            ombh2_homogeneous=0.02237,
            neutrino_hierarchy="normal",
            separation_kpc=200.0,
            time_since_passage_gyr=0.2,
            observed_offset_kpc=150.0,
            offset_sigma_kpc=50.0,
            parent_grid_out=Path("parent.json"),
            out_json=Path("scorecard.json"),
            out_md=Path("scorecard.md"),
        )
        with (
            patch.object(
                dark_empirical_scorecard,
                "build_homogeneous_state",
                return_value=homogeneous,
            ),
            patch.object(
                dark_empirical_scorecard,
                "build_parent_grid",
                side_effect=parent_stub,
            ),
            patch.object(dark_empirical_scorecard, "build_sparc", return_value={}),
            patch.object(dark_empirical_scorecard, "build_cluster", return_value={}),
            patch.object(dark_empirical_scorecard, "build_cmb", return_value={}),
        ):
            payload = dark_empirical_scorecard.compute(args)

        expected_ratio = homogeneous["density_fractions"]["Omega_A"] / homogeneous[
            "density_fractions"
        ]["Omega_b"]
        self.assertAlmostEqual(captured["mu_eq"], expected_ratio)
        self.assertTrue(payload["status"]["invalidated_by_rejected_neutrino_input"])
        self.assertFalse(payload["status"]["public_promotion_allowed"])
        self.assertEqual(
            payload["inputs"]["mu_eq_source"],
            "derived_from_declared_homogeneous_external_neutrino_input",
        )

    def test_cli_defaults_do_not_use_rejected_candidate(self) -> None:
        with patch.object(sys, "argv", ["dark_homogeneous_state_selection.py"]):
            homogeneous = dark_homogeneous_state_selection.parse_args()
        with patch.object(sys, "argv", ["dark_cmb_bao_growth_s8_likelihood.py"]):
            cmb = dark_cmb_bao_growth_s8_likelihood.parse_args()
        with patch.object(sys, "argv", ["dark_empirical_scorecard.py"]):
            scorecard = dark_empirical_scorecard.parse_args()
        with patch.object(sys, "argv", ["dark_parent_collar_grid.py"]):
            parent_grid = dark_parent_collar_grid.parse_args()

        expected = d6_capacity_calculator.DEFAULT_COSMOLOGY_SUM_MNU_EV
        self.assertEqual(homogeneous.sum_mnu_eV, expected)
        self.assertEqual(cmb.sum_mnu_eV, expected)
        self.assertEqual(scorecard.sum_mnu_eV, expected)
        self.assertEqual(cmb.neutrino_hierarchy, "normal")
        self.assertEqual(scorecard.neutrino_hierarchy, "normal")
        self.assertIsNone(scorecard.mu_eq)
        self.assertIsNone(parent_grid.mu_eq)
        self.assertNotEqual(
            expected,
            d6_capacity_calculator.REJECTED_WEIGHTED_CYCLE_SUM_MNU_EV,
        )


if __name__ == "__main__":
    unittest.main()
