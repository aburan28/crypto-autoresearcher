# ATTAINABILITY CHECK — ATTAIN-RR-EQD-1

Duty (2) of TASK-20260801-025. Named deliverable. Reviewer role served by the
red-team subagent (this harness has no reviewer subagent). Independence is
PROCEDURAL, not model-level: this session did not author the specification, the
driver or the reading rule, but the harness resolves author and reviewer to the
same underlying model (`claude-opus-5`). This report is NOT admissible toward
the three-model closure quorum of AGENTS.md rule 13.

Objects reviewed, by hash, recomputed in this session:

- `experiments/EXP-EQD-001/specification.yaml`
  sha256 `295d85c748cf9d1d14e2746d3067fbbbc0a7fc9ebd8b62ccbdbe021a6dc99431`
  (the "7792331b" hash-binding), byte-identical at 7792331bc and at HEAD.
- `experiments/EXP-EQD-001/reading_rule.yaml`
  sha256 `1e6a6e22f4929dada11e7432899cded2d72218a0df2f5a80e0d4e1acfbf21ce5`,
  frozen at TASK-20260801-023, archived at snapshot 2918680a7.
- Calibration package at snapshot 53e202dd2.
- `.../reviews/TASK-20260801-032/calibration_validation_report.yaml`
  sha256 `8eb593a0c4ef035f4e1b672bde00b431c611c3bf255041181094b764d40312c5`
  — RECOMPUTED AND MATCHES the value named in the handoff.

Every number below was recomputed by this session as code against the archived
JSON bytes. The reading rule's arithmetic and the Validator's arithmetic were
not adopted.

## VERDICT ON THIS DUTY: PASS. NO BAND AND NO BRANCH IS UNREACHABLE.

Two arithmetic errors were found. Both are non-load-bearing and neither makes
anything unreachable. They are recorded in §9.

---

## 1. The frozen thresholds, recomputed from the raw arrays

For each statistic and cell I sorted `cells.<bits>.replicate_values.<STAT>`
ascending, asserted length 200, and took index 198 (the 199th ascending order
statistic).

| statistic | bits | recomputed 199th o.s. | frozen value | match |
|---|---|---|---|---|
| STAT-CHI-16 | 16 | 315.4755320010126 | 315.4755320010126 | EXACT |
| STAT-CHI-64 | 16 | 4345.885305765976 | 4345.885305765976 | EXACT |
| STAT-KS1-E1 | 16 | 0.006191903131115506 | 0.006191903131115506 | EXACT |
| STAT-CHI-16 | 20 | 326.2209621328956 | 326.2209621328956 | EXACT |
| STAT-CHI-64 | 20 | 4293.229704961268 | 4293.229704961268 | EXACT |
| STAT-KS1-E1 | 20 | 0.006841670743639949 | 0.006841670743639949 | EXACT |

The archived `measured_order_statistics.<STAT>.value_at_199th_order_statistic`
agrees with my recomputation at all eight statistic-by-cell combinations
(including the two for the excluded STAT-KS1-E2, whose 199th order statistics
are 0.00623012475538165 at bits 16 and 0.00631421232876711 at bits 20).

The mins, medians and sample standard deviations quoted in
`record.threshold_provenance.entries` were reproduced and agree.

`dup_band`, from `cells.<bits>.dup_values`, 400 values each:

- bits 16: 3rd ascending = 0, 398th = 110. Frozen `[0, 110]`. EXACT.
  I independently confirm the file's structural counts: exactly 11 zeros,
  exactly 5 values equal to 110, exactly 2 values strictly above 110, and those
  two are 132 and 182. min 0, max 182, median 20.0, mean 30.8225.
- bits 20: 3rd = 0, 398th = 0. Frozen `[0, 0]`. EXACT. All 400 entries are 0.

Every threshold in the file traces to a named order statistic of a named CAL-1
array. That includes the two N-5 leg (c) endpoints, which I checked separately:
the declared intervals `[182.87972687693338, 321.9563383966048]` at bits 16 and
`[191.40792384797555, 335.54712432476106]` at bits 20 are exactly the 1st and
200th ascending order statistics of the STAT-CHI-16 arrays at those cells.
**There is no analytic-reference threshold anywhere in the file** — no
chi-square quantile, no uniform reference, no Dickman. The RV012-A1 repair is
STRUCTURAL, not cosmetic: a threshold set as an order statistic of the measured
null cannot exceed its declared false-rejection rate on a correct null whatever
the finite-size behaviour of the statistic is, which is exactly the property
RV012-A1 lacked.

## 2. Level arithmetic, redone

- 2/201 = 0.009950248756218905. Per-test exact level, confirmed.
- 5/401 = 0.012468827930174564. THR-EQD-1's declared two-sided STAT-DUP level.
- C(512,2) = 130816. 130816/256 = 511 exactly. 130816/4096 = 31.9375.
- int(round(0.05 × 130816)) = int(round(6540.8)) = 6541. Every CAL-2 replicate
  row at delta 0.05 records `n_replaced: 6541` at both cells. Confirmed.
- (1 − 2/201)**6 = 0.9417640626950365 → 0.9418. The reading rule's corrected
  family-wise figure is RIGHT.
- (1 − 2/201)**8 = 0.9231157309667123 → 0.9231, NOT 0.9234. See §9, defect A-1.

## 3. Branch-by-branch attainability at the frozen thresholds

### N-0 — INTEGRITY GUARD (order 1). REACHABLE both sides.

Firing side is reachable by construction, and the driver enforces it rather
than reporting it: `enumerate_factor_base` raises `ValueError` if the base is
not 512 distinct x-coordinates; `_draw_null_arm` and `run_real_arm` raise
`RuntimeError` on any nonzero degenerate (c_2 = 0) count, on a pair count other
than 130816, and on a range violation. `main()` maps `RuntimeError` to
`status: invalid` and `TimeoutError` to `failed_infrastructure`. **No arm can
record a c_2 = 0 draw and continue** — the RV012-A2 repair holds, and it is
structural: the enumeration is `np.triu_indices(512, k=1)` over 512 distinct
x-coordinates, so c_2 = (x_i − x_j)² is never 0 by construction and n = 130816
is not a post-hoc count.

Non-firing side is measured, not argued: across the calibration,
`degenerate_draw_count` 0 at both cells, `range_violations` 0,
`empty_cell_omission_count_K16` and `_K64` are 0 in every one of the 200 CAL-1
replicates at both cells (I checked all 800 entries), CTRL-EQD-S3 1000/1000 at
both cells, and the OBJ-NULL-RFB admissible-support fraction is exactly 1.0 at
both cells. A correct implementation measurably does not fire N-0.

### N-5 — APPARATUS FAILURE (order 2). ALL THREE LEGS REACHABLE.

**Leg (a), PC-1 fails to reject.** Firing route named and achievable (a plant
stream mis-indexed to n_replaced = 0 makes PC-1 a null-versus-null comparison,
which fails to reject ~99% of the time). Non-firing side measured: at delta
0.05 STAT-CHI-16 exceeded its threshold in 20/20 replicates at BOTH cells. I
recomputed the margins from the raw replicate rows:

- bits 16: min plant value 356.59175248031295 vs threshold 315.4755320010126,
  margin 41.1162 = 1.67 null sd. Max 461.91632096032276.
- bits 20: min 359.02551837653743 vs 326.2209621328956, margin 32.8046
  = 1.28 null sd. Max 477.6809573553279.

Both agree with the file to the digit. I endorse the file's own reading that
**the margin is real but not large and PC-1 is expected to reject, not
guaranteed to** — that is the honest statement and it is the one made.

**Leg (b), DV-7 rejects.** Firing route named and achievable (drawing the two
DV-7 arms from different curve instances). Non-firing side is exactly the CAL-1
distribution because DV-7 *is* a CAL-1 replicate comparison. Median
null-versus-null STAT-CHI-16 is 251.63 at bits 16 and 259.17 at bits 20,
2.59 and 2.62 null sd below their thresholds. Exact false-firing probability
2/201 per cell by exchangeability.

**Leg (c), DV-7 outside the full CAL-1 support.** Firing route named and
achievable, and it is the load-bearing one: comparing an arm against itself
gives a two-sample chi-square of exactly 0, far below the lower endpoints
182.88 and 191.41. I confirm the file's honest statement that on the UPPER side
leg (c) is strictly weaker than leg (b) (the 200th order statistic exceeds the
199th), so the distinctive content of leg (c) is the LOWER side, which leg (b)
cannot see at all. That is a defect class — an arm compared against itself —
that every rejection-side check in the design is blind to. Leg (c) is a real
addition, not decoration.

Combined N-5 false-firing probability at a cell, 3/201 = 0.014925, checked.

### N-1 — ARTIFACT TELL (order 3). BRANCH REACHABLE; one leg declared dead.

Above-band leg reachable at BOTH cells. I re-derived the file's collapse
arithmetic: a stand-in with support of order p rather than order p²/8 gives
n²/(2p) = 1.834e5 duplicates at bits 16 and 1.115e4 at bits 20, against upper
band edges 110 and 0. Fires decisively. Inside-band side reachable: 398/400
measured null draws at bits 16 and 400/400 at bits 20 lie inside.

Below-band leg UNREACHABLE at both cells — 0 is the minimum attainable value of
a count and it is the lower edge at both cells. **This is declared in advance in
the frozen file, in terms that bind later readers**, and I confirm the wording
does bind: `stat_dup_handling.D1_consequence_the_below_band_leg_is_dead` states
"THE DEDUPLICATION / WITHOUT-REPLACEMENT FAILURE MODE STAT-DUP EXISTS TO CATCH
IS UNDETECTABLE UNDER THIS FROZEN BAND, AT BOTH CELLS" and "no deliverable of
this batch may claim that failure mode was checked and passed", and
`attainability_argument.N_1.the_below_band_leg_is_declared_unreachable` repeats
it. That is a declared instrument gap, not an unreachable branch: N-1 as a
branch is reachable through its live leg.

I confirm the three degeneracy declarations the handoff named are present and
binding, not merely mentioned:

1. The declared exact level 0.01247 is NOT attained. Realized 2/400 = 0.005 at
   bits 16 and 0/400 = 0.0 at bits 20 (rule-of-three 95% upper bound ~0.0075).
   Stated at `D1_the_declared_exact_level_is_not_attained` with the direction of
   the error identified as conservative for false alarms. I verified the counts.
2. The below-band leg is dead at both cells. Above.
3. bits-20 DV-5 is a structural constant. Stated at
   `D2_bits_20_is_a_structural_constant` with the binding sentence "IT MUST
   NEVER LATER BE CITED AS A PASSED INTEGRITY CHECK. A control that cannot fail
   supplies no assurance." I confirm #E(F_p) = 767427 is odd (CAL-4,
   `two_adic_valuation_of_curve_order: 0`) and that all 400 bits-20 dup values
   are exactly 0. See §8 for a correction to the *mechanism* the file gives.

### N-2 — NOT DISTINGUISHABLE (order 4). THE FAVOURABLE BRANCH. REACHABLE.

This is the check BATCH-021 failed and it is the one I applied hardest. The
reading rule argues attainability from the six per-test marginals. **A product
of marginals is not a demonstration that the conjunction is reachable**, so I
tested the conjunction directly against the archived CAL-1 rows.

For each of the 200 CAL-1 null replicates at each cell I evaluated the exact
N-2 conjunction — all three retained statistics at or below their frozen
thresholds:

- bits 16: **197 of 200** replicates satisfy the full three-statistic
  conjunction. The 3 that do not are replicate 21 (STAT-KS1-E1), replicate 77
  (STAT-CHI-64) and replicate 147 (STAT-CHI-16) — three distinct statistics,
  three distinct replicates, no overlap.
- bits 20: **197 of 200**. Replicates 26 (KS1-E1), 89 (CHI-16), 185 (CHI-64).
- Both cells jointly, pairing by replicate index: **194 of 200 = 0.97**, against
  a product-of-marginals 0.970225.

The in-sample 197/200 and the out-of-sample 0.9418 are different quantities and
both are right: each threshold is the 199th of the same 200 values, so exactly
one in-sample value strictly exceeds each threshold; the exchangeability figure
2/201 governs a *fresh* value. The file correctly cites the exchangeability
figure. **The favourable branch is reachable by a wide and directly measured
margin, jointly and not merely marginally.**

The file's `end_to_end_figure_including_the_pre_empting_guards` (~0.90 after
N-1 and N-5 pre-emption) is arithmetically consistent and is the more honest of
the two figures; both are reported and neither is presented as the other.

### N-4 — DISTINGUISHABLE (order 4). REACHABLE BY MEASUREMENT.

At delta 0.05 STAT-CHI-16 rejected in 20/20 replicates at bits 16 AND 20/20 at
bits 20 — I recomputed this from the raw replicate rows using my own 199th
order statistics, not the archived reference. An OBJ-PLANT-0.05 object
satisfies the N-4 condition at both cells in all 40 measured replicates. N-4 is
not reachable only in argument.

### N-6 — SPLIT VERDICT (order 4). REACHABLE, WITH A MEASURED ROUTE.

At delta 0.01 the retained per-cell rejection counts are, recomputed:
bits 16 — CHI-16 0/20, CHI-64 1/20, KS1-E1 7/20; bits 20 — 0/20, 0/20, 7/20.
So the per-cell probability that at least one retained statistic rejects is
between 0.35 and 0.40 at bits 16 (union bounds) and exactly 0.35 at bits 20.
Treating the cells as independent (disjoint streams, different curve
instances), an OBJ-PLANT-0.01 deviation splits with probability
≈ 2 × 0.375 × 0.625 = 0.47. Confirmed.

### Exhaustiveness and mutual exclusivity — I tried to break it and could not.

Precedence is total: N-0 > N-5 > N-1 > exactly one of {N-2, N-4, N-6}. Given
the first three do not fire, each cell either satisfies the three-statistic
conjunction or does not; TT → N-2, FF → N-4, TF or FT → N-6. That is a
partition of a two-element boolean product. No result falls outside all
branches and none falls into two.

Tie behaviour: the rule is STRICTLY GREATER, so a value landing exactly on a
threshold does not reject. I verified that at all six retained
statistic-by-cell combinations exactly one CAL-1 value equals the 199th order
statistic and exactly one is strictly greater, so the rule is unambiguous and
conservative, never anti-conservative.

Driver/file agreement: `run_real_arm` builds `rejects` only over
`rr["retained_statistics"]` and sets `EQD_bit_size_not_distinguishable =
not any(rejects.values())`, which is exactly the reading rule's per-cell N-2
conjunction over the retained three. The machine-read part and the documented
part do not diverge.

## 4. Every rung of the resolution ladder

- **K = 16. POWERED, by measurement.** Expected 130816/256 = 511 per cell per
  arm, recomputed. `empty_cell_omission_count_K16` is 0 in all 200 CAL-1
  replicates at both cells, so every chi-square used the full 256 cells at
  df = 255. Detects the certified delta 20/20 at both cells.
- **K = 64. POWERED, and valid.** Expected 130816/4096 = 31.9375, above the
  five-per-cell floor and above a thirty-per-cell floor.
  `empty_cell_omission_count_K64` is 0 in all 200 replicates at both cells.
  Measurably less sensitive: 0.25 and 0.45 at delta 0.05, 20/20 at delta 0.10.
  Retained with that limitation declared in advance rather than discovered.
- **K = 256. DECLARED UNATTAINABLE IN ADVANCE AND RETAINED FOR NOTHING.** I
  verified POW-EQD-1 is present in the tree at 7792331bc, before any datum
  existed, with its powering sample sizes stated: 130816/65536 = 1.996 per cell,
  n ≥ 5×65536 = 327680 and n ≥ 30×65536 = 1966080. The clause
  `and_it_is_not_retained_for_a_secondary_role` states total exclusion, unlike
  the EXP-SMTH-001 u = 6 rung. No branch condition, statistic or threshold in
  the reading rule references K = 256. Retained for nothing, confirmed.

## 5. The certified delta and CAL-STOP-1

I re-evaluated the CERT-EQD-1 predicate myself over the full recomputed
detection-rate table (all four statistics × five deltas × two cells,
recomputed from raw replicate rows against my own thresholds — 40 cells of the
table, all matching the archive exactly):

| delta | CHI-16 (16/20) | CHI-64 (16/20) | KS1-E1 (16/20) | KS1-E2 (16/20) |
|---|---|---|---|---|
| 0.005 | 0/20, 0/20 | 0/20, 0/20 | 0/20, 0/20 | 0/20, 0/20 |
| 0.01 | 0/20, 0/20 | 1/20, 0/20 | 7/20, 7/20 | 1/20, 0/20 |
| 0.02 | 1/20, 0/20 | 0/20, 1/20 | 20/20, 20/20 | 0/20, 0/20 |
| 0.05 | **20/20, 20/20** | 5/20, 9/20 | 20/20, 20/20 | 1/20, 0/20 |
| 0.10 | 20/20, 20/20 | 20/20, 20/20 | 20/20, 20/20 | 1/20, 0/20 |

Deltas 0.005, 0.01 and 0.02 fail the 0.95 bar for both admitted statistics at
one or both cells. Delta 0.05 meets it for STAT-CHI-16 at 20/20 in each cell.
Smallest qualifying delta = 0.05, certifying statistic STAT-CHI-16, tie-break
does not arise. **CAL-STOP-1's first leg is genuinely NOT met** — the apparatus
has certified power and the stop correctly does not fire. This was not a
judgement call; it is the frozen predicate evaluated on the archived table, and
I got the same answer independently.

**Coarseness disclosure.** With R_REPS = 20 the 0.95 bar can only be met at
19/20 or 20/20, so the certification is effectively a 20-of-20 test. The file
says so at `precision_caveat_carried_forward` and gives numbers; I checked them:
a statistic with true power 0.90 passes 20-of-20 with probability
0.90²⁰ = 0.1216 (file: "about 12 percent"), and one with true power 0.97 fails
it with probability 1 − 0.97²⁰ = 0.456 (file: "about 46 percent"). Both right.
The file states "THE CERTIFIED DELTA IS A COARSE QUANTITY" and attributes it to
the calibration budget rather than the arithmetic. **That is disclosed
honestly** and it is carried into the branch dispositions.

**STAT-KS1-E1 at delta 0.02.** It reaches 20/20 at BOTH cells at delta 0.02 —
a stronger measured power fact than the certifying statistic's. CERT-EQD-1,
frozen at TASK-20260801-019, admits only STAT-CHI-16 and STAT-CHI-64 as
certifiers. **Recording it and not acting on it is the right call under the
frozen contract**, and acting on it would have been selection where only
substitution is permitted. This is the cleanest evidence in the package that
the freeze was applied against its author's convenience: acting on KS1-E1 would
have delivered a *better-sounding* certified delta (0.02 rather than 0.05) and
the Coordinator declined it. That is the correct direction of restraint.

**STAT-CHI-64 retention.** Correct under the frozen grounds. I checked all
three second_stop_leg grounds and none is met: non-zero null variance (sample
sd 88.5029 at bits 16, 93.9834 at bits 20), not identically zero, and the
largest-delta plant exceeds its threshold 20/20 at both cells. The non-monotone
bits-16 detection sequence (0.00, 0.05, 0.00, 0.25, 1.00) is noise: I
recomputed the underlying plant-arm mean shift and it IS monotone at
−0.33, +0.10, +0.05, +1.84, +7.22 null sd, exactly as the file states. The lone
delta-0.01 exceedance is consistent with a per-test level of 0.00995
(P(≥1 in 20) = 0.18). Low power against this alternative class is DECLARED in
advance, with the correct explanation (130816 points over 4096 cells rather
than 256) and the correct binding consequence: "a non-rejection by STAT-CHI-64
alone is weak information and no deliverable may present it otherwise."

## 6. The mechanical parse check that the file declares still owed

`record.driver_shape_conformance.residual_verification_owed` states the
load-and-index check was not performed by the freezing session and assigns it
to this review. **I ran it.** I imported the bound driver
(sha256 `bdb2601b195f314a4430fa80fcf8ab15ec0b605335a8386a93c2b9b3c7d7b02f`,
matching the value N-0 binds) and called its own `load_reading_rule()` on the
frozen file, then exercised every indexing site `run_real_arm` uses:
`rr["thresholds"][16]`, `[20]`, `rr["dup_band"][16]` and `[20]` unpacked to
`(0, 110)` and `(0, 0)`, `list(rr["retained_statistics"])`, `thr[sid]` for each
retained id at each cell, `float(rr["certified_delta"]) = 0.05`, and
`thr[rr["certifying_statistic"]]` at both cells. Key types are `int` at both
mappings. **All resolve. D-4 is genuinely defused, and it is now a verified
parse rather than an asserted one.**

## 7. Could I construct a result the rule classifies twice, or not at all?

No double classification and no gap. The precedence is total and the terminal
three branches partition a two-element boolean product (§3). The strict-greater
rule removes boundary ambiguity and the boundary behaviour is conservative.
Driver and file agree on the conjunction.

I did find one **misclassification** route — a result the rule classifies into
the wrong single branch. It is recorded in §8 and in `contract_review.yaml` as
objection RT025-O1. It is not a defect in attainability.

## 8. A correction to the duplicate-model account (RT025-O1 and RT025-O2)

The handoff asks whether the falsification of the spec's own n²/(2S) duplicate
model is recorded with the right force. My answer: **at bits 20 yes, plainly and
without hedging; but the file simultaneously reports the bits-16 agreement as a
"good match", and that is wrong. The model is void at BOTH cells and the
bits-16 agreement is a numerical coincidence.** I derived this, it was not in
the package.

The half-tuple {x_i, x_j} determines the unordered pair {A, B} =
{P_i + P_j, P_i − P_j}; conversely P = (A + B)/2 and Q = (A − B)/2.

- If #E(F_p) is ODD, halving is a bijection on E, so the map from unordered
  x-pairs to (e_1, e_2) is **injective**, and the duplicate count is
  identically 0 for EVERY factor base at that cell. At bits 20,
  #E = 767427 is odd. So 0 duplicates in 52.3 million half-tuples is a
  **theorem, not an improbable event under a valid model**. The file's
  framing — 46 predicted, 0 observed, P ≈ e^−46 — is right that the model is
  falsified, and understates it: the true probability is 0, not e^−46.
- If #E is EVEN with E(F_p)[2] = {O, T} (bits 16: #E = 46860, 2-adic valuation
  2, one nontrivial 2-torsion point), halving is 2-to-1 and the collisions are
  exactly the ι-translates, ι(x(P)) = x(P + T). Expected count for a random
  512-subset S of X_E is |X_E|²/2 · (512/|X_E|)⁴ / 2 = 512⁴/(4|X_E|²)
  ≈ 512⁴/p² ≈ 31.3 with |X_E| = 23430 (CAL-4).
- The birthday figure is n²/(2S) with S = p²/8, that is
  (512²/2)² · 4/p² = **512⁴/p²** — algebraically the SAME leading-order
  expression. The two mechanisms coincide numerically. Measured mean 30.8225.

Consequences, both documentation-level, neither touching a frozen number:

**RT025-O2.** `the_specs_own_idealized_model_is_falsified_at_bits_20` calls the
bits-16 agreement "a good match", which reads as partial corroboration of a
model that has no validity at either cell. And
`D2_bits_20_is_a_structural_constant` argues from multiplicity — "every
duplicate has multiplicity exactly 2 — the signature of a single involution
rather than of birthday collisions". **That observation does not discriminate**:
birthday collisions at an expected count of 31 out of 130816 draws into a
support of ~2.7e8 would also be essentially all of multiplicity 2. The
discriminating quantity is not multiplicity but whether the colliding
half-tuples are ι-translates of one another, which the archive does not record.
The conclusion the file reaches is correct; the argument given for it is not.

**RT025-O1, the consequential one.** At bits 16 the duplicate count is a
DETERMINISTIC ARITHMETIC PROPERTY of the factor base — #{ {i,j} ⊆ S : ι(i) ∈ S
and ι(j) ∈ S }. The band [0, 110] was calibrated on RANDOM S. The frozen
deterministic S (the 512 smallest x-coordinates of points of E) has no reason
to have the random overlap with ι(S); that is precisely the kind of arithmetic
structure this experiment exists to look for. If DV-5 on OBJ-REAL exceeds 110
at bits 16, **N-1 fires first under the precedence** and the run is disposed as
an ARTIFACT TELL carrying the positive instrument finding "the sampled quantity
is not behaving like the fibre invariant, so INT-2 as implemented is a
stand-in". That disposition would be wrong: a real, algebraically explicable
property of the deterministic factor base would be recorded as an instrument
defect, N-4 would be pre-empted, and the batch would be sent to "repair and
re-run" over a genuine signal. The direction of the error is to SUPPRESS a
positive finding.

Cheapest discriminating control, which I did NOT run because the handoff
forbids running any part of the real arm: at the bits-16 cell only, using the
already-recorded nontrivial 2-torsion x-coordinate 39489, compute ι on X_E and
report the fraction of the observed duplicate half-tuple pairs that are
ι-translates of one another. On a correct instrument that fraction is ≈ 1.0
whatever the count; on a support-collapsed stand-in it is ≈ 0. The diagnostic
is the mechanism, not the count.

Because the frozen rule may not be edited without a versioned amendment that
resets confirmatory status, the proportionate remedy is **not an edit**. It is
a binding scope condition at TASK-20260801-026 (condition C-2 in
`contract_review.yaml`).

## 9. Arithmetic errors found. Both non-blocking.

**A-1.** THR-EQD-1 `family_wise_statement_declared_in_advance` gives
(1 − 0.00995)⁸ = 0.9234 and a misread probability of 0.0766. The correct values
are 0.92312 and 0.07688. The reading rule quotes the contract's figures
verbatim at `family_wise_consequences_of_the_exclusion.the_contracts_declared_figure`
and therefore inherits the slip, and its stated exclusion delta of "1.84
percentage points" is really 1.87. The *superseding* figures — 0.9418 and
0.0582 — are correct, and those are the ones every deliverable must carry, so
nothing downstream depends on the wrong number. Cosmetic; correct it where it
is quoted rather than amending the frozen contract.

**A-2.** POW-EQD-1 (frozen in the spec, carried into the reading rule) states
that the five-per-cell floor for K = 256, n ≥ 327680, is "reachable at
Bfb = 810 since C(810, 2) = 327645". C(810,2) = 327645 < 327680, so Bfb = 810
does NOT reach it; Bfb = 811 does, at C(811,2) = 328455. The clause names both
numbers so a reader can see the error, and the thirty-per-cell figure is right
(C(1984,2) = 1967136 ≥ 1966080). K = 256 is excluded entirely and retained for
nothing, so this quantity is load-bearing for nothing. Cosmetic.

## 10. Scope of this attainability finding

This check is about whether measurements can LAND in each branch at the frozen
thresholds. It says nothing about whether any branch is CORRECT about the
Semaev map, nothing about H-EQD-001 or HEUR-DS-1 in either direction, and
nothing at any scale beyond the two toy field cells p = 46663 and p = 767551 on
one curve instance each at one master seed. The thresholds are not known to be
stable across curve instances at the same bit size; no across-instance
variability was measured, and the file says so.
