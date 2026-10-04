---
id: KN-TECH-54c38e
type: technique
title: Counting K-rational roots of X^{p^{n'}} - lambda(X) without materialising it - the composition-lemma reduction to degree d^k, and the k-selection that makes it cheap
tags: [qsp, quasi-subfield, finite-fields, frobenius, gcd, root-counting, polynomial-composition, cantor-zassenhaus, gf2, characteristic-two, blind-rederivation, instrument, verification, ecc2k-130, methodology]
confidence: established
complexity: >-
  Dominated by deg P = d^k, where k is chosen so that k n' = n + e with e small.
  The two gcds against X^{p^n} - X and X^{p^{n'}} - lambda cost about (n + n')
  modular p-th powerings on polynomials of degree at most d^k, plus two Euclidean
  gcds at that degree. THE DEGREE-p^{n'} OBJECT IS NEVER BUILT: at
  (n, n', d) = (131, 33, <=7) the method replaces a degree-2^33 polynomial by one
  of degree at most 2401 and sweeps all 244 candidates in about 6 seconds. The
  method FAILS, and fails loudly rather than silently, when the minimal admissible
  k is large or d is large, because d^k must remain materialisable.
applicability: >-
  Counting DISTINCT K-rational roots of L = X^{p^{n'}} - lambda(X) over
  K = F_{p^n} when deg L is too large to write down, and producing the root-set
  polynomial itself rather than a bound. Requires lambda's coefficients to commute
  with the Frobenius power used - automatic for lambda over the prime field - and
  requires a k with k n' congruent to a small e modulo n such that d^k is
  affordable. Generalises beyond n prime and beyond the quasi-subfield setting:
  anything of the form "x mapped through a fixed polynomial iterated along a
  Frobenius chain, intersected with the K-rational points" admits the same
  reduction.
source_refs: [KN-LIT-0a321c, KN-LIT-4fe9d2, KN-TECH-080]
internal_refs: [EV-QSP-a6aa4b, DEC-20260917-793ae2, EXP-QSP-33b442, TASK-20260917-5fa7d5, TASK-20260917-52b4e6, H-QSP-5540d7]
added: "2026-09-17"
superseded_by: null
---

## Epistemic status

Two different things are recorded here and they carry different weight.

- **The lemma and the reduction are `established`**: a two-line argument in
  elementary finite-field theory, reproduced in full below, checkable by hand by
  any reader without running anything. Nothing about it is taken on a source's
  word.
- **The instrument's validation is this program's own, from ONE task**
  (`TASK-20260917-5fa7d5`), validated many ways rather than across many
  experiments. The distinction matters and is not smoothed over: the checks
  below include ~2000 brute-force ground-truth comparisons, a disjoint
  re-implementation, two disjoint root checkers, an alternative composition
  depth, a disjoint linear-algebra route, and exact agreement with an
  independently produced archive of different lineage — but they were all
  performed inside one task by one agent.
- **The twisted-coefficient variant is NOT validated here.** Everything measured
  used `lambda` with `F_2` coefficients. See "Limits" below.

## The lemma

Let `K = F_{p^n}`, let `lambda` have coefficients in `F_p`, and let
`L = X^{p^{n'}} - lambda(X)`.

Because `lambda` has prime-field coefficients, `lambda(y)^{p^m} = lambda(y^{p^m})`
for every `m`. So for any root `x` of `L`, applying `sigma^{n'}` repeatedly:

```
    x^{p^{n' k}}  =  lambda^{(k)}(x)          for every k >= 1,
```

where `lambda^{(k)}` is the **k-fold composite** of `lambda` with itself, of
degree `d^k`.

Now pick `k` with `k n' = n + e` (more generally `k n' ≡ e mod n`) for a small
`e >= 0`. For `x` in `K` we have `x^{p^n} = x`, hence
`x^{p^{n'k}} = (x^{p^n})^{p^e} = x^{p^e}`. Therefore **every K-root of `L` is a
root of**

```
    P(X)  :=  lambda^{(k)}(X)  -  X^{p^e},        deg P = max(d^k, p^e).
```

That is the whole idea: the K-rationality condition, which on `L` costs degree
`p^{n'}`, costs only degree `d^k` on `P`.

## The instrument

```
    g  :=  gcd( P(X),  X^{p^n} - X )                      # squarefree; K-roots of P
    G  :=  gcd( X^{p^{n'}} - lambda(X),  g )
        =  gcd( (X^{p^{n'}} mod g) + lambda(X),  g )      # char 2 shown
    N  :=  deg G
```

`G` is squarefree and its root set is **exactly** the root set of `L` in `K`, so
`N` is the exact count of DISTINCT roots and `G` is the root-set polynomial
itself. Both reductions are ordinary polynomial arithmetic: `X^{p^n} mod P` by
`n` modular `p`-th powerings, `X^{p^{n'}} mod g` by `n'` more.

Three properties worth stating because they are easy to get wrong:

1. **Distinctness is free.** Intersecting with `X^{p^n} - X`, which is
   squarefree, makes `g` and `G` squarefree. The method therefore does **not**
   assume `L` is squarefree — and `L` need not be, since `L' = -lambda'(X)` can
   vanish identically (any `lambda` that is a `p`-th power).
2. **The bound and the count are different objects.** `deg P` is an upper bound
   on `N` and is exactly the bound of `H-QSP-5540d7` (A) when `k = q + 1`. This
   instrument computes the **exact** `N`, so it can certify that the bound is
   loose, or attained, at a given candidate. Do not conflate them.
3. **Explicit roots come out of `G`, not out of a search.** `G` factors over
   `F_p` into irreducibles whose degrees divide `n`; for `n` prime only degrees
   1 and `n` occur. Each degree-`n` factor is root-found in `K` by
   Cantor-Zassenhaus with the absolute trace, and the remaining `n - 1` roots are
   its Frobenius conjugates. The **root set** is deterministic even though
   Cantor-Zassenhaus is randomised — only which root is found first depends on
   the stream — so a canonical listing order makes the output seed-independent.

## The worked instance

`K = F_2[z]/(z^131 + z^13 + z^2 + z + 1)` (the ECC2K-130 field of
`RQ-QSP-f9bbdb`), `n' = 33`, `lambda` non-linearized of exact degree 3..7.

`33 × 4 = 132 = 131 + 1`, so `k = 4`, `e = 1`, and

```
    P(X)  =  lambda^{(4)}(X) + X^2,      deg P = d^4 <= 2401.
```

A degree-`2^33` polynomial is replaced by one of degree at most 2401. The full
244-candidate sweep runs in about **6 seconds**.

## Validation evidence

All from `TASK-20260917-5fa7d5` unless stated. Each check is named with what it
would have caught.

| check | scale | what it tests | result |
|---|---|---|---|
| Exhaustive brute force at `n = 7, 9, 11, 13`, **two different irreducible field polynomials each** | ~2000 ground-truth comparisons | the lemma itself, and that the count is presentation-independent | 0 mismatches, on count AND on root set |
| `n = 9, n' = 7` — **composite n**, orbits of size 1, 3 and 9 | included above | that the method does not tacitly assume `n` prime | agrees |
| `n = 13, n' = 5` — minimal `k` is **8**, not 4 | included above | the generic `k`/`e` selection logic, not just the `e = 1` case | agrees |
| `n = 13, n' = 10` — `4 × 10 = 40 ≡ 1 mod 13` | included above | the exact structural mirror of the `n = 131, n' = 33` cell | agrees, including full-orbit cases |
| **Disjoint algorithm** at `n = 131`: `F_2`-rank of the linear map `x ↦ x^{2^33} + lambda(x)` on linearized `lambda` | 8 candidates | the `n = 131`-specific machinery, with **no composition, no superset polynomial, no gcd** | agrees exactly |
| **Alternative composition depth** `k = 8` at `n = 131` (`33 × 8 = 264 ≡ 2`, `P_8 = lambda^{(8)} + X^4`) | all exact-degree 3 and 4, degree-5 spot checks | the reduction itself at target scale on **non-linearized** `lambda` | agrees |
| Translation involution `lambda(X) ↦ lambda(X+1) + 1` | all 248 exact-degree polynomials | a symmetry a buggy sweep would violate | `N` invariant without exception |
| **Full independent re-implementation** in sympy `GF(2)` arithmetic — dense lists, highest-degree-first, foreign multiplication/division/gcd | all 244 candidates | arithmetic bugs in the bit-packed implementation | 0 mismatches; max, argmax and histogram independently reproduced |
| **Two disjoint root checkers** (sympy `galoistools`; from-scratch coefficient-list convolution and long division) reading the *published* vectors | 528 roots | that the emitted roots are roots | 528/528 under each |
| **Exact agreement with an independently produced archive** of disjoint lineage (`RUN-QSP-33b442-S3`, instrument I3, per-orbit closing test) | max `N` = 132, argmax {132, 161, 204, 251}, histogram {0:62, 1:118, 2:60, 132:4}, orbit sizes [1, 131] | the quantity, not the implementation | identical on every one |

The last row is the strongest: two implementations with **no shared code, no
shared method and no shared author**, one of them blind to the other's existence
(`blind_from_respected: true`), returning the same numbers.

**A false pass that was caught, recorded because it is the failure mode this
technique invites.** The first small-case harness silently generated **no** field
polynomials (an inverted parity filter), so the brute-force ground truth never
ran and the script still printed "ALL SMALL CASES OK". A validation harness whose
comparison loop can be empty and still report success is worse than no harness.
Assert the comparison count, not just the mismatch count.

## Limits, stated as flatly as the method

1. **`d^k` must be materialisable, and this is the binding constraint.** The
   method's cost is `deg P = d^k`. Where the minimal admissible `k` is large or
   `d` is large it fails outright — and that regime is not hypothetical: in
   `EXP-QSP-33b442` Stage 2 the analogous construction reached `deg D = 8^16`
   and had to be capped by a declared amendment (`AMD-20260917-001`), leaving 10
   of 65 complete splitters on a single instrument. Check `d^k` **before**
   dispatching, not after a run stalls.
2. **Prime-field coefficients, or carry the twist explicitly.** The step
   `lambda(y)^{p^m} = lambda(y^{p^m})` needs `lambda`'s coefficients fixed by
   the Frobenius power used. For `lambda` in `K[X]` the correct object is the
   **twisted** iterate `Lambda_{k+1} = Lambda_k^{(n')} ∘ lambda` of
   `H-QSP-5540d7` (A), and the same construction works with the twist carried —
   but **no measurement in this entry exercised a non-trivial twist**. Treat the
   twisted variant as unvalidated until someone runs it.
3. **A small `e` is not guaranteed.** `k n' ≡ e mod n` with small `e` and small
   `k` is a property of the pair `(n, n')`, not something that can be arranged.
   When no such `k` exists below the affordability ceiling, this technique has
   nothing to offer and a different instrument is needed.
4. **It counts; it does not certify absence in the other direction.** `N = deg G`
   is exact, but a reader who wants an independently checkable artifact needs the
   root list or the compact certificate below — and a root list detects a FALSE
   root and cannot detect a MISSING one. That asymmetry is the whole of joint J4
   in `TASK-20260917-43701b` and is why the archive it validated is described as
   single-instrument on 720 of 732 rows (`EV-QSP-a6aa4b` boundaries).

## The compact certificate this method yields for free

Worth adopting whenever the output is large. Rather than publishing `N` roots,
publish, per candidate:

- the degree-`n` **minimal polynomial** `q` of each non-trivial Frobenius orbit,
  as a bit-packed integer, plus the `F_p`-roots;
- the assertion `X^{p^{n'}} ≡ lambda(X) mod q`, checkable in the abstract field
  `F_p[X]/(q)` with **no reference to any embedding into `K`**.

A reader confirms `q` is irreducible of degree `n` (so its roots lie in the
unique field of that order) and that the congruence holds, and thereby confirms
`N >= 1 + n · #orbits` without redoing any search. `G = (X or X+1) · q` is then
exactly the root-set polynomial. This is a few hundred bytes where the explicit
list is 131 bits × `N`.

## Why this is worth keeping

The obstruction it exploits is the same one that kills the quasi-subfield attack:
`deg D` caps the K-rational fibre. Read as a cost, that cap is what makes the
factor base useless; read as a resource, **it is what makes an exact census at a
131-bit field affordable at all**. An upper bound that converts an intractable
object into a degree-2401 one is a computational asset, and this entry is the
`resource_check` of `EV-QSP-a6aa4b`'s obstruction block discharged into a
reusable instrument.
