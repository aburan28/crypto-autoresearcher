# Bounded-separation preflight v1

## Handoff: coordinate moments and canonical separation

### Claim or task

Derive or refute a bounded-separation representation for the complete finite
branch element

```text
G_(I,Q)=Delta_Q^n*M_I(A_Q/Delta_Q)
       =sum_(k=0)^n m_k*A_Q^k*Delta_Q^(n-k)
```

before constructing a scalar source norm, where `n=deg(M_I)` and the balanced
root has `n=N2=Theta(B^2)`.

### Status

- `RESTRICTED THEOREM`, paper-only: on a split finite branch, the homogeneous
  coordinate powers span `min(n+1,t_Q)` dimensions, where `t_Q` is the number
  of distinct translated coordinate values on that branch.
- `NEGATIVE RESULT`, `MODEL-BOUND`: an explicit canonical symmetric-power CP
  expansion, an uncollected CP/Horner term stream, and a coefficient-linear
  node-oblivious moment interface fail the strict root gate whenever their
  stated `Omega(n)` conditions hold. The explicit reduced trace-resolvent
  recurrence recreates the translated-D3 polynomial and also fails.
- Overall candidate: `REVISE`, `REVIEW_REQUIRED`. Minimal CP/TT rank, a fixed-
  node nonlinear scalar circuit, compact complete selectors, and a
  composition-tower recurrence remain open.

No implementation or experiment is authorized.

### Assumptions

- `K=F_p(omega)` is the registered quadratic encoding field and all source
  branches split over `K`.
- `X_pi` is one fixed typed finite-output branch, or a disjoint registered
  union of such branches on which the denominator is componentwise nonzero.
- The corresponding split algebra is `A_pi=K^X_pi`. The branch element
  `Delta_Q` is a unit and `U_Q=A_Q/Delta_Q` is the exact encoded coordinate of
  `Q-S` on each component.
- `M_I(Z)=sum_(k=0)^n m_k Z^k` is the monic product of the distinct finite D2
  encodings in node `I`.
- `n=Theta(B^2)` and any claim that `t_Q>n` is used only for a measured or proved
  collision-light branch. Translation itself is injective on distinct finite
  points, but ordered source triples may collide before translation.
- Every explicit CP summand below is separable across the three source
  algebras. Counts are generator occurrences in the specified construction,
  not lower bounds on tensor rank after quotient reduction or collection.

### Evidence so far

#### Exact coordinate-moment theorem

Let

```text
t_Q = |{U_Q(x): x in X_pi}|.
```

Because `A_pi` is split, a polynomial annihilates `U_Q` exactly when it
vanishes at every distinct component value. Therefore the minimal polynomial
of `U_Q` in `A_pi` is

```text
mu_(U_Q)(Z)=product_(z in image(U_Q)) (Z-z),
deg(mu_(U_Q))=t_Q.
```

Multiplication by the unit `Delta_Q^n` is an invertible `K`-linear map, and

```text
A_Q^k*Delta_Q^(n-k)=Delta_Q^n*U_Q^k.
```

It follows that

```text
dim_K span{A_Q^k*Delta_Q^(n-k): 0<=k<=n}
  = min(n+1,t_Q).
```

In particular, if one registered finite branch union exposes at least `n+1`
distinct D3 outputs, then it has exactly `n+1` independent homogeneous moment
directions. This instantiates the abstract structured-group concern with the
actual translated elliptic coordinate, but only inside the explicit split
algebra.

For the complete disjoint union of finite-output branches, translation and the
oriented encoding are injective on the distinct D3 points. If `o_3` records
whether the D3 identity is supported, then

```text
t_Q=N3-epsilon_+(Q)+o_3*1_(Q != O).
```

Here `epsilon_+(Q)` removes finite `S=Q`, whose output is the identity. For
finite `Q`, a supported `S=O` contributes the otherwise unattainable finite
output `Q`; for `Q=O` it again outputs the identity and contributes no value.
Thus the collision-light specialization has
`t_Q=Theta(B^3)>n=Theta(B^2)`. This exact cardinality uses distinct D3 points,
not their ordered source multiplicities.

Define the coefficient-linear map

```text
Phi_Q: K^(n+1) -> A_pi,
(m_0,...,m_n) |-> sum_k m_k*A_Q^k*Delta_Q^(n-k).
```

Any node-oblivious linear interface that factors `Phi_Q` through `K^r` and can
recover the complete branch element for every degree-`n` coefficient vector
must have

```text
r >= rank(Phi_Q)=min(n+1,t_Q).
```

Thus, when `t_Q>n`, this model carries `n+1=Theta(B^2)` target moments and fails
the strict `o(B^2)` state or traffic gate. The theorem does **not** apply to a
fixed preprocessed `M_I`, a nonlinear scalar zero test, or a circuit that never
recovers `G_(I,Q)` as an algebra element.

#### Canonical symmetric-power expansion

Suppose a fixed finite branch supplies CP descriptions

```text
A_Q     = sum_(u=1)^r_A alpha_(u,Q),
Delta_Q = sum_(v=1)^r_D delta_(v,Q),
```

where every `alpha_u` and `delta_v` is a rank-one three-source tensor. For one
coefficient `m_k`, the uncollected multinomial expansion emits

```text
binom(k+r_A-1,r_A-1)*binom(n-k+r_D-1,r_D-1)
```

separable generator occurrences. Consequently its exact formal occurrence
count is

```text
L(M_I;r_A,r_D)
  = sum_(k in supp(M_I))
      binom(k+r_A-1,r_A-1)
      *binom(n-k+r_D-1,r_D-1).
```

If all `n+1` coefficients are nonzero, Vandermonde convolution gives

```text
L=binom(n+r_A+r_D-1,r_A+r_D-1).
```

The root polynomial is monic. Its constant coefficient is also nonzero:
`enc(P)=0` would imply `x(P)=y(P)=0`, and a finite point with `y=0` has order
two, which is absent from the registered odd prime-order subgroup. Hence:

- if `r_A>=2`, the monic `A_Q^n` contribution alone emits at least `n+1`
  occurrences;
- if `r_D>=2`, the nonzero constant `Delta_Q^n` contribution alone emits at
  least `n+1` occurrences;
- if `r_A=r_D=1`, then `L=|supp(M_I)|`, so this route reaches `n+1` exactly for
  a dense node polynomial and remains open for a proved `o(n)`-sparse or
  compositional node family.

There is a coordinate-specific symbolic exclusion for the last case. Let
`h=x+omega*y` be the nonconstant oriented encoding function on `E_K`, and
consider before finite source-quotient reduction

```text
F_Q(P_1,P_2,P_3)=h(Q-P_1-P_2-P_3).
```

The pullback of every zero or pole of `h(Q-S)` under the addition map
`E^3 -> E` is a nonvertical addition fiber. By contrast, the divisor of a
nonzero product `f_1(P_1)f_2(P_2)f_3(P_3)` is a sum of coordinate-vertical
divisors. Therefore `F_Q` is not a rank-one separable rational function. If
both a global numerator `A_Q` and denominator `Delta_Q` were rank one, their
ratio would be rank one, a contradiction. Thus at least one symbolic base rank
is at least two, and the explicit global canonical expansion reaches `n+1`
occurrences even when `M_I` is sparse.

This divisor argument is an unreduced function-field statement. Restriction to
the finite registered source roots can create accidental rank collapse, and an
exact quotient-level collection algorithm remains outside the negative result.
A fixed complete projective addition circuit also needs a separately charged
finite-output/identity treatment; completeness of point addition alone does
not make the membership denominator a global unit.

An implementation that explicitly emits, streams, or accumulates these `L`
target-dependent terms performs `Omega(L)` term events even if every source
power is fixed advice. Therefore `L=Omega(n)=Omega(B^2)` fails the strict online
work or traffic gate. Storing three reduced length-`Theta(B)` factors for every
term is worse, but that representation is not needed for the scoped rejection.

Collection, cancellation, quotient reduction, structured cores, or a direct
scalar contraction may reduce the representation. Invoking any of them changes
the interface and requires an exact construction and its own ledger; `L` is
not a minimal CP-rank claim.

#### Trace-resolvent recurrence

A different scalar construction starts from the exact trace resolvent

```text
S_Q(z)=Tr_(A_pi/K)((z-U_Q)^-1)
      =sum_(x in X_pi) 1/(z-U_Q(x)).
```

After equal component values are collected, their positive multiplicities are
strictly below `p` in the asymptotic regime `|X_pi|=O(B^3)<p`; they therefore
do not vanish in `K`. The reduced denominator is exactly

```text
q_Q(z)=product_(u in image(U_Q)) (z-u),
deg(q_Q)=t_Q.
```

The Laurent moments `mu_j=Tr(U_Q^j)` obey the order-`t_Q` recurrence induced by
`q_Q`, and the node predicate is exactly

```text
gcd(M_I,q_Q) != 1.
```

On the complete branch union, `q_Q` is the squarefree translated finite-D3
polynomial `c_Q` from `root-operator-preflight-v1.md`, multiplied for finite
`Q` by `(z-enc(Q))` when `o_3` is present. That extra factor is exactly the
root-only D3-identity route. In the collision-light regime `q_Q` has degree
`Theta(B^3)`, not a bounded recurrence order. Explicitly constructing its
coefficients, initial moments, Bezout certificate, or recurrence state fails
before child descent. A new implicit nonlinear specialization could avoid
exposing `q_Q`; the trace identity alone does not supply one.

#### Horner and child accounting

Homogeneous Horner evaluation avoids writing the multinomial formula, but an
uncompressed CP or TT implementation still appends or multiplies the same
target-dependent power states. It is rejected only when it exposes
`Omega(n)` generator updates, moment reads, or coefficient traffic. An exact
rank-truncation theorem or a structured recurrence would be a distinct positive
candidate; numerical tensor rounding is not exact enough for a zero predicate.

For `I=I_L disjoint-union I_R`, exact semantics give

```text
M_I=M_(I_L)*M_(I_R),
G_I=G_(I_L)*G_(I_R),
R_I=R_(I_L)*R_(I_R).
```

A parent scalar alone does not identify the vanishing child. At the first split
the candidate must compute or update both child scalars. In the explicit
canonical interface the charged term count is

```text
L(M_(I_L);r_A,r_D)+L(M_(I_R);r_A,r_D).
```

If either base rank is at least two, the two monic/nonzero-constant bounds sum
to `Omega(n)` even without coefficient density. If both ranks are one, a pass
requires the two child descriptions and their update law to have total
`o(n)` support or an equally compact non-monomial recurrence.

#### Gate ledger

| Boundary | Exact charge | Disposition |
|---|---:|---|
| Fixed branch `A_Q,Delta_Q` CP factors | construction, reduced factor vectors, and target scalars | `UNDEFINED`; constant CP rank alone is insufficient |
| Canonical symmetric-power list | `L(M_I;r_A,r_D)` target term events | `REJECTED_SCOPED` when `L=Omega(n)` |
| Node-oblivious linear moment state | at least `min(n+1,t_Q)` field coordinates | `REJECTED_SCOPED` when `t_Q>n` |
| Uncompressed CP/TT Horner | every generator update, coefficient read, and exact core | `REJECTED_SCOPED` only if the disclosed path reaches `Omega(n)` |
| Explicit reduced trace resolvent | `t_Q` recurrence coefficients or moments; `t_Q=Theta(B^3)` on full support | `REJECTED_SCOPED` |
| Fixed-node nonlinear scalar circuit | all internal spaces, work, traffic, and proof | `OPEN` |
| Complete branch selector or complete addition law | construction, exceptional cases, and target state | `UNDEFINED`, `REVIEW_REQUIRED` |
| Both child values or update | first-split and full path cost | `UNDEFINED` outside explicit term interface |
| Positive/nonzero certificate | circuit transcript and independent replay | `UNDEFINED` |
| Terminal signed witness | charged `Theta(B)` factor scan against D2 | available and below the root gate |

The `n+1` span theorem is a useful barrier for actual elliptic-coordinate
moments. It is not an arithmetic-circuit lower bound for the scalar norm or its
zero predicate. A high-degree fixed polynomial can have a short circuit, and a
special root set can have a sparse or compositional product polynomial.

#### Positive and negative controls

- Positive compression control: if `r_A=r_D=1`, `p` does not divide `n`, and
  `M(Z)=Z^n-c` has `n` distinct roots, the canonical list has two terms. This
  exceptional multiplicative root geometry prevents degree alone from proving
  an `Omega(n)` barrier. It is a general tensor-algebra control, not a global
  elliptic-addition representation because of the divisor exclusion above.
- Negative interface control: for a dense `M` and formally independent
  generators, the exact canonical count is the Vandermonde value above and
  reaches at least `n+1` even in the minimal nonconstant two-generator case.
- Coordinate control: compare `t_Q` with the exact distinct finite D3 support.
  Translation preserves this cardinality after the `S=Q` identity omission;
  ordered source multiplicities must not be counted as distinct moments.

### Proof track

1. Independently replay the split-algebra minimal-polynomial proof and the
   Vandermonde occurrence count.
2. Instantiate one complete finite addition representation and disclose the
   actual separable ranks, reduced factors, and selector cost.
3. Prove a fixed-node scalar recurrence whose generators, moments, both-child
   updates, and certificates are all strict `o(n)`.
4. Preserve exact root-to-leaf witness recovery through the charged terminal
   scan.

### Disproof track

1. Exhibit quotient reductions or exact collection that compress the actual
   EC tensors below the formal occurrence count.
2. Exhibit a sparse or functionally decomposable D2 node family and show that
   both child descriptions stay compact along every path.
3. Construct a nonlinear scalar norm circuit that never factors through the
   full coefficient-linear moment space.
4. Find a collision-light source branch where `t_Q<=n`, narrowing the moment
   theorem's applicability without affecting its proof.

### Failure modes

- Reporting the formal CP occurrence count as minimal tensor rank.
- Applying the linear moment theorem to one fixed compiled node polynomial.
- Counting ordered source triples rather than distinct translated outputs in
  `t_Q`.
- Treating fixed node coefficients as online reads when a circuit embeds them.
- Omitting branch selectors, exact exceptional cases, both child values,
  certificates, or signed terminal provenance.
- Calling `soft-O(B^2)` strict subquadratic.

### Next concrete action

Specify a composition-tower fiber-node representation in which every root-path
child polynomial and scalar norm update has a proved exact `o(B^2)` interface,
or reject that representation before source code if any layer emits a degree-
`Theta(B^2)` polynomial, moment list, or target state.

### Artifact paths

- `nested-source-norm-preflight-v1.md`
- `nested-source-norm-literature-review-v1.md`
- `candidate-review-v2.md`
- `object-dimension-ledger.md`
