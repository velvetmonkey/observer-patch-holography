#!/usr/bin/env python3
"""Fail-closed comparator for a sealed source artifact and corrective target.

``run_bracket.py`` never reads a target. This separate process reads both
objects after emission, verifies the corrective target's coordinate algebra,
and refuses a verdict unless the target is externally activated and the
artifact is a certified function or enclosure over its registered P domain.

The canonical 2026-07-16 v3 contract is intentionally not activated. The
current sampled singleton bracket is intentionally not certified. Therefore a
real invocation currently returns ``NOT_EVALUABLE``. No point-diagnostic
containment shortcut is implemented.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import string
import sys
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import Any

TARGET_ARTIFACT = "oph_hadronic_closure_corrective_target_contract"
EMISSION_ARTIFACT = "oph_ward_projected_payload_source_bracket"
EMISSION_SCHEMA_VERSION = 3
MACHINE_CONTRACT_SCHEMA_VERSION = 1

TOTAL_COORDINATE = "delta_source_total_alpha_inv"
RESIDUAL_COORDINATE = "delta_source_residual_vs_implemented_alpha_inv"
S_QEW_COORDINATE = "s_qew_effective"
S_HADRONIC_COORDINATE = "s_hadronic"
COORDINATES = (
    TOTAL_COORDINATE,
    RESIDUAL_COORDINATE,
    S_QEW_COORDINATE,
    S_HADRONIC_COORDINATE,
)

REQUIRED_COORDINATE_TYPES = {
    TOTAL_COORDINATE: ("total", "inverse_alpha", "map_input_only"),
    RESIDUAL_COORDINATE: ("residual", "inverse_alpha", "diagnostic_only"),
    S_QEW_COORDINATE: (
        "screening_ratio_qew",
        "dimensionless",
        "diagnostic_only",
    ),
    S_HADRONIC_COORDINATE: (
        "screening_ratio_hadronic",
        "dimensionless",
        "diagnostic_only",
    ),
}

REQUIRED_RECEIPT_FIELDS = {
    "target_free_dependency_dag",
    "forbidden_input_scan",
    "source_commit",
    "source_tree_sha256",
    "generator_argv",
    "environment_lock",
    "python_version",
    "numeric_library_versions",
    "precision_and_cutoffs",
    "executable_dependency_sha256",
    "canonical_json_sha256",
    "external_timestamp",
    "payload_work_started_utc",
}


class ScoringError(ValueError):
    """Fail-closed protocol error with a stable machine code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ScoringError("schema_mismatch", f"{path} must be an object")
    return value


def _field(mapping: dict[str, Any], key: str, path: str) -> Any:
    if key not in mapping:
        raise ScoringError("schema_mismatch", f"missing {path}.{key}")
    return mapping[key]


def _decimal(value: Any, path: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ScoringError("schema_mismatch", f"{path} must be a finite decimal")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ScoringError("schema_mismatch", f"{path} is not a decimal") from exc
    if not result.is_finite():
        raise ScoringError("schema_mismatch", f"{path} must be finite")
    return result


def _sha256(value: Any, path: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in string.hexdigits for character in value)
    ):
        raise ScoringError("schema_mismatch", f"{path} must be a SHA-256 hex digest")
    return value.lower()


def _difference_equals(left: Decimal, right: Decimal, expected: Decimal) -> bool:
    with localcontext() as context:
        context.prec = 100
        return left - right == expected


def _s_separation_matches(
    left: Decimal,
    right: Decimal,
    alpha_u: Decimal,
    q_naive: Decimal,
) -> bool:
    with localcontext() as context:
        context.prec = 100
        return abs((left - right) - alpha_u / q_naive) <= Decimal("1e-36")


def _at_path(mapping: dict[str, Any], dotted_path: str) -> Any:
    value: Any = mapping
    walked: list[str] = []
    for key in dotted_path.split("."):
        parent = ".".join(walked) or "root"
        value = _field(_mapping(value, parent), key, parent)
        walked.append(key)
    return value


def artifact_content_sha256(artifact: dict[str, Any]) -> str:
    """Recompute the source emitter's deterministic embedded hash."""
    digest_source = {
        key: value
        for key, value in artifact.items()
        if key not in {"content_sha256", "wall_time_seconds"}
    }
    try:
        canonical = json.dumps(
            digest_source,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ScoringError(
            "artifact_schema_mismatch", "artifact is not canonical finite JSON"
        ) from exc
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_interval(value: Any, path: str) -> dict[str, Decimal]:
    interval = _mapping(value, path)
    lo = _decimal(_field(interval, "lo", path), f"{path}.lo")
    hi = _decimal(_field(interval, "hi", path), f"{path}.hi")
    width = _decimal(_field(interval, "width", path), f"{path}.width")
    if lo > hi:
        raise ScoringError("coordinate_schema_mismatch", f"{path}.lo exceeds hi")
    expected_width = hi - lo
    width_error = abs(width - expected_width)
    allowed_error = max(abs(expected_width) * Decimal("1e-12"), Decimal("1e-15"))
    if width_error > allowed_error:
        raise ScoringError(
            "coordinate_schema_mismatch",
            f"{path}.width does not equal hi - lo",
        )
    return {"lo": lo, "hi": hi, "width": width}


def _validate_corrective_target(target: dict[str, Any]) -> None:
    """Validate the algebra and epistemic gates present in corrective v3."""
    if target.get("artifact") != TARGET_ARTIFACT:
        raise ScoringError("target_schema_mismatch", "unexpected target artifact")
    if not isinstance(target.get("id"), str):
        raise ScoringError("target_schema_mismatch", "target id is missing")
    _sha256(
        _field(target, "historical_v2_sha256", "target"),
        "target.historical_v2_sha256",
    )

    definitions = _mapping(
        _field(target, "coordinate_definitions", "target"),
        "target.coordinate_definitions",
    )
    required_definitions = {
        "Delta_source_total",
        "Delta_source_residual_vs_implemented",
        "S_QEW_effective",
        "S_hadronic",
        "type_rule",
    }
    if set(definitions) != required_definitions:
        raise ScoringError(
            "target_coordinate_mismatch",
            "target must define total, residual, S_QEW, and S_hadronic separately",
        )

    shared = _mapping(
        _field(target, "shared_payload_contract", "target"),
        "target.shared_payload_contract",
    )
    if shared.get("singleton_P_payload_eligible") is not False:
        raise ScoringError(
            "target_schema_mismatch", "singleton-P payloads must be ineligible"
        )
    if shared.get("sampled_grid_extrema_interval_certificate") is not False:
        raise ScoringError(
            "target_schema_mismatch",
            "sampled grid extrema cannot be an interval certificate",
        )
    if shared.get("Delta_EW_zero_status") != "declared_zero_branch_unproven":
        raise ScoringError(
            "target_coordinate_mismatch", "corrective target must leave Delta_EW open"
        )

    primary = _mapping(
        _field(target, "primary_scoring_rule", "target"),
        "target.primary_scoring_rule",
    )
    if primary.get("producer_and_comparator_separate") is not True:
        raise ScoringError(
            "target_schema_mismatch", "producer and comparator must be separate"
        )
    if primary.get("map_verdicts_independent") is not True:
        raise ScoringError(
            "target_schema_mismatch", "CL-1 and CL-2 verdicts must be independent"
        )
    if primary.get("point_diagnostics_can_decide_verdict") is not False:
        raise ScoringError(
            "target_schema_mismatch", "point diagnostics cannot decide a verdict"
        )

    measurement = _mapping(
        _field(target, "measurement_coordinate", "target"),
        "target.measurement_coordinate",
    )
    implemented = _decimal(
        _field(
            measurement,
            "Delta_source_implemented_at_P_target_point",
            "target.measurement_coordinate",
        ),
        "target.measurement_coordinate.Delta_source_implemented_at_P_target_point",
    )
    alpha_u = _decimal(
        _field(
            measurement,
            "alpha_U_at_P_target_point",
            "target.measurement_coordinate",
        ),
        "target.measurement_coordinate.alpha_U_at_P_target_point",
    )
    q_naive = _decimal(
        _field(
            measurement,
            "Delta_quark_naive_at_P_target_point",
            "target.measurement_coordinate",
        ),
        "target.measurement_coordinate.Delta_quark_naive_at_P_target_point",
    )

    maps = _mapping(_field(target, "map_targets", "target"), "target.map_targets")
    if set(maps) != {"CL-1", "CL-2"}:
        raise ScoringError(
            "target_schema_mismatch", "target must contain separate CL-1 and CL-2 maps"
        )

    totals: dict[str, Decimal] = {}
    s_qew: dict[str, Decimal] = {}
    for map_name in ("CL-1", "CL-2"):
        map_target = _mapping(maps[map_name], f"target.map_targets.{map_name}")
        if map_target.get("closure_rows") != [map_name]:
            raise ScoringError(
                "target_schema_mismatch", f"{map_name} must govern only its own row"
            )
        formula = map_target.get("map_formula")
        if not isinstance(formula, str):
            raise ScoringError(
                "target_schema_mismatch", f"{map_name} map formula missing"
            )
        if (map_name == "CL-2") != ("alpha_U" in formula):
            raise ScoringError(
                "target_coordinate_mismatch",
                "only the CL-2 completed map may add alpha_U",
            )
        point = _mapping(
            _field(
                map_target, "point_diagnostics_only", f"target.map_targets.{map_name}"
            ),
            f"target.map_targets.{map_name}.point_diagnostics_only",
        )
        total = _decimal(
            _field(
                point,
                "Delta_source_total_target",
                f"target.map_targets.{map_name}.point_diagnostics_only",
            ),
            f"target.map_targets.{map_name}.point_diagnostics_only.Delta_source_total_target",
        )
        residual = _decimal(
            _field(
                point,
                "Delta_source_residual_vs_implemented",
                f"target.map_targets.{map_name}.point_diagnostics_only",
            ),
            f"target.map_targets.{map_name}.point_diagnostics_only.Delta_source_residual_vs_implemented",
        )
        if not _difference_equals(total, implemented, residual):
            raise ScoringError(
                "target_coordinate_mismatch",
                f"{map_name} total and residual use inconsistent baselines",
            )
        if point.get("S_hadronic_target") is not None:
            raise ScoringError(
                "target_coordinate_mismatch",
                f"{map_name} cannot name S_QEW as a hadronic target while Delta_EW is open",
            )
        totals[map_name] = total
        s_qew[map_name] = _decimal(
            _field(
                point,
                "S_QEW_effective_target",
                f"target.map_targets.{map_name}.point_diagnostics_only",
            ),
            f"target.map_targets.{map_name}.point_diagnostics_only.S_QEW_effective_target",
        )

    if not _difference_equals(totals["CL-1"], totals["CL-2"], alpha_u):
        raise ScoringError(
            "target_coordinate_mismatch",
            "CL-1 and CL-2 total targets must differ by alpha_U",
        )
    if not _s_separation_matches(s_qew["CL-1"], s_qew["CL-2"], alpha_u, q_naive):
        raise ScoringError(
            "target_coordinate_mismatch",
            "CL-1 and CL-2 S_QEW diagnostics have inconsistent separation",
        )


def _validate_machine_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if contract.get("schema_version") != MACHINE_CONTRACT_SCHEMA_VERSION:
        raise ScoringError(
            "target_schema_mismatch", "unexpected machine_scoring_contract schema"
        )
    if contract.get("payload_artifact") != EMISSION_ARTIFACT:
        raise ScoringError(
            "target_schema_mismatch", "machine contract names the wrong artifact"
        )
    if contract.get("payload_schema_version") != EMISSION_SCHEMA_VERSION:
        raise ScoringError(
            "target_schema_mismatch", "machine contract names the wrong payload schema"
        )
    if contract.get("payload_object") != (
        "target_blind_function_or_certified_interval_enclosure"
    ):
        raise ScoringError(
            "target_schema_mismatch",
            "machine contract permits an ineligible payload object",
        )
    for key in ("source_family_id", "scheme_id", "current_definition_id"):
        if not isinstance(contract.get(key), str) or not contract[key]:
            raise ScoringError(
                "target_schema_mismatch", f"missing machine contract {key}"
            )

    domain = _mapping(
        _field(contract, "p_domain", "target.machine_scoring_contract"),
        "target.machine_scoring_contract.p_domain",
    )
    lo = _decimal(
        _field(domain, "lo", "target.machine_scoring_contract.p_domain"),
        "target.machine_scoring_contract.p_domain.lo",
    )
    hi = _decimal(
        _field(domain, "hi", "target.machine_scoring_contract.p_domain"),
        "target.machine_scoring_contract.p_domain.hi",
    )
    if lo >= hi or domain.get("kind") != "registered_P_basin":
        raise ScoringError(
            "target_schema_mismatch",
            "registered P domain must be a non-singleton basin",
        )

    schema = _mapping(
        _field(contract, "coordinate_schema", "target.machine_scoring_contract"),
        "target.machine_scoring_contract.coordinate_schema",
    )
    if set(schema) != set(COORDINATES):
        raise ScoringError(
            "target_coordinate_mismatch",
            "machine contract must distinguish total, residual, S_QEW, and S_hadronic",
        )
    for name, (kind, units, role) in REQUIRED_COORDINATE_TYPES.items():
        coordinate = _mapping(
            schema[name], f"target.machine_scoring_contract.coordinate_schema.{name}"
        )
        if (
            coordinate.get("kind") != kind
            or coordinate.get("units") != units
            or coordinate.get("scoring_role") != role
            or not isinstance(coordinate.get("artifact_path"), str)
        ):
            raise ScoringError(
                "target_coordinate_mismatch", f"machine contract misclassifies {name}"
            )
    required_receipts = contract.get("required_receipt_fields")
    if (
        not isinstance(required_receipts, list)
        or set(required_receipts) != REQUIRED_RECEIPT_FIELDS
    ):
        raise ScoringError(
            "target_schema_mismatch",
            "machine contract must require the full provenance receipt set",
        )
    return contract


def _require_activated_target(target: dict[str, Any]) -> dict[str, Any]:
    activation = _mapping(
        _field(target, "activation_requirements", "target"),
        "target.activation_requirements",
    )
    inactive = (
        "not_scorable" in str(target.get("registration_status"))
        or target.get("frozen_utc") is None
        or target.get("promotion_or_falsification_allowed") is not True
    )
    if inactive:
        raise ScoringError(
            "target_not_activated",
            "corrective target is not externally frozen or activated; no payload may score",
        )
    required_activation_fields = (
        "governs_payloads_started_after",
        "external_timestamp_receipt",
        "first_eligible_payload_commit_definition",
        "canonical_artifact_digest",
    )
    for field in required_activation_fields:
        if not activation.get(field):
            raise ScoringError(
                "target_not_activated", f"activation receipt {field} is missing"
            )
    _sha256(
        activation["canonical_artifact_digest"],
        "target.activation_requirements.canonical_artifact_digest",
    )
    contract = _mapping(
        _field(target, "machine_scoring_contract", "target"),
        "target.machine_scoring_contract",
    )
    return _validate_machine_contract(contract)


def _validate_artifact(
    artifact: dict[str, Any], contract: dict[str, Any]
) -> dict[str, dict[str, Decimal]]:
    if artifact.get("artifact") != EMISSION_ARTIFACT:
        raise ScoringError(
            "artifact_schema_mismatch",
            "legacy or unknown emission artifact; historical V1 is never scoreable",
        )
    if artifact.get("schema_version") != EMISSION_SCHEMA_VERSION:
        raise ScoringError(
            "artifact_schema_mismatch", "unexpected emission schema_version"
        )

    recorded_hash = artifact.get("content_sha256")
    _sha256(recorded_hash, "artifact.content_sha256")
    if recorded_hash != artifact_content_sha256(artifact):
        raise ScoringError(
            "artifact_hash_mismatch", "content_sha256 verification failed"
        )
    if artifact.get("promotion_allowed") is not False:
        raise ScoringError(
            "artifact_schema_mismatch", "a source emitter cannot authorize promotion"
        )
    if artifact.get("target_or_measurement_inputs_used_in_computation") is not False:
        raise ScoringError(
            "artifact_schema_mismatch",
            "artifact does not attest target-free production",
        )
    if artifact.get("payload_object") != contract["payload_object"]:
        raise ScoringError(
            "artifact_not_certified",
            "payload is not a target-blind function or certified P-domain enclosure",
        )
    if artifact.get("source_family_id") != contract["source_family_id"]:
        raise ScoringError("artifact_schema_mismatch", "source_family_id mismatch")
    scheme = _mapping(_field(artifact, "scheme", "artifact"), "artifact.scheme")
    if scheme.get("scheme_id") != contract["scheme_id"]:
        raise ScoringError("artifact_schema_mismatch", "scheme_id mismatch")
    if artifact.get("current_definition_id") != contract["current_definition_id"]:
        raise ScoringError("artifact_schema_mismatch", "current_definition_id mismatch")

    target_domain = _mapping(
        contract["p_domain"], "target.machine_scoring_contract.p_domain"
    )
    artifact_domain = _mapping(
        _field(artifact, "p_domain", "artifact"), "artifact.p_domain"
    )
    artifact_lo = _decimal(
        _field(artifact_domain, "lo", "artifact.p_domain"), "artifact.p_domain.lo"
    )
    artifact_hi = _decimal(
        _field(artifact_domain, "hi", "artifact.p_domain"), "artifact.p_domain.hi"
    )
    target_lo = _decimal(
        target_domain["lo"], "target.machine_scoring_contract.p_domain.lo"
    )
    target_hi = _decimal(
        target_domain["hi"], "target.machine_scoring_contract.p_domain.hi"
    )
    if (
        artifact_domain.get("kind") != "registered_P_basin"
        or artifact_lo != target_lo
        or artifact_hi != target_hi
    ):
        raise ScoringError(
            "evaluation_point_mismatch",
            "artifact P domain differs from the registered target basin",
        )

    actual_schema = _mapping(
        _field(artifact, "coordinate_schema", "artifact"),
        "artifact.coordinate_schema",
    )
    expected_schema = _mapping(
        contract["coordinate_schema"],
        "target.machine_scoring_contract.coordinate_schema",
    )
    if set(actual_schema) != set(COORDINATES):
        raise ScoringError(
            "coordinate_schema_mismatch",
            "artifact must distinguish total, residual, S_QEW, and S_hadronic",
        )
    intervals: dict[str, dict[str, Decimal]] = {}
    for name in COORDINATES:
        actual = _mapping(actual_schema[name], f"artifact.coordinate_schema.{name}")
        expected = _mapping(
            expected_schema[name],
            f"target.machine_scoring_contract.coordinate_schema.{name}",
        )
        for field in ("kind", "units", "artifact_path", "scoring_role"):
            if actual.get(field) != expected.get(field):
                raise ScoringError(
                    "coordinate_schema_mismatch",
                    f"{name}.{field} does not match the target contract",
                )
        intervals[name] = _validate_interval(
            _at_path(artifact, expected["artifact_path"]),
            f"artifact.{expected['artifact_path']}",
        )

    certification = _mapping(
        _field(artifact, "certification", "artifact"), "artifact.certification"
    )
    if certification.get("status") != "certified":
        raise ScoringError(
            "artifact_not_certified", "source object lacks a certified enclosure"
        )
    if certification.get("sampled_grid_extrema_interval_certificate") is not False:
        raise ScoringError(
            "artifact_not_certified", "sampled extrema cannot certify an interval"
        )
    if certification.get("delta_EW_gate") != "closed":
        raise ScoringError(
            "open_delta_EW_gate",
            "Delta_EW is open, so completed-map scoring is unavailable",
        )
    _validate_interval(
        _field(certification, "numerical_error_interval", "artifact.certification"),
        "artifact.certification.numerical_error_interval",
    )
    _validate_interval(
        _field(certification, "theory_error_interval", "artifact.certification"),
        "artifact.certification.theory_error_interval",
    )
    derivative_bound = _decimal(
        _field(
            certification,
            "derivative_or_lipschitz_bound_over_P_domain",
            "artifact.certification",
        ),
        "artifact.certification.derivative_or_lipschitz_bound_over_P_domain",
    )
    if derivative_bound < 0:
        raise ScoringError(
            "artifact_not_certified",
            "derivative or Lipschitz bound must be non-negative",
        )

    receipts = _mapping(_field(artifact, "receipts", "artifact"), "artifact.receipts")
    if set(receipts) != set(contract["required_receipt_fields"]):
        raise ScoringError(
            "artifact_provenance_mismatch",
            "artifact provenance receipt set is incomplete",
        )
    for hash_field in (
        "source_tree_sha256",
        "canonical_json_sha256",
    ):
        _sha256(receipts[hash_field], f"artifact.receipts.{hash_field}")
    dependencies = _mapping(
        receipts["executable_dependency_sha256"],
        "artifact.receipts.executable_dependency_sha256",
    )
    if not dependencies:
        raise ScoringError(
            "artifact_provenance_mismatch", "dependency hash receipt is empty"
        )
    for name, digest in dependencies.items():
        _sha256(digest, f"artifact.receipts.executable_dependency_sha256.{name}")
    return intervals


def score_artifact(artifact: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    """Validate a sealed source artifact, then fail closed before scalar scoring.

    The function raises :class:`ScoringError` for every non-evaluable state.
    A future completed-map solver must replace the final error; adding scalar
    point containment here would violate the corrective target.
    """
    artifact = _mapping(artifact, "artifact")
    target = _mapping(target, "target")
    _validate_corrective_target(target)
    contract = _require_activated_target(target)
    _validate_artifact(artifact, contract)
    raise ScoringError(
        "completed_map_solver_unavailable",
        "validated payload still requires independent interval solves of CL-1 and CL-2",
    )


def _load_json(path: Path, role: str) -> dict[str, Any]:
    def reject_nonfinite(value: str) -> None:
        raise ValueError(f"non-finite JSON number {value}")

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), parse_constant=reject_nonfinite
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ScoringError(f"{role}_read_error", f"cannot read {role}: {exc}") from exc
    return _mapping(value, role)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        artifact = _load_json(args.artifact, "artifact")
        target = _load_json(args.target, "target")
        score_artifact(artifact, target)
        raise AssertionError("score_artifact must return a verdict or fail closed")
    except ScoringError as exc:
        result = {
            "artifact": "oph_ward_projected_payload_score_attempt",
            "schema_version": 2,
            "status": "NOT_EVALUABLE",
            "error_code": exc.code,
            "error": exc.message,
            "map_results": {"CL-1": "NOT_EVALUABLE", "CL-2": "NOT_EVALUABLE"},
            "closure_allowed": False,
            "falsification_allowed": False,
            "promotion_allowed": False,
        }
        if args.artifact.exists():
            result["source_file_sha256"] = _file_sha256(args.artifact)
        if args.target.exists():
            result["target_file_sha256"] = _file_sha256(args.target)

    text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        output = args.output.resolve()
        if output in {args.artifact.resolve(), args.target.resolve()}:
            print("refusing to overwrite artifact or target", file=sys.stderr)
            return 2
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
