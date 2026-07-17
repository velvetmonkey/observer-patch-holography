#!/usr/bin/env python3
"""Verifier for the quantum regulator gluing evidence bundle (issue #529).

Exit code 0: every positive witness passes the gate and the bare
interface-projection countermodel is rejected with structured reasons.
Exit code 1: any positive witness fails, or the countermodel passes.

Usage:
    python3 code/regulator_gluing/verify_regulator_gluing_bundle.py
    python3 code/regulator_gluing/verify_regulator_gluing_bundle.py --bundle path.json
    python3 code/regulator_gluing/verify_regulator_gluing_bundle.py --show-maps
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from regulator_gluing_bundle import (  # noqa: E402
    ARTIFACT_PATH,
    build_bundle,
    run_bundle,
)


def format_entry(pair):
    re_part, im_part = pair
    if im_part == "0":
        return re_part
    if re_part == "0":
        return f"{im_part}i"
    return f"{re_part}+{im_part}i"


def print_map(recharting, indent="    "):
    if recharting.get("type") == "unitary":
        rows = recharting["matrix"]
        print(f"{indent}unitary U ({recharting['direction'][0]} <- {recharting['direction'][1]}):")
        for row in rows:
            print(f"{indent}  [" + ", ".join(format_entry(e) for e in row) + "]")
    elif recharting.get("type") == "algebra_isomorphism":
        print(f"{indent}algebra isomorphism "
              f"({recharting['direction'][0]} <- {recharting['direction'][1]}), "
              f"{len(recharting['generator_images'])} generator images")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=None,
                        help="verify a stored bundle JSON instead of the canonical build")
    parser.add_argument("--show-maps", action="store_true",
                        help="print every displayed overlap map")
    parser.add_argument("--emit", action="store_true",
                        help="write the artifact JSON to the runs directory")
    args = parser.parse_args()

    if args.bundle is not None:
        stored = json.loads(args.bundle.read_text())
        bundle = stored["bundle"] if "bundle" in stored else stored
    else:
        bundle = build_bundle()

    report = run_bundle(bundle)

    print(f"schema: {bundle['schema']}")
    print(f"issue:  {bundle['issue']}")
    print()

    failures = 0
    for witness, wreport in zip(bundle["witnesses"], report["witness_reports"]):
        status = "PASS" if wreport["passed"] else "FAIL"
        print(f"[{status}] witness {wreport['name']}")
        for overlap, oreport in zip(witness.get("overlaps", []), wreport.get("overlaps", [])):
            ostatus = "ok" if oreport["passed"] else "FAIL"
            checks = ", ".join(
                f"{c['name']}={'ok' if c['passed'] else 'FAIL'}" for c in oreport["checks"]
            )
            print(f"  overlap {oreport['edge']}: {ostatus} ({checks})")
            if args.show_maps:
                print_map(overlap["recharting"])
        for treport in wreport.get("triples", []):
            tstatus = "ok" if treport["passed"] else "FAIL"
            extra = ""
            if "measured_defect" in treport:
                extra = f", defect={format_entry(treport['measured_defect'])}"
            print(f"  triple {treport['patches']} [{treport['law']}]: {tstatus}{extra}")
        for qreport in wreport.get("quadruples", []):
            qstatus = "ok" if qreport["passed"] else "FAIL"
            print(f"  quadruple {qreport['patches']} 2-cocycle identity: {qstatus}")
        if not wreport["passed"]:
            failures += 1
            for reason in wreport["reasons"]:
                print(f"    reason {reason['code']}: {reason['detail']}")
        print()

    counter = report["countermodel_report"]
    if report["negative_gate_holds"]:
        print(f"[PASS] negative gate: countermodel {counter['name']} rejected")
        for reason in counter["reasons"]:
            print(f"  {reason['code']}: {reason['detail']}")
    else:
        print(f"[FAIL] negative gate: countermodel {counter['name']} was accepted; "
              "a bare interface projection must never pass")
        failures += 1
    print()

    if args.emit or args.bundle is None:
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT_PATH.write_text(json.dumps({"bundle": bundle, "report": report}, indent=2) + "\n")
        print(f"artifact: {ARTIFACT_PATH}")

    accepted = report["accepted"] and failures == 0
    print(f"bundle accepted: {accepted}")
    return 0 if accepted else 1


if __name__ == "__main__":
    sys.exit(main())
