# Finite colour leakage and arrival

This is an analytic argument awaiting formal check, with an independently
checked numerical enclosure. There is no Lean proof in this package.

## Fixed construction

The source is revision `912d25da4efbdae9344e4198e75ac8ad93125a88`.
The stored level-zero board has 240 ports, 600 internal seams and 30 bridges.
Every bridge is retained. The sector has one load on a blank background.
The contrast strength is 8. Exposure is 1 in the native evolution parameter.
The integrated triplet budget is 1/1000. These inputs are fixed before the
calculation. The exposure has no independent physical-time calibration.

For the native memory write W, the verifier checks the integer pattern
sqrt(2) W, its isometry identity, and G_memory W = W h_seam exactly.
The echo block formula therefore sends blank memory into blank memory under
the local Hamiltonian. Its restriction is

    h_seam = (I - SWAP)/2 + 8 (n_a - n_b)^2.

On the one-load sector each incident seam adds 17/2 to a diagonal and -1/2
to its endpoint off-diagonal. The degree reference adds 8(6-degree).
Thus the full native generator is 48 I + L/2. The verifier constructs all
240 by 240 entries by this route and compares them exactly with L/2 after
the constant is removed. It uses H = L/2 - 3 I. The extra phase changes no
probability or integrated occupation. The sum of the absolute entries in
each row of H is at most 3, so its operator norm is at most 3.

Let C be the cell adjacency and J its antipodal permutation. The declared
energy meter in singlet_flight uses

    P = (I-J)(I+C/sqrt(5))/4.

The verifier derives J from exact graph distances. Arithmetic over
Q(sqrt(5)) checks symmetry, P squared = P, trace(P) = 3,
C P = sqrt(5) P, and P_ii = 1/4 for every sharp port. This selects the
positive sqrt(5) triplet of the calibrated odd source. It is not a rank
fit to eigenvectors. The ideal local energy meter is supplied apparatus.
The compiled centre-pulse approximation is not used in these probabilities.
Q is the direct sum of all 20 cell projectors.

## Source coordinates and optimization

Write B = I-P in cell zero. Let S contain the nine columns of B listed in
the certificate, embedded into all 240 ports. These columns need not be
orthonormal. Set W = S* S. A strict interval LDL check of W establishes
independence. Since B has rank nine, S spans the whole allowed source.
Since S is a subset of the columns of an orthogonal projector, norm(S)<=1.
There is no error from a floating orthonormal basis.

Every allowed physical density matrix has the unique form S tau S*, where
tau is positive semidefinite and tr(W tau)=1. This representation includes
complex coherences and mixed preparations. Define

    A = S* U(1)* R U(1) S,
    G = integral_0^1 S* U(t)* Q U(t) S dt.

R retains every port outside cell zero. G has units of native exposure.
It measures integrated occupation on independent copies. Its expectation
is not a continuous-monitoring survival probability.

For a certificate vector v, the physical pure state is S v divided by
sqrt(v* W v). The verifier encloses v* G v/(v* W v) strictly below 1/1000
and v* A v/(v* W v) above the claimed lower bound. This establishes
feasibility without a claim that any exactly dark localized source exists.
The source is a supplied deterministic coherent preparation. Its preparation
success probability is 1; refusal and failed preparation probabilities are 0.
These are assumptions of this source domain, not a native source protocol
or postselection efficiencies.

For mu>=0, the matrix condition

    D = lambda W + mu G - A >= 0

implies tr(A tau)<=lambda+mu/1000 for every allowed tau. This follows by
tr(D tau)>=0, tr(W tau)=1 and the leakage constraint. No inversion of G is
used. Every leakage null direction and the equality case of the leakage
constraint is included. Strictly positive checked pivots give slack in the
dual certificate; equality with this upper endpoint is not asserted. The
bracket does not assert the rank or uniqueness of an exact optimizer.

## Outward error enclosure

The verifier uses python-flint 0.9.0 and Arb complex ball arithmetic at 192
bits. Decimal certificate parameters are rational decimal inputs enclosed
by Arb. The projector uses the positive Arb enclosure of sqrt(5), with its
exact algebraic identity checked separately. Every matrix operation rounds
outward. No floating eigenvalue is used by the verifier.

For 0<=t<=1, form the degree-40 Taylor polynomial

    X(t) = sum_(k=0)^40 (-i H)^k S t^k/k!.

The omitted series has norm at most

    e = (3^41/41!) / (1-3/42).

This geometric tail bound holds uniformly in t. The verifier integrates
X(t)* Q X(t) by all coefficient products, using the exact factor
1/(i+j+1). It also evaluates X(1)* R X(1). There is no quadrature error.
Unitarity and norm(S)<=1 give the matrix error bound

    eta = 2 e + e^2

for both A and G in operator norm. The same bound applies to the terminal
outside-triplet matrix. Arb also encloses the finite polynomial arithmetic.
For the dual, the verifier checks the polynomial matrix

    lambda W + mu G_poly - A_poly - (1+mu) eta I

by a strict Hermitian interval LDL factorization. Each Schur-complement
pivot has a positive lower endpoint. Hence the true D is positive definite.
For a witness, the error in each normalized quadratic form is at most
eta (v* v)/(v* W v). The verifier adds that symmetric outward error ball.
This accounts for propagation, integration, projector evaluation, source
normalization and positivity arithmetic. The exact algebraic input checks
have zero approximation error.

## Controls and outcomes

The certificate binds every source file to its blob at the pinned revision
and its SHA-256. The verifier reads the carrier NPZ with the standard
library and compares all its edges and degrees. It does not import the
producer or any native floating propagation code.

Planted changed-edge and changed-projector certificates must fail the input
binding. A bound tightened below the primal lower endpoint must fail the
dual objective check. A reduced lambda must fail the LDL check. A zero
source vector must fail normalization. These controls modify in-memory
copies; no historical file or receipt is edited.

The nonzero-arrival source is the certified feasible witness itself. Its
three mutually exclusive records are outside triplet, outside complement,
and home. Their probabilities sum to 1 with no division by detections.
The closed-bridge control removes only intercell off-diagonals, retaining
the original diagonal energies and the same source. Its generator is block
diagonal, so outside arrival is exactly zero. The verifier also propagates
that control and encloses its outcomes and integrated leakage. Keeping the
diagonal can produce local triplet occupation in this control.
