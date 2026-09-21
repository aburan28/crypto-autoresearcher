# IDEA-098 recursive-S3 field-router candidate v1

Status:
`NO_PASSING_CANDIDATE_OPERATION__SPARSE_FACTOR_MAP_DUPLICATES_PKM16_AND_RESTORES_P1513`

This is a theorem-only candidate-and-removal receipt. No contract, polynomial
system, Grobner basis, prototype, toy curve, relation campaign, or timing run
was executed. One concrete finite-field identity is derived below, then rejected
as the missing P1515 router. The identity is useful as a positive representation
control; it is not novel and does not solve ECDLP.

## Candidate: sparse multiplicative factor map

Let `E/F_p` be a short-Weierstrass curve and suppose `d` divides `p-1`, with

```text
d = Theta(B) = Theta(N^(1/5)).
```

Let `H` be the multiplicative subgroup of `F_p^*` of order `d`, or a public
coset of it. The source x-coordinate predicate has the sparse polynomial

```text
L(X) = X^d - c.
```

When `d` is smooth, `L` is also represented by a composition of low-degree
power maps. Petit, Kosters, and Messeng use precisely this kind of factor map in
their 2016 prime-field ECDLP framework; they also give an auxiliary-isogeny
generalization for primes without the required divisor. Therefore the factor-
base construction is a literature control, not a novelty claim.

## Exact one-step norm identity

For public endpoint x-coordinates `U,V`, write the third Semaev polynomial as a
quadratic in the source coordinate `X`:

```text
q_(U,V)(X) = S3(U,V,X)
            = alpha_2(U,V) X^2
            + alpha_1(U,V) X
            + alpha_0(U,V).
```

The target-independent one-step source incidence is

```text
A(U,V)
  = Res_X(L(X), q_(U,V)(X))
  = product_(x in H_c) S3(U,V,x),
```

up to the standard leading-coefficient convention, where
`H_c={x:x^d=c}`.

Equivalently, in the rank-two quadratic algebra

```text
Q_(U,V) = F_p[X] / (q_(U,V)(X)),
```

the condition `A(U,V)=0` is the vanishing of the norm of `X^d-c`. A fixed
numeric `(U,V)` can compute `X^d mod q_(U,V)` by binary powering in
`O(log d)` rank-two algebra multiplications. If the incidence vanishes, the
candidate source x-coordinates are recovered from

```text
gcd(X^d-c, q_(U,V)(X)),
```

whose output degree is at most two.

This is a real field-specific representation gain for one transition: it is not
simulable from black-box elliptic addition alone, and it avoids listing all `d`
source x-coordinates when evaluating one numeric transition.

## Fatal boundary 1: it is not generic in the prime

The simple identity requires a divisor `d=Theta(p^(1/5))` of `p-1`; a generic
prime does not provide one. Smoothness of that divisor is additionally required
for the low-degree composition used in the PKM16 system.

The auxiliary-isogeny construction in PKM16 extends the factor-map idea to
arbitrary primes only after finding a suitable smooth subgroup on an auxiliary
curve and composing the associated rational maps. That construction still
defines a factor-base constraint; it does not supply the target router required
here.

Consequently the multiplicative-subgroup arm cannot establish an algorithm for
generic ordinary prime-field curves. It may remain a restricted-prime control.

## Fatal boundary 2: x-membership is not exact point membership

Not every `x in H_c` is the x-coordinate of an `F_p`-rational point on `E`.
The exact source predicate also requires

```text
x^3+a*x+b is zero or a quadratic residue in F_p,
```

plus coherent y signs and the projective exceptional charts. Keeping `L` sparse
therefore admits false x-only branches that must be lifted and filtered.

One may precompute the exact point-bearing subset and its dense root polynomial,
but that destroys the declared sparse `X^d-c` representation in general. One
may instead retain `L` and verify outputs; this preserves true sources but must
charge failed nonrational branches and still does not give target routing.

Thus the rank-two gcd is only a local x-source candidate. It is not the required
all-strata signed source biconditional.

## Fatal boundary 3: five-step routing restores occupied objects

The P1515 query is not one transition. It must solve the chain

```text
L(u1)=0,
A(u1,u2)=0,
A(u2,u3)=0,
A(u3,u4)=0,
A(u4,x_R)=0,
```

with coherent projective sign branches, and recover five exact factor sources.
Each `A` correspondence has degree
`Theta(B)` even when represented by a short powering circuit. The identity gives
no algorithm that finds a target-conditioned path through four correspondences
in `B^(1.25+o(1))` work.

The standard ways to compose or solve the chain are already occupied:

1. Specialize endpoints or retain parent alternatives: P1511/IDEA-134 local
   states and `B^3` provenance.
2. Eliminate an intermediate endpoint between two compact transition norms:
   the P1513 shared product/norm/common-factor object.
3. Expand coefficients, quotient bases, resultants, or moments for the complete
   fiber: the P1514 dense elimination/moment-constructor controls.
4. Materialize the squarefree source components or lift paths: the P1515-R1
   universal facet-deck negative.

The compact circuit for `X^d mod q` does not make the composed correspondence's
degree disappear. A new output-sensitive circuit solver would still have to be
derived; assuming it is exactly the missing operation.

## Budget verdict

The candidate supplies no proven pair `(s,q)` for complete five-source routing.
Only the numeric one-transition membership circuit has logarithmic depth in
`d`. The full path remains at an unresolved P1513/P1514 solve, so it cannot be
entered as `s<=2.25,q<=1.25` evidence.

```text
one_step_sparse_membership: positive_control
generic_prime_coverage: fail
exact_signed_point_lift: incomplete
five_step_target_router: not_supplied
P1511_removal_test: fail_on_explicit_states
P1513_removal_test: fail_on_composed_transition_norm
P1514_removal_test: fail_on_dense_system_solution
P1515_promotion: reject
```

## Disposition

No concrete identity checked in this action survives as the P1515 field router.
The sparse factor-map identity is preserved because it clarifies the remaining
obstruction: compact factor-base membership and compact one-step incidence are
not compact target-to-source path finding.

P1515 remains open only to an operation that is simultaneously:

1. generic across the relevant prime fields or equipped with a complete generic-
   prime construction;
2. exact on rational signed points and every exceptional stratum;
3. target-independent in setup;
4. output-sensitive across the composed recursive-`S3` chain; and
5. distinct from explicit states, sum indexing, P1513 norms, and P1514 dense
   elimination, with `s<=2.25,q<=1.25` proved.

No such operation is supplied here.

## Controls and nonclaims

- PKM16 smooth-subgroup and auxiliary-isogeny factor maps are literature
  controls.
- Exhaustive evaluation of `X^d-c`, dense exact-source root polynomials, and
  generic Grobner solving are negative controls.
- A correct one-step membership test or recovered source x-coordinate is not a
  relation campaign, factor-log solve, blind descent, or ECDLP algorithm.
- No generic-group lower-bound improvement or breakthrough is claimed.

## Exactly one next action

Obtain independent static review of the P1515 R1-R5 receipt chain and either
freeze a mechanism-new successor with one explicit target-routing recurrence or
mark P1515 `deferred_no_candidate_operation`. Do not authorize the planned
P1515 contract or any solver search from the sparse factor-map identity.

## Primary references

- Petit, Kosters, and Messeng, *Algebraic Approaches for the Elliptic Curve
  Discrete Logarithm Problem over Prime Fields*:
  <https://christophe.petit.web.ulb.be/files/16PKC_primeECDLP.pdf>.
- Semaev, *Summation polynomials and the discrete logarithm problem on elliptic
  curves*: <https://eprint.iacr.org/2004/031>.
- Amadori, Pintore, and Sala, *On the discrete logarithm problem for prime-field
  elliptic curves*: <https://eprint.iacr.org/2017/609>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.
