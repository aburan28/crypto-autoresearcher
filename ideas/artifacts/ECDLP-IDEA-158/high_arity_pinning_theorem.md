# IDEA-158 high-arity-only Kummer pinning gate

Status:
`SCOPED_NEGATIVE_FULL_AFFINE_SM_FOR_M_GE_5_PP_DEFINES_S3__AFFINE_S4_OR_RESTRICTED_LANGUAGE_OPEN`

This is a theorem-only producer receipt. No contract, CSP solver, finite-field
search, toy curve, relation campaign, or timing run was executed. It tightens
the exception left by `nonfaithful_signature_theorem.md`: merely deleting
`S3` while retaining one full affine `S_m` relation for fixed `m>=5` does not
avoid the faithful-addition/WNU obstruction.

The result is stated on the rational-point Kummer relation. Polynomial charts,
point membership, tangencies, repeated points, extension-field roots, and the
point at infinity still require the usual exact verifier. The theorem uses no
infinity constant.

## Affine Kummer relations

Let

```text
G = Z/NZ,  K_star = (G minus {0})/{+1,-1},
```

where `N` is prime. Write `[x]` for the sign orbit of nonzero `x`. For fixed
`m>=3`, define the full affine Kummer relation

```text
R_m([x1],...,[xm])
  iff there exist ei in {+1,-1} with sum_i ei*xi=0 in G.
```

This is the rational prime-subgroup restriction represented by the affine
Semaev equation `S_m=0` after exact point and chart filtering.

Let `F_x subset K_star` be a proper factor base and

```text
F_tilde = {t in G minus {0}: [t] in F_x}.
```

Assume `N>32m+3`. This is harmless for fixed arity at cryptographic group
sizes and ensures that every small integer coefficient below is nonzero and
that enough distinct public sign orbits exist.

## Lemma 1: a full affine R_m with m>=5 pp-defines affine R_3

Put `k=m-3` and choose

```text
M = 16k+1
```

pairwise distinct nonzero public sign orbits `[z_1],...,[z_M]`.

### Odd m

If `m` is odd, then `k` is even. Define

```text
P_z(a,b,c) = R_m(a,b,c,[z],...,[z]),
```

with `k` copies of `[z]`. The signed padding sums are

```text
C_k*z,  C_k={-k,-k+2,...,k},
```

and `0 in C_k`.

### Even m at least six

If `m` is even, then `k` is odd and `k>=3`. Define

```text
P_z(a,b,c)
  = R_m(a,b,c,
        [z],...,[z],[(k-1)z]),
```

with `k-1` copies of `[z]` followed by `[(k-1)z]`. Its signed padding
coefficients lie in

```text
C'_k={s+e*(k-1): s in C_(k-1), e in {+1,-1}},
```

which contains zero and has at most `2k` elements.

In both cases,

```text
R_3(a,b,c) iff conjunction_(j=1)^M P_(z_j)(a,b,c).
```

Proof. Choose lifts `alpha,beta,gamma` and let

```text
L={e1*alpha+e2*beta+e3*gamma: ei in {+1,-1}}.
```

If `0 in L`, choose a zero signed padding sum. Every `P_(z_j)` holds.

Suppose `0 notin L`. If `P_z` holds, then

```text
l+c*z=0
```

for some `l in L` and some nonzero padding coefficient `c`. The coefficient
cannot be zero because `l` is nonzero. For odd `m` there are at most `k`
nonzero padding coefficients, so at most `8k` possible values of `[z]`. For
even `m` there are at most `2k` coefficients, so at most `16k` possible
values. A non-`R_3` triple therefore cannot satisfy the conjunction at
`16k+1` distinct sign orbits. This proves the equivalence.

The formula is primitive-positive: it is a finite conjunction of `R_m` atoms
with public nonzero constants. It uses neither disjunction nor the point at
infinity.

## Lemma 2: the missing affine chart does not rescue a WNU

Fix a nonzero public `g` and put

```text
U = G minus {0,-g,-2g,-3g}.
Enc(t)=([t],[t+g],[t+2g],[t+3g]) for t in U.
```

Using the affine `R_3` relation from Lemma 1, the six distance atoms

```text
R_3(ai,[(j-i)g],aj) for 0<=i<j<=3
```

define exactly `Enc(U)`. The seven cross atoms in
`nonfaithful_signature_theorem.md` define the partial addition graph

```text
Add_U={(alpha,beta,gamma) in U^3: alpha+beta=gamma}.
```

Thus an idempotent `r`-ary WNU preserving `R_m` and the public constants
induces

```text
W:U^r-->U
```

that preserves every coordinatewise addition triple whose inputs and output
remain in `U`.

This partial homomorphism extends uniquely to a homomorphism

```text
W_bar:G^r-->G.
```

To see this, for `x in G^r` choose `a,b in U^r` with `a+b=x` and define

```text
W_bar(x)=W(a)+W(b).
```

Such a decomposition exists coordinatewise by avoiding at most eight values.
For two decompositions `x=a+b=c+d`, choose `h` coordinatewise so that

```text
h, b+h, d+h, x+h are all in U^r.
```

At most sixteen values are forbidden in each coordinate. Partial additivity
then gives

```text
W(a)+W(b)+W(h)=W(x+h)=W(c)+W(d)+W(h),
```

so the definition is independent of the decomposition. Decompositions of
`x`, `y`, and `x+y` can likewise be chosen so that their two componentwise
sums remain in `U^r`, again by avoiding at most sixteen values per coordinate.
This proves additivity. On `U^r`, `W_bar` agrees with `W`.

## Theorem: full affine S_m for m>=5 has no sparse-base WNU

Every homomorphism `W_bar:G^r-->G` has the form

```text
W_bar(x1,...,xr)=sum_i ai*xi.
```

Idempotence on `U` gives `sum_i ai=1`. The WNU identities on two distinct
elements of `U` make all `ai` equal. If `N` divides `r`, no such coefficients
exist. Otherwise

```text
W_bar(x1,...,xr)=r^(-1)*(x1+...+xr).
```

The primitive-positive unary relation

```text
Enc(t) and F_x([t])
```

represents

```text
A=F_tilde intersection U.
```

For an asymptotic sparse factor base, `1<|A|<N`; removing four values does not
change its exponent. Preservation would require `W_bar(A^r) subset A`, but
iterated Cauchy-Davenport gives

```text
|r*A| >= min(N,r*|A|-r+1) > |A|.
```

Multiplication by `r^(-1)` is bijective, a contradiction. Therefore no
idempotent WNU of any arity at least three preserves the full affine `R_m`,
the required public constants, and a proper asymptotic x-factor base for any
fixed `m>=5`.

## Scope and surviving operation

This closes all of the following proposed escapes:

1. exposing affine `S_5` directly instead of recursively evaluating it with
   `S3`;
2. exposing any one full affine `S_m` for fixed `m>=6`;
3. omitting the infinity constant while retaining the full signed Kummer
   relation; and
4. changing only the bounded-width or CSP solver.

It does not close:

1. the full affine four-ary relation `R_4`, because one nonzero padding point
   cannot have zero signed sum;
2. a proper subrelation, promise relation, or projection of `R_m` that removes
   enough sign branches to invalidate the pinning formula;
3. a non-WNU operation; or
4. any candidate lacking exact all-source lifting and complete cost analysis.

The next admissible theorem target is therefore the strict affine `R_4`
signature. It must either primitive-positive interpret the four-window
addition gadget, or exhibit a non-affine sparse-base WNU and a source-
biconditional lift with complete relation, rank, factor-log, and blind-descent
cost below rho.

No relation campaign, factor-log recovery, blind descent, generic-prime
below-rho algorithm, Shoup-bound improvement, or breakthrough is established.

## Independent review checklist

1. Check the padding coefficient sets and the `16k` root bound.
2. Check that every pinned constant is nonzero and target independent.
3. Check the affine four-window domain and seven-atom partial addition gadget.
4. Check the local-to-global homomorphism extension over the four missing
   scalar values.
5. Check WNU coefficient equality and the factor-base unary interpretation.
6. Check the all-arity Cauchy-Davenport contradiction.
7. Preserve `R_4` and proper restricted languages as explicit open cases.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem*:
  <https://eprint.iacr.org/2004/031>
- Chalcraft and Fryers, *Kummer structures*:
  <https://arxiv.org/abs/0806.0409>
- Cauchy-Davenport background via Green and Ruzsa,
  *Freiman's theorem in an arbitrary abelian group*:
  <https://arxiv.org/abs/math/0505198>
