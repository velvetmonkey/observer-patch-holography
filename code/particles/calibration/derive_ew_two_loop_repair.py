#!/usr/bin/env python3
"""Preregistered CL-5 two-loop prescription diagnostic for the W/Z chart.

Executes falsification/preregistered/ew_two_loop_repair_spec_2026-07-16.json
and emits code/particles/runs/calibration/ew_two_loop_repair_2026-07-16.json.

The numerical packet grafts onto the one-loop transport between mz_run and
mu_U the Standard Model two-loop increment of
sm_two_loop_rge_engine (SM field content, Buttazzo et al. 1307.3536
benchmark). Every other chain object is retained exactly. All branches are
discrete, declared in the spec before any two-loop lane number existed, and
all are emitted. The script fails closed if the spec hash does not verify,
if the baseline chain does not reproduce the frozen one-loop pair, or if any
declared solver loses convergence. Because the baseline uses MSSM one-loop
coefficients and the packet omits MSSM two-loop coefficients and thresholds,
this is a hybrid diagnostic. It marks the physical comparison NOT_EVALUABLE
while any readout-identification gate remains open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

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
    from calibration import sm_two_loop_rge_engine as engine
except ModuleNotFoundError:
    from derive_wzh_residual_elimination_boundary import (
        strict_branch_two_law_evaluation,
    )
    import sm_two_loop_rge_engine as engine

try:
    from calibration.ew_physical_readout_gate import classify_physical_comparison
except ModuleNotFoundError:
    from ew_physical_readout_gate import classify_physical_comparison

SPEC_PATH = (
    REPO / "falsification" / "preregistered"
    / "ew_two_loop_repair_spec_2026-07-16.json"
)
DEFAULT_OUT = (
    ROOT / "particles" / "runs" / "calibration"
    / "ew_two_loop_repair_2026-07-16.json"
)
CLOCK_CERT = (
    ROOT / "particles" / "hierarchy" / "certificates"
    / "R_gamma_noG_DAG_certificate.json"
)

N_STEPS = 8000
NEWTON_MAX_ITER = 40
NEWTON_TOL = 1e-10
NEWTON_GUESS = (0.95, 0.13)
ALPHA_U_WINDOW = (0.02, 0.08)
ALPHA_U_SCAN_POINTS = 41
BISECTION_ITERATIONS = 90
DELTA_RHO_STAGE3 = 3.0 / (32.0 * math.pi**2)
BASELINE_MATCH_RTOL = 1e-9


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


def gauge_state(alpha1: float, alpha2: float, alpha3: float) -> tuple[float, float, float]:
    """(g1, g2, g3) engine state from lane alphas; alpha1 is GUT-normalized."""

    return (
        math.sqrt(4.0 * math.pi * alpha1),
        math.sqrt(4.0 * math.pi * alpha2),
        math.sqrt(4.0 * math.pi * alpha3),
    )


def newton_ytcs(
    g123: tuple[float, float, float],
    lnmu0: float,
    lnmu1: float,
    guess: tuple[float, float],
) -> tuple[float, float, dict]:
    """Shoot (yt, lam) at mz_run so that the loops=2 endpoint satisfies the
    lane D11 boundary: yt(mu_U) on the critical surface, lam(mu_U) = 0."""

    def residuals(yt0: float, lam0: float) -> tuple[float, float]:
        g1u, g2u, g3u, ytu, lamu = engine.run(
            (*g123, yt0, lam0), lnmu0, lnmu1, n_steps=N_STEPS, loops=2
        )
        gy_u = math.sqrt(3.0 / 5.0) * g1u
        return ytu - pm.critical_surface_yukawa(gy_u, g2u), lamu

    yt0, lam0 = guess
    r = residuals(yt0, lam0)
    norm = max(abs(r[0]), abs(r[1]))
    iterations = 0
    while norm > NEWTON_TOL and iterations < NEWTON_MAX_ITER:
        iterations += 1
        h_yt = max(1e-8, abs(yt0) * 1e-6)
        h_lam = max(1e-8, abs(lam0) * 1e-6)
        r_yt = residuals(yt0 + h_yt, lam0)
        r_lam = residuals(yt0, lam0 + h_lam)
        j00 = (r_yt[0] - r[0]) / h_yt
        j01 = (r_lam[0] - r[0]) / h_lam
        j10 = (r_yt[1] - r[1]) / h_yt
        j11 = (r_lam[1] - r[1]) / h_lam
        det = j00 * j11 - j01 * j10
        if det == 0.0:
            break
        d_yt = -(r[0] * j11 - r[1] * j01) / det
        d_lam = -(j00 * r[1] - j10 * r[0]) / det
        step = 1.0
        while step > 1.0 / 1024.0:
            cand = (yt0 + step * d_yt, lam0 + step * d_lam)
            rc = residuals(*cand)
            nc = max(abs(rc[0]), abs(rc[1]))
            if nc < norm:
                yt0, lam0 = cand
                r, norm = rc, nc
                break
            step *= 0.5
        else:
            break
    record = {
        "iterations": iterations,
        "residual_max_norm": norm,
        "converged": norm <= NEWTON_TOL,
        "yt_at_mz": yt0,
        "lam_at_mz": lam0,
    }
    return yt0, lam0, record


def two_loop_increments(
    alpha1: float,
    alpha2: float,
    alpha3: float,
    mz_run: float,
    mu_u: float,
    branch: str,
    guess: tuple[float, float],
) -> dict:
    """Certified two-loop transport increments Delta_i on invalpha at mu_U.

    Both integrations share the same boundary at mz_run; the difference of
    the loops=2 and loops=1 endpoints isolates the two-loop terms.
    """

    g123 = gauge_state(alpha1, alpha2, alpha3)
    lnmu0, lnmu1 = math.log(mz_run), math.log(mu_u)
    if branch == "ytcs":
        yt0, lam0, newton = newton_ytcs(g123, lnmu0, lnmu1, guess)
        if not newton["converged"]:
            return {"gated": True, "gate": "newton_unconverged", "newton": newton}
    elif branch == "yt0":
        yt0, lam0 = 0.0, 0.0
        newton = None
    else:
        raise ValueError(f"unknown branch {branch}")

    boundary = (*g123, yt0, lam0)
    end2 = engine.run(boundary, lnmu0, lnmu1, n_steps=N_STEPS, loops=2)
    end1 = engine.run(boundary, lnmu0, lnmu1, n_steps=N_STEPS, loops=1)

    def inv_alpha(g: float) -> float:
        return 4.0 * math.pi / (g * g)

    delta = [inv_alpha(end2[i]) - inv_alpha(end1[i]) for i in range(3)]
    out = {
        "gated": False,
        "delta_invalpha": {"alpha1": delta[0], "alpha2": delta[1], "alpha3": delta[2]},
        "boundary_yt_lam_at_mz": [yt0, lam0],
        "endpoint_two_loop_g": list(end2),
        "endpoint_one_loop_g": list(end1),
    }
    if newton is not None:
        out["newton"] = newton
    return out


def apply_increments(
    alpha1: float, alpha2: float, alpha3: float, delta: dict
) -> tuple[float, float, float]:
    """invalpha_repaired(mz) = invalpha_lane(mz) - Delta_i."""

    rep = []
    for name, alpha in (("alpha1", alpha1), ("alpha2", alpha2), ("alpha3", alpha3)):
        inv = 1.0 / alpha - delta[name]
        if inv <= 0.0:
            raise OverflowError(f"repaired {name} past its pole")
        rep.append(1.0 / inv)
    return tuple(rep)


def emit_cells(
    tier: str,
    branch: str,
    alpha_u: float,
    a2_rep: float,
    ay_rep: float,
    v_over_e: float,
    e_star: float,
    targets: dict,
    baseline_cells: dict | None,
) -> tuple[list[dict], dict]:
    """Evaluate the retained two-law readout on the repaired basis."""

    sin2 = ay_rep / (ay_rep + a2_rep)
    eta = alpha_u * (1.0 - 2.0 * sin2)
    two = strict_branch_two_law_evaluation(a2_rep, ay_rep, eta, v_over_e)
    cells = []
    for law_id in ("zero_selector", "nonzero_carrier"):
        law = two[f"{law_id}_law"]
        mw_base = law["MW_over_E_star"] * e_star
        mz_base = law["MZ_over_E_star"] * e_star
        for z_id in ("z_tree", "z_stage3"):
            mw = mw_base
            mz = mz_base
            if z_id == "z_stage3":
                mz = mz / math.sqrt(1.0 + DELTA_RHO_STAGE3)
            mw_target, mw_sigma = targets["MW"]
            mz_target, mz_sigma = targets["MZ"]
            cell = {
                "id": f"tier={tier}|yukawa={branch}|law={law_id}|z={z_id}",
                "MW_GeV": mw,
                "MZ_GeV": mz,
                "MW_offset_GeV": mw - mw_target,
                "MZ_offset_GeV": mz - mz_target,
                "MW_pull_sigma": (mw - mw_target) / mw_sigma,
                "MZ_pull_sigma": (mz - mz_target) / mz_sigma,
                "landing": (
                    abs(mw - mw_target) <= mw_sigma
                    and abs(mz - mz_target) <= mz_sigma
                ),
            }
            if baseline_cells is not None:
                base = baseline_cells[f"{law_id}|{z_id}"]
                cell["shift_from_baseline_MW_GeV"] = mw - base["MW_GeV"]
                cell["shift_from_baseline_MZ_GeV"] = mz - base["MZ_GeV"]
            cells.append(cell)
    basis = {
        "alpha_u": alpha_u,
        "alpha2_repaired": a2_rep,
        "alphaY_repaired": ay_rep,
        "sin2_theta_repaired": sin2,
        "eta_source_repaired": eta,
        "v_over_E_star": v_over_e,
    }
    return cells, basis


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
    epsilon_cs, e_star = e_star_display_gev()

    # Engine certification gate: fail closed if the benchmark breaks.
    cert = engine.validate()
    if not cert["all_ok"]:
        raise SystemExit("engine certification failed; fail closed")

    # Baseline one-loop chain, reproduced and matched against the spec.
    d10 = pm.build_paper_d10(pix_area=p_value, n_c=n_c)
    ay0 = 0.6 * d10.alpha1_mz
    a20 = d10.alpha2_mz
    sin2_0 = ay0 / (ay0 + a20)
    eta0 = d10.alpha_u * (1.0 - 2.0 * sin2_0)
    v_over_e0 = math.exp(
        -2.0 * math.pi / (beta_ew * d10.alpha_u)
    ) / math.sqrt(p_value)
    two0 = strict_branch_two_law_evaluation(a20, ay0, eta0, v_over_e0)

    expected = base_spec["recomputed_and_matched_against_frozen_results"]
    mw0 = two0["zero_selector_law"]["MW_over_E_star"] * e_star
    mz0 = two0["zero_selector_law"]["MZ_over_E_star"] * e_star
    checks = {
        "alpha_U": (d10.alpha_u, expected["alpha_U"]),
        "mu_U_GeV": (d10.mu_u, expected["mu_U_GeV"]),
        "mz_run_fixed_point_GeV": (d10.mz_run, expected["mz_run_fixed_point_GeV"]),
        "MW_zero_selector_GeV": (mw0, expected["MW_zero_selector_GeV"]),
        "MZ_zero_selector_GeV": (mz0, expected["MZ_zero_selector_GeV"]),
    }
    for name, (got, want) in checks.items():
        if abs(got - want) > BASELINE_MATCH_RTOL * max(1.0, abs(want)):
            raise SystemExit(
                f"baseline mismatch on {name}: got {got!r}, spec {want!r}; "
                "fail closed"
            )

    baseline_cells = {}
    for law_id in ("zero_selector", "nonzero_carrier"):
        law = two0[f"{law_id}_law"]
        for z_id in ("z_tree", "z_stage3"):
            mz = law["MZ_over_E_star"] * e_star
            if z_id == "z_stage3":
                mz = mz / math.sqrt(1.0 + DELTA_RHO_STAGE3)
            baseline_cells[f"{law_id}|{z_id}"] = {
                "MW_GeV": law["MW_over_E_star"] * e_star,
                "MZ_GeV": mz,
            }

    gates_open = list(spec["fail_closed_gates_declared_open"])
    gates_triggered: list[dict] = []
    diagnostics: dict[str, object] = {}
    cells: list[dict] = []

    # ------------------------------------------------------------------
    # Tier A: readout shift at the frozen baseline alpha_U.
    # ------------------------------------------------------------------
    for branch in ("ytcs", "yt0"):
        inc = two_loop_increments(
            d10.alpha1_mz,
            d10.alpha2_mz,
            d10.alpha3_mz,
            d10.mz_run,
            d10.mu_u,
            branch,
            NEWTON_GUESS,
        )
        diag_key = f"tier_A|{branch}"
        diagnostics[diag_key] = inc
        if inc["gated"]:
            gates_triggered.append({"cell_group": diag_key, "gate": inc["gate"]})
            continue
        a1r, a2r, a3r = apply_increments(
            d10.alpha1_mz, d10.alpha2_mz, d10.alpha3_mz, inc["delta_invalpha"]
        )
        diagnostics[diag_key]["repaired_couplings_at_mz_run"] = {
            "alpha1": a1r,
            "alpha2": a2r,
            "alpha3": a3r,
        }
        tier_cells, basis = emit_cells(
            "A_readout_shift",
            branch,
            d10.alpha_u,
            a2r,
            0.6 * a1r,
            v_over_e0,
            e_star,
            targets,
            baseline_cells,
        )
        diagnostics[diag_key]["repaired_basis"] = basis
        cells.extend(tier_cells)

    # ------------------------------------------------------------------
    # Tier B: full re-solve of alpha_U on the repaired pixel residual.
    # ------------------------------------------------------------------
    import numpy as np

    for branch in ("ytcs", "yt0"):
        diag_key = f"tier_B|{branch}"
        cache: dict[float, tuple] = {}
        warm = {"guess": NEWTON_GUESS}

        def repaired_state(alpha_u: float, _branch=branch, _cache=cache, _warm=warm):
            if alpha_u in _cache:
                return _cache[alpha_u]
            mz_run, v_ev, a1, a2, a3 = pm.solve_mz_fixed_point_tree(
                alpha_u, p_value, n_c, d10.mu_u
            )
            inc = two_loop_increments(
                a1, a2, a3, mz_run, d10.mu_u, _branch, _warm["guess"]
            )
            if inc["gated"]:
                raise RuntimeError(f"increment gated: {inc['gate']}")
            if _branch == "ytcs":
                _warm["guess"] = tuple(inc["boundary_yt_lam_at_mz"])
            a1r, a2r, a3r = apply_increments(a1, a2, a3, inc["delta_invalpha"])
            residual = pm.pixel_residual(a2r, a3r, p_value)
            state = (residual, mz_run, a1r, a2r, a3r, inc)
            _cache[alpha_u] = state
            return state

        def residual_of(alpha_u: float) -> float:
            return repaired_state(alpha_u)[0]

        scan_rows = []
        bracket = None
        last = None
        try:
            for x in np.linspace(*ALPHA_U_WINDOW, ALPHA_U_SCAN_POINTS):
                x = float(x)
                try:
                    rx = residual_of(x)
                except (RuntimeError, OverflowError, ValueError) as exc:
                    scan_rows.append({"alpha_U": x, "status": f"{type(exc).__name__}: {exc}"})
                    last = None
                    continue
                scan_rows.append({"alpha_U": x, "pixel_residual": rx})
                if last is not None and rx * last[1] < 0:
                    bracket = (last[0], x)
                    break
                last = (x, rx)
        except Exception as exc:  # recorded, branch gated
            gates_triggered.append(
                {"cell_group": diag_key, "gate": f"scan_failed: {exc}"}
            )
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
        for _ in range(BISECTION_ITERATIONS):
            mid = 0.5 * (lo + hi)
            if mid == lo or mid == hi:
                break
            if residual_of(lo) * residual_of(mid) <= 0:
                hi = mid
            else:
                lo = mid
        alpha_u_star = 0.5 * (lo + hi)
        residual, mz_run_star, a1r, a2r, a3r, inc = repaired_state(alpha_u_star)
        v_over_e_star = math.exp(
            -2.0 * math.pi / (beta_ew * alpha_u_star)
        ) / math.sqrt(p_value)
        diagnostics[diag_key].update(
            {
                "gated": False,
                "alpha_U_two_loop": alpha_u_star,
                "alpha_U_shift_from_baseline": alpha_u_star - d10.alpha_u,
                "pixel_residual_at_root": residual,
                "mz_run_fixed_point_GeV": mz_run_star,
                "v_over_E_star_two_loop": v_over_e_star,
                "v_over_E_star_shift_relative": v_over_e_star / v_over_e0 - 1.0,
                "delta_invalpha": inc["delta_invalpha"],
                "boundary_yt_lam_at_mz": inc["boundary_yt_lam_at_mz"],
                "newton": inc.get("newton"),
                "repaired_couplings_at_mz_run": {
                    "alpha1": a1r,
                    "alpha2": a2r,
                    "alpha3": a3r,
                },
            }
        )
        tier_cells, basis = emit_cells(
            "B_full_resolve",
            branch,
            alpha_u_star,
            a2r,
            0.6 * a1r,
            v_over_e_star,
            e_star,
            targets,
            baseline_cells,
        )
        diagnostics[diag_key]["repaired_basis"] = basis
        cells.extend(tier_cells)

    # ------------------------------------------------------------------
    # Verdict on the primary display cell.
    # ------------------------------------------------------------------
    primary_id = "tier=B_full_resolve|yukawa=ytcs|law=zero_selector|z=z_tree"
    primary = next((c for c in cells if c["id"] == primary_id), None)
    base = baseline_cells["zero_selector|z_tree"]
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
                "away kills this repair branch; the rule was fixed in the "
                "spec before computation"
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
                "The numerical cells are internal diagnostics of the declared "
                "MSSM-one-loop plus SM-two-loop hybrid. A physical W/Z residual "
                "or pull is forbidden until the readout contract closes."
            ),
            "internal_prescription_diagnostic": diagnostic_verdict,
        }

    landings = [c["id"] for c in cells if c["landing"]]
    wall = time.time() - started
    result = {
        "artifact": "oph_ew_two_loop_repair_results",
        "date": "2026-07-16",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ledger_row": "CL-5",
        "spec": str(SPEC_PATH.name),
        "spec_sha256": spec["spec_sha256"]["hexdigest"],
        "engine_certification": {
            "all_ok": cert["all_ok"],
            "endpoint_ok": cert["endpoint_ok"],
        },
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
        "diagnostics": diagnostics,
        "cells": cells,
        "gates_declared_open": gates_open,
        "gates_triggered": gates_triggered,
        "physical_comparison": physical_comparison,
        "summary": {
            "cells_emitted": len(cells),
            "cells_declared": 16,
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
