# Validation report — TASK-20260913-6c5729

**Round** REVIEW-ICPERF-20260913-66fd51 (plan + addendum V6 + addendum split-V2)
**Under review** RUN-ICPERF-305ca3 of EXP-ICPERF-66fd51 (H-ICPERF-cc4847)
**Joints owned** V1, V3, V4, V5, V6, and `proves_too_much` object 1
**Not owned** V2 and `proves_too_much` object 2 (reassigned to TASK-20260915-195b0c)
**Role** validator · `review-adversarial` · independent session · **0 runs launched**

This report covers my joints only. It offers no verdict on the claim as a whole
and none on P2, which is V2's. Every number below is re-derived by a script
under `work/` in this task directory; the scripts and their JSON outputs are the
holding artifacts the plan asks for.

**Scope, stated once and binding on everything below (core rule 4).** All of
this concerns 60 shipped toy instances over F_{2^15}, F_{2^17}, F_{2^19} at
l ≤ 6, six engine builds, one 4-CPU host, one run. Nothing here asserts anything
about the security of any curve, and nothing here says index calculus beats or
loses to any generic attack anywhere.

---

## Verdicts at a glance

| Joint | Verdict | The one thing that decided it |
|---|---|---|
| V1 — certificates and the P1 failure (blind) | **HOLDS** | 30/30 shipped certificates verify under my own arithmetic; the five unverified SAT answers are **twist decompositions** — f3 = 0, all three x_i and x_R have trace 1 |
| V3 — summary arithmetic | **PARTIAL** | 156/156 per-cell values recompute exactly, but three reported `holds` values do not recompute as stated (P3c, P5, P6) |
| V4 — null-object shape and P6 censoring | **PARTIAL** | 18/18 nulls match their template on every non-constant shape measure and 0/18 match on the constant term, 18/18 in the same direction |
| V5 — timing integrity | **HOLDS** | across all 442 non-Macaulay2 rows, `wall_s − cpu_s` ∈ [0.0003 s, 0.1695 s] |
| V6 — the generic baseline column | **HOLDS** | the curve is Koblitz, and RUN-ICPERF-305ca3 reports **no generic baseline at all**, so nothing moves |
| proves-too-much object 1 | **PASSES** | 0 of 170 bit-flipped certificates accepted; 0 of 170 gave f3 = 0 |
| proves-too-much object 2 | **NOT_EVALUABLE** | needs a WDSat run; routed to V2 with the protocol written out below |

---

## V1 — certificates and the P1 failure (BLIND) — **HOLDS**

### What I wrote before opening the producer's code

`work/valgf.py` is my own GF(2^n) and binary-curve arithmetic, written from the
curve equation on `find_points.sage` line 8 (`EllipticCurve(K,[1,1,0,0,1])`
→ `y² + xy = x³ + x² + 1`) and the modulus on line 2 of each `INFO*.dimacs`.
It was written and run to completion **before** I opened
`experiments/EXP-ICPERF-66fd51/code/binec.py` or `code/convert.py` — which, in
the event, I never opened at all (see "blindness", below). It implements
multiplication and reduction, inversion by Fermat, trace, half-trace, the
quadratic solve `z² + z = c`, the curve membership test, negation, and addition.

Self-tests before any certificate was touched (`work/v1_certs.json`
`field_selftests`): all three shipped moduli are irreducible by Rabin's test;
`Tr(1) = 1` for all three n (as it must be for n odd); and a brute-force count
over every x ∈ F_{2^15} gives `#E(F_{2^15}) = 32494`, which V6 below reproduces
independently from the Frobenius recursion.

### (1) The 30 shipped certificates

| convention | on curve | f3 = 0 | x(±P1 ±P2 ±P3) = x_R |
|---|---|---|---|
| **LSB-first** (Sage `coefficients(sparse=False)`) | **30/30** | **30/30** | **30/30** |
| MSB-first | 4/30 | 0/30 | 0/30 |

Sign choices: for each certificate I tried every combination of the two
y-coordinates per x that is not forced, and took the certificate as verifying
if **any** combination gives `x(P1+P2+P3) = x_R`. Combinations tried were 8 on
24 certificates, 4 on five (one x repeated), and 2 on one. **Every certificate
matched under exactly 2 of the combinations tried**, which is the expected
signature — negating all three points negates the sum and leaves its
x-coordinate fixed in characteristic 2.

The bit-order convention is therefore settled by the data and not by assumption:
LSB-first verifies everything and MSB-first verifies nothing.

### (2) The ANF at the WDSat assignment

I parsed `Xn19l6-19-U.anf` with my own parser (`work/v1_anf.py`) and evaluated
every equation at the `assignment` string recorded on the row
`wdsat/default/n19l6-19-U`. **52 of 52 equations are satisfied; 0 unsatisfied.**
Calibrating the same parser on known-good S instances gives the same convention
(each equation's XOR evaluates to 1, matching the `T` constant), so the parser
is not being tuned to produce the answer I wanted.

Across the whole run: **130 WDSat assignments checked against their ANF, 0 rows
with any unsatisfied equation, 130/130 with core bits matching the recorded
`x_bits`** (`work/v1_allsat.json`).

CryptoMiniSat's model on the upstream CNF-XOR conversion (`work/v1_cms.py`):
**2364 of 2364 OR clauses satisfied and 52 of 52 XOR clauses satisfied**, with
the first 18 model bits decoding to the same three x-values in a different
order. Two independent engines, two independent encodings, one x-set.

### (3) f3 under both conventions, and (4) the four traces

For `n19l6-19-U` (`work/v1_anf.json` `convention_table_n19l6_19_U`):

| convention | x₁, x₂, x₃ | x_R | f3 | Tr(x + 1 + 1/x²) for x₁,x₂,x₃ | Tr for x_R |
|---|---|---|---|---|---|
| **LSB-first** | 0x14, 0x22, 0x29 | 0x29c68 | **0** | **1, 1, 1** | **1** |
| MSB-first | 0x0A, 0x11, 0x25 | 0x0b1ca | 0x45b28 ≠ 0 | 0, 1, 1 | 0 |

All three x_i lie in the subspace V (all < 2⁶ = 64). Under LSB-first — the
convention the 30 certificates force — **every one of the four elements has
trace 1, so none of them is an x-coordinate of E**, and all four are
x-coordinates of the quadratic twist `y² + xy = x³ + 1`. On the twist, the
decomposition holds: `x(P1 ± P2 ± P3) = x_R` for 2 of the 8 sign choices, the
same signature as the 30 genuine certificates.

The Coordinator's "what would change my mind" list is answered directly: f3 is
**not** nonzero (it is 0 under LSB-first), x_R does **not** have trace 0, and
the bit-order convention is **not** inconsistent. None of the three overturning
conditions fired.

### (5) Whether the decoder's convention matches

I did **not** need to open `binec.py` to answer this, and did not. The run's own
recorded `why` field on all five rows reads `x = 0x14 is not an x-coordinate on
the curve` — and `0x14` is exactly the LSB-first decoding of the first 6 bits,
which is the convention under which f3 = 0. So the producer's decoder reads the
same bits I do and rejects for the correct reason. This is the cleaner form of
step (5): the decoder's convention is legible from its output, so the check
costs no blindness. I record this as a **deviation** from the literal attack
plan, which told me to open `binec.py` at this point.

### (6) Classification

**(c) TWIST DECOMPOSITION.** Confidence: **high**, and it is not resting on a
single computation. The five answers are:

- genuine roots of the shipped system — 52/52 ANF equations satisfied, and
  2416/2416 clauses of the independent CNF-XOR encoding;
- genuine roots of the summation polynomial — f3 = 0 under my own arithmetic;
- not on E — trace 1 for all four elements, computed independently;
- on the twist, and decomposing there — 2 of 8 sign choices, the certificate
  signature.

(a) encoding defect and (b) decoder defect are both excluded: the encoding is the
upstream `.anf` that WDSat read directly, a second engine on a different encoding
found the same set, and the decoder rejected under the same bit convention that
verifies all 30 certificates. (d) "something else" is excluded by the exhaustive
search below.

### The exhaustive search that closes it

`work/v1_exhaust.py` enumerates **every** multiset {x₁,x₂,x₃} ⊂ V and evaluates
f3, for all 60 instances — 5984 triples per n15l5 instance, 45760 per l = 6
instance. Results (`work/v1_exhaust.json`):

- **60/60 agreement with the run's SAT/UNSAT status. Zero mismatches.** Every
  instance the run called SAT has a root and every instance it called UNSAT has
  none.
- `n19l6-19-U` has **exactly one** root, the twist one. There is **no**
  E-decomposition of its target in V³, so the solver could not have returned one.
- Of 67 roots across all 60 instances: 45 all-on-E, 1 all-on-twist, 21 mixed
  (some x on E and some on the twist — these are the cancelling-pair
  configurations, and all 21 belong to one instance).

### Unexpected observation: `n15l5-8-S` is degenerate

`n15l5-8-S` has target x_R = 0x12, which **lies inside the subspace V itself**,
and has **32 distinct roots** where every other instance has one. Its SAT answers
verify correctly and P1's verdict is unaffected, but as a benchmark instance it
is not comparable to the others: a solver that finds any of 32 solutions is
solving an easier problem than one that must find the unique solution. Recorded
under core rule 8; it belongs in the instrument's known-quirks list.

### Proves-too-much, object 1 — **PASSES**

- **Bit-flipped certificates.** The plan asked for one bit of x₁ flipped on each
  of the 30 certificates. I ran **every** single-bit flip of x₁ — 5 bits at
  l = 5 and 6 bits at l = 6, so **170 objects**. The checker **accepted 0 of
  170**, and **f3 was nonzero on 170 of 170** (the plan allowed one zero; there
  were none). Of the 170 perturbed x₁ values, 78 are still on E — so the checker
  is rejecting on the decomposition, not merely on curve membership.
- **x_R swap.** Replacing `n19l6-19-U`'s target with `n19l6-1-S`'s target and
  keeping the x-set: rejected under both bit conventions, with f3 = 0x6147f and
  0x2eeb8 respectively — nonzero both ways. (Note: the plan says "the five
  x-sets", but there is only **one** distinct x-set; the five rows return the
  same set, CryptoMiniSat in a different order.)

---

## V3 — summary arithmetic — **PARTIAL**

My reduction (`work/v3_reduce.py`) was written and run from `results.jsonl` and
the contract's metric definitions **before** I opened `code/summary.py`.

### (1) The diff

`work/v3_celldiff.py`: **156 of 156 numeric values in `summary.json`'s per-cell
table reproduce exactly** — every median wall time, every median conflict count,
every finished-row count, to the last printed digit. Not one is off.

The only entries not covered are `m2_f4_*` and `singular_*`, which `summary.json`
emits as `null`/`0` and my reduction omits entirely; both say the same thing
(no row finished), so this is a presentation difference, not a disagreement.

Headline predictions: P1 false, P2 null, P3 true, P4 true, P5 true — all
reproduce. P6 does **not**; see below.

### (2) The identical 83.50030889840438 — confirmed as a bug, and it is a variable leak

`summary.py` line 131 reads `L["cryptominisat5_pure_cnf_wall_s"]` and
`L["wdsat_default_wall_s"]` inside the P3b `for cell / for label` loop — but `L`
is never rebound in that loop. It is a leftover from the per-cell table loop at
lines 53–67, where it ends holding the **last** cell/label processed,
`sorted(cells)[-1] = n19l6` with `label = "U"`. So all four P3c entries are
`195.9794 / 2.34705 = 83.50030889840438`, n19l6/U's ratio, written under four
keys.

The corrected per-cell ratios:

| cell | CMS pure-CNF median | WDSat default (all 10) | **corrected ratio** | vs matched 5-instance subset |
|---|---|---|---|---|
| n17l6/S | 3.0242 | 0.2909 | **10.396** | 26.071 |
| n17l6/U | 80.0281 | 2.32155 | **34.472** | 34.468 |
| n19l6/S | 21.3309 | 0.3162 | **67.460** | 327.664 |
| n19l6/U | 195.9794 | 2.34705 | **83.500** | 82.629 |

**All four remain ≥ 10 under both comparators, so P3c's verdict survives.** The
Coordinator's prior called this exactly, including which cell would be tight:
n17l6/S at 10.40 clears the threshold by 4%. The declared breaking artifact — "a
corrected P3c ratio under 10" — does not fire.

One caveat the correction exposes: the CMS pure-CNF median is over the 5
phase-D instances while `wdsat_default_wall_s` is over all 10, so the `all 10`
column compares medians over different instance sets. The matched-subset column
is the like-for-like one; both clear 10.

### (3) The P3b comparator — matched subset, legitimate

`summary.py` lines 113–118 build `stems` from the instances `noncore_first`
actually ran on and take the default median over exactly those. So
`default_wall_s = 0.0651` (n19l6/S) and `0.116` (n17l6/S) **are** the matched
5-instance medians, against all-10 medians of 0.3162 and 0.2909. This is the
right comparison and the Coordinator's guess was correct. It is, however,
**undocumented**: the key is called `default_wall_s`, a reader comparing it with
the cell table's `wdsat_default_wall_s` sees a 4.9x discrepancy with nothing
saying why. A renamed key would cost nothing.

### (4) The P6 aggregation rule — does not match "on every cell"

Two separate things:

- **How the null median is formed.** `summary.py` computes
  `med([U_null_median, S_null_median])` — the median of two per-label medians,
  i.e. their mean — not the pooled median over all six null rows. Pooled gives
  3630846 (n15l5) and 5539684 (n17l6) against the reported 3540911.5 and
  5109609.75; ratios 117.21 and 21.75 against the reported 114.30 and 20.06.
  Both aggregations clear 10, so no verdict moves, but the reported number is
  not the quantity its key name suggests.
- **How the null cell is handled.** `holds` is
  `all(v["holds"] for v in p6.values() if v["holds"] is not None)`. n19l6 has
  `holds: null` because all six of its nulls timed out, and that cell is
  **dropped from the conjunction**. So `summary.json` reports `P6.holds: true`
  on the strength of two cells out of three. The per-cell block is honest — it
  shows `n19l6: {ratio: null, holds: null}` — but the top-level boolean is not.
  For a prediction the hypothesis words as a claim to be tested on the cells,
  the correct report is **"holds on n15l5 and n17l6, unevaluable on n19l6"**,
  not `true`.

### Two further defects the plan did not ask about

- **P5's Groebner clause is silently absent.** The hypothesis words P5 with two
  clauses: SAT-engine U/S conflicts ≥ 2, and Groebner S/U **cpu** in [0.5, 2].
  `summary.py` guards the second on `S["m2_f4_cpu_s"] and U["m2_f4_cpu_s"]`,
  which reads the row key `engine_cpu_s`. **That key appears on 0 of 504 rows.**
  So the clause is never evaluated, no entry records that it was skipped, and
  `summary.json` reports `P5: {holds: true}` with nothing indicating the report
  covers half the prediction. This is not a wrong number; it is a true number
  labelled as a broader claim than it is.
- **The `stats` block is empty for three engines.** All 32 Macaulay2 rows carry
  no `stats` at all; all 60 CaDiCaL and MiniSat rows carry a `stats` key that is
  empty. Only CryptoMiniSat reports (88 of 90). So conflicts-based comparison is
  available for two engines out of six — an instrumentation gap that limits what
  any successor row can compare, and one worth fixing before the boundary table
  grows.

### V3 verdict

**PARTIAL.** Every declared breaking artifact is **absent**: no median is off by
even the last digit, no corrected P3c ratio is under 10, and the P3b comparator
*is* the matched subset. The joint's own wording — "every per-cell median **and
every P1–P6 value** in `summary.json` recomputes" — is what fails: four P3c
entries are one number copied, and the P5 and P6 `holds` booleans do not
recompute as statements about the predictions as worded. **No P1–P6 verdict
changes under any of the corrections.**

---

## V4 — null-object shape and P6 censoring — **PARTIAL**

### (1) The 18-row shape table

`work/v4_shape_strict.py`, parsing all 18 nulls and their 18 templates with my
own ANF parser — the one pinned by having evaluated every WDSat assignment in
the run to 0 unsatisfied equations:

| property | nulls matching template |
|---|---|
| variable count | **18/18** |
| equation count | **18/18** |
| total degree histogram, excluding the constant | **18/18** |
| per-equation degree multiset, excluding the constant | **18/18** |
| variable support (which indices appear) | **18/18** |
| **number of constant (`T`) terms** | **0/18** |

The nulls are shape-matched on everything except degree 0. There, every null has
**fewer** constants than its template — 18 out of 18 in the same direction, mean
constant fraction **0.510 for the nulls against 0.823 for the templates**. The
0.51 is a fair coin per equation; the 0.82 is a property of the descended system.

The run records `shape_matches_template: true` on all 18 rows, and by the
producer's own sizing tuple (equations, unary terms, non-unary monomials) that is
correct — the constant is not in the tuple. The plan's breaking artifact is
worded more broadly, as "a null object whose **monomial-degree profile** or
variable count differs", and the constant term is part of a monomial-degree
profile. So this fires, weakly.

**What I can and cannot say about it.** It is systematic, not noise. I cannot
determine its effect on conflict counts without running WDSat, which I may not
do, so I do not assert that it is harmless. What I can say is the size: the
observed null/structured conflict gap is 20–114x, and the difference between the
two objects is one Boolean per equation out of 42–52 equations whose degree-1,
degree-2 and degree-3 structure is identical. Whether that Boolean carries any
of the 20–114x is exactly the kind of thing the relabelling control (object 2,
below) exists to measure, and it is unmeasured.

### (2) The P6 ratios

| cell | structured U median conflicts | null median (per-label medians) | ratio | null median (pooled) | ratio | nulls finished |
|---|---|---|---|---|---|---|
| n15l5 | 30978.5 | 3540911.5 | **114.30** | 3630846 | 117.21 | 6/6 |
| n17l6 | 254656.5 | 5109609.75 | **20.06** | 5539684 | 21.75 | 3/6 |
| n19l6 | 255301.0 | — | **null** | — | null | **0/6** |

The reported ratios reproduce exactly under the producer's aggregation, and the
verdict is the same under the pooled one.

The second breaking artifact — "a finishing null with fewer conflicts than its
structured U" — **does not fire**. The *minimum* conflict count over all nine
finished nulls is 1072647 at n15l5 (34.6x its cell's structured-U median) and
4082325 at n17l6 (16.0x). No finished null comes close to structured order.

### (3) The n19l6 censored reading

All six n19l6 nulls hit the 180 s timeout. `180 / 2.34705 = **76.69x**` the
structured-U median wall — the Coordinator's prior said 77x and that is right.

**But the contract words P6 in conflicts, not wall.** The censored wall bound is
a lower bound on a *different quantity* from the one P6 predicts, and none of
the six timed-out rows reports a conflict count at all (`work/v4_null.json`:
`any_timed_out_null_reports_conflicts: false`), so no censored bound on the
predicted quantity exists. The honest statement is that the n19l6 censored wall
**supports the direction** of P6 and **does not evaluate P6**. It is evidence
that the nulls are harder; it is not evidence about the ratio P6 names.

### V4 verdict

**PARTIAL.** The shape match holds on five of six measures and fails
systematically on the sixth; the P6 ratios reproduce; the n19l6 cell is
unevaluable in the predicted quantity and supports the direction in a different
one.

---

## V5 — timing integrity — **HOLDS**

### (1) Gaps, and whether any row spans one

504 rows, of which 474 are solve rows and 30 are certificate rows. Sorting by
`recorded_at` and subtracting the closing row's own wall time — rows are stamped
at completion, so a 900 s Singular timeout *produces* a 900 s gap with nothing
idle in it — leaves exactly **two unexplained idle periods**:

| idle | between | closing row |
|---|---|---|
| **43866 s** | 2026-09-14T00:10:08Z → 12:24:14Z | `n17l6-13-U wdsat default_on_null_object`, wall 180.0036 s |
| **59032 s** | 2026-09-14T13:56:36Z → 2026-09-15T06:21:37Z | `n17l6-13-U cryptominisat5 pure_cnf`, wall 68.8215 s |

Both fall **between** rows, and in both cases the row that closes the gap ran for
far less than the gap. **No row spans either suspension**, and the wall/cpu check
below confirms it independently: a row that had absorbed a suspension would show
wall time enormously in excess of its own CPU time, and none does.

### (1b) wall_s vs cpu_s — this is what settles the joint

| engine | rows | min `wall−cpu` | max `wall−cpu` | cpu/wall range |
|---|---|---|---|---|
| wdsat | 288 | 0.0003 s | **0.1695 s** | ≤ 1.000 |
| cryptominisat5 | 90 | 0.0010 s | 0.1378 s | ≤ 1.000 |
| cadical | 30 | 0.0014 s | 0.0539 s | ≤ 1.000 |
| minisat | 30 | 0.0033 s | 0.1127 s | ≤ 1.000 |
| singular | 4 | 0.0688 s | 0.1502 s | ≤ 1.000 |
| **macaulay2** | 32 | **−26.2516 s** | −0.2647 s | **1.273 – 2.744** |

Across **all 442 non-Macaulay2 rows**, wall time exceeds the row's own CPU time
by between 0.3 ms and 170 ms. Not one row lost a measurable amount of wall time
to anything — contention, suspension or otherwise. Restricted to the 94
high-load non-Macaulay2 rows, the maximum is 0.1378 s.

I also tested the schedule directly. `recorded_at` is truncated to whole seconds,
so a reconstructed start carries up to 1 s of error; counting only pairs that no
assignment of true end times inside those one-second windows can make sequential,
**0 of 21745 ordered pairs are provably concurrent**. The run is sequential.

### (2) The exclusion-sensitivity test — and why it cannot do what the plan asked

125 solve rows launched at `loadavg1 > 2`, concentrated in phase C (31 of 32)
and phase D (82 of 90), matching the Coordinator's count.

**P4** is clean. Excluding high-load rows moves the gauss/default ratio by at
most **0.3%** on any of the six cells (n17l6/U: 7.196 → 7.175, one row dropped;
every other cell unchanged), and **no verdict flips**. P4's rows ran in phases A
and B, which are almost entirely low-load.

**P3c cannot be tested this way.** Its CMS pure-CNF rows are in phase D, which is
82/90 high-load, so excluding high-load rows leaves 0, 2, 1 and 1 CMS rows on the
four l = 6 cells. On **n17l6/S there are no rows left at all** and the ratio
becomes undefined; on n19l6/S a single surviving row gives 122.93 against 67.46,
an 82% move that is not a median of anything. **There is no low-load control in
this run for the phase-D engines**, so the exclusion test is underpowered by
construction, and its outputs measure phase membership rather than contention. I
report this as a limitation of the test rather than as a result about the rows.

The declared breaking artifacts do not fire either way: no P3c or P4 cell
*changes by more than 2x* under exclusion (n19l6/S moves 1.82x, the largest), and
no verdict flips — one cell becomes unevaluable, which is not a flip.

**What the high load actually was, since the exclusion test cannot say.** The
Macaulay2 rows used **2.7 CPU-seconds per wall-second** — they are
multi-threaded. Phase C's 32 such rows drove the 1-minute load average to 4.55,
and phase D's first rows inherit the decay tail: 4.29, 4.10, 3.93, 3.86, 3.71,
3.57, 3.03, 2.68, 2.38, 2.23, decaying monotonically with no row running
concurrently. So the elevated readings are **the run's own memory of its
Macaulay2 phase**, not an external competitor, and — decisively — they cost the
measured rows at most 0.138 s each. (The Macaulay2 rows' multi-threading bears on
V2's bad_alloc question. It is V2's to adjudicate and I offer no verdict on it.)

A note on the Coordinator's prior, which says "every row's wall_s is within 2 s
of **2 ×** cpu_s". The relation in the data is wall ≈ **1 ×** cpu, to within
0.17 s, for every engine except Macaulay2 where cpu **exceeds** wall. The prior's
substance — the measured rows are clean — is right; its stated relation is not
the one the rows satisfy.

### (3) Timeouts

**0 rows** have `wall_s > timeout_s + 1`. The largest overshoot in the run is
`900.0445 − 900 = 0.0445 s`. Every `budget_stop_timeout` row is stopped within
45 ms of its budget.

### V5 verdict

**HOLDS.** No row spans a suspension, no row exceeds its timeout, no row lost
more than 0.17 s of wall to anything, and no P3c or P4 verdict flips under
exclusion. The one departure from the plan is that the exclusion test on P3c is
not evaluable for want of a low-load control, and I have substituted a direct
measurement that answers the same question more tightly.

---

## V6 — the generic baseline column — **HOLDS**

### (1) The coefficients

`find_points.sage` line 8: `E = EllipticCurve(K,[1,1,0,0,1])`, i.e. Sage's
`[a₁,a₂,a₃,a₄,a₆] = [1,1,0,0,1]`, giving `y² + xy = x³ + x² + 1`.

**All five coefficients are the literals 0 and 1**, which are the elements of the
prime field F₂ and lie in F_{2^n} for every n. E is therefore the base change of
a curve defined over F₂, and the 2-power Frobenius `τ(x,y) = (x²,y²)` maps
E(F_{2^n}) to itself — it is an endomorphism. That is the definition of a
**Koblitz (anomalous binary) curve**. The addendum's premise about the curve is
correct.

### (2) Point counts, from the F₂ hand count and the recursion

`#E(F₂)` by hand: for x = 0, `y² = 1` has the single root y = 1 (squaring is a
bijection on F₂), giving (0,1). For x = 1, `y² + y = 1+1+1 = 1`, but `y² + y = 0`
for both y ∈ F₂, so no point. **1 affine point + O = 2**, hence
`t = 2 + 1 − 2 = **1**`.

Then `#E(F_{2^n}) = 2ⁿ + 1 − s_n` with `s_n = s_{n−1} − 2·s_{n−2}`, `s₀ = 2`,
`s₁ = 1`:

| n | s_n | #E(F_{2^n}) | factorisation | r (largest prime) | log₂ r | cofactor h |
|---|---|---|---|---|---|---|
| 15 | 275 | **32494** | 2 · 7 · 11 · **211** | 211 | 7.72 | **154** |
| 17 | −101 | **131174** | 2 · **65587** | 65587 | 16.00 | 2 |
| 19 | −797 | **525086** | 2 · **262543** | 262543 | 18.00 | 2 |

Every one of the three is confirmed by an **independent brute-force count over
all 2ⁿ x-values** using the trace criterion — `recursion_matches_brute_force:
true` for n = 15, 17, 19. The n = 15 value also matches the point count my V1
self-test produced hours earlier by a different code path.

**τ's orbit is the full 2n.** On the order-r subgroup τ acts as an integer λ with
`λ² − λ + 2 ≡ 0 (mod r)`. Exactly one of the two roots satisfies `λⁿ ≡ 1`, which
is forced since `τⁿ = 1` on E(F_{2^n}): λ = 21 mod 211, 17184 mod 65587, 84450
mod 262543, each of multiplicative order **exactly n**, and in each case −1 is
**not** a power of λ. So `⟨τ, −1⟩` acts with orbit size **2n = 30, 34, 38** on
generic points. The addendum's breaking artifact "a subgroup structure making the
⟨τ,−1⟩ orbit smaller than 2n" **does not fire**.

### (3) The baseline, derived from the VOW source record

From `knowledge/literature/KN-LIT-73f7e1.md` (`provenance: retrieved` — an agent
of this program read `inputs/VOW-1996-PCS/` at source), Section 5.1 eq. (5): for
a group of prime order p, `T_ρ = (√(πp/2)/m + 1/θ)·t`. **The paper's constant is
√(π/2) = 1.2533 on √p, and the record states plainly that the paper contains no
negation map and no 0.886 constant.**

For an automorphism group of order k I use `√(π/2)·√(r/k)`, i.e. the same
birthday constant on a set of r/k classes. **That rests on a heuristic, and I name
it: the walk induced on the orbit space of the automorphism group is itself a
random walk on a set of size r/k.** It is the standard assumption and it is known
to be imperfect — for the negation map the induced walk has short fruitless
cycles that must be detected and escaped, at a cost this heuristic does not
model. Note also that **0.886 = √(π/4) is itself only `recalled` in this
program** (KN-LIT-73f7e1 attributes it to Wiener–Zuccherato 1998 / GLV 2000,
neither of which any agent here has opened), so both reduced rows below are
heuristic applications of VOW's constant, not read sources.

| cell | r | k=1 (none) | k=2 (negation) | k=2n (⟨τ,−1⟩) | factor vs none | factor vs negation |
|---|---|---|---|---|---|---|
| n15l5 | 211 | 18.21 | 12.87 | **3.32** | 5.485 | **3.877** |
| n17l6 | 65587 | 320.97 | 226.96 | **55.05** | 5.831 | **4.123** |
| n19l6 | 262543 | 642.19 | 454.09 | **104.18** | 6.164 | **4.359** |

(expected group operations; the `1/θ` term is a design parameter and is dropped
from all three rows equally.)

**The correction factor is √n, not √(2n), against a negation-only baseline.**
√(2n) = 5.477 / 5.831 / 6.164 is the factor against a baseline with **no**
equivalence classes at all. Against negation-only it is
√n = **3.873 / 4.123 / 4.359**.

This corrects the claim the addendum quotes from IDEA-20260915-8fe0ef, which I
did **not** read — I scored only the statement written out in the addendum
itself. That statement is internally inconsistent: its **formula**
(`0.886·√r ÷ √(πr/4n)`) evaluates to √n = 3.87 / 4.12 / 4.36, while the
**number** it asserts is √(2n) = 5.5 / 5.8 / 6.2. The two differ by a factor of
√2 ≈ 1.414 at every n. My own numerator and denominator agree with the
proposal's to the rounding of 0.886 (12.87, 226.96, 454.09 and 3.32, 55.05,
104.18); only the ratio it states is wrong, and it is wrong in the direction of
overstating the correction.

### (4) What the run reports as a baseline: **nothing**

I searched `manifest.yaml`, `summary.json`, `task-report.md`, `command.txt` and
`specification.yaml` for rho, baseline, generic, pollard, vow, oorschot, koblitz
and frobenius. The only hits are `cnf_generic: 300` in the manifest — a timeout
budget key — and the frozen contract's own interpretation limit at
`specification.yaml:151`:

> No relation-yield, linear-algebra or rho column exists in this row.

The hypothesis says the same thing (`interpretation_limits`: "No rho comparison
exists in this batch").

**So RUN-ICPERF-305ca3 reports no generic baseline of any kind.** Every number it
reports is a solver wall time, a conflict count, or a ratio between two of them.
There is no ratio between a reported baseline and a corrected one, and **no
comparison, ratio or verdict in the run or its summary moves** when the Koblitz
correction is applied. The addendum named this as the most likely outcome and as
a holding verdict, and that is what it is.

One correction to the addendum's framing, which matters for the composition: the
addendum says "the negation-only Pollard rho baseline that RUN-ICPERF-305ca3
compares its SAT column against". **There is no such baseline and no such
comparison.** What V6 establishes is a correction to the *future* boundary table
of RQ-ICPERF-94c86e, not a defect in this run. RQ-ICPERF-94c86e already requires
"matched Pollard rho and BSGS on the same group, same machine, same session" —
so if that table is built by **measuring** rho rather than substituting a
formula, a negation-only implementation on this curve will understate rho's speed
by √n, and the correction must be carried by the implementation rather than by
the arithmetic.

### Two things that matter more than the Koblitz factor at these parameters

- **n = 15 has a fully smooth group order.** `32494 = 2 · 7 · 11 · 211`, so
  Pohlig–Hellman reduces the whole ECDLP to the order-211 subgroup. Using
  `√(#E)` instead of `√r` overstates the generic baseline at n = 15 by a factor
  of **12.4** — more than double the Koblitz factor, and on a completely
  different axis. At n = 17 and n = 19 the cofactor is 2 and the same
  substitution costs only √2. Any future baseline column must use r and not #E,
  and must say which.
- **At n = 15 the asymptotic constant is meaningless.** `r/(2n) = 211/30 ≈ 7`
  equivalence classes. A birthday constant on a seven-element set is not a cost
  model; the ⟨τ,−1⟩ figure of 3.32 group operations in the table above should be
  read as arithmetic, not as a prediction. n = 17 and n = 19 give 1929 and 6909
  classes, which are small but not absurd.

### (5) Nearby-object control — the argument fails off Koblitz, as it must

Same Weierstrass shape with `a₆ = a` (the field generator), which is outside F₂:

| n | a₆² = a₆? | τ an endomorphism? | actual #E | what the F₂ recursion would predict | recursion applies? |
|---|---|---|---|---|---|
| 15 | no | **no** | 32642 | 32494 | **no** |
| 17 | no | **no** | 131586 | 131174 | **no** |
| 19 | no | **no** | 525186 | 525086 | **no** |

The curve is non-singular (discriminant `a₆ = a ≠ 0`), so it is a legitimate
nearby object. `τ(a₆) = a₆² ≠ a₆`, so τ does not fix the coefficients and is not
an endomorphism of E; the F₂ trace recursion gives the wrong point count in all
three cases; and no Frobenius speedup is available. **The argument does not prove
too much.**

### V6 verdict

**HOLDS.** The curve is Koblitz, the orbit is the full 2n, the correction is real
for the boundary table, the nearby-object control fails correctly — and nothing
the run reports moves, because the run reports no baseline.

---

## The joint I do not own, and the control I could not run

### proves-too-much object 2 — **NOT_EVALUABLE**, routed to V2

The object is: take `Xn15l5-11-U.anf`, apply a random permutation to its variable
indices (a bijection, so the system is preserved exactly), and run WDSat default.
This requires a solver launch, which my handoff sets `maximum_runs: 0` to
prohibit and which would pollute the in-flight RUN-ICPERF-4ec9b9's per-row
timings. Per the task instruction, here is exactly what I would have run and what
each outcome would mean.

**Protocol.** Generate a uniformly random permutation π of {1,…,42} from a
recorded seed. Rewrite every variable index in `Xn15l5-11-U.anf` as π(i),
preserving monomial and equation structure and the constant terms, and preserving
the declared header counts. Verify before running that the permuted file has an
identical multiset of per-equation degree multisets and an identical constant
count — a permuted file that fails that check is a generator bug, not a control.
Then run the same WDSat build recorded on the original row
(`wdsat_build` field), default configuration, same 120 s timeout, on an
**otherwise idle machine**, and record status and `conflicts`.

**What each outcome would mean.**

- Conflicts of structured order, ~3×10⁴ (the original row's neighbourhood) and
  status UNSAT: P6's mechanism reading survives. The solver's advantage on
  descended systems is a property of the system, not of the index order the
  generator emits, and P3b and P6 measure two different things.
- Conflicts of null order, ≳3×10⁵ (more than 10x the original) : **the control
  fails.** WDSat's speed on these instances is then substantially a property of
  the **variable order** the generator emits, the null comparison measured that
  order as well as the content, and the honest composition merges P3b and P6 into
  one finding about variable order rather than reporting two mechanisms. The
  plan's own `what_a_failure_means` says this, and I endorse the wording.
- Anything in between: report the ratio and treat P6's mechanism reading as
  partially confounded, in proportion.
- A status other than UNSAT: a bug in the permutation, not a result.

I note without having opened it that a file named
`artifacts/PTM2-Xn15l5-11-U-perm20260915.anf` already exists in this task
directory, left by an unattested predecessor (see below). Whoever runs this
control should regenerate the object from a recorded seed rather than trust that
file, for the same reason the predecessor's numbers are not findings.

### V2

Not mine, not read, no verdict offered. One observation from V5 that bears on it
and which I pass along as a measurement rather than a conclusion: the 32
Macaulay2 rows consumed between 1.27 and 2.74 CPU-seconds per wall-second, so
Macaulay2 ran multi-threaded. What that implies about address-space reservation
under `RLIMIT_AS` is V2's to decide.

---

## Things neither the plan nor its addenda anticipated

1. **A second unattested predecessor.** Disclosure D-1 records one abandoned
   attempt, in `scratch/`, from ~09:16–09:33Z. There is a **second** one, in
   `artifacts/`, written 12:35–13:33Z on 2026-09-15, covering V1, V3, V4, V5, V6
   and a prepared PTM2 object — a nearly complete pass over my joints, with no
   `report.md` and no `attestation.yaml`. It is not covered by any disclosure.
   I handled it exactly as the Coordinator handled `scratch/`: I listed the file
   **names** to write this paragraph and opened **none** of their contents.
   Everything I report is re-derived by scripts under `work/` that reference
   nothing in either directory. The round should record this, because two silent
   predecessors is a different independence story from one.

2. **The shipped "U" targets are decomposable far less often than uniform
   targets are.** Having established that a "U" label means "uniform random
   target", I measured how often such a target is decomposable. Exhaustive
   enumeration over V³ gives the exact decomposable fraction per cell — 0.1898
   (n15l5), 0.2871 (n17l6), 0.0799 (n19l6) — and a 300-sample Monte Carlo per
   cell over genuinely uniform draws agrees with it (54/300, 73/300, 23/300, all
   within sampling error, and **0 disagreements in 900 samples** between the
   closed-form membership test and the exhaustive root search).

   Those fractions predict **5.57 decomposable targets among the 30 shipped U
   instances. One is observed** — `n19l6-19-U`, the one this whole round is
   about. Per cell: 0/10, 0/10, 1/10 against 1.90, 2.87, 0.80 expected.
   `P(X ≤ 1) = 0.0148`.

   I ran the obvious control: the on-E/on-twist split of the 30 U targets is
   17/13, consistent with uniform, so the shortfall is not a trace bias. I ran
   the obvious instrument check: my root-existence model agrees with the solver's
   SAT/UNSAT verdict on **60 of 60** instances, so the model is not wrong about
   these instances.

   **I record this as an observation and not a finding.** It is post-hoc, n = 30,
   and 1.5% is unusual without being extraordinary. The mundane explanations are
   that the vendored `benchmarks/` files were not produced by the loop that was
   read at source, or were produced with filtering, or simply that this is the
   1.5%. What would settle it costs no solver: regenerate U targets with the
   shipped generator at a recorded seed and measure the decomposable fraction
   directly. That is a successor task, not mine.

3. **`n15l5-8-S` is degenerate** — 32 roots where every other instance has one,
   because its target lies inside the subspace V. Recorded above under V1.

4. **`P5`'s Groebner clause and the empty `stats` blocks** — recorded above under
   V3. `engine_cpu_s` is on 0 of 504 rows; Macaulay2 rows have no `stats`;
   CaDiCaL and MiniSat rows have empty ones.

5. **The run's own Macaulay2 phase is what raised the load average** the V5
   exclusion test was built to control for, which is why that test has no control
   group. Recorded above under V5.

6. **This round cannot pass its own independence check mechanically.**
   `tools/check_review_independence.py` takes exactly one `--plan` and has no
   flag for an addendum, so it holds each task to the **base** plan's `owners`
   map. That map predates the split. Run against the base plan it reports two
   failures for this task — `does not claim joint 'V2' in joints_owned`, and no
   `V2` entry in the verdict mapping — which are one fact twice: the addendum
   that moved V2 to `TASK-20260915-195b0c` is invisible to the tool. The
   mirror-image failures will land on `TASK-20260915-195b0c` for V1/V3/V4/V5/V6
   when it runs.

   I did **not** clear this by adding `V2` to `joints_owned` and a `V2` verdict.
   That would buy a green check by asserting an ownership the governing addendum
   removed and a verdict on the one joint I could not evaluate under
   `maximum_runs: 0` — a fabrication under core rule 9, and exactly the failure
   the checker exists to catch. It clears properly either by checking the round
   against a composed plan, or by teaching the checker to follow
   `extends`/`also_extends` and apply a later addendum's `what_changes.owners`
   over the base map. Both are Coordinator calls; I write no tooling change and
   commit nothing. Recorded in `attestation.yaml` under
   `independence_checker_result`.

---

## Deviations from the plan

| # | Deviation | Why |
|---|---|---|
| D-a | V1 step (5) says to open `code/binec.py` and compare decoder conventions. I did not open it. | The decoder's convention is legible from its own recorded output (`why: x = 0x14 is not an x-coordinate on the curve`, which is the LSB-first reading). Answering from the output preserves blindness at no cost. `blind_from` is therefore fully respected: I read none of `binec.py`, `convert.py` or `Weil_descent.sage`. |
| D-b | V1's proves-too-much object asked for 30 bit-flipped certificates. I ran 170 (every single-bit flip of x₁). | Strictly stronger; reported as 170/170. |
| D-c | V5 step (2)'s exclusion test is not evaluable for P3c. | Phase D is 82/90 high-load, so no low-load control exists. I substituted a direct per-row wall-vs-cpu measurement, which bounds the contamination at 0.138 s on the rows in question. |
| D-d | I did not read `ledger/proposals/IDEA-20260915-8fe0ef.yaml` at all. | The instruction permits reading it as an unverified pointer. Not reading it is stronger; I scored only the claim quoted inside the committed V6 addendum. |
| D-e | I did not read `artifacts/` or `scratch/` contents. | Independence; see "Things neither the plan nor its addenda anticipated" #1. I did not execute the WDSat binaries under `scratch/wdsat_builds/`. |

## What I did not launch

No solver, no compiler, no build, no re-run — **0 processes launched** against
any engine. Total compute: Python integer and bit arithmetic over committed
artifacts, dominated by three brute-force point counts at n ≤ 19 (116 s of one
core) and the exhaustive V³ search over 60 instances. I did not read
`experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-4ec9b9/`.
