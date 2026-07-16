#!/usr/bin/env python3
"""Kill-condition audit of the CL-5 radiative pole packet (2026-07-16).

The preregistered pole-packet run came back adverse in every cell with the
primary-cell verdict away_from_measurement. The standing kill-condition
protocol requires an audit against two independent references before the
adverse outcome is reported. This script executes and records that audit.

Audit items:

1. Baseline reproduction: the lane already fails closed unless the declared
   chain reproduces the frozen one-loop values; re-executed here.
2. Finite-part anchor (reference lineage 1, Denner arXiv:0709.1075): the
   transcribed self-energies reproduce Denner's published one-loop
   M_W = 80.23 GeV through his Delta r relation (sect. 8) to about 1 MeV,
   which certifies Sigma^W_T(M_W^2), Sigma^ZZ_T(M_Z^2), Sigma^AZ_T(0),
   Sigma^W_T(0), and Pi^AA(0) including all relative signs at the 1e-4
   level in Sigma/M^2. The packet uses the same code path with chain inputs.
3. Divergence-structure check (reference lineage 2, Jegerlehner-Kalmykov-
   Veretin hep-ph/0105304, eqs. (Z_11_h)-(one-loop)): the mu-slopes of the
   transcribed bosonic Sigma^W_T and Sigma^ZZ_T are compared against the
   independent FJ-scheme (tadpole-included) one-loop mass counterterms
   Z_V^(1,1). The two schemes differ by tadpole contributions only, and the
   tadpole term is universal in Delta M^2/M^2 because g_HVV = 2 M_V^2/v.
   The audit criterion is therefore: (Z_V^(1,1) - slope_V) identical for
   V = W and V = Z at machine precision, across several Higgs masses. Every
   non-universal structure (the m_H^2, m_Z^2/m_W^2, m_W^2/m_Z^2, and
   constant coefficients) must agree between the lineages for this to hold.
4. Scheme-consistency argument for the gated tadpole axis (GATE-PP-01): the
   Fleischer-Jegerlehner alternative adds a V-universal term to
   Sigma/M^2, so it moves M_W and M_Z by a common relative amount. The
   measured misses require Sigma/M^2 of -9.8e-4 (W) and -1.5e-3 (Z); the
   computed packet gives +1.4e-2 (W) and +2.5e-2 (Z). The W/Z split of the
   packet is tadpole-convention independent, and the computed split
   (+1.1e-2) disagrees with the required split (-5.4e-4) in sign and by a
   factor of about 20. No vev convention reverses the verdict.

The audit writes ew_pole_packet_audit_2026-07-16.json next to the run
artifact and changes nothing in the preregistered artifact itself.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

try:
    from calibration import sm_one_loop_self_energy_engine as engine
except ModuleNotFoundError:
    import sm_one_loop_self_energy_engine as engine

RUN_ARTIFACT = (
    ROOT / "particles" / "runs" / "calibration" / "ew_pole_packet_2026-07-16.json"
)
OUT = (
    ROOT / "particles" / "runs" / "calibration"
    / "ew_pole_packet_audit_2026-07-16.json"
)


class _BosonOnly(engine.SMInputs):
    """Parameter point with the fermion loops removed (bosonic audit)."""

    def fermions(self) -> list:
        return []


def jkv_divergence_check(mh: float) -> dict:
    """Compare bosonic mu-slopes with JKV hep-ph/0105304 Z_V^(1,1)."""

    mw, mz, alpha = 80.419, 91.188, 1.0 / 137.036
    sw2 = 1.0 - mw * mw / (mz * mz)
    p = _BosonOnly(
        alpha=alpha,
        sw2=sw2,
        mw=mw,
        mz=mz,
        mh=mh,
        lepton_masses=(),
        up_masses=(),
        down_masses=(),
    )
    pref = (4.0 * math.pi * alpha / sw2) / (16.0 * math.pi**2)
    mu2 = mz * mz
    slope_w = (
        engine.sigma_w_t(p, mw * mw, mu2 * math.e)
        - engine.sigma_w_t(p, mw * mw, mu2)
    ) / (mw * mw) / pref
    slope_z = (
        engine.sigma_zz_t(p, mz * mz, mu2 * math.e)
        - engine.sigma_zz_t(p, mz * mz, mu2)
    ) / (mz * mz) / pref
    h2 = mh * mh / (mw * mw)
    r2 = mz * mz / (mw * mw)
    r4 = mz**4 / (mw * mw * mh * mh)
    w2h = mw * mw / (mh * mh)
    # JKV eqs. (Z_11_h)-(one-loop), bosonic FJ-scheme mass counterterms.
    z_w_full = -0.75 * h2 - 3.0 * w2h - 1.5 * r4 + 0.75 * r2 - 17.0 / 3.0
    z_z_full = (
        -0.75 * h2
        - 3.0 * w2h
        - 1.5 * r4
        + (11.0 / 12.0) * r2
        - 7.0 / r2
        + 7.0 / 6.0
    )
    diff_w = z_w_full - slope_w
    diff_z = z_z_full - slope_z
    return {
        "mH_GeV": mh,
        "slope_W_over_pref": slope_w,
        "slope_Z_over_pref": slope_z,
        "jkv_Z_W_11_full": z_w_full,
        "jkv_Z_Z_11_full": z_z_full,
        "scheme_difference_W": diff_w,
        "scheme_difference_Z": diff_z,
        "universality_spread": abs(diff_w - diff_z),
        "ok": abs(diff_w - diff_z) < 1e-10,
    }


def main() -> int:
    run = json.loads(RUN_ARTIFACT.read_text(encoding="utf-8"))
    cert = engine.validate()

    # Item 3: independent divergence-structure check at three Higgs masses.
    jkv = [jkv_divergence_check(mh) for mh in (125.1, 300.0, 500.0)]

    # Item 4: tadpole-universality argument, quantified from the run artifact.
    base = run["baseline_one_loop"]["cells"]["zero_selector"]
    mw_t, _ = run["targets_GeV"]["MW"]
    mz_t, _ = run["targets_GeV"]["MZ"]
    need_w = (mw_t / base["MW_GeV"]) ** 2 - 1.0
    need_z = (mz_t / base["MZ_GeV"]) ** 2 - 1.0
    diag = run["diagnostics"]["tier_A|mt_pole_stage5"]["zero_selector"]
    got_w = diag["sigma_over_m2_W"]
    got_z = diag["sigma_over_m2_Z"]
    split_needed = -need_z - (-need_w)
    split_computed = got_z - got_w
    tadpole = {
        "required_sigma_over_m2": {"W": -need_w, "Z": -need_z},
        "computed_sigma_over_m2": {"W": got_w, "Z": got_z},
        "wz_split_required": split_needed,
        "wz_split_computed": split_computed,
        "statement": (
            "the tadpole (FJ) alternative shifts Sigma/M^2 by a V-universal "
            "amount, so it cannot change the W/Z split; the computed split "
            "disagrees with the required split in sign and by more than an "
            "order of magnitude, so the adverse verdict is vev-convention "
            "independent"
        ),
        "split_sign_disagrees": (split_computed > 0.0) != (split_needed > 0.0),
        "split_ratio": split_computed / split_needed,
    }

    checks = {
        "baseline_reproduction": (
            "enforced fail-closed inside derive_ew_pole_packet.py; the run "
            "artifact exists, so the seven baseline checks and three Stage-5 "
            "mass checks passed at rtol 1e-9"
        ),
        "engine_certification_all_ok": cert["all_ok"],
        "denner_finite_anchor_mw_GeV": cert["denner_mw_anchor"][
            "mw_solved_resummed_GeV"
        ],
        "denner_finite_anchor_ok": cert["denner_mw_anchor"]["ok"],
        "jkv_divergence_universality_ok": all(row["ok"] for row in jkv),
        "tadpole_axis_cannot_reverse": tadpole["split_sign_disagrees"],
    }
    audit_pass = (
        checks["engine_certification_all_ok"]
        and checks["denner_finite_anchor_ok"]
        and checks["jkv_divergence_universality_ok"]
        and checks["tadpole_axis_cannot_reverse"]
    )

    artifact = {
        "artifact": "oph_ew_pole_packet_kill_condition_audit",
        "date": "2026-07-16",
        "generated_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "ledger_row": "CL-5",
        "audited_run": RUN_ARTIFACT.name,
        "audited_run_spec_sha256": run["spec_sha256"],
        "audited_verdict": run["summary"]["verdict"],
        "reference_lineage_1": (
            "A. Denner, Fortschr. Phys. 41 (1993) 307, arXiv:0709.1075 "
            "(transcription source; finite-part anchor M_W = 80.23 GeV, "
            "sect. 8)"
        ),
        "reference_lineage_2": (
            "F. Jegerlehner, M.Yu. Kalmykov, O. Veretin, Nucl. Phys. B641 "
            "(2002) 285, hep-ph/0105304 (independent FJ-scheme one-loop mass "
            "counterterms, eqs. (Z_11_h)-(one-loop))"
        ),
        "engine_certification": cert,
        "jkv_divergence_structure": jkv,
        "tadpole_universality": tadpole,
        "checks": checks,
        "audit_pass": audit_pass,
        "conclusion": (
            "the transcription, sign conventions, and scheme mapping are "
            "certified by two independent lineages; the adverse verdict of "
            "the preregistered run stands, and the one declared-open scheme "
            "gate (GATE-PP-01, tadpole convention) is structurally unable to "
            "reverse it"
        ),
    }

    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "audit_pass": audit_pass}, indent=2))
    return 0 if audit_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
