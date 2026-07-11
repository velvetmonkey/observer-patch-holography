# BD threshold and spectrum gate

This directory carries the reproducible gate for GitHub issue 368. The
Bouchard-Donagi papers determine a visible massless-cohomology branch. They do
not determine the stabilized moduli point, nonzero-mode spectrum, string scale,
hidden completion, or a map from its supersymmetric compactification to the
non-supersymmetric OPH low-energy branch.

The builder therefore has two outputs with different logical roles. It
reproduces the Higgs/top, stop, and one-loop gauge-running proxy coordinates
from frozen inputs. It separately emits a fail-closed certificate with
compatibility_evaluated set to false and promotion_allowed set to false.
Supplying benchmark MSSM values does not close the gate. The OPH low-energy
target used here has no supersymmetric partner sector. The interface accepts
either a conventional SUSY-breaking route with mediation and soft boundary
conditions, or a genuinely non-supersymmetric UV deformation or continuation.
To certify this BD candidate, the latter must be proved OPH-equivalent to the
BD branch and preserve its cited visible data. It is not established by a
projection label or hash: it must also prove its worldsheet or modular
consistency, anomaly cancellation, vacuum stability, spectrum, couplings, and
thresholds. An unrelated construction is a different candidate.

The source packet is:

    code/particles/data/oph_bd_threshold_spectrum_inputs.json

The generated bundle is:

    code/particles/runs/uv/oph_bd_threshold_spectrum/

Regenerate it from the repository root with:

    python3 code/particles/uv/build_oph_bd_threshold_spectrum_receipts.py

Verify the committed bundle bytes and the recorded local dependency hashes,
selectors, and precision without writing files:

    python3 code/particles/uv/build_oph_bd_threshold_spectrum_receipts.py --check

Run the focused tests with:

    python3 -m pytest -q code/particles/uv/test_oph_bd_threshold_spectrum_receipts.py

The builder requires every non-null UV receipt to have
`status=hash_and_envelope_verified`, validates its repository-relative path and
SHA-256 value, and binds its JSON envelope to issue 368, the exact BD branch,
and the named input slot. This verifies identity and bytes, not the receipt's
scientific content. It does not download the external literature sources;
their independently checked hashes are recorded for a separate fetch audit.

This bundle is deliberately an open-evidence generator, not a compatibility
evaluator: both promotion flags remain false even if all receipt slots are
filled. A future evaluator may consume a complete, hash/envelope-bound packet only after
it also performs a real forward spectrum run, threshold matching in one
declared scheme, and the physical-moduli rank test. Target-side proxy agreement
alone can never alter either promotion flag.
