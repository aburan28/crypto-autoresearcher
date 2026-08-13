# Numeric conditions for total time exponent 1/4

**Task:** TASK-20260805-85af9d · **Goal:** GOAL-SSIQ-001 · **Batch:** BATCH-001
**Depends on:** `exponent_budget.md` §3.4 (the parameterised identity) and
`line_locators.yaml` (the verbatim basis of every factor value).
**Compute used:** none. All arithmetic below is exact rational arithmetic on
the exponents named in `exponent_budget.md`.

---

## 0. Read this first

This file answers exactly one question: **if the total time exponent were to be
`1/4` instead of `1/3`, what value would each named factor have to take?**

It does **not** answer, and must not be read as answering, whether any of those
values is attainable, plausible, near, or worth pursuing. That is
`TASK-20260805-87e568`'s question and the campaign's. A condition is a
*bookkeeping consequence of an equation*; deriving one asserts nothing about
its truth. The string `1/4` does not appear anywhere in the frozen source.

Everything below inherits the four qualifiers of `exponent_budget.md` §0: the
`1/3` baseline is **conditional on Heuristic 1**, its **memory equals its
time**, its **`o(1)` is superpolynomial**, and the cost is an **expectation**.

---

## 1. The equation being solved

From `exponent_budget.md` §3.4, with all quantities base-`p` exponents:

```
TIME    T = c · q · d / k  +  r
MEMORY  M =     q · d / k
```

| symbol | meaning | factor | **frozen source value** | locator |
|---|---|---|---|---|
| `d` | exponent of the degree bound on the minimal isogeny `E → E^{(p)}` | F1 | **1/3** | line 81 |
| `k` | arity of the split of that isogeny | F2 | **2** | lines 167, 177, 181 |
| `q` | exponent of the searched-family cardinality as a power of the per-side degree bound | F3 | **2** | lines 133, 156, 230 |
| `c` | exponent of the collision cost as a power of the per-side cardinality | F7 | **1** | lines 158, 171 |
| `r` | exponent of `P0^{-1}` | F4 | **0** | line 212 |

Baseline check: `T = 1·2·(1/3)/2 + 0 = 1/3` and `M = 2·(1/3)/2 = 1/3`, matching
line 19 (*"expected time and memory p^{1/3+o(1)}"*) and line 39.

**Two constraints that are part of the equation, not commentary:**

- **(C-i) `r ≥ 0`.** `P0` is a probability, so `P0^{-1} ≥ 1`. Line 212 pins
  `r ≤ 0 + o(1)`. Hence `r = 0` exactly and it is bounded below by 0.
- **(C-ii) `T ≥ M`.** An algorithm cannot occupy more memory cells than it takes
  time steps. The source gives the same conclusion directly for this algorithm
  at line 158: *"The cost of computing the list is thus at most
  #L · (B + log p)^{O(1)} ... The cost of the final loop through the table L is
  dominated by that previous computation."* The table must be **built** before
  it is searched.

---

## 2. The whole target, in one number

The product `c·q·d/k` currently equals `1/3`. For `T = 1/4` with `r` at its
floor of 0, it must equal `1/4`:

```
(1/4) ÷ (1/3) = 3/4
```

> **The entire target is one multiplicative movement of `3/4`, placed on `c`,
> `q`, or `d` — or inverted to `4/3` and placed on `k`. It cannot be placed on
> `r`.**

That is the whole arithmetic content of "reach 1/4". Everything in §3 is this
sentence, once per factor.

---

## 3. Per-factor conditions (others held at their source values)

### 3.1 `d` — F1, the structural degree bound

```
T = c·q·d/k + r = 1·2·d/2 + 0 = d
Set d = 1/4.
```

> **Condition F1→1/4: the degree bound would have to have exponent `1/4`,
> i.e. a bound of the form `p^{1/4+o(1)}` in place of `(p/2)^{1/3}`.**

Consequences that follow mechanically and must travel with the condition:

- The per-side bound becomes `X = (B·D)^{1/2} = p^{1/8+o(1)}` (was `p^{1/6+o(1)}`).
- The list becomes `X^{2+o(1)} = p^{1/4+o(1)}`; memory falls to `1/4` as well.
- **The quantifier matters and is part of the condition.** Theorem 1.5 as
  written is universal — line 81: *"Let E be a supersingular elliptic curve over
  a finite field F_{p^2}. Then there exists an isogeny from E to E^{(p)} of
  degree less than or equal to (p/2)^{1/3}."* Algorithm 3 re-randomises, so a
  bound holding for a `p^{-o(1)}` fraction of curves would also suffice, at the
  cost of an extra factor absorbed into `r` — which by (C-i) may only *increase*
  `T`. A bound holding for a `p^{-ε}` fraction with `ε > 0` fixed does **not**
  suffice: it would put `r = ε` and give `T = 1/4 + ε`.
- **This is the CITED-NOT-VERIFIED factor** (reference [4], Aubry–Oyono–Vincent,
  arXiv:2607.14624, not in this repository). The condition is stated about a
  bound whose current proof this program has never checked.

### 3.2 `q` — F3, the searched-family cardinality

```
T = 1·q·(1/3)/2 + 0 = q/6
Set q/6 = 1/4  ⟹  q = 3/2.
```

> **Condition F3→1/4: the searched family would have to have cardinality
> `X^{3/2+o(1)}` where the source has `X^{2+o(1)}` — i.e. the three-quarters
> power of the current list, `p^{1/4+o(1)}` instead of `p^{1/3+o(1)}`.**

In the goal record's L2 notation (`|F| = X^{2-δ}`), this is exactly **`δ = 1/2`**.

Two facts about `q` that constrain how this could be stated:

1. **`q = 2` is pinned two-sidedly for the *full* list.** Upper bound, Lemma 3.2
   (line 133): *"For any X > B > 0, we have #L(E, X, B) ≤ Ψ(X, B)X(log(X) + 2)."*
   Lower bound, §4.1 (line 230): *"This is derived like the upper bound from
   Lemma 3.2, but using that the number of isogenies of degree d is at least d."*
   So **no better counting of `L(E,X,B)` is available**; `q < 2` requires a
   proper sub-family, not a sharper estimate.
2. **Both halves live in the same list.** Line 185: *"We have proved that both
   (E′, ψ) and (E′^{(p)}, χ) are entries in the table L, so the algorithm will
   find a matching entry."* A restriction must therefore retain **both** the
   prefix `ψ` and the conjugated suffix `χ`. The exchange-rate fine structure
   this forces is §4.

### 3.3 `k` — F2, the split arity

```
T = 1·2·(1/3)/k + 0 = 2/(3k)
Set 2/(3k) = 1/4  ⟹  k = 8/3.
```

> **Condition F2→1/4: the split arity would have to be `8/3`, which is not an
> integer. No integer arity yields exactly `1/4`.**

| `k` | `T = 2/(3k)` | decimal |
|---|---|---|
| 2 (the source) | 1/3 | 0.3333 |
| **8/3** | **1/4** | **0.2500** |
| 3 | 2/9 | 0.2222 |
| 4 | 1/6 | 0.1667 |

So `1/4` is not a natural landing point for this factor: integer arities skip
over it, `k = 3` landing below. Three things must be said about this row, all
bookkeeping:

- **The `k ≥ 3` arithmetic is this task's own**, applying the paper's balance
  argument (line 181) with `k` pieces to give `Y = (B·D)^{1/k}`. **The frozen
  text contains no split into three or more pieces and makes no statement about
  one in either direction** (`exponent_budget.md` §6.5).
- The tabulated `T` values assume `c = 1` — i.e. that a `k`-way collision costs
  the same exponent in the per-side cardinality as the 2-way lookup does. **The
  source establishes `c = 1` only for `k = 2`**, and only because of the
  conjugation anchor at line 171. For `k ≥ 3` the value of `c` is not given by
  anything in this text, and assuming `c = 1` there would be assuming the
  question. See addition **A1**.
- Larger `k` also raises the number of unknown intermediate curves from 0 to
  `k − 1`, which is what the anchor question is about.

### 3.4 `c` — F7, the collision mechanism

```
T = c·2·(1/3)/2 + 0 = c/3
Set c/3 = 1/4  ⟹  c = 3/4.
```

> **Condition F7→1/4 (arithmetically): the collision would have to be found in
> time equal to the three-quarters power of the per-side cardinality — sublinear
> in the list.**

**But this row has no admissible solution on its own, and the equation says so.**
By (C-ii), `T ≥ M = q·d/k`. With `q, d, k` at their source values, `M = 1/3`,
so `T ≥ 1/3` regardless of `c`. Setting `c = 3/4` alone would give the
arithmetically inconsistent pair `T = 1/4 < M = 1/3`: an algorithm using more
memory cells than time steps. Line 158 is the concrete form of the same
obstruction — the list is built before it is searched, so the build cost floors
the time at the list size.

> **Derived constraint.** `c < 1` is not usable while the family is
> materialised. And if `q·d/k` has *already* been brought to `1/4` by a `d`, `q`
> or `k` movement, then `c = 1` suffices and `c < 1` buys nothing. Hence the
> `c`-lever is only meaningful in a model where **the family is never
> materialised**, at which point `M` is no longer `q·d/k` and the memory
> accounting must be restated from scratch. This is why L3 has a prerequisite;
> see addition **A3**.

### 3.5 `r` — F4, the inverse success probability

```
T = 1·2·(1/3)/2 + r = 1/3 + r
Set 1/3 + r = 1/4  ⟹  r = −1/12.
```

`r = −1/12` means `P0^{-1} = p^{−1/12}`, i.e. `P0 = p^{+1/12} > 1`.

> **Condition F4→1/4: NONE EXISTS. `r ≥ 0` because `P0` is a probability, so no
> movement of F4 can lower the total exponent by any positive amount.**

This is the one row where the arithmetic does not merely state a condition but
excludes one. It **confirms** the goal record's F4 row and the batch opening's
first consequence, with an argument rather than an assertion. The class it
refutes for free is named in `exponent_budget.md` §4.1; the narrowing that
success-probability work remains *practically* relevant per Remark 1 (line 191)
is in §4.3 there.

---

## 4. Fine structure of the `q` condition: the exchange rate, made checkable

The goal record's L2 asks for *"a restriction that shrinks the list strictly
faster than it shrinks the hit probability"* and names the exchange rate as the
whole question. The identity lets that be stated as a number.

Let `F ⊆ L(E,X,B)` with `|F| = X^{2−δ}`, and let the probability that the
required entries lie in `F` be `X^{−e}`. Since `X = p^{1/6+o(1)}`:

```
T = (2 − δ)/6  +  e/6        ⟹  T = 1/4  ⟺  (2 − δ) + e = 3/2  ⟺  e = δ − 1/2
```

> **Condition L2→1/4, sharpened: the hit-probability loss exponent `e` must fall
> short of the list-shrink exponent `δ` by exactly `1/2`. The goal record's
> requested `e = o(1)` corresponds to `δ = 1/2`, consistent with §3.2's
> `q = 3/2`.**

### 4.1 A null model that makes this cheaply falsifiable

The following is **this task's modelling device for bookkeeping, not a claim of
the paper** — the frozen text says nothing about restricted families. Model
membership in `F` as independent and uniform across the list, with density
`X^{−δ}`. Because *both* `ψ` and `χ` must be present (line 185), there are two
membership events:

| model | `e` | resulting `T` | at `δ = 1/2` |
|---|---|---|---|
| **unaligned** — the two events independent | `2δ` | `(2 + δ)/6` | `5/12 ≈ 0.4167` — **worse than 1/3** |
| **aligned** — `ψ ∈ F ⟹ χ ∈ F` | `δ` | `2/6 = 1/3` | `1/3` — **exact break-even, for every `δ`** |
| required for `1/4` | `δ − 1/2` | `1/4` | `1/4` |

Two consequences, both pure arithmetic:

1. **An unaligned restriction is strictly worse than no restriction**, for every
   `δ > 0`. Shrinking a two-sided search set one-sidedly costs more than it
   saves.
2. **Alignment alone only breaks even.** Under the null model, even a perfectly
   aligned restriction returns `T = 1/3` for all `δ`. To reach `1/4` the
   restriction must be **positively correlated with the sought `ψ`**: it must
   contain the solution with probability `X^{1/2}` times its own density.

> This upgrades L2's cheap pre-compute test. L2 currently proposes measuring the
> *exchange rate*. The equation says the informative measurement is the
> **correlation between the two membership events and the solution** — because a
> measured rate of `e = δ` (alignment) or `e = 2δ` (independence) is the null
> outcome, and both are already visible above as `T ≥ 1/3`. A measurement that
> returns `e ≈ δ` has found the null, not a signal. This is the
> controls-before-belief obligation of `docs/inventor-protocol.md` applied to
> L2's own instrument.

---

## 5. Joint conditions

Any assignment satisfying `c·q·d/k = 1/4` with `r = 0` gives `T = 1/4`. The
constraint set is one equation in four unknowns, so the solution set is a
three-parameter family; representative points, all verified by exact rational
arithmetic:

| # | `d` | `k` | `q` | `c` | `T` | `M` | note |
|---|---|---|---|---|---|---|---|
| — | 1/3 | 2 | 2 | 1 | **1/3** | 1/3 | the source |
| 1 | **1/4** | 2 | 2 | 1 | 1/4 | 1/4 | §3.1: F1 alone |
| 2 | 1/3 | 2 | **3/2** | 1 | 1/4 | 1/4 | §3.2: F3 alone |
| 3 | 1/3 | **8/3** | 2 | 1 | 1/4 | 1/4 | §3.3: non-integer arity |
| 4 | **3/8** | **3** | 2 | 1 | 1/4 | 1/4 | a **worse** degree bound (3/8 > 1/3) with a 3-way split still lands at 1/4 |
| 5 | **1/2** | **4** | 2 | 1 | 1/4 | 1/4 | a much worse degree bound with a 4-way split, likewise |
| 6 | 1/3 | 2 | **7/4** | **6/7** | 1/4 | 7/24 | **INADMISSIBLE**: `M = 7/24 > T = 1/4` violates (C-ii) |
| 7 | **5/16** | 2 | 2 | **4/5** | 1/4 | 5/16 | **INADMISSIBLE**: same violation |

Rows 6 and 7 are kept in the table deliberately. They are what the equation
produces if `c < 1` is used without restating the memory model, and they are
self-refuting — `M > T` is impossible. Recording them is cheaper than
rediscovering them in a proposal.

**Row 4 and row 5 are the structurally interesting ones.** They show the target
does not require improving the degree bound at all: `d` and `k` trade against
each other, and a *weaker* degree bound combined with a deeper split reaches the
same total. Whether the deeper split's collision is findable at `c = 1` is
exactly what the text does not say (§3.3), which is the point of addition A1.

---

## 6. Memory, stated beside time as required

`M = q·d/k` and `T = c·q·d/k + r`, so with `r = 0` and `c = 1`:

> **Every admissible route in §5 takes memory to `1/4` too.** In this
> decomposition, time and memory move together, and they are equal precisely
> because `r = 0` and `c = 1`. `T − M = (c−1)·q·d/k + r`, so the only ways to
> separate them are `c > 1` (spend more time to store less — the van
> Oorschot–Wiener direction, line 39, which raises `T`) or `r > 0` (more
> attempts, which also raises `T`).

Consequently: **no route in this table produces a `p^{1/4+o(1)}` time exponent at
polynomial memory.** A memory result is not a time result and a time result here
is not a memory improvement; both are the same number.

The vOW interpolation the source already gives (line 39) runs the other way:
*"The time-memory tradeoff of van Oorschot–Wiener [43] solves a claw-finding
problem of this size in time essentially √(N^3/w) = p^{1/2+o(1)}/w^{1/2} with
memory w."* With `N = p^{T}`, that curve reads `T_vOW = (3/2)·T − (1/2)·log_p w`,
i.e. `c = 3/2` in the notation of §1 at polynomial `w`.

---

## 7. What this file does not say

- It does **not** say any condition in §3, §4 or §5 can be met. No row is
  ranked, endorsed, called promising, or called hopeless.
- It does **not** say `1/4` is a natural or reachable exponent. §3.3 in fact
  records that integer split arities skip over it.
- It does **not** treat the absence of a stated obstruction in the frozen text
  (`exponent_budget.md` §6) as evidence that no obstruction exists. The text is
  silent, which is neither support nor refutation.
- It does **not** re-derive or restate GOAL-P13-001's concrete-cost findings
  (`EV-PEC-2e67ff`, `EV-PEC-857664`); those are inputs, cited where relevant.
- It assigns **no exponent** to the reductions [35, Theorem 1] and
  [35, Proposition 8.5] behind Corollary 1.2, because this task has not verified
  their cost. Every condition above is stated for **OneEnd over `F_{p^2}`**, the
  object of Theorem 1.1 (Problem 2.2, line 119). Extending any of them to
  EndRing or Isogeny inherits that unchecked dependency.
