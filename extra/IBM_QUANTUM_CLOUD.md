# IBM Quantum Cloud Evidence for OPH

## Informal story

If OPH is right, then the local quantum structure of reality has a specific
form. Small toy sectors provide controlled places to test implementations of
that structure on IBM quantum hardware. The first campaign checked whether
prepared OPH-motivated states survived hardware execution and readout. A later
blinded campaign tested a stronger, generative question: whether a bounded
patch could read a local boundary record and apply the preregistered repair
move on two held-out backend/layout roles.

- Stage 1 asks a structural question: do OPH-like local states look more Markovian and more recoverable than generic or strongly non-Markovian controls?
- `Z_3` asks whether the simplest reduced-sector encoding is internally self-consistent.
- `Z_5` asks for a sharp exact-ratio target: does the measured ratio land near the OPH golden-ratio value?
- `S_3` asks the same kind of question in the first nonabelian case, where representation dimensions matter and the target ratio is `2`.
- The blinded generative benchmark asks whether a measured record, rather than
  an initial amplitude alone, selects the correct finite repair against frozen
  open-loop, delayed, shuffled, inverted, state-preparation, noise, label, and
  decoy controls.

The first campaign is state-preparation and readout consistency evidence. The
blinded campaign is implementation evidence for an observer-like self-reading
patch with local state, a measured boundary, a record, conditional feedback,
final readback, append-only receipts, and a public evidence bundle. Neither
campaign distinguishes OPH from unrestricted quantum mechanics.

## What these tests actually are

The names `Z_3`, `Z_5`, and `S_3` come from simple symmetry groups.

- `Z_3` means a 3-step cyclic symmetry: imagine a clock with three positions.
- `Z_5` means a 5-step cyclic symmetry: the same idea, but with five positions.
- `S_3` means the six permutations of three objects: it is the smallest genuinely nonabelian case, so order matters.

These are small toy symmetry systems. They are useful because OPH makes clean statements about what the reduced local probability pattern should look like in such sectors. Failure in these tiny cases would be a serious warning sign. Success in these cases is evidence that the OPH structural picture is pointing in the right direction.

## What the hardware is doing, informally

The original exact-ratio experiments have the same broad shape:

1. pick a tiny reduced sector where OPH predicts a definite probability structure;
2. encode that sector into 2 or 3 qubits;
3. prepare the corresponding state on a real IBM device;
4. measure many shots;
5. reconstruct the probabilities from the counts;
6. compare the measured pattern with the OPH target.

The blinded generative experiment instead prepares balanced finite inputs,
measures a decision record, conditionally applies repair, and retains every
seven-bit joint outcome. Standard quantum mechanics predicts both the prepared
states and this programmed dynamic instrument. The scientific question is
therefore whether the engineered self-reading implementation passes its frozen
reduced-controller nulls, not whether IBM hardware violates or outperforms
standard quantum theory.

## The basic math

For the exact-ratio experiments, the reduced-sector probabilities are modeled in heat-kernel form:

```math
p_R(t) \propto d_R e^{-t \lambda_R}.
```

Here:

- `R` labels the reduced sector or representation;
- `d_R` is its dimension;
- `\lambda_R` is the Laplacian eigenvalue for that sector;
- `t` is the effective heat-kernel time.

The intuition is straightforward:

- sectors with larger `\lambda_R` are more suppressed;
- sectors with larger dimension `d_R` get more multiplicity weight;
- `t` controls how strongly the suppression acts.

So the experiment is really checking whether the relative weights of the measured sectors fall off with the OPH-predicted exponential pattern.

The measured probabilities are then turned into log-gaps

```math
\Delta_R = -\log(p_R/p_0),
```

or, in the `S_3` nonabelian case,

```math
\Delta_{\mathrm{std}} = -\log\!\left(\frac{p_{\mathrm{std}}/2}{p_0}\right),
```

because the standard representation has dimension `2`.

Why take logs at all? Because an exponential law becomes linear after the log. If

```math
p_R \propto e^{-t\lambda_R},
```

then the corresponding gap behaves like

```math
\Delta_R \sim t \lambda_R.
```

That means ratios of gaps should reproduce ratios of eigenvalues. `Z_5` and `S_3` are useful because they turn the test into a clean number-comparison problem.

The concrete tests are:

### Stage 1: Markov / recoverability

For a 3-qubit local state `\rho_{ABC}`, we reconstruct the density matrix from Pauli tomography and evaluate the conditional mutual information

```math
I(A:C|B)=S_{AB}+S_{BC}-S_B-S_{ABC},
```

along with Petz-recovery quality. OPH favors the direction "lower CMI, better recoverability" for more structured local states.

Informally, conditional mutual information asks: conditioned on the middle subsystem `B`, how much extra correlation remains between the two ends `A` and `C`? Smaller values mean the state is closer to the kind of locally consistent, recoverable structure OPH expects.

### `Z_3`

`Z_3` is the sanity check. The two nontrivial sectors have the same eigenvalue, so extracting `t` from either one should agree:

```math
t_1 = -\frac{1}{3}\log(p_1/p_0), \qquad
t_2 = -\frac{1}{3}\log(p_2/p_0).
```

If `t_1` and `t_2` agree, the reduced-sector preparation and readout path is behaving coherently.

`Z_3` is the pipeline sanity check. It tells us whether the reduced-sector preparation and readout path is internally consistent before the sharper ratio claims are interpreted.

### `Z_5`

`Z_5` is the sharp abelian ratio test. The two nontrivial gap scales satisfy

```math
\frac{\Delta_2}{\Delta_1} = \frac{\lambda_2}{\lambda_1} = \varphi^2 \approx 2.618,
```

where `\varphi` is the golden ratio.

That makes `Z_5` much stronger than a vague "looks about right" test. The obvious wrong alternatives, such as `2` and `4`, are well separated from the OPH target.

`Z_5` matters because it asks for a very specific nontrivial number with very little room for interpretation.

### `S_3`

`S_3` is the first nonabelian exact-ratio test. The gauge-invariant one-plaquette sector is 3-dimensional, with representations

- trivial, dimension `1`
- sign, dimension `1`
- standard, dimension `2`

and OPH-normalized Laplacian eigenvalues

```math
\lambda_{\mathrm{triv}} = 0,\qquad
\lambda_{\mathrm{sign}} = 6,\qquad
\lambda_{\mathrm{std}} = 3.
```

So the parameter-free prediction is

```math
\frac{\Delta_{\mathrm{sign}}}{\Delta_{\mathrm{std}}} = 2.
```

`S_3` is the first nonabelian case in this ladder. It is the first test where the representation dimension plays an essential role in the observable.

## Public code and data

The runnable code and representative raw outputs are stored in:

- `code/ibm_quantum_cloud/programs/`
- `code/ibm_quantum_cloud/qc_data/`
- `code/ibm_quantum_cloud/runs/issue_509_20260711_v2/`

The public data bundle includes the main Stage 1, `Z_3`, `Z_5`, and `S_3`
hardware outputs, the `S_3` layout diagnostic, and the complete blinded
generative run: manifest, lock, reveal, provider job IDs, raw joined counts,
calibration receipts, packet, blind report, hashes, and replay commands.

## Results

In the tables below, `Prepared t` is the operating point used to prepare the state. The main tested observable depends on the experiment.

- In `Z_3`, the tested observable is the extracted heat-kernel time, so the comparison is prepared `t` versus measured `t`.
- In `Z_5`, the tested observable is the ratio `Δ₂/Δ₁`, so the comparison is expected `φ²` versus measured `Δ₂/Δ₁`.
- In `S_3`, the tested observable is the ratio `Δ_sign/Δ_std`, so the comparison is expected `2` versus measured ratio.

### Stage 1: positive on two real backends

Hardware runs:

- `ibm_marrakesh`, job `d6t4da6sh9gc73di7720`
- `ibm_fez`, job `d6t4ejngtkcc73cm8l6g`

OPH prediction and reason:

OPH favors locally structured states with lower conditional mutual information and better recoverability. For this benchmark, that gives three direct expectations:

- `CMI(structured_theta_0.00) < CMI(random_seed_2)`
- `CMI(structured_theta_0.00) < CMI(ghz_control)`
- `Petz fidelity(structured_theta_0.00) > Petz fidelity(random_seed_2) > Petz fidelity(ghz_control)`

Measured comparison:

| OPH prediction | Expected relation | `ibm_marrakesh` | `ibm_fez` | Result |
| --- | --- | --- | --- | --- |
| structured state has lower CMI than random control | true | `0.2309 < 0.3890` | `0.1498 < 0.4992` | pass |
| structured state has lower CMI than GHZ control | true | `0.2309 < 0.9474` | `0.1498 < 0.9166` | pass |
| recoverability ranks structured > random > GHZ | true | `0.9297 > 0.8649 > 0.6066` | `0.9479 > 0.8117 > 0.6449` | pass |

Representative reconstructed values:

| Backend | State | CMI (bits) | Petz fidelity |
| --- | --- | ---: | ---: |
| `ibm_marrakesh` | `structured_theta_0.00` | `0.2309` | `0.9297` |
| `ibm_marrakesh` | `random_seed_2` | `0.3890` | `0.8649` |
| `ibm_marrakesh` | `ghz_control` | `0.9474` | `0.6066` |
| `ibm_fez` | `structured_theta_0.00` | `0.1498` | `0.9479` |
| `ibm_fez` | `random_seed_2` | `0.4992` | `0.8117` |
| `ibm_fez` | `ghz_control` | `0.9166` | `0.6449` |

On both backends, the most structured state reconstructs below both controls in CMI, and recoverability worsens as structure is reduced. That is the OPH-favored direction.

The Stage 1 export also preserves the fixed random-control choice recorded in the run catalog: `random_seed_2` was selected from a small candidate seed set by exact CMI before the hardware run.

### `Z_3`: clean pass

Hardware run:

- `ibm_marrakesh`, job `d6t4ic790okc73et0n4g`

OPH prediction and reason:

In `Z_3`, the two nontrivial sectors have the same eigenvalue `lambda = 3`, so both channels should return the same heat-kernel time. The expected measured value is therefore the prepared `t` itself.

| Prepared `t` | Expected measured `t` | Mean measured `t` | Abs. error | Internal abs. `t_q1 - t_q2` | Leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| `0.30` | `0.3000` | `0.3162` | `0.0162` | `0.0142` | `0.10%` |
| `0.60` | `0.6000` | `0.6147` | `0.0147` | `0.0034` | `0.07%` |
| `0.90` | `0.9000` | `0.9153` | `0.0153` | `0.0043` | `0.05%` |

The extracted `t` value stays within about `0.02` of the prepared `t` at all three operating points, and the two independent extractions agree closely. This is a clean internal-consistency success.

### `Z_5`: repeated golden-ratio support

Hardware runs:

- `ibm_marrakesh`, job `d6t4iiv90okc73et0nbg`
- `ibm_marrakesh`, job `d6t4rkjbjfas73fp65m0`
- `ibm_fez`, job `d6t4ipvgtkcc73cm8qg0`
- focused high-shot `ibm_marrakesh` rerun, job `d6t50e790okc73et186g`

OPH prediction and reason:

In `Z_5`, the gap ratio is fixed by the Laplacian spectrum. OPH predicts:

`Delta2 / Delta1 = lambda2 / lambda1 = phi^2 ~= 2.6180`

So the expected value at every prepared `t` is the same number, `2.6180`.

Main `ibm_marrakesh` sweep:

| Prepared `t` | Expected `Delta2 / Delta1` | Measured `Delta2 / Delta1` | Abs. ratio error | Relative error | Internal abs. `t1 - t2` | Leakage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `0.30` | `2.6180` | `2.5974` | `0.0207` | `0.8%` | `0.0025` | `0.29%` |
| `0.60` | `2.6180` | `2.7383` | `0.1203` | `4.6%` | `0.0268` | `0.39%` |
| `0.90` | `2.6180` | `2.5786` | `0.0395` | `1.5%` | `0.0137` | `0.24%` |

Second `ibm_marrakesh` sweep:

| Prepared `t` | Expected `Delta2 / Delta1` | Measured `Delta2 / Delta1` | Abs. ratio error | Relative error | Internal abs. `t1 - t2` | Leakage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `0.30` | `2.6180` | `2.4532` | `0.1649` | `6.3%` | `0.0199` | `0.22%` |
| `0.60` | `2.6180` | `2.8778` | `0.2597` | `9.9%` | `0.0556` | `0.22%` |
| `0.90` | `2.6180` | `2.6488` | `0.0308` | `1.2%` | `0.0104` | `0.39%` |

`ibm_fez` replication:

| Prepared `t` | Expected `Delta2 / Delta1` | Measured `Delta2 / Delta1` | Abs. ratio error | Relative error | Internal abs. `t1 - t2` | Leakage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `0.30` | `2.6180` | `2.7262` | `0.1082` | `4.1%` | `0.0127` | `1.03%` |
| `0.60` | `2.6180` | `2.4068` | `0.2113` | `8.1%` | `0.0521` | `0.66%` |
| `0.90` | `2.6180` | `2.4610` | `0.1570` | `6.0%` | `0.0537` | `0.54%` |

Focused high-shot confirmation at `t = 0.90`:

| Backend | Expected `Delta2 / Delta1` | Measured `Delta2 / Delta1` | Abs. ratio error | Relative error | Internal abs. `t1 - t2` | Leakage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `ibm_marrakesh` | `2.6180` | `2.5498` | `0.0682` | `2.6%` | `0.0238` | `0.31%` |

The best `ibm_marrakesh` points land within `0.8%`, `1.2%`, and `1.5%` of the OPH target. The noisier points remain in the same neighborhood. The `ibm_fez` run is visibly weaker, but it does not produce a clean contradiction.

### `S_3`: layout bias diagnosed and corrected

Hardware diagnostic bundle:

- base layout `ibm_marrakesh`, job `d6t5c47gtkcc73cm9pd0`
- reversed layout `ibm_marrakesh`, job `d6t5cdvgtkcc73cm9pr0`
- direct reversed-layout confirmation, job `d6t5csmsh9gc73di8e8g`

OPH prediction and reason:

In `S_3`, the one-plaquette reduced sector has `lambda_sign = 6` and `lambda_std = 3`, so OPH predicts:

`Delta_sign / Delta_std = 2.0000`

At `t = 0.60`:

| Configuration | Expected ratio | Measured ratio | Abs. ratio error | Relative error | `Δt/t` | Leakage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| base layout `[7, 8]`, raw | `2.0000` | `1.8536` | `0.1464` | `7.3%` | `-0.0760` | `0.08%` |
| base layout `[7, 8]`, mitigated | `2.0000` | `1.8724` | `0.1276` | `6.4%` | `-0.0659` | `0.06%` |
| reversed layout `[8, 7]`, raw | `2.0000` | `2.0348` | `0.0348` | `1.7%` | `0.0172` | `0.04%` |
| reversed layout `[8, 7]`, mitigated | `2.0000` | `2.0299` | `0.0299` | `1.5%` | `0.0148` | `0.01%` |

Direct confirmation of the corrected mapping:

- `ibm_marrakesh`, seed `17`, job `d6t5csmsh9gc73di8e8g`
- expected ratio `2.0000`
- measured ratio `2.0657`
- abs. ratio error `0.0657`
- relative error `3.3%`
- `Δt/t = 0.0323`
- leakage `0.01%`

This result matters because the initial low `S_3` values were largely a layout-dependent hardware bias. After that bias is diagnosed and the mapping is corrected, the nonabelian target ratio returns on hardware very close to `2`.

### Blinded generative repair: preregistered pass on two QPUs

The production-random `issue509-20260711-v2` run used `ibm_fez` for the
development role and submitted the held-out `ibm_kingston` role only after the
development jobs had completed. The run contained 3,104 circuits, 606,208
shots, and 14 completed IBM Runtime jobs. No shots were dropped or
postselected.

The frozen blind report passed every calibration, leakage, completeness, and
shot-conservation gate. Record-gated repair exceeded the preregistered
conditional-likelihood threshold against every required null on each backend
and pooled. The weakest comparison was the 256-component label/layout mixture,
with likelihood ratio approximately `256`; all other primary comparisons had
per-backend log-likelihood ratios above `77,000`. The committed reference
label/layout was the unique top component among 256 possibilities.

After the blind report was file-hashed, the reveal commitment and all 3,104
normalized-OpenQASM logical-circuit hashes verified. The raw receipts and exact
replay are public in
`code/ibm_quantum_cloud/runs/issue_509_20260711_v2/`.

## Assessment of the evidence

> On IBM quantum hardware, the exact-ratio campaign validates preparation and
> readout of OPH-motivated reduced-sector states. The blinded generative
> campaign adds stronger evidence that an engineered finite self-reading patch
> can execute record-gated repair against its frozen reduced-controller nulls
> on two QPUs.

The main caveats are:

- these are IBM hardware consistency benchmarks for OPH-inspired reduced-sector states;
- `S_3` revealed a real layout-dependent hardware bias, and the corrected layout restores the target ratio;
- `Z_5` and `S_3` show that OPH-shaped small-sector states can be prepared and read out with nontrivial fidelity on real hardware.
- the generative pass tests an engineered observer-like implementation, not
  OPH against unrestricted quantum mechanics;
- the reported primary values are conditional likelihood ratios, not Bayes
  factors, because calibration uncertainty is stress-tested by frozen
  sensitivity bounds rather than fully marginalized.

The new result is stronger than state preparation alone because the output is
selected by a measured finite record and feedback. It is still an
implementation-level result under standard quantum mechanics.

## Interpretation boundary

These experiments cover small reduced sectors and one bounded self-reading
implementation.

- The exact-ratio experiments directly prepare OPH-motivated reduced-sector amplitudes, so the result is that the predicted structure survives real-hardware preparation and measurement in a nontrivial way.
- Stage 1 is a real structural success, recoverability behavior by itself also appears in frameworks beyond OPH, and its random control was chosen from a fixed candidate pool.
- The generative experiment instantiates local state, a port or boundary,
  readback, a record, conditional feedback, and public receipts. Its pass says
  that this finite implementation beats the listed frozen controllers, label
  mixture, calibrated-noise model, and decoy checks.

Standard quantum mechanics predicts the programmed circuits. These results do
not establish OPH claims about relativity, the Standard Model, cosmology, or
ontology, and they do not compare OPH with unrestricted quantum theory. They
provide auditable hardware evidence for the narrower prepared-state and
self-reading-implementation claims stated above.
