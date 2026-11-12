# Look-elsewhere control for the charged-lepton phase

The [lepton register](../lepton_register_round/README.md) reads the phase
`theta = 2/9` and gives `m_mu/m_e = 206.770316`, which is `+9.83 ppm` from the
CODATA 2022 value `206.7682827(46)`. The register and its claim row state that
this comparison is not blind. This package measures one part of the selection
freedom: how many simple rational phases land as close to the measured ratio
as `2/9` does.

The circulant and the particle assignment are those of the register:
square-root masses proportional to `1 + sqrt2 cos(theta + 2 pi k/3)`, with
electron, muon and tau on `k = 1, 2, 0`. The script checks its value at `2/9`
against the register receipt. The candidate family is every reduced fraction
`p/q` with `1 <= q <= Q` and `0 < p/q < pi/12` (the positive chamber), for
`Q = 9, 12, 30, 100`. A candidate passes when its relative deviation from the
CODATA ratio is at most that of `2/9`. As a planted control, the script stops
with an error unless `2/9` is in every family and is reported as a pass.

| Q | candidates | passes | expected passes, uniform phase | nearest other candidate |
| --- | --- | --- | --- | --- |
| 9 | 7 | 2/9 | 9.4e-6 | 1/5, -638698 ppm |
| 12 | 11 | 2/9 | 1.5e-5 | 1/5, -638698 ppm |
| 30 | 71 | 2/9 | 9.5e-5 | 5/23, -227038 ppm |
| 100 | 796 | 2/9 | 1.07e-3 | 21/95, -62749 ppm |

The window in `theta` has width `3.50e-7` rad; a phase uniform on the chamber
lands in it with probability `1.34e-6`. Among simple rationals, `2/9` is the
only one near the measured ratio. This is the size of the Koide-Brannen
coincidence in the data (Brannen's fit, 2006, gives `0.2222248(63)`).

The control does not count the freedom in choosing a construction that outputs
a given rational, and it tests no physical claim. The input ancestry of `2/9`
in this repository is in [PROVENANCE.md](PROVENANCE.md).

From the repository root, standard library only:

```sh
python -m model.lepton_phase_selection_control --write
python -m model.lepton_phase_selection_control --check
```

[results.json](results.json) holds every count, the window and the planted
control result.
