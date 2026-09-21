# IDEA-057 ECFFT list-restricted branch-locus gate

Status:
`SCOPED_NEGATIVE_CANONICAL_TWO_ISOGENY_LIST_SUPPORT_HAS_ONLY_DECK_FIXED_COMPONENT__OTHER_MAPS_AND_TARGETS_OPEN`

This is a theorem-only producer receipt. No contract, finite-field sample,
factor-base construction, ECFFT tree, relation search, toy scalar recovery, or
timing run was executed. It consumes the first list-specific exception left by
`ecfft_auxiliary_isogeny_router_gate.md`: perhaps the canonical degree-two
auxiliary map fails globally but becomes an exact Kummer branch transporter on
a deliberately restricted factor-base pair support.

The answer is negative for one frozen symbolic target and the complete
canonical one-parameter map family. The simultaneous transformed trace and norm
invariance locus has only the deck-fixed positive-dimensional component. After
that component is removed, the compatible nonfixed pair set is bounded by an
absolute constant over the algebraic closure. This is not a classification of
all target curves, rational maps, higher isogenies, or non-Cartesian recursive
supports.

## Frozen target and auxiliary map

Work over characteristic different from `2` and `3` with the nonsingular target

```text
E: y^2 = x^3 + 1.
```

Freeze the canonical degree-two map

```text
psi_c(Z) = Z + c + 1/Z,
```

over the coefficient field `Q(c)` before reduction to admissible finite fields.
Its deck involution is

```text
iota(Z) = 1/Z.
```

Let `z_1,z_2` be the two roots of `S3_E(X,Y,Z)`. Their trace and norm are

```text
tau(X,Y) = z_1+z_2,
nu(X,Y)  = z_1*z_2.
```

For the frozen target these are obtained from the standard exact formulas

```text
tau(X,Y) = 2*((X+Y)*X*Y+2)/(X-Y)^2,
nu(X,Y)  = ((X*Y)^2-4*(X+Y))/(X-Y)^2.
```

## Necessary branch-transport equations

The unordered branch image under `psi_c` is determined by its transformed
trace and norm

```text
T_c(X,Y)
  = psi_c(z_1)+psi_c(z_2)
  = tau + 2*c + tau/nu,

N_c(X,Y)
  = psi_c(z_1)*psi_c(z_2)
  = nu + c*tau + c^2
    + (tau^2-2*nu)/nu + c*tau/nu + 1/nu.
```

If the branch polynomial factors through `psi_c(X)` in the first source input
on a support containing both members of a nonfixed deck pair, then necessarily

```text
T_c(X,Y) = T_c(1/X,Y),
N_c(X,Y) = N_c(1/X,Y).
```

Equality of only the first expression is insufficient: it preserves an
aggregate trace while permitting the two output branches to change. Exact
branch transport requires both coefficients.

Let `D_T(X,Y;c)` and `D_N(X,Y;c)` be the reduced-fraction numerators of the two
differences above. Denominator poles correspond to excluded affine charts and
cannot create valid compatible pairs.

## Theorem 1: the only common curve component is deck-fixed

Exact polynomial gcd over `Q(c)[X,Y]` gives

```text
gcd(D_T,D_N) = X^2-1.
```

The factors `X=1` and `X=-1` are precisely the fixed points of `iota`. They do
not represent two distinct source x-coordinates and therefore provide no
two-to-one ECFFT compression.

Write

```text
A_c = D_T/(X^2-1),
C_c = D_N/(X^2-1).
```

The gcd statement means `A_c` and `C_c` have no common positive-dimensional
component for generic `c`. Thus no curve-sized family of nonfixed source pairs
can make the complete Kummer branch polynomial descend through `psi_c` on this
target.

The conclusion is stronger than the trace-only check in P1526. That check
showed the global identity is false. The simultaneous coefficient gcd shows
that restricting to its exact compatibility locus does not recover an
asymptotically growing nonfixed branch-support component.

## Theorem 2: the nonfixed residue is absolutely bounded at `c=0`

At `c=0`, both residual polynomials `A_0,C_0` have bidegree `(6,7)` in `(X,Y)`.
Their resultant in `X` is the following nonzero degree-84 polynomial in `Y`:

```text
Res_X(A_0,C_0)
 = 6718464
   * Y^10
   * (Y-1)^2 * (Y+1)^6 * (Y+4)^2
   * (Y^3+4)^4
   * (Y^2-Y+1)^2
   * (Y^2+2*Y-2)^2
   * (4*Y^2-Y+4)^4
   * (Y^4-2*Y^3+6*Y^2+4*Y+4)^2
   * (Y^4+4*Y^3-9*Y^2+Y-5)^2
   * (2*Y^5+Y^4-16*Y^3-16*Y^2-44*Y-16)^2
   * (2*Y^5+19*Y^4-16*Y^3-16*Y^2+28*Y-16)^2.
```

The polynomial contents of `A_0` and `C_0` in `Y` are coprime. The nonzero
resultant certifies that the residual equations share no curve component.
Equivalently, their projective intersection number is at most

```text
6*7 + 7*6 = 84
```

counted with multiplicity. Removing denominator poles can only reduce the valid
affine set. Therefore there are at most 84 nonfixed compatible ordered pairs
over the algebraic closure for this frozen target/map.

This is an algebraic degree bound, not an extrapolation from finite samples.

## Consequence for a restricted factor base

Let `F_x` be any size-`B` source x-set. To obtain genuine two-to-one compression
from `psi_c`, the admitted pair support must contain both `X` and `1/X` for an
asymptotically growing family of nonfixed inputs and transport the same complete
output branch polynomial for each representative.

For generic `c`, the only positive-dimensional simultaneous-invariance support
has `X=+-1`, where the two representatives coincide. At `c=0`, all nonfixed
compatible pairs number at most 84, independent of `B`. Hence this canonical
map cannot supply `Theta(B)` or more nonfixed compressed first-level merges on
the frozen target.

Keeping only one representative from each deck pair evades the invariance
condition but makes `psi_c` injective on the admitted source set, eliminating
the proposed quotient gain. Keeping the deck-fixed points as constant anchors
also gives no two-to-one source compression and is not a relation-collection or
descent theorem.

## Scope boundary

This receipt closes only:

1. the target `y^2=x^3+1`;
2. the canonical family `psi_c(x)=x+c+1/x`;
3. exact transport of the complete two-branch Kummer polynomial;
4. Cartesian source-pair restriction whose compression uses both members of a
   deck pair; and
5. generic `c`, with the explicit constant residue bound frozen at `c=0`.

It does not close:

1. another target curve or an exceptional parameter specialization;
2. a different degree-two map, higher isogeny, or non-isogeny rational map;
3. a non-Cartesian recursive support whose later constraints create a new
   component not visible in this pair gate;
4. an approximate correction with a proved support-law change; or
5. a nonlinear implicit-batch/multirow source generator outside pairwise branch
   transport.

Every successor must still be generic across the claimed prime-field curve
family, exact on rational signed points and exceptional strata, and satisfy the
P1515 setup `B^2.25`, query `B^1.25`, relation-rank, factor-log, masked-descent,
output, and memory gates. A branch identity, bounded compatible locus, valid
relation, or toy scalar is not a breakthrough.

No relation campaign, factor-log solve, blind descent, generic-prime below-rho
algorithm, Shoup-bound improvement, or ECDLP breakthrough is established.

## Independent review checklist

1. Re-derive `T_c` and `N_c` from the two Kummer roots.
2. Confirm that exact branch descent requires both trace and norm invariance.
3. Verify `gcd(D_T,D_N)=X^2-1` over `Q(c)[X,Y]`.
4. Confirm that `X=+-1` is deck-fixed and supplies no two-to-one compression.
5. At `c=0`, verify the residual bidegrees, polynomial contents, and nonzero
   degree-84 resultant.
6. Confirm that the bound concerns algebraic pairs, not sampled finite-field
   points.
7. Preserve other maps, targets, exceptional parameters, and non-Cartesian
   recursive supports as open.

## Exactly one next action

Independently review P1526-P1527 and either preserve this canonical-map scoped
removal or freeze one different rational map/target family with a positive-
dimensional nonfixed simultaneous trace/norm invariance component, exact signed
source inverse, and complete P1515 plus rank/descent costs. Do not build an
ECFFT tree from a trace-only or deck-fixed component.

## Primary references

- Ben-Sasson, Carmon, Kopparty, and Levit, *Elliptic Curve Fast Fourier
  Transform (ECFFT) Part I: Fast Polynomial Algorithms over all Finite Fields*:
  <https://arxiv.org/abs/2107.08473>.
- Semaev, *Summation polynomials and the discrete logarithm problem*:
  <https://eprint.iacr.org/2004/031>.
- Chalcraft and Fryers, *Kummer structures*:
  <https://arxiv.org/abs/0806.0409>.

These references supply the auxiliary isogeny-tree, summation-polynomial, and
two-branch Kummer settings. None claims the restricted-support intertwiner or a
below-rho prime-field ECDLP algorithm.
