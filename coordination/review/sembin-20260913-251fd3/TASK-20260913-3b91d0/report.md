# Validator report — TASK-20260913-3b91d0 (attempt 2)

Round `REVIEW-SEMBIN-20260913-251fd3`. Joints owned: **N1, N2, N3, N4**.
Reviews the snapshot-archived run package `experiments/EXP-SEMBIN-db9bc3/`
(`RUN-SEMBIN-251fd3`), archived by `TASK-20260913-a10007` at commit `a2cdafc67`.

Independent session. I did not read
`coordination/review/sembin-20260913-251fd3/TASK-20260913-7fb774/` or
`.../TASK-20260913-f6652f/`, nor `coordination/bus/`.

**Scope of this report.** Verdicts are on the INTEGRITY of joints N1–N4 only:
whether the arithmetic, the enumeration, the gate, the controls and the counts
are what the artifacts say they are. The significance of the flagged cells is
joint B1 and is owned by another session. Nothing here is a statement about any
curve's security in either direction, and no degree is measured or asserted
(`IMP-SEMBIN-ENGINE`).

Status: **COMPLETE** — all four joints reported. Verdicts: N1 holds, N2 holds,
N3 holds, N4 holds. Written incrementally (N1 → N2 → N3 → N4); the "Unexpected"
and "Sources read" lists are at the end.

---

## N1 — ARM C arithmetic and enumeration — **HOLDS**

### N1(1) Both bounds re-derived independently, then compared

I coded both bounds from HEUR-1 in `H-SEMBIN-4a80f3` and the plan's N1
statement, and ran them, **before opening `code/arm_c_coset.py` or
`code/binary_field.py`** (scratch: `own_bounds.py` written in attempt 1,
`own_bounds2.py` in this attempt; output `own_bounds2.json`).

Model taken from HEUR-1: `#Fb_i = 2·Bin(2^{C_0}, 1/2)`, `E#Fb_i = 2^{C_0}`,
`m = ceil(n/C_0)`.

**Bound A** — `Pr[all m nonempty] = (1 − 2^{−2^{C_0}})^m ≥ 1 − ε`, ε = 0.05:

| n | 163 | 233 | 283 | 409 | 571 | 4096 | 16384 | 65536 |
|---|---|---|---|---|---|---|---|---|
| my C_0 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 5 |
| reported | 4 | 4 | 4 | 4 | 4 | — | 5 | — |

Exact agreement at all five labels, and A first reaches 5 at n = 16384 exactly
as the report states (n = 4096 still gives 4). Growth order: the condition is
`2^{C_0} ≳ log2(m/ε)`, so `C_0 ≈ log2 log2 n`; measured against `log2 log2 n`
(2.88 at 163 → 4.32 at 2^20, my C_0 4 → 5) — **Θ(log log n) confirmed**.

**Bound B** — total Jensen deficit `Δ(C_0) = m·[log2 E#Fb_i − E log2 #Fb_i] ≤ 1`
bit. My independently computed per-coset and total deficits agree with the
JSON's own `bound_B_deficit_profile_C0_1_to_16` to all printed digits at
n = 571 (C_0 = 1..7: −190.333 / 12.587 / 19.007 / 7.1826 / 2.7256 / 1.1085 /
0.46765 against the JSON's −190.3333 / 12.58686 / 19.00737 / 7.18264 /
2.72556 / 1.10851 / 0.46765).

| n | 163 | 233 | 283 | 409 | 571 | 65536 |
|---|---|---|---|---|---|---|
| my C_0 (tol 1 bit) | 5 | 6 | 6 | 6 | 7 | 12 |
| reported | 5 | 6 | 6 | 6 | 7 | 12 |

Growth order: my own second-order expansion gives per-coset deficit
`≈ 1/(2·2^{C_0}·ln 2)` (checked against the exact binomial sum: 7.04e−4 vs
7.05e−4 at C_0 = 10), hence `2^{C_0}·C_0 ≳ 0.72 n` and
`C_0 = log2 n − log2 log2 n + O(1)`. Measured: C_0 = 5/7/9/12/16 at
n = 163/571/4096/65536/2^20 against `log2 n − log2 log2 n` =
4.47/5.96/8.42/12.00/15.68 — **Θ(log n) confirmed**.

**A definitional point I hit independently and the producer documents.** The
per-coset deficit is *not* monotone in C_0: under the conditional reading it is
**negative** at C_0 = 1 (−0.333 bits/coset, −190.3 bits total at n = 571),
rises to a maximum at C_0 = 3, and only then halves per step. So "the first
C_0 with Δ ≤ tol" returns **C_0 = 1 at every label** — a cell that passes bound
B trivially while failing bound A catastrophically (m·Pr[empty] = 143 at
n = 571, C_0 = 1). A lower bound on C_0 is only well defined as the *monotone
closure* (least C_0 such that the condition holds at C_0 and every larger C_0).
I arrived at that independently; on opening the code, `bound_B`'s docstring
(lines 169–200) states exactly this reasoning, the threshold is implemented as
the monotone tail, and `non_monotone_cells` is emitted per (n, p) — `[1, 2]` at
n = 571, which reproduces. **Disclosed, not hidden**; the reported values are
the closure values.

### N1(2) Threshold sensitivity — computed, not asserted

| variant | 163 | 233 | 283 | 409 | 571 | max move vs reported |
|---|---|---|---|---|---|---|
| **bound B, tol 1 bit, conditional (reported)** | 5 | 6 | 6 | 6 | 7 | — |
| bound B, tol 0.5 bit | 6 | 6 | 7 | 7 | 7 | **+1** |
| bound B, tol 2 bits | 5 | 5 | 5 | 5 | 6 | **−1** |
| bound B, empty event charged into yield (Σ_{x≥1} P(x) log2 x) | 5 | 6 | 6 | 6 | 7 | **0** |
| bound B, real m = n/C_0 (no ceiling) | 5 | 6 | 6 | 6 | 7 | **0** |
| **bound A, ε = 0.05 (reported)** | 4 | 4 | 4 | 4 | 4 | — |
| bound A, ε = 0.01 | 4 | 4 | 4 | 4 | 4 | **0** |
| bound A, ε = 0.5 | 3 | 3 | 3 | 3 | 4 | **−1** |

**No defensible alternative in the declared set moves any label by 2 or more.**
The plan's breaking artifact for this item does not fire, and the Coordinator's
prior ("at most 1 under ε = 0.01 or a 0.5-bit tolerance") holds — indeed
ε = 0.01 moves nothing at all. The alternative conditioning the prior asked
about (charging the empty event into yield rather than conditioning on
non-emptiness) moves **nothing**, because the two definitions differ materially
only at C_0 ≤ 3 (0.167 vs 0.044 bits/coset at C_0 = 2) and agree to 6e−5 bits
from C_0 = 4 upward, i.e. everywhere at or above the threshold. Both have the
same growth order, as the prior expected.

### N1(3) Three enumeration cells recomputed with my own GF(2^n)

Independently derived membership criterion (scratch `own_enum.py`, written
before opening `binary_field.py`): for `y² + xy = x³ + Ax² + B`, x = 0 is always
in the image (squaring is a bijection in char 2), and for x ≠ 0 the substitution
y = xu gives `u² + u = x + A + B·x^{−2}`, solvable iff `Tr(x + A + Bx^{−2}) = 0`.
V = span{1, x, …, x^{k−1}} is the integer range 0..2^k−1 in the polynomial
basis, so the coset index is `e >> k` and there are 2^{n−k} cosets. My own
carry-less multiply/reduce, my own trace vector over the polynomial basis, and
my own exp/log tables (x is a generator for all three moduli).

| cell | my x-image | JSON `x_image_size_exact` | my δ | JSON `measured_delta` | my cosets | my empty (structured V) | JSON structured V | match |
|---|---|---|---|---|---|---|---|---|
| n = 16, k = 2 | 32718 | 32718 | 0.49923706 | 0.49923706 | 16384 | **1023** | 1023 | ✔ |
| n = 18, k = 3 | 130812 | 130812 | 0.49900818 | 0.49900818 | 32768 | **129** | 129 | ✔ |
| n = 20, k = 2 | 524953 | 524953 | 0.50063419 | 0.50063419 | 262144 | **16066** | 16066 | ✔ |

Exact, cell for cell, from the recorded (seed-derived) modulus and (A, B). I
also reproduced the binomial prediction as `2^{n−k}·(1−δ)^{2^k}`
(1030.2643196722124 / 130.04540854637753 / 16301.033018294691 — identical to
the JSON), and confirmed a sampling-without-replacement (hypergeometric)
variant differs by under 0.1 cosets, so the prediction's form is not
load-bearing. The report's worked example also reproduces: n = 20, k = 3 gives
structured 496, random-V mean 540.75, predicted 514.615, null 519.0 ± 19.34.

### N1(3, z-scores) Which variance — the one item I flag

Every reported z reproduces exactly from the JSON's own counts (scratch
`own_zscores.py`, `own_zscores.json`):

* `null_sd` is the **population** SD (ddof = 0) of the 16 null draws (8 under
  structured V + 8 under random V) at every cell.
* `curve_minus_null_in_null_sd` = (mean of the **5** curve draws − mean of the
  **16** null draws) / `null_sd`. Reproduced to 1e−9 at all 24 defined cells;
  mean 0.03666 and max |z| 1.236383 match `comparison` exactly.
* The structured-V single-draw z = (structured count − null mean)/`null_sd`;
  max |z| = 2.0897203954385066 at (n = 20, k = 2), matching exactly, and it is
  the only cell beyond 2 SD.
* Four cells — (8,4), (10,4), (12,4), (14,4) — have all-zero counts, hence
  `null_sd = 0` and `z = None`; the JSON correctly carries 24 values, not 28.

**The flag.** The *pooled* statistic divides a **difference of two means** by
the SD of a **single draw**. It is not a difference-of-means test statistic:
the standard error under independence is `null_sd·√(1/5 + 1/16) = 0.512·null_sd`,
so the reported figure understates |z| by a factor ≈ 1.95. Recomputing with
that SE, **one of the 24 cells exceeds 2 SD** — (n = 10, k = 1) at z = 2.413 —
against the report's "no cell beyond 2 SD". Mitigations, all checked: the JSON
names the variance it uses in the field name itself
(`curve_minus_null_in_null_sd`); 1 cell in 24 at |z| > 2 is 1.09 expected by
chance and none exceeds 3 SD; against the *theoretical* binomial SD of one draw
the structured-V outlier softens to −1.90 and **no cell exceeds 2 SD**, so the
"one chance cell" reading survives the variance change; and both the JSON
(`reading`) and the report decline any verdict on HEUR-1. So this is a
**reporting imprecision in a sentence that reads as a significance claim, not a
defect in the arithmetic, and nothing in the run rests on it.** I record it
because the plan named this exact item.

Related, and not a defect: `null_sd` is systematically *below* the theoretical
binomial SD at k = 1 (179.1 vs 313.2 at n = 20; 16.2 vs 39.2 at n = 14). That
is the expected signature of a null drawn as a **fixed-size random subset**
(sampling without replacement) rather than i.i.d. Bernoulli, which is what the
contract declares, so the null is the object the contract asked for.

### N1(4) The "second reading", recorded and not adjudicated

`c0-lower-bound.json.closed_forms.two_readings_of_the_parenthesis` states both
readings, says in terms "BOTH are reported and neither is asserted to be the
intended one", and records that under the SEARCHED reading "neither bound
constrains C_0 and 'fix k = C_0 a small natural number' is available at every
C_0 ≥ 1". Each (n, p) row additionally carries a quantified
`searched_coset_reading_at_C0_2` block (at n = 571: log2 cosets available 569.0
against log2 needed 8.16; selection cost 2^10.25 field ops against a factor base
of 2^10.16 the algorithm pays anyway). The task-report §1 repeats it as "Second
reading recorded, not adjudicated". **Recorded faithfully as a reading, not
adjudicated.** I do not adjudicate it; that is B2 and is not mine.

### N1 verdict — **holds** (see below for N2–N4)

Both closed forms evaluate to the reported values under my independent
implementation, the reported growth orders follow from my own asymptotics, no
defensible tolerance or conditioning alternative moves a label by 2 or more, and
all three recomputed enumeration cells match exactly. The single flagged item
(the pooled z's divisor) changes no value in the run and no statement the run
makes, and the variance actually used is named in the artifact.

---

## N2 — the vOW baseline charge and the metric definitions — **HOLDS**

### N2(1) The four committed definitions, read first, and my own Pareto minima

Read before touching the run, in this order: the four metric NAMES in
`experiments/EXP-SEMBIN-f4a17b/specification.yaml` (`inputs.cost_metrics`); the
four metric DEFINITIONS in `COST-SEMBIN-8d123b.metrics_defined`; and
`EV-SEMBIN-71e5cd` O-6/O-7. The committed definitions, quoted:

* `time_only_zero_memory_weight` — "time alone; memory free on both sides".
* `time_memory_product` — "time * memory".
* `area_time_AT` — "**area * time with area taken as memory; identical to the
  product here because no separate area term is modelled for the processor
  array**", with the disclosure "AT and the time-memory product **coincide in
  this table by construction**. They are reported separately so that a reader
  is not misled into counting them as two independent confirmations."
* `equal_rate_max_of_time_and_memory` — "max(time, memory)".

My own derivations from `T = W(1/M + 1/w)`, `Mem = 3n·max(w,M)`,
`W = 0.886·2^{n/2}` (scratch `own_vow.py`):

* **Product.** `T·Mem = 3nW(max(w,M)/M + max(w,M)/w)`. For w ≥ M this is
  `3nW(w/M + 1) ≥ 6nW`; for M ≥ w it is `3nW(1 + M/w) ≥ 6nW`. So the minimum is
  **exactly 6nW**, attained anywhere on w = M — invariant along the ray, as O-6
  states.
* **Equal rate.** For a memory ceiling S = max(w,M) the best time is w = M = S,
  giving T = 2W/S; minimising max(2W/S, 3nS) balances at S = √(2W/(3n)) and the
  value is **√(6nW)**.
* **Time only.** With memory free, T falls without bound in M, so there is no
  interior minimum; the run's *declared* convention M = 1, w → ∞ gives
  **T = W**, total sequential work.
* **AT.** Under the committed definition (area = memory, no processor area)
  AT ≡ T·Mem identically, so its minimum is **6nW**, the same expression.

| n | time_only = W | product = 6nW | equal rate = √(6nW) | AT (committed) |
|---|---|---|---|---|
| 163 | 81.3254 | 91.2591 | 45.6295 | 91.2591 |
| 233 | 116.3254 | 126.7745 | 63.3873 | 126.7745 |
| 283 | 141.3254 | 152.0550 | 76.0275 | 152.0550 |
| 409 | 204.3254 | 215.5863 | 107.7931 | 215.5863 |
| 571 | 285.3254 | 297.0677 | 148.5338 | 297.0677 |

**Checked against every cell: 320 cells × 8 margin keys = 2560 comparisons, 0
mismatches above 1e−9 bits.** Every cell's `vow_operating_point` string matches
the metric it is charged under, with no exceptions across the surface.

**The AT question the prior asked.** The prior expected AT ≠ T×M off the w = M
ray *if processors carry area*, with a difference of "a few bits at most", and
set the break at > 3 bits at n = 571. Under the **committed** definition the
answer is not a small constant but **exactly 0.000 bits**, verified over all
640 (cell, memory-reading) pairs: `area_time_AT` and `time_memory_product`
margins are bit-identical. The producer's identical treatment is therefore
*faithful to the committed definition*, and `EV-SEMBIN-71e5cd` O-11 has already
recorded the coincidence as a design defect in the contract rather than a
producer choice.

I computed the counterfactual anyway, since the prior asked for a number. With
`A = 3n·max(w,M) + c·M` (processors carrying c bits of area each), minimising
A·T numerically over (log2 w, log2 M) ∈ [0,400]² at n = 571 gives an offset
above 6nW of **+1.00 bit at c = 3n** (one point of state per processor),
**+2.00 at c = 10n**, **+4.54 at c = 100n**, **+9.09 at c = 3n·2^10**, with the
argmin drifting off the w = M ray as c grows. Direction matters and is the
point: charging processor area **raises** vOW's AT charge, which makes
`margin = Nagao − vOW` *more* negative and would create *more* flagged cells.
The committed no-processor-area reading is therefore the one **less** favourable
to Nagao, and the prior's break condition cannot fire in the direction that
would matter.

### N2(2) Is each side charged under the same convention?

Recomputed at every cell from `column_definitions`, against the `margins`
blocks — **0 mismatches in 2560 checks**:

| metric | Nagao side as charged | vOW side as charged | same function? |
|---|---|---|---|
| `time_only` | `time_log2_total` | W (total sequential work) | yes — total work both sides |
| `time_memory_product` | `time + T5` (log-domain sum = product) | 6nW (product at its min) | yes — product both sides |
| `area_time_AT` | `time + T5`, identical to above | 6nW, identical to above | yes, and identical by the committed definition |
| `equal_rate_max` | `max(time, T5)` | √(6nW) = max(T, Mem) at its min | yes — max both sides |

**The plan's break condition — "a max on one side against a sum on the other" —
does not fire.** Margins equal `nagao_metric_log2 − vow_pareto_minimum_log2` and
`nagao_ahead` equals `margin < 0` at every one of the 2560 checks.

**The one asymmetry I do find, quantified, with its sign** (scratch
`own_symmetry.py`). vOW's (time, memory) pair is *chosen from its own
parallelism curve* under each metric; the Nagao side is *evaluated at its single
modelled point*, because the run models no parallelism for the decompose step.
The `vow_baseline` block explains only the vOW half of that. Nagao's decompose
step is #Fb independent attempts, so M solvers with their own working sets give
`time/M` and `M·memory`. Under that identical treatment:

* `time_only`, `time_memory_product` and `area_time_AT` are **invariant — the
  largest shift over all 320 cells is 0.000 bits**, because total sequential
  work and the time–memory product are both unchanged by M on either side. **All
  114 of the 120 flagged cells that come from T×M or AT are untouched by this
  asymmetry.**
* `equal_rate_max` is the only affected metric: `min_M max(time/M, M·mem)`
  = `(log2 time + log2 mem)/2`, a shift of up to **−83.0 bits** (n = 571,
  ω = 3.0, C_0 = 3, frozen width). Worked representative cell (n = 571,
  ω = 2.807, C_0 = 8, binomial, frozen): charged margin **+24.635**, under
  identical treatment **−33.627** — an asymmetry of **−58.26 bits running
  AGAINST Nagao as charged**. Across the grid it would turn **112 flags ON and
  0 OFF**.

So the single convention asymmetry in the run is **strictly conservative with
respect to the escalation flag**: it is exactly zero for the metrics that
produce the product/AT flags, and for equal rate it understates Nagao. It is a
disclosure gap, not a defect that could manufacture a flagged cell.

### N2(3) The time-only charge, O-6 and O-7 against the committed records

* **Time-only at the five labels.** My `0.886·2^{n/2}` gives 81.325379,
  116.325379, 141.325379, 204.325379, 285.325379. `COST-SEMBIN-8d123b`
  `parameter_sets[*].vow_time_log2` carries 81.3254, 116.3254, 141.3254,
  204.3254, 285.3254 — agreement to **2.14e−5 bits**, which is exactly the
  rounding of the committed record to four decimals. The run's own
  `vow_pareto_minimum_log2` under `time_only` equals my full-precision value at
  every cell.
* **A correction to the plan, not to the run.** The plan's N2(3) says to check
  the time-only charge against "`CORR-20260913-53739b`'s `vow_time_log2`".
  **`CORR-20260913-53739b` contains no `vow_time_log2` field and no vOW figure
  at all** — I grepped the correction and its own
  `coordinator-rederivation-53739b/rederivation.txt`, with no hits. The
  correction is about the Semaev-side yield charge and the floor coefficient.
  The committed source of the time-only vOW figure is
  `COST-SEMBIN-8d123b.parameter_sets`, which is what I checked against. This is
  a mislabelled source in the review plan; it is the same species of error as
  `DEC-20260913-74e208` PD-1 records for the parent round, at far smaller
  stakes, and it does not touch the run.
* **O-6's exactly-29.0 bits, derived myself.** The dominated charge is memory of
  a 2^30-point store with the time of one processor, i.e. `W · 3n · 2^30`
  against the minimum `6nW`. The ratio is `(3n·2^30·W)/(6nW) = 2^30/2 = 2^29`,
  **so n and W cancel and the overcharge is exactly 29 bits at every label** —
  which is why O-6 measured the same number at n = 283, 310, 409 and 571. My
  numeric evaluation returns 29.000000 at all four. `reproduction.json` carries
  four `O6_dominated_charge_overcharge_bits[n=…]` cells with target 29.0,
  reproduced 29.0, `abs_error_bits` 0.0 — **the committed figure, not a
  transcription of something near it**.
* **O-7.** `O7_crossover_vow_at_minimum` 520 dense / 460 sparse and
  `O7_crossover_both_at_own_minimum` 518 dense / 460 sparse reproduce as exact
  integers; `O7_margin_at_409_coherent` −37.7946 / −17.4825 and
  `O7_margin_at_571_sparse_coherent` +40.4889 reproduce against EV-SEMBIN-71e5cd's
  printed −37.79 / −17.48 / +40.49 within 0.0046 bits. Reusing the uncorrected
  baseline call — the parent round's largest single defect — did **not** happen.

### N2(4) The unit-conversion disclosure

Direction, by my own one-line reasoning: Nagao's T1 + T2 = ω·log2(monomials)
counts operations in a Macaulay linear algebra **over F_2**, i.e. bit
operations, while vOW's W counts **elliptic-curve group operations over
F_{2^n}**, each costing at least one F_{2^n} multiplication, i.e. between
~n log n and ~n² bit operations. Putting both sides in one unit therefore adds
bits to **vOW** and ~0 to Nagao. **The stated direction ("moves the comparison
in Nagao's favour; the figures as reported are PESSIMISTIC for Nagao") is
right.**

Magnitude: the block carries **both ends per label** —
`bits_that_would_be_added_to_vow_if_a_group_op_cost_n_squared` (14.697 … 18.315)
and `..._if_a_group_op_cost_n_log_n` (10.226 … 12.352), and I reproduce both as
`2 log2 n` and `log2(n log2 n)`. **It is stated as a range**, so the prior's
concern is answered. One imprecision: the task-report's scope statement quotes
only the ≈ 2 log2 n end ("≈ 2 log2 n bits") while pointing at the block that
holds both; the larger end overstates how pessimistic the table is. Minor and
self-correcting on reading the artifact.

### N2 verdict — **holds**

All four Pareto minima re-derive to the run's baseline charge at every one of
2560 (cell, margin) checks; AT and T×M are identical *because the committed
definition makes them identical*, so the plan's > 3-bit break cannot fire, and
the counterfactual that would separate them runs against Nagao; the metric
function is applied symmetrically on both sides; the committed time-only figures
and O-6's exactly-29.0-bit overcharge reproduce, the latter also from my own
derivation. The one asymmetry found (parallelism modelled only on the vOW side)
is exactly 0 bits for the product and AT metrics and conservative for equal
rate.

---

## N3 — the reproduction gate and the controls' integrity — **HOLDS**

Scratch: `own_n3.py` (`own_n3.json`), `own_n3b.py` (`own_n3b.json`),
`own_driverdiff.py`.

### N3(1) Gate cells picked by me from the committed records

I chose **23 cells** directly from the three committed records — 11 from
`COST-SEMBIN-8d123b.yaml`, 8 from `CORR-20260913-53739b.yaml`, 4 from
`EV-SEMBIN-71e5cd.yaml` — spanning all four tolerance classes the run uses
(8 integer / list cells, 6 four-decimal cells at 1e−3, 6 two-decimal cells at
5e−3, 3 one-decimal cells at 5e−2). For every one, the target `reproduction.json`
carries **is** the committed number (line-cited below), and the reproduced value
is within the declared tolerance of my own reading of the record. **No
transcription defect; the gate passed against the right figures.**

| cell | source : line | committed | JSON target | reproduced | |err| | decl. tol | literal 1e−3? |
|---|---|---|---|---|---|---|---|
| `semaev_time_log2[n=163]` | COST :62 | 123.7697 | 123.7697 | 123.76966 | 4.0e−5 | 1e−3 | yes |
| `semaev_memory_log2_sparse[n=283]` | COST :86 | 61.9374 | 61.9374 | 61.93742 | 2.1e−5 | 1e−3 | yes |
| `vow_time_log2[n=409]` | COST :99 | 204.3254 | 204.3254 | 204.32538 | 2.1e−5 | 1e−3 | yes |
| `margin_bits_time_memory_dense[n=409]` | COST :101 | −8.7946 | −8.7946 | −8.79462 | 1.6e−5 | 1e−3 | yes |
| `margin_bits_time_memory_sparse[n=571]` | COST :122 | 69.4889 | 69.4889 | 69.48889 | 6.8e−6 | 1e−3 | yes |
| `semaev_optimal_m[n=571]` | COST :118 | 12 | 12 | 12 | exact | int | yes |
| `crossover[time_memory_product,dense]` | COST :131 | 435 | 435 | 435 | exact | int | yes |
| `crossover_published[stage1_vs_bare_rho,unceiled]` | COST :134 | 302 | 302 | 302 | exact | int | yes |
| `crossover_ceiled[total_vs_walk_constant]` | COST :179 | 281 | 281 | 281 | exact | int | yes |
| `per_n_stage1_discrepancy_bits[n=409]` | COST :180 | −8.18 | −8.18 | −8.18182 | 1.8e−3 | 5e−3 | **no** |
| `bits_added_if_bound_is_6[n=571]` | COST :192 | 40.654 | 40.654 | 40.65471 | 7.1e−4 | 1e−3 | yes |
| `stage1[571,12,48,eq11,d_sat=5]` | CORR :114 | 185.5 | 185.5 | 185.47178 | 2.8e−2 | 5e−2 | **no** |
| `reoptimised_total[571,eq11,d_sat=6]` | CORR :115 | 192.8 | 192.8 | 192.84838 | 4.8e−2 | 5e−2 | **no** |
| `reoptimised_argmin_m_k[571,eq11,d_sat=6]` | CORR :116 | [21, 28] | [21, 28] | [21, 28] | exact | list | yes |
| `crossover[eq11,d_sat=7]` | CORR :117 | 393 | 393 | 393 | exact | int | yes |
| `log2_lambda_at_optimum[n=1000]` | CORR :124 | −36.25 | −36.25 | −36.25014 | 1.4e−4 | 5e−3 | yes |
| `m_eq_21_total[omega'=2.376]` | CORR :129 | 203.36 | 203.36 | 203.35884 | 1.2e−3 | 5e−3 | **no** |
| `argmin_total[omega'=3.0]` | CORR :129 | 197.08 | 197.08 | 197.07680 | 3.2e−3 | 5e−3 | **no** |
| `omega_prime_invariant_argmin[omega'=1.0]` | CORR :128 | [18, 32] | [18, 32] | [18, 32] | exact | list | yes |
| `O6_dominated_charge_overcharge_bits[n=310]` | EV :99 | 29.0 | 29.0 | 29.0 | 0 | 5e−2 | yes |
| `O7_crossover_both_at_own_minimum[dense]` | EV :108 | 518 | 518 | 518 | exact | int | yes |
| `O7_margin_at_409_coherent[semaev_sparse]` | EV :104 | −17.48 | −17.48 | −17.48253 | 2.5e−3 | 5e−3 | **no** |
| `O7_margin_at_571_sparse_coherent` | EV :109 | 40.49 | 40.49 | 40.48889 | 1.1e−3 | 5e−3 | **no** |

**The tolerance point, stated exactly.** `specification.yaml` line 142 says
"tolerance: 1e-3 bits per cell" and line 267 says "ARM R failing beyond 1e-3
bits at any cell invalidates ARMS N, K, P, M and I". Over all 107 cells,
**26 exceed a literal 1e−3** (11 one-decimal targets, 15 two-decimal targets;
worst 0.0484 bits at `reoptimised_total[571,eq11,d_sat=6]`, 192.8 vs 192.84838).
**All 26 round to their printed committed target** and are within half a unit of
its printed precision; the 1e−3 class itself is clean, with worst error
0.00086 bits (`bits_added_if_bound_is_5[n=310]`), exactly as the task-report
states. The producer records this as PD-4 (targets checked at their printed
precision, 5e−2 / 5e−3, "declared in code before the arm ran").

My reading, as integrity: a committed target printed to one decimal carries
±0.05 bits of information, so a 1e−3 check against it can pass only by luck —
the frozen contract's tolerance is finer than the precision of the very records
it names as targets, which is a **contract defect**, and PD-4 is the only reading
under which ARM R tests anything at those cells. It is also, by the letter of
the frozen protocol, a **deviation**, disclosed as such; whether it is accepted
as an additive amendment is the Coordinator's ruling and not mine. Nothing in it
changes a reproduced value.

### N3(2) The m!-only control matches no corrected figure

The m!-only (uncorrected) targets are 186.7 / 187.2 / 212.8 / 240.3,
186.4 / 186.5 / 197.1, and 303 / 307 / 347 / 400. **None of the corrected-only
figures** (181.7, 185.5, 192.8, the argmin [21, 28], the crossovers
281 / 295 / 337 / 393) appears among the m!-only matches, and no corrected figure
lies within 0.05 bits of an m!-only reproduced value. The two figures the
uncorrected and corrected tables **share** — 212.8 and 240.3, at d_sat = 6, 7
where `CORR-53739b` changes nothing — are reproduced by the eq. (11) pipeline,
which is correct and is exactly the trivially-true case whose label was fixed
between the two driver executions (N3(6)). Break condition does not fire.

### N3(3) ARM K — the predicted rise, derived myself, at four cells

Under `column_definitions` the d_F = 5 rise is `ω·log2 N` (loose) or
`ω·log2((N+5)/5)` (binomial) on the time side and `log2((N+5)/5)` on the memory
side. My predictions against `known-false-dF5.json`:

| cell (n, ω, C_0, reading) | N | my Δtime | JSON observed Δtime | residual | my Δmem | JSON observed Δmem | residual |
|---|---|---|---|---|---|---|---|
| 163, 2.376, 2, loose | 13203 | 32.52406 | 32.52406 | 1.4e−14 | 11.36720 | 11.36720 | < 1e−11 |
| 283, 2.376, 4, loose | 19810 | 33.91488 | 33.91488 | 7.1e−15 | 11.95238 | 11.95238 | < 1e−11 |
| 571, 2.807, 8, binomial | 40541 | 36.44986 | 36.44986 | 3.4e−11 | 12.98534 | 12.98534 | 1.2e−11 |
| 409, 3.0, 16, binomial | 10225 | 32.99577 | 32.99577 | 5.6e−11 | 10.99859 | 10.99859 | 1.9e−11 |

The JSON's own summary over all 240 cells: every cell rose (min 19.85, max
51.94 bits), max |observed − predicted| 5.7e−14 (time) and 1.1e−14 (memory).
The plan's 1e−6 break does not fire.

**A correction to my own first attempt, recorded.** My first script predicted
the memory rise under the loose reading as `log2 N` and disagreed with the JSON
by 2.32 bits at the two loose cells. That was **my** error: `column_definitions`
fixes T5 as the binomial count C(N+4,4) under **both** readings (the reading
governs T1/T2 only), so the memory rise is `log2((N+5)/5)` irrespective of
reading. The JSON's prediction is the right one.

### N3(4) ARM P — the two odd-characteristic traces

Read from `nearby-object-oddchar.json`: the p = 2, 3, 5 traces are 9-call
sequences with identical function names (`nagao_cell, d_F_bound, m_of,
variable_count, log2_monomials, inverse_yield_bits, log2_monomials,
theorem1_exponent, d_F_bound`). Masking **p only** leaves two differences in
each odd-p trace, both `log2_monomials(reading=binomial, d_F=4)` against
`d_F=10` (p = 3) / `d_F=16` (p = 5); masking p **and the p-derived d_F** makes
the traces identical — which is what the JSON's two flags say
(`..._masking_p_only: false`, `..._masking_p_and_derived_dF: true`). d_F in
trace: 4 / 10 / 16 = Proposition 5 at p = 2 and 3p+1 at p = 3, 5; exponent at
p = 3, ω = 2.807: (6·3+2)·2.807 + 1 = **57.14**, reproduced. The exponent
formula `2·d_F·ω + 1` is shared and only d_F differs, which is the "same
formulas" the spec asks for. The failure signature (8ω+1 or d_F = 4 at p = 3)
is absent. `d_F_bound` necessarily branches on p (Prop. 5 vs Prop. 2); that is
the source's own structure, and the spec locates the failure signature at
p = 3, where it does not appear.

### N3(5) ARM M — what the nulls test beyond the identity

1920 checks: `free_yield` share = T4 to 5.7e−14 bits; `zero_memory` share = T5
(or 0 under `time_only`) to 4.3e−14. **In one sentence:** beyond the identity
"margin − column = null margin", the two nulls test only that T4 and T5 enter
the total once, additively, and feed nothing else in the pipeline (not m, not
N, not λ) — a bookkeeping check that would catch a double charge or an inverted
sign (which is how the parent round's free-yield null earned its place), and
**not** a test of the cost model. That limit belongs in the evidence record, as
the Coordinator's prior anticipated.

### N3(6) Hashes, the snapshot, and the two driver executions

* **Manifest vs disk.** `manifest.yaml` (everything under a `run:` key) lists 19
  artifacts; **19/19 sha256 and 19/19 byte counts match** the files on disk.
  The only run-directory file not in the manifest is `manifest.yaml` itself,
  which cannot list its own hash; it is hashed in the snapshot receipt
  (`25e7aa2a…07737`) and matches.
* **Receipt vs disk.** 27 `path_sha256` entries (7 under `code/`, 20 under the
  run directory): **all 27 match**; the manifest and the receipt **agree on all
  19 shared run files**; all 10 `declared_source_artifacts` are present and
  hashed.
* **Frozen source.** `inputs/NAGAO-2015-984/paper_fulltext.md` hashes to
  `337fae55…13218`, equal to the spec's `frozen_nagao_sha256` and the manifest's
  `frozen_nagao_sha256_verified`.
* **Snapshot commit.** `a2cdafc67` exists, is titled for `TASK-20260913-a10007`,
  descends from the manifest's recorded HEAD `0ac05e30` (PD-3: HEAD moved under
  the run), and `git diff a2cdafc67 -- experiments/EXP-SEMBIN-db9bc3/` is empty
  — **I read committed bytes.** The receipt's `commit_sha: null` is by design
  (a receipt cannot hash the commit that contains it); the binding lives in the
  dispatch queue's `archive` block.
* **Artifact-policy fields present in the manifest:** exact command, commit +
  `dirty: true`, environment and dependency versions (numpy 2.4.4, pyyaml
  6.0.1), seed 20260913 with the per-cell formula, requested policy
  `executor-implementation`, resolved `claude-fable-5-1-thinking-medium`
  (`model_verified: false`, `fallback_used: false`, effort medium), stdout
  3594 B, stderr 0 B, `valid: true`, timestamps, peak RSS 119.6 MB, CPU 5.58 s.
* **Driver diff, `raw-result.json` vs `raw-result.driver-exec-1.json`.** The
  two executions share **42,650 numeric leaves — exactly the task-report's
  "42,650 compared values"**. Of these, **28 differ, all `wall_seconds`
  timing fields**; **0 non-timing numeric or boolean differences**; 2 string
  differences (`arm_k/note`, `attempts[1]/started_at`); 96 keys present in only
  one execution, all inside the four blocks named by the manifest's disclosed
  label fixes. `reproduction.json` vs its exec-1 twin: **0** numeric
  differences, 26 key changes all inside `uncorrected_figures_control`. Both
  executions pass the gate. So the sentence "zero numeric differences across
  42,650 compared values" is **literally inaccurate for 28 timing values and
  correct for every mathematical value**; read as the plan intends (results),
  the break condition does not fire, and I report the 28 so the reader decides.
* **What the "label fixes" did.** They changed the *reading* of two control
  flags: `eq11_pipeline_reproduces_any_uncorrected_figure: true` (exec-1) became
  `…_where_it_differs_from_corrected: false` (exec-2), and
  `arm_p_code_path_identical_after_masking_p: false` was split into
  `…_masking_p_only: false` / `…_masking_p_and_derived_dF: true`. In both cases
  I verified the exec-1 flag read as a control failure for a trivial reason
  (shared figures at d_sat = 6, 7; d_F derived from p), the exec-2 definition is
  the semantically right one, no underlying value changed, and all four fixes
  are disclosed in `manifest.yaml` `protocol_deviations[0]` with the exec-1
  files retained. Integrity holds. But a control whose pass/fail flag is
  redefined after the first execution is a pattern a reader should be able to
  see at once, and the task-report's §9 "label fixes only" undersells that two
  flags flipped; the detail is visible only in the manifest and the retained
  exec-1 files. Listed under "Unexpected".

### N3(7) PD-4 — is "declared in code before the arm ran" verifiable?

**No, not from committed history.** The only commit touching
`experiments/EXP-SEMBIN-db9bc3/code/` is `a2cdafc67`, the post-run snapshot;
attempt 1 wrote nothing to the run directory. What **is** verifiable: the
earliest retained artifact is exec-1 (19:52:57Z), and its per-cell tolerances
and `tolerance_policy` text are **identical** to exec-2's, so the policy
predates both retained executions. Whether it predates any unretained ARM R
run cannot be established. **Unverifiable, not a break** — as the prior
expected. One wording flag: the manifest's PD-1 field
`numbers_changed_between_executions: "none expected; verified by the reviewer
against the retained exec-1 files"` asserts a reviewer verification that had
not happened when the manifest was written. It has now (this section); the
phrase should have read "to be verified".

### N3 verdict — **holds**

Every one of 23 gate targets I read off the committed records myself is the
number the gate was run against and reproduces within its declared tolerance;
the m!-only control matches no corrected figure; ARM K's rise matches my own
prediction to ≤ 6e−11 bits; ARM P's traces are identical after masking p and
the p-derived d_F; ARM M's nulls are the identities they claim to be; every
hash in the manifest and the receipt matches the bytes on disk and the snapshot
commit; and the two driver executions differ in no mathematical value. The 26
cells that fail a literal 1e−3 fail only because the contract's tolerance is
finer than its targets' printed precision — a disclosed deviation for the
Coordinator to rule on.

---

## N4 — the surface's arithmetic, the flag counts and the spreads — **HOLDS**

Scratch: `own_n4.py` (`own_n4.json`), `own_n4b.py` (`own_n4b.json`),
`own_n4c.py` (`own_n4c.json`), `own_monotone.json`. All columns recomputed
from `cost-surface.json`'s `column_definitions` text and the hypothesis, with
my own log-domain code (my `deficit()` is the exact binomial sum to 2^17 and
the checked asymptotic `1/(2·2^{C_0} ln 2)` beyond).

### N4(1) Six cells recomputed from the definitions

T1 = log2 monomials under the reading (`4·log2 N` loose, `log2 C(N+4,4)`
binomial, N = n(m−1), m = ceil(n/C_0)); T2 = (ω−1)·T1; T3 = log2(m·2^{C_0}+1);
T4 = −log2(1 − e^{−λ}), log2 λ = m·C_0 − n − m·deficit(C_0); T5 = log2 C(N+4,4)
(frozen) or 2× (dense); T6 = ω·T3; time = (ω·T1 + T3 + T4) ⊕ T6 (log-add).

| (n, ω, C_0, reading) | m | N | T1 | T2 | T3 | T4 | T5 frozen | T5 dense | T6 | time | worst |mine − JSON| over T1..T6, time, 8 margins |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 163, 2.376, 3, loose | 55 | 8802 | 52.414 | 72.122 | 8.785 | 3.538 | 47.831 | 95.662 | 20.872 | 136.859 | 3.6e−11 |
| 163, 3.0, 8, binomial | 21 | 3260 | 42.102 | 84.204 | 12.393 | 0.000 | 42.102 | 84.204 | 37.178 | 138.699 | 1.8e−11 |
| 571, 2.376, 3, binomial | 191 | 108490 | 62.324 | 85.758 | 10.578 | 17.007 | 62.324 | 124.648 | 25.134 | 175.668 | 1.5e−10 |
| 571, 2.376, 16, loose | 36 | 19985 | 57.147 | 78.634 | 21.170 | 0.000 | 52.562 | 105.125 | 50.300 | 156.950 | 2.6e−11 |
| 571, 3.0, 8, binomial | 72 | 40541 | 56.644 | 113.288 | 14.170 | 0.000 | 56.644 | 113.288 | 42.510 | 184.101 | 7.7e−11 |
| 571, 3.0, 16, binomial | 36 | 19985 | 52.562 | 105.125 | 21.170 | 0.000 | 52.562 | 105.125 | 63.510 | 178.857 | 6.4e−11 |

Not six but **all 320 cells**: worst per-column disagreement T1 3.7e−10, T2
7.5e−10, T3 3.6e−15, T4 4.8e−11, T5 3.7e−10 / 7.5e−10, T6 1.4e−14, time
1.1e−9, log2 λ 2.3e−8; N and m exact; worst margin disagreement **1.9e−9 bits**
over 2560 (cell, margin) pairs; **0 `nagao_ahead` flag disagreements**. The
plan's 0.05-bit break is five to eight orders of magnitude away.

### N4(2) The escalation counts under my own filter

Filter: cell at a FIPS label, metric ∈ {T×M, AT, equal rate}, either memory
reading, `margin < 0`. **242.** Restrict to ω ∈ {2.376, 2.807, 3.0}: **180.**
Restrict further to C_0 ≥ bound B at that n — using **my own** bound-B values
5 / 6 / 6 / 6 / 7 from N1, not the JSON's flags: **120.** All three reproduce.

Where the 120 sit (my distribution, cells = (metric, reading) pairs):

| n | ω | T×M frozen | T×M dense | AT frozen | AT dense | ER frozen | ER dense | C_0 and reading |
|---|---|---|---|---|---|---|---|---|
| 409 | 2.376 | 10 | 0 | 10 | 0 | 0 | 0 | C_0 ∈ {6,8,10,12,16}, both readings |
| 409 | 2.807 | 4 | 0 | 4 | 0 | 0 | 0 | C_0 ∈ {8,10,12,16}, binomial only |
| 409 | 3.0 | 1 | 0 | 1 | 0 | 0 | 0 | C_0 = 16, binomial; margin **−0.103** bits |
| 571 | 2.376 | 8 | 8 | 8 | 8 | 3 | 3 | C_0 ∈ {8,…,16} both readings; ER: C_0 ∈ {10,12,16} binomial |
| 571 | 2.807 | 8 | 7 | 8 | 7 | 0 | 0 | dense drops (8, loose) |
| 571 | 3.0 | 8 | **3** | 8 | **3** | 0 | 0 | dense: C_0 ∈ {10,12,16}, binomial |
| | **sum** | 39 | 18 | 39 | 18 | 3 | 3 | = 120 |

Against the report's description: "n = 409 frozen width only" ✔ (0 dense
flags at 409); "C_0 ≥ 8 at ω = 2.807, ≥ 6 at 2.376, = 16 at 3.0 by 0.1 bits" ✔
(−0.1031); "6 equal-rate at ω = 2.376, C_0 ≥ 10" ✔ (3 frozen + 3 dense, C_0 ∈
{10, 12, 16}, binomial reading only); "42 T×M + 42 AT" at 571 ✔ (24 + 18 each).
**One wording inaccuracy:** "under both memory readings for ω ≤ 2.807 and under
frozen width at ω = 3.0" — there are **3 T×M + 3 AT dense-width flags at
ω = 3.0, n = 571** (C_0 = 10, 12, 16, binomial), which the report's own next
sentence states ("negative from C_0 = 10"; I read −4.33 bits at C_0 = 10 and
+0.32 at C_0 = 8, the report's "within 0.3"). The counts are right; the clause
is not.

### N4(3) T6 at every one of the 120 flagged cells

`max(T6 − time)` over the 120 = **−87.22 bits** (at n = 409, ω = 2.376,
C_0 = 16, T×M frozen: T6 = 49.18 against time = 136.40). Largest T6 anywhere in
the 120 is **63.51 bits** (C_0 = 16, ω = 3.0 — exactly the "ω × 21 bits" the
prior asked to have read off rather than assumed), against a smallest time
column of 136.40. **No flagged cell has T6 within 10 bits of time**; the
nearest is 87 bits away. T6 is negligible at every flagged cell, as read.

### N4(4) The crossover surface and the non-monotone cells

* **Crossovers.** 24 randomly sampled `crossover_surface` entries (of 512)
  recomputed by my own first-sign-change scan over [16, 2000]: **24/24 match**
  `crossover_n`. No entry has a null crossover. The task-report's range table
  reproduces exactly for all eight rows, e.g. time-only/binomial 244–399 over
  all C_0 and 244–338 over bound-B C_0; T×M/binomial/dense 457–697 and 457–572;
  equal-rate/loose 614–1039 and 614–820.
* **The `monotone_for_200_beyond` flag.** 194 of 512 entries are flagged
  `false` (C_0 = 2: 52, 3: 62, 4: 60, 6: 16, 8: 2, 12: 2). My independent
  step-1 scan over [crossover, crossover + 200] agrees with the JSON's flag on
  **all 512 entries, 0 disagreements** (318 monotone, 194 not;
  `own_n4c.json.monotone_flag_full_check` — the earlier `own_monotone.json`
  reached the same 0 disagreements from an inline one-off whose script was not
  preserved, so the preserved script re-does it). The plan asked for two cells at
  C_0 = 3; representative, my step-1 margins: (ω = 2.376, C_0 = 3, time-only,
  loose) crossover 325: −0.204, **+0.337, +0.879**, −1.339, −0.798, −0.257,
  −2.477, … at n = 325 … 331 (rise ≈ 0.54 bit/n for two steps, drop ≈ 2.2 when
  m increments), then −17.56 at n = 375, −38.21 at 425, **−77.84 at n = 525**;
  (ω = 2.376, C_0 = 4, T×M frozen, loose) crossover 413: −1.464, −0.996, −0.490,
  **+0.034** (n = 416), −3.043, … then −19.62 at 463, −41.84 at 513, **−83.68 at
  n = 613**.
* **What the non-monotonicity is — characterised over all 194, not asserted.**
  Every re-excursion is confined to **≤ 11 units of n** after the crossover
  (last positive offset by C_0: 2 → 3, 3 → 8, 4 → 11, 6 → 5, 8 → 2, 12 → 2) and
  has amplitude **≤ 2.29 bits** (by C_0: 0.75 / 1.51 / 2.29 / 0.91 / 0.16 /
  0.05); beyond that the margin is monotone to +200. Recomputing the same
  margins with **real m = n/C_0 (no ceiling)**: **0 of 194** entries re-cross
  after their own first crossing. So the non-monotonicity is entirely the
  **ceiling saw-tooth in the yield slack m·C_0 − n ∈ [0, C_0)** inside T4 (T4
  rises ~1 bit per unit n while m is fixed and drops by ≈ C_0 − deficit when m
  increments), superposed on vOW's smooth 0.5 bit/n. The flag is correctly
  computed and the phenomenon is real under the run's declared `m = ceil(n/C_0)`;
  the task-report's *explanation* — "because T4 grows linearly in m at fixed
  small C_0 (17.0 bits at n = 571, C_0 = 3)" — names the right term but the wrong
  mechanism: the linear-in-m Jensen deficit is why Nagao is expensive at small
  C_0, not why the crossover wiggles. The Coordinator's prior ("T4 grows with m
  at fixed slack") has the same imprecision. Neither affects a value.

### N4(5) Spreads at n = 571

Recomputed from the cells for all 16 (metric, memory reading, monomial
reading) keys; worst disagreement with `spreads_at_n_571` **1.9e−9 bits**:

| | time-only | T×M / AT frozen | T×M / AT dense | equal rate |
|---|---|---|---|---|
| C_0 spread over the declared range | **36.88** | **48.99** | **61.09** | 36.88 |
| C_0 spread over bound-B-satisfying C_0 only | **5.25** | **9.33** | **13.41** | 5.25 |
| ω spread (loose / binomial), any C_0 | 43.21 / 40.35 | 43.21 / 40.35 | 43.21 / 40.35 | 43.21 / 40.35 |

Reported: 36.9 / 49.0 / 61.1; 5.2 / 9.3 / 13.4; 40.4 / 43.2 — all reproduce.
The theorem-form n^{8ω+1} ω-spread **45.71** bits reproduces to the last digit
(`(8·(3.0 − 2.376))·log2 571 = 4.992 × 9.157`).

### N4 verdict — **holds**

All 320 cells recompute from the definitions to ≤ 1.9e−9 bits in every column
and every margin; 242 / 180 / 120 reproduce under my own filter and my own
bound-B values with the stated distribution; T6 is ≥ 87 bits below the time
column at every flagged cell; 24/24 sampled crossovers and 512/512 monotonicity
flags reproduce, with the non-monotonicity shown to be the ceiling saw-tooth in
the yield slack; the spreads reproduce to 1e−9. The two imprecisions found (the
"frozen only at ω = 3.0" clause; the mechanism sentence for the non-monotone
crossovers) change no number and no flag.

---

## Unexpected — everything I did not expect to find, in one list

1. **N3(6)** The two driver executions differ in the *definition* of two
   control flags, not only in labels: `eq11_pipeline_reproduces_any_uncorrected_figure`
   read **true** in exec-1 (trivially, via the two figures shared by the
   corrected and uncorrected tables) and its exec-2 replacement reads **false**;
   `arm_p_code_path_identical_after_masking_p` read **false** and was split into
   a false and a true flag. Verified benign, fully disclosed in
   `manifest.yaml` `protocol_deviations[0]`, exec-1 files retained; but the
   task-report's "label fixes only" undersells it.
2. **N3(6)** "Zero numeric differences across 42,650 compared values" is
   literally false for 28 of the 42,650 — all `wall_seconds` — and true for
   every mathematical value.
3. **N3(1)/(7)** 26 of 107 gate cells exceed the spec's literal 1e−3 because the
   contract's tolerance is finer than the committed targets' printed precision;
   PD-4's widened per-cell tolerance is disclosed and is not verifiable as
   pre-run from committed history. Coordinator's ruling, not mine.
4. **N3(7)** The manifest asserts "verified by the reviewer against the
   retained exec-1 files" before any reviewer existed.
5. **N3(3)** My own first ARM K memory-rise prediction under the loose reading
   was wrong by 2.32 bits (I applied the reading to T5, which the definitions
   fix as binomial); the JSON was right. Recorded against myself.
6. **N4(4)** The 194 non-monotone crossovers are a ceiling saw-tooth in the yield
   slack confined to ≤ 11 units of n and ≤ 2.29 bits; with real m none re-cross.
   The producer's (and the prior's) mechanism sentence is imprecise.
7. **N4(2)** The report's "frozen width at ω = 3.0" clause omits 6 dense-width
   flags at ω = 3.0, n = 571 (C_0 ≥ 10, binomial), which its next sentence
   admits.
8. **N1(3)** The pooled ARM C z-score divides a difference of means by a single
   draw's SD; with the difference-of-means SE one cell of 24 exceeds 2 SD against
   the report's "no cell beyond 2 SD". Reporting imprecision; no value rests on it.
9. **N1(1)** Bound B is non-monotone in C_0 (negative deficit at C_0 = 1), so the
   reported bound is the monotone closure; the code documents this and emits
   `non_monotone_cells`. I reached the same definition independently first.
10. **N2(3)** The review plan's N2(3) points at `CORR-20260913-53739b` for
    `vow_time_log2`; that record contains no vOW figure. The committed source is
    `COST-SEMBIN-8d123b.parameter_sets`, which is what I checked. Plan
    mislabel, not a run defect.
11. **N2(1)** AT and T×M margins are *bit-identical* across all 640 pairs
    because the committed definition makes them identical; the prior's "a few
    bits" cannot appear. The counterfactual with processor area runs *against*
    Nagao.
12. **N2(2)** Parallelism is modelled only on the vOW side; under identical
    treatment the equal-rate margin would move by up to −83 bits *against*
    Nagao (112 flags on, 0 off) and the product/AT margins by exactly 0.

## What I did not do

* No statement about any curve's security, in either direction. No degree
  measured or asserted (`IMP-SEMBIN-ENGINE`). No verdict on HEUR-1, on the
  "second reading" of the parenthesis (B2), or on the significance of the 120
  flagged cells (B1).
* I did not open `inputs/NAGAO-2015-984/paper_fulltext.md` or
  `inputs/SEMAEV-2015-310/` in this attempt beyond hashing the Nagao file: no
  N1–N4 item required them — the N1 model comes from HEUR-1 in
  `H-SEMBIN-4a80f3`, the N4 definitions from `column_definitions`, and the N3
  targets from the three committed records.
* No citations to literature are made in this report, so no provenance tags
  are needed; every number above is `internal` and traceable to a scratch file.

## Sources read (every path, honestly)

Contract and plan:
`AGENTS.md`; `CLAUDE.md`; `agents/validator.md`;
`coordination/review/sembin-20260913-251fd3/review-plan.yaml`;
`coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/dispatch_queue.json`
(the `TASK-20260913-3b91d0` entry and the `TASK-20260913-a10007` archive block);
`coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/archives/TASK-20260913-a10007/snapshot-receipt.json`.

Hypothesis, specification, committed targets and definitions:
`ledger/hypotheses/H-SEMBIN-4a80f3.yaml`;
`experiments/EXP-SEMBIN-db9bc3/specification.yaml`;
`experiments/EXP-SEMBIN-f4a17b/specification.yaml`;
`experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/COST-SEMBIN-8d123b.yaml`;
`ledger/corrections/CORR-20260913-53739b.yaml`;
`ledger/evidence/EV-SEMBIN-71e5cd.yaml`;
`coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/coordinator-rederivation-53739b/rederivation.txt` (grepped for `vow_time_log2` only).

Run package `experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/`:
`task-report.md`; `manifest.yaml`; `cost-surface.json`; `c0-lower-bound.json`;
`reproduction.json`; `reproduction.driver-exec-1.json`; `known-false-dF5.json`;
`nearby-object-oddchar.json`; `matched-nulls.json`;
`independent-memory-term.json` (hashed; contents not needed for N1–N4);
`selftest.json` (hashed); `raw-result.json`; `raw-result.driver-exec-1.json`;
`manifest.driver-exec-1.yaml`, `concrete-cost.yaml`, `implementation.md`,
`command.txt`, `environment.json`, `stdout.log`, `stderr.log` (hashed and
byte-counted only).

Producer code `experiments/EXP-SEMBIN-db9bc3/code/`:
`arm_c_coset.py` and `binary_field.py` — opened and read **after** my own
bound and enumeration code had run (N1 sequencing); `semaev_repro.py` and
`run_experiment.py` — opened for the PD-4 tolerance lines; every `*.py` in the
directory was additionally scanned programmatically for tolerance strings by
`own_n3.py` and hashed against the receipt.

Frozen source: `inputs/NAGAO-2015-984/paper_fulltext.md` (sha256 only).

Git: `git cat-file`/`git log`/`git merge-base`/`git diff` on `a2cdafc67` and
`0ac05e30`, read-only.

Not read: `coordination/review/sembin-20260913-251fd3/TASK-20260913-7fb774/`,
`.../TASK-20260913-f6652f/`, `coordination/bus/`.
