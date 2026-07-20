# P1546 split-Jacobian projected-smoothness counting gate

## Status and claim boundary

- Record type: independent theorem-only gate
- Root hypothesis: `ECDLP-IDEA-002`
- Candidate: `P1546`
- Claim: `CLM-P1546-SPLIT-JACOBIAN-PROJECTED-SMOOTHNESS`
- Evidence scale: exact conorm/norm, Abel-map, bounded-correspondence,
  projected-support, and known-log relation statements; heuristic matched-random
  divisor control; no experiment
- Contract state: the IDEA-002 contract remains `review_required`, unapproved,
  and unexecuted
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__CONORM_NORM_RELATIONS_PROJECT_TO_DIRECT_E_RELATIONS__DEGREE_G_ABEL_MAP_IS_BIRATIONAL_ON_A_DENSE_OPEN__FIXED_REDUCTION_BRANCH_IS_A_BOUNDED_DEGREE_CORRESPONDENCE__ONE_BRANCH_CAPTURES_ONLY_O_B_SPARSE_ATOM_TARGETS__FINITE_COVER_FIBERS_GIVE_ONLY_BOUNDED_PROJECTED_MULTIPLICITY__EXPLICIT_DITHER_BRANCHES_CONSERVE_COVERAGE_AND_WORK__FIXED_BRANCH_RELATION_COLLECTION_IS_LINEAR_AND_BLIND_DESCENT_IS_N_OVER_B__ARBITRARY_KERNEL_RESIDUAL_IS_A_TAUTOLOGICAL_PROJECTED_CERTIFICATE__TUPLE_FIRST_RELATIONS_LACK_KNOWN_SOURCE_LOGS__STANDARD_JACOBIAN_INDEX_CALCULUS_IS_SOURCE_RHO_WORSE__GROWING_DEGREE_OR_IMPLICIT_TARGET_ROUTER_UNCLASSIFIED__INCONCLUSIVE`

For every fixed bounded-degree cover and every fixed algebraic reduction or
kernel-dither branch, the reduced divisor above the source line traces a curve
inside a symmetric power of `C`. A target-independent atom set of size `B` can
meet such a branch at only `O(B)` source points, with a constant determined by
the support-correspondence degree. Trying an explicit catalog of dithers raises
coverage and branch-evaluation work by the same factor. With bounded cover
degree, collecting the projected factor-base rows therefore costs
`Omega(N)` branch evaluations, while one blind target descent costs
`Omega(N/B)`.

Allowing an arbitrary kernel residual removes the auxiliary-factor constraint,
but then the accepted identity is exactly an ordinary relation among the norm
images on `E`; the cover has not found it. Enumerating smooth tuples first also
fails the known-log interface: their projected endpoint is public as a point but
its scalar relative to `P` is the original ECDLP. The exact surviving operation
is a compact target-local router that selects a favorable high-degree or
nonalgebraic branch without scanning its catalog. IDEA-002 supplies no such
router or complete cost.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-002_split_jacobian_projected_smoothness_hypothesis.md`:
  `76b0857c718388cc1e054b09362952b9e2dab5874af6eca8b8a316e1bbbf4ffc`
- `ideas/contracts/ECDLP-EXP-CONTRACT-002_split_jacobian_projection_preflight.yaml`:
  `9c45c941f88c5f4c4743e64904644eafabe39c15d8e1ae047b7fef72211ca342`
- `ideas/artifacts/ECDLP-IDEA-009/p1545_trace_zero_cross_encoding_gate.md`:
  `7bdfcbd66e2e559f38d91fece064b19c262d94ac26278a1ee290bb9c41841184`
- `ideas/rejected/ECDLP-IDEA-037_generalized_jacobian_kernel_dither_descent_hypothesis.md`:
  `6c6839e1106f319deaea02cc304c4abe01defa034572c530dad982ea9d4e10f0`
- `ideas/rejected/ECDLP-IDEA-043_imprimitive_monodromy_split_fiber_descent_hypothesis.md`:
  `717a46432521d4628268883a74cf1be07a1b10f4208e7462bf365e32bc37f892`
- `ideas/artifacts/ECDLP-IDEA-001/exact_spectral_rank_density_gate.md`:
  `e572713a3910ef6a3e31ac360123aa8b5135c75d4210cbfb579e6831e9746fca`
- `ideas/reviews/REDTEAM-20260718T123537-0700.md`:
  `6e4eacfcc3fa50e21bf476f60890e05192b5d529a8a444046e33772ad9ab19c9`

The rejected IDEA-037 and IDEA-043 records are semantic controls, not
experiments to revive. The IDEA-001 receipt supplies a nearby exact
rank/density boundary. None is overwritten or promoted.

## Frozen interface

Let

```text
E/F_q be ordinary,
H=<P> subset E(F_q),
ord(P)=N prime,
N=q^(1+o(1)).
```

Let `pi:C->E` be a target-independent finite cover of degree `d`, with `C`
smooth of genus `g`, and write

```text
i=pi^*:E=J(E)->J(C),
n=pi_*:J(C)->E,
n*i=[d].
```

The frozen contract takes `d` and `g` from fixed sets. It also requires
`gcd(d,N)=1`. Let `A` be a target-independent set of bounded-degree divisor
atoms on `C`, initially the rational-point atom model, with

```text
|A|=B_up.
```

After zero, duplicate, sign-equivalent, and auxiliary-factor columns are
removed, let

```text
F=n(A) intersect H,
|F|=B=N^beta.
```

A successful known-log relation must start from a public scalar `a`, set
`R=[a]P`, and return a verified identity whose norm is

```text
[d]R=sum_j e_j F_j.
```

It must retain enough source labels to form a row in the same frozen `B`-column
matrix. Blind descent must use the identical atom base and branch policy on
`Q+[t]P` without target-trained advice.

## Conorm and norm do not create a relation

For a degree-zero divisor class `D` on `E`, pullback and pushforward obey

```text
pi_* pi^*(D)=[d]D.
```

Consequently, an exact Jacobian identity

```text
i(R)=sum_j e_j D_j+K,
n(K)=O,
```

projects to

```text
[d]R=sum_j e_j n(D_j).
```

This proves correctness of a supplied relation. It says nothing about how to
find the `D_j`, how often a fixed atom base works, whether the projected columns
are distinct, or how to decompose a fresh target. Since `[d]` is invertible on
`H`, conorm neither collapses nor enlarges the source prime-order line.

If `K` is allowed to be the post-hoc difference

```text
K=i(R)-sum_j e_j D_j,
```

then `n(K)=O` is equivalent to the projected E relation itself. Calling this
`K` a certificate does not locate the tuple. This is the exact quotient-collapse
control occupied by rejected IDEA-037.

## Abel-map branch normal form

Fix a base point on `C`. The Abel map

```text
a_g:C^(g)->J(C)
```

from the `g`th symmetric power is birational. More generally, for every
`m<=g`, `C^(m)->W_m` is birational. Therefore, away from the special-divisor
and chart boundaries, reduced-divisor output is a rational inverse branch of
the Abel map.

Fix one kernel dither `K_j` and one reduction chart. Restrict reduction to the
embedded source line:

```text
sigma_j:E --> C^(m),
a_m(sigma_j(R))=i(R)+K_j,
m<=g.
```

The map is rational on a dense open subset. Piecewise reduction gives a finite
catalog of such maps for fixed geometry. If `sigma_j` were constant, its Abel
image would be constant, contradicting the nonconstant term `i(R)`. Thus every
correct branch has nonconstant divisor support.

## Sparse-atom capture theorem

Let `sigma:E-->C^(m)` be one nonconstant rational branch. Form its universal
support incidence

```text
I_sigma={(R,Z): Z occurs in sigma(R)} subset E x C.
```

Away from finitely many exceptional points, `I_sigma->E` is finite of total
degree `m`. At least one irreducible component `I_0` has nonconstant projection
to `C`; otherwise every support component, and hence `sigma`, is constant. Put

```text
Delta=deg(I_0->C).
```

For a finite rational atom set `A subset C(F_q)`, if `sigma(R)` is supported on
`A`, then `I_0` contains at least one pair `(R,Z)` with `Z in A`. Each atom has
at most `Delta` preimages on `I_0`, counting multiplicity. Hence

```text
#{R in E(F_q): supp(sigma(R)) subset A}
  <= Delta*|A|+O(1).
```

The `O(1)` term contains the frozen chart, pole, repeated-point, and special
divisor exceptions. For a bounded cover, bounded genus, and a fixed reduction
grammar, `Delta=N^o(1)`. The same proof applies to a fixed-degree place base
after replacing rational support points by its finite atom parameter set.

This is a branch theorem, not a claim that arbitrary structured atom tuples are
random. It is stronger than the naive `B_up^g` count for the frozen reduced
branch because the source line traces only a curve in `C^(g)`.

## Projected-support multiplicity theorem

For rational-point atoms, every point of `E` has at most `d` geometric
preimages under `pi`, counting multiplicity. After atoms with zero or
inadmissible projections are discarded,

```text
B_up <= d*B+O(d).
```

Thus bounded cover fibers can multiply an E-factor column only by a bounded
constant. Counting all upstairs points as independent logarithm unknowns would
overstate both witness supply and matrix rank. Sign variants and repeated norm
images are the same control.

Combining this with the capture theorem, one fixed branch is successful on at
most

```text
O(Delta*d*B)
```

of the `N` source scalars.

## Explicit dither work-conservation theorem

The contract's known-log relation phase samples public scalars `a`, constructs
`R=[a]P`, and evaluates fixed reduction or kernel-dither branches. One branch
evaluation returns at most one materialized row in the frozen interface. Under
the favorable assumptions that every successful row is valid, distinct, and
independent, the success probability of a uniformly sampled known scalar on a
fixed branch is at most

```text
p_branch=O(Delta*d*B/N).
```

At least `B` useful rows are required. The expected number of branch
evaluations is therefore

```text
T_rel >= B/p_branch=Omega(N/(Delta*d)).
```

For a fixed bounded-degree cover and fixed reduction grammar,

```text
T_rel=Omega(N^(1-o(1))).
```

Blind target descent needs only one success, but obeys

```text
T_desc >= 1/p_branch
       = Omega(N/(Delta*d*B))
       = N^(1-beta-o(1)).
```

At the contract gate `beta<=0.20`, blind descent alone has exponent at least
`0.80`.

Trying `T` explicit dithers does not improve these branch-evaluation bounds.
The union can cover at most `O(T*Delta*d*B)` scalars, while evaluating that
catalog costs `T` per target. Sampling branch-target pairs yields the same
success fraction. If each success materializes `L` rows, outputting and
verifying those rows costs `Omega(L)`; an implicit multirow producer is outside
this theorem and must expose its rank and source inverse.

A table that maps covered source points to successful branch IDs stores
`Omega(T*B)` incidences and reaches linear state when it covers a constant
fraction of `H`. A compact target-local router could avoid scanning or storing
that table. Such a router is precisely the unresolved operation, not evidence
for the explicit dither catalog.

## Tuple-first known-log trap

One can enumerate atom tuples, add their norm images, and obtain a public point

```text
R_tuple=sum_j e_j n(D_j) in E(F_q).
```

For base-log relation collection, however, the left side must have a known
scalar `a` with `R_tuple=[a]P`. Computing that scalar for a tuple-first endpoint
is the source ECDLP. If every projected atom was constructed with a known
source logarithm, the factor-base logarithms are already known and the only
remaining task is direct target decomposition over those E points.

Therefore a tuple-first smooth-divisor catalog is not a known-log relation
generator. Starting from known `a` and finding the tuple is exactly the
target-local projected E sum problem. Norm projection verifies its answer but
does not solve it. Summation polynomials, FFE, Groebner bases, resultants, and
sparse solvers are backends for that relation predicate, not the missing
source-return operation.

## Exact-image and random-divisor controls

Requiring `K=O` is stronger than requiring only the projected relation. The
addition map `C^g->J(C)` has a one-dimensional preimage over the embedded
elliptic factor. For a matched random atom subset of density `B_up/q`, the
heuristic expected number of atom-supported exact conorm representatives is

```text
N*(B_up/q)^g.
```

Equivalently, among `B_up^g` generic tuples, the auxiliary factor contributes
`g-1` independent base-field constraints. This is a matched-random heuristic,
not a theorem against deliberately correlated atom sets. The exact capture
theorem above closes each fixed bounded-degree reduction branch without using
this heuristic.

Sampling a random kernel element makes the translated class random inside its
kernel coset. If reduction behaves like a random Jacobian representative, its
probability of support in a sparse rational-point base is `(B_up/q)^g`, not
`B_up^g/N`. A measured departure from this control would still need the same
known-log relation and blind-descent path.

## Standard index-calculus and cover controls

For fixed genus `g>=2`, standard index calculus in the full Jacobian has
base-field complexity

```text
tilde O(q^(2-2/g)).
```

Relative to the source subgroup `N=q^(1+o(1))`, this is at least `N^1` for
`g=2` and has larger exponent for `g=3,4`. Solving the full split Jacobian is
therefore source-rho worse. The special conorm-image distribution must do the
work; a generic Jacobian solver cannot be credited to it.

Classical cover and Weil-descent attacks transfer DLPs defined over non-prime
extension fields to lower-base-field Jacobians. The reviewed cover-attack source
explicitly limits its stated family to non-prime fields. It does not establish
the IDEA-002 generic prime-field transfer.

The split-Jacobian identity itself is standard: a maximal degree-`d` elliptic
subcover of a genus-two curve has a complementary elliptic subcover and an
isogeny from the Jacobian to their product. Existence of that isogeny supplies
neither sparse projected smoothness nor a target-local source return.

## Growing-degree and adaptive boundary

Let

```text
d=N^alpha,
Delta=N^kappa.
```

The favorable fixed-branch bounds become

```text
T_rel >= N^(1-alpha-kappa-o(1)),
T_desc >= N^(1-alpha-kappa-beta-o(1)).
```

These formulas do not alone close a growing-degree cover represented by a
compact circuit, because algebraic degree need not equal evaluation cost. Such
a successor must publish the cover and reduction circuits, applicability
density, coefficient and field representation, output degree, branch policy,
atom-image multiplicities, source-return algorithm, and memory. Dense equations,
full fibers, or explicit branch catalogs must charge their degree-sized payload.

Likewise, a compact adaptive nonalgebraic router may choose among exponentially
many reduction paths without evaluating them all. It remains outside the
bounded-correspondence catalog theorem. Its predicates and updates must be
public and independently checked; the router cannot be inferred from toy
smoothness counts or a post-hoc successful branch.

## Complete cost receipt

Use the frozen model

```text
lambda=max(c+zeta,kappa_rep,beta+r+delta,2*beta,
           r+delta_t,beta+v,v),
mu=max(s,beta,kappa_rep).
```

For a bounded cover and one fixed algebraic branch, the exact capture theorem
gives favorable relation exponent at least one and target exponent at least
`1-beta`. An explicit dither catalog cannot lower either after branch
evaluations are charged. A full Jacobian solve has exponent at least one
relative to `N`. A complete atom or branch table has state exponent one when it
covers the source line. None passes `lambda,mu<=0.45`.

IDEA-002 supplies no cost for a compact implicit branch router or growing-degree
correspondence. Missing construction, representation, query, density, rank,
descent, output, verification, and state exponents are not assigned optimistic
zeros. Its 300 CPU-hour toy contract cannot classify that operation because no
such operation is frozen in the contract.

## Independent findings

1. Conorm followed by norm is `[d]` and preserves the source DLP relation; it
   does not produce a decomposition.
2. The degree-`g` Abel map is birational, so fixed reduced-divisor output on the
   embedded source line is a finite rational branch catalog on a dense open.
3. A nonconstant branch meets a target-independent atom set of size `B_up` at
   only `O(Delta*B_up)` source points.
4. A degree-`d` cover has at most `d` upstairs rational atoms over one projected
   E point; fiber multiplicity is not logarithmic rank.
5. Fixed bounded-degree branch relation collection needs `Omega(N)` branch
   evaluations, and blind descent needs `Omega(N/B)`.
6. Explicit kernel dithers conserve coverage and evaluation work; a complete
   branch incidence table has linear state.
7. An arbitrary kernel residual is equivalent to the projected E relation and
   gives a verifier, not a locator.
8. Tuple-first projected endpoints lack known source logarithms; reversing the
   query is the direct E factor-base sum problem.
9. Standard full-Jacobian index calculus is source-rho worse for the frozen
   prime-field objective.
10. Growing-degree compact circuits, implicit multirow producers, and compact
    adaptive target-local routers remain unclassified, but IDEA-002 supplies
    none with a complete cost.

## Disposition and next action

P1546 is terminal inconclusive within bounded-degree covers, bounded genus,
fixed rational reduced-divisor branches, finite chart catalogs, explicit kernel
dithers, arbitrary post-hoc kernel residuals, tuple-first projected relations,
standard full-Jacobian index calculus, and the frozen review-required contract.
Preserve IDEA-002, IDEA-037, IDEA-043, IDEA-001, and this receipt. Do not
implement or execute the IDEA-002 contract.

Exactly one next action: rerank outside bounded algebraic reduction branches,
quotient-kernel dithers, fixed-degree cover multiplicity, and relation-only norm
certificates. Bind one mechanism-distinct P1547 theorem question. Reopening
IDEA-002 requires an explicit compact growing-degree or adaptive target-local
router, its exact source inverse, distinct projected support and rank, identical
blind target descent, and complete bit costs in the proposal.

No generic-prime ECDLP recovery, factor-log solve, blind descent, below-rho
algorithm, Shoup-bound improvement, or breakthrough is established.

## Primary references

1. J. S. Milne, *Jacobian Varieties*, especially symmetric powers and the
   birational Abel map, <https://www.jmilne.org/math/xnotes/JVs.pdf>.
2. T. Shaska, *Curves of genus 2 with (n,n)-decomposable Jacobians*,
   <https://arxiv.org/abs/math/0312285>.
3. P. Gaudry, *Index calculus for abelian varieties of small dimension and the
   elliptic curve discrete logarithm problem*,
   <https://doi.org/10.1016/j.jsc.2008.08.005>.
4. C. Diem, *On the discrete logarithm problem in class groups of curves*,
   <https://www.math.uni-leipzig.de/~diem/preprints/small-genus.pdf>.
5. C. Diem and J. Scholten, *Cover Attacks*,
   <https://www.math.uni-leipzig.de/~diem/preprints/cover-attacks.pdf>.
6. V. Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
   <https://www.shoup.net/papers/dlbounds1.pdf>.

These sources establish the Jacobian, split-cover, full-Jacobian complexity,
classical cover-attack, and generic controls. The sparse-atom capture and
explicit-dither work-conservation theorems above are direct deductions. None
supplies the missing prime-field target-local router or a complete sub-rho path.
