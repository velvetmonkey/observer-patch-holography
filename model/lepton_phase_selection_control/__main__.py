"""Regenerate or replay the look-elsewhere receipt for the charged-lepton phase."""
import argparse
import json
from pathlib import Path

from .control import result, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    value = result()
    path = Path(__file__).with_name('results.json')
    text = json.dumps(value, indent=1, sort_keys=True) + '\n'
    if args.write:
        path.write_text(text)
    elif json.loads(path.read_text()) != json.loads(text):
        raise SystemExit('the look-elsewhere receipt differs from its complete recomputation')
    print(summary(value))


if __name__ == '__main__':
    main()
