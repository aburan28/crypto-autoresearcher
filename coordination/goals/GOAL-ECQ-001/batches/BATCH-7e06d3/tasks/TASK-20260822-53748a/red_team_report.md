# Red team report — TASK-20260822-53748a

Goal `GOAL-ECQ-001`, batch `BATCH-7e06d3`, hypothesis `H-ECQ-cec3c4`, question
`RQ-ECQ-80f23c`. Reviewed at snapshot commit
`b71f466840fe6cface5a6b87c4e518841793399e`.

**Assigned joints: 3 and 4 only.** Joints 1 and 2, the `proves_too_much` control
set and the blind re-derivation belong to `TASK-20260822-0a0041`, running blind
to me. I did not read that task's directory or any report in it. Where my own
work touches material that also bears on joint 1 or 2, it is marked
*out-of-joint corroboration* and carries no verdict.

---

## 0. Routing determination — this round stays at `review-adversarial`

The highest rank claimed anywhere in the reviewed package is **12**
(`certified_curves.json:best_certified_rank`, one curve at `t = -65/22`). I
re-traced every one of the 137 certified ranks myself (§1.2) and the maximum
is 12. Nothing in the package claims rank ≥ 31 over Q, and
`gap_analysis.json:explicitly_not_progress_toward_31` disclaims it in terms. The
`routing_rules` escalation to `review-breakthrough` is **not** triggered. I
reviewed at the tier the envelope assigned.

## 0.1 Snapshot integrity (precondition, verified before reviewing)

I read committed state, not the working tree. The archive receipt
`archives/TASK-20260822-66bacf/receipt.yaml` carries `commit_sha: null` and binds
by content, so I verified the content binding directly. All six declared
producer paths hash to exactly the values in `path_sha256` at `b71f4668`:

| path | sha256 (verified) |
|---|---|
| `.../81141a/qt_family.json` | `464619426bf4a976…3f919b` |
| `.../81141a/certified_curves.json` | `a342ff9c7c93424e…3d15aee` |
| `.../81141a/gap_analysis.json` | `9c11dabeb42a82e7…fe6278ea` |
| `.../81141a/report.md` | `47c216819d725c61…c0e25e70f` |
| `.../a7a9e8/report.md` | `00cd7dd54b07e081…66d066be440` |
| `.../a7a9e8/highrank_pool.json` | `3d8620ea99343643…67f5e1a24` |

Content binding **holds**. I did not rely on commit reachability.

---

# JOINT 3 — the Mestre–Nagao statistic and the sieve-efficiency claim

> *Joint as stated: the Mestre–Nagao statistic was used ONLY to order candidates
> and never contributed to a certified rank; and the claimed sieve efficiency is
> actually supported.*

## VERDICT: **HOLDS.** Strengthened, not weakened, by independent attack.

I attacked this joint five ways. Four were the Coordinator's worked plan; the
fifth (§1.5) is a new measurement the plan did not ask for and the producer did
not run. All five came back for the producer.

### 1.1 Are the arms genuinely matched? — YES, verified by independent recomputation

I did not take the producer's word for the domain, the ordering, or the draw. I
rebuilt the tier-2 scoring from the published `c4(t)`, `c6(t)` polynomials in
`qt_family.json` using my own model construction, my own prime sieve, and my own
`Fraction` arithmetic, and re-derived both arms from scratch
(`rt` scratch script `rescore.py`; not imported from `src/pipeline.py`).

| check | result |
|---|---|
| tier-1 domain size `|p|≤2000, q≤40, gcd=1` | I enumerate **97 640**; reported 97 640 ✔ |
| tier-2 domain size `|p|≤150, q≤8, gcd=1` | I enumerate **1 548**; reported 1 548 ✔ |
| MN arm ⊂ tier-2 box | 60/60, all distinct ✔ |
| control arm ⊂ **the same** tier-2 box | 60/60, all distinct ✔ |
| my independently computed top-60 vs recorded MN arm | **identical, in order** ✔ |
| max abs. score difference on those 60 | **0.0** ✔ |
| `random.Random(81141).sample(...)` over my score-ordered 1548 | **reproduces the recorded control arm exactly, in order** ✔ |
| overlap MN ∩ control | I compute 2; reported 2 ✔ |
| alarm per arm | `pipeline.py:1130` — both tier-2 arms get `args.alarm`; RUN-004 `command.txt` passes `--alarm 8`. **Matched.** ✔ |
| point-search budget per arm | identical code path `certify_one`, no per-arm branch ✔ |

The control was drawn from **the same 1 548-element domain the MN arm was ranked
over**, by `rng.sample` on that list (`pipeline.py:1058-1059`), and I reproduced
the draw bit-for-bit from the recorded seed. It is a genuine uniform control, not
a differently-scoped or post-selected one. The suspicion the plan raised —
"check the random control was drawn from the SAME domain the MN arm ranked" — is
answered in the affirmative by recomputation rather than by reading the label.

*One nit, real but not fatal:* the producer **discarded the control arm's MN
scores** (`pipeline.py:1071` writes `[frac_str(t), None]`). That threw away the
single most informative covariate in the experiment and is why the producer could
not run the pooled dose-response test in §1.4 that most strongly supports their
own claim. I had to recompute all 1 548 scores to do it. Cost of the fix: one
character.

### 1.2 Does any rank rest on an MN score? — NO. Full re-trace, 137/137.

The plan calls this fatal if found. I looked for it exhaustively rather than by
sampling.

*Structural:* `certify_one` (`pipeline.py:1088`) receives only `(F, t0, alarm)`;
`certify_rank` (`:680`) receives only `(ainv, pts)`. The score is not in scope in
either. `mn_score` is called once, in `cmd_sieve`, and its output flows only into
list ordering. No score field appears in any of the 137 curve records.

*Empirical, by independent recomputation of every reported rank:* for all 137
curves in `certified_curves.json` I re-verified each exhibited point on its exact
curve with my own `Fraction` arithmetic (`y² == x³ + Ax + B`), rebuilt the
Néron–Tate height matrix, and re-ran a greedy independent subset:

- **points off curve: 0** (across all 137 curves, ~1 100 points);
- **rank mismatches, mine vs recorded: 0** (137/137);
- `len(independent_point_indices) == certified_rank` for all 137;
- every index in range; `certified_rank ≤ n_sections + n_descent_points` for all 137;
- histogram reproduces: `{8:93, 9:14, 10:17, 11:12, 12:1}`, best = 12.

*Cross-validation that the independence test neither over- nor under-counts:* in
all **54** fibres where descent completed, `certified_rank == r_low == r_high`
from PARI `ellrank` — a computation the certification does not use. Certified
rank never exceeds `r_high` anywhere. An over-counting independence bug would
show up here as `certified_rank > r_high`; it does not, on any curve.

All **83** timed-out fibres in `certified_curves.json` sit at exactly rank 8, the
section floor, as the design requires.

**Joint 3's fatal condition is definitively absent.**

*Out-of-joint corroboration (no verdict, joint 2 is not mine):* my
reimplementation of the specialisation map reproduced the producer's
`a_invariants` on **all 140** recorded fibres with zero mismatches, which is
independent evidence that the curves being certified are the curves the family
specialises to.

### 1.3 Do the 31 vs 35 timeouts manufacture the gap? — NO.

This is the plan's sharpest question and it deserved a real answer rather than
the producer's "31 vs 35, roughly balanced".

A timeout returns zero descent points (`extra_points` → `[], "timeout"`), so a
timed-out fibre is floored at exactly 8. The right test is therefore to condition
on descent having completed and see whether the gap survives:

| | MN arm | random control |
|---|---|---|
| attempted | 60 | 60 |
| timeouts | 31 (51.7 %) | 35 (58.3 %) |
| **completed descents** | **29** | **25** |
| rank ≥ 9, completed only | **28 / 29 = 96.6 %** | **16 / 25 = 64.0 %** (Fisher p = 2.6e-3) |
| rank ≥ 10, completed only | **24 / 29 = 82.8 %** | **6 / 25 = 24.0 %** (Fisher p = 1.6e-5) |
| rank ≥ 11, completed only | **12 / 29 = 41.4 %** | **0 / 25 = 0 %** (Fisher p = 1.5e-4) |

The gap is **larger** conditional on completion, not smaller, and the MN arm had
*fewer* timeouts, so the censoring cannot be inflating it. Differential timeout
does not manufacture the effect.

I then went after the censoring mechanism itself, since a rank-dependent censor
would still bias the comparison even at equal rates. Over all 120 descended
fibres (Spearman):

| pair | ρ |
|---|---|
| MN score vs is_timeout | **−0.104** |
| MN score vs log&#124;a6&#124; | **−0.084** |
| log&#124;a6&#124; vs is_timeout | **+0.765** |
| log&#124;a6&#124; vs rank (completed) | +0.105 |

Timeout is driven almost entirely by coefficient size and is essentially
**orthogonal to the MN score**. This also kills the obvious alternative
explanation — that the MN top is enriched in small-height `t` whose descents
simply succeed more often. Arm heights are close and point the *wrong* way for
that story anyway (median max(|p|,q): MN 51, control 57; mean denominator: MN
4.80, control 4.05).

### 1.4 Was anything fitted and then validated on the same data? — NO.

- The tier-2 sub-domain (`--pmax2 150 --qmax2 8`), the arm size (`--K 60`) and
  the control seed were **all fixed on the RUN-003 command line, in the same
  invocation that computed the tier-1 scores**, i.e. before any score existed.
  RUN-003 is the only sieve run in the package (7 runs total, all accounted for
  in `command.txt`), so there was no exploratory pass to select the box from.
  This is the garden-of-forking-paths attack and it fails.
- The 8-point configuration search (RUN-002, seed 81141, 4 000 tries) optimised
  **model coefficient height only** — verified in `search_configuration`
  (`pipeline.py:888`) and in `qt_family.json:configuration_search`
  (`model_size_distribution_head`). No rank, no MN score, no property of any
  specialisation enters the objective.
- A random-sample control of the same size was **required by the handoff before
  the run** (`ledger/handoffs/TASK-20260822-81141a.yaml`, constraints) and
  HEUR-1 in `H-ECQ-cec3c4` pre-registers that the hit rate itself is reported
  whatever it turns out to be.

### 1.5 The control the plan did not ask for, and that I ran: **decay**

*"Name the parameter that is supposed to destroy the signal and state what the
measurement should look like as it increases."* Here that parameter is the MN
score itself: if `S(1000)` orders by rank, yield must **decay** as you walk down
the ordering, and a quantity that stays flat is the artifact tell. The producer
sampled the top and the middle (a uniform control is a middle sample) and never
sampled the bottom. I did.

I wrote my own descent harness (`rt_arm.py`; own model construction, own
`reduce_short`, own exact on-curve test, own Gram greedy — it does not import
`src/pipeline.py`) and ran the **bottom 20 of the same 1 548-element tier-2
domain at the same 8 s alarm**:

| arm | n | timeouts | completed | rank ≥ 9 / completed | rank ≥ 11 / completed | max rank |
|---|---|---|---|---|---|---|
| MN top-60 (producer) | 60 | 31 (51.7 %) | 29 | 28/29 = **0.966** | 12/29 = **0.414** | 11 |
| random 60 (producer) | 60 | 35 (58.3 %) | 25 | 16/25 = **0.640** | 0/25 = 0 | 10 |
| **MN bottom-20 (this review)** | 20 | 11 (55.0 %) | 9 | **0/9 = 0.000** | 0/9 = 0 | **8** |

Fisher, random vs bottom at rank ≥ 9: **p = 9.3e-4**. Top vs bottom: **p = 6.1e-8**.

Two things follow, and both matter more than the producer's headline:

1. **The signal decays monotonically to the floor, and past it.** The bottom of
   the ordering is not merely no better than random — it is *worse*, and it is
   where the degenerate fibres live. My independent descents returned rank 4 at
   `t = 1` and rank 7 at `t = 2`, matching exactly the exceptional
   specialisations the producer reports in its own P1 table (`report.md`, rank 4
   at `t=1`, rank 7 at `t=2`). The statistic sorts the bad fibres to the bottom
   as well as the good ones to the top.
2. **The timeout rate is FLAT across the entire ordering** — 51.7 %, 58.3 %,
   55.0 % from top to bottom — while the yield falls 0.966 → 0.640 → 0.000. A
   confound that is constant across the ordering cannot produce a monotone
   response along it. This is the cleanest available disproof of the
   timeout-artifact hypothesis, and it is now measured rather than argued.

I also ran the dose-response *within* the producer's own 120 fibres, using the
control-arm scores I had to recompute. Mean MN score by certified rank, completed
descents only:

| certified rank | n | mean S(1000) | step |
|---|---|---|---|
| 8 | 10 | 990.18 | — |
| 9 | 14 | 995.44 | +5.26 |
| 10 | 18 | 999.36 | +3.91 |
| 11 | 12 | 1001.97 | +2.61 |

The BSD-flavoured heuristic behind the statistic predicts a shift of
`Σ_{p≤1000} log p / p = 5.6095` per unit of rank. The observed first step is
**+5.26** against a predicted **+5.61**; the steps compress at the top exactly as
selection on a noisy score requires. Spearman(score, rank) on completed fibres:
**+0.779**. The tier-2 score range spans 27.74 ≈ **4.95 rank-units**, which is
the dynamic range needed to separate rank 8 from rank 12.

This is a quantity behaving the way the mechanism says it should, over the
parameter that is supposed to destroy it. It is not an artifact.

## 1.6 The MN-vs-prior reversal — explicit statement, as required

**The Coordinator's recorded prior said to disbelieve a large MN yield. I attacked
the measurement on the prior's behalf and the measurement wins. The prior is
overturned, and the correct reading is that the prior was over-generalised from
one object to all objects, not that the earlier measurement was wrong.**

The prior rests on `EV-ECRANK-b6c9b6` (GOAL-ECRANK-001): an MN prefilter over
**364 756 squarefree twists of five small-conductor curves**, `|d| ≤ 300 000`,
primes to 1 500, `ellrank` on the top 400 per curve, producing no twist of rank
≥ 5. I take those numbers as recorded; I did not re-run that experiment.

The two measurements are not about the same object, and the difference is
structural, not statistical:

| | GOAL-ECRANK-001 (prior) | GOAL-ECQ-001 (here) |
|---|---|---|
| family | quadratic twists of 5 fixed curves | one-parameter pencil of plane cubics |
| generic rank of the family | 0 | **8** (every fibre) |
| excursion the statistic must detect | 0 → ≥ 5 | 8 → 9…12 |
| conductor scale | `d² · N_E`, `d` up to 3·10⁵ | fibres of one rational elliptic surface, `|p|≤150, q≤8` |
| fraction certified | top 400 of 364 756 = 0.11 % | top 60 of 1 548 = 3.9 % |

`S(N)` is a rank-*excess* detector with a per-rank signal of ≈ 5.61 at `N = 1000`
and a noise floor set by the family. Asking it for a +5 excursion in the extreme
tail of a rank-0 twist family at conductor ~10¹¹ is a different measurement from
asking it for a +1…+3 excursion in a family whose every member already has rank 8
at modest conductor. The prior's own record scopes itself correctly ("High base
rank over Q … was not reachable by this machinery"); what did not transfer is the
generalisation from twists to all families.

**This is the informative outcome a pre-recorded prior exists to produce**, and I
record it as such: the prior was right to demand the control, the control was run,
and the control says the statistic works *here*. Read narrowly (§4), not as a
rehabilitation of the statistic in general.

## 1.7 Objections that stand against joint 3

- **O3-A (presentation, real).** The headline rates use denominators of 60 that
  include 31 and 35 never-descended fibres. `20.0 % of fibres reach rank ≥ 11` is
  a *product* of a rank property and a solver-budget property, published under a
  name — "Mestre-Nagao efficiency" — that attributes all of it to the statistic.
  A reader sizing a larger sieve from `0.20` will be wrong by ~2×. The conditional
  numbers (§1.3) belong beside them. The producer's "lower bound" caveat is
  correct but does not carry the magnitude.
- **O3-B (scope, real).** n = 1 family, one 8-point configuration, one seed, one
  `K`, one tier-2 box. Every efficiency number is a property of *this pencil*.
  The producer scopes this honestly in
  `tested_parameters_and_transfer_assumptions`; it must not be widened by
  whoever writes the evidence record.
- **O3-C (artifact completeness, minor).** Control-arm MN scores discarded
  (§1.1).
- **O3-D (unbound implementation, real, but harmless here — see §3).** The
  archived `src/pipeline.py` is **not** the file that produced runs 001–004.

---

# JOINT 4 — two-axis gap, framing honesty, hidden cost

> *Joint as stated: the gap to 31 is measured on BOTH axes and the result is not
> framed as progress toward the record.*

## VERDICT: **HOLDS on framing; two substantive objections must be recorded before any evidence record cites `gap_analysis.json`.**

### 2.1 Is a rank-12 curve framed as progress toward 31? — No. Checked adversarially.

I grepped all four deliverables for `progress|toward|approach|record|promis`. There
is no sentence in which 12 approaches 31. The framing is the opposite of the
failure mode:

- `explicitly_not_progress_toward_31` says something **real**, not a hedge: it
  names the *reason* — "a rank-8 base is a different regime, not a smaller
  version of the same one" — rather than merely disclaiming. It survives the test
  I set for it: it identifies a mechanism (base-rank regime), not a magnitude.
- `report.md`: "A rank-12 result from a rank-8 Q(t) base is not a fraction of the
  way to 31; the ladder rests on a different base-rank regime."
- `published_record_base_rank_reference` is explicitly labelled *"cited as
  background, not measured here"* — the producer refuses to launder a recalled
  literature figure into a measurement. That is the right call and I credit it.
- **No extrapolation from sieve volume ignores base rank.** The opposite:
  `what_reaching_31_would_require[0]` states that more sieving of *this* surface
  cannot supply the base rank, because the rational-elliptic-surface bound caps
  it at 8. The one place a volume-based extrapolation could have been smuggled
  in is the place the producer closes.
- "Nothing was tuned toward rank 31" is checkable and checks out: the only search
  with an objective optimised model height (§1.4).

### 2.2 Does `gap_analysis.json` carry numbers on both axes, or narrative? — **Axis 2 yes; axis 1 numbers are hardcoded literals.**

This is my first substantive objection and it is not visible from the JSON.

Reading `cmd_assemble` in the archived `src/pipeline.py` (recovered by diff, §3):

- **Axis 2 is genuinely derived.** `tier1_specialisations_scored_measured`,
  `tier1_domain`, `tier2_matched_domain`, `seconds_per_mestre_nagao_score_measured`,
  `fibres_on_which_descent_was_attempted_measured`, `descent_timeouts_measured`
  all flow from the run records (`sv[...]`, `certs[0][...]`). Good.
- **Axis 1 is not.** `achieved_measured: 8`, `theoretical_ceiling_of_this_construction: 8`,
  `ceiling_reason`, the entire `achieved_evidence` string quoting *"nonsingular at
  t in {-1,-7,7/5,11/3,3} (least eigenvalue > 0.3), singular at t in {1,2,1/2,5}"*,
  `published_record_base_rank_reference` and `gap_in_base_rank: "10 to 12"` are
  **string and integer literals in the aggregation source**. Not one of them reads
  RUN-002's regulator output. The field name carries the suffix `_measured` and
  the value never touched a measurement.

To be exact about the severity: the literals appear to be **true** — the RUN-002
regulator table in `report.md` says what the string says, and out-of-joint my own
bottom-arm descents independently returned rank 4 at `t=1` and rank 7 at `t=2`,
matching the degenerate fibres named in that string. The defect is that
`gap_analysis.json` does not *bind* axis 1 to anything: the same file would be
emitted verbatim if RUN-002 had measured rank 6. A downstream record citing
`axis_1_base_rank_over_Qt.achieved_measured` is citing a constant, and must cite
RUN-002 instead. Same structural point, lower stakes, for
`explicitly_not_progress_toward_31`: it is a format string with only `best`
interpolated, so it would emit the identical disclaimer at any measured rank.
The honesty is the author's, not the artifact's.

Also, `gap_in_base_rank: "10 to 12"` is a string range differenced against an
unmeasured literature figure. Axis 1's *gap* is therefore a scoped estimate, not
a measurement — correctly disclosed, but it should not be read as a number of the
same kind as axis 2's.

### 2.3 Rule-3 audit: does any headline depend on treating a timeout as a negative result?

I checked each headline number against `certify_one`'s actual timeout semantics
(zero descent points, floored at 8, `descent_status: "timeout"`).

| headline | depends on a timeout being negative? |
|---|---|
| `best_certified_rank_over_Q_measured: 12` | **No.** A max over completed descents; a timeout contributes nothing to it either way. |
| `shortfall: 19` | **Marginally.** 31 − 12 where 12 is the max over the **56 fibres actually descended** of 140 attempted. If any of the 84 censored fibres carries rank ≥ 13 the shortfall is smaller. The direction is conservative (understates the family), but the number is published without the censoring qualifier. |
| MN-efficiency rates `0.467 / 0.400 / 0.200` and `0.267 / 0.100 / 0.000` | **Yes, structurally**, denominators include 31 and 35 timeouts. Labelled "LOWER bounds" with the counts shown — the disclosure requirement is met; the magnitude is not conveyed (§1.7 O3-A). |
| "at most +4 … **across 140 fibres** on which descent was attempted" | **Yes, as a rarity statistic.** The honest denominator for "how often does +4 happen" is 56 completed descents, not 140 attempted. 1/140 understates the per-successful-descent frequency by 2.5×. The wording "on which descent was attempted" is literally accurate, which is why this is a presentation defect and not a violation. |
| "84 of 140 descents timed out … Classified `resource_exhaustion`, not negative evidence" | **Rule 3 is honoured in substance, not merely cited.** Every timed-out fibre keeps its certified rank-8 floor from exhibited points; none is recorded as a rank failure; RUN-005's 10 unrun candidates are recorded as `not_run_budget_exhausted` rather than dropped; the deeper-alarm run that failed to beat RUN-004 is retained in full and nothing was re-scored. I checked for the specific abuse — a fibre recorded as "did not reach rank r" on the strength of a timeout — and found none in 137 curve records. |

**Conclusion on rule 3: honoured.** The two presentation defects above should be
corrected in the evidence record, not in the immutable run artifacts.

### 2.4 Omitted costs

- **The invariant's own cost is charged, and it is negligible.** Ordering all
  1 548 tier-2 fibres costs 1 548 × 1.028 ms = **1.59 s** against 327 s of descent
  in the MN arm. Cost per rank-≥11 curve, *including* the scoring cost: MN arm
  **≈ 27 s/hit**; random control **∞** (0 hits in 352 s of descent); my bottom
  arm **∞** (0 hits in 92 s). The eliminated dimension is genuinely paid for
  (`KN-LIT-7593` check passes). This is the strongest *cost* statement in the
  package and the producer does not make it — I recommend it be added.
- **Memory** is reported once (1.22 GB peak RSS, RUN-004) and not per arm. Fine
  at this scale; note it, do not act.
- **`gap_analysis.json:wall_clock_seconds: 0.0105`** is the assemble step, not the
  campaign. The campaign total (1 993.0 s over 7 runs) lives only in `report.md`.
  Trivially misreadable; worth a note in the evidence record.
- **`assembled_from_runs: [RUN-004, RUN-005]` overstates its own provenance.**
  Every count in axis 2 and in the efficiency block is computed from `certs[0]`
  — RUN-004 alone. RUN-005's 10 further attempts and 9 further timeouts are not
  in `140` or `84`. `report.md` attributes both correctly and separately; the
  JSON does not. Real, small, and fixable in the evidence record.
- **The headline 12 was obtained under a different budget from the matched arms.**
  It comes from the `tier1_global_top` arm at a **20 s** alarm on the tier-1
  domain (18 of 20 timed out), not from the 8 s matched tier-2 arms whose maximum
  is 11. `report.md` distinguishes them; `gap_analysis.json`'s
  `best_certified_rank_over_Q_measured: 12` does not.

### 2.5 **The omission that matters most: no Pareto comparison, and a pre-registered control left undischarged**

This is my second substantive objection and the one I would not let pass.

`H-ECQ-cec3c4.proof_search_map.method_ceiling.nearby_object_control` pre-registers,
in terms:

> "The carried-forward Mestre producer TASK-20260822-a7a9e8 is the nearby object:
> a different construction aimed at the same quantity. If the two disagree by a
> lot on best achievable rank, the cheaper one is wrong somewhere."

The deliverables never discharge it. I grepped all four for
`dominated_by|sota|a7a9e8|ECRANK-002|Mestre-style|baseline`: **zero hits in all
four files.** There is no `dominated_by`, no `sota_delta`, and no mention of the
sibling construction.

Meanwhile, **in the same snapshot commit**, `.../TASK-20260822-a7a9e8/report.md`
(hash-verified above) reports:

> maximum certified rank **13**, two curves; and over 34 740 scanned:
> rank 13 × 2, rank 12 × **29**, rank 11 × **425**, rank 10 × 3 445.

So the pencil route produced **one** rank-12 curve from 140 attempted descents,
while the program's own concurrently-archived Mestre-style route reports 29
rank-12 curves, 425 rank-11 curves, and a higher maximum. On the axis
`gap_analysis.json` chooses as its headline — best certified rank over Q — the
reviewed pipeline is, on the face of the archived record, **dominated by a
baseline sitting in the same commit and named in its own hypothesis**.

Three qualifications, so this is not overstated:

1. I did **not** verify the rank-13 claim. It is under binding condition **BC1**
   of the archive receipt (verification must use untrimmed originals recovered
   from history) and is another reviewer's or another round's work. I report the
   comparison as *owed*, not as adjudicated.
2. The two are different objects with different costs and the pencil route's
   value is not only its maximum rank — its base-rank *ceiling* is a theorem,
   which the Mestre route does not offer.
3. `gap_analysis.json` does compare against the published ladder (28/29/30),
   which is the external baseline. It is the *internal* baseline that is missing.

Under `docs/inventor-protocol.md` an unchecked `null` in `dominated_by` is a
fabrication; here there is no field at all, in a deliverable whose hypothesis
pre-registered the comparison. That is a gap to be filled by the Coordinator's
decision record, and `best_certified_rank_over_Q_measured: 12` must be labelled
as **a within-family maximum for this pencil**, never as the program's best.

### 2.6 Challenging the closure — the one place the record over-reaches

Per my contract I attack the negative result as hard as the positive one. The
package asserts, and `H-ECQ-cec3c4` states, that this route **CANNOT** reach 31.

*What survives:* the named obstruction is a genuine theorem, not a fatigue
report. A pencil of plane cubics through 8 base points is a rational elliptic
surface, whose Mordell–Weil rank over `Q̄(t)` is at most 8 (Shioda–Tate). It is
*measured*, not asserted: `deg c4 = 4`, `deg c6 = 6`, `deg Δ = 12` is the
signature of a rational elliptic surface, and it is in `qt_family.json`. Forward
guidance is named — a K3 or higher surface is required, not more sieving. This
meets the closure standard, and I do not object to it.

*Where it over-reaches, by exactly one quantifier:* the theorem caps the base
rank over `Q(t)`. It caps **nothing** about the rank over Q of a specialisation,
which is `8 + extra`, and `extra` is unbounded by anything in the package. The
inference "therefore this route cannot reach 31" needs a second premise —
that `extra` stays small — and the only support for that premise is
`extra ≤ 4` observed over **56 completed descents out of 140 attempted, in a box
of 1 548 fibres drawn from a domain of 97 640, itself a finite window on an
infinite fibration**. The published ladder is itself built by finding `extra` of
order +10 to +12 on higher surfaces, so large `extra` is not a priori absurd; it
is merely unobserved here. The defensible closure is:

> This construction cannot exceed base rank 8 over `Q̄(t)` — theorem. Within the
> searched domain, the largest excess over the base was +4 in 56 completed
> descents — measurement, censored at 60 %. Together these make 31 unreachable
> *by this search as run*; they do not prove it unreachable by this surface.

`gap_analysis.json`'s own text is closer to this than the hypothesis statement
is ("was not observed at any point in this search and is not a scale-up of
anything measured here" is the correct form). The hypothesis's "CANNOT reach 31"
should be narrowed when its status is set.

*Reversal — which theory takes this obstruction as its hypothesis?* The record
does not ask, so I will. The measurement that reads as an asset is §1.5: **on a
family with a fixed, small, provably-capped base rank, `S(N)` separates rank at
≈ 5.6 units per rank against a noise floor small enough to sort rank 8 from rank
11 and to sort the degenerate fibres to the bottom.** The cap is precisely what
makes the calibration clean — every fibre shares a base, so the score's variance
is the excess and nothing else. That is the opposite of the twist-family regime
where the statistic failed. Read as a resource, this pencil is a **cheap, fully
descendable calibration fixture for MN-sieve design**, on which threshold, `N`,
and arm-size choices can be tuned at 1 ms/score and 7.5 s/descent, before they
are spent on a K3 base where 2-descent is unaffordable and where — by the
producer's own axis-2 finding — certification, not scoring, is the binding cost.
This is a candidate for the ranking, not evidence, and it changes no status.

---

## 3. Could the recorded faults have contaminated a NUMBER?

The envelope asks me to separate procedural ugliness from numerical
contamination. I treated this as a question with an answer and went to look.

**D-CONCURRENCY-NOISE (orchestrator durability commits, HEAD moved during
RUN-004): no numerical effect, and one real reproducibility defect discovered
while checking.**

I found and verified a genuine artifact-integrity defect, though not a
contaminating one. `report.md` records `src/pipeline.py` sha256
`8469e148…a78a2c4d` for runs 001–004. The **archived** `src/pipeline.py` at the
snapshot hashes to `0f96a8e5cf47ada2b7af2aa4d579e84bb9073aac2e65460a16b309f1508f869c`
— a **different file**. The receipt's `path_sha256` does not bind
`src/pipeline.py` at all (receipt open item **O2**). So the code in the snapshot
is provably not the code that produced the matched-arm comparison, the certified
curves, or the P1 regulators.

Rather than accept or reject the producer's "additive only" assurance, I
recovered the exact `8469e148…` blob from history (commit
`c8a44009ab2e10e13921beee47477c697703aaf4`, sha256 confirmed byte-for-byte) and
diffed it against the archived file. The complete difference is:

```
@@ -1129,6 +1129,8 @@   cmd_certify
+    if args.only_arm:
+        arms = {args.only_arm: arms[args.only_arm]}
@@ -1172,6 +1174,128 @@
+def cmd_assemble(args): ...        # aggregation only, reads run records, no mathematics
@@ -1209,9 +1333,18 @@   main()
+    s.add_argument("--only-arm", default=None)   # + assemble subparser wiring
```

Not one mathematical function differs — not `certify_rank`, not
`independent_subset`, not `extra_points`, not `mn_score`, not `specialise`, not
`build_family`. The `--only-arm` guard is a no-op unless the flag is passed, and
RUN-004's recorded `command.txt` does not pass it. **The producer's claim is true
and is now verified rather than asserted.** No number in runs 001–004 could have
moved.

Independently: my from-scratch reimplementations reproduced the producer's
`a_invariants` on 140/140 fibres, the MN top-60 in order with zero score
difference, the seeded control draw in order, and all 137 certified ranks. If a
concurrency event had perturbed a computation, these would not all close.

**D-WRITE-SCOPE (orchestrator wrote into a *running* producer's scope): no
numerical effect on the work I reviewed; a real audit cost on the work I did
not.** The writes were into `TASK-20260822-a7a9e8`'s directory, not
`81141a`'s, and were additive (a `.gz` copy and a note). Nothing in
`GOAL-ECQ-001`'s numbers can have been touched by it. But the receipt records
that the collision "interacted with" the producer's decision about what to trim,
and trimming is exactly what BC1 now constrains. So the cost landed on the
*auditability* of the rank-13 figure — which is the figure §2.5 says this batch
owes a comparison against. That is not a coincidence worth ignoring: the
orchestration fault and the missing baseline comparison intersect on the same
number.

**D-IMMUTABILITY (producer overwrote completed run records in place): no effect
on anything I reviewed; unresolved for what I did not.** Confined to
`TASK-20260822-a7a9e8` runs. Under BC1–BC3 the rank-13 comparison must be made
against untrimmed originals; I made no use of that producer's raw output and
assert nothing about it.

**Verdict on contamination: no number in the reviewed package moved.** Every
recorded fault is procedural. The one defect I found that could have hidden a
numerical change — the unbound and *provably different* archived implementation
— I closed by recovering the original from history and diffing it. The
appropriate response is O2's: bind `src/pipeline.py` by hash in the ledger
archive, recording **both** hashes and the recovery commit `c8a44009`, exactly as
D-STORAGE does for the `.gz`.

---

## 4. Narrowest supported statement (both my joints)

> Within one pencil of plane cubics through eight specified rational points, over
> the domain `t = p/q`, `gcd(p,q)=1`, `|p| ≤ 150`, `q ≤ 8` (1 548 fibres), with
> PARI 2.15.4 `ellrank` under an 8 s alarm: ordering by `S(1000)` and certifying
> the top 60 produced certified ranks ≥ 11 on 12 fibres, while a uniform random
> 60 from the same 1 548 produced none, and the bottom 20 produced no fibre above
> rank 8. Every certified rank is a lower bound from exhibited points
> independently re-verified in exact arithmetic; the statistic contributed to no
> rank. The effect survives conditioning on descent completion and is monotone in
> the score. The best certified rank anywhere in the package is 12, on one curve,
> obtained under a 20 s alarm on the tier-1 domain — a within-family maximum,
> shortfall 19 to the open target 31, with 84 of 140 attempted descents censored.
> Base rank over `Q(t)` is 8 and is capped at 8 for this construction by the
> rational-elliptic-surface bound; that theorem caps the base, not the rank of a
> specialisation over Q.

Nothing here supports the Mestre–Nagao statistic in any other family, at any
other `N`, or on any other surface; the GOAL-ECRANK-001 negative result stands
unchanged within its own scope.

---

```yaml
red_team_report:
  id: RT-20260822-53748a   # RT-* is not in tools/allocate_id.py's identifier
                           # space (no 'rt' type); bound to the task token
                           # rather than minting an uncheckable new one.
  task_id: TASK-20260822-53748a
  joints_owned: [3, 4]
  snapshot_commit: b71f466840fe6cface5a6b87c4e518841793399e
  claim_under_review: >-
    Joint 3: the Mestre-Nagao statistic was used ONLY to order candidates and
    never contributed to a certified rank, and the claimed sieve efficiency is
    supported. Joint 4: the gap to 31 is measured on both axes and the result is
    not framed as progress toward the record.
  verdicts:
    joint_3: holds
    joint_4: holds
  routing_check:
    max_rank_claimed_over_Q: 12
    escalation_to_review_breakthrough_triggered: false

  objections:
  - id: OBJ-1
    joint: 4
    severity: substantive
    statement: >-
      gap_analysis.json's entire axis-1 block -- achieved_measured, the ceiling,
      ceiling_reason, achieved_evidence and gap_in_base_rank -- consists of
      literals hardcoded in cmd_assemble. No axis-1 value flows from RUN-002. The
      suffix "_measured" is carried by values that never touched a measurement.
      The literals appear to be true, but the artifact does not bind them.
    artifact: src/pipeline.py cmd_assemble (recovered by diff, see report section 3)
    remedy: >-
      Any downstream record must cite RUN-ECQ-81141a-002 for axis 1, never
      gap_analysis.json's axis-1 fields; derive them, or drop the _measured
      suffix.
  - id: OBJ-2
    joint: 4
    severity: substantive
    statement: >-
      No dominated_by, no sota_delta, and no mention of TASK-20260822-a7a9e8 in
      any of the four deliverables, although H-ECQ-cec3c4's proof_search_map
      pre-registers that producer as the nearby-object control, and although its
      hash-verified report in the SAME snapshot reports max certified rank 13
      with 29 rank-12 and 425 rank-11 curves. On its own headline axis the
      reviewed pipeline appears dominated by a baseline in the same commit.
    artifact: >-
      grep of report.md/gap_analysis.json/certified_curves.json/qt_family.json
      for dominated_by|sota|a7a9e8|ECRANK-002|Mestre-style|baseline -> 0 hits;
      .../TASK-20260822-a7a9e8/report.md section 1
    caveat: >-
      The rank-13 figure is under archive receipt BC1 and is NOT verified by me.
      The comparison is owed, not adjudicated.
    remedy: >-
      Label best_certified_rank_over_Q_measured: 12 as a within-family maximum
      for this pencil; discharge the nearby-object control in the decision record
      with a dominated_by entry across time, memory and volume.
  - id: OBJ-3
    joint: 3
    severity: presentation
    statement: >-
      Efficiency denominators of 60 include 31 and 35 never-descended fibres, so
      the published rates are joint measurements of a rank property and a solver
      budget under a name that attributes all of it to the statistic. Correctly
      labelled lower bounds; magnitude not conveyed (conditional rates are
      28/29, 24/29, 12/29 vs 16/25, 6/25, 0/25).
    artifact: pipeline.py cmd_assemble rate(); runs/RUN-ECQ-81141a-004/raw-result.json
  - id: OBJ-4
    joint: 4
    severity: presentation
    statement: >-
      "at most +4 across 140 fibres" is a rarity statistic whose honest
      denominator is the 56 completed descents, not the 140 attempted; it
      understates the per-successful-descent frequency by 2.5x. Wording is
      literally accurate ("on which descent was attempted"), hence presentation
      and not a rule-3 violation.
    artifact: gap_analysis.json what_reaching_31_would_require[1]
  - id: OBJ-5
    joint: 4
    severity: minor
    statement: >-
      assembled_from_runs lists RUN-004 and RUN-005, but every axis-2 count and
      every efficiency figure is computed from certs[0] = RUN-004 alone; RUN-005's
      10 further attempts and 9 further timeouts are absent from 140 and 84.
      report.md attributes both runs correctly; the JSON does not. Separately,
      best_certified_rank 12 came from the 20 s tier-1 arm, not the 8 s matched
      arms whose maximum is 11, and the JSON does not say so.
    artifact: pipeline.py cmd_assemble; runs/RUN-ECQ-81141a-005/raw-result.json
  - id: OBJ-6
    joint: 3
    severity: minor
    statement: >-
      The control arm's MN scores were written as null (pipeline.py:1071),
      discarding the covariate needed for the pooled dose-response test that most
      strongly supports the producer's own claim. I had to recompute all 1548
      scores to run it.
    artifact: runs/RUN-ECQ-81141a-003/raw-result.json tier2_random_control_arm
  - id: OBJ-7
    joint: both
    severity: real, non-contaminating (closed by this review)
    statement: >-
      The archived src/pipeline.py (sha256 0f96a8e5...f869c) is NOT the file that
      produced runs 001-004 (recorded 8469e148...a78a2c4d), and the archive
      receipt binds no hash for it (receipt open item O2). I recovered the
      original from commit c8a44009 and diffed: the only differences are a no-op
      --only-arm guard, the aggregation-only cmd_assemble, and argparse wiring.
      No mathematical function differs. No number could have moved.
    remedy: >-
      Bind src/pipeline.py in the ledger archive recording BOTH hashes and
      recovery commit c8a44009, as D-STORAGE does for the .gz.
  - id: OBJ-8
    joint: 4 (closure challenge)
    severity: substantive, scoping
    statement: >-
      "This route CANNOT reach 31" over-reaches by one quantifier. The
      rational-elliptic-surface bound caps the base rank over Qbar(t) at 8; it
      caps nothing about rank over Q of a specialisation, which is 8 + extra. The
      only support for "extra stays small" is extra <= 4 over 56 completed
      descents of 140 attempted in a 1548-fibre box drawn from a 97640 domain --
      a finite, 60%-censored window on an infinite fibration. The published
      ladder is built from extra of order +10 on higher surfaces.
    narrowed_form: >-
      This construction cannot exceed base rank 8 over Qbar(t) (theorem); within
      the searched domain the largest excess was +4 in 56 completed descents
      (measurement, censored). Together: 31 is unreachable by this search as run,
      not proven unreachable by this surface.

  required_controls:
  - id: CTRL-1
    priority: 1
    statement: >-
      Un-censor the matched arms. Re-descend the 31 + 35 timed-out tier-2 fibres
      at a 120 s alarm and republish the efficiency rates with completed-descent
      denominators. This converts every "lower bound" into a measurement and
      discharges OBJ-3 directly. Cost bounded by 66 x 120 s; the observed
      distribution suggests far less.
    status: not run
  - id: CTRL-2
    priority: 2
    statement: >-
      Replicate the whole matched-arm design on a SECOND 8-point configuration
      (new seed). Currently n = 1 family; every efficiency number is a property
      of this pencil. Cost approx. one RUN-002 + RUN-003 + RUN-004 (~1200 s).
    status: not run
  - id: CTRL-3
    priority: 3
    statement: >-
      Height-ordered arm: order the same 1548 fibres by naive height of t instead
      of S(N), K = 60, 8 s alarm. Separates "MN measures rank" from "MN measures
      small height". Largely pre-empted by this review's measurement of
      Spearman(score, log|a6|) = -0.084 and Spearman(log|a6|, timeout) = +0.765,
      which show the censoring mechanism is orthogonal to the score.
    status: not run, largely answered
  - id: CTRL-4
    priority: run and reported here
    statement: >-
      Decay control: descend the BOTTOM 20 of the same tier-2 ordering at the same
      8 s alarm. RUN BY THIS REVIEW with an independent harness. Result: 11
      timeouts, 9 completed, ranks {4,5,6,6,7,7,7,8,8}, max 8, zero at rank >= 9
      (Fisher vs random control p = 9.3e-4; vs MN arm p = 6.1e-8). Timeout rate
      51.7 / 58.3 / 55.0 % is FLAT across the ordering while yield falls
      0.966 -> 0.640 -> 0.000.
    status: completed, supports the producer

  counterexample_or_mutation: >-
    None found. The strongest candidate -- that differential descent timeouts
    manufacture the arm gap -- is refuted three ways: the gap widens under
    conditioning on completion (12/29 vs 0/25, p = 1.5e-4); the MN arm has FEWER
    timeouts than the control; and timeout rate is flat top-to-bottom across the
    ordering while yield decays monotonically. The second candidate -- that MN
    selects small-height, easily-descended fibres -- is refuted by
    Spearman(score, log|a6|) = -0.084 against Spearman(log|a6|, timeout) = +0.765.

  baseline_comparison:
    external: >-
      Published ladder over Q: 28 (Elkies 2006), 29 (Elkies-Klagsbrun 2024), 30
      (Alpoge-Howell 2026); target 31 open. Certified here: 12. Shortfall 19,
      correctly stated, with the base-rank regime named as the reason. Cited as
      background by the producer and explicitly not measured -- the right call.
    internal_missing: >-
      TASK-20260822-a7a9e8 (GOAL-ECRANK-002, carried forward under
      DEC-20260822-d9bf63) reports max certified rank 13, with 29 rank-12 and 425
      rank-11 curves over 34740 scanned, in this same snapshot. Not compared
      against, though pre-registered as the nearby-object control. See OBJ-2.
      NOT verified by me; under archive receipt BC1.
    cost_axis_the_producer_did_not_state: >-
      Cost per certified rank->=11 curve, invariant cost included: MN arm 27 s/hit
      (327 s descent + 1.59 s to score all 1548); random control infinite (0 hits
      in 352 s); bottom arm infinite (0 hits in 92 s). The eliminated search
      dimension is genuinely paid for -- the KN-LIT-7593 check passes.

  heuristic_challenges:
  - id: HC-1
    heuristic: >-
      HEUR-1 of H-ECQ-cec3c4: S(N) orders specialisations by likely rank well
      enough that the top of the ordering is worth certifying.
    challenge_and_outcome: >-
      Explicit, numbered, pre-registered with its own falsification ("if it orders
      no better than chance the campaign still reports a certified best rank").
      The random-model justification is the BSD-style prediction of a shift of
      sum_{p<=N} log p / p per unit of rank = 5.6095 at N = 1000. TRANSFER
      CHECKED, not assumed: observed mean-score steps by certified rank are
      +5.26, +3.91, +2.61 (first step vs 5.61 predicted; compression at the top is
      the expected selection effect), Spearman(score, rank | completed) = +0.779,
      and the tier-2 score span of 27.74 is 4.95 rank-units -- adequate dynamic
      range to separate rank 8 from 12. The heuristic transfers to THIS object.
  - id: HC-2
    heuristic: >-
      The implicit assumption that GOAL-ECRANK-001's negative MN result transfers
      to this family. It does not, and the record should say so explicitly.
    challenge_and_outcome: >-
      EV-ECRANK-b6c9b6 measured a rank-0 quadratic-twist family being asked for a
      +5 excursion in its top 0.11% at conductor ~1e11. Here every fibre already
      has rank 8 and the ask is +1..+3 in the top 3.9% at modest conductor. Not
      the same measurement. The prior over-generalised from twists to families;
      the earlier measurement stands within its own scope.

  cost_model_challenges:
  - >-
    Rate denominators include never-descended fibres (OBJ-3).
  - >-
    Rarity statistic "1 in 140" should be "1 in 56" (OBJ-4).
  - >-
    gap_analysis wall_clock_seconds 0.0105 is the assemble step, not the campaign
    (1993.0 s over 7 runs, in report.md only).
  - >-
    Headline 12 obtained at a 20 s alarm on tier 1; matched arms ran at 8 s on
    tier 2 with maximum 11. Not distinguished in the JSON.
  - >-
    Per-arm memory not reported; 1.22 GB peak RSS reported once for RUN-004. Note
    only, no action at this scale.
  - >-
    Positive finding -- the invariant's own cost IS charged and is negligible
    (1.59 s of scoring against 327 s of descent); certification, not scoring, is
    correctly identified as the binding cost.

  reduction_and_scope_challenges:
  - >-
    The rational-elliptic-surface bound is correctly invoked for the base rank and
    incorrectly extended to the specialisation rank over Q (OBJ-8).
  - >-
    published_record_base_rank_reference "roughly 18-20" is explicitly labelled
    background and not measured -- correct provenance discipline, and it must stay
    labelled in any record that repeats it.
  - >-
    Scope must not widen past one pencil, one configuration, one seed, one tier-2
    box, PARI 2.15.4 ellrank, and the stated alarms.

  proof_architecture_challenges:
  - id: PA-1
    attack: quantifier-order
    finding: >-
      H-ECQ-cec3c4 states the order correctly ("EXISTS 8 rational points such
      that FOR ALL specialisations outside a finite bad set ... and EXISTS t0
      among those searched whose certified rank is >= 11"), and the second
      existential is the only thing claimed. The closure statement in the same
      record then quietly universalises over unsearched t (OBJ-8). The theorem
      statement is right; the closure sentence is not.
  - id: PA-2
    attack: method-ceiling
    finding: >-
      The ceiling the resource measure supports is base rank 8 + (excess
      observable within a 60%-censored 56-descent sample). It does not reach 31,
      which is what the package says. Ceiling audit passes for the positive claim
      and is the source of OBJ-8 for the negative one.
  - id: PA-3
    attack: obstruction resource_check (inventor protocol)
    finding: >-
      Neither report.md nor gap_analysis.json carries an obstruction block with a
      quantity, units and error bars, nor a resource_check. As an executor the
      producer does not owe one; the Coordinator's decision record does. Proposed
      reading: the provably-capped base rank is exactly what makes S(N) legible
      here (fixed base => score variance is the excess and nothing else), so this
      pencil is a cheap fully-descendable calibration fixture for MN-sieve design
      (N, threshold, arm size) at 1 ms/score and 7.5 s/descent, transferable to a
      K3 base where 2-descent is unaffordable. Candidate for the ranking; not
      evidence; changes no status.

  narrowest_supported_statement: >-
    Within one pencil of plane cubics through eight specified rational points,
    over t = p/q with gcd(p,q)=1, |p| <= 150, q <= 8 (1548 fibres), using PARI
    2.15.4 ellrank under an 8 s alarm: ordering by S(1000) and certifying the top
    60 produced certified rank >= 11 on 12 fibres, a uniform random 60 from the
    same 1548 produced none, and the bottom 20 produced nothing above rank 8.
    Every certified rank is a lower bound from exhibited points re-verified in
    exact arithmetic; the statistic contributed to no rank. The effect survives
    conditioning on descent completion and is monotone in the score. Best
    certified rank in the package is 12, on one curve, under a 20 s alarm on the
    tier-1 domain -- a within-family maximum, shortfall 19 to the open target 31,
    with 84 of 140 attempted descents censored. Base rank over Q(t) is 8 and is
    capped at 8 for this construction; that theorem caps the base, not the rank of
    a specialisation over Q.

  next_concrete_action: >-
    Before any evidence record cites gap_analysis.json, the Coordinator must (a)
    discharge the pre-registered nearby-object control by comparing against
    TASK-20260822-a7a9e8's reported rank 13 under BC1, and record a dominated_by
    entry across time, memory and volume, relabelling
    best_certified_rank_over_Q_measured: 12 as a within-family maximum (OBJ-2);
    and (b) cite RUN-ECQ-81141a-002 rather than gap_analysis.json's hardcoded
    axis-1 literals for the base rank (OBJ-1). The single highest-value new
    measurement is CTRL-1: re-descend the 66 timed-out tier-2 fibres at a 120 s
    alarm and republish the efficiency rates with completed-descent denominators.

  artifact_paths:
  - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/tasks/TASK-20260822-53748a/red_team_report.md
```

---

```yaml
review_attestation:
  task_id: TASK-20260822-53748a
  role: red-team
  joints_owned: [3, 4]
  verdicts: {joint_3: holds, joint_4: holds}
  independent_session: true
  requested_policy: review-adversarial
  resolved_model: claude-opus-5
  resolved_via: >-
    python3 -m orchestration.adapter resolve --role red-team --independent-session
    -> "review-adversarial -> anthropic:claude-opus-5 (effort=xhigh)"
  reasoning_effort: xhigh
  fallback_used: false
  degraded_allowed: false
  degraded_requirements: []
  model_verified: >-
    NOT probe-verified. `orchestration.adapter doctor --probe` was not run by this
    task; the resolution above is configuration plus the runtime's own model
    identity, not a backend probe.
  runtime: claude_code
  snapshot_commit_read: b71f466840fe6cface5a6b87c4e518841793399e
  read_sibling_reports: false
  sibling_task_in_round: TASK-20260822-0a0041 (joints 1, 2, proves_too_much,
    blind_rederivation) -- its directory was not listed, opened, or read.
  blindness_lifted_for_me: false

  paths_actually_read:
  - AGENTS.md
  - agents/red-team.md
  - ledger/handoffs/TASK-20260822-53748a.yaml
  - ledger/handoffs/TASK-20260822-81141a.yaml
  - ledger/hypotheses/H-ECQ-cec3c4.yaml
  - ledger/questions/RQ-ECQ-80f23c.yaml
  - ledger/evidence/EV-ECRANK-b6c9b6.yaml
  - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/archives/TASK-20260822-66bacf/receipt.yaml
  - "@b71f4668 .../BATCH-7e06d3/tasks/TASK-20260822-81141a/report.md"
  - "@b71f4668 .../BATCH-7e06d3/tasks/TASK-20260822-81141a/gap_analysis.json"
  - "@b71f4668 .../BATCH-7e06d3/tasks/TASK-20260822-81141a/certified_curves.json"
  - "@b71f4668 .../BATCH-7e06d3/tasks/TASK-20260822-81141a/qt_family.json"
  - "@b71f4668 .../BATCH-7e06d3/tasks/TASK-20260822-81141a/src/pipeline.py"
  - "@b71f4668 .../BATCH-7e06d3/tasks/TASK-20260822-81141a/runs/RUN-ECQ-81141a-00{2..7}/raw-result.json"
  - "@b71f4668 .../BATCH-7e06d3/tasks/TASK-20260822-81141a/runs/RUN-ECQ-81141a-00{1..7}/{command.txt,manifest.yaml}"
  - "@b71f4668 .../BATCH-e0caa5/tasks/TASK-20260822-a7a9e8/report.md  (handoff input; producer report, not a reviewer report)"
  - "@c8a44009 .../TASK-20260822-81141a/src/pipeline.py  (pre-modification version, recovered for the diff in section 3)"

  computations_run_by_this_review:
  - id: RTC-1
    what: >-
      Independent recomputation of S(1000) for all 1548 tier-2 specialisations
      from the published c4/c6 polynomials, using own model construction, own
      prime sieve, own Fraction arithmetic; reproduction of the score ordering and
      of random.Random(81141).sample.
    result: >-
      top-60 identical in order to the recorded MN arm, max score difference 0.0;
      seeded draw reproduces the recorded control arm in order; domain sizes 97640
      and 1548 both reproduced.
  - id: RTC-2
    what: >-
      Independent re-trace of all 137 certified ranks: exact on-curve check of
      every exhibited point with own Fraction arithmetic, own height matrix, own
      greedy independent subset.
    result: >-
      0 points off curve, 0 rank mismatches, 0 structural violations; certified
      rank == ellrank r_low == r_high in all 54 completed descents; all 83
      timed-out fibres at exactly rank 8.
  - id: RTC-3
    what: >-
      Conditional and dose-response reanalysis of the 120 descended tier-2 fibres,
      including the control-arm scores the producer discarded (recomputed in RTC-1);
      Fisher exact tests; Spearman correlations for the censoring mechanism.
    result: see report sections 1.3 and 1.5.
  - id: RTC-4
    what: >-
      NEW MEASUREMENT. Bottom-20 decay arm over the same tier-2 domain at the same
      8 s alarm, run with an independent harness that does not import
      src/pipeline.py.
    result: >-
      11 timeouts, 9 completed, ranks {4,5,6,6,7,7,7,8,8}, max 8, zero at rank
      >= 9; timeout rate flat across the ordering.
  - id: RTC-5
    what: >-
      Recovery of the sha256-8469e148 pipeline.py from commit c8a44009 and diff
      against the archived file; verification of the archive receipt's six
      declared path_sha256 values at the snapshot.
    result: >-
      diff is exactly a no-op --only-arm guard + aggregation-only cmd_assemble +
      argparse wiring; no mathematical function differs. All six content hashes
      match the receipt.

  authority_note: >-
    This report changes no research status, no hypothesis, and no raw artifact. It
    is written only under the assigned write_scope
    (coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/tasks/TASK-20260822-53748a)
    and is not committed by this role; it is handed to the Coordinator's ledger
    archive task TASK-20260822-2fa82a. Verdicts are on joints 3 and 4 only -- a
    whole-claim verdict from a blinded reviewer would be an opinion formed from a
    fraction of the evidence, and the Coordinator composes the round.
  authored_at: '2026-08-22'
```
