#!/usr/bin/env python3
"""Conditional logarithmic black-hole entropy coefficients for OPH-like counts.

A finite register alone does not force a logarithmic correction.  This script
separates three mechanisms:
  1. unconstrained q-state cells: c=0;
  2. exact balanced occupations among q categories: c=(q-1)/2;
  3. continuous compact-group singlet projection of dimension d: c=d/2.
A finite A5 quotient changes only the O(1) constant in the generic free-orbit
case, not the coefficient of log K.
"""
from __future__ import annotations

import json
import math


def log_balanced_multinomial(k: int, q: int) -> float:
    if k <= 0 or q <= 1 or k % q:
        raise ValueError("k must be positive and divisible by q>1")
    return math.lgamma(k + 1) - q * math.lgamma(k // q + 1)


def effective_c(q: int, k1: int, k2: int) -> float:
    r1 = k1 * math.log(q) - log_balanced_multinomial(k1, q)
    r2 = k2 * math.log(q) - log_balanced_multinomial(k2, q)
    return (r2 - r1) / math.log(k2 / k1)


def payload() -> dict:
    c12 = 11.0 / 2.0
    c24 = 23.0 / 2.0
    e12 = effective_c(12, 12000, 120000)
    e24 = effective_c(24, 24000, 240000)
    return {
        "schema": "conditional OPH black-hole logarithmic correction audit v1",
        "general_results": {
            "unconstrained_q_state_cells": "S=K log q exactly; c=0",
            "exact_balanced_q_categories": "S=K log q - (q-1)/2 log K + O(1)",
            "continuous_group_singlet_projection": "S=S0 - dim(G)/2 log K + O(1), under a nondegenerate identity saddle",
            "finite_group_quotient": "generic free quotient changes S by -log|H|+O(exp(-const*K)); c is unchanged",
        },
        "candidate_coefficients": {
            "12_port_exact_balance": c12,
            "24_oriented_slot_exact_balance": c24,
            "nonabelian_SM_singlet_dim_11": 11.0 / 2.0,
            "full_SM_gauge_singlet_dim_12": 6.0,
            "unconstrained_finite_register": 0.0,
        },
        "numerical_stirling_checks": {
            "q12_effective_c_12000_to_120000": e12,
            "q24_effective_c_24000_to_240000": e24,
        },
        "decision_required": "OPH must specify the physical horizon ensemble and whether the U(1)/trivial channel is independently constrained. A single coefficient is not yet forced.",
        "warning": "No-marked-point symmetry fixes an invariant distribution, not exact occupation balance. Summing over all occupations removes the -11/2 term and returns c=0.",
    }


if __name__ == "__main__":
    print(json.dumps(payload(), indent=2))
