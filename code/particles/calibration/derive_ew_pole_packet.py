#!/usr/bin/env python3
"""Preregistered CL-5 radiative prescription diagnostic for the W/Z chart.

Executes falsification/preregistered/ew_pole_packet_spec_2026-07-16.json and
emits code/particles/runs/calibration/ew_pole_packet_2026-07-16.json.

The numerical packet applies the partial one-loop propagator prescription
MV_trial^2 = MV_tree^2 - Re Sigma_hat_T(MV_tree^2; mz_run), with the
transverse self-energies of sm_one_loop_self_energy_engine (Denner
arXiv:0709.1075 appendix B, 't Hooft-Feynman gauge, tadpole-renormalized
scheme, MS-bar finite parts). Every transport object, the pixel-residual
selector formula, the transmutation law, and the clock display adapter are
retained exactly. All branches are discrete, declared in the spec before any
pole-packet chain number existed, and all are emitted. The script fails
closed if the spec hash does not verify, if the engine certification breaks,
if the baseline chain does not reproduce the frozen one-loop values, or if
any declared solver loses its bracket. It also marks the physical comparison
NOT_EVALUABLE while any readout-identification gate remains open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent

try:
    from calibration._legacy_d10 import require_legacy_d10_path
except ModuleNotFoundError:
    from _legacy_d10 import require_legacy_d10_path

require_legacy_d10_path()

import particle_masses_paper_d10_d11 as pm  # type: ignore

try:
    from calibration.derive_wzh_residual_elimination_boundary import (
        strict_branch_two_law_evaluation,
    )
    from calibration import sm_one_loop_self_energy_engine as engine
except ModuleNotFoundError:
    from derive_wzh_residual_elimination_boundary import (
        strict_branch_two_law_evaluation,
    )
    import sm_one_loop_self_energy_engine as engine

try:
    from calibration.ew_physical_readout_gate import classify_physical_comparison
except ModuleNotFoundError:
    from ew_physical_readout_gate import classify_physical_comparison

SPEC_PATH = (
    REPO / "falsification" / "preregistered" / "ew_pole_packet_spec_2026-07-16.json"
)
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "calibration" / "ew_pole_packet_2026-07-16.json"
)
CLOCK_CERT = (
    ROOT / "particles" / "hierarchy" / "certificates"
    / "R_gamma_noG_DAG_certificate.json"
)

ALPHA_U_WINDOW = (0.02, 0.08)
ALPHA_U_SCAN_POINTS = 41
BISECTION_ITERATIONS = 90
BASELINE_MATCH_RTOL = 1e-9
LAWS = ("zero_selector", "nonzero_carrier")
MT_BRANCHES = ("mt_pole_stage5", "mt_msbar_stage5")


def load_and_verify_spec() -> dict:
    """Load the preregistration spec and verify its companion sha256."""

    doc = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    body = {k: v for k, v in doc.items() if k != "spec_sha256"}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    recorded = doc["spec_sha256"]["hexdigest"]
    if digest != recorded:
        raise SystemExit(
            f"spec hash mismatch: recomputed {digest}, recorded {recorded}; "
            "fail closed"
        )
    return doc


def e_star_display_gev() -> tuple[str, float]:
    clock = json.loads(CLOCK_CERT.read_text(encoding="utf-8"))
    epsilon_cs = clock["candidate_values_from_sources"]["epsilon_Cs"]
    value = 6.62607015e-34 * 9192631770.0 / float(epsilon_cs) / 1.602176634e-10
    return epsilon_cs, value


def sm_point(
    alpha: float, sw2: float, mw: float, mz: float, mh: float, mt: float
) -> engine.SMInputs:
    """Declared per-cell parameter point: massless light fermions, top per branch."""

    return engine.SMInputs(
        alpha=alpha,
        sw2=sw2,
        mw=mw,
        mz=mz,
        mh=mh,
        lepton_masses=(0.0, 0.0, 0.0),
        up_masses=(0.0, 0.0, mt),
        down_masses=(0.0, 0.0, 0.0),
    )


def pole_shift_pair(
    law: dict,
    v_over_e: float,
    e_star: float,
    mu_scale_gev: float,
    mt: float,
    mh: float,
) -> dict:
    """The declared pole shift on one law cell.

    MV_pole^2 = MV_tree^2 - Re Sigma_hat_T(MV_tree^2; mu), parameter point per
    the spec's self_energy_parameter_point_per_cell rule.
    """

    mw_tree = law["MW_over_E_star"] * e_star
    mz_tree = law["MZ_over_E_star"] * e_star
    sw2 = law["sin2w_eff"]
    a2p_eff = law["MW_over_E_star"] ** 2 / (math.pi * v_over_e**2)
    alpha_eff = a2p_eff * sw2
    point = sm_point(alpha_eff, sw2, mw_tree, mz_tree, mh, mt)
    mu2 = mu_scale_gev**2
    sig_w = engine.sigma_w_t(point, mw_tree**2, mu2)
    sig_z = engine.sigma_zz_t(point, mz_tree**2, mu2)
    mw_pole2 = mw_tree**2 - sig_w
    mz_pole2 = mz_tree**2 - sig_z
    if mw_pole2 <= 0.0 or mz_pole2 <= 0.0:
        return {"gated": True, "gate": "pole_mass_squared_nonpositive"}
    return {
        "gated": False,
        "MW_GeV": math.sqrt(mw_pole2),
        "MZ_GeV": math.sqrt(mz_pole2),
        "tree_pair_GeV": [mw_tree, mz_tree],
        "sigma_over_m2_W": sig_w / mw_tree**2,
        "sigma_over_m2_Z": sig_z / mz_tree**2,
    }


def solve_mz_pole_fixed_point(
    alpha_u: float, p_value: float, n_c: int, mu_u: float, mt: float, mh: float
) -> tuple[float, float, float, float, float]:
    """Tier B fixed point: mu solves MZ_pole(mu) = mu.

    Mirrors solve_mz_fixed_point_tree of the lane (260-point logspace grid,
    90 geometric-midpoint bisections); grid points with MZ_pole^2 <= 0 are
    invalid and never bracket. Fails closed via RuntimeError.
    """

    v_ev = pm.v_from_transmutation(alpha_u, p_value, n_c)

    def f(mu: float) -> float | None:
        a1, a2, a3 = pm.run_alphas_from_unification(alpha_u, mu, mu_u)
        if a1 <= 0.0 or a2 <= 0.0 or a3 <= 0.0:
            return None
        ay = 0.6 * a1
        sw2 = ay / (a2 + ay)
        mz_tree = pm.mz_tree_from_v_and_couplings(v_ev, a1, a2)
        mw_tree = 0.5 * v_ev * math.sqrt(4.0 * math.pi * a2)
        point = sm_point(a2 * sw2, sw2, mw_tree, mz_tree, mh, mt)
        pole2 = mz_tree**2 - engine.sigma_zz_t(point, mz_tree**2, mu * mu)
        if pole2 <= 0.0:
            return None
        return math.sqrt(pole2) - mu

    grid = np.logspace(0, 5, 260)
    prev_mu = None
    prev_f = None
    for mu in grid:
        mu = float(mu)
        val = f(mu)
        if val is None:
            prev_mu, prev_f = None, None
            continue
        if prev_f is not None and val * prev_f < 0:
            lo, hi = float(prev_mu), mu
            flo = float(prev_f)
            for _ in range(BISECTION_ITERATIONS):
                mid = math.sqrt(lo * hi)
                fm = f(mid)
                if fm is None:
                    raise RuntimeError(
                        "MZ pole fixed point: invalid midpoint inside bracket"
                    )
                if flo * fm > 0:
                    lo, flo = mid, fm
                else:
                    hi = mid
            mz_run = 0.5 * (lo + hi)
            a1, a2, a3 = pm.run_alphas_from_unification(alpha_u, mz_run, mu_u)
            return mz_run, v_ev, a1, a2, a3
        prev_mu, prev_f = mu, float(val)

    raise RuntimeError("Could not bracket the MZ pole fixed point.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    started = time.time()
    spec = load_and_verify_spec()
    base_spec = spec["baseline_one_loop_chain"]
    p_value = float(base_spec["pixel_P"])
    n_c = int(base_spec["n_c"])
    beta_ew = float(base_spec["beta_EW"])
    targets = {
        "MW": tuple(spec["targets_GeV"]["MW"]),
        "MZ": tuple(spec["targets_GeV"]["MZ"]),
    }
    stage5 = spec["revision_declaration"]["stage5_internal_masses_GeV"]
    epsilon_cs, e_star = e_star_display_gev()

    # Engine certification gate: fail closed if any anchor breaks.
    cert = engine.validate()
    if not cert["all_ok"]:
        raise SystemExit("self-energy engine certification failed; fail closed")

    # Baseline one-loop chain, reproduced and matched against the spec.
    d10 = pm.build_paper_d10(pix_area=p_value, n_c=n_c)
    ay0 = 0.6 * d10.alpha1_mz
    a20 = d10.alpha2_mz
    sin2_0 = ay0 / (ay0 + a20)
    eta0 = d10.alpha_u * (1.0 - 2.0 * sin2_0)
    v_over_e0 = math.exp(-2.0 * math.pi / (beta_ew * d10.alpha_u)) / math.sqrt(
        p_value
    )
    two0 = strict_branch_two_law_evaluation(a20, ay0, eta0, v_over_e0)

    expected = base_spec["recomputed_and_matched_against_frozen_results"]
    checks = {
        "alpha_U": (d10.alpha_u, expected["alpha_U"]),
        "mu_U_GeV": (d10.mu_u, expected["mu_U_GeV"]),
        "mz_run_fixed_point_GeV": (d10.mz_run, expected["mz_run_fixed_point_GeV"]),
        "MW_zero_selector_GeV": (
            two0["zero_selector_law"]["MW_over_E_star"] * e_star,
            expected["MW_zero_selector_GeV"],
        ),
        "MZ_zero_selector_GeV": (
            two0["zero_selector_law"]["MZ_over_E_star"] * e_star,
            expected["MZ_zero_selector_GeV"],
        ),
        "MW_nonzero_carrier_GeV": (
            two0["nonzero_carrier_law"]["MW_over_E_star"] * e_star,
            expected["MW_nonzero_carrier_GeV"],
        ),
        "MZ_nonzero_carrier_GeV": (
            two0["nonzero_carrier_law"]["MZ_over_E_star"] * e_star,
            expected["MZ_nonzero_carrier_GeV"],
        ),
    }
    for name, (got, want) in checks.items():
        if abs(got - want) > BASELINE_MATCH_RTOL * max(1.0, abs(want)):
            raise SystemExit(
                f"baseline mismatch on {name}: got {got!r}, spec {want!r}; "
                "fail closed"
            )

    # Stage-5 internal loop masses, recomputed and matched against the spec.
    d11 = pm.integrate_d11_literal_core(d10)
    stage5_checks = {
        "mt_pole_stage5": (d11.mt_pole, stage5["mt_pole_stage5"]),
        "mt_msbar_stage5": (d11.mt_ms, stage5["mt_msbar_stage5"]),
        "mH_stage5": (d11.m_h_tree, stage5["mH_stage5"]),
    }
    for name, (got, want) in stage5_checks.items():
        if abs(got - want) > BASELINE_MATCH_RTOL * max(1.0, abs(want)):
            raise SystemExit(
                f"stage-5 mass mismatch on {name}: got {got!r}, spec {want!r}; "
                "fail closed"
            )
    mt_by_branch = {
        "mt_pole_stage5": stage5["mt_pole_stage5"],
        "mt_msbar_stage5": stage5["mt_msbar_stage5"],
    }
    mh_stage5 = stage5["mH_stage5"]

    baseline_cells = {
        law_id: {
            "MW_GeV": two0[f"{law_id}_law"]["MW_over_E_star"] * e_star,
            "MZ_GeV": two0[f"{law_id}_law"]["MZ_over_E_star"] * e_star,
        }
        for law_id in LAWS
    }

    gates_open = list(spec["fail_closed_gates_declared_open"])
    gates_triggered: list[dict] = []
    diagnostics: dict[str, object] = {}
    cells: list[dict] = []

    def emit(tier: str, branch: str, law_id: str, shifted: dict) -> None:
        mw, mz = shifted["MW_GeV"], shifted["MZ_GeV"]
        mw_t, mw_s = targets["MW"]
        mz_t, mz_s = targets["MZ"]
        base = baseline_cells[law_id]
        cells.append(
            {
                "id": f"tier={tier}|mt={branch}|law={law_id}",
                "MW_GeV": mw,
                "MZ_GeV": mz,
                "MW_offset_GeV": mw - mw_t,
                "MZ_offset_GeV": mz - mz_t,
                "MW_pull_sigma": (mw - mw_t) / mw_s,
                "MZ_pull_sigma": (mz - mz_t) / mz_s,
                "landing": (
                    abs(mw - mw_t) <= mw_s and abs(mz - mz_t) <= mz_s
                ),
                "shift_from_baseline_MW_GeV": mw - base["MW_GeV"],
                "shift_from_baseline_MZ_GeV": mz - base["MZ_GeV"],
            }
        )

    # ------------------------------------------------------------------
    # Tier A: pole shift on the frozen baseline basis.
    # ------------------------------------------------------------------
    for branch in MT_BRANCHES:
        mt = mt_by_branch[branch]
        diag_key = f"tier_A|{branch}"
        diagnostics[diag_key] = {}
        for law_id in LAWS:
            shifted = pole_shift_pair(
                two0[f"{law_id}_law"], v_over_e0, e_star, d10.mz_run, mt, mh_stage5
            )
            diagnostics[diag_key][law_id] = shifted
            if shifted["gated"]:
                gates_triggered.append(
                    {"cell_group": f"{diag_key}|{law_id}", "gate": shifted["gate"]}
                )
                continue
            emit("A_readout_shift", branch, law_id, shifted)

    # ------------------------------------------------------------------
    # Tier B: pole-declared fixed point plus alpha_U re-solve.
    # ------------------------------------------------------------------
    for branch in MT_BRANCHES:
        mt = mt_by_branch[branch]
        diag_key = f"tier_B|{branch}"
        cache: dict[float, tuple] = {}

        def state_of(alpha_u: float, _mt=mt, _cache=cache):
            if alpha_u in _cache:
                return _cache[alpha_u]
            mz_run, v_ev, a1, a2, a3 = solve_mz_pole_fixed_point(
                alpha_u, p_value, n_c, d10.mu_u, _mt, mh_stage5
            )
            residual = pm.pixel_residual(a2, a3, p_value)
            state = (residual, mz_run, a1, a2, a3)
            _cache[alpha_u] = state
            return state

        scan_rows = []
        bracket = None
        last = None
        for x in np.linspace(*ALPHA_U_WINDOW, ALPHA_U_SCAN_POINTS):
            x = float(x)
            try:
                rx = state_of(x)[0]
            except (RuntimeError, OverflowError, ValueError) as exc:
                scan_rows.append(
                    {"alpha_U": x, "status": f"{type(exc).__name__}: {exc}"}
                )
                last = None
                continue
            scan_rows.append({"alpha_U": x, "pixel_residual": rx})
            if last is not None and rx * last[1] < 0:
                bracket = (last[0], x)
                break
            last = (x, rx)
        diagnostics[diag_key] = {"alpha_U_scan": scan_rows}

        if bracket is None:
            gates_triggered.append(
                {
                    "cell_group": diag_key,
                    "gate": "alpha_U_bracket_lost_in_declared_window",
                }
            )
            diagnostics[diag_key]["gated"] = True
            continue

        lo, hi = bracket
        try:
            for _ in range(BISECTION_ITERATIONS):
                mid = 0.5 * (lo + hi)
                if mid == lo or mid == hi:
                    break
                if state_of(lo)[0] * state_of(mid)[0] <= 0:
                    hi = mid
                else:
                    lo = mid
        except (RuntimeError, OverflowError, ValueError) as exc:
            gates_triggered.append(
                {"cell_group": diag_key, "gate": f"bisection_failed: {exc}"}
            )
            diagnostics[diag_key]["gated"] = True
            continue
        alpha_u_star = 0.5 * (lo + hi)
        residual, mz_run_star, a1s, a2s, a3s = state_of(alpha_u_star)
        ay_s = 0.6 * a1s
        sin2_s = ay_s / (a2s + ay_s)
        eta_s = alpha_u_star * (1.0 - 2.0 * sin2_s)
        v_over_e_s = math.exp(
            -2.0 * math.pi / (beta_ew * alpha_u_star)
        ) / math.sqrt(p_value)
        two_s = strict_branch_two_law_evaluation(a2s, ay_s, eta_s, v_over_e_s)
        diagnostics[diag_key].update(
            {
                "gated": False,
                "alpha_U_pole": alpha_u_star,
                "alpha_U_shift_from_baseline": alpha_u_star - d10.alpha_u,
                "pixel_residual_at_root": residual,
                "mz_run_pole_fixed_point_GeV": mz_run_star,
                "mz_run_shift_from_baseline_GeV": mz_run_star - d10.mz_run,
                "v_over_E_star_pole": v_over_e_s,
                "v_over_E_star_shift_relative": v_over_e_s / v_over_e0 - 1.0,
                "couplings_at_mz_run": {
                    "alpha1": a1s,
                    "alpha2": a2s,
                    "alpha3": a3s,
                },
                "basis": {
                    "sin2_theta": sin2_s,
                    "eta_source": eta_s,
                },
                "laws": {},
            }
        )
        for law_id in LAWS:
            shifted = pole_shift_pair(
                two_s[f"{law_id}_law"], v_over_e_s, e_star, mz_run_star, mt, mh_stage5
            )
            diagnostics[diag_key]["laws"][law_id] = shifted
            if shifted["gated"]:
                gates_triggered.append(
                    {"cell_group": f"{diag_key}|{law_id}", "gate": shifted["gate"]}
                )
                continue
            emit("B_pole_fixed_point", branch, law_id, shifted)

    # ------------------------------------------------------------------
    # Verdict on the primary display cell (declared in the spec).
    # ------------------------------------------------------------------
    primary_id = "tier=B_pole_fixed_point|mt=mt_pole_stage5|law=zero_selector"
    primary = next((c for c in cells if c["id"] == primary_id), None)
    base = baseline_cells["zero_selector"]
    if primary is None:
        verdict = {
            "primary_cell": primary_id,
            "status": "gated",
            "direction": "undetermined",
            "statement": "the primary cell is gated; see gates_triggered",
        }
    else:
        mw_t, _ = targets["MW"]
        mz_t, _ = targets["MZ"]
        mw_shrinks = abs(primary["MW_offset_GeV"]) < abs(base["MW_GeV"] - mw_t)
        mz_shrinks = abs(primary["MZ_offset_GeV"]) < abs(base["MZ_GeV"] - mz_t)
        if mw_shrinks and mz_shrinks:
            direction = "toward_measurement"
        elif not mw_shrinks and not mz_shrinks:
            direction = "away_from_measurement"
        else:
            direction = "mixed"
        verdict = {
            "primary_cell": primary_id,
            "status": "evaluated",
            "direction": direction,
            "landing": primary["landing"],
            "statement": (
                "toward supports the missing-correction reading of CL-5; "
                "away kills the pole-packet branch as declared; the rule was "
                "fixed in the spec before computation"
            ),
        }

    diagnostic_verdict = verdict
    physical_comparison = classify_physical_comparison(spec)
    if physical_comparison["status"] != "EVALUABLE":
        verdict = {
            "primary_cell": primary_id,
            "status": "not_evaluable",
            "direction": "not_evaluable",
            "landing": None,
            "statement": (
                "The numerical cells are internal diagnostics of one partial "
                "prescription. A physical W/Z residual or pull is forbidden "
                "until the readout contract closes."
            ),
            "internal_prescription_diagnostic": diagnostic_verdict,
        }

    landings = [c["id"] for c in cells if c["landing"]]
    wall = time.time() - started
    result = {
        "artifact": "oph_ew_pole_packet_results",
        "date": "2026-07-16",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ledger_row": "CL-5",
        "spec": str(SPEC_PATH.name),
        "spec_sha256": spec["spec_sha256"]["hexdigest"],
        "engine_certification": cert,
        "targets_GeV": {k: list(v) for k, v in targets.items()},
        "display_adapter": {
            "epsilon_Cs": epsilon_cs,
            "E_star_display_GeV": e_star,
        },
        "baseline_one_loop": {
            "alpha_U": d10.alpha_u,
            "mu_U_GeV": d10.mu_u,
            "mz_run_fixed_point_GeV": d10.mz_run,
            "alpha1_mz": d10.alpha1_mz,
            "alpha2_mz": d10.alpha2_mz,
            "alpha3_mz": d10.alpha3_mz,
            "v_over_E_star": v_over_e0,
            "cells": baseline_cells,
        },
        "stage5_internal_masses_GeV": dict(stage5),
        "diagnostics": diagnostics,
        "cells": cells,
        "gates_declared_open": gates_open,
        "gates_triggered": gates_triggered,
        "physical_comparison": physical_comparison,
        "summary": {
            "cells_emitted": len(cells),
            "cells_declared": 8,
            "landings": landings,
            "landing_count": len(landings),
            "verdict": verdict,
        },
        "wall_time_seconds": wall,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "cells_emitted": len(cells),
                "gates_triggered": [g["cell_group"] for g in gates_triggered],
                "landing_count": len(landings),
                "verdict_direction": verdict["direction"],
                "wall_time_seconds": round(wall, 2),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
