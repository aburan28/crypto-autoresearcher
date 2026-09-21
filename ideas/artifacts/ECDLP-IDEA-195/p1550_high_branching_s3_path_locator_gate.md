# P1550 high-branching S3 path-locator theorem gate

## Status and claim boundary

- Record type: independent theorem-only gate
- Root hypothesis: `ECDLP-IDEA-195`
- Candidate: `P1550`
- Claim: `CLM-P1550-HIGH-BRANCHING-S3-PATH-LOCATOR`
- Evidence scale: exact Semaev one-step algebra, elliptic-curve morphism
  classification, prime-subgroup counting, finite-domain divisor counting, and
  complete asymptotic cost statements; no experiment
- Contract state: the IDEA-195 contract remains retired, `review_required`,
  unapproved, and zero-run
- Claim labels: `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__DENSE_FACTOR_POLYNOMIAL_GIVES_GENERIC_PRIME_O_B_ONE_STEP_MEMBERSHIP_AND_EXACT_GCD_SOURCE_LIFT__EVERY_GLOBAL_RATIONAL_SOURCE_BRANCH_IS_SCALAR_AFFINE_ON_THE_PRIME_SUBGROUP__SUM_IDENTITY_FORCES_ONE_PERMUTATION_COORDINATE__EACH_BRANCH_CAPTURES_AT_MOST_B_TARGETS__EXPLICIT_K_BRANCH_RELATION_WORK_IS_AT_LEAST_N_AND_BLIND_DESCENT_AT_LEAST_N_OVER_B__FINITE_DOMAIN_NONMORPHIC_SELECTOR_REQUIRES_DEGREE_AT_LEAST_B_11_OVER_4_IN_THE_ENUMERATED_BRANCH_MODEL__SUCCINCT_HIGH_DEGREE_FINITE_FIELD_CIRCUIT_UNCLASSIFIED__INCONCLUSIVE`

P1550 freezes the strongest algebraic interpretation of the `O(D)` locator
left by P1549. Put `D=B` and let the locator enumerate `K=O(B)` public
target-independent algebraic path branches. Each branch returns five rational
source maps whose elliptic sum is identically the input target; factor-base
membership decides whether the branch is accepted. This grants direct path
output and therefore grants the simultaneous trace, norm, and seven marked
channels after constant-work replay.

The family does not pass. Every rational map from an elliptic curve to itself
is a translation of an endomorphism. On the rational prime-order subgroup it
is scalar-affine. The global five-source sum identity forces at least one
source coordinate to have nonzero scalar coefficient, hence to permute the
subgroup. Requiring that coordinate to land in a factor base of size `B`
limits the whole branch to at most `B` targets, independently of its geometric
degree or straight-line-program representation. Enumerating `K` such branches
therefore costs at least `N` branch evaluations for `B` relation rows and at
least `N/B` branch evaluations for one blind descent.

This closes globally rational branch formulas and rational sections of
algebraic covers. It does not close a finite-field program whose output agrees
with point and summation equations only on selected elements of `E(F_p)`.
For an explicitly enumerated piecewise-rational version, divisor counting
forces coordinate degree at least `B^(11/4)` to meet the complete
`B^(9/4)` relation-work gate. That degree floor is not an arithmetic-circuit
lower bound: repeated powering, reduction modulo finite-field equations, and
branching can represent some high-degree functions succinctly. The exact
remaining class is therefore a compact high-degree finite-field selector
circuit, not another rational map, branch catalog, dense resultant, or solver.

There is no sub-rho ECDLP algorithm, Shoup-bound improvement, or breakthrough.

## Hash-bound inputs

- `ideas/artifacts/ECDLP-IDEA-195/p1549_noncartesian_finite_state_closure_gate.md`:
  `cd42b2b8ae71af0fb2c3d09ff264307b8705488daac2e6ec69e92a41d7c08fe1`
- `ideas/artifacts/ECDLP-IDEA-003/p1530_r1_r2_independent_audit.md`:
  `e7dfae990f357da7d1f3f8503c06d6334323d925244d3803f2a002888081c402`
- `ideas/artifacts/ECDLP-IDEA-010/p1548_torsor_deck_orbit_router_gate.md`:
  `ea22392aeebf6f436a3ed19f9126f4c618c3327437c06f25a263439208e38742`
- `ideas/artifacts/ECDLP-IDEA-098/p1515_r1_r11_independent_audit.md`:
  `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e`
- `ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md`:
  `1cc162302ba898dfbdff0ddee4483cf0935b2fe975a8782c7c0b54aa622e563e`
- `ideas/rejected/ECDLP-IDEA-135_source_faithful_decomposable_relation_circuit_hypothesis.md`:
  `782d1a0c7fc2318ed55c1348d1ff3fb1f89993dd6337ee812b37c997d9abee61`
- `ideas/rejected/ECDLP-IDEA-266_equiprojectable_dynamic_evaluation_source_tree_hypothesis.md`:
  `a9529076339b09b881d4504de45c132219352d4e0edc282cc0d2d955577ea1b1`

P1530 supplies the independently reconstructed rational-map classification.
P1548 separates rational sections from finite-field root ordering. P1515,
IDEA-120, IDEA-135, and IDEA-266 are semantic controls for explicit serial
provenance, completion-state compilation, decomposable model compilation, and
dynamic triangular source output. None is promoted or generalized here.

## Frozen generic-prime one-step correspondence

Let

```text
E/F_p be ordinary,
G=<P> subset E(F_p),
|G|=N prime,
B=N^(1/5),
F_i subset G, |F_i|<=B, i=1,...,5.
```

The `F_i` are public coloured exact signed factor bases. For each colour let

```text
X_i={x(A):A in F_i},
L_i(X)=product_(a in X_i)(X-a).
```

`L_i` is squarefree; a public dictionary records the one or two admitted
signed points above every root. This is `O(B)` setup and state per colour and
works for every prime. It does not require a large divisor of `p-1`.

For exact projective states `U,V`, use the relevant projective chart of

```text
q_(U,V)(X)=S_3(x(U),x(V),X).
```

On a nondegenerate ordinary affine chart, `q_(U,V)` has degree at most two.
Its roots are the Kummer candidates compatible with the two-valued addition relation. The
edge predicate

```text
R_i(U,V)=Res_X(L_i(X),q_(U,V)(X))
```

vanishes exactly when one Kummer candidate belongs to `X_i`. Multiplicity is
retained by the gcd and projective homogenization. At a numeric pair `(U,V)`,
reduce the dense polynomial `L_i` modulo `q_(U,V)` by Horner evaluation in the
rank-two algebra `F_p[X]/(q_(U,V))`. This takes `O(B)` base-field operations
and two field words of working state. The rank-two norm gives the resultant.

When the resultant vanishes, `gcd(L_i,q_(U,V))` has degree at most two. Its
rational roots and the signed dictionary give a constant-size candidate list
in `N^o(1)` bit work.
Direct projective group-law checks select exactly the points satisfying the
oriented transition, and reject a wrong Kummer sign. Degenerate leading
coefficient, repeated-root, tangent, vertical, pole, and infinity cases use
the preregistered projective charts and the same exact point check.

This is a genuine generic-prime positive control:

```text
setup/state: O(B),
one arbitrary edge-membership query: O(B),
source lift after a hit: O(1) candidates plus exact verification.
```

It improves the applicability of P1549's `X^d-c` one-step control. It does
not locate a four-edge path. Evaluating it on all `B^2` pairs in one layer,
composing its resultants, or supplying the intermediate states restores an
existing pair-table, dense-elimination, or provenance control.

## Frozen algebraic path-locator family

Set `D=B`, the most favorable endpoint of P1549's surviving window. An
explicit algebraic `O(D)` locator has at most

```text
K=c*D=O(B)
```

public branches. Branch `b` consists of five `F_p`-rational maps

```text
s_(b,i):E-->E, i=1,...,5,
```

defined on a dense open and extending across `E`, with the global identity

```text
s_(b,1)(R)+...+s_(b,5)(R)=R                  (1)
```

as maps `E->E`. It is accepted at a rational target `R in G` only if

```text
s_(b,i)(R) in F_i for every i.                (2)
```

The branch then returns those five exact signed sources and their four
projective `S3` transition certificates. The locator evaluates every one of
the `K` public branches or an explicitly listed equivalent branch schedule.
It receives no target-trained coefficients, source advice, root prefix,
output dictionary, or post-hoc path selector.

This family is optimistic. It grants the path directly rather than deriving
it from `D^4` continuations. Exact sources reconstruct both coefficients of
each Kummer branch, all seven square-zero channels, every sign and
multiplicity, and the final endpoint in constant work per output branch. It
also allows each `s_(b,i)` to have growing geometric degree and a succinct
addition-chain or straight-line representation.

A nonsplit algebraic cover branch does not enlarge this family. A rational
target-compatible choice of one sheet is a rational section and P1548 forces
the selected component to split. Enumerating every sheet is an explicit
branch catalog. A finite-field root-ordering program that is not a rational
section is deliberately outside the family.

This direct-output model dominates the rational shared-layer realization
assigned by P1549. If the five state layers, edge transitions, and one of the
`K=O(D)` target-conditioned path recurrences are rational on `E`, compose the
recurrence with the four edge source labels. The five returned sources are
exactly maps `s_(b,i)` satisfying (1). Forgetting the intermediate states and
granting direct source output can only lower its charged work. Therefore the
theorem below closes every explicitly enumerated rational shared-layer
recurrence as well as a branch formula written directly. A recurrence that
uses finite-field equality tests or root ordering and is not rational as the
target varies is the preserved finite-domain circuit exception.

## Prime-subgroup affine-branch theorem

Every rational map from the smooth projective curve `E` to the proper curve
`E` extends to a morphism. For each source map write

```text
s_(b,i)(R)=psi_(b,i)(R)+T_(b,i),              (3)
```

where `psi_(b,i)` is an endomorphism and `T_(b,i)=s_(b,i)(O)`.

Because the map is defined over `F_p`, `psi_(b,i)` preserves `E(F_p)`. The
near-prime-order setting has a unique rational order-`N` subgroup: `N^2` does
not divide `#E(F_p)` for the asymptotic family. Hence on `G`

```text
psi_(b,i)([u]P)=[n_(b,i)*u]P                  (4)
```

for one `n_(b,i) in F_N`. Any branch with one accepted target has
`T_(b,i) in G`, because both the accepted output and the homomorphic part lie
in `G`. Thus there is a `t_(b,i)` with

```text
s_(b,i)([u]P)=[n_(b,i)*u+t_(b,i)]P.           (5)
```

Apply (1) on `G`. Equality of the affine scalar functions gives

```text
sum_i n_(b,i)=1 mod N,
sum_i t_(b,i)=0 mod N.                         (6)
```

At least one coefficient `n_(b,i)` is nonzero. For that index, (5) is a
permutation of `G`. Its inverse image of `F_i` therefore has exactly
`|F_i|<=B` elements. Condition (2) can only reduce this set. Consequently

```text
number of accepted targets for branch b <= B.  (7)
```

The bound is independent of the branch degree, ramification, formula size,
endomorphism degree, or use of Frobenius, isogenies, Lattes coordinates, and
short multiplication chains. Those devices may make one scalar-affine map
cheap; they do not change its capture set.

The theorem assumes the global identity (1). If the point and sum equations
hold only on a finite selected subset of `E(F_p)`, the equality need not
extend to a morphism identity. That finite-domain case is treated separately
below and is not claimed closed.

## Explicit-branch work conservation

Across all `K` branches, the number of accepted branch-target incidences is at
most

```text
I<=K*B.                                         (8)
```

A uniformly sampled known scalar gives a uniform target in `G`. Even granting
one independent useful row for every accepted incidence, one attempted target
returns at most `K*B/N` expected rows. Collecting `B` rows needs at least

```text
A_rel>=B/(K*B/N)=N/K                           (9)
```

attempted targets. Evaluating the `K` explicit branches per target gives

```text
W_rel>=K*A_rel>=N=B^5.                         (10)
```

One blind masked target has success probability at most `K*B/N`, so

```text
A_desc>=N/(K*B),
W_desc>=K*A_desc>=N/B=B^4.                     (11)
```

These bounds already grant independent rank, no duplicate rows, free factor
logs, free output, free verification, no exceptional losses, and identical
known-scalar and masked-target distributions. Actual seven-channel replay and
point checks only add work. The complete `B^(9/4)=N^0.45` gate is missed by a
wide margin.

Batch evaluation that does not pay for its `K` branches is not covered by
(10). To remain outside the theorem it must publish one compact aggregate
finite-field circuit that selects and outputs the successful branch without
materializing, evaluating, or receiving the branch catalog. Naming
multipoint evaluation, a resultant, a triangular decomposition, or a compiled
decision diagram does not establish that operation; those are P1513,
IDEA-120, IDEA-135, and IDEA-266 controls until exact input and source-output
traffic are below the gate.

## Finite-domain piecewise-rational degree gate

The next broader explicit model lets a branch use rational coordinate
functions that satisfy the curve, factor-base, and sum equations only on its
accepted rational targets. Suppose branch `b` publishes

```text
(x_(b,i)(R),y_(b,i)(R)), i=1,...,5,
```

with every nonconstant coordinate having map degree at most `d`. If at least
one source coordinate is nonconstant, the inverse image of one coordinate
value has at most `d` geometric points. Membership in a factor base of size
`B` therefore limits that branch to at most `dB` accepted targets. If all five
source points are constant, their sum is constant and the branch accepts at
most one target. Thus, up to fixed chart and exceptional constants,

```text
I<=K*max(1,dB)=O(K*d*B).                       (12)
```

Let `W` be explicit branch-evaluation work. A target query checking `K`
branches permits at most `W/K` attempted targets. Equation (12) gives at most

```text
(W/K)*(K*d*B/N)=W*d*B/N                        (13)
```

expected rows. Requiring `B` relation rows yields

```text
W_rel>=N/d.                                    (14)
```

Meeting P1549's complete cap `W_rel<=B^(9/4)` therefore requires

```text
d>=N/B^(9/4)=B^(11/4)=N^0.55.                 (15)
```

For one blind row, (13) instead yields

```text
W_desc>=N/(dB)=B^4/d.                          (16)
```

Keeping that term below the same complete `B^(9/4)` cap requires

```text
d>=B^(7/4)=N^0.35.                             (17)
```

The relation gate is stronger. Dense coefficient or value-table
representations of degree `B^(11/4)` already exceed the `B^(9/4)` setup and
state budget. This eliminates explicit dense piecewise-rational catalogs.

Equations (15)-(17) are degree and explicit-enumeration gates, not lower
bounds on arithmetic-circuit size. Over `F_p`, a short circuit can have a
large reduced degree through repeated powering, Frobenius, modular reduction,
gcd logic, or equality masks. Whether such a circuit can output an exact
five-source path rather than only a membership bit is the remaining question.

## Simultaneous channels and all-strata replay

The frozen rational branch family is given the strongest possible channel
semantics. Once it outputs exact signed sources `A_1,...,A_5`, direct
projective addition verifies

```text
A_1+...+A_5=R.
```

The four intermediate states reconstruct every complete `S3` quadratic.
Their trace and norm are exact on each valid chart. Substituting the five
sources into P1537's square-zero marked norm reconstructs the constant,
constant-marker derivative, and five source-marker derivatives. Repeated
sources, tangent and vertical additions, poles, infinity, and nonreduced
fibers are accepted only through the projective point and multiplicity rules.

Giving this replay for free does not change (10) or (11). Conversely, a
locator that emits only a norm zero, trace, endpoint, whole branch orbit, or
simple-fiber derivative ratio is source-incomplete and fails before the cost
theorem is needed.

## Complete cost receipt

For the generic-prime dense-factor one-step primitive:

```text
setup/state: B,
one edge membership and exact lift: B^(1+o(1)).
```

For the frozen `K=O(B)` global rational branch locator, the optimistic direct
query cost is `K=O(B)`, but the capture theorem gives

```text
relation work >=N=B^5,
blind descent >=N/B=B^4.
```

Sparse factor-log linear algebra `B^2`, five-source output, projective
verification, and seven-channel reconstruction are all smaller than these
lower bounds under the grants above. Hence the family has

```text
lambda>=1,
```

before bit-complexity factors and cannot meet `lambda,mu<=0.45`.

For explicitly enumerated finite-domain rational branches, meeting the time
rectangle requires degree at least `B^(11/4)`. A dense representation then
misses setup/state. A succinct circuit representation remains unclassified,
so no value of `lambda` or `mu` is assigned to it and no optimistic zero is
inserted.

## Independent findings

1. A dense split factor polynomial gives a generic-prime exact `O(B)`
   one-step `S3` membership test and constant-list signed source lift.
2. The one-step primitive does not compose four transitions or locate an
   endpoint path below existing pair, provenance, and resultant controls.
3. Every global `F_p`-rational source branch is scalar-affine on the rational
   prime-order subgroup.
4. A global five-source sum identity forces at least one source coordinate to
   permute the subgroup.
5. Factor-base membership limits that branch to at most `B` target scalars,
   independently of branch degree and formula succinctness.
6. An explicit `K`-branch campaign costs at least `N` branch evaluations for
   `B` rows and `N/B` for one blind descent.
7. A finite-domain explicitly enumerated piecewise-rational selector needs
   degree at least `B^(11/4)` to fit the relation-work gate.
8. Dense representations of that degree miss the setup/state gate, but degree
   alone does not lower-bound a finite-field circuit.
9. Compact high-degree finite-field selector circuits that output exact
   all-strata source paths remain unclassified and unsupplied.
10. No contract, implementation, solver, fixture, or experiment is authorized.

## Decision

P1550 is terminal inconclusive within generic-prime dense-polynomial one-step
membership, explicit global rational source branches, rational sections,
explicit algebraic branch catalogs, and explicitly enumerated finite-domain
piecewise-rational selectors. The hoped-for `O(D)` algebraic path recurrence
is eliminated in that scope even when high degree and direct seven-channel
replay are granted.

The exact residual is narrower: a compact high-degree finite-field circuit
whose formulas need agree with the curve and sum laws only on `E(F_p)`, that
selects rather than enumerates a successful path, and that outputs all five
signed sources with complete setup, query, rank, factor-log, descent, output,
verification, bit-time, and memory costs. No audited record supplies it.

This terminal disposition is not an unconditional arithmetic-circuit lower
bound. It does not claim that generic prime-field ECDLP is impossible below
rho. It records a new degree-independent obstruction for global rational path
branches and preserves the exact finite-field-only exception.

## Exactly one next action

Freeze P1551 as a theorem-only finite-domain high-degree `S3` selector-circuit
audit. Admit only circuits built target-independently from the five dense
factor polynomials, projective `S3` coefficients, rank-two remainder/norm and
gcd operations, Frobenius or public powering, equality masks, and at most a
constant number of modular-composition stages. Require reduced source
coordinate degree at least `B^(11/4)`, setup/state at most `B^(9/4)`, one
target query at most `B^(5/4)`, exact all-strata five-source output, and the
complete `lambda,mu<=0.45` path. Derive one selector or show that this exact
grammar materializes a branch/root list, dense composed eliminant, `B^3`
provenance, or equivalent P1513/P1515 output traffic. Do not implement, run a
solver, execute the retired contract, or generate a toy fixture.
