# Input ancestry of the phase 2/9

AGENTS.md asks that settings chosen with target masses keep their input
ancestry explicit. This table gives the commits on `main` where the target
value and each rule that outputs `2/9` enter the repository. Each row is
reproducible with `git show <commit>` and the search string given.

| Commit | Commit date | Content | Search string |
| --- | --- | --- | --- |
| `88543fecf` | 2026-01-19 | Rule A, `delta = beta_EW Y_Q / N_g = (N_c + 1)/(2 N_c N_g) = 2/9`, and the target `delta_exp = 0.2222248 +/- 0.0000063`, in the same commit | `0.2222248` |
| `3ab16a2c9` | 2026-03-06 | Rule A restated: `delta = (N_c + 1)/(2 N_c N_g)` | `(N_c+1)/(2N_cN_g)` |
| `594a6f9bc` | 2026-06-15 | Ratio `206.770315972729` at `theta = 2/9` | `206.77031` |
| `32f099fba` | 2026-07-12 | CODATA ratio `206.76828270846718` as a regression witness | `206.7682827` |
| `9e8017777` | 2026-07-12 | Rule A restated as the phase ansatz `delta_e = beta_EW/(2 N_c N_g)` | `\beta_{\rm EW}/(2N_cN_g)` |
| `bfb876d65` | 2026-07-13 | Table row `206.7703160` against `206.76828`, `9.83 ppm` | `206.7703160` |
| `d54fcdbda` | 2026-11-06 | Rule B, two flag counts `p = 1/12`, `q = 1/6`, exclusive count `p + q - 2pq = 2/9` | `p+q-2pq` |
| `736c6d929` | 2026-11-11 | Register certificate with the exclusive read count and the check `abs(mu/e - 206.770316) < 5e-7` | `1/12 + 1/6 - 2/72` |

Two constructions output `2/9`. Rule A is a group count and appears in three
written forms; the forms agree because `Y_Q = 1/(2 N_c) = 1/6`. Rule B is the
register read count. The measured phase enters the repository in the same
commit as rule A. Rule B enters about ten months after the measured phase. From the same marginal counts `p = 1/12` and
`q = 1/6`, the combinations `p`, `q`, `pq`, `p + q - pq`, `p + q` and
`p + q - 2pq` give `1/12`, `1/6`, `1/72`, `17/72`, `1/4` and `2/9`; the claim
row `OPH-LEPTON-GENERATION-REGISTER` states that marginal counts without
independence allow any exclusive phase from `1/12` to `1/4`.
