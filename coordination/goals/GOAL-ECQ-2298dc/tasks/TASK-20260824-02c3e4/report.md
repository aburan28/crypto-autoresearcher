# EXP-ECQ-f5af06 v2 — execution report

**Task** TASK-20260824-02c3e4 · **Goal** GOAL-ECQ-2298dc · **Question** RQ-ECQ-e9b361
**Contract** `experiments/EXP-ECQ-f5af06/specification.yaml` (v1, immutable, binding in full)
**Governing overlay** `experiments/EXP-ECQ-f5af06/amendments/PA-ECQ-f5af06-v2-triage-gate-sign.yaml`
**Approval** `ledger/decisions/DEC-20260824-5246b7.yaml` (`decision: approve`)
**Implementation commit at run start** `f10c841e2` (the working tree carried this task's own
uncommitted scripts and deliverables; the frozen contract, the frozen overlay and the reused
certifier were unmodified)

This report records observations. It draws no conclusion about any hypothesis and declares no
heuristic validated or refuted. Those judgements belong to the Reviewer and the Coordinator.

---

## 1. The gate was inverted in v1 and is corrected here

v1 froze the part-C triage gate as *the exact gate is applied to exactly the **top 20 candidates
by S** in each arm*, with `S = sum over p <= 500 of (a_p log p) / p`. **S decreases with rank**, so
top-by-S selects the candidates each arm's own score ranks as **least** promising — the opposite of
the triage's stated purpose. Under `PA-ECQ-f5af06-v2-triage-gate-sign` (CHG-1, CHG-2) the gate is
**the 200 candidates of smallest S per arm — most negative first**, ties broken by smallest |D|
(respectively |v|), then positive sign before negative. The defect was the Coordinator's; v1's
Executor applied the frozen rule exactly as written and refused to self-authorise a change, which
was correct.

**In one sentence: S decreases with rank, so the gate selects the most negative scores.**

### Calibration table (CTL-GATE-DIRECTION, blocking — measured in this run set)

| curve | rank used | basis of that rank | S measured here | overlay reference | in pass condition |
|---|---|---|---|---|---|
| 11a1 | 0 | external, **not** verified by this program (rank 0 is a rank *equality* claim) | +1.5742 | +1.57 | **no** |
| 37a1 | 1 | certified rank lower bound 1 inside this program | -4.0589 | -4.06 | yes |
| 389a1 | 2 | certified rank lower bound 2 (CTL-POSITIVE-INDEPENDENCE, this run set) | -11.0355 | -11.04 | yes |
| 5077a1 | 3 | certified rank lower bound 3 (CTL-POSITIVE-INDEPENDENCE, this run set) | -18.0995 | -18.10 | yes |
| ICARM no. 302 | >= 31 | certified rank lower bound 31 (part A, this run set) | -38.8258 | -38.83 | yes |

Pass condition, stated in the overlay before the run: S(37a1) > S(389a1) > S(5077a1) > S(no. 302),
**and** the gate's own selection routine returns the toy population in the order
302, 5077a1, 389a1, 37a1. Both hold. **CTL-GATE-DIRECTION: PASS.** The four rows the control rests
on are all certified rank lower bounds produced by this program's own runs, so the gate direction
depends on no external rank claim. The table is not a proof: certified lower bounds do not pin true
ranks, five curves are not a distribution, and the score certifies nothing — every rank reported
below is decided by the exact gate.

### What this does and does not do to v1

**v1's results stand exactly as recorded and are reported beside v2's, never replaced:** A-FULL
31/31, B-NULL at 2 347 563 / 2 347 563, C-NULL with maximum certified rank 0 in both arms. What the
overlay re-scopes is what v1's C-NULL *ever supported*: it is **uninformative about the twist
neighbourhood**, because the gate examined the twenty candidates each arm's own score ranks as
least promising. It may not be cited as evidence that the neighbourhood is barren. That re-scoping
is a statement about what the run always licensed, not an edit to it.

---

## 2. Runs

Four runs of a maximum of 40, all terminal, all written directly under
`experiments/EXP-ECQ-f5af06/runs/RUN-<id>/` with `run.experiment_id` set from the start and
validator-schema manifests plus `command.txt`, `environment.json`, `stdout.log`, `stderr.log` and
`raw-result.json`.

| run | part | status | wall | cap | outcome |
|---|---|---|---|---|---|
| `RUN-ECQ-f5af06-v2-A-certify` | A | completed_valid | 4.2 s | 200 s | A-FULL, k = 31 of 31 |
| `RUN-ECQ-f5af06-v2-B-extension` | B | completed_valid | 140.2 s | 700 s | B-NULL, box exhausted |
| `RUN-ECQ-f5af06-v2-C-twists` | C | completed_valid | 694.8 s | 2400 s | C2-NULL, all regions exhausted |
| `RUN-ECQ-f5af06-v2-FINAL-reverify` | re-verification | completed_valid | 1.9 s | 300 s | certificate re-verified |

No run was superseded, none timed out, no memory cap was breached, no run made a network call, and
nothing was submitted to the ICARM endpoint. cypari/PARI is used nowhere, including the triage.

---

## 3. Part A — calibration re-run (branch **A-FULL**, k = 31 of 31)

**Part A is re-run for calibration, not for a new result.** Its purpose is to put the three
mandatory controls in the *same run set* as any v2 positive, which claim-bar clause (5) requires and
which a v1 control cannot discharge. **v1's A-FULL is not superseded, not strengthened and not
re-earned by it.**

- k = 31 of 31; F_l-rank 31 at l = 2 over 45 good primes; torsion bound 1.
- Search bounds used: `max_prime 1500, torsion_primes 8, l in (2,3,5,7,11,13), max_good_primes 250`.
  Recorded because the contract makes them the Executor's to raise **and to record**; raising a
  search bound changes nothing about what is proved. The certifier's **defaults**
  (`max_good_primes 60`) were re-measured *in this run*: k = 27 of 31 in 1.8 s, so the binding bound
  is `max_good_primes`, not `max_prime`. (v1 reported the same 27 / 1.9 s; that figure is quoted
  beside, never reused as this run's measurement.)
- `CTL-CITED-INPUT-AGREEMENT` **PASS**: `on_curve_failures` empty for all 31 points; recomputed
  log max(|c4|^3, c6^2) = 468.2771 and log|disc| = 453.0469, both agreeing with the cited values to
  the 4 decimal places quoted.
- Certifying no. 302 is a **confirmation of someone else's result** and an external positive
  control, never this program's own rank result. **Rank >= 31 over Q is the live world record and it
  is claimed** (ICARM curve no. 302, posted 2026-08-23).

---

## 4. Part B — 32nd-point search (branch **B-NULL**)

Frozen v2 box (CHG-6, verbatim): *x = u / w^2 in lowest terms, w an integer in [1, 100],
gcd(u, w) = 1, |u| <= 30 000 000 for w = 1 and |u| <= 300 000 for 2 <= w <= 100.*

- **N_B_v2 = 95 899 629, computed from the frozen description and written to disk before any
  candidate was tested.** Coverage **95 899 629 / 95 899 629 = 100 %**, box exhausted in 140.0 s.
- 0 hits, hence 0 rank-increasing and 0 index-reducing points. `CTL-SATURATION-DISTINCTION`
  **PASS** (a discovered P against a presented subgroup {2P} on rank-1 37a1 is classified
  index-reducing, not rank-increasing).
- **v1 reported beside, not replaced:** B-NULL at 2 347 563 / 2 347 563 over the v1 box (w <= 30,
  |u| <= 10^6). The v2 box strictly contains the v1 box, so v1's fraction remains recoverable as a
  sub-fraction and no v1 candidate is dropped.
- **What a miss licenses, and nothing more:** *no point of E(Q) was found within the frozen box at
  coverage 95 899 629 / 95 899 629.* A miss is consistent with the board's "rank exactly 31" reading
  **and equally consistent with the box being far too small**, and cannot distinguish the two. The
  31 known points have x-numerators of about 33 decimal digits; v1's box reached 7 and v2's reaches
  8. **The gap is not closed by this or any affordable box.**

---

## 5. Part C — twists and near neighbours under the corrected gate (branch **C2-NULL**)

### 5.1 Frozen denominators, computed before anything was scored or tested

| quantity | exact value (binding) | Coordinator hand estimate (explicitly non-binding) |
|---|---|---|
| N_C_TWIST_v2 (squarefree D, 2 <= \|D\| <= 10000, plus D = -1) | **12 165** | ~12 159 |
| N_C_NULL_v2 (a6 -> a6 + v, 1 <= \|v\| <= 6000, zero-discriminant discarded) | **12 000** (0 discards) | 12 000 |
| N_BC_v2 (reduced box, w in [1,15], \|u\| <= 500 000 for w = 1, <= 10 000 otherwise) | **1 167 027** | ~1 167 031 |

Each was derived from the frozen description alone and written to disk before the first candidate in
its region was scored or tested. Where an exact count differs from an estimate, the exact count
governs and the estimate was simply wrong. No denominator was recomputed, narrowed or widened.

### 5.2 Coverage — every region exhausted

| arm | generated | discarded | scored | triage coverage | gated | reduced-box coverage per gated curve |
|---|---|---|---|---|---|---|
| twist | 12 165 | 0 | 12 165 | **12 165 / 12 165 = 100 %** | **200 / 200** | 1 167 027 / 1 167 027 on all 200 |
| null | 12 000 | 0 | 12 000 | **12 000 / 12 000 = 100 %** | **200 / 200** | 1 167 027 / 1 167 027 on all 200 |

Every generated candidate in both arms is persisted in `twist_search.json` with an identifier, a
status and a reason (24 165 rows, reduced at source to one compact array each under the
artifact-size budget). Attempted equals reported; there is no arithmetic difference.

### 5.3 Result of the exact gate

**Zero points were found in the frozen reduced box on any of the 400 gated curves. The maximum
certified rank lower bound over Q is 0 in both arms.** No certificate was produced by part C
(`certificate_kind: none` on every row, stated explicitly). Branch **C2-NULL**.

**Scope of that negative, exactly and narrowly:** no certifiable rank was found *within the frozen
reduced box B-C, among the 200 lowest-S candidates per arm, over the frozen ranges |D| <= 10000 and
|v| <= 6000, at 100 % triage and 100 % box coverage.* It is **not** a statement that the twist
neighbourhood is barren: the reduced box reaches 6-digit numerators while the gated curves have
naive heights (of the stated model) of 508.5-531.8 in the twist arm and 476.6 in the null arm. It is
a statement that **this gate at this depth found nothing.** Unlike v1's C-NULL, this one does bear
on the neighbourhood at this depth, because the gate now examines the candidates each arm's own
score ranks as most promising; what that supports is the Reviewer's and Coordinator's judgement, not
the Executor's.

### 5.4 v1's gated set beside v2's — both stand, each labelled with its rule

| arm | v1 rule (top 20 by S, largest first) | v2 rule (200 smallest S, most negative first) |
|---|---|---|
| twist | S in [+7.195, +12.009], max certified rank **0** | S in [-15.817, -9.119], max certified rank **0** |
| null | S in [+5.518, +13.048], max certified rank **0** | S in [-15.675, -8.651], max certified rank **0** |

The two gated sets are disjoint and well separated in S — roughly 24 units apart on distributions
whose within-arm standard deviation is about 4.0-4.6 — so the correction did select a distinctly
different population, which is the operative fact CHG-1 rested on. Both gates returned the same
maximum certified rank, 0. **The v1 rows are reported, not superseded.**

Lowest-S gated candidates (twist): D = -9822 (S = -15.817), -8430, -9069, -6598, -302.
Lowest-S gated candidates (null): v = -2765 (S = -15.675), -4530, -2332, -2703, -5823.

### 5.5 The number-field trap, stated correctly

`rank E(Q) + rank E^(D)(Q) = rank E(Q(sqrt D))`, so **adding** no. 302's rank >= 31 to a
positive-rank twist would give a rank >= 32 over the **quadratic field** Q(sqrt D) — the shape a
previous campaign's result was rejected for, and **no artifact of this run performs that addition**.
What the trap does *not* forbid: a quadratic twist E^(D) whose **own** Mordell-Weil rank **over Q**
is at least 32 is a legitimate rank->=32 curve over Q and **would meet GOAL-ECQ-2298dc C1 in full**,
subject to the six-clause claim bar. That E^(D) was found as a twist of no. 302 is a fact about how
it was found, not a defect in what it is, and rank is not twist-invariant, so nothing is inherited
or added. **Part C is not structurally disqualified; only its v1 gate was broken.** Every gated row
carries `field_of_the_reported_rank: Q`. No rank >= 1 was certified anywhere in part C, so no such
row arises here.

### 5.6 Between-arm comparison — one confirmatory test, the rest descriptive only

**Confirmatory (the disjoint v2-only subset, and nothing else).** Population: twist candidates with
200 < |D| <= 10000 (n = 11 922) against null candidates with 100 < |v| <= 6000 (n = 11 800). No
score in this population existed anywhere when the threshold was frozen, which is the only reason a
threshold may honestly be pre-registered against it.

- Two-sided Mann-Whitney U, normal approximation: **z = -2.4868**
- Common-language effect size P(random twist scores above random null) = **0.4907**
- Means: twist -0.0265, null -0.0013
- **Frozen threshold:** NOTABLE only if **both** |z| >= 3.0 **and** the effect size falls outside
  [0.45, 0.55]. Observed: |z| = 2.49 (**fails**) and effect size 0.4907 inside [0.45, 0.55]
  (**fails**). → **NOT NOTABLE.** Both conditions were required and neither is met.
- Confounds recorded before the run: the arms are structurally different families under one shared
  bad-prime convention, and the twist arm's coefficients grow like D^3 across a range reaching
  10 000 while the null arm's do not grow at all. A between-arm difference is confounded with
  coefficient growth and bad-prime handling; no statistic here removes either.

**Descriptive only, carrying no pre-registered threshold and citable as no finding:**

| population | n (twist / null) | z | effect size | status |
|---|---|---|---|---|
| v1 subset (\|D\| <= 200, \|v\| <= 100) — the 443 already-seen scores | 243 / 200 | +3.2447 | 0.5895 | descriptive only |
| pooled (all scored candidates, v1 + v2) | 12 165 / 12 000 | -1.9725 | 0.4927 | descriptive only |
| v1's recorded figures, carried forward unchanged | 243 / 200 | +3.24 | 0.5895 | descriptive only |

The v1-subset statistics reproduce v1's recorded values exactly. **Those 443 scores were seen before
the v2 rule was written and no reasoning un-sees them**, which is why the pre-registered inference is
confined to the disjoint subset.

**Unexpected observation, recorded and not discarded:** the descriptive v1 subset and the
confirmatory v2-only subset carry **opposite signs** (+3.24 versus -2.49; effect size 0.590 versus
0.491). Both are reported as measured. The Executor draws no conclusion from the reversal; note only
that the v1 subset is the previously-seen one, that the pre-registered test on the disjoint subset is
not notable, and that the score certifies nothing in either direction.

### 5.7 Minimality (CHG-7)

Every one of the 400 gated rows carries a non-null `minimality_status` and a partial screen: trial
division of the exact discriminant by every prime p <= 100 000, with the Kraus-Laska condition
(p^12 | disc, p^4 | c4, p^6 | c6) tested at each p that survives. Exact integer arithmetic
throughout; no floating point. Screen coverage **400 / 400**, 2.3 s of a 300 s cap.

- **All 400 rows: `not_established_with_reason`.** In every case the *only* prime implicated is
  **p = 2**, and no prime p >= 5 admits a descent on any row. p = 2 is expected: both arms are scored
  and gated on the standard integral model [0, b2, 0, 8*b4, 16*b6], whose construction multiplies
  coefficients by powers of 2. For p in {2, 3} the Kraus-Laska condition is necessary but not
  sufficient, so such a prime is reported as *admitting a possible descent* — the conservative
  direction, which withholds minimality rather than asserting it.
- **A partial screen does not discharge claim-bar clause (1), and this report does not say that it
  does.** Global minimality is not established for any part-C model; Laska-Kraus-Connell needs the
  factorisation of discriminants of roughly 450-900 decimal digits.
- **This does not touch the measurement.** A certified rank lower bound from exhibited points is
  invariant under Q-isomorphism and needs no minimal model. Minimality binds the claim bar, not the
  arithmetic. Every part-C naive height reported here is a height **of the stated model** and is
  labelled so. Established minimality would bind on any row certifying rank >= 1 — there are none —
  and a row certifying rank >= 32 would flag clause (1) **OUTSTANDING** and route out to a dedicated
  task rather than being attempted inline.

---

## 6. Controls — all nine ran

| control | outcome | note |
|---|---|---|
| CTL-CITED-INPUT-AGREEMENT (blocking) | **PASS** | on-curve failures empty; 468.2771 and 453.0469 reproduced to 4 dp |
| CTL-POSITIVE-INDEPENDENCE (mandatory) | **PASS** | 389a1 -> 2, 5077a1 -> 3, in this run set |
| CTL-NEGATIVE-INDEPENDENCE-PROVES-TOO-MUCH (mandatory) | **PASS** | {P,2P}/37a1 -> 1; {P,Q,P+Q}/389a1 -> 2; dependent 5077a1 triple -> 2 |
| CTL-SATURATION-DISTINCTION (mandatory) | **PASS** | discovered P against {2P} classified index-reducing |
| CTL-MATCHED-NULL | **PASS** | both arms scored to completion with one instrument, gated to equal depth 200 |
| CTL-PROVENANCE | **PASS** | all 400 gated curves checked by curve_key **and** a-invariants; none is a snapshot curve |
| CTL-GATE-DIRECTION (blocking, new) | **PASS** | strictly decreasing in certified rank; selection order 302, 5077a1, 389a1, 37a1 |
| CTL-SCORE-REUSE-AGREEMENT (blocking, new) | **PASS** | all **443** v1 candidates re-scored; **maximum absolute disagreement 0.0** |
| CTL-MINIMALITY-DISCLOSURE (new) | **PASS** | 400/400 gated rows carry non-null `minimality_status`; heights labelled |

The three mandatory controls passed **in this run set**, as claim-bar clause (5) requires; a v1
control does not discharge them for v2. Score reuse: the 443 v1 values remain the **values of
record** (`score_source: v1_reused`) and the re-score is a control, not a replacement — it turned an
assumption about implementation identity into a checked fact at a cost of about 2.4 s.

**Standing warning honoured (v1 DEV-A-01):** the 5077a1 triple {(-1,3), (0,2), (2,0)} is *dependent*
(their sum is O); the correct rank-3 generators {(-2,3), (-1,3), (0,2)} were used from the start,
and the dependent triple is retained as a proves-too-much control row.

**CTL-PROVENANCE, honest scope:** Cremona's tables cover conductors far below this scale, so a
Cremona lookup is vacuous here and is recorded as not-applicable-with-reason rather than as a pass.
The frozen snapshot predates no. 302 (posted 2026-08-23) and does not contain it — a fact about the
timeline, not a defect and not a licence to re-baseline.

---

## 7. Certificates

- **Part A** emits an `independence_certificate` (protocol level) for rank >= 31 of no. 302, and it
  was **re-verified in `RUN-ECQ-f5af06-v2-FINAL-reverify` by code that does not import the solver**:
  `verify_certificate.py` re-derives the group law, the point counts, the torsion bound, the mod-l
  coordinatisation and the F_l-rank from scratch. Result: on-curve all, no torsion points,
  recomputed torsion bound 1, recomputed F_2-rank **31** over 45 re-checked primes,
  `verified: true`, no failures.
- **Parts B and C** are pure measurement runs with nothing to certify: `certificate_kind: none`,
  stated explicitly rather than left blank.
- **Manifest schema reconciliation** (contract clause, unchanged): `independence_certificate` is a
  protocol-level artifact kind and is not a legal value of `run.result.certificate.kind`, which
  admits only `discrete_log | decomposition | none`. Every manifest therefore sets that field to
  `none` and references the protocol certificate by path. This is a schema reconciliation, not a
  weakening.

---

## 8. Budget: measured consumption against the v2 caps and the overlay's sizing projections

| part | cap (v2) | overlay projection | **measured** | measured / cap |
|---|---|---|---|---|
| A | 200 s | 10 s | **4.2 s** | 2.1 % |
| B | 700 s | 192 s | **140.2 s** | 20.0 % |
| C triage | 600 s | 131 s | **128.9 s** | 21.5 % |
| C exact gate | 1500 s | 934 s | **563.1 s** | 37.5 % |
| C minimality screen | 300 s | 15 s | **2.3 s** | 0.8 % |
| re-verification | (artifact reserve) | — | **1.9 s** | — |
| **task total** | 3600 s | 1282 s | **841.1 s** | **23.4 %** |

**Measured throughput** (measured, not modelled):

- point test, part B box: **1.46e-06 s/test** (95 899 629 tests in 140.0 s)
- point test, part C reduced box on gated curves: **1.21e-06 s/test** (466.8 M tests in 563.1 s)
- triage score at p <= 500: **5.335e-03 s/candidate** (24 165 scores in 128.9 s)

The overlay's sizing constant of 2.0e-06 s/test proved conservative by about 1.4-1.7x, and its
triage constant of 5.4 ms was accurate to 1 %. Every frozen region exhausted; no cap bound anywhere;
no coverage shortfall arose in any region. Peak memory stayed far below the 3 GB cap. Nothing was
widened to consume the remaining budget. Artifacts: 3.6 MiB of deliverables and 3.4 MiB of run
records, inside the 25 MiB total / 5 MiB per-file budget, with the 24 165-row per-candidate dump
reduced at source rather than retained out of band.

---

## 9. Where floating point appears, and why it decides nothing

1. **Reported logarithms** log max(|c4|^3, c6^2) and log|disc| of exact integers — reporting
   quantities; the underlying c4, c6 and disc are exact integers and are recorded as such. The
   contract permits floats here explicitly, including for the 4-dp comparison in
   CTL-CITED-INPUT-AGREEMENT.
2. **The Mestre-Nagao triage score S** — it *orders* candidates for the exact gate and certifies
   nothing. Every rank reported is decided by the exact gate.
3. **The Mann-Whitney z and effect size** — statistics about scores, not about ranks.

Every certification, squareness test, independence decision, minimality screen and classification is
exact integer or `Fraction` arithmetic. Squareness is decided by `math.isqrt` plus an integer
equality, never by a floating-point square root.

---

## 10. Deviations from the approved protocol

No deviation from any frozen quantity, range, rule or cap. Three implementation decisions are
recorded so a reviewer can check them:

1. **DEV-C-GATE-SLICE (recorded, not a protocol change).** The exact gate processes the two arms
   **interleaved** with an equal adaptive per-curve time slice, so that a cap — had one bound —
   would truncate both arms symmetrically rather than exhausting one arm first. No cap bound: all
   400 curves exhausted the full reduced box, so the mechanism never engaged.
2. **Denominator counting by Moebius inversion.** `box_denominator` counts admissible (u, w) pairs
   with an exact inclusion-exclusion instead of v1's O(U) gcd loop, which would take minutes at v2
   box sizes while the denominator must be on disk *before* anything is tested. The integer is
   identical; agreement with the v1 loop was unit-checked over w <= 40, U <= 1000.
3. **Per-candidate dump reduced at source.** The 24 165 candidate rows are written as compact
   one-line arrays with a declared column schema (`all_candidates_schema`), keeping every attempted
   candidate inside the deliverable at 3.4 MiB rather than about 14 MiB. Nothing is retained out of
   band.

**Carried forward from v1, not a v2 deviation:** DEV-A-01, the mis-transcribed 5077a1 generators.
v2 used the correct generators from the start.

**Gaps recorded rather than papered over:** part A's cited membership verification and the
Coordinator's independent re-derivation of the score direction have no committed run records; both
are cited with that limitation. `CTL-GATE-DIRECTION` re-establishes the direction inside this run
set with a stated pass condition, so nothing here rests on the latter citation alone.

---

## 11. Provenance caveat (repeated wherever the board's data is relied on)

The a-invariants, the 31 witness points, the rank-31 claim, the naive height, the submitter and the
date for ICARM no. 302 were retrieved on 2026-08-24 from
`https://elliptic-rank.icarm.cloud/curve/302` **through a summarising fetch tool, not by direct
page-source inspection**, and the board comment string "BSD + GRH certified to rank 31" is
**unverified at source**. The a-invariants and points are not trusted as published: they are
re-derived here by the certifier's exact on-curve check and exact recomputation of c4, c6 and disc,
which reproduced both cited logarithms to 4 dp. Every figure above that depends on that fetch
carries this caveat. Input pinned by sha256
`29bb6d29b88c09b0ad822549fad5092359bc19c9da8df92356ea21cf0dee149e`.

---

## 12. Branch labels, defended against their pre-declared conditions

| part | branch | pre-declared condition | met? |
|---|---|---|---|
| A | **A-FULL** | k = 31 | yes — 31 of 31; a confirmation of an external result, establishing nothing about 32 |
| B | **B-NULL** | no rank-increasing hit in the frozen box, reported as n_B / N_B | yes — 0 hits at 95 899 629 / 95 899 629 |
| C | **C2-NULL** | no gated curve in either arm certifies rank above 0 under the corrected bottom-200 gate | yes — max certified rank 0 in both arms at 100 % coverage |

The pre-registered v2 prior was: no rank-increasing hit in part B; maximum certified rank lower bound
0 in both arms of part C even under the corrected gate; k = 31 in part A; and the informative readout
being the coverage fractions, the two score distributions at roughly 50x v1's sample size, and the
pre-registered between-arm comparison on the disjoint subset — **not a rank**. Every part matched
that prior. The experiment succeeds as an experiment in every branch provided k, the coverage
fractions with their pre-recorded denominators, the branch labels, the nine control outcomes and the
v1-beside-v2 comparison are all reported; all of those are above. **No branch is reported that was
not earned**, and no rank >= 32 over Q — or over any field — is claimed, implied or approached
anywhere in this run set.
