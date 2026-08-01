# IDEA-165 fixed pair-sum quotient theorem gate

Status:
`SCOPED_NEGATIVE_BOUNDED_DEGREE_PAIR_QUOTIENT_COMPRESSION__TARGET_LOCAL_ROUTER_OPEN`

This is a theorem-only producer receipt. No contract, table, relation search,
toy curve, or experiment was run. It screens the operation declared by
ECDLP-IDEA-165: a target-independent bounded-degree rational map on pair sums
with subquadratic states and constant-list exact source inversion.

The result is deliberately scoped. It is not a lower bound against arbitrary
preprocessed sum-indexing data structures or arithmetic circuits. It shows
that the fixed rational quotient itself cannot be the missing compression:
either its pair-state image is quadratic, its exact inverse has growing
source lists, or an additional target-local router must do the original hard
work.

## Frozen interface

Let `G=<P>` be a prime-order subgroup of order `N`, written additively. Let
`F subset G` be an oriented target-independent factor base of size

```text
B = N^beta,  1 < B < N.
```

Use unordered pairs for the favorable accounting. Let

```text
D = {{S,T}: S,T in F},
|D| = B(B+1)/2,
sigma({S,T}) = S+T,
A = sigma(D) subset G.
```

Ordered slots, independent signs, or separate factor bases only increase the
source domain by a constant or replace `B^2/2` by another `Theta(B^2)` term.

Let

```text
pi: E --> C
```

be one target-independent nonconstant rational map of bounded geometric
degree `d=O(1)`, after projective completion. Its pair state is

```text
phi = pi o sigma: D --> pi(A).
```

Write `M=|pi(A)|`. An exact state-only source inverse assigns a list `U(z)`
to every state and must satisfy

```text
{S,T} in U(phi({S,T}))
```

for every admitted pair. Let `L=max_z |U(z)|`.

## Lemma 1: exact state-only composition cannot use a proper quotient

Suppose a relation predicate decides

```text
u+v+w=R
```

biconditionally from only the four states

```text
pi(u), pi(v), pi(w), pi(R)
```

for all `u,v,w,R in G`. Then `pi` is injective on `G`.

Indeed, assume `pi(u)=pi(u')`. Fix `v=w=0` and `R=u`. The state tuple for

```text
u+0+0=u
```

is identical to the state tuple for

```text
u'+0+0=u.
```

The first equation is true, so biconditional state-only evaluation makes the
second true, hence `u'=u`.

Thus a noninjective state map can be used only as a filter with false
positives, source lists, or an additional discriminator. A composable exact
quotient of a prime cyclic group is therefore not a hidden smaller group:
the only group congruences are equality and the universal congruence.

## Lemma 2: states times exact inverse list is quadratic

The source domain is the disjoint union of the exact inverse fibers, so

```text
|D| <= sum_z |U(z)| <= M*L.
```

Consequently

```text
M*L >= B(B+1)/2 = Theta(B^2).
```

In particular:

- if `L=O(1)`, then `M=Omega(B^2)`;
- if `M=O(B^(2-epsilon))`, then some exact source list has
  `L=Omega(B^epsilon)`;
- serializing target-independent inverse advice for every pair costs
  `Omega(B^2)` source references even when the states themselves are fewer.

This is an output/advice statement, not an assertion that every target query
must emit all pair fibers.

## Lemma 3: bounded rational degree does not compress generic pair sums

A nonconstant degree-`d` morphism between projective curves has at most `d`
geometric preimages of one state, counted with multiplicity. Therefore

```text
M = |pi(A)| >= |A|/d.
```

For a Sidon factor base, distinct unordered pairs have distinct sums, so

```text
|A| = |D| = Theta(B^2)
```

and every bounded-degree `pi` has

```text
M = Omega(B^2/d) = Omega(B^2).
```

This is the generic control at the campaign value `beta=1/5`. A uniformly
random `B`-set in a prime cyclic group has expected nontrivial pair-sum
collisions `O(B^4/N)`. Since `B=N^(1/5)`, this expectation is `O(N^(-1/5))`;
with probability tending to one, the factor base is Sidon up to the trivial
pair permutation.

Hence a fixed map of bounded degree cannot turn a generic pair-sum support
from `Theta(B^2)` points into `B^(2-epsilon)` states.

## Lemma 4: small doubling moves the cost into source multiplicity

An intentionally structured factor base may have

```text
|A| = |F+F| = O(B^(2-epsilon)).
```

That does not give constant-list source unranking. The average number of
unordered source pairs per pair-sum point is

```text
|D|/|A| = Omega(B^epsilon).
```

Combining this with the degree bound gives the same trilemma:

1. retain enough states or inverse advice to distinguish `Theta(B^2)` pairs;
2. accept growing source lists; or
3. use target context to select the useful pairs without expanding the
   collision fibers.

The third arm is not supplied by `pi`. It is a new target-local restricted
decomposition operation.

## The role of the public target

IDEA-165 allows an inverse to inspect `(pi(S+T),R)`, not only the state. For a
fixed target define

```text
D_R = {{S,T} in D: there exist U,V,W in F with S+T+U+V+W=R}.
```

If a target-local inverse emits every pair in `D_R` with list bound `L_R`,
the same counting argument gives

```text
|phi(D_R)|*L_R >= |D_R|.
```

For relation endpoints, `D_R` may be small. The theorem therefore does not
claim a per-target lower bound from pair counting alone. But determining
which collision-bucket members belong to `D_R`, from public `R` and without
enumerating the complementary three-source support, is exactly the missing
source-reporting five-term sum-index query. Treating this membership test as
free would assume the desired router.

Any surviving version must specify that target-local operation and charge:

- its target-independent index and inverse advice;
- every inspected collision member and complementary state;
- false positives, source lists, and exceptional fibers;
- known-log relation collection, rank, factor-log linear algebra, masked
  target descent, verification, and peak bit memory.

An arbitrary indexed or factored target router remains outside this theorem.

## Cost disposition at five sources

At `beta=1/5`, the generic bounded-degree state support has

```text
M = Omega(B^2) = Omega(N^0.4).
```

This setup size alone is below rho and below P1515's favorable
`B^2.25=N^0.45` setup cap. It is not by itself falsifying. The obstruction is
that the quotient has not reduced the pair support: a direct scan per one of
`Omega(B)` relation targets costs

```text
Omega(B^3) = Omega(N^0.6),
```

while a target-independent exact inverse still carries `Theta(B^2)` pair
payload. Avoiding that scan requires a new indexed target router with query
cost at most `B^1.25`, complete source output, and no hidden `B^3` support.
The checked generic `kSUM` indexing controls miss this rectangle, but those
upper bounds are not lower bounds on every data structure.

## Disposition for ECDLP-IDEA-165

The declared fixed bounded-degree rational quotient is scoped negative as the
compression mechanism:

- on generic/Sidon factor bases its image has `Theta(B^2)` states;
- on compressed/small-doubling supports its exact source lists grow;
- state-only exact composition forces injectivity;
- target-assisted filtering requires the unsupplied P1515-style router.

This does not reject every target-local indexed decomposition algorithm. A
mechanism-new successor must give an explicit recurrence or data structure
for the collision-membership query and satisfy the complete setup/query,
source, rank, descent, and memory gates. Merely naming `R` as an inverse input
does not construct that operation.

No relation campaign, factor-log recovery, blind descent, generic-prime
below-rho algorithm, Shoup-bound improvement, or breakthrough is established.

## Independent review checklist

An independent reviewer should verify:

1. `|D|=B(B+1)/2` is the favorable unordered-pair count;
2. state-only exact composition really forces injectivity;
3. `M*L>=|D|` counts exact source references rather than only pair-sum points;
4. a degree-`d` map has fibers of geometric size at most `d` with
   multiplicity;
5. the random-Sidon estimate is used only as a generic control;
6. small doubling is not incorrectly called impossible;
7. the target-local `D_R` exception is preserved; and
8. no checked `kSUM` upper bound is promoted into a lower bound.

## Primary references

- Green and Ruzsa, *Freiman's theorem in an arbitrary abelian group*:
  <https://arxiv.org/abs/math/0505198>.
- Golovnev et al., *Data Structures Meet Cryptography: 3SUM with
  Preprocessing*: <https://arxiv.org/abs/1907.08355>.
- The Stacks Project, *Universally bounded fibres*:
  <https://stacks.math.columbia.edu/tag/03J3>.
- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*: <https://eprint.iacr.org/2004/031>.

The references supply neighboring small-sumset, preprocessing, and elliptic
relation controls. None states the theorem gate above or a below-rho ECDLP
algorithm.
