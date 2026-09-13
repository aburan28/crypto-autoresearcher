# Validator report — TASK-20260913-da3982

**Round:** REVIEW-SEMBIN-20260913-9d649f
**Joints owned:** J1 (Semaev's memory model) and J4 (the exponential-versus-polynomial
mechanism of CLAIM B), plus the four proves-too-much objects.
**Joints NOT owned and not addressed:** J2, J3, J5, J6.
**Runs under review:** RUN-SEMBIN-121b59 (EXP-SEMBIN-f4a17b), RUN-SEMBIN-aa5161
(EXP-SEMBIN-81dc96), both validated from the Coordinator-committed snapshot
`04f15d7f1`.

## Verdicts

| joint | verdict | rests on |
| --- | --- | --- |
| J1 — Semaev's memory model | **holds**, with one material undisclosed assumption quantified | `work/j1_memory_from_text.py`, `work/j1_memory_from_text.json` |
| J4 — exponential-vs-polynomial mechanism | **holds**, with more support than the record itself supplies | `work/j4_mechanism.py`, `work/j4_mechanism.json` |
| proves-too-much, objects 1–4 | all four executed; **all four returned the known-false-refuting answer** | `proves-too-much.json`, `work/objects.py`, `work/objects_raw.json` |

Neither verdict says the algorithm works, and neither bears on Assumption 1,
on eq. (11)'s realism, or on the security of any curve. Confirming an
accounting is not evidence that the thing accounted for is a threat.

---

## J1 — Semaev's memory model: **holds**

### The joint as written mis-describes the record at four points

Before attacking the model I had to establish what the model *is*, and the
joint statement in `review-plan.yaml` does not describe the accounting the
record implements. All four discrepancies are in the plan, not in the record.

1. **The variable count.** The plan and the task card both give
   `N = m*k + 2n`. That is not the variable count; it is the *relation-store
   row width*, a different quantity used a few lines earlier in the same
   function. The record uses `N = (m-2)n + km`, which is Section 4.2's own
   count ("a system of (m-1)n multivariate equations in (m-2)n + km ≈ (m-1)n
   variables in F_p") and Section 4.5.1's ("n(t-1) coordinate equations in
   n(t-2) + kt variables"). The plan's formula is off by a factor of three:

   | (n, m) | plan's `m*k + 2n` | Section 4.2's `(m-2)n + km` | record asserts |
   | --- | --- | --- | --- |
   | (310, 10) | 930 | **2790** | 2790 |
   | (409, 11) | 1236 | **4099** | 4099 |
   | (571, 12) | 1718 | **6286** | 6286 |

   **J1(c) answered: the record's 2790, 4099 and 6286 are correct** for a
   `t = m` chain, re-derived here from Section 4.2 without reading the
   producer's code first.

2. **max versus sum.** The plan says peak memory is `max(store, working set)`.
   `memory_charged_cost.py` computes `log2_add(...)`, i.e. a **sum**. See J1(d)
   below: the sum is the correct charge and the difference is numerically nil,
   so this is a documentation defect with no consequence — but the run manifest
   also calls it a maximum (`overestimating_factors_semaev`), so the record
   describes itself wrongly in the direction that would understate its own
   conservatism.

3. **The sparse reading.** The plan says "sparse reading width bits". It is not:
   it is `(nm)^4/24` columns × `n^3/m` nonzeros per row, which at (409, 11) is
   66.53 bits against a width of 43.42 bits — a 23.1-bit difference. A reviewer
   who audited "width bits" would have audited nothing in the record.

4. **The attribution.** CLAIM A as quoted in the plan says the shift is
   "attributable to Semaev's *relation store*". Under the record's own model the
   relation store is **never** the peak term: `raw-result.json` records
   `memory_dominant_term: "working_set"` at all five FIPS labels, and my
   independent accounting agrees (store 32.9–58.7 bits against a sparse working
   set of 54.4–69.8 bits). The run manifest itself says only "Semaev's own
   memory", which is right; the plan's paraphrase is what is wrong. The
   matched-null control establishes *not the baseline*, which is a weaker
   statement than *the relation store*.

I therefore audited the model as implemented and recorded, not as stated.

### (a) What the frozen text says is stored

Reading Sections 3, 4.2, 4.3, 4.5, 4.5.1 and 4.5.2 in full:

- **The relation store is textually fixed.** Section 3 step 3: "At most |V|
  relations (7) are necessary on the average", and Section 4.5 fixes
  `|V| = 2^k`, `k = ceil(n/m)`. Section 4.5.2 repeats it: "collecting a system
  of ≤ 2^k, k = ceil(n/m) linear relations (7)". A relation carries at most `t`
  factor-base entries of `k` bits each plus the pair `(u, v)` at `n` bits each,
  hence `m*k + 2n` bits per row at `t = m`. The record's row width is supported.
- **The paper names memory as a difficulty and then drops it.** Section 4.2:
  "The problem of generating such a system and keeping it in computer memory
  before solving is difficult by itself for m ≥ 4 and the difficulties increase
  rapidly for larger m." Tables 1–2 (Section 4.5.1) report "overall amount of
  memory in MB used for solving 100 systems". Section 4.5.2, eqs. (15)–(17) and
  Table 3 carry **no memory column at all**. So the paper states that memory is
  the hard part, measures it at n ≤ 40, and then omits it from the claim. That
  is exactly the gap KN-OPEN-86e7e1 opened, and the record fills it rather than
  inventing it.
- **The Galbraith objection was NOT answered with a count this record should be
  using instead.** From KN-LIT-e77232: Galbraith's memory objection is
  `C(N+3,4)^2` entries with `N = (m-1)n`, giving ≥ 2^91 bits at n = 571, m = 12.
  Semaev's reply supplies a *sparsity* count — about `n^3/m` monomials per
  equation and `(nm)^4/4!` for the whole system, hence about 2^70 bits — plus a
  robustness argument (the method still beats Pollard even at regularity degree
  6 with ω = 3). He does not supply a substitute peak-memory figure.
  **The record already uses both counts**: its dense reading *is* Galbraith's
  formula and its sparse reading *is* Semaev's. There is no third count owed.

### (b) Is the dense `width^2` reading defensible? **Yes — and the Coordinator's prior is wrong here**

The Coordinator's recorded prior is that `width^2` "is not a reading Semaev's
own text supports at all", that the honest dense figure is a
sparse-times-fill-factor estimate, and that the 435 crossover and the n = 409
flip should go with it. I find the opposite, on three independent grounds.

1. **It is a named participant's published formula, and it reproduces exactly.**
   Deriving it from the frozen text alone — Section 4.2's variable count, the
   degree-≤4 Boolean monomial count under Assumption 1, squared — I get the
   record's dense figure at **all five FIPS labels to 0.0000 bits**:

   | n | m | N | width (log2) | my dense total | record | Δ |
   | --- | --- | --- | --- | --- | --- | --- |
   | 163 | 7 | 983 | 35.1763 | 70.3526 | 70.3526 | 0.0000 |
   | 233 | 9 | 1865 | 38.8733 | 77.7467 | 77.7467 | 0.0000 |
   | 283 | 9 | 2269 | 40.0051 | 80.0103 | 80.0103 | 0.0000 |
   | 409 | 11 | 4099 | 43.4186 | 86.8371 | 86.8371 | 0.0000 |
   | 571 | 12 | 6286 | 45.8863 | 91.7726 | 91.7726 | 0.0000 |

   The n = 571 row, 91.77 bits, is Galbraith's 2^91. A straw reading is one no
   participant holds; this is the number the objection was actually made with.

2. **It is the memory counterpart of the time bound the record leaves
   unchanged.** Section 4.5.2 states the F4 solving cost as `[n(m-1)]^{4ω}`.
   With `N ≈ (m-1)n` and `W = Θ(N^4/4!)` the degree-≤4 monomial count, that is
   `W^ω` up to a constant — i.e. Semaev's own time bound is dense linear algebra
   with exponent ω on a **W × W** matrix, and ω = 3 (the record's and Table 3's
   value) is Gaussian elimination on a dense square matrix. The memory of that
   object is `W^2` bits. Charging `W^ω` time while charging only `W^1`-ish memory
   is the internally *inconsistent* pairing; the dense reading is the consistent
   one. Semaev's own rebuttal reinforces this: he proposes XL with block
   Wiedemann, and XL at degree 4 requires rank ≈ W for the linear-algebra step
   to determine the solution, which is precisely a W × W matrix.

3. **The sparse reading shares the same square-matrix assumption.** The record's
   sparse figure is `#columns × #nonzeros-per-row`, which equals total nonzeros
   only if `#rows = #columns`. KN-LIT-e77232 says so on its face ("with row count
   of the order of the column count"). So the two readings bracket a dispute
   about *density*, not about *shape*, and neither is a straw relative to the
   other.

My independent sparse figures come out **0.44–0.86 bits below** the record's at
every FIPS label. The whole difference is the column count: the record uses
Semaev's `(nm)^4/24`, I used the width from Section 4.2's `N = (m-2)n + km`.
Both are defensible; the record's is the one Semaev stated. Well inside the
5-bit threshold, so not a break.

### The one material finding: an undisclosed square-matrix assumption, worth 8.9–12.5 bits

Both readings presuppose W rows. The frozen text bounds the row count well
below that. The degree-≤4 part of the ideal is spanned by `f_i · (monomials of
degree ≤ 4 − deg f_i)`; Section 4.5 gives `deg_{F2} S3(x1,x2,x3) = 3` for the
interior chain equations and `deg_{F2} S3(x1,x2,z) = 2` for the final one with
`R_X` constant, so the reachable row space has dimension at most
`(m-2)n(1+N) + n(1+N+C(N,2))`. That is an **exact** bound on the rank, not a
guess:

| n | width W (log2) | reachable rows (log2) | inflation | record dense | dense at the true shape | record sparse | sparse at the true shape |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 163 | 35.18 | 26.25 | 8.93 | 70.35 | 61.42 | 55.28 | 45.49 |
| 233 | 38.87 | 28.61 | 10.27 | 77.75 | 67.48 | 59.97 | 49.03 |
| 283 | 40.01 | 29.45 | 10.56 | 80.01 | 69.46 | 61.94 | 50.72 |
| 409 | 43.42 | 31.68 | **11.73** | 86.84 | **75.10** | 66.53 | 54.28 |
| 571 | 45.89 | 33.40 | 12.49 | 91.77 | 79.28 | 70.27 | 59.19 |

**Why I do not call this a break, and what the Coordinator should do with it.**
Read literally, J1's breaking artifact ("a memory accounting derived from the
frozen text that differs from the record's by more than 5 bits at any FIPS
label, with the section it comes from") is satisfied: 11.73 bits at n = 409
under the dense reading, from Sections 4.2 and 4.5. But that accounting
describes a **different object** — F4's actual working set, whose elimination
cost is also far below `W^ω`. Substituting it while leaving the time model at
`W^ω` would tighten memory and not time, which is incoherent and would make the
comparison *kinder* to Semaev than either published estimate. Since the record's
declared design is to leave Semaev's time model unchanged so that memory is the
only added axis, `W^2` is the memory the record must charge.

So the honest disposition is an **additive limitation, not a correction**: both
storage readings inherit a square-matrix idealisation from the published
dispute; correcting it requires correcting the time model in the same direction;
uncorrected it inflates both memory readings by 8.9–12.5 bits, and the direction
is that the record **understates** Semaev. The record's
`overestimating_factors_semaev` flags over-charging on *density* but not on
*shape*, and does not quantify either. It should carry this number.

For the Coordinator's composition, the consequence if it were applied to memory
alone: the n = 409 dense time-memory margin moves from −8.79 to about +2.94
bits, both readings then put Semaev ahead at n = 409, and the "46.6-bit swing
straddling zero" stops straddling zero. That is a real sensitivity and it should
be recorded as such. It is not a defect in the arithmetic and it is not, on my
reading, a licence to retire the 435 crossover.

### (d) MAX or SUM? **They overlap in time, so SUM is right — and the code already sums**

Section 3 step 3 loops over fresh `R` values, solving a system (5) for each and
appending relation (7) on success, and Section 3 step 4 (the linear algebra)
runs only afterwards. So the store *accumulates while stage 1 is still solving*:
the two live simultaneously and the honest charge is a sum. `log2_add` is
therefore correct, and the plan's and the manifest's description of it as a
maximum is what is wrong.

Numerically it makes no difference at all, because the working set dominates by
18.6 bits (sparse, n = 163) to 38.6 bits (dense, n = 409): the sum exceeds the
max by between 0.0000000 and 0.0007 bits across the five labels. The relation
store never binds. A reader should not conclude from CLAIM A that the store is
the operative memory cost — the Gröbner working set is, under both readings, at
every FIPS label.

---

## J4 — the exponential-versus-polynomial mechanism: **holds**

### (a) The yield-loss scaling, re-derived, and the regime boundary

From Section 4.3 alone: `K ≈ |V|^t/t!`, `P = 1 − (1 − 1/q)^K ≈ 1 − exp(−x)` with
`x = |V|^t/(q·t!) = 2^{tk−n}/t!`. Section 4.3 states the small-argument case
itself: "If |V|^t/(q t!) = o(1), then P ≈ |V|^t/(q t!)".

In that regime `log2 P = tk − n − log2 t!` exactly, so the yield loss from one
unit of chain shortening is

> **k − log2 t bits per unit of t.**

**The plan has the regime boundary backwards.** It says "near tk = n the
exponential collapses to a linear term and the argument's premise fails there".
`P ≈ x` — linear in `x` — is precisely where the mechanism is *strongest*: it is
where `log2 P` tracks `tk` bit for bit. The premise fails in the **saturated**
regime `x ≳ 1`, where `P → 1` and shortening the chain costs no yield at all.

Sweeping `n ∈ [250, 600]`, `m ∈ [2, 20]`, `t ∈ [2, m]`, both `k` readings
(23,660 cells):

- **`x ≥ 1` (saturation) occurs in 175 cells, and only at `m = 2, t = 2`** with
  the ceiled `k` and odd `n`, where `2·ceil(n/2) − n = 1` and `log2 2! = 1` give
  `x = 1` exactly. `m = 2` is never within 7 of the optimal `m` anywhere in the
  sweep, and its stage-1 cost is astronomically worse.
- `x ≥ 0.1` (where the linearisation is off by more than 5%) occurs only at
  `m ∈ {2,3,4,5}`.
- **At the optimal `m`, the largest `log2 x` anywhere in the sweep is −10.469**,
  i.e. `x ≤ 7·10^-4`. `P ≈ x` holds to four significant figures at every `n`
  that matters.

**Answer to (a): no `(n, m, t)` in the swept range at or near the optimal `m`
sits in the regime that breaks the premise.** The boundary is touched only at
`m = 2`, and the mechanism is exponential in the chain length everywhere it is
used.

Yield loss per unit of `t`, at the optimal `m` with ceiled `k`, re-derived:

| n | m* | k | yield loss per unit of t (bits) |
| --- | --- | --- | --- |
| 163 | 7 | 24 | 21.19 |
| 233 | 9 | 26 | 22.83 |
| 283 | 9 | 32 | 28.83 |
| 409 | 11 | 38 | 34.54 |
| 571 | 12 | 48 | 44.42 |

**Two precision defects in CLAIM B's own wording**, both in the direction of
understating its own case:

1. "**25–28 bits per unit of t at the FIPS labels**" is not the range at the
   FIPS labels. The record's own `mechanism` block gives 24.978 (n = 283),
   27.678 (n = 310 — not a FIPS label), 37.578 (n = 409), 53.778 (n = 571). The
   quoted range is the two smallest rows. The true range is 25.0–53.8 under the
   record's convention and 21.2–44.4 under mine.
2. "**Exponential in n**" is loose. The loss is `2^{Θ(k)}` with
   `k = ceil(n/m)` and `m ≈ sqrt(2 ln2 · n / ln n)`, so it is
   `2^{Θ(sqrt(n log n))}` — subexponential in `n`, superpolynomial. The
   comparison CLAIM B needs is superpolynomial-versus-polynomial and it holds;
   "exponential in n" should be corrected to keep the record consistent with
   the paper's own eq. (17).

### (b) Is any solving-cost saving exponential in (m − t)? **No, under all three of the paper's readings**

| n | m* | block_n4w | f4_std | macaulay4 | yield loss |
| --- | --- | --- | --- | --- | --- |
| 163 | 7 | 0.000 | 3.156 | 3.655 | 21.19 |
| 233 | 9 | 0.000 | 2.312 | 2.589 | 22.83 |
| 283 | 9 | 0.000 | 2.312 | 2.588 | 28.83 |
| 310 | 10 | 0.000 | 2.039 | 2.257 | 27.68 |
| 409 | 11 | 0.000 | 1.824 | 1.999 | 34.54 |
| 571 | 12 | 0.000 | 1.650 | 1.795 | 44.42 |

(bits saved per unit of `t`, `ω = 3`.) The record's "2–3 bits" is right in
substance; the honest range across the FIPS labels is **1.65–3.66 bits**, so the
quoted "2–3" understates the spread at both ends.

The *total* saving available, from `t = m` down to `t = 2`, is what decides
whether the saving can be exponential in `(m − t)`. Under `f4_std` it equals
`4ω·log2(m−1)` **exactly** — I confirmed the closed form against the swept
values to three decimals at all six `n` (31.020, 36.000, 36.000, 38.039, 39.863,
41.513). Since `m = Θ(sqrt(n/log n))`, that is `n^{2ω}` up to logs:
**polynomial in n, and a factor `(m−1)^{4ω}` in `(m−t)`, not an exponential.**
`macaulay4` gives 52.4–72.5 bits total, also polynomial. `block_n4w` gives zero
because Section 4.5.2's preferred `n^{4ω}` carries no `t`.

Against total yield losses of 108.7–452.2 bits, the largest available saving is
short by a factor of **2.1× (n = 163) rising to 6.2× (n = 571)** — the margin
*widens* with n. No reading in the frozen text is exponential in `(m − t)`, and
Assumption 1 forecloses the one route that could produce one: it fixes
`d_F4 ≤ 4` uniformly for all `2 ≤ t ≤ m`, and Section 4.5.1 observes "For t < m
the maximal total degree was smaller or equal to 4", so the degree does not grow
as the chain shortens.

### Reconciling "drops dramatically" with "2–3 bits" — reconciled, quantitatively

This is the part of J4 I expected to break and it does not. Table 2 is the only
published measurement of the short-chain tradeoff, and I used it as data the run
never touched.

| n | m | t → t′ | measured drop | f4_std predicts | macaulay4 predicts | yield loss | net per relation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 15 | 4 | 4→3 | 7.75 | 7.02 | 9.32 | 1.96 | **+5.80** |
| 15 | 4 | 3→2 | 8.52 | 12.00 | 21.00 | 2.44 | **+6.08** |
| 15 | 5 | 5→4 | 3.75 | 4.98 | 6.22 | 0.69 | **+3.07** |
| 15 | 5 | 4→3 | 8.58 | 7.02 | 9.79 | 0.97 | **+7.61** |
| 15 | 5 | 3→2 | 5.82 | 12.00 | 23.48 | 1.53 | **+4.29** |
| 16 | 4 | 4→3 | 8.33 | 7.02 | 9.42 | 1.99 | **+6.35** |
| 16 | 4 | 3→2 | 8.48 | 12.00 | 21.63 | 2.44 | **+6.04** |
| 19 | 3 | 3→2 | 13.87 | 12.00 | 18.35 | 4.97 | **+8.89** |
| 21 | 3 | 3→2 | 13.78 | 12.00 | 19.20 | 5.34 | **+8.44** |

(bits; "net per relation" positive means the **shorter** chain is cheaper per
relation.) Three things follow.

1. **"Dramatically" is real, and at those parameters `t < m` genuinely pays** —
   in **9/9** rows, by 3.07 to 8.89 bits per unit of `t`, and by 8.4 to 15.0
   bits end to end from `t = m` to `t = 2`. Semaev's Section 3 step 3 remark
   ("One can probably win in efficiency and lose in probability. Though the
   trade off may be positive") is, at his own experimental parameters, correct.
2. **"Dramatically" and "2–3 bits" are the same model at different `m`.** The
   per-unit saving is `((t−1)/(t−2))^{4ω}` ≈ `4ω·log2(e)/(m−2)` bits, which is
   ~12 bits at `m = 3` and ~1.7 bits at `m = 12`. The measured drops are
   reproduced by `f4_std` to within 0.73–6.18 bits with no consistent sign
   (measured exceeds predicted in 4/9 rows, falls short in 5/9). So the
   polynomial model *predicts* "dramatically" at small `m` rather than
   contradicting it. **Reconciled; I do not have to report that I cannot.**
3. **The sign reverses because `k` grows, not because the solving model
   changes.** Yield loss per unit of `t` is `k − log2 t`, and `k` is 3–7 in
   Table 2 against 24–48 at the FIPS labels, while the solving saving per unit
   of `t` *shrinks* as `m` grows. Two curves cross between `n = 21` and
   `n = 250`. **CLAIM B is therefore true in the large-k regime and false in the
   only regime that has ever been measured** — and its scope statement should
   say so in those terms, because "t = m is optimal under his own cost model at
   concrete n" reads as though it covered Tables 1–2 as well.

One model-free robustness number, since (3) invites an extrapolation objection:
the largest per-unit solving drop ever measured is 13.87 bits (n = 19, m = 3).
Holding that constant against `m` — an extrapolation every solving model in the
paper contradicts, since all of them shrink with `m` — `t < m` still loses by
20.7 bits per unit at n = 409 and 30.5 bits at n = 571. So no reading of the
measured data, however aggressive, makes `t < m` pay at the FIPS labels under
eq. (11).

### (c) Does the optimizer genuinely sweep t? **Yes**

The `known_false_t_independent_solve` control could indeed have passed for a
trivial reason: it forces `t* = m*` using Semaev's own `t`-free `n^{4ω}`, so a
`t`-blind optimizer would pass it. Object 4 rules that out, and does more than a
binary check — the flip to `t* = 2` occurs between an exponential rate of
`0.9·k` and `1.0·k`, and the independently derived break-even rate is just under
`1.0·k`. The optimizer is trading `t` against the yield term with the correct
sensitivity, not merely enumerating it. The `t`-slice at `m*` for n = 409 carries
8 distinct costs, monotone in `t`. Details in `proves-too-much.json`.

### Where J4 is scoped, and where it is not closed

The record's own limitation is the right one and I confirm it: everything above
is **under the published yield law**. eq. (11) is a random-mapping model
(Section 4.3: "we adopt the following model. For random z the mapping ... is a
symmetric random mapping"), and Table 2's experimental probabilities sit below
the theoretical ones in most rows. If eq. (11) overstates realized yield more at
`t = m` than at `t < m`, the comparison inverts. CLAIM B should be stated as
"under eq. (11)" rather than flatly, which is what the record's
`what_this_does_not_close` already says.

---

## The four proves-too-much objects

All four executed; all four returned the known-false-refuting answer. Full
detail, including the objects the producer had not run, is in
`proves-too-much.json`.

| object | known-false conclusion | required signature | outcome |
| --- | --- | --- | --- |
| 1 — n = 163 | "the chain beats rho at n = 163" | Semaev loses under every metric and both readings | **PASS** — 0/8 cells win; margins −42.4 to −73.9 bits; and 4/4 printed Table 3 rows below n = 300 have stage 1 above 2^{n/2} |
| 2 — eq. (4) | "eq. (4) is competitive" | catastrophically worse | **PASS** — 328 to 1257 bits worse in time, under a *more generous* reading of eq. (4) than the producer's (first fall degree m²+1 from Section 4.5, not 2^{m−1}) |
| 3 — free-yield null (**new**) | "a free lunch makes the attack worse" | crossover must move DOWN | **PASS** — down in 16/16 CLAIM A cells (by 57 to 110 in n) and 3/3 CLAIM B readings (by 106 to 217). No inverted sign convention. |
| 4 — solving cost exponential in (m−t) (**new**) | "t* = m*" | t* < m* | **PASS** — t* = 2 at every tested n once the rate exceeds the yield-loss rate, with the flip at the predicted threshold |

Two notes the Coordinator should carry.

**Object 2 has narrow teeth.** A 328–1257 bit margin cannot fail at
cryptographic parameters. A *failing* eq. (4) control would require the
degree-bounded width at degree `m²+1` in `m·k` variables to come within a factor
of degree 4 in `(m−2)n+km` variables — which happens only at small `m` and small
`n`. So the control detects a machinery that has lost its degree dependence
entirely, and nothing subtler. It should be read as a smoke test. It does not
discharge the prime-field control that D1 records as owed; whether that
substitution is adequate is J6, which I do not own.

**Object 3 also bought a bonus check.** Re-running the producer's crossover scan
over `n ∈ [150, 900]` instead of the record's `[250, 650]` returned 303, 375 and
435 unchanged. The three headline crossovers are not artifacts of the sweep
window.

**One control the run does not have, which I added and which passes.** A cost
model that returns `t* = m*` everywhere must still agree with the paper's own
measurement at the parameters where it was made. Evaluating the producer's
`macaulay4` model at the five Table 2 parameter sets with `t < m` rows, the model
puts the argmin at `t = 2` in 5/5, and the measurement agrees in 5/5. The model
*overstates* the magnitude (36.4 bits predicted against 15.0 measured at
n = 15, m = 5), so it is biased **toward** finding an interior optimum — and it
still returns `t* = m*` at every `n ≥ 250`. That is a one-sided robustness
statement in CLAIM B's favour and it is the only place CLAIM B's model can be
confronted with data.

---

## Artifact and receipt checks

| check | result |
| --- | --- |
| snapshot committed before review | yes — `04f15d7f1`, "experiments: archive the two SEMBIN derivation runs (snapshot before review)"; `git status` clean for both experiment trees |
| recorded sha256 digests verify | RUN-SEMBIN-121b59 9/10, RUN-SEMBIN-aa5161 8/9 (see below) |
| command, revision, dirty-tree state recorded | yes; `dirty: true` with the three untracked paths enumerated and explained |
| seeds | `null`, declared seedless deterministic; consistent with the code (no RNG anywhere) |
| environment and dependencies | recorded; standard library only, confirmed by reading both scripts' imports |
| resource records | wall 0.44 s / 1.9 s, cpu, peak RSS, caps, `within_budget: true` |
| inference block | `fallback_used: true` with reason; `model_verified: false` with reason; `independent_session: false` **declared** for both runs |
| certificate | `kind: none`, correct — nothing is solved, so nothing is certifiable under `docs/claims-and-verification.md` |
| controls declared vs reported | CLAIM A 6/6 with `prime_field_control: NOT RUN -- substituted` stated on the face of the manifest; CLAIM B 5/5 |
| preregistered prediction recorded and scored | yes, and **refuted**: EXP-SEMBIN-81dc96 preregistered `t* < m*` strictly and the run records `prediction_refuted: true`, `coordinator_prior_was_wrong: true`. Recording a refuted prior in its own artifact is the behaviour the protocol asks for. |

Two minor artifact-integrity gaps, neither material:

1. `artifact-digests.json` lists a sha256 **for itself**, which cannot match by
   construction (that is the one "mismatch" in each run). Benign but it means
   each run ships one digest entry that is guaranteed wrong; a future wrapper
   should omit the self-entry.
2. `manifest.yaml` is **not** in either digest set, so the manifest — the file
   carrying every claim — is the one artifact not hash-bound to the run. It is
   covered by the commit, so this is a belt-and-braces gap rather than an
   integrity failure.

---

## What I re-derived, and what I took on trust

**Re-derived independently from `inputs/SEMAEV-2015-310/` before reading the
producer's implementation of the same quantity:**

- the variable count `N = (m-2)n + km` at (310,10), (409,11), (571,12) — Section 4.2, Section 4.5.1;
- the optimal `m` at all five FIPS labels (7, 9, 9, 11, 12) from eq. (15);
- the relation-store size and row width — Section 3 step 3, Section 4.5;
- the degree-≤4 Macaulay width and its square, reproducing all five dense memory figures **to 0.0000 bits**;
- the sparse memory figures, reproducing them to within 0.44–0.86 bits, with the residual traced to `(nm)^4/24` versus `W`;
- the reachable degree-≤4 row count, from Section 4.5's degree statements — a quantity the record does not carry;
- eq. (11)'s yield-loss scaling, its per-unit-of-`t` value, and its regime boundary over 23,660 cells — Section 4.3;
- the solving saving per unit of `t` under all three readings, and the exact closed form `4ω log2(m−1)` for `f4_std` — Section 4.5.2;
- eq. (4)'s width and cost gap at the first-fall degree `m²+1` — Section 4.5;
- the direction of every printed Table 3 row below `n = 300` against `2^{n/2}`;
- the sum-versus-max difference (≤ 0.0007 bits) and which term dominates;
- the recorded artifact digests.

**Replicated using the producer's own code (agreement here is weaker evidence —
it reproduces a wrong-but-self-consistent implementation faithfully):**

- the n = 163 margins across metrics and readings (object 1);
- the crossovers 303 / 375 / 435 under a wider sweep window (object 3);
- the free-yield and exponential-solve object runs, which by design exercise the
  producer's optimizer.

**Taken on trust — NOT checked by me:**

- **Assumption 1 itself** (`d_F4 ≤ 4`). It is an input to every figure in both
  records and to every derivation above. `KN-OPEN-d218ec` and
  EXP-SEMBIN-7e1371 own it.
- the paper's own derivation of eq. (15) from `P`. I read Section 4.5.2 and
  confirmed the code transcribes `m!·2^{k+n−mk}·n^{4ω}` faithfully; I did not
  re-derive the paper's algebra.
- **the vOW baseline in its entirety** — the 0.886 walk constant, `store_log2 = 30`,
  the near-linear parallel speedup, `q = 2^n`. Relayed from KN-TECH-006 and
  KN-LIT-012, and KN-LIT-012 records that its own full text was not re-read.
  That is **J2**, not mine, and every J1 memory figure above is a Semaev-side
  figure that does not depend on it — but every *margin* and *crossover* does.
- **Semaev's sparsity figures** (`n^3/m` monomials per equation, `(nm)^4/4!`
  total). They are his blog numbers, relayed through KN-LIT-e77232, which itself
  records "The sparsity formulas are his, not re-derived." The record's sparse
  reading — and therefore the 375 crossover and the +11.52 bit margin at
  n = 409 — rests on an unverified relayed formula. I confirmed only that the
  record transcribes it correctly.
- the "36/36 Table 3 cells reproduce exactly" claim. I checked only the
  sub-300 rows' direction and the argmin at five labels.
- the 106-check transcription log. I spot-checked the five dense and five sparse
  memory figures and the three n = 409 margins against `raw-result.json`; all
  agreed.
- the fitted exponent constant `c` and the argmin ladder (**J5**), and the
  independence of the metric set (**J3**).
- **Tables 1–2 as transcribed** in `inputs/SEMAEV-2015-310/tables.yaml`. The
  fulltext rendering of those tables is column-scrambled and unusable, so my
  entire "drops dramatically" reconciliation inherits that transcription. I did
  not open the PDF. Mitigating: I recomputed eq. (11) at each of the nine
  `t < m` rows and the printed `P_theoretical` column agrees to within 0.12 bits
  in all nine, which independently corroborates the row assignment those rows
  would have had to get wrong.

---

## Limitations of this report

1. **Two joints out of six.** J2, J3, J5 and J6 are owned by a sibling I have
   not read. J1 verifies the Semaev side of the accounting; the *margins* and
   *crossovers* additionally require the baseline (J2) and the metric set (J3),
   and both claims consume the cost formulas J5 attacks. A `holds` from me on
   J1 and J4 is not a verdict on either claim.
2. **My J1 dense figure agreeing with the record to 0.0000 bits is a
   consistency result, not a correctness result.** It says the record computes
   the quantity the frozen text and the published dispute both name. Whether
   `width^2` is the memory a real implementation would pay is a question no
   party to that dispute settled and this report does not settle either.
3. **Object 4 rebound the producer's own function.** It shows that optimizer
   varies `t` correctly; it does not independently re-derive `t*`. A genuinely
   blind re-derivation of the load-bearing quantity is TASK-20260913-ec11c4's,
   which I have not read.
4. **A defect in an implementation is not a mathematical conclusion, and none
   of the above is evidence that the chained algorithm works.** Every figure in
   both records is conditional on Assumption 1 and on eq. (11), neither of which
   this task evaluated.

---

```yaml
validation_report:
  id: VAL-20260913-da3982
  task_id: TASK-20260913-da3982
  run_ids: [RUN-SEMBIN-121b59, RUN-SEMBIN-aa5161]
  snapshot_commit: 04f15d7f1
  joints_owned: [J1, J4]
  joint_verdicts:
    J1: holds
    J4: holds
  artifact_checks:
    - >-
      digests_verify: 17/19 files across both runs; the 2 exceptions are each
      run's self-referential artifact-digests.json entry, unverifiable by
      construction
    - 'manifest_yaml_not_in_digest_set: both runs'
    - >-
      snapshot_committed_before_review: true (04f15d7f1); working tree clean for
      both experiment trees
    - >-
      command, revision, dirty-tree state, seed, environment and resource
      records all present and consistent with the code
    - 'certificate kind none, appropriate: nothing is solved'
  metric_recomputations:
    - >-
      semaev_dense_memory_log2_bits at n = 163, 233, 283, 409, 571 -- re-derived
      from Sections 4.2/4.5 and Assumption 1; agrees to 0.0000 bits
    - >-
      semaev_sparse_memory_log2_bits -- agrees to within 0.44-0.86 bits;
      residual traced to (nm)^4/24 versus the Section 4.2 width
    - >-
      macaulay_nvars 2790/4099/6286 -- confirmed as (m-2)n + km; the review
      plan's m*k + 2n is the relation row width, not the variable count
    - >-
      eq. (11) yield loss per unit of t -- 21.19 to 44.42 bits at the FIPS
      labels (optimal m, ceiled k); the record's own convention gives 24.978 to
      53.778
    - >-
      solving saving per unit of t -- 0.000 (block_n4w), 1.650-3.156 (f4_std),
      1.795-3.655 (macaulay4)
    - >-
      f4_std total saving equals 4*omega*log2(m-1) exactly, to three decimals at
      six values of n -- establishes the saving is polynomial in n and a fixed
      power in (m-t), never exponential
    - sum-versus-max on the two memory terms differs by at most 0.0007 bits
  control_checks:
    - >-
      proves_too_much object 1, n = 163: PASS (0/8 cells win; 4/4 Table 3 rows
      below n = 300 lose on time alone)
    - >-
      proves_too_much object 2, eq. (4): PASS (328-1257 bits worse under a
      reading more generous to eq. (4) than the producer's); teeth are narrow
    - >-
      proves_too_much object 3, free-yield null: PASS, NOT PREVIOUSLY RUN --
      crossover moved DOWN in 16/16 CLAIM A cells and 3/3 CLAIM B readings; no
      inverted sign convention
    - >-
      proves_too_much object 4, solving cost exponential in (m-t): PASS, NOT
      PREVIOUSLY RUN -- t* = 2 once the rate exceeds the yield-loss rate, with
      the flip at the independently predicted threshold of 1.0*k
    - >-
      added by this validator, sign of the measured tradeoff: PASS 5/5 -- the
      model reproduces the sign of Table 2's measured short-chain tradeoff, and
      overstates its magnitude, which biases toward interior optima
    - >-
      known_false_t_independent_solve has teeth: confirmed via object 4; the
      optimizer genuinely sweeps t (8 distinct costs in the t-slice at m*)
    - >-
      crossovers are not a sweep-window artifact: 303/375/435 unchanged over
      n in [150, 900]
  cost_model_checks:
    - >-
      cost unit declared, with the incomparability of a rho group operation
      against a Groebner step disclosed rather than modelled
    - memory reported beside time, which is the record's purpose
    - optimistic_assumptions present on both sides
    - time-memory tradeoff declared NOT MODELLED on the baseline side
    - >-
      per-attempt cost times inverse success probability verified -- eq. (15)'s
      1/P factor is exactly m! * 2^{n-mk} and both implementations carry it;
      object 3 confirms removing it makes the attack cheaper, never dearer
    - >-
      UNDISCLOSED ASSUMPTION FOUND: both storage readings presuppose a square
      W x W matrix. The frozen text's own generator count and degree statements
      bound the reachable degree-4 row space 8.93-12.49 bits below W. Direction:
      the record UNDERSTATES Semaev. Not a correction, because applying it would
      require tightening the unchanged W^omega time model in the same direction,
      but it is owed as a limitation; applied to memory alone it would move the
      n = 409 dense margin from -8.79 to about +2.94 bits.
  heuristic_validation_checks:
    - >-
      eq. (11) is the published law, not one fitted after the fact -- Section
      4.3, quoted and re-derived
    - >-
      regime of validity located: x = 2^{tk-n}/t! < 1 required; saturation
      occurs only at m = 2, t = 2, odd n; the maximum log2 x at the optimal m
      anywhere in the sweep is -10.469
    - >-
      prediction preregistered and scored, and REFUTED -- the contract predicted
      t* < m* strictly and the run records the refutation in its own artifact
    - >-
      heuristic conditionality stated: CLAIM B is scoped to "under the published
      yield law" in what_this_does_not_close
  proof_architecture_checks:
    - >-
      baseline fixture: the sub-300 Table 3 rows and the argmin at five labels
      reproduce; the full 36/36 claim was NOT re-checked here
    - >-
      nearby-object control: eq. (4) verified to have the asserted direction but
      narrow teeth; the prime-field control remains owed (D1) and its adequacy
      is J6
  reporting_defects_found:
    - >-
      CLAIM B's "25-28 bits per unit of t at the FIPS labels" should be
      25.0-53.8 under the record's own convention; the quoted range is the two
      smallest rows and one of them (n = 310) is not a FIPS label. Direction:
      understates.
    - >-
      CLAIM B's "exponential in n" is 2^{Theta(sqrt(n log n))}, subexponential
      in n. The superpolynomial-versus-polynomial comparison holds; the wording
      should match eq. (17).
    - >-
      CLAIM A as restated in the review plan attributes the shift to the
      relation store. Under the record's own model the working set dominates at
      every FIPS label under both readings and the store never binds. The run
      manifest says "Semaev's own memory", which is correct; the plan's
      paraphrase is not.
    - >-
      the run manifest describes the two memory terms as charged at a MAXIMUM;
      the code sums them. The sum is the correct charge and the difference is at
      most 0.0007 bits, so this is documentation only.
    - >-
      each run's artifact-digests.json carries a sha256 for itself, and neither
      digest set covers manifest.yaml.
  verdict: passed
  verdict_scope: >-
    Passed as to J1 and J4 and as to the four proves-too-much objects, on the
    committed snapshot 04f15d7f1. This says the two receipts are admissible
    evidence for the accounting they report on the axes this task owns. It does
    not support an ECDLP claim, does not demonstrate a speedup, does not
    authorize promotion of H-SEMBIN-83999d or H-SEMBIN-b1708c, and is not a
    verdict on CLAIM A or CLAIM B -- J2, J3, J5 and J6 are owned elsewhere and
    the Coordinator composes.
  limitations:
    - two joints of six; no whole-claim verdict is offered or implied
    - Assumption 1 (d_F4 <= 4) is an input to every figure and was not evaluated
    - >-
      the vOW baseline, including the relayed 0.886 constant and the unswept
      store_log2 = 30, was taken on trust; it is J2's
    - >-
      Semaev's sparsity formulas are relayed and unverified; the 375 crossover
      and the +11.52 bit n = 409 margin rest on them
    - >-
      the Tables 1-2 reconciliation inherits tables.yaml's transcription of a
      column-scrambled table; corroborated by recomputing eq. (11) at each
      t < m row (agrees to within 0.12 bits in 9/9) but the PDF was not opened
    - >-
      CLAIM B is true in the large-k regime, and its own model evaluated at the
      only parameters where the tradeoff was ever MEASURED says t < m pays
      there -- as does the measurement. The scope statement should say so.
    - >-
      objects 1, 3 and 4 exercise the producer's implementation; agreement there
      is replication, not independent derivation
  artifact_paths:
    - coordination/review/sembin-20260913-9d649f/validator-da3982/report.md
    - coordination/review/sembin-20260913-9d649f/validator-da3982/attestation.yaml
    - coordination/review/sembin-20260913-9d649f/validator-da3982/proves-too-much.json
    - coordination/review/sembin-20260913-9d649f/validator-da3982/work/j1_memory_from_text.py
    - coordination/review/sembin-20260913-9d649f/validator-da3982/work/j1_memory_from_text.json
    - coordination/review/sembin-20260913-9d649f/validator-da3982/work/j4_mechanism.py
    - coordination/review/sembin-20260913-9d649f/validator-da3982/work/j4_mechanism.json
    - coordination/review/sembin-20260913-9d649f/validator-da3982/work/objects.py
    - coordination/review/sembin-20260913-9d649f/validator-da3982/work/objects_raw.json
```
