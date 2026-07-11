#!/usr/bin/env python3
"""Dynamic-circuit realization of the finite-sector generative repair kernel.

The circuit is a small observer-like self-reading system:

* three qubits hold a bounded local sector state;
* a mid-circuit readback is written to a public classical record;
* one qubit records a stochastic accept/reject repair decision;
* conditional feedback updates the sector state through a declared proposal
  port; and
* a final readback verifies the repair action.

Initial states are computational-basis states, never target heat-kernel
amplitudes.  This file runs local simulator validation only.  Hardware
submission is intentionally kept behind the separate preregistration gate.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, qpy, transpile
from qiskit_aer import AerSimulator

from generative_repair_kernel import (
    DEFAULT_BETA,
    OPH_KAPPA,
    SectorSpectrum,
    builtin_spectra,
    compare_acceptance_hypotheses,
    metropolis_acceptance,
    sha256_json,
)


CIRCUIT_SCHEMA_VERSION = "oph.generative-repair-instrument.v1"
SECTOR_QUBITS = 3
TOTAL_QUBITS = 4


@dataclass(frozen=True)
class EdgeRecipe:
    spectrum: str
    beta: float
    programmed_kappa: float
    semantic_source: int
    semantic_target: int
    physical_source: int
    physical_target: int
    label_permutation: tuple[int, ...]
    expected_acceptance: float


def validate_label_permutation(spectrum: SectorSpectrum, permutation: tuple[int, ...]) -> None:
    if len(permutation) != spectrum.size:
        raise ValueError("label permutation length does not match the spectrum")
    if sorted(permutation) != list(range(spectrum.size)):
        raise ValueError("label permutation must map each semantic sector to one physical code")
    if max(permutation) >= 2**SECTOR_QUBITS:
        raise ValueError("physical sector code does not fit the three-qubit register")


def edge_recipe(
    spectrum: SectorSpectrum,
    beta: float,
    programmed_kappa: float,
    semantic_source: int,
    semantic_target: int,
    label_permutation: tuple[int, ...] | None = None,
) -> EdgeRecipe:
    if semantic_source == semantic_target:
        raise ValueError("a repair proposal must connect distinct sectors")
    if semantic_source not in range(spectrum.size) or semantic_target not in range(spectrum.size):
        raise ValueError("source or target is outside the active spectrum")
    if label_permutation is None:
        label_permutation = tuple(range(spectrum.size))
    validate_label_permutation(spectrum, label_permutation)
    acceptance = metropolis_acceptance(spectrum, beta, programmed_kappa)
    return EdgeRecipe(
        spectrum=spectrum.name,
        beta=beta,
        programmed_kappa=programmed_kappa,
        semantic_source=semantic_source,
        semantic_target=semantic_target,
        physical_source=label_permutation[semantic_source],
        physical_target=label_permutation[semantic_target],
        label_permutation=label_permutation,
        expected_acceptance=float(acceptance[semantic_source, semantic_target]),
    )


def _apply_basis_code(circuit: QuantumCircuit, register: QuantumRegister, code: int) -> None:
    for bit in range(SECTOR_QUBITS):
        if (code >> bit) & 1:
            circuit.x(register[bit])
        else:
            circuit.id(register[bit])


def _apply_fixed_width_xor(
    circuit: QuantumCircuit,
    register: QuantumRegister,
    source: int,
    target: int,
) -> None:
    mask = source ^ target
    for bit in range(SECTOR_QUBITS):
        if (mask >> bit) & 1:
            circuit.x(register[bit])
        else:
            circuit.id(register[bit])


def build_edge_instrument(recipe: EdgeRecipe, circuit_name: str | None = None) -> QuantumCircuit:
    """Build one record-gated proposal/repair instrument.

    The first sector measurement is not discarded: it gates the acceptance
    rotation.  A wrong or corrupted readback therefore prevents the feedback
    action and remains visible in the public record.
    """

    sector = QuantumRegister(SECTOR_QUBITS, "sector")
    readback = QuantumRegister(1, "readback")
    before = ClassicalRegister(SECTOR_QUBITS, "before")
    accepted = ClassicalRegister(1, "accepted")
    after = ClassicalRegister(SECTOR_QUBITS, "after")
    name = circuit_name or (
        f"{recipe.spectrum}__k{recipe.programmed_kappa:g}__"
        f"{recipe.semantic_source}_to_{recipe.semantic_target}"
    )
    circuit = QuantumCircuit(sector, readback, before, accepted, after, name=name)

    _apply_basis_code(circuit, sector, recipe.physical_source)
    circuit.measure(sector, before)

    theta = 2.0 * math.asin(math.sqrt(recipe.expected_acceptance))
    with circuit.if_test((before, recipe.physical_source)):
        circuit.ry(theta, readback[0])
    circuit.measure(readback[0], accepted[0])

    with circuit.if_test((accepted[0], 1)):
        _apply_fixed_width_xor(
            circuit,
            sector,
            recipe.physical_source,
            recipe.physical_target,
        )

    circuit.reset(readback[0])
    circuit.measure(sector, after)
    circuit.metadata = {
        "schema_version": CIRCUIT_SCHEMA_VERSION,
        "recipe": asdict(recipe),
        "claim_boundary": "declared experimental kernel; not a physical-law selector",
    }
    return circuit


def qpy_sha256(circuit: QuantumCircuit) -> str:
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def circuit_receipt(circuit: QuantumCircuit) -> dict[str, Any]:
    return {
        "name": circuit.name,
        "qpy_sha256": qpy_sha256(circuit),
        "num_qubits": circuit.num_qubits,
        "num_clbits": circuit.num_clbits,
        "logical_depth": circuit.depth(),
        "operation_counts": {str(key): int(value) for key, value in circuit.count_ops().items()},
        "metadata": circuit.metadata,
    }


def parse_grouped_counts(counts: Mapping[str, int]) -> list[dict[str, int]]:
    """Parse Qiskit count keys ordered as ``after accepted before``."""

    rows: list[dict[str, int]] = []
    for key, count in counts.items():
        groups = key.split()
        if len(groups) != 3:
            raise ValueError(f"unexpected dynamic-circuit count key: {key!r}")
        after_bits, accepted_bits, before_bits = groups
        rows.append(
            {
                "before": int(before_bits, 2),
                "accepted": int(accepted_bits, 2),
                "after": int(after_bits, 2),
                "count": int(count),
            }
        )
    return rows


def summarize_edge_counts(recipe: EdgeRecipe, counts: Mapping[str, int]) -> dict[str, Any]:
    rows = parse_grouped_counts(counts)
    shots = sum(row["count"] for row in rows)
    accepted = sum(row["count"] for row in rows if row["accepted"] == 1)
    correct_before = sum(
        row["count"] for row in rows if row["before"] == recipe.physical_source
    )
    correct_transition = sum(
        row["count"]
        for row in rows
        if (
            row["before"] == recipe.physical_source
            and (
                (row["accepted"] == 1 and row["after"] == recipe.physical_target)
                or (row["accepted"] == 0 and row["after"] == recipe.physical_source)
            )
        )
    )
    return {
        "recipe": asdict(recipe),
        "shots": shots,
        "accepted_count": accepted,
        "observed_acceptance": accepted / shots,
        "expected_acceptance": recipe.expected_acceptance,
        "absolute_acceptance_error": abs(accepted / shots - recipe.expected_acceptance),
        "correct_before_fraction": correct_before / shots,
        "record_conditioned_transition_consistency": correct_transition / shots,
        "raw_counts": dict(counts),
    }


def build_family(
    spectrum: SectorSpectrum,
    beta: float,
    programmed_kappa: float,
    label_permutation: tuple[int, ...] | None = None,
) -> list[tuple[EdgeRecipe, QuantumCircuit]]:
    if label_permutation is None:
        label_permutation = tuple(range(spectrum.size))
    family = []
    for source in range(spectrum.size):
        for target in range(spectrum.size):
            if source == target:
                continue
            recipe = edge_recipe(
                spectrum,
                beta,
                programmed_kappa,
                source,
                target,
                label_permutation,
            )
            family.append((recipe, build_edge_instrument(recipe)))
    return family


def run_ideal_family(
    spectrum: SectorSpectrum,
    beta: float,
    programmed_kappa: float,
    shots: int,
    seed: int,
    label_permutation: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    if shots <= 0:
        raise ValueError("shots must be positive")
    family = build_family(spectrum, beta, programmed_kappa, label_permutation)
    recipes = [item[0] for item in family]
    circuits = [item[1] for item in family]
    backend = AerSimulator(seed_simulator=seed)
    isa = transpile(circuits, backend=backend, optimization_level=0, seed_transpiler=seed)
    result = backend.run(isa, shots=shots).result()

    accepted_matrix = np.zeros((spectrum.size, spectrum.size), dtype=int)
    total_matrix = np.zeros((spectrum.size, spectrum.size), dtype=int)
    edge_summaries = []
    for recipe, circuit in zip(recipes, circuits):
        counts = result.get_counts(circuit)
        summary = summarize_edge_counts(recipe, counts)
        edge_summaries.append(summary)
        source = recipe.semantic_source
        target = recipe.semantic_target
        accepted_matrix[source, target] = summary["accepted_count"]
        total_matrix[source, target] = summary["shots"]

    comparison = compare_acceptance_hypotheses(
        spectrum,
        beta,
        accepted_matrix,
        total_matrix,
    )
    receipt = {
        "schema_version": CIRCUIT_SCHEMA_VERSION,
        "receipt_class": "ideal_dynamic_circuit_simulation_not_hardware_evidence",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "spectrum": asdict(spectrum),
        "beta": beta,
        "programmed_kappa": programmed_kappa,
        "shots_per_directed_edge": shots,
        "seed": seed,
        "accepted_matrix": accepted_matrix.tolist(),
        "total_matrix": total_matrix.tolist(),
        "hypothesis_comparison": comparison,
        "edge_summaries": edge_summaries,
        "circuit_receipts": [circuit_receipt(circuit) for circuit in circuits],
        "claim_boundary": (
            "Ordinary quantum mechanics predicts this programmed instrument. The receipt can "
            "distinguish frozen stationary-law kernels and reject state-preparation-only nulls; "
            "it cannot distinguish OPH from unrestricted quantum mechanics."
        ),
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ideal local validation of the self-reading generative repair instrument."
    )
    parser.add_argument("--spectrum", choices=sorted(builtin_spectra()), default="s3_primary")
    parser.add_argument("--beta", type=float, default=DEFAULT_BETA)
    parser.add_argument("--programmed-kappa", type=float, default=OPH_KAPPA)
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=509)
    parser.add_argument("--label-permutation", type=int, nargs="+")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spectrum = builtin_spectra()[args.spectrum]
    permutation = None
    if args.label_permutation is not None:
        permutation = tuple(args.label_permutation)
    receipt = run_ideal_family(
        spectrum=spectrum,
        beta=args.beta,
        programmed_kappa=args.programmed_kappa,
        shots=args.shots,
        seed=args.seed,
        label_permutation=permutation,
    )
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
