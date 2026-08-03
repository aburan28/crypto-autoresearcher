# Direct five-source TT zero-locator preflight v2

## Handoff: exact equality tensor and compiler gap

### Claim or task

Determine whether a complete projective five-point addition circuit can be
compiled directly into an exact tensor-train locator for

```text
P_(i1)+P_(i2)+P_(i3)+P_(i4)+P_(i5)=Q,
```

with per-target work, traffic, and peak state strictly below `B^2`, bypassing
the D2 root polynomial, scalar source norm, and subset descent.

### Status

- This v2 preserves and supersedes `preflight-v1.md` once exact-byte theory,
  accounting, and red-team reviews return `GO`.
- `RESTRICTED THEOREM`, paper-only: the scalar `g_Q` below vanishes exactly on
  ordered five-term witnesses, its finite-field indicator is exact, and its
  pre-indicator CP/TT ranks are bounded independently of `B`.
- `RESTRICTED THEOREM`, paper-only: every final TT cut rank is the number of
  distinct matching partial sums at that cut. Low final rank therefore records
  a sparse intersection; it does not construct that intersection.
- `NEGATIVE RESULT`, `MODEL-BOUND`: generic exact entry-oracle TT
  reconstruction cannot infer an unknown sparse support from low output rank.
- Overall candidate: `HYPOTHESIS`, `NOVELTY-UNVERIFIED`, `REVIEW_REQUIRED`.
  Exact algebraic normalization may reach full middle rank before the final
  indicator, while direct skeletonization is circular without a separate
  coordinate-specific completeness theorem.

No implementation or experiment is authorized.

### Assumptions

- `E/F_p` is an authorized generated ordinary short-Weierstrass curve
  `Y^2*Z=X^3+a*X*Z^2+b*Z^3`, `char(F_p)` is neither two nor three, and the
  registered subgroup has odd prime order `q`.
- Point addition is Renes--Costello--Batina Algorithm 1 for arbitrary prime-
  order short-Weierstrass curves, with `b3=3*b`, used exactly as its 40-gate
  division-free homogeneous circuit. Its exceptional pairs differ by a point
  of order two; no such point lies in the registered odd-order subgroup.
- The fixed addition tree is left-associated:
  `S12=Add(P1,P2)`, `S123=Add(S12,P3)`, `S1234=Add(S123,P4)`, and
  `S=Add(S1234,P5)`. Every intermediate remains in the odd-order subgroup, so
  each call returns a valid nonzero projective representative even for the
  identity, inverse pairs, doubling, and repeated identifiers.
- `K=F_p(omega)` is a registered quadratic extension with basis `{1,omega}`.
  All ranks and tensor arithmetic below are over `K` unless stated otherwise.
- Each of five modes indexes the same registry of `B` signed public points.
  Repeated indices and distinct identifiers representing the same point remain
  distinct ordered witnesses.
- The asymptotic relation regime has `q=Theta(B^5)` and `p=Theta(q)`. This is
  the five-term factor-base scale, not a claim that every target has a witness.
- Tier A records any fixed-curve online result with all offline costs and an
  exact amortization count, even if it does not improve an ECDLP exponent.
- Tier B, the strict compiler hypothesis tested here, requires fixed advice,
  preprocessing workspace, preprocessing operations, and preprocessing
  traffic each to be `o(B^3)`, and per-target work, traffic, and peak state
  each to be `o(B^2)`.
- A single-instance or complete ECDLP improvement is a separate Tier C claim:
  preprocessing, actual relation attempts, filtering, linear algebra, and
  individual descent must share a total `o(B^2.5)` gate. Logarithmic factors
  and canonical record widths are charged in every tier.
- The output must be five registered identifiers whose signed affine points
  independently add to `Q`. A tensor zero test alone is not a decomposition.

### Evidence so far

#### Exact complete projective equality scalar

The bound circuit is Algorithm 1 of Renes, Costello, and Batina, *Complete
addition formulas for prime order elliptic curves* (EUROCRYPT 2016). It is a
complete bidegree-`(2,2)` homogeneous law on the registered odd-order subgroup
over `char(F_p) != 2,3`; there are no selectors or exceptional branches to
charge. Four calls in the fixed tree compute

```text
S=P_(i1)+P_(i2)+P_(i3)+P_(i4)+P_(i5)=(X:Y:Z).
```

For the target `Q=(X_Q:Y_Q:Z_Q)`, define two `F_p` residuals and one `K`
scalar:

```text
e_X = X*Z_Q-X_Q*Z,
e_Y = Y*Z_Q-Y_Q*Z,
g_Q = e_X+omega*e_Y.
```

Linear independence of `1` and `omega` gives

```text
g_Q=0  iff  e_X=e_Y=0.
```

If `Q=(x_Q:y_Q:1)` is finite, these equations are `X=x_Q*Z` and
`Y=y_Q*Z`; a valid projective point satisfying them is exactly `Q`. If
`Q=O`, then `g_O=-omega*Z`; on this cubic, `Z=0` implies `X=0`, so the only
valid projective point is `(0:1:0)`. Rescaling either projective
representative multiplies `g_Q` by a nonzero scalar and does not change its
zero set. Thus

```text
g_Q(i1,...,i5)=0  iff  sum_j P_(ij)=Q.
```

This binding is part of the theorem, not an implementation oracle. An altered
formula, weighted-projective convention, incomplete affine circuit, uncharged
exceptional branch, or output `(0:0:0)` invalidates the claim and requires a
new reviewed version.

#### Constant rank before the zero indicator

Every input coordinate in one mode is a length-`B` vector and therefore a
rank-one five-mode tensor after broadcasting across the other modes. The four
addition circuit has a fixed number of additions and multiplications. Fully
expanding any output coordinate yields a fixed finite number of monomials, and
each monomial factors across the five modes. Consequently there are constants
`C_X,C_Y,C_Z`, independent of `B`, such that

```text
CP-rank(X)<=C_X,
CP-rank(Y)<=C_Y,
CP-rank(Z)<=C_Z,
CP-rank(g_Q)<=R_0=C_X+C_Y+C_Z=O(1).
```

Every initial TT cut rank is at most `R_0`. This is an existence upper bound
from a fixed circuit, not a minimal-rank claim and not a bound after applying a
zero predicate.

#### Exact finite-field indicator

The componentwise tensor

```text
Zcal_Q = 1-g_Q^(|K|-1) = 1-g_Q^(p^2-1)
```

equals one exactly on ordered witnesses and zero elsewhere. Frobenius reduces
the explicit exponent route to

```text
gbar_Q = g_Q^p,
h_Q    = g_Q*gbar_Q = Norm_(K/F_p)(g_Q),
Zcal_Q = 1-h_Q^(p-1).
```

Conjugation preserves TT ranks, but the norm is a Hadamard product and the
remaining addition chain has `Theta(log p)=Theta(log B)` products.

For cut `k` of an order-five tensor, let `rho_k(T)` be its unfolding rank and

```text
D_k=B^min(k,5-k).
```

Exact TT arithmetic only gives

```text
rho_k(U+V)   <= min(D_k,rho_k(U)+rho_k(V)),
rho_k(U*V)   <= min(D_k,rho_k(U)*rho_k(V)).
```

The middle ambient caps are `D_2=D_3=B^2`. Hence the rank recurrence permits
the exponent chain to reach full middle rank long before its last step. The
final Boolean tensor may collapse sharply, but that does not retroactively
remove intermediate cores, normalization work, or memory traffic.

There is also a hard dense-core gate below ambient saturation. Any order-five
TT satisfies `rho_2<=B*rho_1`, so its second core allocation obeys

```text
B*rho_1*rho_2 >= rho_2^2.
```

The symmetric statement holds at cut three. Therefore an actual intermediate
central bond `Omega(B)` forces `Omega(B^2)` dense core words and fails the
strict state and traffic gates before normalization. This is a bound for the
standard dense TT representation, not for every structured circuit or sparse
core scheme.

At Hadamard stage `j`, let the actual operand bonds be `u_(j,k),v_(j,k)` and
put

```text
pi_(j,k)=u_(j,k)*v_(j,k).
```

The standard dense Kronecker-core construction has exact raw allocation

```text
S_j=B*(pi_(j,1)+pi_(j,1)*pi_(j,2)
       +pi_(j,2)*pi_(j,3)+pi_(j,3)*pi_(j,4)+pi_(j,4))
```

in `K`-words. If every operand bond is exactly `r`, this is
`B*(2*r^2+3*r^4)`. The latter is a construction-conditional saturated count,
not a lower bound for every product representation.

Vilmart's 2026 exact arbitrary-field reduction runs in `O(r*s)` field
operations for input maximum TT rank `r` and input size `s`. Applied to a raw
train of maximum bond `P`, this gives the coarse classical schedule
`N_j=O(B*P^3)`. Let `m=1+ell(p-1)=Theta(log B)` include the norm product and
one addition chain for `p-1`. The exact cumulative work gate is

```text
sum_(j=1)^m (S_j+N_j)+N_(1-minus)+W_locate=o(B^2),
```

with the analogous cumulative read/write traffic and peak liveness. If all
normalized operand bonds are bounded by `r`, then `P<=r^2` and

```text
r=o((B/m)^(1/6))
```

is a sufficient, route-specific work condition. It is not a necessary rank
condition. The saturated dense raw-state condition in field words is
`r=o(B^(1/4))`.

Canonical storage and traffic use

```text
b_K=2*ceil(log2(p)/8)
```

uncompressed bytes per `K` element, plus metadata. Every word count is also
reported after multiplication by `b_K`; for example the saturated raw-state
byte gate is `r=o((B/b_K)^(1/4))`. Frobenius conjugation is rank-preserving but
still charges one core read, coefficient conjugation, and core write. The
final direct sum `1-h_Q^(p-1)` has raw bonds `d_k=r_k+1` and requires its own
exact normalization.

#### Exact final TT cut ranks

For cut `k in {1,2,3,4}`, define the registered partial-sum supports

```text
L_k(s) = {(i1,...,ik): sum_(j<=k) P_(ij)=s},
R_k(s) = {(i_(k+1),...,i5): sum_(j>k) P_(ij)=Q-s}.
```

Let `M_(k,Q)` be the set of group elements `s` for which both sets are
nonempty, and put `m_(k,Q)=|M_(k,Q)|`. The cut-`k` unfolding is the disjoint
block sum

```text
Zcal_Q^<k> = sum_(s in M_(k,Q)) 1_(L_k(s))*1_(R_k(s))^T.
```

The row supports and column supports of different summands are disjoint, so
the nonzero rank-one blocks are linearly independent over every field. Thus

```text
rho_k(Zcal_Q)=m_(k,Q).
```

In particular, the middle ranks count distinct matching two-versus-three and
three-versus-two partial sums. If `w_Q` is the number of ordered witnesses,
then `m_(k,Q)<=w_Q`, so sparse relation fibers have compact final TT
representations. Conversely, constructing those blocks requires identifying
the matching partial sums or finding another exact algebraic route that does
not expose them.

The standard dense final-core allocation for these bond dimensions is

```text
S_TT = B*(rho_1+rho_1*rho_2+rho_2*rho_3
          +rho_3*rho_4+rho_4)
```

`K`-words. Its complete word gate is

```text
rho_1+rho_1*rho_2+rho_2*rho_3+rho_3*rho_4+rho_4=o(B).
```

All five nonnegative terms must pass. A uniform sufficient canonical-byte
gate is `max_k rho_k=o((B/b_K)^(1/2))`. Structured or sparse core storage is
outside this dense-allocation statement, and no final storage formula says
anything about the cost of constructing the cores.

#### Why generic TT skeletonization is not yet a compiler

Suppose an algorithm sees only an exact entry oracle for a tensor and is
promised rank at most one. After fewer than `B^5` deterministic queries that
all return zero, its transcript is consistent both with the zero tensor and
with a one-entry rank-one tensor supported at any unqueried index. Therefore a
generic exact black-box method cannot reconstruct arbitrary low-rank sparse
tensors, test zero, or return a leading nonzero index with sub-`B^5` worst-case
queries. A randomized method making `t` queries finds an adversarially uniform
single spike with probability at most `t/B^5`.

This is a `MODEL-BOUND` rejection of unstructured TT-cross or skeletonization
from equality queries. It is not a lower bound for the elliptic-coordinate
family: a useful compiler must exploit more than entry access, such as a
proved low-rank algebraic interpolation invariant, an additive expansion
theorem, or a target-update structure unavailable to the spike oracle.

#### Locator and certificate after cores exist

An exact arbitrary-field TT first sweep exposes whether `Zcal_Q` is zero. On a
nonzero swept train of order `d`, maximum mode `n`, and maximum rank `r`, the
2026 leading-index algorithm costs `O(d*n*r)` field operations. The sweep,
suffix/pivot data, core reads and writes, and final replay remain separately
charged; leading-index recovery is not free merely because `d=5`.

The returned mode indices are already five signed public identifiers. The
positive certificate is those IDs plus independent complete or affine point
addition to `Q`. A negative certificate requires canonical exact zero cores or
another independently checkable proof; a failed heuristic cross search is not
such a certificate.

#### Fixed-curve and ECDLP boundary

This object is a target-decomposition primitive, not an ECDLP break. For target
support `D5`, report `epsilon=|D5|/q`. Convert every returned ordered tuple to a
canonical signed relation row; permutations and duplicate labels do not create
new relations. Report `eta_r`, the fraction of accepted rows that increment
the relation-matrix rank.

Preregister uniform no-hit, one-canonical-witness, many-witness, `Q=O`,
repeated-index, and duplicate-label target classes. A route continues only if
its work gate, correct support probability, canonical relation yield, and
rank-increment yield pass conjunctively. Cheap no-hit targets or many
permutations of one relation are not positive evidence.

Every offline report separates advice bytes, preprocessing field operations,
preprocessing reads/writes, peak preprocessing workspace, number of supported
online targets, and amortization crossover. `Q`-dependent cores, powers,
pivots, transcripts, suffix data, and certificates are online. Tier A may be a
useful reused-curve compiler even with large preprocessing, but Tier C may be
compared with rho only after the entire relation and descent pipeline fits the
common `o(B^2.5)` gate.

The task-matched fixed-advice comparator uses the measured distinct supports
`N2=|D2|` and `N3=|D3|`, not automatically `B^2` and `B^3`:

```text
S_D2D3=N2*b_D2+N3*b_D3,
T_D2D3(Q)<=N2 EC subtractions and D3 probes,
```

plus witness replay. Collision-light asymptotics must be measured or proved.
D2+D3 is a complete comparator, not a lower bound.

### Experiment contract

#### Hypothesis

There exists a coordinate-specific exact compiler for `Zcal_Q` whose complete
Tier B target path, including construction, normalization, location, and
certificate, uses `o(B^2)` field operations, canonical-byte traffic, and peak
live bytes while fixed advice, preprocessing operations/traffic, and peak
workspace remain `o(B^3)` in their declared units.

#### Null hypothesis

Every specified compiler either materializes a two-sum boundary object,
reaches `Omega(B^2)` target work, traffic, or state, hides a larger fixed table,
or loses exactness before returning five registered identifiers.

#### Parameters

- field/curve family: generated ordinary prime-order short-Weierstrass curves;
- sizes: paper gate first, then only reviewed toy sizes `8,10,12` bits;
- seeds: preregistered before any authorized run;
- factor base: one registry of `B` signed public points;
- relation shape: ordered five-term sum to a target `Q`;
- baseline: explicit complete addition, exact full tensor at tiny size,
  fixed-advice two-versus-three lookup, and normalized Pollard rho accounting.

#### Metrics

- offline and online field additions, multiplications, inversions, and
  Frobenius maps separately;
- preprocessing reads/writes, peak preprocessing workspace, amortized target
  count, bytes read and written, peak online bytes, and fixed advice bytes;
- all four TT cut ranks before and after every gate and exact normalization;
- raw Hadamard ranks and normalizer transcripts;
- entry queries, prefix-child tests, distinct support `epsilon`, and target-
  class-conditioned success probability;
- canonical witness replay, relation-row deduplication, rank-increment yield
  `eta_r`, and downstream matrix costs.

#### Positive control

At tiny `B`, materialize `Zcal_Q`, compute every unfolding rank by exact linear
algebra, construct canonical cores, recover the leading witness, and replay
its five points.

#### Negative control

Run the same generic entry-oracle skeletonizer on zero tensors and uniformly
hidden one-entry rank-one tensors. It must not claim exact zero or complete
reconstruction without a valid coverage certificate.

#### Success criterion

Independent theory, accounting, literature, and red-team review must first
approve every paper gate. Only then may a toy implementation proceed. Empirical
promotion requires three sizes, preregistered seeds and target classes, exact
replay, canonical relation yield, and fitted Tier B target exponent below two
in the `B` scale with advice, preprocessing, and traffic included. Tier C also
requires the complete fitted pipeline exponent below `2.5`.

#### Falsification criterion

Stop the implementation path if any specified route reaches `Omega(B^2)`
target work, traffic, or peak state; reaches the Tier B `Omega(B^3)` boundary
in advice, preprocessing operations/traffic, or workspace; has an intermediate
central dense-TT rank `Omega(B)`; requires an unproved exact skeleton coverage
assumption; or cannot recover, canonicalize, and independently replay five
registered identifiers. Failure of Tier C does not erase a correctly labeled
Tier A or Tier B fixed-curve result.

#### Reproduction command

```bash
# NOT AUTHORIZED: paper contract remains REVIEW_REQUIRED.
```

### Failure modes

- Calling complete projective addition a complete compressed locator.
- Treating constant CP/TT rank of `g_Q` as a rank bound for its zero indicator.
- Reporting only the low final rank while omitting high-rank exponent states.
- Materializing Kronecker-product cores and charging only their recompressed
  descendants.
- Calling approximate SVD rounding or heuristic TT-cross exact.
- Assuming a low-rank sparse tensor can be reconstructed from entry access
  without locating its support.
- Hiding a `B^2` pair table, `B^3` triple table, target table, selector tensor,
  or normalizer transcript in preprocessing.
- Returning a zero test, projective coordinate, or unregistered index instead
  of five signed public identifiers.
- Comparing a fixed-curve online result with single-instance rho while omitting
  offline work, advice, number of targets, and success probability.
- Counting ordered permutations or duplicate point labels as independent
  relation yield.

### Next concrete action

Obtain exact-byte theory, accounting, literature, and red-team reviews of v2.
Then derive or refute a gate-by-gate central-rank certificate for the bound RCB
plus norm-indicator circuit; stop before source code if any dense intermediate
central rank reaches `Omega(B)` or any cumulative Tier B gate fails.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/research-question.json`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v1.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v2.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v2.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/theory-review-v1.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/accounting-review-v1.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/red-team-v1.md`
