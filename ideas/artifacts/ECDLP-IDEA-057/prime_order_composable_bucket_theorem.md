# IDEA-057 prime-order composable bucket theorem

Status:
`SCOPED_NEGATIVE_EXACT_COMPOSABLE_BUCKET_LABELS_ARE_CONSTANT_OR_INJECTIVE__NONHOMOMORPHIC_CORRECTION_OPEN`

This is a theorem-only producer receipt. No contract, bucket campaign, finite
instance, relation search, toy curve, or timing run was executed. It screens
the exact nested-filter arm of the Wagner/generalized-birthday operation in
ECDLP-IDEA-057.

The result is deliberately scoped to target-independent bucket labels whose
equality is exactly composable under every group addition. It does not close a
list-restricted filter, an approximate filter with a proved support-changing
correction law, or a field-specific nonhomomorphic operation.

## Frozen interface

Let `G=<P>` be cyclic of prime order `N`. Let

```text
pi:G-->S
```

be a public bucket label. Assume bucket equality is composable:

```text
pi(x)=pi(x') and pi(y)=pi(y')
  implies pi(x+y)=pi(x'+y')
```

for every `x,x',y,y' in G`.

This condition is necessary whenever the next merge label is determined only
from the two current labels. In particular it holds if there is an operation

```text
mu:pi(G) times pi(G) --> pi(G)
```

such that

```text
pi(x+y)=mu(pi(x),pi(y)).
```

## Theorem: a composable label on prime order is constant or injective

Define

```text
x equivalent y iff pi(x)=pi(y).
```

The composability assumption makes this equivalence a group congruence. Put

```text
H={h in G: h equivalent 0}.
```

Then `H` is a subgroup. It contains zero. If `a,b in H`, composability gives
`a+b equivalent 0`. If `a in H`, add `-a` to `a equivalent 0` to obtain
`0 equivalent -a`, so `-a in H`.

Moreover

```text
x equivalent y iff x-y in H.
```

The forward implication follows by adding `-y`; the reverse follows by adding
`y`. Thus the bucket fibers are exactly the cosets of `H`, and `pi(G)` carries
the quotient group `G/H`.

Since `G` has prime order,

```text
H={0} or H=G.
```

In the first case every bucket is a singleton and `pi` is injective. In the
second case there is one bucket and `pi` is constant. No exact composable label
has a state count strictly between `1` and `N`.

## Consequence for nested birthday filters

An exact Wagner tree progressively discards label information while requiring
earlier cancellations to survive later merges. If every level uses a
target-independent label satisfying the frozen interface, then every
nonconstant level is injective and retains all `N` group states. A constant
level performs no filtering.

Therefore a prime-order generic group has no exact compressed analogue of the
proper quotient-bit projections used by generalized birthday algorithms on
groups with nontrivial quotient chains. An explicit table covering an
injective alphabet has `N` labels, while a succinct injective label merely
retains the full group point and creates no quotient collisions. A constant
state gives no filtering. Thus the exact quotient-chain operation used by the
Wagner speedup is absent; this statement alone is not a time lower bound for
every list-specific algorithm.

The x-coordinate orbit map does not contradict the theorem. It is not an exact
single-valued composable group label: adding two Kummer states has multiple
sign branches. The IDEA-158 four-window theorem shows that restoring enough
constant-size adjacent Kummer context to make addition faithful recovers a
state set of order `N`.

## Relation to existing scoped gates

IDEA-165 proves that a state-only exact ternary composition predicate forces a
bounded-degree quotient map to be injective. The theorem here expresses the
same prime-order obstruction at the more general bucket-congruence interface
used by nested list merging.

IDEA-057 remains open only to an operation outside that interface:

1. a nonhomomorphic field-derived label;
2. an explicit correction identity that transports failed merges to valid
   elliptic relations rather than merely relabelling buckets;
3. a proved support-distribution change or an implicit support router;
4. exact signed source replay through every correction branch; and
5. complete relation, cycle/rank, factor-log, masked-descent, time, and memory
   costs below rho.

Random hashes, truncated point encodings, or x-coordinate prefixes do not
preserve prior cancellations. Adding a lookup table that repairs them must
charge the table and all collision/source lists. Merely calling that table a
correction map does not leave the scoped no-go.

This theorem is not an unconditional lower bound against list-specific
filters, approximate algebraic sieves, arithmetic circuits, or nonhomomorphic
finite-field corrections. It identifies the exact algebraic operation such a
successor must change.

No relation campaign, factor-log recovery, blind descent, generic-prime
below-rho algorithm, Shoup-bound improvement, or breakthrough is established.

## Independent review checklist

1. Verify that composable bucket equality is a group congruence.
2. Verify that its zero fiber is a subgroup and all fibers are cosets.
3. Verify the prime-order constant/injective dichotomy.
4. Confirm that the Wagner consequence is limited to exact globally composable
   labels.
5. Preserve nonhomomorphic field-specific correction identities as open.
6. Check the semantic overlap and scope distinction from IDEA-165.

## Primary references

- Wagner, *A generalized birthday problem*:
  <https://doi.org/10.1007/3-540-45708-9_19>
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>
- Semaev, *Summation polynomials and the discrete logarithm problem*:
  <https://eprint.iacr.org/2004/031>
