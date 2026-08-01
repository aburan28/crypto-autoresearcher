# P1534 R1 independent induced-template WNU router audit

## Record status

- Candidate root: `ECDLP-IDEA-158`
- Focus experiment: `P1534`
- Producer hypothesis:
  `ideas/ECDLP-IDEA-158_x_only_nonfaithful_wnu_signed_lift_hypothesis.md`
- Artifact class: independent theorem-only reconstruction and scoped deferral audit
- Decision:
  `INDEPENDENT_SCOPED_AUDIT_PASS__DEFERRED_INDUCED_TEMPLATE_ROUTER_NOT_SUPPLIED`
- Evidence scale: symbolic relation, quotient-algebra, source, and cost audit; no experiment
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Contract authorization: none
- CSP solver, finite-field fixture, or relation campaign: none

The four producer gates reconstruct in their stated scopes. Full fixed-arity
rational-point Kummer summation relations primitive-positive interpret faithful
addition, and fixed deletion of signed branches is not a lift-invariant x-only
relation. Restricting to the induced sparse factor-base template is a logically valid
scope exception, but it does not supply the relation that a bounded-width algorithm
consumes.

This audit writes one exact finite-field-elimination realization through to its
coordinate algebra and one favorable `2+3` split. The first has dimension `B^5`; the
second retains `B^2` pair states and a target-dependent `B^3` triple side. A WNU does
not construct either support. No explicit target-independent support/witness router
meets the `B^2.25` setup and `B^1.25` query rectangle.

This is a scoped no-candidate receipt, not a data-structure lower bound and not a
proof that every induced sparse relation lacks a WNU.

## Bound inputs

| Input | SHA-256 |
|---|---|
| `ECDLP-IDEA-158_x_only_nonfaithful_wnu_signed_lift_hypothesis.md` | `0e84f9b24f956e5d340205a5a6c60d0285d3053d5612becf5bf432c83209be43` |
| `nonfaithful_signature_theorem.md` | `e904d2d29504f67cb45728fb621c221287baf7ca7527d810fa4cd3b691d82a7b` |
| `high_arity_pinning_theorem.md` | `9da224432a97db91e002cd220503df8857235792faecfdbc2eb58f2660b604be` |
| `affine_s4_chain_theorem.md` | `84fefb4193dfa0e47acad8751a2a79e3b6b0c3818d7926e14db9fad0c24ffb4e` |
| `restricted_language_access_gate.md` | `d54344c1c063dd7a7df1fadcc7826a8cb6bb5627414458b9877b47569803f302` |
| P1515 R1-R11 independent audit | `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e` |
| P1514 scope correction | `d718a341153f1ea805c59fe1f45511712fda1805fbcc61103bbe9f1f4159866f` |
| IDEA-158 review-required contract | `9a2c0c073aa746ba112b469ccfdd1a6a8476fe71561ffb473de7d3a893551632` |

The contract remains `review_required`, `approved_by: null`, and `maximum_runs: 0`.

## Independent reconstruction of the four gates

### Full ternary Kummer gate

The six pairwise distance atoms on

```text
Enc(t)=([t],[t+g],[t+2g],[t+3g])
```

exclude the inconsistent sign branches for prime `N>=5`, so `Enc` is a
primitive-positive defined oriented copy of `G`. The seven cross atoms force
`gamma=alpha+beta`: the horizontal and vertical triples leave only the true sum or
`alpha=beta,gamma=0`, and the two mixed atoms remove the distinct `alpha=-2` branch.

An idempotent WNU preserving this structure transports to a homomorphism

```text
W(x_1,...,x_k)=sum_i a_i*x_i
```

on the prime cyclic group. WNU and idempotence make the coefficients equal and sum
to one. Iterated Cauchy-Davenport then forbids preservation of a proper nontrivial
oriented factor-base lift. This gate reconstructs.

### Full high-arity affine gate

For fixed `m>=5`, the producer pins the `m-3` padding positions at `16(m-3)+1`
distinct nonzero public sign orbits. If the ternary source sum is false, each pinned
atom forces `l+c*z=0` for one of at most eight source sums and at most `2(m-3)`
padding coefficients, so it can pass at no more than `16(m-3)` sign orbits. The
conjunction therefore defines affine `R_3`.

Removing the four scalar values whose adjacent windows meet zero gives

```text
U=G minus {0,-g,-2g,-3g}.
```

The partial additive WNU on `U` extends uniquely to `G`: every scalar has a two-term
decomposition in `U`, and comparison bridges exist after avoiding at most sixteen
coordinate values. The modular-averaging and factor-base contradiction follows. The
producer's stronger assumption `N>32m+3` supplies all required nonzero pins. This
gate reconstructs.

### Strict affine four-ary gate

Two full affine `R_4` atoms sharing one nonzero Kummer state eliminate to a signed
relation on `(a,b,c,z,z,2z)`. A true ternary relation uses padding
`z+z-2z=0`; if its first partial sum is zero, flipping all three source signs makes
that partial sum nonzero. For a false ternary relation, a passing pin obeys

```text
l+c*z=0,                 c in {-4,-2,2,4}.
```

There are at most 32 passing sign orbits, so 33 distinct nonzero pins define affine
`R_3`. The preceding WNU obstruction applies. This gate reconstructs for `N>=67`.

### Fixed branch deletion and induced-template gate

Modulo global sign, the full affine relation is a union of `2^(m-1)` distinct branch
hyperplanes. Under the stated prime-size condition, every branch has a nonzero point
outside every other branch and every coordinate hyperplane. Independent lift flips
act transitively on branch classes, so an invariant fixed branch family is empty or
full. This closes fixed parity, preferred-sign, and other fixed branch catalogs.

The scope correction also reconstructs. An operation defined only on `F_x` need not
extend to the ambient Kummer quotient because the adjacent public constants and
windows can leave `F_x`. A singleton induced target fiber is preserved by every
idempotent operation, showing that induced WNU existence can be vacuous.

## Ambient-versus-induced access dichotomy

There are two materially different CSP presentations.

### Ambient presentation

Use the full rational-point `S_6` relation and five unary factor-base constraints.
Given a complete tuple, relation membership is checked by evaluating `S_6` and the
point/subgroup charts. The relation is available intensionally, but it is one of the
full fixed-arity Kummer relations covered by the producer's faithful-addition WNU
theorems. The proposed non-affine sparse-base WNU does not exist on this signature.

### Induced target-fiber presentation

For a target `R`, define

```text
T_R={(a_1,...,a_5) in F_x^5: S_6(a_1,...,a_5,x(R))=0
     and every exact chart and subgroup condition passes}.
```

If `T_R` is supplied extensionally, each row is already the desired x-source tuple.
Reading one row solves the support problem before any bounded-width algorithm runs.
If `T_R` is not supplied, every local-consistency projection asks whether a partial
assignment extends to a member of `T_R`; this is exactly a residual restricted
summation query. A witness-bearing projection is exact source unranking.

The bounded-width literature concerns a finite relational structure as a fixed
template. Here the domain, factor base, target fiber, and relation access scale with
`N`. Its polynomial-time conclusion does not make target-fiber construction free.
Even a generic `(2,3)` consistency table has up to `B^3` entries per target, and
constructing its sparse supported entries is the same missing router.

Thus the induced-template reformulation is logically valid but algorithmically
circular unless it supplies a target-independent access operation.

## Explicit FFE attempt: fivefold quotient-algebra kernel

Let the valid x-factor base be the roots of the squarefree polynomial

```text
F(T)=product_(a in F_x) (T-a),       deg(F)=B.
```

Because all roots lie in `F_p`, the reduced factor-base algebra is

```text
A_F=F_p[T]/(F) isomorphic to F_p^B.
```

For one target form the fivefold tensor algebra

```text
A_5=A_F tensor ... tensor A_F isomorphic to F_p^(B^5)
```

and the element

```text
s_R=S_6(T_1,T_2,T_3,T_4,T_5,x(R)) in A_5.
```

Multiplication by `s_R` is diagonal in the evaluation basis. Its diagonal entries
are exactly the `S_6` values on `F_x^5`. Therefore, on the reduced good-chart branch,

```text
det(M_(s_R))=Norm_(A_5/F_p)(s_R)
            =product_(a in F_x^5) S_6(a_1,...,a_5,x(R)),

ker(M_(s_R)) != 0  iff  T_R != empty.
```

A primitive kernel idempotent identifies a supported tuple. Restricting the five
coordinate multiplications to the kernel returns its five x-coordinates; exact point
and sign checks then recover the signed source row. This is an exact FFE
support-and-witness formulation.

It misses the cost gate. `A_5` has `B^5=N` base-field coordinates. The fact that
fixed-arity `S_6` has bounded individual degree gives `M_(s_R)` a bounded sum of
Kronecker terms, but one general algebra vector still has `B^5` coordinates. Direct
norm, dense Macaulay, multiplication-matrix, and black-box kernel realizations all
read, write, or materialize this payload in the explicit representation. This is the
P1514 dense quotient/moment control, not a compact target-local constructor.

The scoped disposition is representation-specific: a future succinct circuit for the
kernel is not ruled out merely by the dimension of this explicit algebra.

## Favorable split attempt: pair support versus triple support

The same relation can be organized by exact group sums. Precompute every unordered
signed pair from the factor base, retaining exact sources. For a generic/Sidon factor
base this gives

```text
|PAIR|=Theta(B^2).
```

This setup fits under `B^2.25`. A five-source target then asks for an intersection
between one pair-sum support and the target translate of a three-source support. The
triple side has

```text
|TRIPLE|=Theta(B^3)
```

in the favorable generic control. It can be streamed with smaller memory, but it
still costs `B^3` time per target; precomputing it once costs `B^3` setup and state.

The quotient-algebra flattening says the same thing without group-sum tables. Split
the bounded-degree polynomial as

```text
S_6=sum_(nu=1)^r f_nu(T_1,T_2)*g_nu(T_3,T_4,T_5;x(R)),
```

where `r` depends only on the fixed polynomial. The pair side supplies `B^2`
signature vectors and the triple side supplies `B^3` target-dependent vectors; a
zero dot product is the collision condition. No audited orthogonal-vector locator,
resultant, or norm avoids constructing or searching the triple side while retaining
exact sources.

This is exactly the corrected P1514 `2+3` control and P1515 target-local router
interface. Calling it a WNU support oracle does not change the operation.

## WNU and exact signed-lift audit

No non-affine operation `w_F:F_x^k->F_x` is supplied. More importantly, a WNU does
not create the first member of `T_R`:

- a singleton fiber is preserved by every idempotent operation;
- any fiber containing at most two tuples is preserved by ordinary ternary majority,
  because a majority of three choices from two complete tuples is one of them; and
- both facts remain useless when the tuple or fiber is not already available.

A target-specific WNU chosen after inspecting `T_R` would include the target support
as advice. A useful operation must be frozen target-independently and preserve the
entire admitted relation family without requiring its source deck.

Once a valid x-tuple is available, signed lifting is not the asymptotic obstruction at
fixed arity five. Store one rational point above every factor-base x-coordinate and
check all at most `2^5` sign choices, plus the frozen repetition, infinity, tangent,
and subgroup branches. Every accepted signed tuple is verified by elliptic addition.
This is constant work per candidate. It does not compensate for missing x-support.

## Complete cost receipt

Freeze `B=N^(1/5)`. The favorable complete-path rectangle is

```text
setup <= B^2.25=N^0.45,
query <= B^1.25=N^0.25,
B relation queries <= B^2.25=N^0.45,
optimistic factor-log algebra <= B^2=N^0.40.
```

| Route | Setup/state | Per-target work | Campaign work | Disposition |
|---|---:|---:|---:|---|
| Explicit endpoint-labelled induced template | `B^5=N` | row lookup | `B^5` already paid | Relation table is the source deck |
| Fivefold quotient-algebra norm/kernel | `B` for `F`, then `B^5` explicit algebra payload | `B^5` | at least `B^5` | Exact FFE, above rho |
| Pair plus streamed triple support | `B^2` | `B^3` | `B^4=N^0.8` | Pair setup passes; target query fails |
| Pair plus precomputed triple support | `B^3` | target intersection plus output | at least `B^3=N^0.6` setup/state | Fails setup and memory caps |
| Standard induced `(2,3)` consistency tables | template/source access already required; up to `B^3` entries | up to `B^3` plus support construction | up to `B^4` | Fixed-template CSP theorem does not construct entries |
| Hypothetical P1515 support router | at most `B^2.25` | at most `B^1.25` | at most `B^2.25` | Target only; no operation supplied |

For the explicit FFE route, the best complete time exponent is at least `1`. For the
favorable `2+3` route it is

```text
lambda=max(2/5,3/5,4/5)=4/5
```

when the `B`-target relation campaign is charged; one target already costs exponent
`3/5`. The reusable triple table instead has time and state exponent `3/5` before
rank, factor logs, or blind descent. None meets `lambda,mu<=0.45`.

If the hypothetical router existed with `s<=2.25,q<=1.25`, favorable constant
density and one independent row per query would only give the model

```text
lambda=max(s/5,(1+q)/5,2/5,target descent,verification)<=0.45.
```

Relation density, post-aggregation rank `B`, and blind-target success would still
need proof. The WNU identity does not establish any of them.

## Primary-source boundary

- Semaev's summation-polynomial construction reduces ECDLP progress to solving the
  bounded multivariate equations; it does not supply the missing sparse source
  locator: <https://eprint.iacr.org/2004/031.pdf>.
- Barto and Kozik characterize local consistency for a finite relational structure
  used as a fixed template; the theorem does not make a scaling target-fiber table
  free: <https://www.cs.cmu.edu/~odonnell/hits09/barto-kozik-bounded-width-CSPs.pdf>.
- Golovnev et al. give preprocessing tradeoffs for `kSUM`-indexing and explicitly
  leave group-dependent improvements open; their upper and conditional lower bounds
  are controls, not a lower bound for every elliptic router:
  <https://arxiv.org/abs/1907.08355>.

No checked source gives the induced elliptic support router, a source-complete WNU
algorithm, or an end-to-end generic-prime below-rho ECDLP method.

## Independent disposition

The audit records:

```text
full S3 gate:                         reconstructed scoped negative
full affine S_m, m>=5:               reconstructed scoped negative
strict full affine S4:               reconstructed scoped negative
fixed signed-branch deletion:        reconstructed scoped negative
ambient-versus-induced correction:   accepted
fivefold quotient-algebra attempt:   exact, B^5 payload
2+3 support attempt:                 exact, B^3 target side
non-affine induced WNU:               not supplied
exact x-support router:               not supplied
fixed-arity sign lift after support:  constant and admissible
contract or solver authorization:     no
breakthrough:                         no
```

P1534 should be focus-deferred with recommendation

```text
INDEPENDENT_SCOPED_AUDIT_PASS__DEFERRED_INDUCED_TEMPLATE_ROUTER_NOT_SUPPLIED.
```

The residual support operation is semantically P1515's nonlinear
implicit-batch/source-router class. IDEA-158 adds no explicit operation that removes
that obstruction, so it should not remain queued merely because an induced WNU is
logically possible.

Exactly one next action: preserve P1534 as deferred and independently audit
`ideas/artifacts/ECDLP-IDEA-159/non_diagonal_polar_theorem.md`; either supply one
nonordinary target-independent representation with a compact exact source-component
rule and complete sub-rho cost, or sign a scoped no-candidate receipt. Do not
construct a Rees algebra or authorize its review-required contract.

This audit is not an ECDLP algorithm, a generic-order result, a Shoup-bound
improvement, or a breakthrough.
