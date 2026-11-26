"""Exercise the replay CLI with the real verifier and an invalid certificate."""
import json
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


try:
    import flint
except ImportError:
    HAS_FLINT = False
else:
    HAS_FLINT = True


REPLAY = Path(__file__).resolve().with_name('replay.py')
LOAD = '''
import importlib.util
from pathlib import Path
import sys
from unittest import mock

path = Path(sys.argv.pop(1))
spec = importlib.util.spec_from_file_location('colour_replay', path)
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)
verifier = replay.load_verifier()
'''


@unittest.skipUnless(HAS_FLINT, 'Replay tests require python-flint')
class ReplayTests(unittest.TestCase):
    def run_cli(self, code):
        return subprocess.run(
            [sys.executable, '-I', '-c', textwrap.dedent(LOAD) + textwrap.dedent(code),
             str(REPLAY)], capture_output=True, text=True, check=False,
        )

    def test_replay_success_has_fixed_question_and_numerical_scope(self):
        completed = self.run_cli('''
            import contextlib
            import io
            import json

            output = io.StringIO()
            reference = {}
            real_run = verifier.run

            def checked_run(all_controls):
                result = real_run(all_controls)
                reference.update(result)
                return result

            with mock.patch.object(replay, 'load_verifier', return_value=verifier):
                with mock.patch.object(verifier, 'run', side_effect=checked_run) as run:
                    with contextlib.redirect_stdout(output):
                        rc = replay.main()
                    run.assert_called_once_with(False)
            summary = json.loads(output.getvalue())
            assert all(summary[key] == value for key, value in reference.items())
            print(output.getvalue(), end='')
            sys.exit(rc)
        ''')
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, '')
        summary = json.loads(completed.stdout)
        self.assertEqual(summary['status'], 'independently checked numerical enclosure')
        self.assertEqual(summary['revision'], '912d25da4efbdae9344e4198e75ac8ad93125a88')
        data = json.loads(REPLAY.with_name('certificate.json').read_text())
        self.assertEqual(summary['bracket'], [data['lower'], data['upper']])
        self.assertTrue(all(isinstance(value, str) for value in summary['bracket']))
        self.assertEqual(summary['board'], {
            'cells': 20, 'ports': 240, 'seams': 630, 'bridges': 30,
            'strength': 8, 'source': 'cell-zero rank-nine singlet complement',
        })
        self.assertEqual(summary['native_exposure'], '1')
        self.assertEqual(summary['integrated_triplet_tolerance'], '1/1000')
        self.assertEqual(summary['scope'],
                         'Numerical enclosure only. No kernel-checked Lean colour theorem. '
                         'Python refusal is not Lean refusal.')
        self.assertIn('home', summary)
        self.assertEqual(summary['preparation'], {
            'supplied_pure_state_probability': 1, 'refused_probability': 0,
            'failed_probability': 0,
        })

    def test_replay_invalid_certificate_has_no_success_summary(self):
        completed = self.run_cli('''
            from copy import deepcopy
            from fractions import Fraction

            check = verifier.check_certificate

            def invalid(data, *args):
                bad = deepcopy(data)
                bad['upper'] = str(Fraction(data['lower']) - Fraction(1, 10000))
                return check(bad, *args)

            with mock.patch.object(replay, 'load_verifier', return_value=verifier):
                with mock.patch.object(verifier, 'check_certificate', side_effect=invalid) as check_mock:
                    rc = replay.main()
                    check_mock.assert_called_once()
            sys.exit(rc)
        ''')
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn('claimed dual upper bound', completed.stderr)
        self.assertEqual(completed.stdout, '')


if __name__ == '__main__':
    unittest.main()
