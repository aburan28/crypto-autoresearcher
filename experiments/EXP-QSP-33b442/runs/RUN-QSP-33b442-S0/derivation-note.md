# EXP-QSP-33b442 Stage 0 — hand re-derivation note

**Zero compute.** No program was run to produce this file. It is archived
before any Stage 1 run, as `specification.yaml` `stage_0` requires. It
re-derives (i)–(vi) of `H-QSP-5540d7` (A)/(B) by hand, states the symbolic
slices of `proof_search_map.baseline_embedding` and `method_ceiling`
required by `stage_0.content` (vii), and works the two `(n, n') = (4, 3)`
cells by hand so that the Stage 1 run can be required to agree with them.

Executor of `TASK-20260917-892420`. Observations and re-derivation only: this
note decides nothing about whether `H-QSP-5540d7` is supported.

Setting throughout: `p` prime, `K = F_{p^n}`, `sigma` the `p`-Frobenius,
`lambda in K[X]` of degree `d >= 1`, `L = X^{p^{n'}} - lambda(X)`,
`n = q n' + r` with `0 <= r < n'`. For `f in K[X]`, `f^{(k)}` is `f` with
every coefficient raised to the `p^k`-th power. Twisted iterates:
`Lambda_1 = lambda`, `Lambda_{k+1} = Lambda_k^{(n')} o lambda`.
`N_K(L)` is the number of **distinct** roots of `L` in `K`.

---

## (i) `f(z)^{p^k} = f^{(k)}(z^{p^k})`

Write `f = sum_i c_i X^i`. In characteristic `p` the map `u -> u^p` is a ring
homomorphism of the algebraic closure, hence so is `u -> u^{p^k}`. Therefore

    f(z)^{p^k} = (sum_i c_i z^i)^{p^k} = sum_i c_i^{p^k} (z^i)^{p^k}
               = sum_i c_i^{p^k} (z^{p^k})^i = f^{(k)}(z^{p^k}).

Nothing here needs `z in K`; it holds in the algebraic closure. **Re-derives.**
Degrees are untouched: `deg f^{(k)} = deg f`, because `c -> c^{p^k}` is
injective on a field of characteristic `p`, so the leading coefficient stays
nonzero. **This is the only place the coefficient twist does any work, and it
is why the statement extends from `lambda in F_p[X]` to `lambda in K[X]`.**

## (ii) `x^{p^{(k+1)n'}} = Lambda_{k+1}(x)` for every root `x` of `L`

Induction on `k >= 0`. Base `k = 0`: `x` is a root of `L`, so
`x^{p^{n'}} = lambda(x) = Lambda_1(x)`. Step: assume
`x^{p^{k n'}} = Lambda_k(x)`. Then

    x^{p^{(k+1)n'}} = (x^{p^{k n'}})^{p^{n'}}
                    = Lambda_k(x)^{p^{n'}}
                    = Lambda_k^{(n')}(x^{p^{n'}})      [by (i) with k := n']
                    = Lambda_k^{(n')}(lambda(x))       [x is a root of L]
                    = Lambda_{k+1}(x).                 [definition]

**Re-derives.** `deg Lambda_{k+1} = d^{k+1}`, since composition multiplies
degrees and the twist preserves them.

## (iii) `x in K` and `(q+1) n' = n + (n' - r)` give `D(x) = 0`

`n = q n' + r`, so `(q+1) n' = q n' + n' = (n - r) + n' = n + (n' - r)`, and
`n' - r >= 1` because `r < n'`. For `x in K` we have `x^{p^n} = x`, hence

    x^{p^{n'(q+1)}} = x^{p^{n + (n'-r)}} = (x^{p^n})^{p^{n'-r}} = x^{p^{n'-r}}.

Combining with (ii) at `k = q`: every `x in K` with `L(x) = 0` satisfies

    Lambda_{q+1}(x) = x^{p^{n'-r}},   i.e.   D(x) = 0
    where D(Y) := Lambda_{q+1}(Y) - Y^{p^{n'-r}}.

**Re-derives.** Note what is used and what is not: `x` itself is the root of
`D`; **no injection `x -> y` is needed** in this form. The proposal's route
via `y = x^{p^r}` and `H(Y) = Y^{p^{n'-r}} - lambda(Lambda_q^{(r)}(Y))` gives
the weaker *sum* bound `d^{q+1} + p^{n'-r}`. For `lambda in F_p[X]` all twists
are trivial, `Lambda_{q+1} = lambda^{o(q+1)}`, and `D` and `H` coincide up to
sign — the `F_2` form recorded in `CORR-20260916-8d0b81`.

The step `x^{p^n} = x` is the **only** place `x in K` (as opposed to the
algebraic closure) is used, and it is where the hypothesis `n' does not divide
n` will earn its keep in (vi): at `r = 0` the identity still holds but the
degree comparison becomes vacuous.

## (iv) `deg D <= max(d^{q+1}, p^{n'-r})`, hence the bound

`D` is the difference of a polynomial of degree `d^{q+1}` and the monomial
`Y^{p^{n'-r}}`, so `deg D <= max(d^{q+1}, p^{n'-r})`, with equality unless the
two leading terms cancel (which needs `d^{q+1} = p^{n'-r}`). When `D != 0`, a
nonzero polynomial has at most `deg D` roots, and by (iii) every one of the
distinct `K`-roots of `L` is among them:

    N_K(L) <= deg D <= max(d^{q+1}, p^{n'-r}).            (A)

**Re-derives.** The count is of *distinct* roots on both sides, which is the
right reading: `L' = -lambda'`, so when `lambda' = 0` (e.g. `lambda` a square
at `p = 2`) `L` has repeated roots and `deg L = p^{n'}` overstates the size of
the root **set**. It is the set that is a factor base, and it is the set that
(A) bounds.

## (v) The degenerate case `D = 0`

`D = 0` means `Lambda_{q+1}(Y) = Y^{p^{n'-r}}` identically. Comparing degrees
forces `d^{q+1} = p^{n'-r}`, so `d = p^j` with `j (q+1) = n' - r`, and
`j >= 1` because `n' - r >= 1`.

A composition `f o g` of polynomials over a field equals a monomial `Y^m`
only if each factor is (up to translation) a monomial: if `f o g = Y^m` then
for every root `a` of `f`, the polynomial `g - a` has `0` as its only root, so
`g = c Y^e + b` with `a = b`; hence `f` has the single root `b` and
`f = c'(Y - b)^{m/e}`. Applying this along the chain
`Lambda_{q+1} = Lambda_q^{(n')} o lambda` forces

    lambda = c X^{p^j} + b,

and then `L = X^{p^{n'}} - c X^{p^j} - b = M^{p^j}` with
`M = X^{p^{n'-j}} - c' X - b'`, `c' = c^{p^{-j}}`, `b' = b^{p^{-j}}`
(`p`-th powering is bijective on a finite field, so the roots `c'`, `b'`
exist and are unique). Therefore

    N_K(L) = N_K(M) <= deg M = p^{n'-j} < p^{n'}.

**Re-derives.** So the degenerate case is a `p^j`-th power of an affine
binomial of subfield or multiplicative type (Appendix C.2 of `KN-LIT-0a321c`;
Proposition 6 of `KN-LIT-4fe9d2`), it never splits completely **as a set of
distinct roots**, and it is excluded from (A) by hypothesis and covered
separately by the trivial bound. For `d` not a power of `p` the degenerate
case cannot occur at all.

## (vi) The beta corollary

Let `r >= 1` and suppose `L` splits completely in `K` as a **set**:
`N_K(L) = p^{n'}`. By (v) `L` is then non-degenerate, so (A) applies:

    p^{n'} <= max(d^{q+1}, p^{n'-r}).

Since `r >= 1`, `p^{n'-r} < p^{n'}`, so the maximum must be the other term:

    d^{q+1} >= p^{n'},   i.e.   (q+1) l >= n'   with l := log_p d.

Using `(q+1) n' = n + n' - r` from (iii):

    beta := l n / n'^2 >= n / ((q+1) n') = n / (n + n' - r).          (B)

And `n + n' - r < 2n` whenever `n' - r <= n' <= n`, so `beta > 1/2` for every
`n'` not dividing `n`. **Re-derives.**

The proposal's conservative form follows from the weaker sum bound
`d^{q+1} + p^{n'-r} >= p^{n'}`, i.e. `d^{q+1} >= p^{n'} - p^{n'-r} >= p^{n'-1}`,
giving `beta >= n (n' - 1) / (n' (n + n' - r))`, which (B) implies. Both are
computed for every complete splitter in Stage 2, as the contract requires.

Approximate splitting, for completeness: if `N_K(L) >= p^{n'}/c` with `c < p^r`
then `d^{q+1} >= p^{n'}/c` and `beta >= n (n' - log_p c) / (n' (n + n' - r))`.

---

## (vii) The symbolic slices

### `baseline_embedding`

1. **Lemma 4.1 of `KN-LIT-0a321c` is incomparable to (A), not weaker.**
   Lemma 4.1 runs the same chain identity to step `q` and applies `sigma^r` on
   the **right**, giving `q l + r >= n'` for a QSP. (A) runs the chain one step
   further, to `q + 1`, and applies `x^{p^n} = x` on the **left**, giving
   `(q+1) l >= n'`. Neither implies the other: `(q+1) l >= q l + r` iff
   `l >= r`, so (A) is the stronger statement exactly when `l < r` — which is
   the regime `r` close to `n'`, the regime the paper identifies as the
   attacker's best case and the regime `n = 131`, `n' in {33, 44, 66}` sits in
   (`r = n' - 1` there). Together they give `q l + min(l, r) >= n'`.
   *Symbolic check, zero compute; nothing here is measured.*

2. **Tightness slice A — Theorem 1's equality case.** `X^{p^2} + X^p + X` over
   `F_{p^3}`: `n = 3`, `n' = 2`, `lambda = X^p + X`, `d = p`, `q = r = 1`.
   Bound `max(d^{q+1}, p^{n'-r}) = max(p^2, p) = p^2 = N`: **attained**.
   `beta = l n / n'^2 = 1 * 3 / 4 = 3/4`, and the exact corollary is
   `n/(n + n' - r) = 3/(3 + 2 - 1) = 3/4`: **equality**. Agrees with Theorem 1
   of `KN-LIT-4fe9d2`. Run numerically as control C4 at `p = 2` (forced 4).

3. **Tightness slice B — Type 2 at `n = 7`.** `n' = 3`, `lambda = X^2 + X`,
   `d = 2`, `q = 2`, `r = 1`. Bound `max(2^3, 2^2) = 8 = 2^{n'} = N`:
   **attained**. `beta = 1 * 7 / 9 = 7/9`, exact corollary
   `7/(7 + 3 - 1) = 7/9`: **equality**. Run as control C2 (forced 8).

4. **Vacuity slice — `r = 0`.** If `n' | n` then `r = 0`, and the bound reads
   `N <= max(d^{q+1}, p^{n'})`, which is `>= p^{n'} = deg L >= N` for every
   `lambda`: the statement is **vacuous**, as it must be, because its
   conclusion is known false there (Diem's subfield family: `lambda = X`,
   `d = 1`, `N = p^{n'}`, `beta` arbitrarily small). Run as control C1
   (`n = 12`, `n' = 6`, `lambda = X`, forced 64). An argument that excluded
   this object would have proved too much.

5. **The `F_p`-coefficient slice** is the one already re-derived by the
   Coordinator session in `CORR-20260916-8d0b81`; the twist of (i) is what
   carries it to `lambda in K[X]`.

### `method_ceiling`

6. **`n' | n` cannot be certified and is not claimed.** The method is silent
   there by slice 4. At `n = 131` (prime) the only such `n'` are `1` and `131`.

7. **Type 2 at `n = 127` must be ADMITTED, and is.** `n' = 63`, `q = 2`,
   `r = 1`, `d = 2^31`, so `l = 31` and `d^{q+1} = 2^93 >= 2^63 = p^{n'}`:
   admitted with room. Its published quality `beta = 1 - 2^5/63^2 = 0.99194...`
   against the exact corollary `127/(127 + 63 - 1) = 127/189 = 0.67195...`:
   consistent. Not executable here (`deg L = 2^63`); the executable analogue is
   control C3, Type 2 at `n = 31`, `n' = 15`, `d = 2^7`, where
   `d^{q+1} = 2^21 >= 2^15` and the forced count is `32768`.

8. **`n = 129 = 3 * 43`.** At `n' = 43`, `43 | 129`, so `r = 0` and the bound
   is correctly vacuous (the subfield `F_{2^43}` exists). At `n' = 33`,
   `129 = 3*33 + 30`, so `q = 3`, `r = 30`, `n' - r = 3`, and the bound bites:
   `N <= max(d^4, 8)`. The method's ceiling is exactly the divisibility line.

9. **What the method cannot certify:** anything about `n' | n`; anything about
   factor bases that are not root sets of a single `X^{p^{n'}} - lambda`;
   anything about a solver whose cost does not grow with `d` (that is `H1`,
   not tested by this contract); and the isogeny-`L` reading of (D)(iii) if
   `[20]` of `KN-LIT-0a321c` means something other than the two forms named
   there.

---

## The `(4, 3)` hand counts (the Stage 0 numeric gate)

`p = 2`, `n = 4`, `n' = 3`; `q = 1`, `r = 1`, `n' - r = 2`. Bound
`max(d^{q+1}, 2^{n'-r}) = max(d^2, 4)`. `n' = 3` does not divide `n = 4`.
`K = F_16`; the count of *distinct* roots is independent of the model chosen
for `F_16`. Twists are trivial (`F_2` coefficients), so
`Lambda_2 = lambda o lambda`.

### Cell 1: `lambda = X^2 + X + 1`, `d = 2`, bound `max(4, 4) = 4`

    Lambda_2(Y) = (Y^2+Y+1)^2 + (Y^2+Y+1) + 1
                = Y^4 + Y^2 + 1 + Y^2 + Y + 1 + 1        [char 2: (u+v)^2 = u^2+v^2]
                = Y^4 + Y + 1.
    D(Y)        = Lambda_2(Y) + Y^{2^{n'-r}} = (Y^4 + Y + 1) + Y^4 = Y + 1.

`D` is nonzero (non-degenerate) and has the single root `y = 1`, which lies in
`F_2 subset F_16`. **Closing test:** `L(1) = 1^8 + (1 + 1 + 1) = 1 + 1 = 0`, so
`1` is retained.

    HAND COUNTS:  N = 1,  D-roots in K = 1,  slack = 0,  ratio = 1/4.

### Cell 2: `lambda = X^3 + 1`, `d = 3`, bound `max(9, 4) = 9`

    Lambda_2(Y) = (Y^3 + 1)^3 + 1
                = (Y^6 + 1)(Y^3 + 1) + 1                 [(u+v)^2 = u^2+v^2]
                = Y^9 + Y^6 + Y^3 + 1 + 1
                = Y^9 + Y^6 + Y^3.
    D(Y)        = Y^9 + Y^6 + Y^3 + Y^4 = Y^3 (Y^6 + Y^3 + Y + 1).

`deg D = 9`, nonzero. Its roots in `K = F_16`: `Y = 0` (from the factor `Y^3`,
one *distinct* root); and in the second factor, `Y = 1` gives
`1 + 1 + 1 + 1 = 0`, so `Y = 1` is a root. The remaining roots of
`Y^6 + Y^3 + Y + 1` lie outside `F_16`; concretely `F_16^* ` has exponent 15,
so any `y != 0` in `K` satisfies `y^{16} = y`, and the two `F_2` elements are
the only candidates that can be checked by hand — which is what the numeric
gate requires the instrument to confirm.

**Closing test:** `L(x) = x^8 + x^3 + 1`. `L(0) = 0 + 0 + 1 = 1 != 0` —
discarded. `L(1) = 1 + 1 + 1 = 1 != 0` — discarded.

    HAND COUNTS:  N = 0,  D-roots in K = 2,  slack = 2,  ratio = 0.

Both cells satisfy (A) with room. **These two lines — `N = 1` with slack `0`,
and `N = 0` with slack `2` — are what the Stage 1 run must reproduce with all
three instruments; a disagreement is `F0` and stops everything.**

---

## What this note does NOT do

It does not measure anything, it does not read any number from
`analysis/qsp-ecc2k130/explore/`, and it does not conclude that
`H-QSP-5540d7` is supported, refuted, or anything else. Whether (A) and (B)
survive the numerical stages, and what that is worth, is a Coordinator
decision on a later review round.
