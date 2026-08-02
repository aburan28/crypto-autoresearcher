# Direct five-source TT zero-locator preflight v1

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
- The registered complete projective addition formula is valid for every pair
  of registered subgroup points, including the identity `O=(0:1:0)`, and
  returns a nonzero projective representative.
- `K=F_p(omega)` is a registered quadratic extension with basis `{1,omega}`.
  All ranks and tensor arithmetic below are over `K` unless stated otherwise.
- Each of five modes indexes the same registry of `B` signed public points.
  Repeated indices and distinct identifiers representing the same point remain
  distinct ordered witnesses.
- The asymptotic relation regime has `q=Theta(B^5)` and `p=Theta(q)`. This is
  the five-term factor-base scale, not a claim that every target has a witness.
- Fixed-curve advice and preprocessing workspace must be `o(B^3)`. Per-target
  field operations, memory traffic, and peak live state must each be
  `o(B^2)`. Logarithmic factors are charged.
- The output must be five registered identifiers whose signed affine points
  independently add to `Q`. A tensor zero test alone is not a decomposition.

### Evidence so far

#### Exact complete projective equality scalar

Four registered complete additions compute

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

This relies on the registered complete formula. An incomplete affine circuit,
an uncharged exceptional branch, or an output `(0:0:0)` invalidates the claim.

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

If two normalized operands have uniform rank at most `r`, their unreduced
Hadamard cores have ranks at most `r^2` and occupy `O(B*r^4)` words. Even this
raw state is strict `o(B^2)` only when `r=o(B^(1/4))`. A cubic exact reduction
in the raw rank would cost `O(B*r^6)` and require `r=o(B^(1/6))`, before the
logarithmic chain factor. These are coarse necessary gates, not an asserted
complexity theorem for the 2026 normal-form algorithm; its exact field-
operation and traffic schedule must be derived and reviewed separately.

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

The exact final core storage is

```text
S_TT = B*(rho_1+rho_1*rho_2+rho_2*rho_3
          +rho_3*rho_4+rho_4)
```

`K`-words. A convenient sufficient gate is `max_k rho_k=o(B^(1/2))`; the
actual middle requirement is `rho_2*rho_3=o(B)`. This storage theorem says
nothing about the cost of constructing the cores.

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

An exact arbitrary-field TT normal form can expose whether `Zcal_Q` is zero
and can return a leading nonzero index. Equivalently, suffix spaces can be
built backwards and at most `5B` prefix children tested for a nonzero
completion. These tests, suffix bases, and their field operations are charged;
a straightforward schedule is polynomial in the adjacent TT ranks and is not
free merely because the number of modes is five.

The returned mode indices are already five signed public identifiers. The
positive certificate is those IDs plus independent complete or affine point
addition to `Q`. A negative certificate requires canonical exact zero cores or
another independently checkable proof; a failed heuristic cross search is not
such a certificate.

#### Fixed-curve and ECDLP boundary

This object is a target-decomposition primitive, not an ECDLP break. A complete
pipeline must separately report fixed advice construction, number and
distribution of supported targets, relation independence, matrix filtering
and rank, sparse linear algebra, and individual logarithm descent. An online
win that consumes `Theta(B^3)` fixed advice can be meaningful for a reused
curve, but it must be compared with the generic fixed-preprocessing frontier
and cannot be reported as a single-instance exponent break.

### Experiment contract

#### Hypothesis

There exists a coordinate-specific exact compiler for `Zcal_Q` whose complete
target path, including construction, normalization, location, and certificate,
uses `o(B^2)` field operations, memory traffic, and peak live words while
fixed advice and workspace remain `o(B^3)`.

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
- bytes read and written, peak live bytes, and fixed advice bytes;
- all four TT cut ranks before and after every gate and exact normalization;
- raw Hadamard ranks and normalizer transcripts;
- entry queries, prefix-child tests, supported-target count, and success
  probability;
- witness replay, relation independence, and downstream matrix costs.

#### Positive control

At tiny `B`, materialize `Zcal_Q`, compute every unfolding rank by exact linear
algebra, construct canonical cores, recover the leading witness, and replay
its five points.

#### Negative control

Run the same generic entry-oracle skeletonizer on zero tensors and uniformly
hidden one-entry rank-one tensors. It must not claim exact zero or complete
reconstruction without a valid coverage certificate.

#### Success criterion

Independent theory, accounting, and red-team review must first prove every
paper gate. Only then may a toy implementation proceed; empirical promotion
requires three sizes, preregistered seeds, exact replay, and fitted total target
exponent below two in the `B` scale with advice and traffic included.

#### Falsification criterion

Stop the implementation path if any specified route reaches `Omega(B^2)`
target work, traffic, or peak state; uses `Omega(B^3)` fixed advice/workspace;
requires an unproved exact skeleton coverage assumption; or cannot recover and
independently replay five registered identifiers.

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

### Next concrete action

Obtain independent theory, accounting, literature, and red-team reviews of
the exact cut-rank theorem and the algebraic construction gap; derive the
arbitrary-field normalizer's full operation and traffic schedule before any
source-code authorization.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/research-question.json`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v1.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger.md`
