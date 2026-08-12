# Theory note: injectivity barriers for exact recursive-state quotients

## Status

`RESTRICTED THEOREMS`, `MODEL-BOUND`, `REJECTED_SCOPED`.

The results below rule out one proposed initial observation and sharply limit
exact arbitrary-target equivalence classes and exact low-dimensional linear
profile modules. They do not rule out implicit resultants, full-rank structured
transforms, nonlinear branch operators, multipoint operators, target
distributions, approximate filters with exact fallback, or ECDLP improvements
generally.

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

## Theorem 4: prime-cycle translation profiles have full linear rank

Let `G=C_q` for prime `q`, let `D` be nonempty and proper, and let `f=1_D`.
Over `Q` or `C`, convolution by `f`,

```text
T_f(g) = f * g,
```

is invertible. Consequently all `q` oriented profiles `T_f(delta_R)` are
linearly independent. For odd `q`, the x-orbit multiplicity profiles

```text
T_f(delta_0),
T_f(delta_R + delta_-R),  1 <= R <= (q-1)/2,
```

are also linearly independent.

### Proof

Write

```text
F_D(X) = sum_{d in D} X^d
```

using representatives `0,...,q-1`, and let `zeta` be a primitive qth root of
unity. The Fourier eigenvalues of `T_f` are `F_D(zeta^k)`. At `k=0` the
eigenvalue is `|D|`, which is nonzero. For `k != 0`, `zeta^k` is primitive and
has minimal polynomial

```text
Phi_q(X) = 1 + X + ... + X^(q-1).
```

If `F_D(zeta^k)=0`, then `Phi_q` divides `F_D` over `Q`. Since `F_D` has degree
less than `q` and 0/1 coefficients, this forces `F_D=0` or `F_D=Phi_q`, meaning
`D` is empty or all of `G`. Both contradict the assumptions. Every Fourier
eigenvalue is therefore nonzero, so `T_f` is invertible over `C`. Its matrix has
integer entries and nonzero determinant, so it is also invertible over `Q`.

The point masses `delta_R` form a basis. Their images under an invertible map
are independent. The orbit vectors `delta_0` and `delta_R+delta_-R` are also
independent, so their images are independent as well. QED.

### Even-subspace correction

The orbit vectors form a basis of the even subspace `E+`. Their profiles form a
basis of `T_f(E+)`. If `D=-D`, as for a sign-complete exact complement support,
then convolution preserves inversion symmetry and `T_f(E+)=E+`. Without that
symmetry, the image basis remains independent but need not itself be even.

### Linear-module corollary

Any exact linear factorization over `Q` or `C` of the complete all-target
oriented compatibility matrix needs latent dimension at least the number of
retained oriented states. The corresponding x-orbit multiplicity matrix needs
latent dimension at least the number of retained x-orbits. Thus injective state
names cannot be replaced by a lower-dimensional exact linear profile module.

### Finite-characteristic and model limits

- Over a field `K`, convolution is invertible exactly when
  `gcd(F_D(X),X^q-1)=1` in `K[X]`. Rank can drop modulo exceptional primes, so
  every finite-field linear-module preflight must compute this gcd.
- In characteristic `q`, `X^q-1=(X-1)^q` and `F_D(1)=|D| != 0 mod q`, so the
  convolution remains invertible even though the Fourier proof is unavailable.
- The theorem requires all targets and exact integer orientation multiplicity.
  Target restriction, Boolean OR support, or one-witness semantics are different
  operators.
- Full rank does not imply a large circuit. Circulant operators have succinct
  descriptions and fast transforms when their character coordinates are
  available. The theorem does not rule out full-rank structured transforms,
  nonlinear first-witness reporting, adaptive subtree predicates, or sparse
  recovery with an exact charged fallback.

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

Theorem 4 also rejects an exact low-dimensional linear factorization of the
complete compatibility profiles. This is a rank statement, not a circuit or
data-structure lower bound.

## Open positive directions

- A full-rank structured transform whose resident representation is succinct
  and whose first-witness decoder does not emit every profile value.
- An exact nonlinear subtree predicate that supports first-witness descent with
  a logarithmic witness trace.
- An implicit multipoint operator that reports sparse roots without emitting
  the full evaluation vector.
- Target-distribution-specific filters with exact fallback and fully charged
  failure probability.
- A batch operator sharing work across `K` targets without emitting `K|D2_x|`
  state.

Each direction needs an exact witness-lifting path and a same-map random
control. None is established by these restricted theorems.

## Next proof obligation

The exact all-target partition and exact low-dimensional linear-profile routes
are now closed as scoped barriers. Write an object-dimension ledger for an exact
first-witness branch operator. Reject it before implementation if the root
subtree predicate, cached node state, target specialization, fallback, or
witness routing contains a full D2 profile or target-support table.
