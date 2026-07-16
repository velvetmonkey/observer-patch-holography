# Radiative pole packet scope study, CL-5 forward electroweak lane (2026-07-16)

Status: scope study only. No preregistration is consumed by this document and
no corrected (M_W, M_Z) pair is computed in it. The preregistered computation
is specified in `falsification/preregistered/ew_pole_packet_spec_2026-07-16.json`.

## 1. Object under study

The declared chain (`build_paper_d10` in
`code/particles/calibration/legacy_d10/particle_masses_paper_d10_d11.py`, plus
the two-law readout `strict_branch_two_law_evaluation` in
`code/particles/calibration/derive_wzh_residual_elimination_boundary.py` and
the caesium display adapter) emits

    (M_W, M_Z) = (80.33006, 91.11912) GeV

as a tree-level readout from the running couplings alpha_2(mz_run),
alpha_Y(mz_run) at the one-loop mZ fixed-point scale mz_run = 91.58833 GeV and
the transmutation vev. The chain key is
`mssm|beta4|P_sl3|law=zero_selector|z=z_tree`. The 2026-07-16 two-loop
transport repair executed under spec sha256 `5a91bbab...0bf7` and came back
adverse in the primary cell. That result excludes only the declared hybrid
MSSM-one-loop plus SM-two-loop prescription, not a general running-correction
family. The pole packet is a partial prescription study, not a surviving
physical correction family. The source chart has no complete map to a pole
observable.

## 2. What the on-shell packet contains, and what the declared chain absorbs

The Standard Model on-shell packet for the (M_W, M_Z) pair decomposes into
pieces with different input anchors. The mapping to the declared chain:

| Packet piece | Standard role | Status in the declared chain |
| --- | --- | --- |
| Delta r (Sirlin scheme; Denner arXiv:0709.1075 sect. 8, eq. with the vertex/box constant `(alpha/4 pi s_W^2)(6 + (7-4 s_W^2)/(2 s_W^2) log c_W^2)`) | converts the (G_F, alpha(0), M_Z) input set into M_W | not applicable as a correction. The chain consumes no G_F, no alpha(0), and no muon-decay amplitude. The O(1e-2) size of Delta r is dominated by the alpha(0) -> alpha(M_Z) vacuum-polarization jump, which the chain never performs. Delta r enters this lane only as a certification target for the transcribed self-energies. |
| Photonic vacuum polarization, Delta alpha_had | runs alpha(0) up to the weak scale | not represented as an explicit same-scheme endpoint transport. The chain's couplings arrive from alpha_U rather than a zero-momentum anchor, but that does not prove the physical contribution is absorbed. |
| kappa_Z / rho_Z effective-coupling corrections (Z-pole asymmetry form factors) | dress sin^2 theta_eff in asymmetry observables | not applicable. The pair readout consumes no asymmetry observable; no effective mixing angle is emitted for comparison. |
| Gauge-boson pole shift `M_pole^2 = m^2(mu) - Re Sigma_hat_T(m^2; mu)` | relates a scheme-declared running mass parameter to the propagator pole | candidate diagnostic only. The chain uses running couplings, but its transmutation vev has no completed renormalization or tadpole scheme. The chart masses therefore cannot yet be identified as the `m^2(mu)` input of this formula. |
| delta_rho z_stage3 switch, `MZ -> MZ / sqrt(1 + 3/(32 pi^2))` | the chain's single declared scheme switch | superseded inside this lane. The stage-3 divisor is a partial rho-type piece of the same self-energy packet; carrying it alongside the full Re Sigma_ZZ double-counts. Packet cells are z_tree only, and the z axis is retired for this lane (gate PP-03). |
| Tadpole contributions to the vev definition | distinguishes the tadpole-renormalized vev from the Fleischer-Jegerlehner parameter convention | open. Calling the transmutation vev an "actual vacuum value" does not select a renormalized tadpole prescription. The computed branch is one partial PRTS/Feynman-gauge convention; FJ and other vev definitions remain uncomputed and fail closed (PP-01/PP-05). |
| alpha_U pixel selector | fixes alpha_U from pixel_residual(alpha_2, alpha_3, P) = 0 at mz_run | invariant at fixed (alpha_U, mz_run): the packet changes no running coupling. The selector re-enters only through the fixed-point scale (tier B below). |
| mZ fixed point mu = MZ_tree(mu) | fixes the evaluation scale | the packet's one self-consistency channel. Re-declaring the fixed point on the pole mass, mu = MZ_pole(mu), moves mz_run, hence alpha_2, alpha_3 at the readout, hence the alpha_U root and v. This is the analog of the two-loop tier B re-solve, which shifted v by about 1 percent. |
| v/E_star transmutation | emits the vev | retained exactly. v is read as the scheme parameter at mz_run; its own scheme and scale completion stays an open gate (gate PP-05, same standing as GATE-2L-02). |
| Caesium display adapter | E_star units to GeV | absorbed. Multiplicative display constant; correction-neutral. |

Scope expectation recorded before computation: within this partial prescription the size is set by
`Re Sigma_hat_T / M^2` with couplings and internal masses of the declared
chain, of order alpha_2/(4 pi) times O(1..10) coefficients, comparable in raw
size to the two-loop transport shifts. The naive Delta r-based O(1e-2)
expectation conflates the input-scheme conversion (which the chain absorbs)
with the candidate self-energy shift. This order estimate does not supply the missing
physical readout identification.

## 3. Correction formulas and reference set

- Self-energies: A. Denner, "Techniques for the calculation of electroweak
  radiative corrections at the one-loop level...", Fortschr. Phys. 41 (1993)
  307, arXiv:0709.1075. Appendix B ("Self energies"): Sigma^W_T(k^2),
  Sigma^ZZ_T(k^2), Sigma^AZ_T(k^2), Sigma^AA_T(k^2), 't Hooft-Feynman gauge,
  tadpole-renormalized scheme (hat T = 0, sect. 3.3 eq. (RCT)). Coupling
  conventions appendix A: g_f^+ = -(s_W/c_W) Q_f,
  g_f^- = (I^3_{W,f} - s_W^2 Q_f)/(s_W c_W).
- Loop functions: A_0 and B_0 from sect. 4.4 (eq. (B0)); MS-bar finite parts
  are taken by Delta -> 0 at scale mu = mz_run.
- Sign convention: sect. 3.3 defines the transverse two-point function as
  Gamma^W_T(k^2) = -i (k^2 - M_W^2) - i Sigma^W_T(k^2), so the pole sits at
  M_pole^2 = m^2(mu) - Re Sigma_hat_T(M_pole^2; mu) once the MS-bar
  counterterm is absorbed into m^2(mu). Evaluation at k^2 = m_tree^2 differs
  from the iterated pole point at two-loop order (gate PP-06).
- Certification harness (measured-world numbers enter the harness only, never
  the chain): Denner sect. 8 input set (alpha = 1/137.0359895, M_Z = 91.177,
  G_F = 1.16637e-5, m_t = 140, M_H = 100, effective quark masses
  0.041/0.041/0.15/1.5/4.5, leptons 0.000511/0.10566/1.7841) must reproduce
  his quoted one-loop M_W = 80.23 GeV through the Delta r relation
  M_W^2 (1 - M_W^2/M_Z^2) = pi alpha / (sqrt 2 G_F) (1 + Delta r); Delta r
  must be mu-independent to numerical precision; the large-m_t limit of
  Sigma_ZZ(0)/M_Z^2 - Sigma_W(0)/M_W^2 must reproduce
  Delta rho = 3 alpha m_t^2 / (16 pi s_W^2 c_W^2 M_Z^2); Sigma_AA(0) must
  vanish; the closed-form B_0 must match direct Feynman-parameter quadrature.

## 4. Internal-input policy (Stage-5 values, never PDG)

Loop-internal masses come from the chain itself:

- M_W, M_Z inside the loops: the evaluated cell's own tree masses.
- s_W^2, c_W^2, alpha inside the loops: the evaluated cell's own effective
  tuple (sin^2 theta_eff of the cell's law; alpha = a_2p sin^2 theta_eff).
- Top and Higgs: the Stage-5 D11 literal core of the same chain,
  `integrate_d11_literal_core(build_paper_d10(P_sl3))`:
  mt_pole = 164.13057624202088, mt_MSbar = 154.77925772233598,
  mH_tree = 115.10126842614258 GeV. No PDG mass enters any loop.
- All other fermions massless, CKM = identity (the chain declares neither
  light Yukawas nor flavor structure).
- Stage-5 loop masses stay frozen at their baseline values inside the tier B
  re-solve; their alpha_U dependence enters the packet at two-loop order
  (gate PP-04).

## 5. Discrete menu (enumerated here, frozen in the spec)

1. tier: `A_readout_shift` (frozen baseline basis, correction on the readout
   only) | `B_pole_fixed_point` (fixed point re-declared as
   mu = MZ_pole(mu), alpha_U re-solved on the pixel residual at the new
   mz_run, v recomputed; the full self-consistent absorption).
2. mt_loop: `mt_pole_stage5` | `mt_msbar_stage5` (which internal top mass
   enters the loops; the reference parameterizes loops by pole masses, the
   chain's own scheme carries both).
3. value_law: `zero_selector` | `nonzero_carrier` (the declared two-law
   readout ambiguity, carried unchanged).

Eight cells, all emitted. The z axis is retired (section 2, gate PP-03). The
primary display cell is declared in the spec before any packet number exists.

## 6. Fail-closed gates carried by this lane

- PP-01 tadpole_fj_branch_uncertified: the FJ vev-convention alternative is
  declared, uncomputed, and gated; mt^4/M_H^2-enhanced difference noted.
- PP-02 higher_order_pole_terms: O(alpha alpha_s) and two-loop electroweak
  pole terms uncomputed.
- PP-03 z_stage3_superseded: the stage-3 divisor is retired inside this lane
  to prevent rho double-counting.
- PP-04 stage5_loop_masses_frozen: internal (mt, mH) frozen at baseline in
  tier B.
- PP-05 transmutation_vev_scheme_open: v carries no declared loop-order
  completion; read as the scheme parameter at mz_run.
- PP-06 pole_point_iteration: self-energies evaluated at the tree mass point;
  iteration to the pole is second order.
- PP-07 w_fixed_point_absent: the chain declares a Z fixed point only; M_W
  receives its pole shift at the readout and enters no scale condition.
