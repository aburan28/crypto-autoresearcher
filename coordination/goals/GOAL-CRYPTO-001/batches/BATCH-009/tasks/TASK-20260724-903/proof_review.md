# Independent proof review: TASK-20260724-903

Verdict: `CONFIRM`  
Gaps closed: `yes`  
Breakthrough claimed: `false`

The producer verdict `PROOF_PACKET_COMPLETE` is supported only within the
packet's stated boundary: the exact right-comb, original target-sectioned
Semaev Newton hull and a separately scoped fresh-uniform-mask bridge. This is
a negative mechanism gate, not a cryptographic breakthrough or a general
lower bound.

## Snapshot integrity

I reviewed the producer files from commit
`efcc65cab393e659ef9e43c77735547a4cf6d58c`, not working-tree copies. The
commit is reachable from the review head and changes exactly the two producer
artifacts plus the declared snapshot receipt. Recomputed SHA-256 values are:

- `proof_packet.yaml`:
  `f7995f7f201752c5df5223efc9bc583b01b4e9b0d0cc9ddb0a237e4381632f0f`
- `normalization_locked_proof.md`:
  `c72df71108d7e0b18a37d8282594f5e9edf22ec455b14e399e921695afa85aed`

They match the receipt. The receipt embedded at the named snapshot still has
`pending_post_commit` status and null commit fields; the task card supplies
the immutable commit, and the independent reachability, path-scope, and hash
checks above are the basis of this review. Dispatcher acceptance remains a
Coordinator concern, not a premise of the mathematical verdict.

## 1. Normalization and leading unit

This gap is closed.

The packet freezes the coefficient ring, resultant convention, base
polynomials, argument order, and the entire right-comb recurrence. It also
forbids every post-resultant operation that could introduce a
specialization-dependent scalar.

For
\[
f(Z)=S_{s-1}(X_1,\ldots,X_{s-2},Z),
\]
the coefficient of \(X_s^2\) in
\(S_3(X_{s-1},X_s,Z)\) is exactly
\((X_{s-1}-Z)^2\). Therefore the coefficient of
\(X_s^{2D_{s-1}}\) in the locked resultant is
\[
\operatorname{Res}_Z(f,(X_{s-1}-Z)^2)
  =f(X_{s-1})^2.
\]
The factor is exactly \(1_R\), not a declared generically nonzero scalar.
Exact symmetry gives the same identity in every variable. At a box corner,
degree \(D_s=2D_{s-1}\) forces the unique split
\(D_{s-1}+D_{s-1}\), while exponent zero forces \(0+0\). Thus the
corner-square recurrence has no hidden convolution.

The cheapest hostile mutation is to multiply one resultant output by \(A\).
That factor is generically nonzero but is not a unit of the frozen ring and
vanishes on the allowed nonsingular branch \(A=0,\ B\ne0\). The packet rejects
this mutation both as forbidden postprocessing and because the replayed
leading factor is no longer \(1_R\).

## 2. All-zero corner and degeneracies

This gap is closed set-theoretically; no multiplicity statement is needed.

For \(B\ne0\), every lift of zero is \(P_0\) or \(-P_0\). The first \(s-1\)
lifts therefore sum to \([r]P_0\) with
\[
r\in\{-(s-1),-(s-3),\ldots,s-3,s-1\}.
\]
When that sum is affine, the last point is uniquely its negative and gives
the root \(x([r]P_0)\). When it is the identity, no finite last
\(x\)-coordinate can cancel it. The pointwise summation-polynomial
biconditional supplies both directions, so torsion, opposite-point
collisions, and repeated \(x\)-coordinates can only merge or omit listed
roots.

For \(B=0\), nonsingularity forces \(A\ne0\), and the only lift is the
two-torsion point \(P_0=(0,0)\). Odd \(s\) gives no finite root; even \(s\)
gives exactly \(t=0\). This agrees with the parity of every displayed
index. The finite set of possible partial sums also leaves some finite
target outside it over the infinite algebraic closure, proving that no
\(F_s\) specializes to the zero polynomial. The exact pointwise
biconditional excludes any further finite root caused by a degree drop or
an intermediate projective common root.

The corner formulas then give
\[
\{0\}\cup\bigcup_{s=3}^{m}V(F_s)
 =\{x([r]P_0):1\le r\le m-1,\ [r]P_0\ne\mathcal O\}.
\]
The forward inclusion follows from \(|r|\le s-1\); the reverse inclusion
uses the \(t^{D_m}\) corner for \(r=1\) and \(s=r+1\) for every
\(2\le r\le m-1\).

## 3. Newton/BKK consequence

Outside the exact exception set all \(2^{m-1}\) box vertices occur, so the
Newton hull is the full degree box. Inside it, at least one box vertex is
absent; a vertex of a box cannot be reconstructed as a convex combination of
other points in that box, so the hull is proper.

For \(n=m-1\) nonexceptional original sections, all \(n\) polytopes are
\([0,D_m]^n\), and normalized mixed volume is
\[
n!D_m^n=(m-1)!\,2^{(m-1)(m-2)}.
\]
This equals the multigraded box-Bezout count. It does not imply equal sparse
and dense runtime, generic structured coefficients, or a lower bound for a
lifted, Gröbner, arithmetic-circuit, unsectioned, or alternative-curve-model
formulation. A proper exceptional hull also gives no positive solver or
relation credit without a separate mixed-volume and end-to-end certificate.

## 4. Exception bridge and common cost model

This gap is closed for the bridge actually stated.

Fresh independent uniform \(U\) makes \(Q+[U]P\) uniform in prime-order
\(H\). At most two subgroup points lie over each of at most \(m-1\)
exceptional coordinates, so, when a hit is possible,
\[
\mathbb E[T]\ge \frac{N}{2(m-1)}.
\]
The same `M_logN/1.0.0` ledger charges at least one unit for every trial and
\(\Omega(m)\) for the required expanded replay. Hence
\[
\mathbb E[W]\ge a\frac{N}{2(m-1)}+bm
 =\Omega(N/m+m)=\Omega(\sqrt N).
\]
The addition is legitimate because both terms use the same word/traffic
ledger. It gives no sub-rho exponent credit.

The \(\Omega(m)\) term is conditional on mandatory materialization or
retrieval of all \(m\) entries. Compressed multiplicity descriptions,
nonuniform advice, and different target bridges are outside the claim. The
proof does not purport to lower-bound those alternatives.

## 5. Replay obligation and scope

This gap is closed as an obligation, not as an executed specialized
certificate.

`newton-corner-theorem-mode/1.0.0` separates universal and specialized
inputs, binds future instances to a snapshot and both artifact digests,
requires the exact recurrence and unit replay, names the \(B=0\), identity,
torsion, and collision branches, constrains outputs, and fails closed on
normalization or version mismatch. Random masking is correctly moved to the
distinct `uniform-mask-exception-bridge/1.0.0` transcript rather than being
smuggled into a randomness-free theorem mode.

No specialized theorem instance or bridge transcript is claimed to exist in
this zero-compute packet. A later user must instantiate the required schema;
the schema name alone is not execution evidence.

## Baselines and omitted end-to-end path

Pollard rho has expected \(N^{1/2+o(1)}\) work with negligible serial memory.
The scoped bridge lower bound reaches the same exponent floor, with no
constant-factor comparison.

BSGS has \(N^{1/2+o(1)}\) work and \(N^{1/2+o(1)}\) stored group elements.
The packet establishes no advantage over it because it supplies neither a
bridge upper bound nor a common peak-memory comparison.

The closest specialized baseline is canonical original-section Semaev
point-decomposition/index calculus using the multigraded box driver. The
proved ratio is one for nonexceptional sections, so original Newton support
provides no BKK path-count reduction. Relation supply and independence,
factor-base representation, source recovery and sign orientation, matrix
rank, factor-log linear algebra, target descent, verification, traffic, and
peak memory are all absent. That absence is acceptable for this local
negative gate and blocks any broader algorithmic or ECDLP conclusion.

## Disposition

The five named BATCH-008 gaps are closed within the stated original-section
boundary. The narrow result is an all-\(m\) Newton-box classification plus a
uniform-mask escape-route lower bound under explicit replay assumptions.
There is no standardized-curve result, key recovery, knowledge promotion, or
cryptographically relevant breakthrough.
