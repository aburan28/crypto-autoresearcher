# IDEA-057 ECFFT/Lattes rational-kernel cofactor gate

Status:
`SCOPED_NEGATIVE_TARGET_ISOGENY_INTERTWINER_HAS_SUBPOLYNOMIAL_RATIONAL_KERNEL_AND_DUPLICATE_LOG_COLUMNS__EXTENSION_AND_NONGROUP_SUPPORT_OPEN`

This is a theorem-only producer receipt. No contract, isogeny chain, curve
fixture, finite-field sample, preimage tree, relation search, factor-log solve,
toy scalar recovery, or timing run was executed. It consumes the strongest
global-intertwiner exception left by P1526-P1527.

Unlike an unrelated auxiliary ECFFT map, a rational map induced by an isogeny
on the target isogeny class really does transport Kummer addition. The question
is whether its smooth kernel or rational preimage multiplicity can provide a
polynomial number of source representations and thereby support a Wagner-style
or implicit-batch gain.

For a prime subgroup of size `N=p^(1+o(1))`, Hasse and the cofactor answer this
question negatively. A rational kernel on the target isogeny class is contained
in the small cofactor, and all of its preimages collapse to the same factor-log
column. This is a quantitative same-field representation gate, not a new claim
that all Lattes maps or extension-field transfers are impossible.

## Frozen target family

Let `E/F_p` contain the public prime-order subgroup

```text
G=<P>,
|G|=N,
N=p^(1+o(1)).
```

Write

```text
#E(F_p) = M = h*N.
```

Thus the cofactor satisfies

```text
h = p^o(1).
```

The cofactor-one and constant-cofactor cryptographic families are the strictest
special cases. The theorem permits any subpolynomial `h`; it does not assume
`h=1`.

Consider an `F_p`-rational separable isogeny chain

```text
Phi:E_0 -> E_k
```

inside the target isogeny class. Let its total degree be `K`, with the ECFFT
case using a smooth power of two. Every curve in the chain is `F_p`-isogenous,
so every curve has the same Frobenius trace and the same number `M` of rational
points.

The target DLP may be transported to the order-`N` subgroup

```text
G_k=Phi(G_0) subset E_k(F_p)
```

only if `Phi` does not kill `G_0`.

## Theorem 1: the rational kernel is contained in the cofactor

Let

```text
H_rat = ker(Phi) intersection E_0(F_p),
K_rat = |H_rat|.
```

Then `H_rat` is a rational subgroup of `E_0(F_p)`, so

```text
K_rat divides M=h*N.
```

If `Phi` preserves the target prime subgroup, its restriction to `G_0` is
injective. Hence

```text
H_rat intersection G_0 = {O},
gcd(K_rat,N)=1.
```

Because `N` is prime, it follows that

```text
K_rat divides h,
K_rat <= h = p^o(1) = N^o(1).
```

For a cofactor-one target there is no nontrivial rational kernel. For a
constant-cofactor target every rational kernel and every rational isogeny-chain
fiber has constant size.

The conclusion also covers a geometrically larger kernel that is not fully
rational. If one rational preimage of `R in E_k(F_p)` exists, all rational
preimages form a torsor under `H_rat`, so their number is exactly `K_rat`; if no
rational preimage exists, the number is zero. Nonrational geometric preimages
live over extension fields and are not factor points with logs in `G_0`.

## Corollary: an ECFFT-size target kernel contradicts Hasse/cofactor

ECFFT obtains a tree of size `K` from a smooth rational subgroup on a deliberately
chosen auxiliary curve. If the same curve also carried the target subgroup of
order `N=p^(1+o(1))`, then

```text
K*N divides #E_0(F_p) <= p+1+2*sqrt(p).
```

Therefore

```text
K <= (p+1+2*sqrt(p))/N = p^o(1).
```

In particular no fixed positive exponent `kappa` can satisfy

```text
K >= N^kappa
```

on the frozen family. The polynomial-size ECFFT tree must be built on an
auxiliary curve that does not simultaneously carry the near-`p` target subgroup.
That returns to P1526's missing target-addition intertwiner.

This explains why ECFFT's generic-field existence theorem and the target ECDLP
requirements do not conflict: they choose different elliptic curves for
different purposes.

## Theorem 2: rational preimages duplicate factor-log columns

Suppose `R,R+T in E_0(F_p)` differ by `T in H_rat`. Then

```text
Phi(R+T) = Phi(R).
```

After transporting a relation to `E_k`, both preimages represent the same
factor point and the same unknown logarithm in the order-`N` subgroup. Replacing
one by the other changes a lift label but not the factor-log coefficient column.

For an `m`-source relation, a fiber of size `K_rat` can create at most
`K_rat^m` lifted representations of the same image-source tuple. Since `m` is
fixed and

```text
K_rat^m = N^o(1),
```

this multiplicity changes only subpolynomial factors. It cannot remove a fixed
exponent gap such as P1515's `B^3` explicit separator versus `B^2.25` setup cap.

Moreover, counting the lifted representations as independent rows is invalid:
after image-column aggregation they are duplicate coefficient rows or differ
only by kernel labels whose logarithms are absent from the target order-`N`
system. Exact source replay may retain the labels for verification, but sparse
linear algebra receives no new factor-log rank from them.

This is distinct from the IDEA-113 arboreal branch-state gate. IDEA-113 charges
the state needed to orient a deep inverse tree. The theorem here acts earlier:
on the same-field near-prime-order family, the rational branching factor itself
is only `N^o(1)`, and its branches collapse to duplicate target-log columns.

## Degree divisible by the target prime

The ECFFT smooth-kernel case has `gcd(K,N)=1`, but the remaining algebraic
possibility should be explicit. If an isogeny kernel contains the rational
subgroup `G_0`, then the map kills both `P` and the target `Q=[x]P`; it cannot
transport the DLP. If the geometric degree is divisible by `N` but the rational
kernel does not contain `G_0`, then Theorem 1 still bounds rational preimage
multiplicity by `h`. A large nonrational kernel is extension-field data, not a
same-field factor-base representation.

## Scoped decision

The following exact-intertwiner routes are removed:

1. put a polynomial-size smooth rational ECFFT kernel on a same-field curve that
   also carries the near-`p` prime target subgroup;
2. credit rational isogeny preimages as `N^kappa` representations for any fixed
   `kappa>0`;
3. count kernel-lift variants as independent factor-log rows; and
4. use a chain of same-field low-degree isogenies to obtain an exponent-changing
   Wagner quotient while preserving the target DLP.

The following mechanisms remain outside scope:

1. an unrelated auxiliary curve equipped with a new explicit non-group
   `S3` intertwiner;
2. extension-field kernels with a proved, fully charged descent to exact
   `F_p` target-subgroup sources;
3. a non-Cartesian list-specific support law that is not rational-kernel
   multiplicity; and
4. a nonlinear implicit-batch or multirow operation that does not rely on
   isogeny preimages for its rank gain.

Every successor must prove exact all-strata source inversion, independent
relation rank after column aggregation, factor-log calibration, masked target
descent, and complete time and memory exponents below `1/2`. An isogeny
identity, smooth auxiliary kernel, many geometric preimages, relation, or toy
scalar is not a breakthrough.

No relation campaign, factor-log solve, blind descent, generic-prime below-rho
algorithm, Shoup-bound improvement, or ECDLP breakthrough is established.

## Independent review checklist

1. Verify that all `F_p`-isogenous curves have the same rational point count.
2. Verify `K_rat|h` when the target prime subgroup is preserved.
3. Verify that rational preimages form a torsor under `H_rat`.
4. Recompute the Hasse/cofactor bound `K=N^o(1)`.
5. Confirm that kernel-coset lifts map to the same factor-log column.
6. Distinguish this rational-branch bound from IDEA-113's deep arboreal state
   argument.
7. Preserve extension-field, non-group, non-Cartesian, and nonlinear multirow
   exceptions.

## Exactly one next action

Independently review P1526-P1528 and either preserve the same-field ECFFT/Lattes
removal or freeze one explicit extension-field or unrelated-auxiliary
intertwiner whose rational target-source yield, column rank, setup/query,
factor-log, and blind-descent costs meet the P1515 gates. Do not credit geometric
or kernel-coset multiplicity before image-column aggregation.

## Primary references

- Ben-Sasson, Carmon, Kopparty, and Levit, *Elliptic Curve Fast Fourier
  Transform (ECFFT) Part I: Fast Polynomial Algorithms over all Finite Fields*:
  <https://arxiv.org/abs/2107.08473>.
- Milnor, *On Lattes Maps*:
  <https://arxiv.org/abs/math/0402147>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.

The first reference supplies the auxiliary smooth-isogeny tree, the second the
target-isogeny/Lattes setting, and the third the generic square-root comparison
boundary. None supplies polynomial rational preimage multiplicity on a
near-prime-order target curve or a below-rho ECDLP algorithm.
