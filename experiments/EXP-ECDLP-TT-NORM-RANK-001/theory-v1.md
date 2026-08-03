# First-norm Hilbert bound and fixed-source construction v1

## Handoff: degree-preserving norm compiler

### Claim or task

Determine exactly what the first quadratic norm step contributes to a
five-source RCB equality tensor, prove its finite-registry TT rank bounds, and
separate a constructive fixed-curve specialization route from the unresolved
Fermat-powering and witness-localization problems.

### Status

- `RESTRICTED THEOREM`: the frozen RCB output has source multidegree at most
  `(16,16,8,4,2)`.
- `RESTRICTED THEOREM`: the componentwise norm tensor has a degree-preserving
  representative of multidegree at most `(32,32,16,8,4)` on registered
  `F_p` inputs.
- `RESTRICTED THEOREM`: its exact TT cut ranks are bounded by
  `(96,9216,288,12)`, subject to finite-registry ambient caps.
- `RESTRICTED THEOREM`: it is a target-quadratic linear combination of six
  target-independent source tensors, five in the frozen trace-zero basis.
- `HYPOTHESIS`, `NOVELTY-UNVERIFIED`: exact source or common-basis TT advice
  can be constructed with useful constants and specialized online in `O(B)`
  field operations and field words.
- `OPEN`: compression through `h_Q^(p-1)`, exact zero localization, relation
  generation, matrix solution, target descent, and any ECDLP improvement.

This note is a paper theorem and implementation contract. It is not evidence
of a complete relation compiler.

### Assumptions

- `E/F_p` is a smooth short-Weierstrass plane cubic
  `Y^2 Z=X^3+aXZ^2+bZ^3`, with `p>3`.
- Every primary registry entry is a distinct `F_p` point represented in
  projective coordinates.
- Point addition is the literal 40-gate Algorithm 1 of Renes, Costello, and
  Batina, with `b3=3b`, in the frozen left-associated tree. The paper gives a
  complete bidegree-`(2,2)` addition law for the relevant prime-order setting:
  [official publication page](https://www.microsoft.com/en-us/research/publication/complete-addition-formulas-for-prime-order-elliptic-curves/).
- `K=F_p(omega)` is the manifest's quadratic extension. Put
  `t=Tr(omega)` and `n=Norm(omega)`.
- The target is `Q=(X_Q:Y_Q:Z_Q)`. The frozen RCB tree returns
  `S=(X:Y:Z)`.
- Exact TT rank is the exact matrix rank of a declared unfolding over a
  declared finite field.

### Evidence so far

#### 1. RCB multidegrees

One RCB call is bihomogeneous of degree `(2,2)` in its two projective inputs.
Composing the frozen left-associated tree gives the following upper bounds:

```text
S12     = Add(P1,P2)        : (2,2)
S123    = Add(S12,P3)       : (4,4,2)
S1234   = Add(S123,P4)      : (8,8,4,2)
S12345  = Add(S1234,P5)     : (16,16,8,4,2)
```

Define

```text
e_X = Z_Q X-X_Q Z,
e_Y = Z_Q Y-Y_Q Z,
g_Q = e_X+omega e_Y.
```

The target coordinates are coefficients with respect to the five source
modes, so `e_X`, `e_Y`, and `g_Q` have source multidegree at most

```text
D=(16,16,8,4,2).
```

"At most" is essential: target specialization and reduction modulo the curve
equation may cancel leading terms.

#### 2. Frobenius qualification and exact norm

The literal homogeneous polynomial `g_Q^p` has multidegree `pD`. It is wrong
to use that literal polynomial in a degree-doubling proof.

The registered source and target coordinates lie in `F_p`, hence `e_X` and
`e_Y` are `F_p`-valued. Define the degree-preserving conjugate representative

```text
gbar_Q=e_X+omega^p e_Y.
```

At every registered tuple,

```text
gbar_Q(tuple)=g_Q(tuple)^p.
```

Therefore the componentwise norm tensor is represented exactly by

```text
h_Q = g_Q gbar_Q
    = e_X^2+t e_X e_Y+n e_Y^2.
```

This representative has source multidegree at most

```text
2D=(32,32,16,8,4).
```

The theorem concerns the evaluated tensor on registered `F_p` points and this
degree-preserving representative. It does not identify absolute Frobenius
pullback with coefficient conjugation in the homogeneous coordinate ring.

#### 3. Plane-cubic Hilbert dimensions

Let

```text
R=F[X,Y,Z]/(Y^2 Z-X^3-aXZ^2-bZ^3).
```

For `d>=1`, one cubic relation gives

```text
dim_F R_d = binom(d+2,2)-binom(d-1,2)=3d.
```

This is also the genus-one Riemann-Roch dimension; see the
[Stacks Project Riemann-Roch chapter](https://stacks.math.columbia.edu/tag/0B5B).
For degrees `(32,32,16,8,4)`, the five mode function spaces therefore have
dimensions at most

```text
(n1,n2,n3,n4,n5)=(96,96,48,24,12).
```

At cut `k`, an evaluated polynomial in the tensor product of these function
spaces has matrix rank no larger than the smaller tensor-product dimension on
the two sides. Thus

```text
rho1 <= min(96,96*48*24*12)       = 96
rho2 <= min(96*96,48*24*12)       = 9216
rho3 <= min(96*96*48,24*12)       = 288
rho4 <= min(96*96*48*24,12)       = 12.
```

For a registry of size `B`, the exact theorem includes physical ambient caps.
Writing

```text
m=(min(B,96),min(B,96),min(B,48),min(B,24),min(B,12)),
```

the four bounds are

```text
rho_k <= min(product(m_j,j<=k), product(m_j,j>k)).
```

A simpler but sometimes weaker display is

```text
(rho1,rho2,rho3,rho4)
  <= (min(B,96), min(B^2,9216), min(B^2,288), min(B,12)).
```

Because an `F_p` matrix has the same rank after scalar extension to `K`, the
rank of `h_Q` over `F_p` equals its rank over `K`. The implementation must
still compute the declared base-field rank independently.

For comparison, `g_Q` has per-mode dimensions `(48,48,24,12,6)` and
asymptotic rank bounds

```text
(48,1728,72,6).
```

These are upper bounds, not exact or minimal ranks.

#### 4. Six fixed source tensors

Expanding the quadratic norm gives

```text
h_Q = c1 X^2+c2 XZ+c3 Z^2+c4 XY+c5 YZ+c6 Y^2,
```

where

```text
c1 = Z_Q^2
c2 = -Z_Q(2X_Q+tY_Q)
c3 = X_Q^2+tX_QY_Q+nY_Q^2
c4 = tZ_Q^2
c5 = -Z_Q(tX_Q+2nY_Q)
c6 = nZ_Q^2.
```

The six tensors

```text
X^2, XZ, Z^2, XY, YZ, Y^2
```

depend on the curve, registry, circuit, mode order, and tree but not on the
target. The coefficients are homogeneous quadratic functions of the target;
the construction is not target-linear.

Every frozen extension basis has `t=0`, so `c4=0` and only five source tensors
have nonzero coefficients. The general six-source statement is retained to
make the basis dependence explicit.

For `Q=O=(0:1:0)`, the formula gives `h_O=nZ^2`, as required. If the target is
rescaled by `mu` and source mode `j` by `lambda_j`, homogeneity predicts

```text
h_Q -> mu^2 product_j(lambda_j^(2D_j)) h_Q.
```

This gives a stronger projective-rescaling control than zero-set agreement
alone.

#### 5. Conditional `O(B)` online construction

There are two exact preprocessing routes.

1. Construct exact TT advice for the fixed source tensors and combine it with
   the six target coefficients.
2. Reduce the source polynomials into fixed bases of
   `R_32 tensor R_32 tensor R_16 tensor R_8 tensor R_4`, construct a common
   coefficient-space TT, specialize the target there, and apply the five mode
   evaluation matrices.

All section dimensions and theorem rank caps are independent of `B`.
Conditional on actually producing this advice, target coefficient formation,
physical-core specialization, and exact fixed-rank normalization use `O(B)`
field operations and field words. In canonical bytes this is
`O(B log p)=O(B log B)` in the factor-base regime.

The existence proof does not construct the advice. Adding six independent TTs
by direct sums can multiply raw ranks by six; retaining the Hilbert caps
requires common bases or exact normalization. Every such operation is charged.

The constants are severe. The full coefficient tensor ceiling contains

```text
96*96*48*24*12 = 127401984
```

base-field coefficients. A dense TT at the theorem ranks allocates

```text
B*(96+96*9216+9216*288+288*12+12)
  = 3542508*B
```

base-field words. These are bounds, not a recommended materialization. Useful
structure must reduce actual ranks, exploit sparsity, or provide implicit
exact cores.

#### 6. Why toy rank growth is not the benchmark

At the central `2|3` cut,

```text
rho2(h_Q)<=min(B^2,9216).
```

Every `B<=96` experiment permits full `B^2` rank. Observing saturation for the
entire frozen `B=3..10` sweep is therefore compatible with the theorem and
cannot reject the asymptotic route. The full tensor runs are `SANITY_ONLY`.

The coefficient flattening for `h_Q` has dimensions

```text
9216 by 13824.
```

It has 127401984 entries, about 972 MiB at eight bytes per entry before exact
elimination workspace. Dense construction is prohibited by the v1 contract.
The useful successor must derive an implicit row space, sparse exact cores, or
an exact upper/lower certificate directly from the circuit.

#### 7. The next power frontier

For a fixed positive integer `e`, `h_Q^e` has multidegree at most

```text
(32e,32e,16e,8e,4e)
```

and asymptotic cut bounds

```text
(96e,9216e^2,288e^2,12e).
```

The immediate square `h_Q^2` has bounds

```text
(192,36864,1152,24)
```

and a central coefficient flattening of size `36864 by 110592`, about 30.4
GiB at eight bytes per entry before elimination. It must also be handled
implicitly.

For the binary state `h_Q^(2^j)`, the central Hilbert ceiling is

```text
rho2 <= min(B^2,9216*4^j).
```

The first stage where this ceiling can reach `B` is

```text
j_star(B)=max(0,ceil(log_4(B/9216))).
```

The decisive later experiment must bracket `j_star-1` and `j_star`, rather
than fit several fixed toy powers. Fixed powers always have a constant Hilbert
ceiling as `B` tends to infinity; the Fermat exponent grows with `p`.

### Failure modes

- Treating literal `g_Q^p` as a degree-`D` polynomial.
- Calling a Hilbert upper bound an attained or minimal exact rank.
- Inferring asymptotic growth from `B<=96` ambient saturation.
- Hiding the 127401984-coefficient ceiling behind `O(1)` notation.
- Calling six direct-summed source TTs a Hilbert-capped train without exact
  normalization.
- Omitting fixed-curve advice construction, traffic, peak workspace, or
  canonical byte width.
- Using affine addition to assign nonzero RCB tensor values.
- Testing only fixed powers while the exponent grows with `B`.
- Treating a first-norm representation as a zero locator or decomposition.

### Next concrete action

Implement the frozen `SANITY_ONLY` generator and non-importing verifier, run
the mutation suite, and authorize a successor coefficient-space experiment
only if every semantic and accounting gate passes.

### Artifact paths

- `experiments/EXP-ECDLP-TT-NORM-RANK-001/research-question.json`
- `experiments/EXP-ECDLP-TT-NORM-RANK-001/hypothesis.json`
- `experiments/EXP-ECDLP-TT-NORM-RANK-001/specification-v1.json`
- `experiments/EXP-ECDLP-TT-NORM-RANK-001/instance-manifest-v1.json`
- `experiments/EXP-ECDLP-TT-NORM-RANK-001/contract-v1.md`

