# TASK-20260824-261bb4 — execution report

**Experiment** EXP-ECQ-f5af06 (frozen contract, `status: approved`, `approved_by: coordinator`)
**Goal** GOAL-ECQ-2298dc · **Question** RQ-ECQ-e9b361 · **Hypothesis** deliberately null
**Contract commit** `4b1f96db975c5b8c5ea5c08b876c2acf4fdd9f7e`, clean tree at run start
**Producer wall clock** 23.8 s of the 3600 s task budget · **Runs** 7 of a maximum 40
**Peak memory** tens of MB against a 3 GB cap; the cap never bound

This report records **observations only**. It declares no hypothesis supported or
rejected, and it draws no research conclusion. The Coordinator verifies run validity
before interpreting anything.

---

## 0. Branch labels, up front

| Part | Branch | Pre-declared condition | Met? |
|---|---|---|---|
| A | **A-FULL** | `k = 31` | Yes — 31 of 31 |
| B | **B-NULL** | no rank-increasing hit in the frozen box, reported as `n_B / N_B` | Yes — 0 hits at 2347563 / 2347563 |
| C | **C-NULL** | no gated curve in either arm certifies rank above 0 or 1, no separation between arms | Yes — max certified rank 0 in both arms |

All six controls **PASS**. One of them failed on first execution because of an
executor input error; both runs are recorded and neither was deleted (§6).

**Nothing here is a new rank result of this program's own.** Rank >= 31 over **Q** is
the **live world record and it is claimed** — ICARM curve no. 302, posted 2026-08-23.
It is not unclaimed. Part A is a **confirmation of someone else's result** and an
external positive control. Part B found nothing. Part C's certified ranks are 0.

---

## 1. Provenance caveat, carried not dropped

The a-invariants, the 31 witness points, the rank-31 claim, the naive height, the
submitter and the date for ICARM no. 302 were retrieved on 2026-08-24 from
`https://elliptic-rank.icarm.cloud/curve/302` **through a summarising fetch tool, not
by direct page-source inspection**. The board comment string *"BSD + GRH certified to
rank 31, found by Claude, Levent Alpoge, and Ava Howell"* is **unverified at source**.
Every figure below that depends on that fetch carries this caveat.

The a-invariants and the points were **not trusted as published**: they were re-derived
through the certifier's exact on-curve check and exact recomputation of c4, c6 and the
discriminant. See CTL-CITED-INPUT-AGREEMENT.

**No network call was made by any run. Nothing was submitted to the ICARM endpoint.**

---

## 2. Part A — independent certification of rank >= 31

**Branch A-FULL. k = 31 of 31.**

| quantity | value |
|---|---|
| certified rank lower bound `k` | **31 of 31** |
| point indices certified independent | all of `0..30` |
| torsion bound | 1 |
| torsion-bound primes | 17, 47, 53, 59, 61, 67, 71, 79 |
| prime `l` used | 2 |
| good primes used | 45 primes, 17 through 521 |
| stacked matrix F_2-rank | 31 |
| wall clock | 1.905 s (cap 1500 s) |
| search bounds used | `max_prime=1500`, `max_good_primes=250`, `torsion_primes=8`, `l in (2,3,5,7,11,13)` |

**Search bounds were raised, and here is the record of it.** At the certifier's
defaults (`max_prime=1500`, `max_good_primes=60`) the result was **k = 27 of 31** in
1.9 s. The binding bound was `max_good_primes`, not `max_prime`: E(F_p)[2] contributes
at most 2 columns per prime, so >= 16 usable primes are needed for F_2-rank 31, and the
witness-point denominators exclude the primes 2, 3, 5, 7, 11, 29, 31, 43, 103, 229 and
60257 from the pool. Raising `max_good_primes` to 250 reaches k = 31 at the same
`max_prime` and the same cost. **These are search bounds, not claims: raising them
changes nothing about what is proved.**

*(Contract detail, reported not corrected: the contract's illustrative list of excluded
primes names 23, but 23 does not divide any witness-point denominator and 23 is not
excluded. The primes actually excluded are listed above. This changes no frozen
quantity and no result.)*

**CTL-CITED-INPUT-AGREEMENT — PASS, exactly.**

| | recomputed | cited | agrees to 4 dp |
|---|---|---|---|
| `on_curve_failures` | `[]` (empty) | — | yes |
| `log max(|c4|^3, c6^2)` | **468.2771** | 468.2771 | yes |
| `log|disc|` | **453.0469** | 453.0469 | yes |

c4 is an exact 68-digit integer, c6 an exact 103-digit integer, disc an exact 197-digit
integer; all three are recorded exactly in `certification.json`. The cited membership
verification was **cited as an input, not recommissioned**; it carries no committed run
record and is cited with that limitation. The certifier's step-(0) on-curve check
recomputed the figures as an unavoidable side effect, so they were **compared, not
assumed** — and they agree. This is the blocking control and it did not block.

**Independent re-verification.** `scripts/verify_certificate.py` re-checks the
certificate **without importing the solver**: its group law, point count, mod-`l`
coordinatisation and F_l rank are all written again from scratch. It re-derived
F_2-rank **31** over the 45 stated primes, recomputed the torsion bound as 1, confirmed
all 31 points on-curve and none torsion. `all_verified: true`. Third-party re-runnable
from the committed artifacts with `python3 scripts/verify_certificate.py`.

**What A-FULL means and does not mean.** It establishes that this program can certify
independence at record scale, and it **independently confirms an external party's rank
lower bound of 31 for no. 302** rather than taking the leaderboard's word for it. It
establishes **nothing whatever about rank 32** and is not progress toward it.

---

## 3. Part B — search for a 32nd independent point

**Branch B-NULL. Coverage 2 347 563 / 2 347 563 = 100 % of the frozen box. 0 hits.**

`N_B = 2347563` was **computed and written to disk before the first candidate was
tested**, from the frozen box description alone. The box was **exhausted**, so the
numerator equals the denominator; no truncation occurred.

- Frozen box, verbatim: `x = u / w^2` in lowest terms, `w in [1,30]`, `gcd(u,w)=1`,
  `|u| <= 1000000` for `w=1` and `|u| <= 10000` for `2 <= w <= 30`.
- Test: exact. `D(x) = (a1 x + a3)^2 + 4(x^3 + a2 x^2 + a4 x + a6)` is a rational square
  iff the integer `T = w^2 (a1 u + a3 w^2)^2 + 4(u^3 + a2 u^2 w^2 + a4 u w^4 + a6 w^6)`
  is a perfect square, since `w^6 = (w^3)^2`. Decided by `math.isqrt` and an integer
  equality. **Never a floating-point square root.**
- Kernel positive control: the same square test recovers **all 31** known witness
  x-coordinates, 31/31.
- Wall clock **3.418 s** against a 700 s cap.

**CTL-SATURATION-DISTINCTION — PASS.** On rank-1 curve 37a1 with generator P, the
"known subgroup" presented as `{2P}` and P presented as the discovery, the classifier
returned **index-reducing-or-dependent** with certified rank lower bound 1, not
rank-increasing. This is the control that stands between an index-reducing point and a
false record claim, and it was exercised before the search ran.

**The only sentence this null licenses**, stated as the contract requires:

> No point of E(Q) was found within the frozen box, at coverage 2 347 563 / 2 347 563.

It is **consistent with the board's rank-exactly-31 claim and equally consistent with
the box being far too small, and it distinguishes neither.** It supports no statement
of the form "the rank is 31", "the rank is not above 31", or "no further points exist".
The 31 known points have x-numerators of about 33 decimal digits; this box reaches 7.

**Reportable budget observation, not a licence.** The frozen box cost 3.4 s of a 700 s
cap — about 0.5 % of the part-B budget. The budget could have supported a box some two
orders of magnitude larger. **The box was not widened**: it is frozen, and widening it
after seeing a null would make the denominator a function of the outcome. This is
recorded for the Coordinator's sizing of any successor contract.

---

## 4. Part C — twists and near neighbours

**Branch C-NULL.** Denominators computed and written **before any candidate was
scored**: `N_C_TWIST = 243`, `N_C_NULL = 200` (0 discarded for zero discriminant),
reduced-box denominator `N = 220901`.

| | twist arm | null arm |
|---|---|---|
| generated | 243 | 200 |
| discarded | 0 | 0 |
| **scored** | **243 / 243 (100 %)** | **200 / 200 (100 %)** |
| **gated** | **20 / 20** | **20 / 20** |
| reduced-box coverage per gated curve | 220901 / 220901 (exhausted) | 220901 / 220901 (exhausted) |
| points found, all gated curves | **0** | **0** |
| **max certified rank lower bound over Q** | **0** | **0** |

Triage ran **in lockstep**, alternating arms, so a truncation would still have left a
matched comparison. Neither cap was reached: triage 2.4 s of 600 s, gate 11 s of 500 s.
**CTL-MATCHED-NULL — PASS**: same implementation, same prime bound 500, same top-20
rule, same reduced box, both arms scored to completion and gated to the same depth. No
differential attrition. Every one of the 443 generated candidates is persisted in
`twist_search.json` with an identifier, a status and a reason; attempted equals
reported exactly.

### 4.1 Rank is not twist-invariant

The 31 points of no. 302 **do not transfer** to E^(D). E^(D) has its own Mordell-Weil
rank, about which the rank of no. 302 says nothing. No row treats a twist as inheriting
rank.

### 4.2 The number-field trap

`rank E(Q) + rank E^(D)(Q) = rank E(Q(sqrt D))`. Since rank E(Q) >= 31, **any** twist of
positive rank would immediately give rank >= 32 **over the quadratic field Q(sqrt D)**.
**That is not this goal's objective.** GOAL-ECQ-2298dc C1 is rank >= 32 **over Q**, and a
previous campaign's rank->=-31 result over multiquadratic fields was rejected for exactly
this reason. Every rank reported in part C is a rank **over Q** of the named curve, and
every gated row carries `field_of_the_reported_rank: Q` explicitly. **In this run the
question is moot: every certified rank in both arms is 0, so no quadratic-field
consequence arises at all.**

### 4.3 The frozen triage gate is sign-inverted — read this before reading §4 as a negative

Calibrated against published curves of known rank, with the same implementation and the
same prime bound used for both arms:

| curve | published rank | S |
|---|---|---|
| 11a1 | 0 | **+1.57** |
| 37a1 | 1 | -4.06 |
| 389a1 | 2 | -11.04 |
| 5077a1 | 3 | -18.10 |
| ICARM no. 302 | >= 31 (certified, §2) | **-38.83** |

**S decreases monotonically with rank.** `a_p = p + 1 - #E(F_p)` is small or negative
exactly when `#E(F_p)` is large, which is the Mestre-Nagao signature of *high* rank. The
contract's frozen gate selects the **top 20 by S — the largest S — which selects the
lowest-rank candidates in each arm**, the opposite of the triage's stated purpose. This
is Nagao's statistic with the sign the wrong way round relative to the sentence written
around it.

**Nothing was changed.** The gate was applied exactly as frozen. Changing a frozen
selection rule after any score is known makes numerator and denominator both functions
of the outcome — the defect class this program has already paid for twice — and the
contract requires a versioned `protocol_amendment` for any such change. The **full
score of every scored candidate in both arms** is recorded in `twist_search.json`, so a
re-gate under an amendment needs **no new scoring run**. A clearly-labelled
`score_extremes_VIEW_NOT_A_GATE` block lists both ends of each arm's distribution; **no
exact gate was applied to the bottom 20.**

**Therefore, stated plainly: the pre-registered part-C prior of rank 0-1 in both arms
was met, but it was met for the wrong reason.** The gate looked at the 20 candidates
that the score's own logic ranks as *least* promising in each arm. **§4's C-NULL is not
evidence that the twist neighbourhood of no. 302 is barren.** A reader who takes "prior
met" without this paragraph would draw exactly the false conclusion.

**Bad-prime convention, stated so the two independent derivations reconcile.** This run
includes **every** prime p <= 500, good or bad; `#E(F_p)` is the naive affine point count
of the *stated model* over F_p plus the point at infinity, which at a bad prime is the
count on the singular model — a uniform convention, applied identically to every
candidate in both arms, not the arithmetic `a_p` of the curve. The Coordinator's
independent re-derivation **skips p | disc**, which is why the absolute scales differ
slightly (11a1: +1.57 here vs +0.66 there; no. 302: -38.83 here vs -38.78 there). **The
two are reconcilable by exactly that choice**, and the ordering and direction are
identical under both conventions.

### 4.4 Score distributions and the between-arm comparison

Requested for the amendment record. Both arms scored to completion, so this comparison
is at full coverage.

| statistic | twist (n=243) | null (n=200) |
|---|---|---|
| min | -8.0504 | -10.0243 |
| q1 | -1.4165 | -2.2114 |
| median | 1.7209 | 0.2001 |
| q3 | 4.4767 | 2.6981 |
| max | 12.0089 | 13.0485 |
| mean | 1.4789 | 0.2979 |
| sd | 4.0348 | 4.0090 |
| range | 20.0593 | 23.0728 |

Deciles for both arms are in `twist_search.json`. **The neighbourhood is not scored
flat**: each arm spans about 20-23 units of S with a standard deviation near 4.0, so a
bottom-20 gate would select a distinctly different and well-separated set of candidates
rather than an arbitrary one.

**Do the arms differ?** Descriptively, yes, slightly:

- mean difference (twist - null) **+1.181**; median difference **+1.521**
- Mann-Whitney U = 28651 against 24300 expected under no difference; normal-approximation
  **z = +3.24**
- P(a random twist scores above a random null) = **0.5895**
- ranges overlap almost entirely: twist [-8.05, 12.01], null [-10.02, 13.05]

These are **descriptive statistics**. No significance threshold was pre-registered and
none is asserted. The Executor records them and draws no conclusion.

One directional observation, offered as an observation only: since S *decreases* with
rank, the twist arm scoring **higher** than the null arm is, in the score's own logic,
the twist arm looking **lower**-rank than its matched null — the opposite direction from
enrichment. The effect is small relative to the within-arm spread. Whether it is real,
an artifact of the shared bad-prime convention across two structurally different model
families, or noise, is not something these runs can settle.

### 4.5 Minimality limitation, recorded in advance

**Global minimality of the twist and null models is not established.** Laska-Kraus-Connell
minimalisation requires factoring discriminants of roughly 450-900 decimal digits, which
is not feasible at any budget. This does **not** invalidate the measurements: a rank
lower bound from exhibited points is invariant under Q-isomorphism and needs no minimal
model. The reported naive heights are heights **of the stated model** and are labelled
as such. It **would** bind at claim-bar clause (1), which requires minimality to be
*established* rather than assumed before the words "rank 32" may appear — recorded here
in advance so it cannot be skipped later. No such claim arises: every certified rank in
part C is 0.

**Model normalisation (executor decision, not a frozen term).** Both arms are scored and
gated on the standard integral model `[0, b2, 0, 8 b4, 16 b6]`. The twist arm is
`[0, b2 D, 0, 8 b4 D^2, 16 b6 D^3]`; the null arm is the *same* transformation applied to
`[1,1,1,a4,a6+v]`. Applying identical normalisation to both arms is what CTL-MATCHED-NULL
requires; `a_p` at a good prime is a Q-isomorphism invariant, so it changes no score at a
good prime.

---

## 5. Controls — all six

| control | outcome | evidence |
|---|---|---|
| CTL-CITED-INPUT-AGREEMENT | **PASS** | `on_curve_failures` empty; 468.2771 and 453.0469 both reproduced to 4 dp |
| CTL-POSITIVE-INDEPENDENCE | **PASS** | 389a1 rank 2 -> certified 2; 5077a1 rank 3 -> certified 3 |
| CTL-NEGATIVE-INDEPENDENCE-PROVES-TOO-MUCH | **PASS** | `{P,2P}` on 37a1 -> 1 (not 2); `{P,Q,P+Q}` on 389a1 -> 2 (not 3); dependent triple on 5077a1 -> 2 (not 3) |
| CTL-SATURATION-DISTINCTION | **PASS** | `{2P}` + discovered P on 37a1 -> index-reducing, k=1, not rank-increasing |
| CTL-MATCHED-NULL | **PASS** | both arms 100 % scored, both gated 20/20, same instrument, no differential attrition |
| CTL-PROVENANCE | **reported** | see below |

**CTL-PROVENANCE.** Every reported curve was checked against the frozen snapshot
`coordination/goals/GOAL-ECQ-002/baseline/icarm_database_20260823.json`
(sha256 `118db069...cadc59`, verified) by **curve_key and by a-invariants**. No. 302 is
**not** in the snapshot, and the 40 gated part-C curves are not either. **The snapshot
predates curve no. 302, which was posted 2026-08-23; its highest curve id is 289. That
is a fact about the timeline, not a defect, and not a licence to re-baseline.** A
Cremona check is recorded as **not-applicable-with-reason**, not as a pass: Cremona's
tables cover conductors far below the ~10^450 discriminant scale here, so a lookup
would be vacuous.

**Where floating point appears, and why it decides nothing.** Exactly two places: (i)
the reported logarithms `log max(|c4|^3, c6^2)` and `log|disc|` of exact integers, used
for reporting and for the 4-dp comparison in CTL-CITED-INPUT-AGREEMENT; (ii) the part-C
Mestre-Nagao triage score S, which only selects which candidates receive the exact gate.
**No certification, independence decision, squareness test, minimality decision or
classification anywhere in this task touched floating point.** Torsion bounds, point
counts, mod-`l` linear algebra, the group law and the square test are exact integer or
`Fraction` arithmetic. **cypari/PARI was not used anywhere**, including the triage where
the contract would have permitted it.

---

## 6. Deviations, failures and unexpected observations — recorded, not discarded

**DEV-A-01 — mis-transcribed control generators (executor error).** The first execution
of part A, `RUN-ECQ-f5af06-A-certify`, supplied `{(-1,3), (0,2), (2,0)}` as the rank-3
generator set of Cremona 5077a1. **That triple is dependent**: exact computation gives
`(-1,3) + (0,2) + (2,0) = O`. The certifier returned 2 and CTL-POSITIVE-INDEPENDENCE was
scored **FAIL**.

This was **a defect in the control's input, not in the instrument**. Returning 2 was the
*correct* answer for a dependent triple. The correct generators `{(-2,3), (-1,3), (0,2)}`
certify rank 3 in 4 primes.

Handling: the defective run **remains on disk, unedited**, at
`experiments/EXP-ECQ-f5af06/runs/RUN-ECQ-f5af06-A-certify/` with its FAIL recorded.
`RUN-ECQ-f5af06-A-certify-r2` supersedes it with the corrected control input; part A's
own measurement was **identical in both runs (k = 31)**, since the mis-transcription
touched only the control curve. The dependent triple was then **carried forward as an
additional row of CTL-NEGATIVE-INDEPENDENCE-PROVES-TOO-MUCH**, where it is exactly the
control it accidentally performed — and it passes there.

*Note for the Coordinator:* `RUN-ECQ-f5af06-A-certify/manifest.yaml` carries
`status: completed_valid`. That is accurate as far as it goes — the run completed and
faithfully recorded `ctl_positive_independence: FAIL` — but it must be read together
with this section. It is superseded by `-r2` and should not be read as evidence the
certifier is broken.

**DEV-A-02 — runner flag mismatch.** `RUN-ECQ-f5af06-A-reverify` exited rc=2 because
`verify_certificate.py` did not yet accept the runner's `--raw-out` flag. Recorded as
`infrastructure_error`, superseded by `RUN-ECQ-f5af06-A-reverify-r2`. Both runs are on
disk. No measurement was affected.

**Unexpected observations.**
1. The part-C frozen gate is sign-inverted (§4.3). This is the most consequential
   finding of the task and it is about the contract, not the mathematics.
2. Part B's frozen box consumed 0.5 % of its cap (§3); part A 0.13 % of its; part C
   1.2 % of its. Total producer wall clock 23.8 s against 3600 s. Every frozen search
   region in this contract was sized far below what the budget permitted.
3. The contract's illustrative excluded-prime list names 23, which is not excluded (§2).

**No protocol amendment was made and none was self-authorised.** No frozen quantity —
box B, reduced box B-C, `|D| <= 200`, `|v| <= 100`, prime bound 500, the top-20 rule —
was changed at any point.

---

## 7. What was not reached, and why

- **The bottom-20 gate in either part-C arm.** Not reached **by decision, not by budget**:
  the frozen gate specifies the top 20 "and no others", and re-gating requires a versioned
  `protocol_amendment` from the Coordinator. All scores needed for it are already
  recorded, so it needs no new scoring run.
- **Any search region beyond the frozen boxes.** Not reached by decision. Budget
  remained (§6, observation 2) but the boxes are frozen.
- **Global minimality of part-C models** (§4.5) — infeasible at any budget.
- **Live-board re-read.** Not attempted: it is a Coordinator step outside the runs, and
  no run may make a network call.
- **Nothing was reached and withheld.** Every part reports its result with its
  denominator, including the parts whose result is zero.

---

## 8. Claim discipline

No sentence in this report describes rank >= 31 over **Q** as unclaimed. No number-field
rank is presented as meeting or approaching GOAL-ECQ-2298dc C1. The strongest statement
drawn from these runs is a **certified rank lower bound of 31 for ICARM no. 302, an
externally produced and externally claimed curve**, re-verified by code independent of
the solver. Rank equality is never claimed; BSD and GRH are never invoked; the phrase
"world record" is not used of any result of this program's own. **The six-clause claim
bar was never engaged, because no rank >= 32 was found in any part.**

## 9. Artifacts

Deliverables — `coordination/goals/GOAL-ECQ-2298dc/tasks/TASK-20260824-261bb4/`:
`certification.json`, `extension_search.json`, `twist_search.json`, `report.md`,
`scripts/{common,runner,part_a,part_b,part_c,verify_certificate}.py`

Runs — `experiments/EXP-ECQ-f5af06/runs/`, each with `manifest.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`:
`RUN-ECQ-f5af06-A-certify` (superseded), `RUN-ECQ-f5af06-A-certify-r2`,
`RUN-ECQ-f5af06-A-reverify` (infrastructure_error, superseded),
`RUN-ECQ-f5af06-A-reverify-r2`, `RUN-ECQ-f5af06-B-extension`,
`RUN-ECQ-f5af06-C-twists`, `RUN-ECQ-f5af06-FINAL-reverify`.
