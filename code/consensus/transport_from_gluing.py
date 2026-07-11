#!/usr/bin/env python3
"""Executable finite-sector form of the combined overlap-transport criterion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


Matrix = tuple[tuple[complex, ...], ...]
Edge = tuple[int, int]


def identity_matrix(dimension: int) -> Matrix:
    if dimension < 1:
        raise ValueError("matrix dimension must be positive")
    return tuple(
        tuple(1.0 + 0.0j if row == column else 0.0 + 0.0j for column in range(dimension))
        for row in range(dimension)
    )


def _matrix_dimension(matrix: Matrix) -> int:
    dimension = len(matrix)
    if dimension == 0 or any(len(row) != dimension for row in matrix):
        raise ValueError("matrices must be nonempty and square")
    return dimension


def multiply(left: Matrix, right: Matrix) -> Matrix:
    """Return ``left @ right`` for square matrices represented by tuples."""

    dimension = _matrix_dimension(left)
    if _matrix_dimension(right) != dimension:
        raise ValueError("matrices must be nonempty and have equal dimensions")
    return tuple(
        tuple(
            sum(left[row][k] * right[k][column] for k in range(dimension))
            for column in range(dimension)
        )
        for row in range(dimension)
    )


def path_transport(path: Sequence[int], edge_transports: Mapping[Edge, Matrix]) -> Matrix:
    """Compose edge transports using the manuscript convention ``U_last ... U_first``."""

    if not path:
        raise ValueError("a path must contain at least one vertex")
    if len(path) == 1:
        try:
            sample = next(iter(edge_transports.values()))
        except StopIteration as exc:
            raise ValueError("an identity path needs a matrix dimension") from exc
        return identity_matrix(len(sample))

    first_edge = (path[0], path[1])
    if first_edge not in edge_transports:
        raise KeyError(f"missing edge transport {first_edge}")
    result = identity_matrix(len(edge_transports[first_edge]))
    for edge in zip(path, path[1:]):
        result = multiply(edge_transports[edge], result)
    return result


def is_identity(matrix: Matrix, *, tolerance: float = 1e-12) -> bool:
    dimension = _matrix_dimension(matrix)
    target = identity_matrix(dimension)
    return all(
        abs(matrix[row][column] - target[row][column]) <= tolerance
        for row in range(dimension)
        for column in range(dimension)
    )


@dataclass(frozen=True)
class StrictTransportabilityReport:
    associator_defect_strictifiable: bool
    represented_loop_holonomy_trivial: bool

    @property
    def strict_path_independent(self) -> bool:
        return self.associator_defect_strictifiable and self.represented_loop_holonomy_trivial


def strict_transportability_report(
    *,
    associator_defect_strictifiable: bool,
    fundamental_loop_holonomies: Sequence[Matrix],
    expected_loop_generator_count: int,
    tolerance: float = 1e-12,
) -> StrictTransportabilityReport:
    """Apply the combined criterion to generators of represented sector holonomy.

    A vanishing central triangle class, or a strictifiable noncentral higher
    associator, only supplies a strict edge 1-cocycle. Strict endpoint-only
    transport also requires the represented holonomy of every fundamental-loop
    generator to be the identity.
    """

    if expected_loop_generator_count < 0:
        raise ValueError("expected loop-generator count must be nonnegative")
    if len(fundamental_loop_holonomies) != expected_loop_generator_count:
        raise ValueError("a complete fundamental-loop generating set is required")

    loop_holonomy_trivial = all(
        is_identity(holonomy, tolerance=tolerance) for holonomy in fundamental_loop_holonomies
    )
    return StrictTransportabilityReport(
        associator_defect_strictifiable=associator_defect_strictifiable,
        represented_loop_holonomy_trivial=loop_holonomy_trivial,
    )
