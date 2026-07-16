"""Fail-closed gate for an electroweak chart-to-measurement comparison.

Numerical chart cells may be emitted as internal diagnostics.  They become a
physical W/Z comparison only after one contract identifies the theory output
and the experimental target as the same observable and supplies the missing
renormalization and uncertainty information.
"""

from __future__ import annotations

from typing import Any


REQUIRED_THEORY_FIELDS = (
    "output_observable",
    "renormalized_vev_scheme",
    "tadpole_scheme",
    "field_content",
    "threshold_matching",
    "rg_order",
    "self_energy_order",
    "finite_parts_completion",
    "complex_pole_definition",
    "analytic_sheet_receipt",
    "gauge_independence_receipt",
    "scale_stability_receipt",
    "theory_covariance",
)

REQUIRED_TARGET_FIELDS = (
    "observable",
    "data_release",
    "release_date",
    "lineshape_convention",
    "central_values",
    "covariance",
)

OPEN_MARKERS = (None, "", "open", "missing", "unknown", "tbd", "n/a")


def _missing_fields(section: Any, required: tuple[str, ...], prefix: str) -> list[str]:
    if not isinstance(section, dict):
        return [f"{prefix}.{field}" for field in required]
    missing: list[str] = []
    for field in required:
        value = section.get(field)
        if isinstance(value, str):
            value_is_open = value.strip().lower() in OPEN_MARKERS
        else:
            value_is_open = value in OPEN_MARKERS
        if value_is_open:
            missing.append(f"{prefix}.{field}")
    return missing


def classify_physical_comparison(
    preregistration: dict[str, Any],
    readout_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return an auditable physical-comparison status.

    The old packet specs have no physical readout contract and explicitly list
    open gates.  They therefore return ``NOT_EVALUABLE`` while their numerical
    cells remain available as internal prescription diagnostics.
    """

    contract = readout_contract or preregistration.get("physical_readout_contract")
    declared_open = list(preregistration.get("fail_closed_gates_declared_open", []))
    missing: list[str] = []
    if not isinstance(contract, dict):
        missing.append("physical_readout_contract")
        theory = None
        target = None
    else:
        theory = contract.get("theory")
        target = contract.get("target")
        missing.extend(_missing_fields(theory, REQUIRED_THEORY_FIELDS, "theory"))
        missing.extend(_missing_fields(target, REQUIRED_TARGET_FIELDS, "target"))

    convention_match = bool(
        isinstance(theory, dict)
        and isinstance(target, dict)
        and theory.get("output_observable") == target.get("observable")
        and contract.get("observable_identity_receipt")
    )
    if not convention_match:
        missing.append("observable_identity_receipt")

    blockers = {
        "declared_open_gates": declared_open,
        "missing_or_open_contract_fields": sorted(set(missing)),
    }
    evaluable = not declared_open and not missing and convention_match
    return {
        "status": "EVALUABLE" if evaluable else "NOT_EVALUABLE",
        "physical_pull_allowed": evaluable,
        "internal_prescription_diagnostics_allowed": True,
        "blockers": blockers,
        "rule": (
            "A physical residual or pull is allowed only when all readout fields "
            "are closed, no fail-closed gate remains open, and an identity receipt "
            "places theory and target in the same observable convention."
        ),
    }

