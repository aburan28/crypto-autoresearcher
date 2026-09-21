# TASK-20260823-416e78 — tuple-space scan of Mestre's construction

Executor · BATCH-541940 · GOAL-ECQ-002 · H-ECQ-8b600d
Repo `566cd442f`, branch `claude/elliptic-curve-high-rank-h0y9j2`, tree clean at start.
Requested policy `executor-implementation`; answered by **`claude-opus-5`**, reasoning effort
`medium`, `fallback_used: false`, `degraded_requirements: []`, `model_verified: false`
(no `adapter doctor --probe` was run in this session).

**Observations only.** Nothing here declares H-ECQ-8b600d supported, weakened or rejected, and
nothing here asserts a cell was taken. **Nothing was submitted to the ICARM endpoint.**

Every frontier number below was READ from
`coordination/goals/GOAL-ECQ-002/baseline/frontier_20260823.json` at run time by
`scripts/build_deliverables.py` and written straight into `best_candidates.json`; the sha256 of
the frozen snapshot was recomputed in that same run and matches the value H-ECQ-8b600d froze
(`118db069…cadc59`). No frontier value is transcribed into this report by hand: the table in §4
is a rendering of `best_candidates.json -> per_rank_threshold_vs_frozen_frontier`.

---

## 1. Headline, stated against both targets

| target | value | our best at that rank | result |
| --- | --- | --- | --- |
| INTERMEDIATE BENCHMARK, rank 12 | **79.329** (H-ECQ-8b600d `intermediate_benchmark.value`) | **86.7737** at certified rank >= 12 | **NOT beaten**, by **+7.4447** |
| PRE-DECLARED CELL r >= 12, min naive height | **69.33884136527462** (read from the frozen file) | **86.7737** | **NOT beaten**, by **+17.4349** |

So this is the *other* branch of the constraint the task card set out: **we failed to beat 79.329
and therefore also failed to beat 69.339.** It is not the "success of the method / shortfall
against the board" case. No cell was taken at any rank threshold; the full 12-row comparison is
in §4 and every row is a miss.

The best certified curve at rank >= 12 is new — it is not in the frozen ICARM snapshot by
`curve_key` or by a-invariants — but being new and being small are different things, and it is
not small enough.

## 2. What was measured

**13 391 distinct admissible Mestre families**, each one regenerated from its own integer 6-tuple, each
measured over an identical, pre-declared T-box of 73 parameter values (§7), each given its own
surface degree and its own Shioda-Tate ceiling from its own fibre configuration.

Measured envelope (minimum minimal-model naive height over the T-box):

* minimum **25.4298**, median **110.7045**, maximum **245.6902** — a spread of **220.26**.
* Published Mestre tuple A `(-17,-16,10,11,14,17)`: **79.6238** at t = 4, reproducing the
  BATCH-f2341e validator's independent 79.6 to four decimals. This was run as a pre-declared
  control (`C4` in RUN-...-001) *before* any tuple was scanned.
* Published tuple B `(399,380,352,47,4,0)`: **121.2252**.

**Tuple choice moves the raw envelope by 220 log units.** 1 489 of the 13 391 families have a
measured envelope below 79.329. On the raw-envelope reading, prior P1 is confirmed and confirmed
by a wide margin.

**That reading is the wrong one, and the scan says why.** The envelope and the attainable rank
are not independent: they are two readings of the same fibre configuration (§3). Of the 1 489
families whose envelope is below 79.329, only **46** have a Shioda-Tate ceiling that even permits
rank 12, and none of those 46 produced a certified rank-12 fibre inside the searched T-box.

## 3. The coupling that decides the outcome

Every one of the 13 391 families is an elliptic **K3** (`d = 2`, no exceptions), so the generic
bound is 10d - 2 = 18. **No family reaches it.** Each has 18-20 `I_1` fibres over the finite
T-line and exactly one multiplicative fibre at T = infinity, and the type of THAT fibre decides
everything:

| fibre at T = inf | sum(m_v - 1) | own Shioda-Tate ceiling | families | min envelope | max certified rank observed |
| --- | --- | --- | --- | --- | --- |
| `I_14` | 13 | **5** | 17 | 25.430 | 5 |
| `I_12` | 11 | **7** | 16 | 38.353 | 7 |
| `I_10` | 9 | **9** | 13 257 | 30.323 | 8 |
| `I_8` | 7 | **11** | 5 | 29.773 | 9 |
| `I_6` | 5 | **13** | 82 | 50.450 | **12** |
| `I_4` | 3 | **15** | 14 | 70.259 | **12** |

Read the last three columns together, and read them precisely, because the pattern is not a
clean monotonicity and should not be reported as one.

* The **maximum certified rank observed rises monotonically with the ceiling**: 5, 7, 8, 9, 12,
  12. Certified rank 12 was reached only in the two smallest classes, `I_6` (82 families) and
  `I_4` (14 families).
* The **minimum envelope does not** rise monotonically across the low classes: 25.43, 38.35,
  30.32, 29.77 for ceilings 5, 7, 9, 11 is within the noise of very unequal class populations.
  What it does do is **jump once, at exactly the place that matters** -- 29.77 at ceiling 11,
  then 50.45 at ceiling 13 and 70.26 at ceiling 15. The two classes that can host rank 12 are
  the two classes whose envelopes sit 20 to 40 log units above everything else.

The same reducible fibre that buys a small model destroys the Mordell-Weil rank that made the
model worth having. This is
exactly the mechanism the BATCH-da59ec validator found in Nagao's family (an `I_4` at infinity
costing 3), generalised: here it is a one-parameter family of the same defect, and the campaign's
Axis-A2 premise runs straight into it.

Two consequences worth recording separately, because neither is in H-ECQ-8b600d:

* **The generic K3 ceiling 18 is not merely an overstatement for one family — it is attained by
  none of the 13 391.** The best ceiling any admissible Mestre tuple achieves is 15.
* **99.0 % of admissible tuples have ceiling 9**, i.e. their twelve sections cannot span rank 11
  OVER Q(T). The ceiling bounds the GENERIC rank; a single special fibre may exceed it, and this
  is a real caveat, not a formality -- but the highest rank certified anywhere in that class was
  8. Mestre's rank->=11 statement is a statement about the sparse `I_4` subfamily (14 of the
  13 391 here). The tuple search is therefore not a search over "rank-11 families with varying
  intercept"; it is mostly a search over families whose generic rank has collapsed.

## 4. Certified rank versus the frozen frontier

Every rank is a LOWER bound from exhibited points verified in exact arithmetic by
`exact_certify.py` (BATCH-f2341e pipeline, unchanged: stdlib only, no floating point, no PARI, no
Selmer bound). PARI `ellrank` was used only to SEARCH for points; where it returned
`r_low = r_high` it also gives an independent upper bound, recorded per fibre but never used as
our rank. 5 092 distinct curves were certified.

| rank threshold | frozen frontier min naive height (read at run time) | our best certified | delta | cell taken |
| --- | --- | --- | --- | --- |
| >= 1 | 11.6136 | 25.4297 | +13.8161 | no |
| >= 2 | 13.5255 | 25.4297 | +11.9043 | no |
| >= 3 | 16.8284 | 29.7728 | +12.9443 | no |
| >= 4 | 20.7040 | 29.7728 | +9.0687 | no |
| >= 5 | 24.3180 | 29.7728 | +5.4548 | no |
| >= 6 | 30.3760 | 47.1788 | +16.8028 | no |
| >= 7 | 35.7790 | 49.5960 | +13.8170 | no |
| >= 8 | 41.8264 | 51.0697 | +9.2433 | no |
| >= 9 | 47.9739 | 61.1274 | +13.1535 | no |
| >= 10 | 54.3490 | 68.6386 | +14.2897 | no |
| >= 11 | 61.5069 | 74.1215 | +12.6146 | no |
| >= 12 | 69.3388 | 86.7737 | +17.4349 | no |

The gap is remarkably flat at +9 to +17 across the whole board. Note in particular
**74.1215 at certified rank >= 11**: that number is below the rank-12 benchmark 79.329, and it
must not be read as beating it. 79.329 is a rank-12 value and 74.1215 is a rank-11 curve; the
right incumbent for it is the r >= 11 cell at 61.5069, which it misses by +12.61.

### The four reported curves, in full

All four are in `best_candidates.json` in ICARM record format with every exhibited point. For
each, the deliverable builder independently (i) recomputed c4, c6 and the naive height **from the
minimal a-invariants alone in pure Python with no PARI** — agreement to 0.0 in all four cases;
(ii) re-ran `exact_certify.py` from scratch on the exhibited points — same rank in all four
cases; (iii) re-checked every point on the minimal model in exact rational arithmetic; and
(iv) checked the curve against the frozen ICARM snapshot by `curve_key` and by a-invariants —
none of the four is a board curve rediscovered.

| rank | a-invariants | h | family (tuple) | t | pts |
| --- | --- | --- | --- | --- | --- |
| >= 9 | `[1, -1, 1, -14718207, 16462936056]` | 61.1274 | (0,1,29,32,33,37) | 10 | 20 |
| >= 10 | `[0, 0, 0, -171750343, 929343771658]` | 68.6386 | (0,2,44,49,51,58) | 4 | 20 |
| >= 11 | `[1, -1, 0, -1119287770, 13845239780296]` | 74.1215 | (0,1,53,55,64,67) | 9 | 22 |
| >= 12 | `[0, 0, 0, -75951713419, 5158556462007754]` | **86.7737** | (0,20,40,45,52,77) | 23 | 23 |

## 5. The envelope law, both arms fitted separately

The two arms were fitted **independently** with a free breakpoint chosen to minimise total SSE;
no single line was fitted across the vertex. Over all 13 391 families:

* **steep arm slope: median 22.10, interquartile range [19.83, 24.32]**, against the forced value
  **12d = 24** for d = 2. The measured median sits just under the forced slope, which is what a
  box truncated at t = 800 should produce; the IQR straddles 24.
* **flat arm slope: median -0.48** — flat, as the law says.
* The crossover and both intercepts are recorded per family in `tuple_envelope_scan.json`.

Regression of envelope on the coefficient-content statistic log P2 (P2 = sum of squares of the
centred roots of q, translation-invariant and scale-covariant of weight 2) over all families:
**envelope = -4.54 + 14.69 * log P2, R^2 = 0.19**. Content predicts the envelope in the mean and
predicts it weakly; the ceiling stratification of §3 explains far more of the variance.

## 6. THE REQUIRED NULL — run, and it does not come out clean either way

The control owed since BATCH-f2341e. `q` is a monic degree-6 polynomial with **k rational roots
and (6-k)/2 irreducible quadratic factors**, satisfying the SAME admissibility condition. The
construction, the quartic, the surface degree, the T-box and the height code are all held fixed;
only the number of rational sections changes (2k). Rungs are compared inside the log-P2 window
all four cover, [5.100, 8.178], so rank is not confounded with size:

| rung | rational sections | n in window | min envelope | median envelope |
| --- | --- | --- | --- | --- |
| k = 6 (treatment) | 12 | 147 | 44.84 | 101.17 |
| k = 4 | 8 | 44 | 42.76 | 79.61 |
| k = 2 | 4 | 50 | 49.85 | 111.21 |
| k = 0 | 0 | 96 | 69.05 | 136.44 |

Two things, and they point in different directions:

* **The k = 0 rung is clearly worse** — no rational section at all costs about 35 log units of
  median envelope and 24 of minimum envelope against the treatment. To that extent rank does buy
  something on the size axis, and P3's prediction holds at the bottom of the ladder.
* **The k = 4 rung is NOT worse than the treatment; it is better** (median 79.61 vs 101.17,
  minimum 42.76 vs 44.84) at matched content. **Going from 8 rational sections to 12 buys nothing
  measurable on the envelope.** P3 predicted the low-rank rungs would show "clearly higher"
  envelopes; at the k = 4 rung the measurement goes the other way, and at k = 2 the median is
  higher but the minimum is within 5 of the treatment.

Certified ranks at each rung's envelope argmin are recorded too, and they carry an independent
warning: the k = 0 families — which have **no rational section by construction** — reached
certified ranks of 6, 5, 5, 4, 4, ... at their envelope minima, i.e. comparable to the treatment
rung's 8, 6, 5, 5, 5, 4, ... . At the small-|t| specialisations where the envelope lives, the
rank that is actually there is largely not coming from the construction's sections.

## 7. Scope, and what would move it

* **Tested parameters.** Tuples: all canonical admissible integer 6-tuples of spread <= 74
  (13 624 of them, from 16 108 764 tuples tested exhaustively for admissibility), plus
  296 admissible tuples found among 3 000 000 random draws from spread 57-600, plus the two published tuples. Canonical form quotients the two
  exact symmetries of the construction (translation `a_i -> a_i + c`; simultaneous scaling
  `a_i -> L a_i`, `T -> L T`) and reflection.
* **T-box.** `t = n/d` with `1 <= n <= 30`, `d in {1,2,3}`, `gcd(n,d) = 1`, plus
  `t in {40,60,90,130,200,300,500,800}`; 73 values. Only `t > 0`, because `r` is even in `T` so
  `h(-t) = h(t)` identically. The large values exist so the steep arm is inside the box rather
  than on its edge.
* **This is a lower-bound search.** Every "min naive height at certified rank >= r" is the minimum
  over what was searched. Fibres outside the T-box, tuples of spread > 74, and rational t of
  denominator > 3 are untested. A certified rank is a lower bound on the true rank.
* **Transfer.** Nothing here transfers to families outside Mestre's construction, and nothing
  here says anything about a construction that is not `q(x-T)q(x+T) = g^2 - r`.

**An admissibility fact not in the hypothesis, which bounds any future tuple search.**
`deg_x r = 4` — needed for `y^2 = r(x,T)` to be genus 1 at all — is **not automatic**. It is a
single codimension-1 condition on the tuple, measured here in closed form as
`12*sum(c_i^5) = 5*(sum c_i^2)(sum c_i^3)` with `c_i = 6a_i - sum(a)`, verified against the
symbolic `deg_x r` on 400 random tuples with zero mismatches and satisfied by both published
tuples. **0.15 % of tuples of spread <= 56 satisfy it, and 0.064 % of spread 57-74.** Every other
tuple gives a genus-2 quintic. Tuple space is therefore ~3 orders of magnitude smaller than a
naive count suggests, which is the main reason a broader search is cheaper than it looks — the
admissibility test costs microseconds and the measurement only runs on survivors.

## 8. Runs

| run | what | status |
| --- | --- | --- |
| `RUN-ECQTUP-416e78-001` | construction + map + Jacobian + prior-measurement + negative controls | `completed_valid`, all 5 pass |
| `RUN-ECQTUP-416e78-002` | first tuple scan, 10 694 tuples | **`invalid_measurement`** — see `runs/VALIDITY-CORRECTION-RUN-002.md` |
| `RUN-ECQTUP-416e78-003` | corrected scan, 5 627 admissible families, spread <= 56 | `completed_valid` |
| `RUN-ECQTUP-416e78-004` | exact certification of best-envelope families + low-ceiling control | `completed_valid` |
| `RUN-ECQTUP-416e78-005` | rank search, top-400 by envelope | `completed_valid`, budget reached at 3 898 fibres |
| `RUN-ECQTUP-416e78-006` | rank search restricted to ceiling >= 12 | `completed_valid`, budget reached at 584 fibres, 2 PARI alarms |
| `RUN-ECQTUP-416e78-007` | THE REQUIRED NULL, four rungs | `completed_valid` |
| `RUN-ECQTUP-416e78-008` | admissible tuples sampled from spread 57-600 | `completed_valid` |
| `RUN-ECQTUP-416e78-009` | scan of spread 57-74 | **`invalid_measurement`** — bad CLI flag, produced no result; superseded by 010 |
| `RUN-ECQTUP-416e78-010` | scan of spread 57-74, 7 603 families | `completed_valid` |
| `RUN-ECQTUP-416e78-011` | rank search on those, ceiling >= 12 | `completed_valid`, budget reached at 687 fibres, 1 PARI alarm |
| `RUN-ECQTUP-416e78-012` | deliverables, first build | superseded by 013 (missing the spread-57-74 scan) |
| `RUN-ECQTUP-416e78-013` | deliverables | `completed_valid` |

Three runs hit their declared time budget (005, 006, 011) and PARI `alarm` fired three times
across the searches. **Both are infrastructure outcomes and neither is mathematical evidence.**
Concretely: the searched fibre sets are smaller than the fibre sets the families offer, so the
§4 minima are upper bounds on what this method reaches, not its limit.

Total measured wall clock ~2 470 s of the 3 600 s budget; peak RSS well inside 4 GB; 13 runs of
the 80-run limit.
