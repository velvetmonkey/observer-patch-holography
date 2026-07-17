#!/usr/bin/env python3
"""A5 decomposition of SO(3) angular momentum multiplets.

This is the symmetry-only core of the proposed OPH horizon/CMB spectroscopy
signature.  It uses the A5 character table and the SO(3) character
chi_l(theta)=sin((l+1/2)theta)/sin(theta/2).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHIBAR = (1.0 - math.sqrt(5.0)) / 2.0
CLASS_SIZES = [1, 15, 20, 12, 12]
ANGLES = [0.0, math.pi, 2.0 * math.pi / 3.0, 2.0 * math.pi / 5.0, 4.0 * math.pi / 5.0]
CHARS = {
    "1": [1, 1, 1, 1, 1],
    "3": [3, -1, 0, PHI, PHIBAR],
    "3prime": [3, -1, 0, PHIBAR, PHI],
    "4": [4, 0, 1, -1, -1],
    "5": [5, 1, -1, 0, 0],
}
DIMS = {"1": 1, "3": 3, "3prime": 3, "4": 4, "5": 5}


def so3_character(ell: int, theta: float) -> float:
    if ell < 0:
        raise ValueError("ell must be nonnegative")
    if abs(theta) < 1e-14:
        return float(2 * ell + 1)
    return math.sin((ell + 0.5) * theta) / math.sin(theta / 2.0)


def decompose(ell: int) -> dict[str, int]:
    chi = [so3_character(ell, theta) for theta in ANGLES]
    out: dict[str, int] = {}
    for name, ir in CHARS.items():
        raw = sum(s * a * b for s, a, b in zip(CLASS_SIZES, chi, ir)) / 60.0
        multiplicity = int(round(raw))
        if abs(raw - multiplicity) > 1e-8 or multiplicity < 0:
            raise ArithmeticError(f"nonintegral multiplicity ell={ell}, irrep={name}, raw={raw}")
        if multiplicity:
            out[name] = multiplicity
    if sum(DIMS[k] * v for k, v in out.items()) != 2 * ell + 1:
        raise ArithmeticError(f"dimension mismatch at ell={ell}: {out}")
    return out


def pretty(d: dict[str, int]) -> str:
    terms = []
    for name in ("1", "3", "3prime", "4", "5"):
        m = d.get(name, 0)
        if m == 1:
            terms.append(name)
        elif m > 1:
            terms.append(f"{m}*{name}")
    return " + ".join(terms) if terms else "0"


def payload(max_ell: int = 15) -> dict:
    rows = []
    for ell in range(max_ell + 1):
        dec = decompose(ell)
        rows.append({
            "ell": ell,
            "dimension": 2 * ell + 1,
            "decomposition": dec,
            "pretty": pretty(dec),
            "n_trivial_invariants": dec.get("1", 0),
            "multiplet_dimensions": sorted([DIMS[k] for k, m in dec.items() for _ in range(m)]),
        })
    port = {"1": 1, "3": 1, "3prime": 1, "5": 1}
    h0_plus_h5 = decompose(0).copy()
    for k, v in decompose(5).items():
        h0_plus_h5[k] = h0_plus_h5.get(k, 0) + v
    return {
        "schema": "A5 angular multiplet decomposition v1",
        "rows": rows,
        "first_nonconstant_A5_invariant_ell": next(r["ell"] for r in rows[1:] if r["n_trivial_invariants"]),
        "port_module": port,
        "restriction_H0_plus_H5": h0_plus_h5,
        "port_equals_restriction_H0_plus_H5": port == h0_plus_h5,
        "spectroscopy_targets": {
            "ell_2": "one 5-fold multiplet",
            "ell_3": "3prime + 4",
            "ell_4": "4 + 5",
            "ell_5": "3 + 3prime + 5",
            "ell_6": "1 + 3 + 4 + 5",
        },
        "caveat": "This fixes degeneracy/mixing representations only. Frequencies, amplitudes, linewidths, and the screen-to-observable coupling remain dynamical inputs.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-ell", type=int, default=15)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = payload(args.max_ell)
    if args.json:
        print(json.dumps(data, indent=2))
        return
    for row in data["rows"]:
        print(f"ell={row['ell']:2d}  dim={row['dimension']:2d}  {row['pretty']}")
    print(f"first nonconstant invariant: ell={data['first_nonconstant_A5_invariant_ell']}")


if __name__ == "__main__":
    main()
