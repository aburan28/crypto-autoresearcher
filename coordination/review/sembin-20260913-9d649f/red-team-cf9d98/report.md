# Red-team report — REVIEW-SEMBIN-20260913-9d649f, joints J2, J3, J5, J6

- **Task:** TASK-20260913-cf9d98 · **Role:** red-team · **Policy:** review-adversarial, xhigh
- **Under review:** RUN-SEMBIN-121b59 / COST-SEMBIN-8d123b (CLAIM A) and RUN-SEMBIN-aa5161 (CLAIM B)
- **Joints owned:** J2, J3, J5, J6. **J1 and J4 are not mine and no verdict here bears on them.**
- **Blindness honoured:** I read nothing under `validator-da3982/` or
  `blind-rederivation-ec11c4/`. Neither directory existed in the tree when I began; both
  are present in it now and I did not open either. Full read list in `attestation.yaml`.
- **Machine-readable backing:** `recomputations.json`. Scripts: `work/redteam_recompute.py`,
  `work/redteam_recompute2.py`, `work/redteam_combined.py`, `work/redteam_extend.py`,
  `work/redteam_pf_store.py`, `work/redteam_j6_control.py`. None imports producer code;
  the producer's run artifacts and one committed prime-field cost record are read as
  **data**.

## Verdict summary

| Joint | Subject | Verdict |
| --- | --- | --- |
| J2 | Is the baseline charged symmetrically | **breaks** |
| J3 | The metric set and the n = 409 flip | **breaks** |
| J5 | The declined stopping rule on the fitted `c` | **holds** |
| J6 | The substituted nearby-object control | **breaks** |

Nothing below touches the arithmetic. My reimplementation reproduces every figure
in COST-SEMBIN-8d123b to a worst disagreement of **4.8e-5 bits** and reproduces all
four published crossovers (303 / 303 / 435 / 375) exactly, from formulas restated
independently and importing none of the producer's code
(`recomputations.json → step0_validation`). The arithmetic is not in dispute and I
did not attack it. What breaks is the comparison and the interpretation.

**The one result to read if you read nothing else.** The contract's prime-field
nearby-object control — the one the run declined as impossible to build — is buildable
from a committed record in this repository, and I built and ran it. Charged against the
baseline the way COST-SEMBIN-8d123b charges it, prime-field index calculus **beats
Pollard rho at 64, 128 and 256 bits** under the record's own product metric. This corpus
records that ordering as false (KN-OPEN-001, KN-TECH-003). The inversion appears at
`store_log2 ≥ 21.5` and the record charges 30; under a baseline charged coherently on its
own time-memory curve it does not appear at any size. J2 and J6 are one defect, reached
from two directions: **a 29-bit memory overcharge on the baseline, sitting under every
crossover in the record.**

---

## Step 0 — the reimplementation, so that every objection below is a difference and not a bug

| n | record time | mine | record sparse mem | mine | record margin (sparse product) | mine |
| --- | --- | --- | --- | --- | --- | --- |
| 163 | 123.7697 | 123.7697 | 55.2782 | 55.2782 | −58.7888 | −58.7888 |
| 283 | 147.6495 | 147.6495 | 61.9374 | 61.9374 | −28.5319 | −28.5319 |
| 409 | 166.5438 | 166.5438 | 66.5250 | 66.5250 | +11.5175 | +11.5175 |
| 571 | 186.3070 | 186.3070 | 70.2718 | 70.2718 | +69.4889 | +69.4889 |

Crossovers recomputed: time-only 303 (both readings), product 435 dense / 375 sparse,
max 303 (both). Identical to the record.

---

## J2 — IS THE BASELINE CHARGED SYMMETRICALLY — **breaks**

### J2(a) The unswept store, and the contract's own framing-failure condition

`store_log2 = 30` is fixed in `vow_log2`'s default and never varied in any crossover.
Recomputing the product-metric crossover across it:

| `store_log2` | crossover, dense | crossover, sparse | margin at n = 409, sparse | verdict at 409 |
| --- | --- | --- | --- | --- |
| 0 | 522 | 462 | −18.48 | vOW |
| 10 | 495 | 434 | −8.48 | vOW |
| **20** | 464 | 405 | +1.52 | Semaev |
| **30 (record)** | 435 | 375 | +11.52 | Semaev |
| **40** | 406 | 344 | +21.52 | Semaev |
| 48 | 379 | 319 | +29.52 | Semaev |
| **60** | 342 | 279 | +41.52 | Semaev |

Over `store_log2 ∈ {0, 20, 40, 60}` the crossover moves **180 in n** (dense) and
**183 in n** (sparse). Metric choice moves it 132 (dense) and 72 (sparse). Even
restricted to the store values the **contract itself declares**
(`vow_parameters.distinguished_point_store_log2: [30, 40, 48, 60]`), the sparse
crossover ranges over 96 in n against the metric's 72.

EXP-SEMBIN-f4a17b's own `falsification_criterion` says:

> "If the crossover depends more strongly on the vOW store parameter than on the
> metric choice, the deliverable is a two-parameter surface and the hypothesis's
> framing is wrong even where its direction is right."

That condition is met, on the record's own preregistered parameter list, for the
sparse reading — the reading that produces the headline n = 409 result. The
contract declared the store as an independent variable and as a primary metric
(`time_memory_curve_per_algorithm`); the run tabulated vOW's time and memory across
it in `cost_table()` but never pushed it through `compare_at` or `crossover_curve`,
which take the default 30 in every call. This is an unmet preregistered deliverable,
not merely an omission.

The n = 409 sparse verdict flips to vOW at `store_log2 ≲ 18.5`, and the dense verdict
flips to Semaev at `store_log2 ≳ 38.8`. A crossover quoted without its store is
underdetermined in exactly the way the record says a crossover quoted without its
metric would be.

### J2(b) The missing tradeoff — and it does not run the way the Coordinator expects

Model vOW on its actual curve: total work `W = 0.886·2^{n/2}`, `M` processors,
`w` stored distinguished points, DP probability `θ = w/W` so that exactly `w` points
are stored. Then

    T   = W · (1/M + 1/w)            wall time, including the DP tail 1/θ
    Mem = 3n · max(w, M) bits        the store, or the per-processor state

**Result 1 — the time penalty is zero where the record charges it.** At the record's
own operating point `M = 1`, the DP-tail penalty is `log2(1 + 1/w)`, which is
`0.0000 bits` for every `w ∈ {2^20, 2^30, 2^40, 2^60}` at n = 409 and n = 571
(`recomputations.json → J2_baseline_symmetry.dp_time_penalty`). It first becomes
visible at `M = 2^20, w = 2^20`, where it is 1.0 bit.

**The Coordinator's prior on this joint is refuted.** The prior says charging the
granularity/steps tradeoff would move the crossover DOWN, making the record too kind
to the baseline. Charged as a time penalty at the operating point the record uses, it
moves the crossover by nothing at all. The tradeoff bites through **memory**, and it
bites the other way.

**Result 2 — the product is invariant along vOW's curve, and the record charges a
dominated point.**

    T · Mem = 3n · W · (max(w,M)/M + max(w,M)/w)  ≥  2 · 3n · W

with the minimum attained anywhere with `w ≈ M`. A numeric grid over
`(log2 w, log2 M) ∈ [0,80]²` confirms it: at every n the minimum product equals
`W · 3n · 2` and the record's charge exceeds it by **exactly 29.0 bits**
(n = 283, 310, 409, 571 alike). The record charges vOW the **memory of a
2^30-point store** and the **time of one processor**. Those are different points on
the curve, and the combination `M = 1, w = 2^30` is dominated: a single walk needs
`O(1)` points with Brent/Floyd cycle detection, which is what this program's own
KN-TECH-001 records ("`O(1)` storage") and what KN-TECH-035 says keeps parallel
collision search competitive under full cost ("per-processor storage stays small").

Charging vOW coherently (any single point on its own curve):

| | record | coherent vOW | shift |
| --- | --- | --- | --- |
| crossover, dense | 435 | **520** | +85 |
| crossover, sparse | 375 | **460** | +85 |
| margin at n = 409, dense | −8.79 | **−37.79** | −29.0 |
| margin at n = 409, sparse | **+11.52** | **−17.48** | −29.0 |

**At n = 409 the chained algorithm loses under *both* storage readings once the
baseline is charged at a point it could actually occupy.** The 46.6-bit swing is
still 20.3 bits wide, but it no longer straddles zero.

Semaev's side is not disadvantaged by this treatment. Parallelising his stage 1
across `M` workers gives time `T0/M` and memory `max(relation store, M · working set)`;
since the working set dominates at every FIPS n under both readings, his product is
also M-invariant at `T0 · WS`. Charging **each algorithm the minimum of its own
time-memory curve** — the Pareto-honest comparison of two tunable algorithms — gives:

| n | vOW min product | Semaev min, sparse | margin | Semaev min, dense | margin |
| --- | --- | --- | --- | --- | --- |
| 283 | 152.06 | 209.59 | −57.53 | 226.88 | −74.83 |
| 310 | 165.69 | 215.08 | −49.40 | 232.87 | −67.18 |
| **409** | **215.59** | **232.92** | **−17.33** | **252.28** | **−36.69** |
| 571 | 297.07 | 256.58 | +40.49 | 277.71 | +19.35 |

Crossover **460** (sparse) / **518** (dense). This is the `dominated_by` check the
record owes and does not have.

**Calibration against a real attack.** The one public operating point in this
program's corpus is sect113r2 (KN-TECH-036): 82.2M ≈ 2^26.3 distinguished points
stored on up to 120 FPGAs, i.e. `w/M ≈ 2^13.3`. Charging vOW at that ratio rather
than at the record's effective 2^30 gives crossovers **486 / 424** and a **−5.18**
margin at n = 409 under sparse — still a loss.

### J2(c) The 0.886 constant — closed, it cannot matter

KN-TECH-018 records that the program's "0.886·sqrt(n)" convention **already includes
the sqrt(2) negation factor**; 0.886 = sqrt(π/2)/sqrt(2). The corpus separately
carries sqrt(πn/2) = 1.2533·sqrt(n) in KN-TECH-001, i.e. two constants differing by
0.5 bits, and the record uses the one favourable to the baseline. Recomputing:

| walk constant | shift vs record | crossover, sparse | margin at 409 |
| --- | --- | --- | --- |
| 0.886 (record) | 0 | 375 | +11.52 |
| 1.0 | +0.175 bits | 374 | +11.69 |
| 1.2533 = sqrt(π/2) | +0.500 bits | 373 | +12.02 |

**Two in n across the whole plausible range. Closed — a wrong walk constant cannot
matter here, and I say so plainly rather than leaving it open.** The relayed
provenance of the constant (KN-LIT-012 records its own full text was not re-read) is
therefore not load-bearing for any conclusion in the record.

### J2(d) The FIPS cofactor — the record's stated direction is inverted

The record (`vow_log2` docstring and `optimistic_assumptions_baseline`) says taking
`q = 2^n` and neglecting the cofactor "makes rho look marginally CHEAPER than it is,
so it flatters the baseline and not Semaev." **The review plan repeats this** ("q is
taken as 2^n, neglecting the FIPS cofactor of 2 or 4, which flatters the baseline").

Both are backwards. Pollard rho runs in the prime-order subgroup of order `≈ 2^n/h`,
so its true cost is `0.886·2^{n/2}/sqrt(h)` — **smaller** than what the record charges.
Taking `q = 2^n` **overcharges** the baseline and therefore flatters Semaev:

| cofactor h | vOW time at 409 | bits cheaper | crossover, sparse | crossover, time-only |
| --- | --- | --- | --- | --- |
| 1 (record) | 204.3254 | — | 375 | 303 |
| 2 | 203.8254 | 0.5 | 376 | 304 |
| 4 | 203.3254 | 1.0 | 378 | 305 |

**Magnitude 1–3 in n.** Small, but it is a sign error inside a disclosure the record
uses to argue its own conservatism, and it is repeated in the review plan, so it
would have propagated.

**Automorphisms.** KN-TECH-018 gives the rho discount as `sqrt(|Aut|)`, with
`~sqrt(2m)` for an order-`m` Frobenius, and notes the sqrt(2) negation factor is
already in 0.886. For **K-409** (Koblitz), `|Aut| ≈ 2n = 818`, so the discount beyond
negation is `log2(sqrt(818)/sqrt(2)) = 4.34 bits`. The record's parameter sets label
"K-409 **and** B-409" as one row and charge them identically; they differ by 4.34
bits of baseline, which is 11 in n. This is disclosed nowhere.

### J2 — the two-directional tally, which is the part a one-sided red team would miss

I looked as hard for asymmetries favouring Semaev as against him. Three of the four
I found run the other way from the Coordinator's prior, and three run with it:

**Record over-credits Semaev (baseline undercharged):**

| effect | shift in n |
| --- | --- |
| baseline charged at a dominated operating point | **+85** |
| FIPS cofactor neglected | +1 to +3 |
| Koblitz Frobenius discount neglected (K-409 only) | +11 |

**Record under-credits Semaev (baseline overcharged) — the Coordinator's expected
direction, and it is real:**

| effect | shift in n |
| --- | --- |
| `k = ceil(n/m)`, the reading Section 3 and 4.5.2 actually define | **−24** under the product metric (435→411, 375→351). The record computes this only under time-only (303→281) and never under the metric its headline lives in. |
| unit conversion: one group operation is 10–100 field operations | −11 to −21 (product, sparse: 375 → 364 → 354) |
| `m` not re-optimised under the memory-charged metric | −0 to −2 (dense 435→433; sparse unchanged) |

Applying **everything at once** rather than adding separately-quoted shifts:

| scenario | crossover dense | crossover sparse | margin at 409, dense | sparse | readings agree at 409? |
| --- | --- | --- | --- | --- | --- |
| record as published | 435 | 375 | −8.79 | **+11.52** | **no** |
| coherent vOW only | 520 | 460 | −37.79 | −17.48 | yes (vOW) |
| sect113r2-calibrated store only | 486 | 424 | −25.49 | −5.18 | yes (vOW) |
| **all corrections, B-409** | **481** | **421** | −24.80 | −3.76 | yes (vOW) |
| all corrections, B-409, no unit conversion | 493 | 441 | −29.80 | −8.76 | yes (vOW) |
| all corrections, K-409 | 493 | 441 | −29.64 | −8.60 | yes (vOW) |
| **every pro-Semaev correction, record's baseline kept** | 397 | 337 | **+4.70** | +25.74 | yes (Semaev) |

**Of the eight configurations examined, only two straddle zero at n = 409, and one of
them is the record's own.** Push the corrections in the direction that favours Semaev
and the two readings agree that he wins; charge the baseline coherently and they agree
that he loses. The straddle is not a property of the two storage readings; it is a
property of one particular charging of the baseline.

### J2(e) The matched-null attribution is overturned

CLAIM A asserts: *"The whole shift is attributable to Semaev's relation store rather
than to charging the baseline's distinguished-point store (matched-null share = 0)."*

The run's control returns `share = 0` under `time_only` and `equal_rate_max` — the two
metrics under which memory is inert — and returns **`null`** under `time_memory_product`
and `area_time_AT`, the two metrics the claim is about. It returns `null` because a
zero-memory comparator makes `log2(memory) = −inf`, so the baseline's product cost is
`−10^9` and the crossover does not exist. **Under the metric the claim quotes it for,
the control did not run; it degenerated.** The record's prose converts "the control
reported 0 where memory is inert and undefined where it is not" into "the share is
zero."

The informative null is a baseline with the memory it actually needs (`3n` bits), not
with none. Decomposing the shift that way:

| step | dense | sparse |
| --- | --- | --- |
| time-only crossover | 303 | 303 |
| charge Semaev's memory, baseline at 3n bits | 522 | 462 |
| **also** charge the baseline a 2^30-point store | 435 | 375 |
| shift from Semaev's memory | **+219** | **+159** |
| shift from the baseline's store | **−87** | **−87** |
| net shift the record reports | +132 | +72 |

The baseline's charge is 55% of the magnitude of Semaev's and it works in Semaev's
favour. "Share = 0" is false; the correct statement is that the reported +72 is a
near-cancellation of +159 and −87. The Coordinator recorded that it did **not** expect
a reviewer to overturn the matched-null attribution. It is overturned.

### J2(f) The proves-too-much control: the record's baseline charge inverts a known-false ordering

Everything above argues that the 2^30-point store is the wrong charge. This subsection
does not argue it — it runs the argument against an object whose answer is already
recorded in this corpus, which is the control the review architecture requires.

`experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml` is a committed 54-cell
prime-field index-calculus concrete-cost table over `log2 N ∈ {64, 128, 256}`, charging
time **and** memory, and — this is what makes it usable — charging its Pollard-rho prior
in exactly this record's `0.886·2^{n/2}` convention. I verified that agreement cell by
cell before importing anything (`recomputations.json → J6 …
baseline_convention_agrees_with_sembin: true`, at all three sizes to 1e-3). The known
answer is in the corpus twice: KN-OPEN-001 ("Does index calculus beat Pollard rho for
prime-field ECDLP? — No") and KN-TECH-003 ("uncompetitive with rho").

Charging those cells against the baseline as the record charges it, and sweeping only
the store:

| `store_log2` | `log2 N = 64` | `log2 N = 128` | `log2 N = 256` | ordering inverted? |
| --- | --- | --- | --- | --- |
| 0 | −21.51 | −23.16 | −25.23 | no |
| 10 | −11.51 | −13.16 | −15.23 | no |
| 20 | −1.51 | −3.16 | −5.23 | no |
| **30 (record)** | **+8.49** | **+6.84** | **+4.77** | **yes, at all three sizes** |
| 40 | +18.49 | +16.84 | +14.77 | yes |
| 60 | +38.49 | +36.84 | +34.77 | yes |

(entries are the best product-metric margin in bits **for index calculus**; positive
means index calculus wins.) The ordering inverts at `store_log2 ≥ 21.51` (64 bits),
`23.16` (128), `25.23` (256). **The record charges 30.**

At `log2 N = 64` the winning cell loses on time by 9.12 bits and wins under the record's
product metric by 8.49, entirely because the record charges rho 37.59 bits of memory
against index calculus's 19.97. Nobody believes prime-field index calculus beats Pollard
rho at 64 bits. Under the coherent baseline of J2(b) it does not: the margin is −20.51
bits at 64, −22.16 at 128, −24.23 at 256, and **zero cells invert at any size**.

This is the strongest single artifact in this report and it is not an opinion about
realism. The record's memory convention, applied to an object whose ordering this
program has already recorded, produces the wrong ordering — at three sizes, including one
where the answer is not in dispute — and the coherent convention produces the right one.
The 29-bit differential between the two conventions is exactly the overcharge computed
in J2(b), arrived at from a completely different direction.

One honesty note that does not weaken it. Every PFDR cell is conditional on HEUR-001 of
H-PFDR-06fd60, which that record itself prices at a 0.05 prior, so these cells are not a
claim that prime-field index calculus is fast. They do not need to be: the inversion is a
property of the *difference* between the two baseline conventions, and that difference is
29 bits whatever the index-calculus side is worth.

### J2 breaking artifact

Delivered, three times over. The plan asks for "a crossover figure that moves by more than
10 in n under a defensible change to the baseline's charging" — it moves by **85**
(coherent operating point) and by **180** (across the store parameter the contract
declared and the run never swept) — "OR a demonstration that the comparison is
asymmetric in a direction the record does not disclose": the record discloses the
asymmetry with the **wrong sign** on both the tradeoff (it says the missing tradeoff
favours the baseline; it favours Semaev by 29 bits) and the cofactor. J2(f) adds the
control that decides it: the record's baseline convention **inverts a known ordering on a
known-false object**, at the store size the record charges and at no smaller one.

### What J2 does NOT break

The record's transparency is not in question. Every input I used to break it is stated
somewhere in the record: the store value, the absent tradeoff, the M = 1 charging, the
neglected cofactor. The failure is in the **sign and magnitude** the record attaches to
its own disclosures, not in concealment. And the direction of CLAIM A's headline —
that charging memory moves the crossover up and that the paper states no memory model —
survives: it moves up by more than the record says, not less.

---

## J3 — THE METRIC SET AND THE n = 409 FLIP — **breaks**

### J3(a) Four metrics are two

`area_time_AT` and `time_memory_product` are the *same expression* in
`memory_charged_cost.py` (`log2_time + mem` in both branches, with
`memory_weight = 1`). The code comment claims AT is "distinguished from the plain
product by charging memory at the ceiled-k relation store even when the working set
is the smaller term"; **the implementation does no such thing.** The record's
`disclosure` field is honest about the coincidence; the code comment is not, and a
later reader who reads the code will be misled in the opposite direction.

`equal_rate_max_of_time_and_memory` returns `max(time, memory)`, and at every one of
the 10 (n, storage) cells **neither algorithm's memory exceeds its own time**, so max
reduces to time-only identically. The record notes this for Semaev's side in
`affected_scope` but does not say that the metric is therefore not a fourth
observation.

So: **four declared metrics, two distinct functions, two distinct verdicts.** The
"four metrics" framing overstates the corroboration by a factor of two, and the
correction is not "should be three" — it is "should be two, reported as one
memory-charged metric and one memory-free one."

I clear the other half of the accusation. The four metrics are the contract's own
preregistered list (`cost_metrics` in `specification.yaml`, approved in
DEC-20260913-ebd639 before the run). **There is no evidence of metric-shopping**, and
a red team should say so: the degeneracy is a design defect in the contract, not a
result selected after the fact.

### J3(b) Two metrics the Coordinator did not choose

**Metric 1 — memory-weighted time, `T · M^α`.** This interpolates the record's own
two endpoints and shows how knife-edge the headline is:

| α | crossover dense | crossover sparse | margin at 409, dense | sparse |
| --- | --- | --- | --- | --- |
| 0 | 303 | 303 | +37.78 | +37.78 |
| 0.25 | 334 | 320 | +26.14 | +31.22 |
| 0.5 | 366 | 338 | +14.49 | +24.65 |
| 0.75 | 401 | 356 | +2.85 | +18.08 |
| 1.0 | 435 | 375 | −8.79 | +11.52 |

The dense reading flips at n = 409 only for **α ≥ 0.811**; the sparse reading does not
flip anywhere in `α ∈ [0, 1]`. The "swing straddling zero" exists only in the last
19% of this family's range.

**Metric 2 — the fixed memory budget, which the Coordinator names as the one that is
missing and most realistic.** The attack is charged the time it needs when memory is
capped at `B` bits. The baseline is charged **honestly**: for any `B ≥ 3n` bits vOW's
total work is `0.886·2^{n/2}` unchanged, because a larger store buys wall-clock
(parallelism) but not total work, and at `M = 1` cycle detection needs `O(1)` points.
Semaev may re-choose `m` to fit the budget. Two readings:

*Hard (an algorithm that does not fit does not run).* Semaev's **cheapest** memory over
all `m ∈ [2,30]` at n = 409 is `2^65.33` bits sparse (at m = 8) and `2^80.07` dense
(at m = 6); at n = 571 it is `2^69.9` / `2^86.7`. So:

| budget B | verdict at n = 409, dense | verdict at n = 409, sparse |
| --- | --- | --- |
| 2^30 (128 MB) | vOW (infeasible) | vOW (infeasible) |
| 2^40 (128 GB) | vOW (infeasible) | vOW (infeasible) |
| 2^50 (128 TB) | vOW (infeasible) | vOW (infeasible) |
| 2^60 (131 PB) | vOW (infeasible) | vOW (infeasible) |
| 2^64 | vOW (infeasible) | vOW (infeasible) |
| 2^70 (134 EB) | vOW (infeasible) | Semaev |
| 2^90 | Semaev | Semaev |

**Under any memory budget below 2^65 bits — four exabytes, above every storage system
that exists — the two storage readings AGREE that n = 409 is a loss.** They disagree
only in the band `2^65 … 2^89` bits.

*Soft (external memory: `memory/B` passes).* n = 409 turns to Semaev at
`B ≥ 2^28.6` bits sparse and `B ≥ 2^48.0` bits dense; the readings agree below 2^28.6
(both vOW) and above 2^48 (both Semaev), and disagree in between. At a realistic
single-machine budget of 2^40 bits the readings disagree, so **the flip survives the
soft reading.**

*Robustness of the sparse figure off the argmin.* The fixed-budget metric lets Semaev
re-choose `m`, but the record's `raw-result.json` exposes its sparse memory only at the
time-argmin — five `(n, m)` pairs. So the budget verdicts rest on a restatement of the
sparse reading evaluated at `m` values the record never printed. I bounded that
extrapolation by rebuilding the sparse figure a second way, anchored on the **exact**
Macaulay width of `N = (m−2)n + km` rather than the `(nm)^4/24` surrogate: over all
`m ∈ [2, 30]` at every FIPS `n` the two disagree by at most **1.33 bits**, and every
hard- and soft-budget verdict in the two tables above is identical under both
(`recomputations.json → J3 … sparse_restatement_robustness`). The budget conclusions do
not depend on which sparse restatement is used.

### J3(c) Does "the verdict at n = 409 is decided by the memory model" survive?

**Yes in letter, no in substance, and not at all as the record frames it.**

- It survives under my soft-budget metric at B ≈ 2^40 bits, and under the record's
  own product metric. Two of the four metrics I constructed preserve it.
- It does **not** survive the hard-budget metric at any realistic B, nor the
  Pareto min-of-own-curves product from J2, nor `T·M^α` for any α < 0.811. Under all
  three, n = 409 is a loss under **both** readings.
- Where it does survive, what decides it is the **memory budget**, not the
  dense-versus-sparse storage reading the record puts at the centre of CLAIM A. At any
  fixed budget the two readings agree with each other except inside one band; the band
  is what the record has mistaken for a property of the algorithm.

The honest restatement CLAIM A can support is: *at n = 409 the verdict is undetermined
by cost models that charge memory multiplicatively and leave the memory scale free, and
is determined — against Semaev — by any model that fixes a physical memory budget or
charges the baseline at a point on its own tradeoff curve.* That is a weaker and more
useful claim than "decided by the storage reading."

### J3 breaking artifact

Delivered: two defensible metrics under which the n = 409 swing does not straddle zero
(hard budget at any `B < 2^65`; Pareto min-of-own-curves), plus the fixed-budget
computation the plan says the record owes.

---

## J5 — THE DECLINED STOPPING RULE — **holds**

This is the joint the Coordinator most wanted attacked. I attacked it with a fitting
procedure that shares no code with the producer's, and it survives.

### J5(a) Is `c` converging or sitting?

I fit `c = log2(stage 1 at the argmin) / sqrt(n · ln n)` where stage 1 is
`n/m + log2(m!) + 12·log2 n`, with the argmin found by **golden-section search over
real `m`** and then checked on both integer neighbours — deliberately not the coarse
grid plus refinement window that `joint_balance.py` uses, since that was the suspect
component. I extended the ladder from the record's 10^13 out to **10^300**, the limit
of float64.

| log10 n | ln m / ln n | c (real m) | c (integer m) | record's c | gap to 1.698644 |
| --- | --- | --- | --- | --- | --- |
| 3 | 0.3992 | 2.72308 | 2.72328 | 2.72328 | −1.0246 |
| 5 | 0.4160 | 1.57796 | 1.57797 | 1.57797 | +0.1207 |
| 7 | 0.4287 | **1.48148** | 1.48148 | 1.48148 | +0.2172 |
| 9 | 0.4379 | 1.50470 | 1.50470 | 1.50470 | +0.1939 |
| 13 | 0.4504 | 1.55248 | 1.55248 | 1.55248 | +0.1462 |
| 30 | 0.4721 | 1.62531 | — | *(beyond the record's ladder)* | +0.0733 |
| 80 | 0.4868 | 1.66673 | — | | +0.0319 |
| 180 | 0.4931 | 1.68282 | — | | +0.0158 |
| 300 | 0.4955 | **1.68853** | — | | **+0.0101** |

My fit agrees with the record's to five decimals at every rung it reports
(1.48148 / 1.50470 / 1.55248 and the rest). **The producer's fitting code is not
defective.** The minimum near 10^7 and the monotone rise thereafter reproduce exactly.

The record's evidence for convergence was a 7-point monotonicity test over
10^7…10^13 — a window in which `c` moves by 0.071 and is still 0.146 short. That is
weak evidence for an asymptote, and it is exactly the shape of argument the
Coordinator flagged. So I ran the discriminating test the record did not:

**The gap-scaling test.** If the deficit is the `o(1)` cofactor it must decay like
`log log n / log n`; if it is an implementation defect it is a fixed offset. Over
10^7…10^300 (43 decades) the raw gap falls from 0.2172 to 0.0101, while
`gap · log n / log log n` stays in **[1.068, 1.326]**. Relative scatter: **7.7%** for
the `log log n / log n` model against **62%** for the constant-offset model — an 8-fold
better fit. The deficit decays at precisely the predicted rate.

**The analytic continuation.** Beyond float64, the balance `m² log2 m = n` can be
solved in log space and `c = 2·sqrt(ln m / (ln2 · ln n))`:

| log10 n | ln m / ln n | c | gap |
| --- | --- | --- | --- |
| 10^3 | 0.49839 | 1.69591 | 2.7e−3 |
| 10^4 | 0.49979 | 1.69829 | 3.6e−4 |
| 10^6 | 0.49999689 | 1.698638 | 5.3e−6 |
| 10^9 | 0.5 | 1.6986436 | 1.0e−8 |

**The guilty null — a convergence test that cannot fail is not a control.** The gap-scaling
test above shows the deficit decays; it does not by itself show the test could have said
otherwise. So I fitted a two-parameter tail model `gap ≈ A + B·(log log n / log n)` over
the eight rungs from 10^20 to 10^300 and read off `A`, the limit offset — zero means
convergence to 1.6986, non-zero means a wrong constant — then re-ran the *identical* fit
against perturbed cost models whose true asymptote is known to have moved:

| cost model | true asymptote | fitted limit offset `A` | rms residual |
| --- | --- | --- | --- |
| **the record's, unperturbed** | 1.698644 | **−0.00265** | 0.00088 |
| `ω = 4` instead of 3 (benign: polylog only) | 1.698644 | −0.00265 | 0.00088 |
| `α = 1.05` on the `n/m` term | 1.740592 | **−0.04459** (expected −0.04195) | 0.00087 |
| `α = 0.90` on the `n/m` term | 1.611475 | **+0.08449** (expected +0.08717) | 0.00089 |
| `(m!)²` instead of `m!` | — | **−0.70893** | 0.00178 |

The true model's limit offset is within 0.003 of zero; every null whose asymptote actually
moved reports an offset **16 to 267 times larger**, and within 7% of the value predicted
from the shifted asymptote. A benign perturbation that changes only the polylog cofactor
correctly reports the same near-zero offset. **The test has power**, and the record's
conclusion survives a test that could have failed it.

The `c_fitted`-versus-`c_balance_identity` discrepancy the record leaves unexplained is
also closed rather than waved at. Stirling gives `log2 m! = m log2 m − m/ln 2 + O(log m)`,
which predicts `c_fit = c_balance·(1 − 1/(2 ln m))` exactly; the prediction holds to
0.0225 at 10^7, 0.0025 at 10^9, 3e−5 at 10^13 and to floating-point zero from 10^20 on.
It is a named finite-`m` term with a known decay rate, not a defect — but the record
should say so rather than print two numbers that look like a cross-check.

**VERDICT: `c` is CONVERGING, not sitting below.** The mechanism is exactly the one the
record names: `ln m / ln n = 1/2 − log2(log2 m)/(2 log2 n)`, so the approach is
`Θ(log log n / log n)` — genuinely convergent and genuinely glacial. Declining the
stopping rule was **correct**, and the two claims do not fall on this axis.

Two things I will say against the record even though it holds. First, its evidence was
inadequate to its conclusion: a 7-point monotone rise over 6 decades does not
distinguish an asymptote at 1.6986 from one at 1.60, and the gap-scaling test and the
analytic continuation — both cheap, both absent — are what actually settle it. Shipping
a correct conclusion on evidence that does not reach it is the pattern the Coordinator
was right to be uncomfortable about, even where the conclusion survives. Second, the
`c_fit_ladder` carries `c_from_balance_identity` alongside `c_fitted` and the two
disagree by 0.06–0.20 at every rung (1.61224 against 1.55248 at 10^13) without the
record remarking on it; they differ because the fitted value includes the `12 log2 n`
cofactor and the `−m log2 e` Stirling term. Harmless, unexplained, and it invites a
later reader to treat two numbers as a cross-check when they are not.

### J5(b) Does eq. (17)'s `m*` law understate the argmin by 4–15%?

**Direction confirmed, range misquoted.** The law `m* ~ sqrt(2 ln2 · n / ln n)`
substitutes `ln m = (ln n)/2`, which overstates `ln m`, so it necessarily returns a
smaller `m` than the exact stationarity condition `m² log2 m = n`. My independent
values:

| log10 n | true argmin | law | law understates by |
| --- | --- | --- | --- |
| 3 | 15.76 | 14.17 | 10.14% |
| 5 | 120.25 | 109.73 | 8.75% |
| 7 | 1001.6 | 927.4 | 7.40% |
| 9 | 8739.3 | 8179.0 | 6.41% |
| 11 | 78425 | 73982 | 5.67% |
| 13 | 717005 | 680531 | **5.09%** |

Range **5.09%–10.14%** (5.09%–11.46% measured against the integer argmin). The
record's own `c_fit_ladder` carries `law_relative_error` running from −0.1146 to
−0.0509 — i.e. 5.09% to 11.46%. **Neither 4% nor 15% appears in the record's own data.**
The quoted "4–15%" is wider than the computation at both ends and is the number a later
reader will lift. It should read 5–11%. This is a scoped correction, not a break: the
direction, the mechanism, and the role the gap plays in explaining the `c` deficit are
all confirmed.

### J5(c) Is the implementation defective?

**No.** Unambiguously: the fitted `c` converges to 1.6986, my independent fit
reproduces the producer's to five decimals, the deficit decays at the rate the `o(1)`
cofactor predicts, and the `m*` direction is right. Neither CLAIM A nor CLAIM B falls
on this joint.

### J5 breaking artifact

The plan's second alternative is delivered: **confirmation of monotone convergence with
the ladder**, extended 287 decades past the record's, cross-checked against an analytic
continuation, and — the part the record does not have — shown to be a test with
demonstrated power against nulls whose asymptote moved. The deviation is discharged.

---

## J6 — THE SUBSTITUTED CONTROL — **breaks**

### J6(a) Can a same-family object serve this control's function? No.

The contract states the control's purpose explicitly:

> "If the machinery reports index calculus winning there, it is mischarging memory or
> parallelism and every SEMBIN row is void. **This is the control that catches a cost
> model tuned to produce the answer wanted.**"

That is a **family-wide-bias** detector. eq. (4) is Semaev's own single summation
polynomial over the same field `F_{2^n}`, Weil-descended by the same construction,
costed by the same degree-bounded Macaulay monomial count, under the same storage
readings. Every error class the detector exists to catch — a wrong Macaulay-width
model, a wrong Weil-descent variable count, a wrong storage reading, a max-versus-sum
convention error, a mischarged parallelism — is applied **identically to both sides and
cancels in the comparison**. The prime-field arm was specified precisely because it is a
different family: no subfield to descend to, no Boolean Weil restriction, an
unstructured factor base, and a known reference answer in KN-OPEN-001.

**Verdict on (a): inadequate**, not merely "inadequate-but-admissible-with-disclosure".
The substitution is disclosed candidly and the prose is recorded as owed, which is to the
record's credit, but disclosure does not restore the function. CLAIM A has five controls,
not six.

### J6(b) Does a prime-field cost model exist in this repository? Yes.

The run asserts: *"A prime-field index-calculus cost model is in neither the frozen
source nor this repository's corpus. Building one would have meant inventing formulas."*
I searched `knowledge/techniques/`, `knowledge/literature/`, `knowledge/open-problems/`,
`knowledge/findings/`, `ledger/` and `experiments/`. (The `search_knowledge` MCP server
is **not available in this session** — `GetDynamicTools` returns no matching namespace —
so this is a filesystem search of the corpus and ledger, and per AGENTS.md absence of a
result is not evidence of absence. What I found is present regardless.)

The assertion is **false as written**, and the strongest counterexample is not a
specification but an executed record:

- **`experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml`** (committed) — a
  **54-cell prime-field index-calculus concrete-cost table** over
  `log2 N ∈ {64, 128, 256}`, sweeping `m ∈ {3,4,5}`, `D_0 ∈ {4,6,8}` and
  `ω ∈ {2.0, 2.807}`, charging **time and memory**, and carrying its own Pollard-rho
  prior in **exactly this record's `0.886·2^{n/2}` convention** — verified cell by cell
  before use. This is not a formula that had to be invented; it is a table that had to
  be read. I ran the control with it, below.
- **`experiments/EXP-ICEX-c32447/specification.yaml`** — a fully specified prime-field
  index-calculus cost model: a shared cost of `m!·N` charged group operations, three
  separated counters (`C_rel`, `C_LA`, `C_descent`), and **a genuine multi-target rho arm
  with a shared distinguished-point table whose memory is counted in stored group
  elements** — i.e. the exact comparison shape COST-SEMBIN-8d123b needed. Status `draft`,
  no runs.
- **`experiments/EXP-ICEX-349205/specification.yaml`** — a two-term index-calculus
  charge against Pollard rho with a symbolically verified optimizer at every arity 2–8
  and a threshold table with pinned constants. Status `review_required`,
  `execution_authorized: false`, no runs.
- **`ledger/decisions/DEC-20260804-14b457`** (committed) — asserts a characterization of
  prime-field ECDLP index-calculus complexity as `exp(c·sqrt(log N · log log N))`,
  "tight — both achievable and (empirically) bounded above", alongside the Bezout no-go
  and H-PSEUDO.
- **`KN-OPEN-001`** — the reference answer the contract itself names, present and
  explicit: "no known construction yields an advantage over prime fields."

The correct disclosure is not "it does not exist so building one means fabrication." It
is: *"a committed prime-field index-calculus concrete-cost table exists at
EXP-PFDR-c04716/runs/STATIC-001, conditional on HEUR-001, and further models exist as
unexecuted contracts (EXP-ICEX-c32447, EXP-ICEX-349205); instantiating the control was
out of this experiment's scope."* That is a materially different statement, it does not
rest on a false premise, and it leaves the control owed for a reason a later reader can
act on. **The record should be corrected on this point.**

### J6(b′) I ran the declined control, and the contract's stopping rule fires

The contract's clause D3 says: *if the machinery reports index calculus winning there, it
is mischarging memory or parallelism and every SEMBIN row is void.* Charging the 54 PFDR
cells against the baseline as this record charges it:

| `log2 N` | cells | IC beats rho on **time only** | largest IC advantage | IC beats rho under the **product** | largest |
| --- | --- | --- | --- | --- | --- |
| 64 | 18 | 0 | −9.12 | **1** | **+8.49** |
| 128 | 18 | 0 | −0.22 | **1** | **+6.84** |
| 256 | 18 | **4** | **+19.06** | **1** | **+4.77** |

**D3 fires**, under time-only at 256 bits and under the product at every size. Taken
literally, the contract says every SEMBIN row is void. I do not draw that conclusion, and
the reason I do not is the finding:

**D3's stated diagnosis is wrong for the way the control actually fires, and the two
firings have different causes.** The time-only firing at 256 bits involves no memory and
no parallelism — it is driven entirely by HEUR-001, an external conditional heuristic the
corpus itself prices at a 0.05 prior, and it says nothing whatever about SEMBIN's
machinery. Under the program's own unit discipline (EXP-ICEX-c32447's `kappa ∈ {1,10,100}`)
it fires harder, 6 cells of 18 rather than 4, because converting the index-calculus side
from field to group operations moves it the favourable way. The product firing has the
opposite character: it is **entirely** the store size (J2(f)), it vanishes under the
coherent baseline at every size, and it is a real defect in this record's convention.

So the control is worth more than the contract knew, and the stopping rule is worth less.
As written D3 conflates a conditional external model with a defect in the machinery under
test, and it has no conditionality filter, no unit tag, and no localisation step — so any
faithful instantiation trips it and voids a claim for a reason that is not a fault. **The
control was owed a design, not merely an instantiation**, and the run's substitution
concealed that: eq. (4) passes by thousands of bits and so never exposed that D3 cannot
tell a mischarged baseline from a speculative heuristic.

One thing the located models would have forced. `EXP-ICEX-c32447` declares a binding
unit discipline — solver work counted in field operations is converted to group
operations at `kappa ∈ {1, 10, 100}`, and **"a conclusion that flips across the kappa
range is labelled convention-dependent and may not be quoted without kappa."**
COST-SEMBIN-8d123b declines any conversion and calls the mismatch "the largest single
source of imprecision in the table." Across the program's own kappa grid the crossover
moves by 20 in n (time-only 303 → 293 → 283; product/sparse 375 → 364 → 354). No FIPS
verdict flips on kappa alone, so the record's verdict map survives — but its **crossover
figures are convention-dependent under a rule this program has already written down**,
and they are quoted without it.

### J6(c) Does the eq. (4) control have teeth? No.

The control compares the chain's degree-4 Macaulay width against a lower bound on
eq. (4)'s width taken at degree `2^{m-1}`:

| n | chain width (D = 4) | eq. (4) lower bound | margin | largest uncertainty the record itself discloses (degree bound 6) | ratio |
| --- | --- | --- | --- | --- | --- |
| 310 | 2^41.20 | 2^1998.50 | 1957.3 bits | 35.96 bits | **54×** |
| 409 | 2^43.42 | 2^3475.25 | 3431.8 bits | 38.19 bits | **90×** |
| 571 | 2^45.89 | 2^6022.72 | 5976.8 bits | 40.65 bits | **147×** |

The control's discriminating threshold sits **54 to 147 times further away** than the
largest error the record's own sensitivity analysis contemplates. Every error class in
that analysis — degree bound 5 or 6 (18–40 bits), dense versus sparse (20 bits),
max versus sum (≤ 1 bit), a variable count wrong by a factor of three (~6 bits) — leaves
the control passing.

Solved exactly rather than argued: the smallest degree bound `D` at which the chain's own
Macaulay width would rise above the eq. (4) lower bound is **D = 553** at n = 310,
**D = 1130** at n = 409 and **D = 2397** at n = 571 — a headroom of 549, 1126 and 2393
over Assumption 1's `D = 4`. The record's own live failure mode, Assumption 1 breaking so
that the effective bound is 5 or 6, costs 18–41 bits and sits roughly two orders of
magnitude inside that threshold. **The control cannot detect the one failure the record
itself says is the thing most likely to go wrong.**

**What would a failing eq. (4) control look like?** The chain side is
`log2 C(N, ≤4) ≈ 4·log2 N − log2 24`, which is bounded by 2^46 for any `N ≤ 7000`, while
the eq. (4) side is `log2 C(mn, 2^{m-1}) ≥ 2^1998`. For the control to fail the
machinery would have to charge the chain more than 2^1957 bits, which requires the
effective degree bound to be wrong by a factor of roughly 500 — not by one or two. The
only defect it can detect is confusing the chain's `D = 4` with eq. (4)'s `2^{m-1}`, i.e.
a transposition in the degree argument. **It is a typo detector for one line, not a
validity check on the cost model**, and it cannot fail for any input inside the record's
own uncertainty envelope.

### J6 breaking artifact

Both of the plan's alternatives are delivered, and a third that the plan did not ask for:
a prime-field cost model **located in the repository and actually run as the control**,
which retires the stated reason for the substitution; a demonstration that the eq. (4)
control is **vacuous within the record's own error envelope** (it cannot see a `D = 5`
or `D = 6` failure, which is the record's own named risk), leaving CLAIM A with five
controls rather than six; and the finding that the contract's D3 stopping rule, once the
control is real, **fires — and is mis-specified**, because it cannot distinguish a
mischarged baseline from a heuristic-conditional external model.

### What J6 does NOT break

CLAIM A is not void for want of this control. The four remaining controls — the Table 3
baseline reproduction (36/36 cells exact under the inferred truncation convention, the
argmin `m`, and the n = 302 crossover), the known-false metric-sensitivity check, the
invalid-input check, and the independent arithmetic — are live and did real work. The
missing control is the one that would catch a bias shared by the whole
summation-polynomial family, which is a real gap and a bounded one.

---

## The strongest objection I could NOT make land

**That the missing vOW time-memory tradeoff makes the record too kind to the baseline.**
This is the Coordinator's own recorded prior, it is the direction the handoff says a red
team should most want to find, and I could not make it land — the honest answer is the
opposite. Worked: at the record's operating point `M = 1`, the distinguished-point tail
penalty is `log2(1 + 2^{-w})`, which is **0.0000 bits** for every store size from 2^20 to
2^60. It first becomes 1.0 bit at `M = w = 2^20`. Charging the tradeoff as a *time* cost
moves the crossover by nothing; charging it coherently as a *memory* cost moves the
crossover 85 in n **against** Semaev. The prior had the sign right about there being an
asymmetry and the sign wrong about who it favours.

Three smaller objections I raised and could not sustain, recorded because a red team
that only reports its hits is reporting its bias:

1. **The 0.886 walk constant.** Two in n across the full plausible range (0.886 → 1.2533).
   Cannot matter. Closed.
2. **`m` not re-optimised under the memory-charged metrics.** Real — the record evaluates
   every metric at the argmin of stage-1 *time* — but worth 0 to 2 in n. The record leaves
   0.0 to 2.06 bits on Semaev's table and it changes no verdict.
3. **That `joint_balance.py`'s `c` fit is defective.** Refuted decisively. My independent
   real-valued argmin agrees with its coarse-grid-plus-refinement to five decimals at
   every rung, and the grid-cap assertion it carries is doing its job.

---

## Observations outside my joints (not verdicts, and not mine to judge)

**The review plan's own `blind_rederivation.parameters` block does not reproduce the
record's model, and will manufacture a false disagreement.** It states the working set as
"the number of degree-≤4 monomials in `N = m·ceil(n/m) + 2n` variables"; the record uses
`N = (m−2)·n + k·m` (J1's attack plan quotes the record's counts 2790 / 4099 / 6286,
which are the latter). At (409, 11) the two are 1236 and 4099. The plan additionally
describes the sparse reading as "one field element per nonzero", where the record's sparse
reading is `(nm)^4/24` columns at `n^3/m` nonzeros per row and does not involve `N` at all.
Read literally, the plan's parameterisation returns **crossover 306 and margin +29.77 at
n = 409**, against the 375 and +11.52 the plan tells the re-deriver to expect.

I own neither J1 nor the blind re-derivation and I take no position on which reading of
the memory model is right. I flag it because the round is set up to read a 69-in-n
disagreement as evidence about the implementations when it would be an artifact of the
plan's parameter statement, and because the plan's stated purpose for that block —
"disagreement localises to one of two named implementations" — is defeated if a third,
undeclared model is what the re-deriver actually implements. This is a `procedure_deviations`
item for the Coordinator, not a finding.

---

## Scope limits on everything above

- All of it is `bound_kind: heuristic_estimate` under `docs/claims-and-verification.md`.
  No curve was instantiated, no relation computed, no Gröbner basis run, no solve
  performed, and **no certificate attaches to any number in this report.**
- Nothing here is a statement about the security of B-409, K-409, B-571, K-571 or any
  other curve, **in either direction.** A metric under which n = 409 leaves the affected
  range does not make those curves safe, and one under which it does not does not make
  them attackable. Both are statements about two heuristic cost models.
- Every figure inherits Semaev's Assumption 1 (degree bound ≤ 4) and eq. (11)
  unchanged. Where Assumption 1 fails, every memory figure here is an underestimate by
  the amounts the record tabulates, which is one-sided against Semaev and would move the
  crossovers further up than I report.
- **The prime-field cells are conditional and I do not launder that.** Every cell of
  EXP-PFDR-c04716/runs/STATIC-001 is conditional on HEUR-001 of H-PFDR-06fd60, which that
  record prices at a 0.05 prior, is a zero-run static derivation, and is stated in field
  operations against a group-operation baseline (`kappa = 1`). Nothing here asserts that
  prime-field index calculus is fast. The proves-too-much result in J2(f) turns on the
  **difference** between two baseline conventions applied to the same cells, which is 29
  bits regardless of what those cells are worth; the D3 firing on the time axis (J6(b′))
  is the part that does depend on HEUR-001, and I have said so where it appears.
- My J2 corrections are scoped to the comparison. **I did not re-derive Semaev's memory
  accounting** (J1) and I take his numbers as the record states them. If J1 finds the
  memory model wrong, every crossover in this report moves with it.
- The Koblitz `sqrt(2n)` automorphism figure rests on KN-TECH-018's `sqrt(|Aut|)` rule
  (corpus, read) applied to `|Aut| = 2n` for a Koblitz curve, which is my own step and is
  marked `recalled`. It is not load-bearing: dropping it changes S5 from 441 to 441 in the
  sparse crossover.
- The vOW tradeoff model `T = W(1/M + 1/w)`, `Mem = 3n·max(w, M)` is my own restatement of
  the distinguished-point method as KN-TECH-006 and KN-LIT-012 describe it. **The primary
  paper (van Oorschot–Wiener 1999) was not opened by me**; those two internal records were.
  The load-bearing consequence — that the product is invariant along the curve and the
  record's point is dominated — follows from the structure, not from any constant, and it
  is confirmed by the numeric grid over `(w, M)`.

## One next concrete action

**Recompute `crossover_n_by_metric` as a two-parameter surface over
(metric × `store_log2`) with the baseline charged at a single coherent operating point on
its own tradeoff curve, and supersede COST-SEMBIN-8d123b with a record that reports it.**
Concretely: sweep `store_log2 ∈ {0, 10, 20, 30, 40, 48, 60}` — the contract already
declares four of these — and add one row per metric for the Pareto-minimum product of each
algorithm's own curve. This is under ten minutes of compute in the existing
`memory_charged_cost.py` (add `store_log2` and `processors_log2` to `crossover_curve`'s
kwargs, which already accepts them via `**kw`), it discharges a preregistered deliverable
the run did not meet, and it decides the only question that matters for CLAIM A's
headline: whether n = 409 straddles zero or sits below it. On my recomputation it sits
below it.

The cheapest single check that decides it is already run and costs nothing to repeat:
re-charge the 54 committed PFDR prime-field cells under the candidate baseline and require
that the KN-OPEN-001 ordering come out right. The record's present convention fails that
check at all three sizes; a coherent one passes at all three. Make it a standing admission
test for any memory-charged comparison this program publishes, because it is the one test
here that has a known answer.

Four corrections should travel with that record, each cheap and each independent of the
recomputation: the inverted cofactor direction (J2(d), also present in the review plan),
the "4–15%" range that its own ladder puts at 5–11% (J5(b)), the false premise under the
substituted control (J6(b)), and a rewritten D3 that names its conditionality filter, its
`kappa` tag, and a localisation step — otherwise the next faithful instantiation voids a
claim for a heuristic's sake (J6(b′)).
