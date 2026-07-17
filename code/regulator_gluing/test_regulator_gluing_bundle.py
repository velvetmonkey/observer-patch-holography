"""Pytest suite for the quantum regulator gluing gate (issue #529)."""

import copy
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from regulator_gluing_bundle import (
    GQ,
    PAULI_X,
    build_bundle,
    build_central_witness,
    build_countermodel,
    build_strict_witness,
    dagger,
    identity,
    mat_eq,
    mat_mul,
    mat_to_json,
    run_bundle,
    run_gate,
)

HERE = Path(__file__).parent


# ---------------------------------------------------------------------------
# Positive witnesses
# ---------------------------------------------------------------------------

def test_strict_witness_passes():
    report = run_gate(build_strict_witness())
    assert report["passed"], report["reasons"]


def test_strict_witness_has_triple_overlap_and_nonabelian_algebra():
    witness = build_strict_witness()
    assert witness["triples"], "a genuine triple overlap is required"
    assert any(p["hilbert_dim"] >= 2 for p in witness["patches"])


def test_strict_witness_subalgebra_map_checked():
    report = run_gate(build_strict_witness())
    ad_report = next(r for r in report["overlaps"] if r["edge"] == ["A", "D"])
    names = {c["name"] for c in ad_report["checks"]}
    assert "preserves_product" in names
    assert "preserves_adjoint" in names
    assert "linear_bijection_on_domain" in names
    assert ad_report["passed"]


def test_central_witness_passes_with_nontrivial_cocycle():
    witness = build_central_witness()
    report = run_gate(witness)
    assert report["passed"], report["reasons"]
    defects = [t["measured_defect"] for t in report["triples"]]
    assert any(d != ["1", "0"] for d in defects), "the central cocycle must be nontrivial"


def test_central_witness_quadruple_identity():
    report = run_gate(build_central_witness())
    assert report["quadruples"], "the 2-cocycle identity must be exercised"
    assert all(q["passed"] for q in report["quadruples"])
    assert all(q["measured_product"] == ["1", "0"] for q in report["quadruples"])


def test_every_overlap_map_is_displayed():
    for witness in (build_strict_witness(), build_central_witness()):
        report = run_gate(witness)
        for oreport in report["overlaps"]:
            assert "displayed_map" in oreport, oreport


# ---------------------------------------------------------------------------
# Negative gate: the issue #529 countermodel must fail
# ---------------------------------------------------------------------------

def test_countermodel_is_rejected():
    report = run_gate(build_countermodel())
    assert report["passed"] is False


def test_countermodel_rejection_reasons_are_structured():
    report = run_gate(build_countermodel())
    codes = {r["code"] for r in report["reasons"]}
    assert "NO_RECHARTING_MAP" in codes
    assert "STATE_SPACE_BIJECTION_IMPOSSIBLE" in codes
    assert "ALGEBRA_DIMENSION_MISMATCH" in codes
    assert "MANY_TO_ONE_PROJECTION" in codes
    dim_reason = next(r for r in report["reasons"] if r["code"] == "ALGEBRA_DIMENSION_MISMATCH")
    assert "16" in dim_reason["detail"] and "4" in dim_reason["detail"]
    state_reason = next(r for r in report["reasons"] if r["code"] == "STATE_SPACE_BIJECTION_IMPOSSIBLE")
    assert "4" in state_reason["detail"] and "2" in state_reason["detail"]


# ---------------------------------------------------------------------------
# Tamper checks: the gate must fail closed
# ---------------------------------------------------------------------------

def test_non_unitary_matrix_fails():
    witness = build_strict_witness()
    witness["overlaps"][0]["recharting"]["matrix"] = [
        [["1", "0"], ["1", "0"]],
        [["0", "0"], ["1", "0"]],
    ]
    report = run_gate(witness)
    assert report["passed"] is False
    assert any(r["code"] == "NOT_UNITARY" for r in report["reasons"])


def test_broken_strict_cocycle_fails():
    witness = build_strict_witness()
    # Replace U_AC with a unitary that violates U_AB U_BC = U_AC.
    witness["overlaps"][2]["recharting"]["matrix"] = mat_to_json(PAULI_X)
    report = run_gate(witness)
    assert report["passed"] is False
    assert any(r["code"] == "COCYCLE_VIOLATION" for r in report["reasons"])


def test_wrong_declared_central_defect_fails():
    witness = build_central_witness()
    witness["triples"][0]["expected_defect"] = GQ(0, -1).to_json()
    report = run_gate(witness)
    assert report["passed"] is False
    assert any(r["code"] == "CENTRAL_DEFECT_VIOLATION" for r in report["reasons"])


def test_dimension_mismatched_unitary_edge_fails():
    witness = build_strict_witness()
    witness["patches"][1]["hilbert_dim"] = 4  # patch B: M_4(C) against 2x2 unitaries
    report = run_gate(witness)
    assert report["passed"] is False
    codes = {r["code"] for r in report["reasons"]}
    assert "ALGEBRA_DIMENSION_MISMATCH" in codes or "UNITARY_DIMENSION_MISMATCH" in codes


def test_missing_recharting_map_fails():
    witness = build_strict_witness()
    witness["overlaps"][0]["recharting"] = None
    report = run_gate(witness)
    assert report["passed"] is False
    assert any(r["code"] == "NO_RECHARTING_MAP" for r in report["reasons"])


def test_degenerate_isomorphism_images_fail():
    witness = build_strict_witness()
    ad_overlap = witness["overlaps"][3]
    first = ad_overlap["recharting"]["generator_images"][0]
    ad_overlap["recharting"]["generator_images"] = [copy.deepcopy(first) for _ in range(4)]
    report = run_gate(witness)
    assert report["passed"] is False


# ---------------------------------------------------------------------------
# Exact arithmetic sanity
# ---------------------------------------------------------------------------

def test_pauli_x_is_exactly_unitary():
    assert mat_eq(mat_mul(dagger(PAULI_X), PAULI_X), identity(2))


# ---------------------------------------------------------------------------
# End-to-end bundle and verifier command
# ---------------------------------------------------------------------------

def test_bundle_accepted_end_to_end():
    report = run_bundle(build_bundle())
    assert report["accepted"]
    assert report["negative_gate_holds"]


def test_verifier_command_exit_zero_on_canonical_bundle():
    result = subprocess.run(
        [sys.executable, str(HERE / "verify_regulator_gluing_bundle.py")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "bundle accepted: True" in result.stdout


def test_verifier_command_exit_nonzero_on_countermodel_promotion(tmp_path):
    """A stored bundle whose witness list contains the countermodel document
    must drive the verifier to a nonzero exit."""
    import json
    bundle = build_bundle()
    bundle["witnesses"].append(build_countermodel())
    path = tmp_path / "tampered_bundle.json"
    path.write_text(json.dumps({"bundle": bundle}))
    result = subprocess.run(
        [sys.executable, str(HERE / "verify_regulator_gluing_bundle.py"),
         "--bundle", str(path)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
