#!/usr/bin/env python3
"""Hybrid IR bracket diagnostic for the blind hadronic closure lane (G1).

Output class: diagnostic, non-promoting; comparison label
compare_only_non_blind; row_class diagnostic_non_promoting;
physical_claim false. The frozen v2 target and the protocol artifacts are
untouched: ``ward_projected_payload/`` is imported read-only and
``falsification/`` is not referenced.

Pipeline (all rules declared beforehand in the envelope spec, see
``code/particles/runs/hadron/hybrid_ir_bracket_envelope_spec_2026-07-16.json``):

1. Load the measured ensembles produced by
   ``run_hybrid_ensemble_measurement.py`` (quenched, seeded,
   deterministic).
2. Extract a*m_V, Z_V (conserved-local estimator), and the physical TMR
   t^2 moment; measure the matched free-field lattice reference and form
   S_IR with jackknife statistics.
3. Apply the declared multiplicative systematic envelope (quadrature).
4. Rebuild the frozen pqcd grid above-cutoff moments, replace the
   below-cutoff free/zero dichotomy with [S_IR_lo, S_IR_hi], and emit the
   hybrid s_effective bracket with the compare-only containment check
   against S_required.

Run:
    python3 run_hybrid_ir_bracket_diagnostic.py
writes code/particles/runs/hadron/hybrid_ir_bracket_diagnostic_2026-07-16.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from hybrid_ir_bracket import (  # noqa: E402  (also sets the payload path)
    apply_envelope,
    build_hybrid_rows,
    continuum_free_moment_context,
    effective_mass_windowed,
    estimate_s_ir,
    integrated_autocorrelation_time,
    kappa_free_for_vector_mass,
    physical_moment,
    zv_windowed,
)
from lattice_backend.vector_correlator import fold_correlator, tmr_moment  # noqa: E402
from run_hybrid_ensemble_measurement import measure_free  # noqa: E402

import payload_harness as ph  # noqa: E402  (read-only frozen import)

RUNS_DIR = HERE.parent / "runs" / "hadron"
SPEC_PATH = RUNS_DIR / "hybrid_ir_bracket_envelope_spec_2026-07-16.json"
OUT_PATH = RUNS_DIR / "hybrid_ir_bracket_diagnostic_2026-07-16.json"
NOTE_PATH = RUNS_DIR / "hybrid_ir_bracket_diagnostic_2026-07-16.md"
FROZEN_BRACKET_PATH = (
    HERE / "ward_projected_payload" / "runtime"
    / "ward_projected_payload_bracket_current.json")

S_REQUIRED_STR = "0.895400132647658797805800283181670641"
PASS_TOLERANCE_ALPHA_INV = 2.1e-8
PASS_TOLERANCE_REL_DELTA_HAD = 4.036126488247091e-09
FREE_SLOPE_DELTA_MV = 0.05


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def build_free_moment_model(
    shape: tuple[int, ...], c_sw: float, m_v_ref: float,
    delta: float = FREE_SLOPE_DELTA_MV, log=print,
) -> dict[str, float]:
    """Matched free-field physical moment and its linear m_V sensitivity."""
    def free_phys_moment(m_v: float) -> float:
        kappa_f = kappa_free_for_vector_mass(m_v)
        g = measure_free(shape, kappa_f, c_sw, out_path=None, log=log)
        return physical_moment(fold_correlator(g), kappa_f)

    center = free_phys_moment(m_v_ref)
    plus = free_phys_moment(m_v_ref + delta)
    minus = free_phys_moment(m_v_ref - delta)
    return {
        "m_v_ref": m_v_ref,
        "m_free_phys_ref": center,
        "dm_free_phys_dm_v": (plus - minus) / (2.0 * delta),
        "slope_delta_m_v": delta,
        "kappa_free_ref": kappa_free_for_vector_mass(m_v_ref),
    }


def analyze_ensemble(npz_path: Path, log=print) -> dict[str, Any]:
    """Chain statistics, spectroscopy, Z_V, moments, and S_IR per ensemble."""
    d = np.load(npz_path)
    kappa = float(d["kappa"])
    shape = tuple(int(v) for v in d["shape"])
    g_ll = d["g_ll"]
    g_cl = d["g_cl"]
    n_cfg = g_ll.shape[0]

    # Thermalization check: last 20 thermalization plaquettes vs chain scatter.
    therm = d["therm_plaquettes"]
    chain_plaq = d["plaquettes"]
    chain_mean = float(np.mean(chain_plaq))
    chain_std = float(np.std(chain_plaq, ddof=1))
    therm_tail_mean = float(np.mean(therm[-20:]))
    therm_ok = abs(therm_tail_mean - chain_mean) <= 2.0 * chain_std

    # Autocorrelation of the plaquette and of the per-config hopping moment.
    moments_per_cfg = np.array(
        [tmr_moment(fold_correlator(row), amz=None) for row in g_ll])
    tau_plaq = integrated_autocorrelation_time(chain_plaq)
    tau_moment = integrated_autocorrelation_time(moments_per_cfg)
    inflation = math.sqrt(2.0 * tau_moment) if tau_moment > 0.5 else 1.0

    folded_ll_mean = fold_correlator(g_ll.mean(axis=0))
    folded_cl_mean = fold_correlator(g_cl.mean(axis=0))
    m_v = effective_mass_windowed(folded_ll_mean)
    z_v, z_v_per_t = zv_windowed(folded_cl_mean, folded_ll_mean, kappa)
    m_ps = effective_mass_windowed(fold_correlator(d["g_pion"].mean(axis=0)))

    log(f"[{npz_path.name}] n_cfg={n_cfg} plaq={chain_mean:.5f} "
        f"am_V={m_v:.4f} am_PS={m_ps:.4f} Z_V={z_v:.4f} "
        f"tau_plaq={tau_plaq:.2f} tau_moment={tau_moment:.2f}")

    free_model = build_free_moment_model(shape, float(d["c_sw"]), m_v, log=log)
    s_ir = estimate_s_ir(g_ll, g_cl, kappa, free_model)
    stat_rel = abs(s_ir["errors"]["s_ir"] / s_ir["s_ir"]) * inflation

    return {
        "npz_file": npz_path.name,
        "ensemble_id": str(d["ensemble_id"]),
        "lattice_shape_TXYZ": list(shape),
        "beta": float(d["beta"]),
        "kappa": kappa,
        "c_sw": float(d["c_sw"]),
        "n_therm_sweeps": int(d["n_therm"]),
        "n_sep_sweeps": int(d["n_sep"]),
        "n_configs": n_cfg,
        "budget_truncation": str(d["budget_truncation"])
        if "budget_truncation" in d else "",
        "rng_seed": int(d["seed"]),
        "cg_tol": float(d["cg_tol"]),
        "max_cg_iterations": int(np.max(d["cg_iterations"])),
        "plaquette_mean": chain_mean,
        "plaquette_std": chain_std,
        "thermalization": {
            "n_therm_sweeps": int(d["n_therm"]),
            "therm_tail_mean_last20": therm_tail_mean,
            "chain_mean": chain_mean,
            "accepted": bool(therm_ok),
        },
        "autocorrelation": {
            "tau_int_plaquette": tau_plaq,
            "tau_int_moment": tau_moment,
            "error_inflation_factor": inflation,
        },
        "spectroscopy": {
            "am_vector_windowed": m_v,
            "am_vector_jackknife_error": s_ir["errors"]["m_v"],
            "am_pseudoscalar_windowed_context_only": m_ps,
        },
        "z_v": {
            "estimator": "conserved_local_over_2kappa_local_local",
            "windowed_mean": z_v,
            "jackknife_error": s_ir["errors"]["z_v"],
            "per_t_values": z_v_per_t,
            "values_outside_declared_range_0p2_1p2": [
                v for v in z_v_per_t if not (0.2 < v < 1.2)],
        },
        "moments": {
            "m_ll_hopping_units": tmr_moment(folded_ll_mean, amz=None),
            "m_ll_physical": s_ir["m_ll_phys"],
            "m_ll_physical_jackknife_error": s_ir["errors"]["m_ll_phys"],
            "relative_statistical_error_moment": float(
                abs(s_ir["errors"]["m_ll_phys"] / s_ir["m_ll_phys"])),
        },
        "free_reference": {
            **free_model,
            "continuum_infinite_volume_context_only":
                continuum_free_moment_context(m_v / 2.0, shape[0]),
        },
        "s_ir": {
            "central": s_ir["s_ir"],
            "jackknife_error": s_ir["errors"]["s_ir"],
            "relative_statistical_error_raw": float(
                abs(s_ir["errors"]["s_ir"] / s_ir["s_ir"])),
            "relative_statistical_error_inflated": stat_rel,
        },
        "correlator_folded_mean": folded_ll_mean.tolist(),
        "correlator_cl_folded_mean": folded_cl_mean.tolist(),
    }


def build_payload(
    ensemble_reports: dict[str, dict[str, Any]],
    central_key: str,
    *,
    precision: int = 40,
    log=print,
) -> dict[str, Any]:
    t_start = time.time()
    spec_bytes = SPEC_PATH.read_bytes()
    spec_sha = hashlib.sha256(spec_bytes).hexdigest()
    spec = json.loads(spec_bytes)

    frozen = json.loads(FROZEN_BRACKET_PATH.read_text(encoding="utf-8"))
    old_bracket = frozen["bracket"]["s_effective"]

    central = ensemble_reports[central_key]
    s_c = central["s_ir"]["central"]
    envelope = apply_envelope(
        s_c, central["s_ir"]["relative_statistical_error_inflated"])

    log("rebuilding evaluation point and frozen pqcd grid ...")
    ep = ph.build_evaluation_point(precision=precision)
    hybrid = build_hybrid_rows(
        ep, envelope["s_ir_lo"], envelope["s_ir_hi"])
    naive = hybrid["quark_delta_alpha_inv_naive"]
    new_lo = hybrid["s_effective_hybrid"]["lo"]
    new_hi = hybrid["s_effective_hybrid"]["hi"]
    new_width = hybrid["s_effective_hybrid"]["width"]

    s_required = float(S_REQUIRED_STR)
    inside = bool(new_lo <= s_required <= new_hi)
    distance_to_nearest_edge = min(abs(s_required - new_lo),
                                   abs(new_hi - s_required))
    width_delta_source = new_width * naive
    delta_had_central_grid = float(np.mean([
        r["delta_above_alpha_inv"] + s_c * r["delta_ir_free_alpha_inv"]
        for r in hybrid["rows"]]))

    payload: dict[str, Any] = {
        "artifact": "oph_hybrid_ir_bracket_diagnostic",
        "format_version": 1,
        "date_utc": "2026-07-16",
        "label": "compare_only_non_blind",
        "row_class": "diagnostic_non_promoting",
        "physical_claim": False,
        "guards": {
            "promotion_allowed": False,
            "public_promotion_allowed": False,
            "satisfies_issue_425_closure": False,
            "target_anchored": False,
            "frozen_v2_target_modified": False,
            "ward_projected_payload_modified": False,
            "falsification_modified": False,
        },
        "envelope_spec": {
            "file": SPEC_PATH.name,
            "sha256": spec_sha,
            "declared_before_evaluation": True,
            "embedded_copy": spec,
        },
        "old_bracket": {
            "artifact": FROZEN_BRACKET_PATH.name,
            "content_sha256": frozen["content_sha256"],
            "s_effective": old_bracket,
            "below_cutoff_treatment":
                "free-parton versus zero-support dichotomy (factor {0, 1})",
        },
        "lattice_ir_measurement": {
            "ensembles": ensemble_reports,
            "central_ensemble": central_key,
            "central_rule_applied": spec["ensembles"]["central_rule"],
            "declared_deviations": [
                "ensemble B (24x6^3, declared n_cfg 20, seed 716002) did "
                "not complete inside the wall-clock budget: the first "
                "attempt was restarted with a declared budget truncation "
                "to 10 configurations and the restarted process died at "
                "configuration 8 of 10 before its cache was written; no "
                "durable B data exists, so per the spec central rule "
                "ensemble A is central and B is absent from this artifact",
                "spec amendment hybrid_ir_bracket_envelope_spec_amendment_"
                "2026-07-16.json (sha256 382596e828b7bb259a253418d5ffc8bc"
                "611e0a06b61ebd693f666a03721f50ba): cosh effective mass in "
                "place of the plain log ratio, fixed from the free-field "
                "anchor before any interacting evaluation",
            ],
            "known_dilution_note": (
                "the pre-existing demo contraction (GAMMA[0..2]) carries a "
                "factor 2/3 temporal-channel dilution relative to the "
                "per-polarization transverse correlator; this analysis uses "
                "the three transverse channels GAMMA[1..3]"),
        },
        "s_ir_interval": envelope,
        "hybrid_bracket": {
            "construction": spec["bracket_construction"],
            "quark_delta_alpha_inv_naive": naive,
            "max_zero_free_identity_defect":
                hybrid["max_zero_free_identity_defect"],
            "rows": hybrid["rows"],
            "s_effective": {
                "lo": new_lo, "hi": new_hi, "width": new_width},
            "width_vs_old": {
                "old_width": old_bracket["width"],
                "new_width": new_width,
                "narrower_than_old": bool(new_width < old_bracket["width"]),
                "width_ratio_new_over_old":
                    new_width / old_bracket["width"],
            },
        },
        "containment_check": {
            "comparison": "compare_only_non_blind",
            "s_required": S_REQUIRED_STR,
            "s_required_float": s_required,
            "inside_hybrid_bracket": inside,
            "distance_to_nearest_edge": distance_to_nearest_edge,
            "old_bracket_contains_s_required": bool(
                old_bracket["lo"] <= s_required <= old_bracket["hi"]),
        },
        "distance_to_pass_tolerance": {
            "pass_tolerance_alpha_inv": PASS_TOLERANCE_ALPHA_INV,
            "pass_tolerance_relative_on_delta_had":
                PASS_TOLERANCE_REL_DELTA_HAD,
            "hybrid_width_delta_source_alpha_inv": width_delta_source,
            "width_over_tolerance":
                width_delta_source / PASS_TOLERANCE_ALPHA_INV,
            "hybrid_relative_width_on_delta_had":
                width_delta_source / delta_had_central_grid,
            "orders_of_magnitude_remaining": math.log10(
                width_delta_source / PASS_TOLERANCE_ALPHA_INV),
        },
        "evaluation_point": ep.to_json(),
        "external_inputs_used_in_computation": False,
    }
    payload["content_sha256"] = hashlib.sha256(
        _canonical_json(payload).encode("utf-8")).hexdigest()
    payload["volatile"] = {
        "generated_utc": _now_utc(),
        "runtime_seconds": round(time.time() - t_start, 1),
        "machine": f"{platform.node()} {platform.machine()} "
                   f"python{platform.python_version()}",
        "note": "excluded from content_sha256",
    }
    return payload


def write_note(payload: dict[str, Any], path: Path) -> None:
    env = payload["s_ir_interval"]
    hyb = payload["hybrid_bracket"]
    cont = payload["containment_check"]
    dist = payload["distance_to_pass_tolerance"]
    ens = payload["lattice_ir_measurement"]["ensembles"]
    lines = [
        "# Hybrid IR bracket diagnostic, 2026-07-16",
        "",
        "Label: compare_only_non_blind. row_class diagnostic_non_promoting,",
        "physical_claim false. The frozen v2 target, the payload grid, and",
        "the protocol artifacts are unmodified; every analysis choice was",
        "declared and hashed in the envelope spec before evaluation",
        f"(sha256 {payload['envelope_spec']['sha256']}).",
        "",
        "## Measurement",
        "",
    ]
    for key, rep in ens.items():
        s = rep["s_ir"]
        lines.append(
            f"- Ensemble {key} ({rep['ensemble_id']}): "
            f"{rep['n_configs']} cfgs, plaquette {rep['plaquette_mean']:.5f}, "
            f"a*m_V = {rep['spectroscopy']['am_vector_windowed']:.4f}, "
            f"Z_V = {rep['z_v']['windowed_mean']:.4f}, moment stat. "
            f"{100 * rep['moments']['relative_statistical_error_moment']:.1f}%, "
            f"S_IR = {s['central']:.4f} +- {s['jackknife_error']:.4f}.")
    lines += [
        "",
        f"Central ensemble: {payload['lattice_ir_measurement']['central_ensemble']}.",
        f"Envelope (quadrature, declared first): E_total = {env['e_total']:.4f};",
        f"S_IR interval [{env['s_ir_lo']:.4f}, {env['s_ir_hi']:.4f}].",
        "",
        "## Bracket",
        "",
        f"- Old S_eff bracket: [{payload['old_bracket']['s_effective']['lo']:.6f}, "
        f"{payload['old_bracket']['s_effective']['hi']:.6f}], width "
        f"{payload['old_bracket']['s_effective']['width']:.6f}.",
        f"- Hybrid S_eff bracket: [{hyb['s_effective']['lo']:.6f}, "
        f"{hyb['s_effective']['hi']:.6f}], width {hyb['s_effective']['width']:.6f} "
        f"({'narrower' if hyb['width_vs_old']['narrower_than_old'] else 'wider'} "
        f"than old by factor "
        f"{hyb['width_vs_old']['width_ratio_new_over_old']:.3f}).",
        f"- S_required = {cont['s_required_float']:.12f}: "
        f"{'inside' if cont['inside_hybrid_bracket'] else 'OUTSIDE'} the hybrid "
        f"bracket; distance to nearest edge {cont['distance_to_nearest_edge']:.4f}.",
        "",
        "## Distance to the pass tolerance",
        "",
        f"The hybrid bracket width in Delta_source units is "
        f"{dist['hybrid_width_delta_source_alpha_inv']:.4f} alpha^-1 against the "
        f"{dist['pass_tolerance_alpha_inv']:.1e} pass tolerance: a factor "
        f"{dist['width_over_tolerance']:.3e}, i.e. "
        f"{dist['orders_of_magnitude_remaining']:.1f} orders of magnitude remain "
        f"to the 4e-9 relative pass tolerance on Delta_had.",
        "",
        "## Deviations and dominant limitation",
        "",
    ]
    for dev in payload["lattice_ir_measurement"].get("declared_deviations", []):
        lines.append(f"- {dev}")
    central = ens[payload["lattice_ir_measurement"]["central_ensemble"]]
    lines += [
        "",
        "The TMR moment itself reached "
        f"{100 * central['moments']['relative_statistical_error_moment']:.1f}% "
        "statistical precision (demo lane: 21.6% on the diluted contraction).",
        "The S_IR statistical error is instead dominated by the vector-mass",
        "matching jitter (a*m_V = "
        f"{central['spectroscopy']['am_vector_windowed']:.3f} +- "
        f"{central['spectroscopy']['am_vector_jackknife_error']:.3f}, with the "
        "vector channel entering noise at t >= 6 on this volume) and by the",
        "Z_V window contamination, both propagated through the declared",
        "jackknife. At this diagnostic scale the envelope clamps S_IR_lo at",
        "zero, so the hybrid lower edge coincides with the old zero-support",
        "edge and the upper edge exceeds the old free-parton edge: the",
        "measured IR treatment is currently WIDER than the dichotomy it",
        "replaces. The declared route to a narrower interval is a longer",
        "time extent and larger spatial volume (the abandoned ensemble B",
        "geometry) plus a smeared vector source for an earlier plateau.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ensemble-a", default=str(
        RUNS_DIR / "hybrid_ir_ensembleA_2026-07-16.npz"))
    parser.add_argument("--ensemble-b", default=str(
        RUNS_DIR / "hybrid_ir_ensembleB_2026-07-16.npz"))
    parser.add_argument("--output", default=str(OUT_PATH))
    parser.add_argument("--note", default=str(NOTE_PATH))
    args = parser.parse_args()

    reports: dict[str, dict[str, Any]] = {}
    central_key = None
    path_b = Path(args.ensemble_b)
    path_a = Path(args.ensemble_a)
    if path_a.exists():
        reports["A"] = analyze_ensemble(path_a)
        central_key = "A"
    if path_b.exists():
        reports["B"] = analyze_ensemble(path_b)
        central_key = "B"
    if not reports:
        print("no ensemble caches found", file=sys.stderr)
        return 1

    payload = build_payload(reports, central_key)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
        f.write("\n")
    write_note(payload, Path(args.note))
    print(f"wrote {out}")
    print(f"wrote {args.note}")
    print(json.dumps({
        "s_ir_interval": [payload["s_ir_interval"]["s_ir_lo"],
                          payload["s_ir_interval"]["s_ir_hi"]],
        "hybrid_s_effective": payload["hybrid_bracket"]["s_effective"],
        "old_s_effective": payload["old_bracket"]["s_effective"],
        "s_required_inside": payload["containment_check"]["inside_hybrid_bracket"],
        "width_over_tolerance":
            payload["distance_to_pass_tolerance"]["width_over_tolerance"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
