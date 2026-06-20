#!/usr/bin/env python3
"""Validate the OPH claim-registry seed files.

The registry file is JSON-compatible YAML, so this validator avoids an external
YAML dependency while keeping the requested `.yaml` public path.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "claims" / "claim_registry.yaml"
NOVELTY = ROOT / "claims" / "novelty_matrix.csv"
FALSIFICATION = ROOT / "claims" / "falsification_matrix.csv"
GRAPH = ROOT / "claims" / "dependency_graph.json"
PREDICTIONS = ROOT / "predictions" / "prospective_predictions.json"
RELEASE_INFO = ROOT / "paper" / "release_info.tex"

PAPER_EXTERNAL_REGISTRY_PATTERNS = [
    "claims/claim_registry",
    "\\ophid{claims/",
]

REQUIRED_CLAIM_FIELDS = {
    "claim_id",
    "statement",
    "owner_paper",
    "tier",
    "assumptions",
    "imported_results",
    "oph_specific_delta",
    "novelty_type",
    "evidence",
    "falsifier",
    "scope_if_false",
    "status",
}


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON-compatible YAML: {exc}") from exc


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def release_id_from_tex() -> str:
    text = RELEASE_INFO.read_text(encoding="utf-8")
    match = re.search(r"\\newcommand\{\\OPHPaperReleaseID\}\{([^}]+)\}", text)
    require(match is not None, "paper/release_info.tex does not define OPHPaperReleaseID")
    return match.group(1)


def check_standalone_papers() -> None:
    for folder in ["paper", "extra"]:
        for path in (ROOT / folder).glob("*.tex"):
            text = path.read_text(encoding="utf-8")
            for pattern in PAPER_EXTERNAL_REGISTRY_PATTERNS:
                require(
                    pattern not in text,
                    f"{path.relative_to(ROOT)} references the external claim registry; papers must remain standalone",
                )


def main() -> None:
    registry = load_json(CLAIMS)
    require(
        registry.get("release_id") == release_id_from_tex(),
        f"registry release_id {registry.get('release_id')!r} does not match paper/release_info.tex",
    )
    claims = registry.get("claims", [])
    require(isinstance(claims, list) and claims, "claim registry has no claims")
    check_standalone_papers()

    seen: set[str] = set()
    owner_paths: set[str] = set()
    for claim in claims:
        missing = REQUIRED_CLAIM_FIELDS - set(claim)
        require(not missing, f"{claim.get('claim_id', '<missing>')}: missing fields {sorted(missing)}")
        claim_id = claim["claim_id"]
        require(claim_id not in seen, f"duplicate claim_id {claim_id}")
        seen.add(claim_id)
        require(claim["statement"].strip(), f"{claim_id}: empty statement")
        require(claim["assumptions"], f"{claim_id}: empty assumptions")
        require(claim["imported_results"], f"{claim_id}: empty imported_results")
        require(claim["oph_specific_delta"].strip(), f"{claim_id}: empty OPH delta")
        require(claim["falsifier"].strip(), f"{claim_id}: empty falsifier")
        owner = ROOT / claim["owner_paper"]
        require(owner.exists(), f"{claim_id}: owner paper does not exist: {claim['owner_paper']}")
        owner_paths.add(claim["owner_paper"])

    for matrix_path, required_columns in [
        (NOVELTY, {"claim_id", "closest_prior_work", "oph_specific_delta", "novelty_type", "falsifier"}),
        (FALSIFICATION, {"claim_id", "mathematical_falsifier", "physical_identification_falsifier", "phenomenological_falsifier", "scope_if_false"}),
    ]:
        rows = load_csv(matrix_path)
        require(rows, f"{matrix_path}: no rows")
        require(required_columns.issubset(rows[0].keys()), f"{matrix_path}: missing required columns")
        for row in rows:
            claim_id = row["claim_id"]
            require(claim_id in seen, f"{matrix_path}: unknown claim_id {claim_id}")

    graph = load_json(GRAPH)
    nodes = set(graph.get("nodes", []))
    require(nodes <= seen, f"dependency graph has unknown nodes: {sorted(nodes - seen)}")
    for edge in graph.get("edges", []):
        require(edge.get("from") in seen, f"dependency graph has unknown edge source: {edge}")
        require(edge.get("to") in seen, f"dependency graph has unknown edge target: {edge}")
        require(edge.get("role"), f"dependency graph edge lacks role: {edge}")

    predictions = load_json(PREDICTIONS)
    protocol = predictions.get("protocol", {})
    require(protocol.get("publish_null_result") is True, "prediction protocol must publish null results")
    require(isinstance(predictions.get("entries"), list), "prediction entries must be a list")

    print(f"claim registry OK: {len(seen)} claims, {len(owner_paths)} owner papers")


if __name__ == "__main__":
    main()
