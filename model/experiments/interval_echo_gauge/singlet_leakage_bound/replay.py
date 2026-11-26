"""Show the fixed numerical question after one certificate check."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys


def load_verifier():
    path = Path(__file__).resolve().with_name('verify.py')
    spec = importlib.util.spec_from_file_location('colour_verifier', path)
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    return verifier


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result = load_verifier().run(False)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    summary = dict(result)
    summary.update({
        'scope': 'Numerical enclosure only. No kernel-checked Lean colour theorem. '
                 'Python refusal is not Lean refusal.',
        'board': {
            'cells': 20, 'ports': 240, 'seams': 630, 'bridges': 30,
            'strength': 8, 'source': 'cell-zero rank-nine singlet complement',
        },
        'native_exposure': '1',
        'integrated_triplet_tolerance': '1/1000',
    })
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
