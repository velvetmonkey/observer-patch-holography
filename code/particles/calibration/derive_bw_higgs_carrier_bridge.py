#!/usr/bin/env python3
"""Emit the Borel-Weil one-Higgs carrier bridge artifact.

Chain role: identify the OPH one-Higgs slot with the minimal nontrivial
holomorphic section carrier on the local electroweak screen chart. This is a
representation and symmetry-breaking bridge only; the Higgs mass, quartic,
weak scale, and hierarchy/naturality closure remain in the D10/D11 and
hierarchy lanes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "particles" / "runs" / "calibration" / "bw_higgs_carrier_bridge.json"


def build_artifact() -> dict:
    section_degree = 1
    complex_dim = section_degree + 1
    real_dof = 2 * complex_dim
    group_dim_su2_u1 = 4
    unbroken_u1_dim = 1
    goldstone_count = group_dim_su2_u1 - unbroken_u1_dim
    radial_modes = real_dof - goldstone_count
    t3_lower = -0.5
    hypercharge = 0.5
    neutral_component_charge = t3_lower + hypercharge
    receipt = bool(
        section_degree == 1
        and complex_dim == 2
        and real_dof == 4
        and goldstone_count == 3
        and radial_modes == 1
        and neutral_component_charge == 0.0
    )
    return {
        "artifact": "oph_bw_higgs_carrier_bridge",
        "theorem_id": "BorelWeilHiggsCarrierBridge",
        "proof_status": "closed_carrier_representation_bridge",
        "BOREL_WEIL_HIGGS_CARRIER_RECEIPT": receipt,
        "claim_tier": "carrier_representation_bridge",
        "carrier": {
            "screen_chart": "C_EW ~= CP1",
            "line_bundle": "O(1)",
            "section_space": "H^0(C_EW,O(1))",
            "identification": "H_OPH ~= C^2",
            "section_degree_n": section_degree,
            "complex_dimension": complex_dim,
            "real_degrees_of_freedom": real_dof,
        },
        "representation": {
            "su2_L_representation": "fundamental_doublet",
            "su2_L_dimension": complex_dim,
            "lorentz_role": "internal_scalar_0_form",
            "hypercharge_normalization": "OPH_Z6_plus_neutral_vev",
            "T3_lower_component": t3_lower,
            "Y_H": hypercharge,
            "Q_phi0": neutral_component_charge,
        },
        "symmetry_breaking_geometry": {
            "projective_vacuum_space": "P(H_OPH) ~= CP1",
            "stabilizer": "U(1)_Q",
            "goldstone_count": goldstone_count,
            "radial_higgs_modes": radial_modes,
            "dof_split": "4 = 3 + 1",
        },
        "minimality": {
            "n_0": "H^0(CP1,O(0)) is a singlet and fails weak-doublet breaking",
            "n_1": "H^0(CP1,O(1)) is the first nontrivial section space and gives C^2",
            "n_ge_2": "higher O(n) produce larger SU(2) multiplets and fail one-Higgs minimality",
        },
        "explicit_nonclaims": [
            "Higgs mass m_H",
            "Higgs quartic lambda",
            "weak scale v",
            "Coleman-Weinberg breaking",
            "replacement of the epsilon_H=0 hierarchy/naturality lane",
        ],
        "claim_boundary": (
            "This artifact identifies the OPH one-Higgs carrier as the minimal "
            "Borel-Weil section object H^0(CP1,O(1)). It supplies representation, "
            "hypercharge-convention, and stabilizer geometry only."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the Borel-Weil OPH one-Higgs carrier bridge artifact.")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output JSON path.")
    args = parser.parse_args(argv)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_artifact(), indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
