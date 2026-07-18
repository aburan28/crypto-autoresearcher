# P1531 R1 independent audit and batched type-2 rerank

## Record status

- Candidate root: `ECDLP-IDEA-003`
- Focus experiment: `P1531`
- Audit class: independent theorem-only reconstruction and prior-art screen
- Producer artifact:
  `ideas/artifacts/ECDLP-IDEA-003/p1531_cauchy_elliptic_period_type2_spec.md`
- Producer SHA-256:
  `b59775a7fa5329df780c3a4aa8d453c585ae5782139a3f01d46ba571fc9d682a`
- Decision:
  `INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__RERANK_BATCHED_TYPE2`
- Evidence scale: exact algebra and asymptotic route audit; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- Solver or elliptic fixture: none

The independent audit reconstructs the three-trace separator and the type-2 cost
rectangle. It also adds three controls that were absent from the producer: a favorable
square-root Velu evaluator still lands exactly on rho, elliptic Fourier modes reduce to
type-1 character distinguishers whose classical orientation-free powers erase the hidden
scalar, and an isogeny nonzero on the prime subgroup cannot collapse a multiplicative
scalar orbit. The only reranked primitive is joint, row-preserving evaluation of the
structured batch of labels already required by Gallant's type-2 algorithm.

## Independent reconstruction boundary

The audit used only the public curve and subgroup interface, the producer artifact, and
the cited primary sources. It did not use a known logarithm, a target-specific selector,
a supplied orbit table, or producer code. The result verifies the scoped disposition of
P1531, not the broader nonexistence of a representation-specific orbit evaluator.

Let

```text
E/F_p ordinary,                  G=<P>, |G|=ell prime,
ell-1=A*D,                       gcd(A,D)=1,
D=ell^(alpha+o(1)),              H <= F_ell^*, |H|=D,
D even,                          n=D/2.
```

For `u in F_ell^*`, define

```text
X_u={x([u*h]P):h in H/{+1,-1}},
F_u(Z)=product_(z in X_u)(Z-z),
L_c([u]P)=POLE if F_u(c)=0, else F_u'(c)/F_u(c).
```

## Separator theorem: pass

Because `-1 in H`, equality of abscissas from `X_u` and `X_v` implies `u/v in H`.
Thus distinct scalar cosets have disjoint squarefree root sets, and every `F_u` is monic
of degree `n`.

For distinct cosets define

```text
N_(u,v)=F_u'F_v-F_v'F_u.
```

The leading degree cancels, so `deg N_(u,v)<=2n-2=D-2`. If `N_(u,v)=0`, then
`(F_u/F_v)'=0`. Since `F_p` is perfect, `F_u/F_v` would lie in `F_p(Z^p)` and every
zero and pole multiplicity would be divisible by `p`. Its zeros and poles are instead
disjoint and simple, a contradiction. Tagged poles cannot collide because the two root
sets are disjoint.

For one public uniform `c`, a fixed pair collides with probability at most `(D-2)/p`.
For `t` independent constants and fewer than `A^2/2` pairs,

```text
Pr[any collision] <= A^2/2 * ((D-2)/p)^t.
```

With `p=ell^(1+o(1))` and `t=3`, this is
`ell^(-(1-alpha)+o(1))`. This part of the producer is correct. It proves only a public
randomized separator; it does not evaluate it.

## Type-2 cost rectangle: pass

Gallant's type-2 algorithm evaluates `K=ceil(sqrt(A))` labels on each of two structured
sets and then performs an inner `sqrt(D)` orbit search. If target-independent setup,
one label query, and label state have exponents `c`, `q`, and `m`, then

```text
lambda_2=max(c,(1-alpha)/2,alpha/2,(1-alpha)/2+q,final),
mu_2=max(m,(1-alpha)/2,alpha/2).
```

Therefore an independently charged evaluator needs `q<alpha/2` and `c<1/2` for
strict sub-rho time. At `alpha=1/2`, the focus promotion caps require
`c<=0.45`, `q<=0.20`, and `m<=0.30`. Constantly many traces and pole tags do not
change these exponents.

Final scalar verification makes a bad public setup detectable after a candidate is
recovered. Since the proved setup-failure probability is negligible, resampling has
expected constant repetitions. It does not make a collision-free label deterministic.

## New control 1: square-root Velu reaches rho exactly

Bernstein, De Feo, Leroux, and Smith evaluate products

```text
h_S(c)=product_(s in S)(c-x([s]R))
```

in quasi-square-root time when the scalar set `S` has an additive index system
`I +/- J` with only a square-root-size remainder. Grant the most favorable case: an
integer lift of `H/{+1,-1}` admits such an index system for every queried orbit.

The algebraic evaluator can be differentiated with constant overhead, equivalently by
running it over `F_p[epsilon]/(epsilon^2)` at `c+epsilon`, whenever its public
denominators are units. It then returns `F_u(c)` and `F_u'(c)`, and hence the Cauchy
trace away from tagged poles, in

```text
q_velu=alpha/2+o(1).
```

Inserted into the independent-query type-2 cost, this gives

```text
(1-alpha)/2+q_velu=1/2+o(1).
```

It reaches the rho boundary and does not beat it. The two-set resultant model cannot
improve its exponent by rebalancing: if `S=(I+/-J) union K0`, then
`|S|<=2|I||J|+|K0|`, so at least one of `|I|,|J|,|K0|` is
`Omega(sqrt(|S|))`. This is a lower bound for this single-level index-system
implementation only, not for arbitrary arithmetic circuits.

The audit does not assume that a multiplicative subgroup actually has the required
additive index system. Granting it makes the control stronger.

## New control 2: elliptic Fourier modes are type-1 distinguishers

Let `f_c(R)=1/(c-x(R))`, with poles tagged separately, and let `H_perp` be the `A`
multiplicative characters of `F_ell^*` that are trivial on `H`. Define the elliptic
Fourier mode

```text
G_(chi,c)(R)=sum_(a in F_ell^*) chi(a) f_c([a]R).
```

Character orthogonality gives the exact normal form

```text
sum_(h in H) f_c([u*h]P)
  = D/(ell-1) * sum_(chi in H_perp) chi(u)^(-1) G_(chi,c)(P).
```

The full `H` sum is twice the x-only Cauchy trace. A change of variables also gives

```text
G_(chi,c)([u]P)=chi(u)^(-1) G_(chi,c)(P).
```

Thus any nonzero mode that can be evaluated and normalized substantially below rho
reveals a multiplicative character of the hidden scalar. It is a Gallant type-1 orbit
distinguisher, not a new bypass of P1530.

Classical universal elliptic Gauss-sum formulas do not provide the missing orientation.
They compute an order-`r` power of a resolvent; raising
`chi(u)^(-1)G(P)` to `r=ord(chi)` erases `chi(u)`. Recovering a root relative to the
chosen generator restores exactly the hidden character. Their published arithmetic
cost also retains a factor linear in the auxiliary torsion prime, so substituting the
cryptographic subgroup order is not sub-rho setup.

This closes direct Fourier expansion, all-mode materialization, and orientation-free
universal Gauss powers. It does not rule out a new compressed aggregate that never
materializes or normalizes an individual mode.

## New control 3: isogenies cannot collapse scalar orbits

Let `phi:E->E'` be an isogeny whose restriction to `G` is nonzero. Since `G` has prime
order, that restriction is injective. For `R` of order `ell` and any `h != 1 mod ell`,

```text
phi([h]R)=phi(R)
  implies [h-1]phi(R)=O
  implies phi(R)=O,
```

a contradiction. Therefore no isogeny chain nonzero on `G` sends the multiplicative
scalar orbit `{[h]R:h in H}` to one point or one additive kernel coset. If an isogeny
kills `G`, its degree is divisible by `ell` and its construction or representation is
already rho-exceeding for the present gate.

Square-root Velu accelerates sums over an additive kernel generated by a point. The set
of scalar coefficients `H` is multiplicative and `{[h]R:h in H}` is not an additive
subgroup of the prime-order curve group. Renaming it as an isogeny kernel is invalid.

This proves the missing homomorphic ECFFT/isogeny noncollapse gate. A nonlinear,
nonhomomorphic row-preserving encoder remains outside it.

## Cyclic-algebra and summation-polynomial controls

The coordinate algebra of the nonzero rational prime subgroup modulo sign is a split
algebra of dimension `(ell-1)/2`. The fixed algebra under `H/{+1,-1}` has dimension
`A`, and its relative trace is the formal Cauchy orbit sum. Materializing the split
algebra, its generic element, or the full relative-trace map costs `ell^(1+o(1))` base
field words. Merely naming the `A`-dimensional fixed algebra does not evaluate the trace
at a concrete hidden-scalar point.

Semaev polynomials can certify addition chains for individual multiples. They do not
alter the Fourier normal form, produce an additive isogeny kernel, or aggregate the
`D` Cauchy summands. The producer's direct, subgroup-tree, FFE-degree, global-invariant,
and backend-only ECFFT controls therefore pass in their stated scopes.

## Surviving primitive: batch the labels Gallant already requests

The independent-query model is stronger than Gallant's actual interface. His outer
collision stage requests two structured batches of `K=ceil(sqrt(A))` labels:

```text
B_i = L([a^(i*K)]P),             0<=i<K,
T_j = L([a^(-j)]Q),              0<=j<K,
```

where `a` has order `A` modulo `ell`. Let `c_B` be the exponent for the complete public
base batch, `b_B` the exponent for the complete target batch, and `m_B` their state.
Then a row-preserving batch evaluator changes the cost model to

```text
lambda_batch=max(c_B,b_B,(1-alpha)/2,alpha/2,final),
mu_batch=max(m_B,(1-alpha)/2,alpha/2),
```

instead of charging `K` independent evaluations. This is a semantically distinct
operation: it must return every row label, not just their product or one collision bit.

The direct batch touches `K*D` orbit terms and has exponent `(1+alpha)/2`. Applying a
square-root Velu evaluator independently to each row has exponent exactly

```text
(1-alpha)/2+alpha/2=1/2.
```

A hypothetical row-preserving evaluator quasi-linear in `sqrt(K*D)` would instead have

```text
b_B=(1+alpha)/4+o(1),
```

which is `3/8+o(1)` at `alpha=1/2` and would cross the time gate. No such identity is
known or supplied. A product over the union of all rows loses the row labels; evaluating
over a product ring charges one field operation per row; and Fourier row tags restore
the individual character modes above.

This exact batch interface, rather than another independent trace evaluator, is the sole
successor.

## Primary-source checks

- Gallant, *Finding discrete logarithms with a set orbit distinguisher*:
  <https://eprint.iacr.org/2010/370.pdf>
- Bernstein, De Feo, Leroux, and Smith,
  *Faster computation of isogenies of large prime degree*:
  <https://arxiv.org/pdf/2003.10118>
- Berghoff, *Efficient computation of universal elliptic Gauss sums*:
  <https://arxiv.org/pdf/1707.08610>
- Bostan and Yurkevich,
  *Fast Computation of the N-th Term of a q-Holonomic Sequence and Applications*:
  <https://arxiv.org/abs/2012.08656>

The square-root Velu and q-holonomic references reach quasi-square-root arithmetic
complexity. Neither publishes a row-preserving batch orbit label below that boundary.

## Decision

The independent audit passes the P1531 separator and cost rectangle and verifies the
producer's scoped no-pass disposition. It adds exact square-root-resultant, Fourier
orientation, and homomorphic isogeny controls. P1531 becomes terminal `inconclusive`,
independently verified only at this scoped audit level.

Decision:

```text
INDEPENDENT_SCOPED_AUDIT_PASS__INCONCLUSIVE__RERANK_BATCHED_TYPE2
```

Exactly one next action: freeze P1532 as a theorem-only row-preserving batch-label
specification, requiring either one explicit target-independent recurrence or transposed
resultant with `c_B,b_B<1/2` and complete memory, applicability, and recovery costs, or
a scoped no-candidate disposition. Do not authorize a contract, solver, or toy fixture.

This audit does not provide an ECDLP algorithm, a generic-order result, a Shoup-bound
improvement, or a breakthrough.
