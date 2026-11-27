#!/usr/bin/env python3
"""Reproduce conditional acceleration benchmark arithmetic from declared inputs.

Physical normalization and external capacity attachment are unproved.
The source literals define a computational benchmark, with no stated uncertainty.
"""

from __future__ import annotations

import argparse
import json
import math
from numbers import Real

C = 299_792_458.0
G = 6.67430e-11
HBAR = 1.054_571_817e-34
DEFAULT_N_SCR = 3.31e122
DEFAULT_P = 1.630968209403959
SOURCE_COMMIT = "3b09f6b26655606b144a526a1b246d1d865f04a7"
STATUS = "RECOVERED CONDITIONAL BENCHMARK ARITHMETIC"

# Paths, line numbers and SHA-256 identify the complete historical source blobs.
SOURCES = (
    ("code/dark_matter/scripts/d6_capacity_calculator.py", [17, 18, 19, 21, 23, 94, 96, 104],
     "2f539954bb8ba7414501281181d686e803ae3a65a14c97d623bf475dcf184a30",
     "SI constants, declared N_scr and dimensional benchmark coefficient"),
    ("code/dark_matter/scripts/z6_shared_edge_reserve.py", [31, 32, 33, 34, 38, 39],
     "38f591339e76297405ffe2852482ffa4b0fc2224549b167324fc635c0ff578f2",
     "P, epsilon and the presence and Poisson survival assumptions"),
    ("code/dark_matter/scripts/galaxy_channel_selector_candidates.py", [125],
     "bae5b10b1f64b017b34e47edb65d38f34eb3d5a4f458dd7f7c4dfd39c2d6196d",
     "Inverse-square survival factor"),
    ("cosmology/oph_dark_matter_paper.tex", [855, 956, 960, 2197, 2199, 2243],
     "842778a5b182c3ec0fda3992e24b9410e0cf178436df6edc92966b989e9de482",
     "eq:aeff, reserve assumptions and empirical input boundary"),
)


def _finite(name: str, value: float, *, allow_zero: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(value) or value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{name} must be finite and {'nonnegative' if allow_zero else 'positive'}")
    return value


def compute(n_scr: float = DEFAULT_N_SCR, p: float = DEFAULT_P, *,
            c: float = C, g: float = G, hbar: float = HBAR) -> dict:
    """Compute both readings for N_scr > 0, 0 <= P < 24 and positive SI constants.

    Reject arithmetic outside finite positive floating-point range.
    P=0 is the zero-reserve limit. Both survival factors then equal one.
    """
    n_scr = _finite("N_scr", n_scr)
    p = _finite("P", p, allow_zero=True)
    c, g, hbar = (_finite(name, value) for name, value in
                  (("c", c), ("G", g), ("hbar", hbar)))
    if p >= 24:
        raise ValueError("P must be less than 24 for positive presence survival")
    try:
        l_p = _finite("l_P", math.sqrt(hbar * g / c**3))
        cosmological_lambda = _finite("Lambda", 3 * math.pi / (n_scr * l_p**2))
        r_ds = _finite("r_dS", math.sqrt(3 / cosmological_lambda))
        a_oph = _finite("a_OPH", 15 * c**2 / (8 * math.pi**2 * r_ds))
        epsilon = p / 24
        presence = _finite("lambda_presence", 1 - epsilon)
        poisson = _finite("lambda_poisson", math.exp(-epsilon))
        a_presence = _finite("a_eff_presence", a_oph / presence**2)
        a_poisson = _finite("a_eff_poisson", a_oph / poisson**2)
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("Inputs exceed finite positive arithmetic range") from exc
    return {
        "status": STATUS,
        "inputs": {"N_scr": n_scr, "P": p, "c": c, "G": g, "hbar": hbar},
        "units": {"N_scr": "1", "P": "1", "c": "m s^-1",
                  "G": "m^3 kg^-1 s^-2", "hbar": "J s", "l_P": "m",
                  "Lambda": "m^-2", "r_dS": "m", "a_OPH": "m s^-2",
                  "epsilon": "1", "lambda_presence": "1", "lambda_poisson": "1",
                  "a_eff_presence": "m s^-2", "a_eff_poisson": "m s^-2"},
        "intermediates": {"l_P": l_p, "Lambda": cosmological_lambda,
                          "r_dS": r_ds, "a_OPH": a_oph, "epsilon": epsilon,
                          "lambda_presence": presence, "lambda_poisson": poisson},
        "readings": {"a_eff_presence": a_presence, "a_eff_poisson": a_poisson},
        "provenance": {
            "commit": SOURCE_COMMIT,
            "sources": [{"path": path, "lines": list(lines), "sha256": digest, "role": role}
                        for path, lines, digest, role in SOURCES],
            "input_roles": {
                "N_scr": "Declared capacity benchmark; exact external dataset attachment unproved.",
                "P": "Working CODATA-alpha-located coordinate under historical SL-2.",
                "SI_constants": "Declared SI literals; source edition and uncertainty unspecified.",
                "overrides": "Returned inputs are the supplied computational values.",
            },
        },
        "physical_normalization": "UNPROVED",
        "external_capacity_attachment": "UNPROVED",
        "boundary": (
            "Physical normalization and external capacity attachment are unproved. "
            "Presence assumes the P/24 one-class reserve; Poisson assumes zero-count semantics. "
            "This arithmetic selects neither physical branch. "
            "Audit verdicts and empirical input counts are unchanged."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-scr", type=float, default=DEFAULT_N_SCR)
    parser.add_argument("--p", type=float, default=DEFAULT_P)
    parser.add_argument("--c", type=float, default=C, help="Speed in m s^-1")
    parser.add_argument("--g", type=float, default=G, help="Constant in m^3 kg^-1 s^-2")
    parser.add_argument("--hbar", type=float, default=HBAR, help="Constant in J s")
    args = parser.parse_args(argv)
    try:
        result = compute(args.n_scr, args.p, c=args.c, g=args.g, hbar=args.hbar)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
