#!/usr/bin/env python3
"""Certify the forward D10 transmutation map behind the calibration lane.

Chain role: expose the internal D10 `P -> alpha_U -> t` map as an explicit
calibration artifact beneath the source-only electroweak repair theorem.

Mathematics: solve the unified coupling from the pixel-closure residual, record
the associated heat-kernel diffusion times, and reconstruct the same internal
transmutation parameters from the emitted D10 source-only basis without any
low-energy target readback.

OPH-derived inputs: the D10 observable family emitted from `P` and the reduced
source transport pair `(alpha2_mz, alphaY_mz, eta_source, v_report)`.

Output: a machine-readable certificate for
`EWForwardTransmutationCertificate_D10`.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

try:
    from calibration._legacy_d10 import require_legacy_d10_path
except ModuleNotFoundError:  # direct script execution from calibration/
    from _legacy_d10 import require_legacy_d10_path


require_legacy_d10_path()

from particle_masses_paper_d10_d11 import E_PLANCK_GEV, pixel_residual, solve_mz_fixed_point_tree  # type: ignore


DEFAULT_FAMILY = ROOT / "particles" / "runs" / "calibration" / "d10_ew_observable_family.json"
DEFAULT_SOURCE_PAIR = ROOT / "particles" / "runs" / "calibration" / "d10_ew_source_transport_pair.json"
DEFAULT_OUT = ROOT / "particles" / "runs" / "calibration" / "d10_ew_forward_transmutation_certificate.json"
DEFAULT_COLOR_COUNT = 3


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact(family: dict, source_pair: dict, *, color_count: int) -> dict:
    core = dict(family.get("core_source") or {})
    pair = dict(source_pair.get("source_pair") or {})
    compact_slice = dict(source_pair.get("compact_hypercharge_only_mass_slice") or {})
    population_basis = dict(source_pair.get("population_basis") or {})

    p_value = float(family["p"])
    mu_u = float(core["mu_u"])
    alpha_u = float(core["alpha_u"])
    alpha1_mz = float(core["alpha1_mz"])
    alpha2_mz = float(core["alpha2_mz"])
    alpha3_mz = float(core["alpha3_mz"])
    alpha_y_mz = float(pair["alphaY_mz"])
    eta_source = float(compact_slice["eta_EW"])
    beta_ratio_ew = float(population_basis["beta_EW"])
    beta_transmutation_ew = color_count + 1
    e_cell = E_PLANCK_GEV / math.sqrt(p_value)

    alpha_u_from_source = eta_source / beta_ratio_ew
    t_u = 4.0 * math.pi * math.pi * alpha_u
    t_u_from_source = 4.0 * math.pi * math.pi * alpha_u_from_source
    t1_mz = 4.0 * math.pi * math.pi * alpha1_mz
    t2_mz = 4.0 * math.pi * math.pi * alpha2_mz
    t3_mz = 4.0 * math.pi * math.pi * alpha3_mz
    t_tr = 2.0 * math.pi / (beta_transmutation_ew * alpha_u)
    t_tr_from_source = 2.0 * math.pi / (beta_transmutation_ew * alpha_u_from_source)
    v_core = float(core["v"])
    v_from_source = e_cell * math.exp(-t_tr_from_source)
    mz_run = float(core["mz_run"])
    mz_check, v_check, a1_check, a2_check, a3_check = solve_mz_fixed_point_tree(alpha_u, p_value, color_count, mu_u)

    return {
        "artifact": "oph_d10_ew_forward_transmutation_certificate",
        "generated_utc": _timestamp(),
        "status": "closed_forward_p_to_t_map",
        "object_id": "EWForwardTransmutationCertificate_D10",
        "proof_gate": "P_to_alphaU_to_t_without_low_energy_readback",
        "family_source_id": family.get("observable_family_id"),
        "source_pair_artifact": source_pair.get("artifact"),
        "theorem": {
            "name": "EWForwardTransmutationCertificate_D10",
            "statement": (
                "On the realized D10 branch, the OPH input P fixes alpha_U through the pixel-closure "
                "equation, which then fixes both the unified diffusion time t_U = 4*pi^2*alpha_U and "
                "the dimensional-transmutation exponent t_tr = 2*pi / ((N_c + 1) * alpha_U). Once the "
                "source-only basis (alpha2_mz, alphaY_mz, eta_source, v_report) has been emitted on that "
                "same branch, it reconstructs the same alpha_U through alpha_U = eta_source / beta_ratio_EW. "
                "No measured low-energy coupling or reference W/Z target is used to determine the internal "
                "transmutation parameters."
            ),
            "formulas": {
                "alpha_u_from_source": "eta_source / beta_ratio_EW",
                "t_unified": "4 * pi^2 * alpha_U",
                "t_transmutation": "2 * pi / (beta_transmutation_EW * alpha_U)",
                "v_from_transmutation": "E_cell(P) * exp(-t_transmutation)",
                "pixel_constraint": "ellbar_SU2(t2_mz_run) + ellbar_SU3(t3_mz_run) = P / 4",
            },
        },
        "oph_inputs": {
            "p": p_value,
            "mu_u_gev": mu_u,
            "e_cell_gev": e_cell,
            "realized_color_count": color_count,
        },
        "notation_split": {
            "beta_ratio_EW": {
                "role": "existing_calibration_source_ratio",
                "formula": "(alpha2_mz - alphaY_mz) / (alpha2_mz + alphaY_mz)",
                "value": beta_ratio_ew,
            },
            "beta_transmutation_EW": {
                "role": "paper_e25_transmutation_counting_factor",
                "formula": "N_c + 1",
                "value": beta_transmutation_ew,
            },
        },
        "forward_core_solution": {
            "alpha_u": alpha_u,
            "t_unified": t_u,
            "t1_mz_run": t1_mz,
            "t2_mz_run": t2_mz,
            "t3_mz_run": t3_mz,
            "t_transmutation": t_tr,
            "mz_run_gev": mz_run,
            "v_report_gev": v_core,
        },
        "source_only_reconstruction": {
            "alpha2_mz": alpha2_mz,
            "alphaY_mz": alpha_y_mz,
            "eta_source": eta_source,
            "alpha_u_from_source": alpha_u_from_source,
            "t_unified_from_source": t_u_from_source,
            "t_transmutation_from_source": t_tr_from_source,
            "v_from_source_transmutation_gev": v_from_source,
        },
        "forward_checks": {
            "pixel_residual": pixel_residual(alpha2_mz, alpha3_mz, p_value),
            "mz_fixed_point_residual_gev": mz_check - mz_run,
            "v_fixed_point_residual_gev": v_check - v_core,
            "alpha1_fixed_point_residual": a1_check - alpha1_mz,
            "alpha2_fixed_point_residual": a2_check - alpha2_mz,
            "alpha3_fixed_point_residual": a3_check - alpha3_mz,
            "alpha_u_source_vs_core_residual": alpha_u_from_source - alpha_u,
            "t_unified_source_vs_core_residual": t_u_from_source - t_u,
            "t_transmutation_source_vs_core_residual": t_tr_from_source - t_tr,
            "v_source_vs_core_residual_gev": v_from_source - v_core,
        },
        "notes": [
            "The certificate exposes alpha_U and the transmutation parameters t_U and t_tr as first-class artifacts.",
            "This certificate separates the source-ratio beta_ratio_EW from the paper's transmutation counting factor beta_transmutation_EW = N_c + 1 so the two roles are not conflated.",
            "Low-energy gauge observables remain compare-only outputs of the forward D10 branch, not inputs that fix alpha_U, t_U, or t_tr.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the D10 forward transmutation certificate artifact.")
    parser.add_argument("--family", default=str(DEFAULT_FAMILY))
    parser.add_argument("--source-pair", default=str(DEFAULT_SOURCE_PAIR))
    parser.add_argument("--color-count", type=int, default=DEFAULT_COLOR_COUNT)
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    family = _load_json(Path(args.family))
    source_pair = _load_json(Path(args.source_pair))
    artifact = build_artifact(family, source_pair, color_count=args.color_count)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
