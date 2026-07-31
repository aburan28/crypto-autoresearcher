# PO-transfer-012 Pole Classification and Visible-Algebra Boundary

## Claim Status

- Target assignment of `u*du/y`: `OBSERVATION / EXACT FINITE-FIELD CHECK`.
- Denominator and degree classification: `RESTRICTED THEOREM`.
- Empty degree `5,7,8` registered charts: `NEGATIVE RESULT / TOY-EVIDENCE`.
- Visible-algebra splitting obstruction: `RESTRICTED THEOREM`.
- Explicit hidden correspondence and decomposition algorithm: `OPEN`.

## Setup and Assumptions

Let

```text
X_alpha: y^2=f_alpha(u),
f_alpha=(u^3+alpha)^3+832*(u^3+alpha)+931,
E: Y^2=x^3+832*x+931,
```

over `F_1009`, with `alpha in {24,598}`.  Characteristic is not `2` or `3`.
Consider a separable pointed map `phi:X_alpha->E` satisfying

```text
phi(infinity)=O_E,
phi^*(dx/Y)=c*u*du/y,            c != 0.
```

The pointed map induced by a Jacobian homomorphism is hyperelliptic-equivariant:
`phi(u,-y)=-phi(u,y)`.  It therefore has

```text
x=N(u)/M(u),
Y=y*S(u),
gcd(N,M)=1,
```

after making `M` monic.

## Target-Line Check

On the basis

```text
du/y, u*du/y, u^2*du/y, u^3*du/y,
```

the two Cartier-Manin matrices are

```text
alpha=24                    alpha=598
[764   0   0 622]           [595   0   0 578]
[  0 998   0   0]           [  0 998   0   0]
[  0   0 998   0]           [  0   0 998   0]
[608   0   0 296]           [321   0   0 465].
```

Both have characteristic polynomial `(T-62)*(T+11)^3`.  Since `998=-11`
modulo `1009`, `u*du/y` is an isolated target-trace line at both anchors; the
known quotient line `u^2*du/y` has the same target trace.  This removes the
untested assignment of the one-dimensional deck character.

## Differential Identity

Write

```text
K=N'*M-N*M',
G=N^3+832*N*M^2+931*M^3.
```

From `dx/Y=c*u*du/y`,

```text
S=K/(c*u*M^2).
```

Substitution into the target equation gives the exact polynomial identity

```text
f_alpha*K^2=lambda*u^2*M*G,       lambda=c^2.       (1)
```

## Pole-Divisor Lemma

Let `q` be an irreducible factor of `M` with multiplicity `m`.

If `q` does not divide the squarefree polynomial `f_alpha`, then `G` is a unit
at `q` and `ord_q(K)=m-1`.  Comparing valuations in (1) gives

```text
2*(m-1)=m,
m=2.
```

If `q|f_alpha`, squarefreeness contributes one to the left side, so

```text
1+2*(m-1)=m,
m=1.
```

Consequently

```text
M=D^2*H,
H|f_alpha squarefree,
gcd(D,H)=1.
```

At infinity, `ord(u)=-2`, `ord(du)=-3`, and `ord(y)=-9`, hence
`ord(u*du/y)=4`.  Pullback of a nonzero elliptic differential has order
`e_infinity-1`, so `e_infinity=5`.  If `d=deg N` and `m=deg M`, this is
`d-m=5`.  Finite roots of `D` contribute two unramified poles and roots of
`H` contribute one Weierstrass pole.  Therefore

```text
deg(phi)=d=5+2*deg(D)+deg(H).      (2)
```

For both anchors, `f_alpha` factors as three irreducible cubics.  Equations
(1) and (2) exhaust all base-field charts through degree eight:

| degree | denominator chart |
|---:|---|
| 5 | `M=1` |
| 6 | impossible: no linear factor of `f_alpha` |
| 7 | `M=(u-d0)^2` |
| 8 | `M=H`, one of the three cubic factors of `f_alpha` |

This classification is restricted to the pointed, separable,
hyperelliptic-equivariant target model above.  It does not classify translated
or isogenous codomains or non-point correspondences.

## Leading-Coefficient Reduction

For every chart, `deg(N)=5+deg(M)`.  The leading coefficient of (1) is

```text
n_d^2*(25-lambda*n_d).
```

After saturation by `n_d`, substituting `lambda=25/n_d` is exact.  The reduced
identity

```text
n_d*f_alpha*K^2-25*u^2*M*G=0
```

defines the same saturated chart.  PO12's independent verifier reconstructs
this relation and stores Singular lift certificates
`1=sum_i h_i*f_i` for every empty coefficient ideal.

## Visible-Algebra Splitting Obstruction

Let `K=Q(pi_E)` and let `W` be the `K`-rank-two multiplicity space of the
hidden `E^2` block.  On `W`, the deck operator satisfies

```text
sigma^2+sigma+1=0.
```

Because `K` is not `Q(sqrt(-3))`, this polynomial is irreducible over `K` and

```text
K[sigma] = K(zeta_3)
```

is a field embedded as a maximal commutative subalgebra of `M_2(K)`.  Frobenius
and Verschiebung act as elements of `K`.  Rosati sends `pi_E` to its complex
conjugate and `sigma` to `sigma^-1`, so adjoining Rosati does not leave this
field.

A field has only idempotents `0` and `1`.  Hence the rational algebra generated
by `F,V,sigma` and their Rosati adjoints contains no rank-one idempotent that
selects one hidden copy of `E`.  Any successful split must add a correspondence
in

```text
M_2(K) \ K(sigma).
```

This is a negative result for the visible operator algebra, not for the hidden
correspondence.  It explains why PO10's projector can isolate `E^2` but cannot
split it.

## Prime-41 Reconstruction Certifier

The first practical lift target is `ell=41`:

```text
41 != 3,73,1009,
41^2=1681 > 4*217=868,
41 == 2 (mod 3).
```

Modulo `41`, target Frobenius has eigenvalues `9,21` of orders `4,20`; the
complementary Frobenius polynomial is irreducible with eigenvalue order `140`.
Thus `F_(1009^140)` contains the required `41`-torsion.  Define

```text
P_41=21*I-(Phi+25*Phi^-1),
Q_41=P_41*(2*I-Sigma-Sigma^2),
e_hidden=3*Q_41.
```

Expected ranks on `J[41]` are `rank(P_41)=6` and `rank(e_hidden)=4`.
If two homomorphisms of Rosati norm at most `217` agree on `41`-torsion, their
difference is divisible by `41`; its norm is either zero or at least `41^2`.
The triangle bound gives norm at most `4*217`, so the difference is zero.  This
gives a uniqueness certificate after a candidate correspondence is recovered.

## Handoff: bounded maps and split obstruction

### Claim or task

Classify all normalized degree-at-most-eight point-map charts and determine
whether the known operators can split the hidden `E^2` block.

### Status

NEGATIVE RESULT / RESTRICTED THEOREM / TOY-EVIDENCE

### Assumptions

- The map and field assumptions are exactly those in the setup.
- The PO9 Weil-factor and endomorphism-ring checks are valid.

### Evidence so far

- Cartier-Manin matrices assign `u*du/y` to the target trace.
- The pole lemma exhausts degrees `5..8`.
- Independently reconstructed unit ideals and lift certificates close every
  registered chart at both anchors.
- The visible algebra is a field and has no nontrivial idempotent.

### Failure modes

- A degree-at-least-nine point map can exist.
- The bounded map can land on an isogenous target model.
- A divisor or theta correspondence need not be a point map.

### Next concrete action

Recover a polarization-derived rank-one correspondence outside `K(sigma)` on
`J[41]`, then uniquely lift and verify it under the degree-217 bound.

### Artifact paths

- `experiments/ecdlp_isogeny/po_transfer_012_verify_v3.json`
- `experiments/ecdlp_isogeny/po_transfer_012_verify.sage`
- `research/PO_transfer_013_contract.md`
