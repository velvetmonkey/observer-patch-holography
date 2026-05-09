#!/usr/bin/env python3
"""Friendly CLI for the OPH P/alpha closure experiment."""

from __future__ import annotations

import argparse
import json
import os
from decimal import Decimal, localcontext
from pathlib import Path
import sys
from time import monotonic
from typing import Any

from alpha_gap_audit import CODATA_2022_ALPHA_INV, CODATA_2022_ALPHA_INV_UNCERTAINTY
from paper_math import build_report


DEFAULT_HADRON_CLOSURE_DELTA_ALPHA_INV = Decimal(
    "0.041164012378350542050005414212806737971"
)
DEFAULT_MODE = "thomson_structured_running"
MODES = ("thomson_structured_running", "thomson_structured_running_asymptotic", "mz_anchor")


class Palette:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def paint(self, text: str, code: str) -> str:
        if not self.enabled:
            return text
        return f"\033[{code}m{text}\033[0m"

    def dim(self, text: str) -> str:
        return self.paint(text, "2")

    def cyan(self, text: str) -> str:
        return self.paint(text, "36")

    def green(self, text: str) -> str:
        return self.paint(text, "32")

    def gold(self, text: str) -> str:
        return self.paint(text, "33")

    def rose(self, text: str) -> str:
        return self.paint(text, "31")

    def bold(self, text: str) -> str:
        return self.paint(text, "1")


class ProgressDisplay:
    def __init__(self, palette: Palette, *, stream: Any = sys.stderr):
        self.palette = palette
        self.stream = stream
        self.started = monotonic()
        self.last_stage: str | None = None

    def __call__(self, event: dict[str, Any]) -> None:
        stage = str(event.get("stage", "progress"))
        percent = _percent(event.get("percent", Decimal(0)))
        elapsed = monotonic() - self.started
        bar = self._bar(percent)
        label = self._stage_label(stage)
        details = self._details(stage, event)

        if stage != self.last_stage and self.last_stage is not None:
            print("", file=self.stream)
        self.last_stage = stage

        print(
            f"{bar} {self.palette.green(f'{percent:6.2f}%')} "
            f"{label} {self.palette.dim(f'{elapsed:6.1f}s')} {details}",
            file=self.stream,
            flush=True,
        )

    def _stage_label(self, stage: str) -> str:
        labels = {
            "scan_start": self.palette.cyan("setup"),
            "scan": self.palette.cyan("scan"),
            "bracket": self.palette.gold("bracket"),
            "bisect": self.palette.gold("solve"),
            "complete": self.palette.green("done"),
        }
        return labels.get(stage, self.palette.cyan(stage))

    def _bar(self, percent: float) -> str:
        width = 24
        filled = max(0, min(width, round(width * percent / 100)))
        return (
            self.palette.green("[" + "#" * filled)
            + self.palette.dim("-" * (width - filled) + "]")
        )

    def _details(self, stage: str, event: dict[str, Any]) -> str:
        if stage == "scan_start":
            return (
                f"mode={event['mode']} precision={event['precision']} "
                f"cutoffs=SU2:{event['su2_cutoff']} SU3:{event['su3_cutoff']}"
            )
        if stage == "scan":
            return (
                f"{event['index'] + 1:>3}/{event['total']:<3} "
                f"alpha={_short_dec(event['alpha_probe'])} "
                f"P={_short_dec(event['p'])} "
                f"res={_signed_short_dec(event['residual_alpha'])} "
                f"A_in={_short_dec(event['inner_alpha_inv'])}"
            )
        if stage == "bracket":
            return (
                f"alpha in [{_short_dec(event['lo_alpha'])}, {_short_dec(event['hi_alpha'])}] "
                f"res=[{_signed_short_dec(event['lo_residual_alpha'])}, "
                f"{_signed_short_dec(event['hi_residual_alpha'])}]"
            )
        if stage == "bisect":
            transport = event.get("transport_delta_alpha_inv")
            transport_text = f" delta={_short_dec(transport)}" if transport is not None else ""
            return (
                f"{event['iteration']:>3}/{event['total']:<3} "
                f"A_in={_short_dec(event['inner_alpha_inv'])} "
                f"a0={_short_dec(event['source_anchor_alpha_inv'])}"
                f"{transport_text} "
                f"res={_signed_short_dec(event['residual_alpha'])}"
            )
        if stage == "complete":
            return (
                f"alpha^-1={_short_dec(event['alpha_inv'])} "
                f"P={_short_dec(event['p'])} "
                f"res={_signed_short_dec(event['alpha_fixed_point_residual'])}"
            )
        return ""


def _dec(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _percent(value: Any) -> float:
    try:
        return float(_dec(value))
    except Exception:
        return 0.0


def _short_dec(value: Any, sig: int = 12) -> str:
    dec = _dec(value)
    if dec.is_zero():
        return "0"
    return f"{dec:.{sig}g}"


def _signed_short_dec(value: Any, sig: int = 6) -> str:
    dec = _dec(value)
    sign = "+" if dec >= 0 else ""
    return f"{sign}{dec:.{sig}g}"


def _resolve_color(mode: str) -> bool:
    if mode == "always":
        return True
    if mode == "never":
        return False
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stderr.isatty()


def _build_endpoint_summary(
    report: dict[str, Any],
    *,
    hadron_closure_delta_alpha_inv: Decimal | None,
    compare_alpha_inv: Decimal,
    compare_alpha_inv_uncertainty: Decimal,
) -> dict[str, Any]:
    with localcontext() as ctx:
        ctx.prec = max(80, int(report["precision"]) + 20)
        source_alpha_inv = _dec(report["alpha_inv"])
        source_alpha = _dec(report["alpha"])
        source_alpha_from_inverse = Decimal(1) / source_alpha_inv
        source_p = _dec(report["p"])
        phi = _dec(report["phi"])
        sqrt_pi = _dec(report["sqrt_pi"])
        closure_delta = hadron_closure_delta_alpha_inv or Decimal(0)
        closed_alpha_inv = +(source_alpha_inv + closure_delta)
        closed_alpha = +(Decimal(1) / closed_alpha_inv)
        closed_p = +(phi + sqrt_pi / closed_alpha_inv)
        gap = +(closed_alpha_inv - compare_alpha_inv)
        sigma = +(gap / compare_alpha_inv_uncertainty) if compare_alpha_inv_uncertainty else None
        source_gap = +(source_alpha_inv - compare_alpha_inv)

    return {
        "row_class": (
            "oph_plus_empirical_hadron_closure"
            if hadron_closure_delta_alpha_inv is not None
            else "source_only_oph_audit"
        ),
        "source_fixed_point": {
            "alpha_inv": str(+source_alpha_inv),
            "alpha": str(+source_alpha),
            "alpha_from_inverse": str(+source_alpha_from_inverse),
            "P": str(+source_p),
            "fixed_point_residual_alpha": report["alpha_fixed_point_residual"],
        },
        "closure_delta_alpha_inv": str(+closure_delta),
        "closure_delta_label": (
            "empirical_hadron_and_same_scheme_endpoint_closure_delta"
            if hadron_closure_delta_alpha_inv is not None
            else "none"
        ),
        "closed_endpoint": {
            "alpha_inv": str(+closed_alpha_inv),
            "alpha": str(+closed_alpha),
            "P": str(+closed_p),
        },
        "comparison": {
            "reference": "CODATA 2022/NIST inverse fine-structure constant",
            "alpha_inv": str(+compare_alpha_inv),
            "alpha_inv_standard_uncertainty": str(+compare_alpha_inv_uncertainty),
            "closed_minus_reference_alpha_inv": str(+gap),
            "closed_minus_reference_sigma": str(+sigma) if sigma is not None else None,
            "source_minus_reference_alpha_inv": str(+source_gap),
        },
        "claim_boundary": (
            "The source fixed point is computed without the comparison value. The displayed endpoint "
            "row adds the declared empirical hadron/same-scheme closure packet; it is not a "
            "source-only OPH hadronic spectral theorem."
        ),
    }


def _print_summary(report: dict[str, Any], endpoint: dict[str, Any], palette: Palette) -> None:
    source = endpoint["source_fixed_point"]
    closed = endpoint["closed_endpoint"]
    comparison = endpoint["comparison"]
    running = report.get("structured_running") or {}

    print("")
    print(palette.bold("OPH Fine-Structure Fixed Point"))
    print(f"mode                         = {report['mode']}")
    print(f"row class                    = {endpoint['row_class']}")
    print("")
    print(palette.cyan("source fixed-point search"))
    print(f"  alpha^-1 source audit      = {source['alpha_inv']}")
    print(f"  alpha source audit         = {source['alpha']}")
    print(f"  P source audit             = {source['P']}")
    print(f"  fixed-point residual       = {source['fixed_point_residual_alpha']}")
    print("")
    print(palette.gold("transport and closure"))
    print(f"  source anchor a0(P)        = {report['source_anchor_alpha_inv']}")
    if running:
        print(f"  lepton transport           = {running.get('lepton_delta_alpha_inv')}")
        print(f"  quark transport screened   = {running.get('quark_delta_alpha_inv_screened')}")
        print(f"  implemented transport      = {running.get('total_delta_alpha_inv')}")
    print(f"  closure delta alpha^-1     = {endpoint['closure_delta_alpha_inv']}")
    print("")
    print(palette.green("endpoint after closure packet"))
    print(f"  alpha^-1(0)                = {closed['alpha_inv']}")
    print(f"  alpha(0)                   = {closed['alpha']}")
    print(f"  P                          = {closed['P']}")
    print("")
    print(palette.cyan("measurement comparison"))
    print(f"  reference alpha^-1         = {comparison['alpha_inv']} +/- {comparison['alpha_inv_standard_uncertainty']}")
    print(f"  closed - reference         = {comparison['closed_minus_reference_alpha_inv']}")
    print(f"  closed - reference sigma   = {comparison['closed_minus_reference_sigma']}")
    print(f"  source - reference         = {comparison['source_minus_reference_alpha_inv']}")
    print("")
    print(palette.dim(endpoint["claim_boundary"]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="derive_p.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Solve the OPH P/alpha fixed point and print the fine-structure endpoint.\n\n"
            "The source solve does not use the measurement. By default the final display row\n"
            "adds the declared empirical hadron/same-scheme closure packet and then compares\n"
            "the result with CODATA/NIST."
        ),
        epilog=(
            "Examples:\n"
            "  python3 derive_p.py\n"
            "  python3 derive_p.py --color always --precision 50 --max-iterations 40\n"
            "  python3 derive_p.py --no-hadron-closure\n"
            "  python3 derive_p.py --json --output runtime/report.json\n\n"
            "Notes:\n"
            "  * --json disables the live progress display unless --progress is explicitly set.\n"
            "  * Increase --max-iterations when you increase --precision and want more trusted digits.\n"
            "  * The default closure delta is the current ledger packet, not a source-only hadron theorem."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=MODES,
        default=DEFAULT_MODE,
        help="Alpha readout fed into P = phi + alpha*sqrt(pi).",
    )
    parser.add_argument("--precision", type=int, default=40, help="Decimal precision for the solver.")
    parser.add_argument("--su2-cutoff", type=int, default=120, help="Representation cutoff for the SU(2) edge sum.")
    parser.add_argument("--su3-cutoff", type=int, default=90, help="Representation cutoff for the SU(3) edge sum.")
    parser.add_argument("--scan-points", type=int, default=60, help="Alpha-space scan points used to bracket closure.")
    parser.add_argument("--max-iterations", type=int, default=20, help="Maximum outer fixed-point bisection steps.")
    parser.add_argument(
        "--hadron-closure-delta-alpha-inv",
        default=str(DEFAULT_HADRON_CLOSURE_DELTA_ALPHA_INV),
        help=(
            "Empirical hadron/same-scheme endpoint closure packet to add in inverse-alpha units. "
            "Use --no-hadron-closure to print only the source audit row."
        ),
    )
    parser.add_argument(
        "--no-hadron-closure",
        action="store_true",
        help="Do not add the empirical closure packet; print only the source fixed-point audit row.",
    )
    parser.add_argument(
        "--compare-alpha-inv",
        default=str(CODATA_2022_ALPHA_INV),
        help="Inverse-alpha comparison value used only after the solve.",
    )
    parser.add_argument(
        "--compare-alpha-inv-uncertainty",
        default=str(CODATA_2022_ALPHA_INV_UNCERTAINTY),
        help="One-sigma uncertainty for the comparison value.",
    )
    parser.add_argument("--json", action="store_true", help="Print the full report plus endpoint summary as JSON.")
    parser.add_argument("--output", help="Optional path for the JSON report.")
    parser.add_argument(
        "--progress",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Show the colored progress display. Defaults to on for human text output and off for JSON.",
    )
    parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="Color mode for progress and summary output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    use_progress = args.progress if args.progress is not None else not args.json
    palette = Palette(_resolve_color(args.color))
    progress = ProgressDisplay(palette) if use_progress else None

    report = build_report(
        precision=args.precision,
        mode=args.mode,
        su2_cutoff=args.su2_cutoff,
        su3_cutoff=args.su3_cutoff,
        scan_points=args.scan_points,
        max_iterations=args.max_iterations,
        progress=progress,
    )
    closure_delta = None if args.no_hadron_closure else _dec(args.hadron_closure_delta_alpha_inv)
    endpoint = _build_endpoint_summary(
        report,
        hadron_closure_delta_alpha_inv=closure_delta,
        compare_alpha_inv=_dec(args.compare_alpha_inv),
        compare_alpha_inv_uncertainty=_dec(args.compare_alpha_inv_uncertainty),
    )
    payload = {**report, "fine_structure_endpoint": endpoint}

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    _print_summary(report, endpoint, palette)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
