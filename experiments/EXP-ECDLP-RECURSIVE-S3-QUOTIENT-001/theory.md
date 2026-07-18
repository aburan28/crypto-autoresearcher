# Theory note: injectivity barriers for exact recursive-state quotients

## Status

`RESTRICTED THEOREM`, `MODEL-BOUND`, `REVIEW_REQUIRED`.

The results below rule out one proposed initial observation and sharply limit
exact arbitrary-target equivalence classes. They do not rule out implicit
resultants, low-rank modules, multipoint operators, target distributions,
approximate filters with exact fallback, or ECDLP improvements generally.

## Setup

Let `p` be odd. For one source branch write the public rational map as

```text
phi(t) = N(t) / D(t)
```

over `F_p`. Let `m(t)` be an accepted-root polynomial whose roots are distinct,
and assume `D(r) != 0` at every accepted root `r`. Let `u` be the finite
x-coordinate of a partial-sum state.

Viewed as a quadratic in `Z`, the leading coefficient of
`f3(u,phi(t),Z)` is `(u-phi(t))^2`. After denominator clearing by `D(t)^2`, it
is

```text
L_u(t) = (u D(t) - N(t))^2 mod m(t).
```

## Theorem 1: branch leading-coefficient injectivity

Assume the accepted roots contain `r1,r2` with
`phi(r1) != phi(r2)`. Then the map

```text
u -> L_u(t) in F_p[t]/(m(t))
```

is injective on finite state x-coordinates.

### Proof

Suppose `L_u=L_v mod m`. Evaluation at each accepted root is valid, so

```text
(u D(r)-N(r))^2 = (v D(r)-N(r))^2.
```

Subtract and factor:

```text
(u-v) D(r) ((u+v)D(r)-2N(r)) = 0.
```

Every accepted root is a non-pole, so `D(r) != 0`. If `u != v`, division by
`(u-v)D(r)` gives

```text
phi(r) = N(r)/D(r) = (u+v)/2
```

for every accepted root. This contradicts the existence of two distinct mapped
x-values. Therefore `u=v`. QED.

### Corollary

The complete denominator-cleared coefficient tuple of
`f3(u,phi(t),Z) mod m(t)` is also injective under these assumptions. Using it as
an initial partition color forces every finite state into a singleton before
transition refinement. It is an implementation negative control, not a
candidate compression observable.

### Exceptions and limits

- If the branch has no accepted roots, the observation carries no eligible
  transition semantics.
- If all accepted roots map to one x-value `x0`, the leading coefficient alone
  permits the reflection collision `v=2x0-u`; lower coefficients may split it.
- Accepted poles invalidate denominator clearing and must be rejected.
- The identity has no finite x-coordinate and needs a separate sentinel.
- Characteristic two is excluded; the experiment uses odd prime fields.
- Squarefreeness is useful for the product-of-fields interpretation. The proof
  only needs equality modulo `m` to imply equality at each accepted root.
- Normalization by a state-dependent projective scalar is a different map and
  requires a separate theorem; it cannot inherit this exact-equality proof.

## Theorem 2: arbitrary-target translation profiles are injective

Let `G` be a group of prime order and let `D` be a nonempty proper subset. For
an oriented state `R`, define its exact target profile

```text
h_R(Q) = 1_D(Q-R),  Q in G.
```

If `h_R=h_S` for all targets `Q`, then `R=S`.

### Proof

Equality of profiles is equality of translated sets:

```text
D+R = D+S.
```

Hence `D=D+(S-R)`. If `S-R` is nonzero, it generates the prime-order group, so
translation invariance forces `D` to be empty or all of `G`, contrary to the
assumption. Thus `S-R=0`. QED.

### Orbit caveat

An x-orbit identifies `{R,-R}` and a sign-symmetric output may identify the two
orientations already represented by that orbit. Any further merging requires a
separate classification of the complement set's sign symmetry. The theorem
still shows that preserving exact behavior for every arbitrary target is a
strongly state-separating requirement.

## Theorem 3: complete x-orbit profiles are injective

Let `G` be cyclic of odd prime order `n`, let `D` be a nonempty proper subset,
and let `f=1_D`. For the x-orbit `[R]={R,-R}`, retain the complete unordered
two-orientation compatibility result through its multiplicity profile

```text
c_[R](Q) = f(Q-R) + f(Q+R),  Q in G.
```

If `c_[R]=c_[S]` for all targets `Q`, then `[R]=[S]`.

### Proof

Fix an identification `G=Z/nZ` and an `n`th root of unity `zeta`. Because `f`
is not constant, Fourier inversion gives a nonzero frequency `k` with
`f_hat(k) != 0`. Fourier transforming the profile equality at that frequency
and cancelling `f_hat(k)` gives

```text
zeta^(kR) + zeta^(-kR) = zeta^(kS) + zeta^(-kS).
```

For nonzero `a,b`, equality `a+a^-1=b+b^-1` factors as
`(a-b)(ab-1)=0`. Hence `zeta^(kR)=zeta^(kS)` or
`zeta^(kR)=zeta^(-kS)`. Since `n` is prime and `k` is nonzero, multiplication
by `k` is invertible modulo `n`, so `R=S` or `R=-S`. Thus `[R]=[S]`. QED.

### Limits

- The theorem uses the complete orientation multiplicity `0`, `1`, or `2`.
  A boolean OR that discards multiplicity is a weaker query and needs a
  separate classification.
- Exact signed witness output contains at least this multiplicity information,
  so retaining witnesses cannot create additional merges.
- Composite-order groups can have noninvertible Fourier frequencies and need a
  stabilizer-by-stabilizer statement.
- Target subsets or target distributions do not provide the all-target profile
  assumed here.

## Consequence for the draft quotient

The original proposal combined state-separating choices:

1. an initial `f3` coefficient observation that is generically injective;
2. terminal equality for arbitrary-target behavior, which is injective on
   oriented states for every proper nonempty complement set;
3. complete two-orientation terminal behavior, which is injective on x-orbits
   for every proper nonempty complement set.

Singleton refinement under those definitions would be true by construction and
would not measure additive-combinatorial expansion. The full coefficient tuple
must remain a planted injective negative control. A viable positive candidate
must weaken state equality or change representation while proving that exact
queries do not reconstruct a full member-discrimination vector elsewhere.

## Open positive directions

- A low-rank module of transition operators rather than equality classes.
- An implicit multipoint operator whose resident state is sublinear even when
  its logical action distinguishes all points.
- Target-distribution-specific filters with exact fallback and fully charged
  failure probability.
- A batch operator sharing work across `K` targets without emitting `K|D2_x|`
  state.

Each direction needs an exact witness-lifting path and a same-map random
control. None is established by these restricted theorems.

## Next proof obligation

The exact all-target partition quotient is now closed as a scoped barrier under
complete orientation multiplicities. Formulate the weakest exact implicit
operator that can answer a registered target batch without storing one state
or coefficient per D2 x-orbit, then prove that its resident representation and
witness-lifting path are not a disguised member-discrimination vector.
