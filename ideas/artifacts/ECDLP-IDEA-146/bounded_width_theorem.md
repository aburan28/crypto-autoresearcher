# IDEA-146 faithful-addition WNU preservation gate

Status:
`SCOPED_NEGATIVE_FAITHFUL_GROUP_ADDITION_SIGNATURE_HAS_NO_PROPER_FACTOR_BASE_PRESERVING_WNU`

This is a theorem-only producer receipt. No contract or experiment was run. It
closes the WNU operation declared by IDEA-146 when the CSP faithfully exposes
the prime-order group-addition graph and the factor base as a unary relation.
It does not claim a lower bound for every x-only summation-polynomial CSP or
for every possible source-generation algorithm.

## Frozen interface

Let

```text
G = <P> ~= Z/NZ
```

where `N` is prime. Let `F` be a target-independent factor base with

```text
1 < B = |F| < N.
```

The relational signature contains the faithful ternary addition graph

```text
Add = {(x,y,z) in G^3 : x+y=z}
```

and the unary relation `F`. Signs, repeated points, the identity, target
parameters, and projective exceptional charts may also be present. They can
only add preservation obligations and are not needed below.

Fix an arity `k >= 3`. A candidate operation `w:G^k -> G` must:

1. preserve `Add`;
2. be idempotent, `w(x,...,x)=x`;
3. satisfy the weak-near-unanimity identities

   ```text
   w(y,x,...,x) = w(x,y,x,...,x) = ... = w(x,...,x,y);
   ```

4. preserve the factor base, `w(F^k) subseteq F`.

These are necessary conditions for the factor-base-preserving WNU bounded-
width route stated in IDEA-146.

## Theorem 1: the only faithful-addition WNU is averaging

For vectors `u,v in G^k`, every coordinate triple

```text
(u_i,v_i,u_i+v_i)
```

lies in `Add`. Preservation by `w` therefore gives

```text
w(u+v) = w(u)+w(v).
```

Thus `w:G^k -> G` is a group homomorphism. Since `G` is cyclic of prime
order, there are coefficients `a_1,...,a_k in Z/NZ` such that

```text
w(x_1,...,x_k) = sum_i a_i x_i.
```

Idempotence gives

```text
sum_i a_i = 1 mod N.
```

Putting `y` in slot `i` and `x` in every other slot gives

```text
w(x,...,y,...,x) = a_i y + (1-a_i)x.
```

The WNU identities make this value independent of `i`. Choosing `y-x` to be
a generator of `G` gives `a_i=a_j` for all `i,j`. Hence there is one
coefficient `a` with

```text
k*a = 1 mod N,
w(x_1,...,x_k) = k^(-1) * sum_i x_i.
```

If `k=0 mod N`, no idempotent faithful-addition WNU of this arity exists. For
the fixed arities relevant to the ECDLP campaign and sufficiently large `N`,
`k` is invertible and modular averaging is the unique candidate.

## Theorem 2: modular averaging cannot preserve a proper factor base

Because multiplication by `a=k^(-1)` is a bijection of `G`,

```text
|w(F^k)| = |a*(F+...+F)| = |kF|.
```

The iterated Cauchy-Davenport bound in the prime cyclic group gives

```text
|kF| >= min(N, kB-k+1).
```

For `k>=2` and `1<B<N`, this is strictly larger than `B`:

- if the minimum is `N`, then `N>B`;
- otherwise

  ```text
  kB-k+1-B = (k-1)(B-1) > 0.
  ```

Therefore `w(F^k)` cannot be a subset of `F`. This contradicts factor-base
preservation.

## Corollary for IDEA-146

No proper nontrivial factor base in a prime-order subgroup admits a WNU
polymorphism that preserves both the faithful addition graph and factor-base
membership. Consequently, bounded-width local consistency cannot supply the
claimed source tuples through the operation frozen by IDEA-146.

The two equality cases are controls, not ECDLP algorithms:

- `|F|=1` is closed but cannot provide a rank-`B` relation campaign or generic
  blind descent;
- `F=G` is closed but has `B=N`, so factor-base storage, relation output, and
  factor-log work already exceed the `N^0.45` gate and Pollard rho.

Changing the CSP backend does not alter this nonexistence result. Replacing
`F` by an affine/coset language is the already occupied IDEA-122 control and
does not preserve a generic public factor base.

## Exact scope and surviving exception

The proof applies to any signature in which `Add` and `F` are basic or
primitive-positive definable relations, because polymorphisms preserve such
relations. It therefore covers a faithful projective addition signature even
if extra sign, identity, repetition, or exceptional-chart relations are
included.

It does not automatically cover a deliberately nonfaithful x-only signature
that exposes only one high-arity summation-polynomial relation and does not
primitive-positive define signed group addition. Such a successor must prove,
before implementation, all of the following:

1. a non-affine WNU on that exact x-only structure;
2. preservation of the target-independent factor-base unary relation;
3. an exact lift from x-only local-consistency views to every signed source,
   including repeats, vertical pairs, infinity, and nonreduced fibers;
4. no reintroduction of the faithful addition graph, a source table, or a
   growing-width completion oracle during the lift; and
5. complete relation-collection and blind-descent exponents at most `0.45`.

That exception is a mechanism-new theorem obligation, not evidence that the
frozen IDEA-146 operation survives.

## Cost disposition

The claimed WNU constructor does not exist on the frozen faithful signature,
so its query exponents `q,q_m` are not finite algorithmic costs. Falling back
to `F=G` sets `beta=1`; falling back to explicit source completion restores at
least the source-fiber cost that IDEA-146 was required to remove. Neither path
can satisfy

```text
lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta) <= 0.45,
mu=max(a_m,q_m,beta+o,ell_m,u) <= 0.45.
```

This is a scoped algebraic nonexistence result, not a generic-group lower
bound, relation campaign, factor-log solve, blind descent, Shoup-bound
improvement, or breakthrough.

## Independent review checklist

An independent reviewer should verify:

1. preservation of `Add` really implies `w(u+v)=w(u)+w(v)`;
2. every homomorphism `G^k -> G` has the displayed coefficient form;
3. idempotence and WNU force equal coefficients and `k*a=1`;
4. the iterated Cauchy-Davenport inequality is applied in the prime cyclic
   subgroup, not to the ambient curve coordinates;
5. the strict inequality holds for every `k>=2` and `1<B<N`; and
6. no conclusion is extended to an x-only signature lacking a definition of
   faithful signed addition.

## Primary references

- Barto and Kozik, *Constraint Satisfaction Problems of Bounded Width*:
  <https://doi.org/10.1109/FOCS.2009.32>.
- Davenport, *On the Addition of Residue Classes*:
  <https://doi.org/10.1112/jlms/s1-10.37.30>.
- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*: <https://eprint.iacr.org/2004/031>.

The first reference supplies the neighboring WNU/bounded-width framework; the
second supplies the sumset bound used in Theorem 2; the third supplies the
neighboring ECDLP relation representation. None states a below-rho ECDLP
algorithm.
