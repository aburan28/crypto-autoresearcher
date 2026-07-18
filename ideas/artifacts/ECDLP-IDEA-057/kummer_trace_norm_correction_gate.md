# IDEA-057 Kummer trace/norm correction gate

Status:
`SCOPED_NEGATIVE_PAIRWISE_KUMMER_TRACE_NORM_IS_AN_S3_NORM_BACKEND__LIST_SPECIFIC_SUPPORT_ROUTER_OPEN`

This theorem/identity receipt screens one concrete candidate for the
nonhomomorphic exception left by the prime-order composable-bucket theorem. No
contract, finite-field search, bucket campaign, relation collection, toy curve,
or timing run was executed.

The candidate is mathematically exact but not mechanism-new: the trace and norm
of the two Kummer pseudo-sums are just the coefficients of Semaev's quadratic
`S3` branch polynomial. Aggregating those coefficients over a source deck is a
resultant/norm, and composing source-complete levels is the already frozen
P1478/P1513 recursive-resultant route. This is a scoped semantic removal, not a
lower bound against every list-specific or circuit-level algorithm.

## Pairwise Kummer identity

Let

```text
E: y^2 = x^3 + a*x + b
```

over a field of odd characteristic. For affine nonvertical inputs `u != v`, the
third summation polynomial is

```text
S3(u,v,Z)
  = (u-v)^2 Z^2
    - 2*((u+v)*(u*v+a)+2*b) Z
    + (u*v-a)^2 - 4*b*(u+v).
```

If `u=x(P)` and `v=x(Q)`, its two roots are the unordered Kummer pseudo-sums

```text
{x(P+Q), x(P-Q)}.
```

Consequently their trace and norm are

```text
tau(u,v) = 2*((u+v)*(u*v+a)+2*b)/(u-v)^2,
nu(u,v)  = ((u*v-a)^2-4*b*(u+v))/(u-v)^2.
```

Thus the proposed rank-two trace/norm state is exactly the monic normalization
of `S3(u,v,Z)`. It packages both sign branches without selecting one, which is
useful for exact evaluation, but it does not define a new elliptic correction
law.

The restriction `u != v` is not discarded. Vertical, repeated, infinity,
return, and nonreduced strata require the complete addition charts already
charged by the corpus. A candidate that omits them does not have an exact
all-strata source lift.

## Deck aggregation is a resultant

Let a public source deck be encoded by

```text
F(U) = product_i (U-u_i).
```

The branch-complete endpoint polynomial for adding one fixed Kummer state `v`
to every deck element is

```text
K_F(v,Z)
  = Res_U(F(U), S3(U,v,Z))
  = product_i S3(u_i,v,Z)
```

up to the public leading-coefficient convention. Calling each quadratic factor
by its pair `(tau,nu)` changes the evaluation representation, not the norm.

For two source decks `F` and `G`, the complete pair-endpoint object is

```text
D_(F,G)(Z)
  = Res_U(F(U), Res_V(G(V), S3(U,V,Z)))
  = product_(i,j) S3(u_i,v_j,Z).
```

The product has one quadratic leaf for every source pair. If exact source
replay is required, cofactor markers or an equivalent inverse must distinguish
those pair leaves. This is the P1478 one-transition subgroup norm when `F` has
the special sparse form `U^L-1`, and it is the P1510/P1513 source-marked
product/resultant interface for a general deck.

## Composition does not preserve a Wagner cancellation

The map `(u,v) -> (tau,nu)` is nonhomomorphic because it records an unordered
two-branch Kummer sum. It therefore avoids the prime-order congruence theorem,
but it also provides no operation that transports an earlier bucket equality
through the next group merge.

Composing another Kummer merge while preserving every sign/source branch
requires elimination of the intermediate root. At deck level this is an
iterated resultant or norm of the factors above. The pairwise quadratic degree
is constant, but the source-pair leaf family and its provenance are not removed.
The frozen controls record the resulting boundary:

- P1478 evaluates one sparse subgroup transition in logarithmic work but its
  first exact source-complete composition is a dense quadratic state object;
- P1513 keeps one shared bivariate product circuit but still lacks an
  output-sensitive common-norm/source operation below the rho threshold;
- the P1515 recursive-`S3` gate routes known norm composition to P1513/P1514
  unless a new target-local support and source-unranking primitive is supplied.

Taking a hash, prefix, residue class, or bucket of `tau` or `nu` does not repair
this gap. Such a bucket is not proved to preserve earlier cancellations, map a
failed merge to a new valid elliptic relation, or enrich successful support.
Reopening the discarded branch/source data with a table must charge that table
and every emitted preimage.

## Scoped decision

The raw Kummer trace/norm proposal is removed as a representation/backend merge,
not promoted as IDEA-057's missing nonhomomorphic correction. It proves no
support-law change and no setup/query improvement.

A mechanism-new successor must instead exhibit at least one of:

1. a list-specific field identity that changes the success support and proves
   enrichment beyond the frozen occupancy control;
2. an implicit target-support router with setup and query below the P1515
   rectangle, including exact all-strata source unranking; or
3. a correction map that sends a failed near-merge to a different exact elliptic
   relation with a proved source biconditional and full rank/descent accounting.

Any successor must remain generic over the prime family, charge exceptional
charts, failed queries, coefficient traffic, output, factor logs, blind descent,
and memory, and establish complete exponents below rho. A compact local identity,
valid relation, or toy scalar recovery is not a breakthrough.

## Independent review checklist

1. Re-derive the `S3` coefficient, trace, and norm formulas.
2. Verify that deck aggregation is the stated resultant/product identity.
3. Confirm that source-complete composition is routed only to the frozen
   P1478/P1513/P1515 controls, without claiming an unconditional lower bound.
4. Confirm that list-specific support-changing corrections and implicit source
   routers remain open.
5. Preserve all exceptional Kummer/addition strata in any successor gate.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem*:
  <https://eprint.iacr.org/2004/031>
- Chalcraft and Fryers, *Kummer structures*:
  <https://arxiv.org/abs/0806.0409>
- Wagner, *A generalized birthday problem*:
  <https://doi.org/10.1007/3-540-45708-9_19>
