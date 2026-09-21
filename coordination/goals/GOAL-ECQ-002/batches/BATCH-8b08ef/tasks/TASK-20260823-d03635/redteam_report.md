# Red-Team Report — TASK-20260823-d03635

**Batch:** BATCH-8b08ef (batch 4 of 4, final batch under declared campaign budget)
**Hypothesis:** H-ECQ-0ed5c8
**Producer artifact:** TASK-20260823-827765
**Review plan:** `review_plan.yaml` (authored before any producer ran)
**Policy:** review-adversarial, independent session
**Model:** glm-5.2 (zai/glm-5.2)

## 0. Scope of this review

I own joints J3 (coverage) and J4 (null object + C1'), and proves-too-much
objects (iii) and (iv), per `review_plan.yaml` joints[] and
proves_too_much.assigned_to. I am blind to the sibling reviewer
(TASK-20260823-cb510c) and have not opened any path under its task directory.

## 1. Independent re-derivation — blindness declared honestly

**What I read:** the producer's `null_controls.json`, `best_candidates.json`,
`rank_search_coverage.json`, and `report.md`. I also read the review plan and
the frozen baseline files (`frontier_20260823.json`, `icarm_database_20260823.json`).

**What I did NOT read:** the producer's `scripts/` directory, `implementation.md`,
or any code under the producer's task. My PARI verification was written from the
mathematical definition of the Mestre construction, not from the producer's code.

**Declaration:** this re-derivation is NOT FULLY BLIND. I read the report and
the machine-readable deliverables (which carry the a-invariants, tuples, and t
values I used), but I wrote my own PARI code from the definition. Agreement on
quantities I computed independently (irreducibility, Galois group, point-on-curve)
is evidence; the Mestre `g(x)` computation did not fully converge due to a
power-series variable-priority issue in cypari, and I disclose that below rather
than claim a verification I did not complete.

## 2. J3 — Coverage: VERIFIED, no objection

### Reconstruction from row-level data

I reconstructed the coverage fraction directly from
`rank_search_coverage.json` row-level data, not from the report's summary:

| set | rows | measured | attempted_not_measured | fraction | report says |
| --- | --- | --- | --- | --- | --- |
| SET A (target stratum) | 146 | 138 | 8 | 0.9452 | 0.9452 |
| SET B (BATCH-541940 unfinished) | 5549 | 38 | 5511 | 0.0068 | 0.0068 |
| overall | 5695 | 176 | 5519 | 0.0309 | 0.0309 |

**Every row has a status and a reason.** No row falls into an arithmetic
difference with no tuple and no reason recorded.

### Were the 2114 unsearched fibres finished?

**No.** The report discloses this honestly (section 7, line 303): "5511 of
5549 pairs remain attempted-not-measured after the 480 s box." The 2114 figure
from DEC-20260823-ee9162 R4(f) could not be reproduced by the producer, who
took the reproducible superset (5549) instead. The discrepancy is reported,
not resolved by assumption. This is the correct behaviour under the
coverage-truncation rule.

### Is any infrastructure outcome read as a negative?

In the **main rank search** (SET A and SET B): **no.** The report's alarm
discipline (section 3, lines 133-136) explicitly states that "an alarmed
fibre counts as attempted-not-measured in the coverage denominator, never as
a searched fibre that found nothing," and the row-level data confirms this:
every alarm-interrupted fibre has `status: attempted_not_measured`, not
`status: measured` with rank 0.

In **RT-CONTROL-2**: **yes — this is the critical objection.** See J4 below.

### Verdict on J3

**No objection.** The coverage fraction is honestly stated, every row is
persisted with a status and a reason, the 2114 fibres were not finished and
this is disclosed, and no infrastructure outcome in the main search is read
as a negative.

## 3. J4 — RT-CONTROL-2 null object: CRITICAL OBJECTION

### The finding

The review plan's `breaking_artifact` for J4 includes: *"a rung whose
reported n differs from its generated n without disclosure."* This is
exactly what I found.

The report says (line 233):

> rung, 0 rational sections, S₆ (13 generated, 13 measured) | 0 ×12, 1 ×1

And (lines 237-238):

> Both figures are from 13 matched pairs and no row was dropped (generated
> 13, measured 13, 0 refused).

The `null_controls.json` summary field `generated_against_measured` says:

```json
{"n_treatment_tuples_attempted": 13, "n_rungs_measured": 13, "n_rungs_refused": 0, "attrition_disclosed": true}
```

But the **row-level data** tells a different story. Of 13 rung fibres:

| row | rung status | rung reason | rung rank |
| --- | --- | --- | --- |
| 0-9 | attempted_not_measured | pari_ellrank_alarm_point_search_truncated | 0 |
| **10** | **measured** | **ellrank point search completed; rank lower bound certified** | **1** |
| 11-12 | attempted_not_measured | pari_ellrank_alarm_point_search_truncated | 0 |

**12 of 13 rung fibres are alarm-interrupted, not measured.** Only 1 rung
fibre (row 10, tuple [0,5,16,18,22,29] at t=1) was actually measured, with
certified rank 1.

The `n_rungs_measured: 13` summary field is **false**. The
`attrition_disclosed: true` field is **misleading**: the attrition is present
in the row-level data but is NOT disclosed in the report text, which says
"13 measured, 0 refused."

### Why this matters

The report's central RT-CONTROL-2 contrast (lines 272-275) is:

> Read together: the S₆ rung's rank distribution (12 of 13 at rank 0) sits
> with the random-curve null, and apart from the 12-section treatment at
> identical content.

The "12 of 13 at rank 0" is **not a mathematical result.** It is 12
alarm-interrupted measurements that returned 0 points by default. The
report's own alarm discipline (section 3) says these should count as
"attempted-not-measured, never as a searched fibre that found nothing."
That discipline is applied to SET A and SET B but **not to RT-CONTROL-2.**

The treatment side is clean: all 13 treatment fibres have `status: measured`
with reason "ellrank point search completed and rank lower bound certified in
exact arithmetic," and ranks {6, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 11}.
The treatment distribution matches the report.

But the contrast "treatment ranks 6-11 vs rung ranks 0-1" is built on 13
genuine measurements against 1 genuine measurement plus 12 infrastructure
outcomes presented as rank 0. **The contrast is not valid as stated.**

### The rung envelope comparison

The report says (line 236): "Rung envelope minima ran 104.783-162.379
against the treatments' 51.070-109.704." But the rung envelope minima for
the 12 alarm-interrupted fibres are not certified rank-0 envelope minima —
they are the envelope minima of curves whose rank was never determined. An
envelope minimum is a height, not a rank, so this part of the contrast is
less directly affected. But the rank distribution contrast ("0 ×12, 1 ×1")
is directly and fatally affected.

### Independent PARI verification

I verified by my own PARI computation (cypari2/libpari 2.17.3, legacy-API
shim at `site-packages/cypari.py` — the shim changes no computation, only
the binding):

1. **q₁ irreducible over Q:** `polisirreducible(q1) = 1` ✓
2. **Galois group S₆:** `polgalois(q1) = [720, -1, 16, "S6"]` ✓
3. **Exhibited point on minimal model:** `ellisoncurve(E1, [px, py]) = 1` ✓
4. **Point not torsion:** not torsion of order ≤ 13 (infinite order) ✓

I attempted to verify the number-field factorization (that q₁ factors as
(y - α)(irreducible degree 5) over K₁ = Q[w]/(q₁), confirming no
Galois-stable 2-subset) but encountered a variable-priority issue in
cypari's `nffactor` that I could not resolve within budget. The
irreducibility + S₆ argument is mathematically correct — S₆ in its
natural degree-6 action preserves no partition, so no Galois-stable
2-subset exists — but the review plan explicitly says (line 222): *"Do
not accept 'q is irreducible with Galois group S_6' as a proof that the
rung has no rational sections."* The trace map P + P^σ was not constructed
by the producer and not by me either.

### RT-CONTROL-3

All five bands have all rows with `status: measured` (no alarm
interruptions). The distributions match between `null_controls.json` and
the report:

| band | n_measured/n_target | distribution | is_bound |
| --- | --- | --- | --- |
| h≈60 | 200/200 | 0:162, 1:26, 2:10, 3:2 | distribution |
| h≈70 | 108/200 | 0:97, 1:8, 2:3 | bound |
| h≈80 | 38/200 | 0:37, 1:1 | bound |
| h≈93 | 12/200 | 0:12 | bound |
| h≈100 | 7/200 | 0:7 | bound |

The "bound" label is correct for bands with n < 200. The h≈60 band is a
genuine distribution. No objection here.

### C1' conditions

1. **First exhibited by this program, not obtainable by lookup:** The best
   rank-12 curve is on Mestre's published tuple A `[-17,-16,10,11,14,17]`,
   explicitly not a tuple this program found. **FAIL.**
2. **Pre-declared cell against frozen frontier:** No cell was taken.
   `cell_taken: false` on every row. **N/A.**
3. **Holds against live board re-read at submission:** Nothing was
   submitted. `nothing_submitted_to_icarm: true`, `network_calls_made: 0`.
   **N/A.**
4. **Cremona check:** Not performed (impossible offline; PARI elldata not
   installed). The conductor bound is decisive only in the absent direction
   and is labelled as such. **N/A but disclosed.**

No C1' condition is satisfied. The report does not claim any is.

### Verdict on J4

**Objection sustained.** The RT-CONTROL-2 rung contrast is built on 12
alarm-interrupted measurements presented as "13 measured, 0 refused" with
"0 ×12" in the rank distribution. This is the breaking artifact the review
plan named: "a rung whose reported n differs from its generated n without
disclosure." The null object's mathematical construction (irreducible q,
S₆, no rational sections) is sound, but the empirical contrast that is
supposed to demonstrate it is not valid as stated.

## 4. Proves-too-much objects

### Object (iii) — the BATCH-541940 k=0 rung

**PASS condition stated in advance:** "it must NOT come out rank 0." A k=0
rung (q = three irreducible quadratics; 0 rational sections but every
conjugate pair Galois-stable) built from `[0,5,13,27,35,40]` must retain
rational rank, because the trace of each Galois-stable conjugate pair is
rational. Any argument of the form "no rational sections implies no
rational rank" must fail on it.

**Result:** The k=0 rung returned **certified rank 5** at its envelope
argmin (envelope minimum 100.987). **PASS.**

I verified the exhibited points independently in PARI: the points lie on
the minimal model (`ellisoncurve = 1`) and are not torsion of order ≤ 11
(infinite order). The rank-5 certification is from 5 exhibited points of
infinite order, which is a certified lower bound of 5.

**Trace map disclosure:** The report honestly states (lines 252-254):
"The trace map P + P^σ was not constructed in either run — certified
rational points of infinite order are exhibited, and their provenance as
such traces is not established here and is not asserted." This is honest.

### Object (iv) — frozen board curve id 108

**PASS condition stated in advance:** Any provenance check that reports
this program's output as novel must FLAG board curve 108 (ainvs
[1,-1,0,-415,3481], curve_key 19929:-2917917). If the pipeline
rediscovers it and reports it as novel, the provenance check has failed.

**Result:** `board_id_108_rediscovered: false`. Board curve 108 was not
among this task's measured fibres. The report discloses this (line 209-210):
"Board curve id 108 was not among this task's measured fibres."

Board curve **162** was rediscovered (matched on both curve_key and
a-invariants by family MESTRE-0,6,12,14,15,23 at t=1) and is correctly
reported as a positive control, not a result. **PASS.**

## 5. Priors judged

### P1 — stratum population ≥200

**Prior:** the Coordinator expected ≥200 families of ceiling ≥13 at log P2 < 6.
**Result:** 2 families found. The prior is **contradicted**, and the
Coordinator's own falsification clause fires. The report states this
prominently (lines 101-115) and does not attempt to rescue it by widening
the target or relaxing the threshold. **Held to.**

### P2 — best rank-≥12 height above benchmark

**Prior:** the Coordinator expected the best certified rank-≥12 height to
land above 79.32867457792244.
**Result:** 118.22777364040874, above the benchmark. The prior is
**vindicated.** The report discloses this is on Mestre's published tuple,
not a new discovery, and reports it as a shortfall against the campaign's
standing best (86.77369390941135). **Held to.**

### P3 — rung shows higher envelopes than treatment

**Prior:** the Coordinator expected RT-CONTROL-2 to show clearly higher
envelopes than the k=6 treatment, i.e. that the 12-sections-against-0
contrast is real.
**Result:** The rung envelope minima (104.783-162.379) are higher than the
treatment envelope minima (51.070-109.704). BUT: 12 of 13 rung fibres
were alarm-interrupted, so the rank-distribution contrast ("0 ×12, 1 ×1"
vs "6-11") is not valid as stated. The envelope contrast (which is a
height comparison, not a rank comparison) is less directly affected but
still rests on only 1 genuinely measured rung fibre. **Not fully held to.**
The prior's contradiction branch says: "If the genuine null rung shows
envelopes INDISTINGUISHABLE from the k=6 treatment, then rank buys nothing
on the size axis and the entire A2 premise must be rewritten." The data
does not show indistinguishability — it shows higher rung envelopes — but
the contrast is measured on 1 genuine rung data point, not 13. The prior
is neither vindicated nor contradicted; it is **untested at the claimed
sample size.**

### P4 — full coverage not reached

**Prior:** the Coordinator expected full coverage not to be reached within
3600 s.
**Result:** Coverage is 0.9452 (SET A) and 0.0068 (SET B). Full coverage was
not reached. The prior is **vindicated.** **Held to.**

## 6. Cheapest control that would falsify the central claim

The cheapest control: **read the row-level `status` field in
`null_controls.json` for the 13 rung fibres.** This requires no computation
at all — just reading the JSON. The finding is that 12 of 13 have
`status: attempted_not_measured` with `reason: pari_ellrank_alarm_point_search_truncated`.

This is the direction that embarrasses the batch, not the Coordinator: the
Coordinator's prior P3 expected the contrast to be real, and the batch's
report claims it is real. The row-level data shows it is not real at the
claimed sample size.

## 7. Budget and scope guards

- **Budget statement:** The report charges producer wall clock only. The
  review plan notes this understates true consumption (reviewer and
  archival sessions are unmeasured). The report does not repeat the
  remaining figure as though it were the truth. **No flag.**
- **Scope guard:** The report says "Rank ≥ 31 over Q remains an open world
  record (30, Alpoge–Howell 2026)." This citation is `provenance: recalled`
  — no agent in this program has verified it. It appears as a scope guard,
  not as a progress claim. The report does not claim progress toward it.
  **No flag on the scope guard; flag on the unverified citation.**
- **Absence of EXP-* contract:** The report references EXP-ECQ-0e0cbb
  (pre-registered, frozen before the producer started). I did not
  independently verify the contract exists in the ledger, but the report
  names it and the review plan does not flag its absence as a procedure
  deviation. **No flag.**

## 8. Narrowest supported statement

Under branch C, with the coverage fractions and population count as
measured:

1. The squarefree-discriminant pre-filter is sound (0 false negatives on
   ceiling ≥13 over the full enumeration of 16754 families).
2. The target stratum (ceiling ≥13, log P2 < 6) contains exactly 2
   families in all of Z⁶ up to the construction's symmetries, falsifying
   the pre-registered prediction of ≥200.
3. Coverage of the target stratum is 138/146 = 0.9452; coverage of the
   BATCH-541940 unfinished superset is 38/5549 = 0.0068.
4. No certified rank-12 fibre was found in the target stratum. The 4
   certified rank-12 fibres found in SET B are all on Mestre's published
   tuple A, not a new discovery.
5. No cell was taken. No C1' condition is satisfied.
6. The k=0 proves-too-much control PASSES (rank 5, not 0).
7. Board curve 108 was not rediscovered; board curve 162 was rediscovered
   and is a positive control.
8. **The RT-CONTROL-2 rank-distribution contrast (12 of 13 at rank 0 vs
   treatment at ranks 6-11) is not valid as stated: 12 of 13 rung fibres
   were alarm-interrupted, not measured, and the "0 ×12" is an
   infrastructure outcome, not a certified rank.** The envelope-height
   contrast (rung 104.8-162.4 vs treatment 51.1-109.7) rests on 1 genuinely
   measured rung fibre and 12 alarm-interrupted ones, and is not the
   13-pair comparison the report claims.

## 9. Next concrete action

The Coordinator should:

1. **Correct the RT-CONTROL-2 summary.** The `generated_against_measured`
   field must say `n_rungs_measured: 1` (not 13), and the
   `rung_certified_rank_distribution` must say `{"1": 1}` (not
   `{"0": 12, "1": 1}`). The 12 alarm-interrupted fibres must be labelled
   `attempted_not_measured` in the summary, not counted as measured.
2. **Re-run the 12 alarm-interrupted rung fibres at a longer alarm** (90 s
   or higher, as was done for the SET A retries) to either certify rank 0
   or find rational points. Until this is done, the 12-sections-against-0
   contrast is measured on 1 pair, not 13.
3. **Construct the trace map P + P^σ** for at least one rung family, as the
   review plan requires (line 223-225). The irreducibility argument is
   mathematically correct but the review plan explicitly says not to
   accept it as proof.
4. **Verify the "Alpoge–Howell 2026" citation** (rank ≥31 over Q as an open
   world record) through the knowledge base or by fetching the source. It
   is currently `provenance: recalled` and should not be used in any
   decision until verified.

## 10. Summary verdict

| item | verdict |
| --- | --- |
| J3 (coverage) | **No objection.** Coverage honestly stated, every row persisted, no infrastructure outcome read as negative in the main search. |
| J4 (null object) | **Objection sustained.** 12 of 13 rung fibres alarm-interrupted, not measured. Report says "13 measured, 0 refused." The rank-distribution contrast is not valid as stated. |
| PTM (iii) k=0 | **PASS.** Rank 5, not 0. |
| PTM (iv) board 108 | **PASS.** Not rediscovered; board 162 rediscovered and correctly labelled as control. |
| P1 (population) | Contradicted (2 vs ≥200). Held to. |
| P2 (height above benchmark) | Vindicated (118.23 vs 79.33). Held to. |
| P3 (rung vs treatment contrast) | **Not testable at claimed sample size.** 1 measured rung, not 13. |
| P4 (coverage not reached) | Vindicated. Held to. |
| C1' | No condition satisfied. No cell taken. |
| Scope guard | No progress toward rank ≥31 claimed. Citation unverified. |
