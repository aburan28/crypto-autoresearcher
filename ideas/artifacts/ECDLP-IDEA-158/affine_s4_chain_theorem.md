# IDEA-158 strict affine S4 chain gate

Status:
`SCOPED_NEGATIVE_FULL_AFFINE_S4_PP_DEFINES_S3__RESTRICTED_LANGUAGE_OR_NON_WNU_OPEN`

This is a theorem-only producer receipt. No contract, CSP solver, finite-field
search, toy curve, relation campaign, or timing run was executed. It closes the
strict affine four-ary exception preserved by `high_arity_pinning_theorem.md`.

Together, the IDEA-158 theorem chain covers the full rational-point Kummer
relations `S_m` for every fixed `m>=3`. It does not cover a proper promise
subrelation, a projection that deletes sign branches, or a non-WNU operation.

## Frozen affine relation

Let

```text
G=Z/NZ,  K_star=(G minus {0})/{+1,-1},
```

where `N` is prime and `N>=67`. For nonzero lifts, define

```text
R_4([x1],[x2],[x3],[x4])
  iff there exist ei in {+1,-1} with sum_i ei*xi=0.
```

This is the exact rational prime-subgroup Kummer relation represented by
affine `S4=0` after point, chart, and subgroup filtering.

## Lemma 1: a two-atom R4 chain gives a six-term signed relation

For a nonzero public `z`, define

```text
Q_z(a,b,c) iff there exists u in K_star such that
  R_4(a,b,[z],u) and R_4(u,c,[z],[2z]).
```

Eliminating a lift of `u` shows that `Q_z(a,b,c)` holds exactly when there is
a signed relation

```text
e1*alpha+e2*beta+e3*gamma+d1*z+d2*z+d3*2z=0
```

whose first partial sum

```text
e1*alpha+e2*beta+d1*z
```

is nonzero. The common sign introduced by the shared `u` does not restrict
the three source signs or the three padding signs.

## Lemma 2: thirty-three nonzero pins pp-define affine R3

Choose 33 pairwise distinct nonzero public sign orbits

```text
[z_1],...,[z_33].
```

Then

```text
R_3(a,b,c) iff conjunction_(j=1)^33 Q_(z_j)(a,b,c).
```

Proof. Suppose a signed ternary sum is zero:

```text
A+B+C=0.
```

Use padding signs `z+z-2z=0`. The first partial sum is `-C+z`.
If this vanishes, flip only the three source signs; the first partial becomes
`C+z`, which cannot also vanish in odd characteristic. Thus the intermediate
`u` can always be chosen nonzero and every `Q_z` holds without using the
point at infinity.

Conversely, let

```text
L={e1*alpha+e2*beta+e3*gamma: ei in {+1,-1}}
```

and suppose `0 notin L`. Every `Q_z` implies

```text
l+c*z=0
```

for some `l in L` and

```text
c in {-4,-2,2,4}.
```

There are at most `8*4=32` possible values, hence at most 32 possible sign
orbits, for `[z]`. A non-`R_3` triple cannot satisfy `Q_z` at 33 distinct
public pins. The displayed conjunction is therefore a primitive-positive
definition of affine `R_3` from full affine `R_4` using only nonzero constants
and one existential nonzero Kummer state per atom pair.

## Theorem: full affine S4 has no sparse-base WNU

The affine `R_3` relation obtained above supplies the six distance atoms and
seven cross atoms from `nonfaithful_signature_theorem.md`. On

```text
U=G minus {0,-g,-2g,-3g},
```

they primitive-positive define the four-window oriented domain and its partial
addition graph.

The local-extension lemma in `high_arity_pinning_theorem.md` then applies
unchanged. Any idempotent `r`-ary WNU preserving full affine `R_4`, the public
pins, adjacent constants, and an asymptotic proper x-factor base induces a
partial additive operation on `U^r`, which extends to

```text
W_bar(x1,...,xr)=sum_i ai*xi on G^r.
```

WNU and idempotence make all coefficients equal with sum one. If `N` divides
`r`, this is impossible; otherwise `W_bar` is modular averaging. The oriented
factor-base subset loses at most four values on `U`, and iterated
Cauchy-Davenport forbids its preservation.

Therefore no idempotent WNU of any arity at least three preserves full affine
`S4`, the required target-independent public constants, and a proper
asymptotic x-factor base.

## Combined disposition

The three IDEA-158 receipts now close:

1. full projective or affine ternary Kummer `S3`;
2. every full affine `S_m` for fixed `m>=5`; and
3. strict full affine `S4`, even though the intermediate point at infinity is
   unavailable.

The surviving mechanism must change the operation, not just arity or solver:

1. specify a proper promise subrelation or projection that removes enough sign
   branches to invalidate the pinning gadgets;
2. prove a non-affine WNU on that exact target-uniform signature and sparse
   factor base;
3. recover every exact signed source and multiplicity without reintroducing
   the full relation or a source dictionary; and
4. charge relation collection, rank, factor logs, blind target descent,
   verification, output, time, and bit memory below rho.

A non-WNU operation remains outside this theorem chain. No relation campaign,
factor-log recovery, blind descent, generic-prime below-rho algorithm,
Shoup-bound improvement, or breakthrough is established.

## Independent review checklist

1. Verify elimination of the shared nonzero Kummer state in the two-atom chain.
2. Verify that a true ternary relation always has a nonzero intermediate.
3. Verify the four nonzero padding coefficients and the 32-root bound.
4. Verify the reuse of the affine local-extension theorem.
5. Preserve restricted relation languages and non-WNU operations as open.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem*:
  <https://eprint.iacr.org/2004/031>
- Chalcraft and Fryers, *Kummer structures*:
  <https://arxiv.org/abs/0806.0409>
- Cauchy-Davenport background via Green and Ruzsa,
  *Freiman's theorem in an arbitrary abelian group*:
  <https://arxiv.org/abs/math/0505198>
