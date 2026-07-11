# Pinned D10/D11 basis

`particle_masses_paper_d10_d11.py` is the repository-local copy of the D10/D11 equation implementation previously available only in the workspace archive at `arXiv/RC1/ancillary/code/particles/`.

It is vendored so the current electroweak calibration and hierarchy tests are reproducible from this repository alone. `_legacy_d10.py` loads this pinned copy by default; `OPH_LEGACY_PARTICLE_DIR` remains an explicit developer override for archive comparisons.

This module supplies the declared equation basis. It does not turn target-anchored comparisons into predictions, and consumers must continue to label reference-fed outputs as diagnostics or compare-only artifacts.
