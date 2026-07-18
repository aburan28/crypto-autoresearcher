# IDEA-057 ECFFT auxiliary-isogeny router gate

Status:
`SCOPED_NEGATIVE_ECFFT_AUXILIARY_TREE_IS_NOT_A_TARGET_GROUP_ROUTER__LIST_SPECIFIC_INTERTWINER_OPEN`

This is a theorem-only producer receipt. No contract, ECFFT construction,
finite-field search, curve fixture, bucket campaign, relation search, or timing
run was executed. It screens one concrete generic-prime realization of the
field-specific exception left by the prime-order bucket and Kummer trace/norm
gates.

ECFFT supplies fast polynomial evaluation sets over every sufficiently large
finite field by taking x-coordinates from a coset of a smooth subgroup on a
well-chosen auxiliary elliptic curve and descending through low-degree
isogenies. That is a genuine generic-field polynomial-arithmetic primitive. It
does not by itself supply a quotient or correction hierarchy for addition on a
different prime-order target curve.

The result below is scoped to using the ECFFT tree directly as the missing
P1515/IDEA-057 target router. It does not rule out a new list-specific identity
that intertwines an auxiliary rational map with the target curve's recursive
`S3` relation on the admitted supports.

## Frozen interface

Let `E/F_p` contain the cryptographic subgroup

```text
G=<P>,  |G|=N,
B=N^(1/5),
N=Theta(p),
```

where `N` is an odd prime. Let the signed factor alphabet have size
`Theta(B)`. A useful router must preserve or recover exact signed source points,
including vertical, repeated, infinity, and nonreduced strata.

An ECFFT tree over `F_p` consists of sets

```text
L^(0) -> L^(1) -> ... -> L^(k)
```

and degree-two rational maps `psi_i` such that `psi_i` is two-to-one from
`L^(i)` onto `L^(i+1)`. The construction obtains the sets from x-coordinates of
a coset of a `2^k`-subgroup on an auxiliary elliptic curve. The ECFFT existence
theorem permits `2^k=O(sqrt(p))` uniformly over large finite fields.

The proposed router would use the ECFFT hierarchy either on `E` itself, on a
curve isogenous to `E`, or as an unrelated field-coordinate hierarchy whose
labels are applied to intermediate sums on `E`.

## Theorem 1: a low-degree isogeny does not bucket the prime subgroup

Let

```text
phi:E -> E'
```

be an `F_p`-rational isogeny with `deg(phi)<N`. Its restriction to `G` has
kernel

```text
ker(phi|_G) = G intersection ker(phi),
```

which is a subgroup of the prime-order group `G`. The kernel is therefore
`{O}` or `G`. The second case would put all `N` elements of `G` in the isogeny
kernel, impossible when `deg(phi)<N`. Hence `phi|_G` is injective.

The same conclusion holds whenever `gcd(deg(phi),N)=1`. In particular, an
ECFFT chain of total degree `2^k=O(sqrt(p))<N` is injective on `G` for the
frozen asymptotic family. Its x-coordinate label satisfies

```text
x(phi(P)) = x(phi(Q))  implies  P=Q or P=-Q
```

on `G`. Thus the chain gives no growing rational quotient alphabet on the
target subgroup: after the ordinary Kummer sign quotient, every label remains
injective.

This is the isogeny form of the P1523 prime-order congruence boundary. The
degree-two fibers used by ECFFT live on the auxiliary smooth subgroup; they are
not degree-two fibers on `G`.

## Theorem 2: an unrelated auxiliary tree has no supplied addition law

Suppose instead that the ECFFT curve `A/F_p` carries the required smooth
subgroup but is unrelated to the target curve. The rational maps `psi_i` act on
field coordinates and retain their two-to-one property on the particular
ECFFT sets `L^(i)`. They do not come with an identity of the form

```text
label(P+Q) = MU(label(P),label(Q))
```

for points on `E`, nor with a correction law that maps a failed merge to a new
exact relation on `E`.

If a nonconstant elliptic-curve morphism were supplied to transport the
auxiliary group law to the target, then after translating the origin it would
be an isogeny. Its restriction to `G` would return to Theorem 1. Without such a
map, applying `psi_i` to target x-coordinates is only a rational hash/filter.
The ECFFT polynomial-decomposition theorem does not make it composable under
the target group law.

The exact algebraic witness needed to escape this conclusion is a
source-compatible factorization such as

```text
Res_Z(S3_E(X,Y,Z), T-psi(Z))
  = c(X,Y) * H(psi(X),psi(Y),T)
```

on the frozen source and partial-sum supports, together with bounded branch
growth and an exact inverse to every signed source. No such identity is supplied
by ECFFT. If asserted globally as a single-valued exact label law, it falls back
under P1523; a genuinely list-specific factorization remains outside scope.

## Canonical degree-two coefficient test

The first ECFFT isogeny map can be written, after choosing a model with a
rational two-torsion point, in the canonical form

```text
psi(Z) = Z + c + d/Z.
```

Its generic deck involution is `Z -> d/Z`. Let `z_1,z_2` be the roots of the
target curve's `S3(X,Y,Z)`, and write their trace and norm as `tau(X,Y)` and
`nu(X,Y)`. The trace after applying `psi` to both Kummer branches is

```text
Theta_psi(X,Y)
  = psi(z_1)+psi(z_2)
  = tau(X,Y) + 2*c + d*tau(X,Y)/nu(X,Y).
```

If the branch polynomial after `psi` factored globally through `psi(X)` and
`psi(Y)`, then `Theta_psi` would be invariant under the deck involution in
either input. This necessary condition already fails identically.

For the nonsingular target model

```text
E: y^2=x^3+1,
d=1,
Y=2,
```

direct substitution into the exact `S3` trace and norm formulas gives

```text
Theta_psi(X,2)-Theta_psi(1/X,2)
  = 9*(X-1)*(X+1)*(2*X^2+X+2)
    / ((X-2)^2*(2*X-1)^2),
```

which is a nonzero rational function. The additive constant `c` cancels. This
single exact specialization disproves a universal generic-curve factorization
for the canonical degree-two auxiliary map. It is a symbolic identity check,
not a finite scaling experiment.

The test does not rule out an exceptional target curve, a different rational
map, or a factorization valid only on a frozen factor-base/partial-sum support.
Those are precisely the list-specific intertwiner exceptions retained here.

## Occupancy gate for keeping partial sums inside the FFT tree

One attempted repair is to require each target-curve partial sum to have
x-coordinate in an ECFFT set so the next tree map remains in its certified
domain. On the frozen low-additive-energy/random-support control, a pair sum is
uniform up to lower-order collision effects. For a certified set `M subset F_p`
with

```text
|M| = O(sqrt(p)) = O(N^(1/2)),
```

the expected number of factor-base pairs whose sum lands in `M` is at most

```text
O(B^2 * |M|/N)
  = O(N^(2/5+1/2-1))
  = O(N^(-1/10)).
```

Thus even the first merge is empty with probability tending to one in this
control. To obtain constant expected first-merge occupancy from a fixed explicit
support requires

```text
|M| = Omega(N/B^2) = Omega(N^(3/5)) = Omega(B^3),
```

already beyond both one ECFFT tree's generic-field size and the P1515
`B^2.25` setup cap. An explicit union of enough trees has the same support-size
charge.

This is a model-bound occupancy removal, not an unconditional additive-energy
theorem for every structured factor base. A succinct union or a factor base
whose pair sums are provably enriched in the auxiliary sets would be a new
list-specific support-changing operation and must state that theorem explicitly.

## Fast polynomial arithmetic does not supply source routing

ECFFT can accelerate evaluation, interpolation, multiplication, division, and
related dense univariate operations over arbitrary finite fields. Those
algorithms preserve the polynomial's degree and the number of evaluation
values; their local transforms are invertible linear changes of representation.

Consequently:

1. using ECFFT for a degree-`B^3` pair/triple or provenance polynomial changes
   the polynomial-arithmetic backend, not the `B^3` exact state/source charge;
2. using it to evaluate the pairwise Kummer trace/norm object returns to the
   P1524 `S3` norm/resultant backend;
3. composing transition norms returns to the P1513 common-norm circuit unless
   a new output-sensitive exact source splitter is proved; and
4. expanding a target fiber or quotient basis returns to the P1514 dense
   elimination/moment controls.

This semantic routing grants quasi-linear polynomial arithmetic wherever
applicable. It does not infer a lower bound against a nonlinear arithmetic
circuit whose cost is not proportional to dense degree or explicit source
traffic.

## Scoped decision

The following proposed mechanisms are removed:

1. use a same-curve or isogenous ECFFT chain as a nontrivial quotient hierarchy
   on the prime-order target subgroup;
2. apply an unrelated auxiliary tree to target x-coordinates and assume its
   two-to-one fibers compose under target addition;
3. keep every partial sum inside one certified `O(sqrt(p))` ECFFT set on the
   low-energy occupancy control; and
4. credit ECFFT's fast dense polynomial operations as the missing exact
   endpoint-to-source router.

The surviving mechanism is narrower:

```text
an explicit list-specific ECFFT/S3 intertwining identity that changes partial-
sum support, stays generic in p, avoids global quotient composition, and returns
all exact signed sources with setup <= B^2.25 and query <= B^1.25
```

It must also prove independent relation rank, factor-log calibration, masked
target descent, failed-query/output costs, and complete time and memory
exponents below `1/2`. A fast FFT, valid local factorization, relation, or toy
scalar is not a breakthrough.

No relation campaign, factor-log solve, blind descent, generic-prime below-rho
algorithm, Shoup-bound improvement, or ECDLP breakthrough is established.

## Independent review checklist

1. Verify that `ker(phi|_G)` is trivial for `deg(phi)<N`.
2. Verify that `x after phi` has only the Kummer sign ambiguity on `G`.
3. Distinguish the auxiliary ECFFT subgroup from the target prime subgroup.
4. Confirm that ECFFT's two-to-one guarantee is restricted to its evaluation
   sets and supplies no target-addition intertwiner.
5. Recompute the canonical-map transformed trace and verify its failure under
   `X -> d/X` on the stated exact specialization.
6. Recompute `B^2*sqrt(N)/N=N^(-1/10)` at `B=N^(1/5)`.
7. Confirm that the occupancy statement is explicitly model-bound.
8. Preserve a list-specific support-changing `ECFFT/S3` factorization as open.

## Exactly one next action

Independently review this receipt together with P1523-P1525 and either preserve
the scoped ECFFT removal or freeze one explicit resultant factorization through
an auxiliary `psi` on the admitted recursive-`S3` supports, with exact source
inverse and complete `B^2.25/B^1.25` plus rank/descent accounting. Do not build
an FFT tree or run a bucket campaign without that identity.

## Primary references

- Ben-Sasson, Carmon, Kopparty, and Levit, *Elliptic Curve Fast Fourier
  Transform (ECFFT) Part I: Fast Polynomial Algorithms over all Finite Fields*:
  <https://arxiv.org/abs/2107.08473>.
- Semaev, *Summation polynomials and the discrete logarithm problem*:
  <https://eprint.iacr.org/2004/031>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.

The first reference supplies the auxiliary isogeny-tree and fast polynomial
arithmetic primitive. It does not claim an ECDLP source router. The second
supplies the target addition relation, and the third supplies the generic
square-root comparison boundary.
