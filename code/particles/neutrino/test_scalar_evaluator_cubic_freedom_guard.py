import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "particles" / "neutrino" / "derive_majorana_overlap_defect_scalar_evaluator.py"
OUTPUT = ROOT / "particles" / "runs" / "neutrino" / "majorana_overlap_defect_scalar_evaluator.json"


def test_scalar_evaluator_closes_current_isotropic_branch_and_eliminates_cubic_freedom() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], check=True, cwd=ROOT)
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["proof_status"] == "exact_scalar_evaluator_conditional_on_source_open_inputs"
    assert payload["source_only_physical_input_eligible"] is False
    assert payload["presentation_independence_status"] == "closed_from_common_refinement_transport_equivalence"
    assert payload["quadraticity_clause_status"] == "closed_from_descended_hermitian_direct_sum_norm"
    assert payload["finite_angle_exactness_status"] == "closed_on_current_isotropic_branch"
    assert payload["invariant_ring_obstruction"]["cubic_freedom_eliminated"] is True
    assert payload["next_exact_object_after_scalar_closure"] == "source_closed_neutrino_operator_basis_and_mass_label_contract"
