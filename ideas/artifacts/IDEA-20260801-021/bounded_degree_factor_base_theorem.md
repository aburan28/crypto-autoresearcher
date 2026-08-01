# IDEA-20260801-021 bounded-degree algebraic factor-base theorem

Status:
`SCOPED_NEGATIVE_BOUNDED_DEGREE_ALGEBRAIC_FACTOR_BASE__UNRESTRICTED_NO_GO_OPEN`

This is a theorem-only derivation receipt. It makes precise the strongest
negative statement currently justified by the proposed mechanism. It does not
prove that every algebraically described factor base, every implicit algebraic
membership solver, or every prime-field ECDLP algorithm is subexponential-
impossible.

## Frozen interface

Let `p` be prime. Let `E/F_p` be a nonsingular geometrically irreducible plane
cubic and let `G <= E(F_p)` be a subgroup of prime order `N`, with `N =
Theta(p)`. Let `f_p(X,Y) in F_p[X,Y]` have integer total degree `d_p >= 1`.
Its projective homogenization must share no component with the projective
closure of `E`; equivalently, the restriction of `f_p` to `E` is nonzero over
the algebraic closure. The polynomial is fixed before, and independently of,
the challenge and any trial randomness. Define the affine rational factor base

```text
F_p = { Q in G : f_p(x(Q), y(Q)) = 0 }.
```

This receipt covers an explicit point-decomposition descent of integer arity
`m_p >= 1`, using exactly `m_p` ordered factors with repetitions allowed. For a
target `T`, the descent accepts only if

```text
T in m_p F_p = {Q_1 + ... + Q_{m_p} : Q_i in F_p}.
```

The target family has min-entropy at least `log_2(N) - C` for one constant `C`
independent of `p`; uniform targets have `C=0`. Relation collection, membership
verification, and linear algebra are granted for free. A fixed-target statement
uses only the static coverage event `T in m_p F_p`. A separate optional
fresh-rerandomization interface is declared below; it may not be inferred from
repeating tuples against one fixed target and one fixed factor base.

## Theorem 1: the algebraic predicate cannot define a large factor base

Homogenize `f_p` to a degree-`d_p` projective curve. The projective closure of
`E` is an irreducible cubic. Since `f_p` does not contain `E` as a component,
Bezout's intersection theorem gives

```text
sum_{P in E_bar intersect V(f_p)} I_P(E_bar, V(f_p)) = 3 d_p.
```

Every rational affine point in `F_p` contributes at least one to this
intersection multiplicity. Therefore

```text
B_p := |F_p| <= 3 d_p.
```

The non-containment check is essential. A polynomial that vanishes identically
on `E` is not an admissible predicate in this theorem.

### Algebraic-degree generalization

The polynomial presentation is only a concrete way to expose the relevant
complexity. More generally, let `Z_p` be any projective algebraic locus whose
intersection with the projective cubic is proper and has finite geometric
intersection degree `Delta_p`. For

```text
F_p subseteq G intersect (E_bar intersect Z_p)(F_p),
```

the same argument gives `|F_p| <= Delta_p`. A finite zero-dimensional locus
uses its scheme degree as `Delta_p`; a proper complete intersection may use its
Bezout product bound. Replacing `3 d_p` by `Delta_p` in Theorems 2--4 yields
the identical coverage and rerandomized-cost conclusions. Thus the durable
scope is “algebraic factor bases with an explicit subpolynomial intersection-
degree bound,” not merely one syntactic polynomial form. Descriptions whose
closure contains `E`, or whose degree/intersection complexity is not charged,
remain outside the theorem.

### Theorem 1G: universal form within the algebraic-degree interface

For every sequence of target-independent projective algebraic loci `Z_p` with
no component equal to `E` and finite intersection degree `Delta_p`, and every
factor base satisfying

```text
F_p subseteq G intersect (E_bar intersect Z_p)(F_p),
```

the bound `|F_p| <= Delta_p` holds. Consequently, for every fixed
`0 < epsilon < 1`, every eventual sequence with

```text
Delta_p^{m_p} <= N^(1-epsilon)
```

has the same fixed-target coverage cap and fresh-rerandomized cost lower bound
as Theorems 2--4 after replacing `3 d_p` by `Delta_p`. This is the theorem's
universal quantifier: it covers every algebraic description admitted by the
explicit intersection-degree interface. It does not assign a subpolynomial
`Delta_p` to an unrestricted description for free.

## Theorem 2: sumset coverage is bounded by tuple count

The elliptic-curve addition map

```text
sigma : F_p^{m_p} -> G,
        (Q_1,...,Q_{m_p}) |-> Q_1 + ... + Q_{m_p}
```

has image `m_p F_p`. An image cannot have more elements than its domain, so

```text
|m_p F_p| <= B_p^{m_p} <= (3 d_p)^{m_p}.
```

This bound does not assume that sums are collision-free. Collisions only make
the reachable target set smaller.

## Theorem 3: min-entropy converts coverage into a success bound

If a distribution `D` on `G` has min-entropy at least `log_2(N) - C`, then for
every subset `A <= G`,

```text
Pr_{T <- D}[T in A]
  <= |A| * max_T Pr[D=T]
  <= 2^C |A| / N.
```

Taking `A = m_p F_p` and applying Theorem 2 gives

```text
Pr[T in m_p F_p] <= 2^C (3 d_p)^{m_p} / N.
```

For a uniform random target, `C=0`.

## Theorem 4: fixed-target coverage and optional rerandomized cost

For a fixed target family, let

```text
q_p = Pr[T in m_p F_p] <= 2^C (3 d_p)^{m_p}/N.
```

This is a one-time support event. Repeating tuple trials from the same fixed
`F_p` does not turn it into independent coverage attempts. Any fixed-target
protocol whose accepted output requires `T in m_p F_p` has success probability
at most `q_p`, regardless of how many tuples it tests. Thus if `q_p < delta`,
constant `delta`-success is impossible in this interface.

For the optional fresh-rerandomization interface, each trial must, conditional
on the complete prior transcript, draw a fresh target-equivalent image with
success probability at most `q_p`, preserve source recovery for the original
challenge, and cost at least one charged group-operation equivalent. If `tau`
is its stopping time, the conditional union bound gives

```text
Pr[success by tau] <= q_p E[tau].
```

Therefore a protocol with success probability at least `delta` has

```text
E[cost] >= E[tau] >= delta/q_p
  >= delta * 2^(-C) * N / (3 d_p)^{m_p}.
```

In particular, for any fixed `0 < epsilon < 1`, if

```text
(3 d_p)^{m_p} <= N^(1-epsilon),
```

then the fixed-target success is at most `2^C N^(-epsilon)`, while the
fresh-rerandomized delta-success cost is at least

```text
delta * 2^(-C) N^epsilon.
```

Giving the algorithm free relation collection, verification, and linear algebra
can only lower the charged cost, so this is a necessary-condition barrier for
the explicitly declared rerandomized descent interface. Without that interface,
the fixed-target coverage cap is the strongest supported statement.

## Corollary: bounded-degree, bounded-arity predicates do not yield
subexponential descent

If `d_p = N^(o(1))` and `m_p = O(1)`, then

```text
(3 d_p)^{m_p} = N^(o(1))
```

and Theorem 4 rules out constant-success fixed-target descent in this interface;
under fresh rerandomization it gives `N^(1-o(1))` expected charged trials. In
the security parameter `n = log_2(N)`, this is `2^(n-o(n))`, not an
`L_N[alpha,c]` cost with `alpha < 1` and not `N^(o(1))`.

Equivalently, any subexponential descent in this model must satisfy the
necessary coverage condition

```text
m_p * log(3 d_p) >= (1-o(1)) log(N).
```

If the algorithm explicitly enumerates ordered tuples, that particular
implementation costs `B_p^{m_p}` tuple operations. The theorem does not equate
this with the cost of computing the distinct image when collisions occur; an
implicit image or membership solver is a separate interface whose setup,
queries, and source recovery must be charged.

## Why this is not the unrestricted theorem

The phrase “algebraically-defined factor base” is too broad without a
complexity interface. The following are deliberate escape routes, not
counterexamples to the four theorems:

1. A high-degree interpolation polynomial can describe an arbitrary finite
   subset; its degree and evaluation/solving cost must be charged separately.
2. A predicate with `f_p|_E = 0` describes all of `E`, so the Bezout premise
   fails and the factor base is not small.
3. A growing-arity method with an implicit solver may avoid explicit
   `m_p`-tuple enumeration; Theorem 2 still bounds the image but not the cost
   of such an implicit solver.
4. Multiple predicates, constructible sets, signed or weighted factors,
   extension fields, special curves, target-dependent bases, and non-sumset
   relation families are not covered by this single-predicate interface.
5. A target-dependent predicate (for example, a line chosen through the public
   challenge) is an explicit counterexample to target-independence, not a
   falsification of this theorem.
6. A relation bank without random-target coverage is not a full ECDLP solver;
   it cannot be used to bypass Theorem 3 by relabelling relation collection as
   descent.

Closing all of these escape routes would require a lower bound for implicit
algebraic membership or a classification of all ECDLP relation mechanisms.
`KN-OPEN-019` records that no such attack-family taxonomy is currently closed.

## Independent review checklist

1. Verify that the plane cubic is irreducible and that `f_p` is not a component
   of it before applying Bezout.
2. Check that affine rational factor-base points are a subset of the projective
   intersection and that multiplicities can only strengthen the bound.
3. Check that the addition-map image has cardinality at most its tuple-domain
   cardinality, including repeated points and the identity.
4. Derive the min-entropy inequality from the maximum point mass, not from an
   unstated uniformity assumption.
5. Check that fixed-target repetition is treated as a static coverage event,
   not as geometric retry success.
6. For the optional rerandomized result, check conditional success, source
   recovery, and the stopping-time inequality `P(success by tau) <= q E[tau]`.
7. Convert `N^epsilon` to the security parameter `log N` before calling it
   exponential rather than subexponential.
8. Confirm that no claim is extended to unrestricted algebraic descriptions,
   extension fields, special curves, or non-sumset relations.

## Disposition

The four theorems are a derivation-level scoped obstruction once the checklist
passes. They do not close the universal prime-field ECDLP question in
`KN-OPEN-001`, do not promote toy relation results into a break, and do not
support a claim that every algebraically described factor base is impossible.
