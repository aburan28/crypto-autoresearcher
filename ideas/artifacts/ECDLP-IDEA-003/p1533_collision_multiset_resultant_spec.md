# P1533 collision-recovering multiset resultant specification

## Record status

- Candidate root: `ECDLP-IDEA-003`
- Focus experiment: `P1533`
- Expansion of: `P1532`
- Artifact class: theorem-only producer specification and corrected interface
- Decision: `SCOPED_NO_PASS__OPEN_COLLISION_RESULTANT`
- Evidence scale: symbolic interface, probability, and cost gates; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- Solver or elliptic fixture: none

P1533 weakens P1532's output requirement without weakening Gallant recovery. It asks
for an exact multiset-intersection certificate with deterministic source-index recovery,
not for all row labels. A direct resultant may exploit symmetry that an ordered batch
cannot. No passing resultant is supplied.

## Bound predecessor

- `ideas/artifacts/ECDLP-IDEA-003/p1532_r1_independent_audit.md`
  - Decision:
    `INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__REVISE_TO_COLLISION_RESULTANT`

The predecessor verifies the batch rectangle and rho controls, proves a full-order
constant-recurrence floor, and corrects the claim that ordered row materialization is
necessary.

## Exact label and batch

Retain

```text
ell-1=A*D,                 gcd(A,D)=1,
A=ell^(1-alpha+o(1)),      D=ell^(alpha+o(1)),
H=<b>, |H|=D, -1 in H,    K=ceil(sqrt(A)),
BASE[i]=L([a^(i*K)]P),    TARGET[j]=L([a^(-j)]Q).
```

Each `L` is the three-coordinate tagged P1531 Cauchy label. Equality identifies one
`H` orbit except with the already charged public-setup failure probability. The inner
orbit search and final `[x]P=Q` verification remain mandatory.

## Randomized field compression

On a pole-free setup choose public uniform `eta in F_p^3` and set

```text
z_eta(R)=eta dot L(R).
```

For unequal labels, `Pr_eta[z_eta(R)=z_eta(S)]<=1/p`. There are at most `K^2` cross
pairs, so

```text
Pr[false compressed cross collision] <= K^2/p
                                      = ell^(-alpha+o(1)).
```

Every recovered scalar is finally verified. A deterministic projective encoding of
the three numerator/denominator pairs is also admissible. Otherwise the operation must
return an aggregate bad-setup bit for any pole in the queried subsets and charge every
resample or repeated hash. Mapping `POLE` to an unchecked field sentinel is invalid.

## Admitted certificate interfaces

For a side `R`, public row multipliers `r_i`, and deterministic index set `I`, define

```text
C_(R,I)(Z)=product_(i in I) (Z-z_eta([r_i]R)).
```

One of the following is sufficient.

### Characteristic-polynomial family

Return the complete base and target characteristic polynomials and either:

1. a subdivision tree binding each factor to deterministic source intervals; or
2. an evaluator for `C_(R,I)(z)` on the deterministic subdivisions used during
   recovery.

The gcd supplies a common compressed label. Evaluating subdivision certificates at
that root recovers one base and one target index.

### Direct intersection resultant

Return a certified predicate or nonzero witness for

```text
Res_Z(C_(P,I), C_(Q,J))=0
```

for the full batches and for deterministic subdivisions. Recursive bisection must
recover source indices. A scalar collision bit for the full batches without the
subdivision interface is insufficient.

### Equivalent relative norm

A relative norm, determinant, or cyclic-algebra trace is admissible only if its zero
set is biconditional to compressed-label intersection on the rational prime subgroup
and it supports the same source recovery. A union orbit product or sum of row traces is
not such a certificate.

## Cost gate

Let

```text
c_C = exponent for complete target-independent base setup and certificates,
b_C = exponent for challenge-dependent intersection and source recovery,
m_C = peak retained state exponent.
```

The end-to-end path has

```text
lambda_C=max(c_C,b_C,(1-alpha)/2,alpha/2,final verification),
mu_C=max(m_C,required collision state).
```

Strict sub-rho time requires `c_C,b_C<1/2`. At `alpha=1/2`, promotion additionally
requires

```text
c_C<=0.45,                b_C<=0.45,                mu_C<=0.30.
```

If a size-`n` subset call costs `sqrt(nD)^(1+o(1))`, deterministic bisection has a
geometric total `O(sqrt(KD))`; it does not add an exponent. Recomputing a full-size
certificate at every level also adds only a logarithm, but making `K` singleton calls
returns to rho. Every coefficient, gcd, resultant, field extension, replay, and bad
setup must be charged.

## Quantitative target

The top-level batches contain `KD` orbit terms. A direct intersection operation with
cost

```text
(KD)^(1/2+o(1))=ell^((1+alpha)/4+o(1))
```

would have exponent `3/8` at `alpha=1/2`. This is only a target. Producing a
degree-`K` characteristic polynomial is compatible with the output floor because
`K=ell^((1-alpha)/2+o(1))`, but coefficient-ring operations and construction time are
not free.

## Balanced CRT normalization

For the restricted family

```text
A=A_1*A_2,                gcd(A_1,A_2)=1,
A_1,A_2=ell^((1-alpha)/2+o(1)),
```

replace interval BSGS by the exact CRT decomposition

```text
J_1=<a^(A_2)>,            J_2=<a^(A_1)>.
```

Every quotient exponent has a unique representation from `J_1*J_2`, so the base and
target rows can both be complete multiplicative-subgroup batches. This normalization
is admitted because relative norms and resultants may need complete subgroup actions.
It restricts the curve/order family and must include generation probability and cost.
Simple nested labels over `H*J_i` followed by `sqrt(K)` independent quotient queries
cost `sqrt(D*K^2)=sqrt(ell)` and are the rho control.

## Required explicit attempt

The independent audit must write one of these objects through to base-field
operations:

1. a bivariate elliptic resultant whose elimination variable ranges over `H` and whose
   second action ranges over a complete balanced subgroup `J_i`;
2. a relative norm in the rational prime-subgroup coordinate algebra with an explicit
   representation smaller than its `KD` value table; or
3. a direct cross-resultant recursion that decides and localizes equality without
   constructing both degree-`K` polynomials.

For the chosen attempt, bound every intermediate degree, coefficient-ring dimension,
resultant or gcd cost, field extension, denominator, pole branch, and source inverse.

## Frozen controls

Reject the first applicable route:

1. It computes only a union product, aggregate trace, checksum, or full-batch bit with
   no deterministic source recovery.
2. It constructs all `K` labels, performs `K` square-root orbit calls, or materializes
   `K*D` point terms before the resultant.
3. It hides degree-`K` polynomial arithmetic or `K` product-ring operations as one
   base-field operation.
4. It uses a low-order constant recurrence; the P1532 disjoint-pole proof gives order
   at least `A` for the full symbolic quotient sequence.
5. It parameterizes `a^j in F_ell` as though it were a base-field variable in `F_p`
   without a valid transfer map.
6. It normalizes a nonzero Fourier mode and assumes the missing hidden-scalar character
   orientation.
7. It uses a homomorphism or isogeny nonzero on `G` to collapse a multiplicative scalar
   orbit.
8. It omits balanced-factor availability, bad setup, false compressed collisions,
   inner `H` recovery, final verification, time, or memory.

## Primary-source boundary

- Gallant type-2 collision recovery: <https://eprint.iacr.org/2010/370.pdf>
- Square-root elliptic products and resultants: <https://arxiv.org/pdf/2003.10118>
- q-holonomic square-root product algorithms: <https://arxiv.org/abs/2012.08656>
- Universal elliptic Gauss sums: <https://arxiv.org/pdf/1707.08610>
- Parallel square-root Velu is a latency/constant control, not an exponent reduction:
  <https://eprint.iacr.org/2024/851.pdf>

The collision-certificate interface and balanced-CRT application are
`novelty-unverified`. No audited source supplies the required direct ECDLP resultant.

## Decision

No admitted construction currently decides and localizes the two structured label-set
intersection with `c_C,b_C<1/2`. The corrected open disposition is

```text
SCOPED_NO_PASS__OPEN_COLLISION_RESULTANT
```

Exactly one next action: independently audit this specification and derive one explicit
balanced-subgroup relative resultant or direct cross-resultant recurrence with complete
source recovery and `c_C,b_C<1/2`, or sign a scoped no-candidate disposition. Do not
authorize a contract, solver, or toy fixture.

This specification is not an ECDLP algorithm, a generic-order result, a Shoup-bound
improvement, or a breakthrough.
