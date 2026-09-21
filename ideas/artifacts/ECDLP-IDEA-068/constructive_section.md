# IDEA-068 Source-Coded Hasse-Jet Constructive Section

## Scope

This artifact specializes IDEA-068's missing constructive section to the exact
P1490/P1491 factored-finite-field-elimination (FFE) transition algebra. It asks
whether source markers can be propagated through a resultant before opening
each endpoint with an independent gcd.

The result below is a derivation and a frozen P1509 preflight target. It is not
yet a construction-cost theorem, relation campaign, target descent, or
better-than-rho algorithm.

## Accepted Transition Object

Let the rational selector roots be `x_0,...,x_(r-1)` and write

```text
f_i(u,v) = S3(u,v,x_i),
N(u,v)   = product_i f_i(u,v).
```

P1490 independently verified that `N(u,v)=0` exactly recognizes a one-step
transition through a selector root, including exact endpoint and sign replay.
For fixed public start x-coordinate `u` and endpoint coordinate `w`, define

```text
A(V) = N(u,V),
B(V) = N(V,w).
```

P1491 verifies the endpoint predicate by `Res_V(A,B)=0` and opens a source from
`gcd(A,B)`, but repeating that opening for every endpoint costs
`r(2r^2+1)=Theta(r^3)`.

## Linear Source Markers

Choose distinct public field elements `alpha_i`. Use two source-code
coordinates per transition,

```text
c_0(i)=1,  c_1(i)=alpha_i.
```

For the left transition define the cofactor markers

```text
A_k(V) = sum_i c_k(i) product_(ell != i) f_ell(u,V),  k in {0,1},
```

and analogously define `B_0,B_1` from the factors `f_j(V,w)`. The marked
polynomials are

```text
A_E = A + E_0 A_0 + E_1 A_1,
B_H = B + H_0 B_0 + H_1 B_1.
```

These are the first Hasse jets of
`product_i(f_i+E_0+E_1*alpha_i)`. A balanced product/cofactor tree can build
each marker polynomial without a source-tuple table. The P1509 gate must
measure rather than assume the total construction cost.

## Leading-Resultant Lemma

Let `A,B in K[V]` have squarefree gcd `g` of degree `t`, and assume every root
of `g` is simple in `A` and `B`. For perturbations `delta A` and `delta B`, the
first nonzero homogeneous Hasse form of

```text
Res_V(A+delta A, B+delta B)
```

has total marker degree `t`. Up to a nonzero public scalar, it is

```text
product_(rho:g(rho)=0)
  (A'(rho) delta B(rho) - B'(rho) delta A(rho)).
```

Proof: continue each simple root of `A` as
`rho-delta A(rho)/A'(rho)+O(delta^2)`, evaluate the perturbed `B` there, and
multiply the `t` vanishing local factors. Every noncommon root contributes a
nonzero constant. The formula is also independently checkable through the
Poisson product formula for the resultant.

Suppose exactly one left factor `f_i(u,V)` and one right factor `f_j(V,w)`
vanish at a common root `rho`. Then

```text
A_k(rho) = c_k(i) A'(rho) / partial_V f_i(u,rho),
B_k(rho) = c_k(j) B'(rho) / partial_V f_j(rho,w).
```

After discarding a nonzero local scalar, the corresponding linear factor of
the leading Hasse form is

```text
-s_i(rho) (E_0 + alpha_i E_1)
+t_j(rho) (H_0 + alpha_j H_1),
```

where `s_i(rho),t_j(rho)` are nonzero public derivative scalars. Factoring the
leading form and taking the within-block coefficient ratios

```text
coeff(E_1)/coeff(E_0) = alpha_i,
coeff(H_1)/coeff(H_0) = alpha_j
```

recovers both selector-factor indices independently of the unknown local
scales. Elliptic sign branches are then enumerated and replayed exactly, as in
P1490/P1491. No hidden scalar label enters the code.

## Frozen Multiplicity Census

An exact Sage census rebuilt all P1490 selectors, both public nonces, every
squarefree endpoint root, every pointwise gcd, and every vanishing S3 factor.
The nonreturn histograms are identical for both nonces:

| L | r | gcd degree 1 | gcd degree 2 | known return gcd degree |
|---:|---:|---:|---:|---:|
| 4 | 4 | 8 | 24 | 8 |
| 8 | 4 | 8 | 24 | 8 |
| 16 | 7 | 14 | 84 | 14 |
| 32 | 12 | 24 | 264 | 24 |

Thus every nonreturn endpoint has `t in {1,2}`. The counts are exactly

```text
degree-1 endpoints = 2r,
degree-2 endpoints = 2r(r-1),
nonreturn total     = 2r^2.
```

The only growing-degree endpoint is the public return branch, with gcd degree
`2r`; it is already isolated and removed in P1490's nonreturn object. At every
common root in every cell, exactly one selector factor vanishes on the left
and exactly one vanishes on the right. Therefore the proposed nonreturn
decoder needs only the linear and quadratic Hasse forms and two code
coordinates per transition on this frozen family.

## P1509 Exact Preflight

The first executable gate must not use the explicit source table as algorithmic
advice. It must:

1. rebuild `A,B,A_0,A_1,B_0,B_1` from the public selector factors;
2. compute the degree-one and degree-two leading Hasse resultant forms for
   every nonreturn endpoint;
3. factor each form over the base field and decode all `(i,j)` factor pairs;
4. enumerate constant-size sign branches and reproduce every canonical P1505
   source tag, including repeated indices;
5. compare against explicit sources only after decoding;
6. retain the return endpoint as a growing-order negative control;
7. count coefficient state and field operations for a batched marked-eliminant
   construction, per-endpoint local replay, and the P1491 all-key baseline;
8. include random-factor, planted-linear, planted-quadratic, marker-mutation,
   multiplicity-mutation, and sign-mutation controls.

The positive gate is exact source recovery with a constant number of marked
coefficient polynomials of degree `O(r^2)`, total source output `Theta(r^2)`,
and no per-endpoint degree-`r` gcd. The negative gate fires if global marked
resultant construction costs `Omega(r^3)`, if quadratic form factorization does
not preserve rootwise pairings, or if complete sign/source replay needs an
`Omega(r)` branch or code list.

## Algorithmic Boundary

Even a positive P1509 source reporter would remove only P1505's all-key opening
floor. A full ECDLP claim must still supply candidate generation, at least
`B+sigma` independent rows, factor-log linear algebra, blind target descent,
verification, and peak memory below rho and BSGS. In particular, materializing
the complete A3 source state remains disallowed.
