## What is being constructed? — derived algebra

A Solinas prime is presented using a short formula such as
`p = f(m)`, with `m = 2^k` and a sparse integer polynomial `f`.
For the P-192 shape, `f(t) = t^3 - t - 1`.
The deployed P-192 prime uses `m = 2^64`; this experiment uses smaller `m`.
The finite field is still the ordinary field of integers modulo `p`.
The formula supplies a useful presentation; it does not by itself supply
new elliptic-curve endomorphisms or an algorithm for unknown discrete logs.

Now introduce an algebraic number alpha satisfying `f(alpha) = 0` and form
`K = Q(alpha)` (assuming `f` is irreducible). This field has characteristic
zero. Its elements can be expressed as rational linear combinations of
`1, alpha, ..., alpha^(d-1)`, where `d = degree(f)`.
The relation `f(alpha) = 0` lets us simplify products exactly.
For the cubic example, `alpha^3 = alpha + 1`.

Because `f(m) = p`, substitution `alpha -> m mod p` respects this defining
relation: `f(m) = 0 mod p`. More precisely, it defines a ring map
`Z[alpha] -> F_p`. It is NOT a homomorphism from the entire characteristic-zero
field `K` to `F_p`; a field homomorphism would preserve characteristic.
Fractions can be reduced when their denominators are invertible modulo `p`.
For the monic polynomials here, `(p, alpha-m)` is the degree-one maximal
ideal of the order `Z[alpha]` defining this reduction. At good reduction,
the corresponding elliptic-curve reduction respects point addition.

For a curve `E: y^2 = x^3 + A*x + B` with rational coefficients, extending
coordinates from `Q` to `K` can give additional points `E(K)`.
An exact point whose affine coordinates reduce maps to a point on `E(F_p)`.
The implication is useful in this direction. The construction does not
give an efficient way to lift an arbitrary target point of `E(F_p)` to a
small point of `E(K)`.

## A worked example — derived identity, not a measured trial

Choose `f(t) = t^3 - t - 1`, `m = 4`, and `p = f(4) = 59`.
On `E: y^2 = x^3 - x + 3`, the point `(alpha, 2)` satisfies the equation:
`alpha^3 - alpha + 3 = (alpha+1) - alpha + 3 = 4 = 2^2`.
Reduction sends it to `(4, 2)` because
`4^3 - 4 + 3 = 63 = 4 mod 59`.
The curve discriminant is `-16*(4*(-1)^3 + 27*3^2) = -16*239`,
which is nonzero modulo 59, so this curve has good reduction there.
The cubic is irreducible over Q by the rational-root test (neither 1 nor -1
is a root). This small example is below the run's prime-size cutoff and
is used only to explain the map; no rank or torsion claim is made about it.

## Why discriminants enter — derived relation and proposed mechanism

In the real/complex embeddings of a number field, its algebraic integers
form a lattice. Its covolume is `2^(-r2)*sqrt(|disc(K)|)` in the standard
Minkowski embedding, where `r2` is the number of conjugate complex pairs.
A smaller field discriminant can make this lattice denser and motivates
searching for smaller coordinates. The degree-normalized measure used here
is the root discriminant `|disc(K)|^(1/d)`.
That is a motivation, not a guarantee that `x^3 + A*x + B` is a square in K.
The experiment also searches a bounded power-basis coefficient box, which
is not identical to a ball in Minkowski space or a canonical-height ball.

The polynomial discriminant and field discriminant need not coincide:
`disc(f) = disc(K) * [O_K : Z[alpha]]^2`.
The runner records both its exact polynomial discriminant and PARI's
number-field discriminant, using the latter for the regression when
available. This distinction avoids treating an order's discriminant as
the maximal order's discriminant without checking the index.

## What the existing experiment measures — implementation description

For each seeded curve and field, the runner tries coordinates
`x = (a0 + a1*alpha + ... + a_(d-1)*alpha^(d-1))/e`, with integer
coefficient vectors in bounded sup-norm shells and `e` in `{1,2,3,4}`.
Eight auxiliary degree-one primes supply modular square tests. Surviving
candidates receive the library's number-field square-root search; accepted
roots are checked exactly in K. The square-root procedure has bounded
reconstruction effort, so exact verification of accepted points does not
certify completeness of discovery. The run compares the existing search
algorithm across fields, not an exhaustive enumeration of E(K).

The cumulative work count `W` is candidate x attempts. At six recorded
checkpoints through W=100,000, `D(W)` counts distinct affine points reduced
at the designated prime above p. Both signs of a nonzero y can contribute.
The runner fits the slope gamma of `log D` against `log W`, using up to the
last three positive-D checkpoints (at least two are required).
Gamma near zero indicates little additional coverage over that tail;
a larger gamma indicates more growth within this finite search window.
It is not an asymptotic ECDLP complexity exponent.

Controls include random monic irreducible polynomials with the same degree
and number of nonzero coefficients, fields `Q[t]/(t^d-c)` when the toy
prime selector finds one, and Q itself. They use the declared seeds,
curve-generation rule, and search ladder. Degree/weight matching does not
match prime sizes, field isomorphism classes, integral bases, or independent
samples. The seeded random generator samples polynomials with replacement;
repeated polynomial/curve instances are retained in the records.

The runner also reports points it classifies as non-rational and
non-torsion, and the smallest naive logarithmic x-height among those points,
divided by log(p). This height is a coefficient proxy: after clearing
coefficient denominators to a common denominator e, it is
`log(max(e, |a0|, ..., |a_(d-1)|))`. It is not an absolute Weil height
of an algebraic number or a canonical point height. These measurements
do not certify point independence or rank. The rank arm is explicitly
skipped because no number-field descent tool is provided. Point signs and
repeated cells must not be interpreted as independent rank contributions.

For background, the Mordell–Weil theorem describes `E(K)` as a finite
torsion group plus `r` independent integer directions; `r` is the rank.
The points P, -P, and 2P all use one direction. Even a non-rational,
non-torsion point can be a division of a rational point and add no rank
relative to E(Q). Establishing rank gain therefore needs independence
modulo the rational subgroup, not just coordinates outside Q.

## What remains between this and an ECDLP method — proposed research gap

In the special number field sieve for multiplicative discrete logs, small
norms can factor into small prime ideals and produce usable relations.
Elliptic-curve points have an additive group law; small coordinates do not
automatically give an analogous factorization or known-scalar relation.
For this direction to solve an ECDLP, further work must supply affordable
lifts or relations for arbitrary targets, justify relation independence,
and count the full costs of construction and recovery against a baseline.
This experiment measures one ingredient: the existing algorithm's supply
of small number-field points and their finite-field coverage. Neither high
coverage nor low coverage alone establishes a discrete-log algorithm or
rules out all such algorithms.
