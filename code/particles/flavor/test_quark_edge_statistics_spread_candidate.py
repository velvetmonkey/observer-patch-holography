import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "flavor" / "derive_quark_edge_statistics_spread_candidate.py"
OUTPUT = ROOT / "particles" / "runs" / "flavor" / "quark_edge_statistics_spread_candidate.json"


def test_quark_edge_statistics_spread_candidate_is_explicit_and_near_current_pair() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["artifact"] == "oph_quark_edge_statistics_spread_candidate"
    assert payload["bridge_status"] == "candidate_only"
    assert payload["candidate_kind"] == "shared_edge_suppression_plus_ordered_gap"
    assert payload["edge_statistics_inputs"]["shared_seed_matches_cocycle"] is True
    assert payload["candidate_formulas"]["sigma_u_total_log_per_side"] == "S_13 + rho_ord * delta21 / (1 + rho_ord)"
    assert payload["candidate_formulas"]["sigma_d_total_log_per_side"] == "S_23 + delta21 / (2 * (1 + rho_ord - x2^2))"

    comparison = payload["comparison_to_active_spread_pair"]
    assert comparison["status"] == "diagnostic_witness_not_source_emission"
    assert abs(comparison["sigma_u_residual"]) < 0.05
    assert abs(comparison["sigma_d_residual"]) < 0.2
