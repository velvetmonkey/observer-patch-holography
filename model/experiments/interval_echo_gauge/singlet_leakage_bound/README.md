# Colour leakage limits on transport

A source in the colour-singlet complement of cell zero can send about
3.098 percent of its probability outside that cell by native exposure 1,
while its integrated local triplet occupation is at most 0.001. On the fixed
20-cell Interval Echo board, the certified optimum lies in

    [0.030977574608, 0.030977796786472].

The width is 0.000000222178472, below the requested 0.001. The result is an
independently checked numerical enclosure. It is not a kernel-checked
Lean proof. It includes all coherent and mixed source density matrices,
all 240 ports, all 30 bridges and the home outcome.

This constrains approximate singlet motion at this exposure and tolerance:
the allowed source can transport a small nonzero fraction, and no allowed
source transports more than the upper endpoint. Integrated occupation is
measured on independent copies. It is not the probability of a continuously
monitored trajectory. The guarded orbital triplet is a declared colour
representation with a supplied energy meter. This result supplies no
particle identity, physical quark colour, empirical prediction, continuum
limit, global OPH obstruction or maintainer approval.

| Input | Scope |
| --- | --- |
| Source | Revision 912d25da4efbdae9344e4198e75ac8ad93125a88 |
| Board | Stored level-zero federation, 20 complete cells, 630 seams |
| Law | Native blank-memory isolated one-load restriction, strength 8 |
| Preparation | Any density matrix in the nine-dimensional cell-zero singlet complement |
| Time | Native exposure 1, supplied timing |
| Tolerance | Integral of total triplet occupation at most 1/1000 |
| Readout | Outside triplet, outside complement, home; all outcomes retained |
| Preparation losses | Supplied ideal preparation, success 1, refusal 0, failure 0 |
| Arithmetic | Exact input checks and 192-bit outward-rounded Arb enclosures |

The exact rational bracket and witness coordinates are in
[certificate.json](certificate.json). [results.json](results.json) retains the
verifier output, including the outcome probabilities and rejected controls. [DERIVATION.md](DERIVATION.md) gives the
source map, optimization reduction and error budget.
[verify.py](verify.py) checks the certificate without an optimizer or NumPy.
It reads the pinned Git blobs, checks the native restriction and intended
projector, computes the propagation and integral with a bounded Taylor
series, checks the primal witness, and checks the dual matrix by interval
LDL. Its terminal records include the home probability and preparation
losses. `--all-controls` also rejects corrupted inputs and bounds and runs
the closed-bridge control with the same source. The accepted witness itself
has nonzero arrival.

## Replay

Use Python 3.12 and python-flint 0.9.0. Install dependencies only inside a
private environment. The checkout must contain the pinned source commit.
From the repository root:

```sh
python3 -m venv /path/to/private/environment
/path/to/private/environment/bin/python3 -m pip install --prefix /path/to/private/environment python-flint==0.9.0
/path/to/private/environment/bin/python3 -I model/experiments/interval_echo_gauge/singlet_leakage_bound/verify.py --all-controls
```

In the lane estate, run the same Python command through `suiterun`. The
bound does not depend on the floating search program
[derive.py](derive.py). That program proposes certificate data using NumPy
2.5.5 and SciPy 1.18.1. It can be run from the repository root with those
packages installed in the same private environment:

```sh
/path/to/private/environment/bin/python3 -I model/experiments/interval_echo_gauge/singlet_leakage_bound/derive.py
```

The producer regenerates the certificate with its own mechanism. A floating
search result alone carries no certificate status. The independent verifier
must accept any regenerated data before its bracket is used. The source
file hashes in the certificate are checked against both the working files
and the exact pinned commit. No existing file is changed by either command.

Acceptance 1 to 3 and 5 to 6 are covered by the verifier, controls and
derivation. Acceptance 4 is satisfied by the explicit numerical-enclosure
label: no formal-proof claim is made and no Lean file is supplied. The
smallest separate experiment is to hold the board and source domain fixed
and test another predeclared exposure or leakage tolerance. That would be
a separate finite test with its own certificate.
