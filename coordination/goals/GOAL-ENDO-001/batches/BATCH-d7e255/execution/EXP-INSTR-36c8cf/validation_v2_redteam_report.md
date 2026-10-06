# Red-team review V2: the freeze question in EXP-INSTR-36c8cf amendment v2 (E6/E7)

`RT-20260811-35ab34` · GOAL-ENDO-001 · BATCH-d7e255 · EXP-INSTR-36c8cf
Snapshot read: **2b9af4d611aeb6034485f7d958271281f1182e53** (working tree matched `HEAD`
exactly at read time — `git status --short` empty — so this is a committed-snapshot read,
not a working-tree-only read). No `TASK-*` handoff for this specific V2 review exists yet
under `ledger/handoffs/`; this report's `task_id` is therefore recorded as not provided
rather than invented.

## VERDICT

**QUALIFIED DISSENT — not a flat rejection, but a blocking finding on the CURRENT TEXT of
E6/E7.** The *mechanism* the amendment describes (deterministic doubling, unchanged
estimator formula, unchanged coverage, filed before its data exists, a declared terminal
rung with a declared terminal outcome) is **genuinely different in kind** from the
[1.3, 3.6]-band hull-fitting this campaign already burned itself on
(`experiments/EXP-ICINV-4d33aa/amendments/v2.yaml` post-review A5). That distinction holds
up under attack: E6 moves no acceptance boundary in response to an observed failure, and E7
bounds the number of future "looks" and pre-commits to a terminal outcome in both
directions, which a naive sample-until-you-pass loop does not do. **On form, this is closer
to a genuine sequential design than to optional stopping.**

But **the *substance* the amendment claims — that reaching the terminal rung without firing
F4 would mean something about HEUR-INSTR-4 over the competing heavy-tail explanation — does
not follow from the mechanism as specified**, for a reason independent of whether HEUR-INSTR-4
is in fact true: **E3's stability criterion (T2's actual accept/stop trigger) is satisfied
by both live explanations, given enough seeds, as long as the true distribution has finite
variance.** A heavy-tailed-but-finite-variance row (Explanation B, the one
`competing_explanation_not_excluded` names) will *also* eventually show a shrinking
rung-to-rung half-width change — more slowly, but shrinking — so "the 5% rule was met at
rung 8" cannot by itself discharge HEUR-INSTR-2/4 the way `specification.yaml`'s own
`heuristic_under_test_note` says it does ("HEUR-INSTR-2 ... is validated by C-SEED-STABILITY").
The only mechanism that *can* discriminate the two explanations is the E9 D1/D2 diagnostic
(rate-of-shrinkage, skewness, one-sided exceedance count) — and D2 explicitly **"gates
nothing"** (E9 text, `what_this_amendment_does_not_do` block does not mention it either). So
the *binding* stopping/acceptance rule (T2) can fire and hand an interval to the SR3 v3 gate
before the only diagnostic that could have caught a heavy tail has any power to stop it.
That is not optional stopping in the classical p-hacking sense, but it is a **stopping rule
whose formal trigger is only weakly informative about the thing it is being used to certify**,
and the amendment presents passing it as though it were strong validation.

Three further, independently-checkable findings (below) sharpen this into concrete required
repairs rather than a vague misgiving. None of them individually proves motivated design; all
three point the same direction (toward making eventual "stability" easier to reach or more
persuasive than it should be), and the amendment evaluates each in isolation without noting
that they compound.

---

## Material findings

### F1 (Q1 — optional stopping vs precision). The stopping trigger does not distinguish the two live hypotheses; it distinguishes "finite variance" from "infinite variance," which nobody is proposing

`the_freeze_question_confronted_rather_than_assumed` argues the extension is licensed by four
conditions: (a) acceptance region untouched, (b) no visible datum to fit toward, (c) filed
before the governed data exists, (d) deterministic and terminating. All four hold as stated —
I checked each against the amendment text and found no violation. **But those four conditions
answer "is this the same defect as widening the [1.3, 3.6] band?" (no) without answering
"does satisfying E3 at rung 8 actually validate HEUR-INSTR-2/4 over
`competing_explanation_not_excluded`?" (not by itself).**

Concretely: the derivation in `DEC-20260810-5aeeaa.adjudication_item_1.arithmetic_check_of_the_input_offered_by_the_archiving_session`
establishes that the *rate* at which rung-to-rung noise shrinks is `1/(2*sqrt(n_prev))` under
an i.i.d.-with-finite-variance model — this is a **general consistency fact about sample
standard deviations**, true whenever the underlying distribution has a finite fourth moment,
Gaussian or not. A right-skewed or heavy-tailed-but-finite-variance row (exactly what
`competing_explanation_not_excluded` proposes) obeys the *same* asymptotic shrinkage law, just
possibly with a larger constant or a slower approach to it. So **E3 passing at some large rung
is compatible with both Explanation A (ordinary noise, HEUR-INSTR-4 true) and Explanation B
(heavy tail, HEUR-INSTR-3 inadequate at 259/260 coverage)** — the criterion that actually
falsifies HEUR-INSTR-4 is *sustained*, *anomalous* (non-1/√n) persistence of instability, or a
skewed/heavy exceedance pattern in D1/D2, not "did it eventually pass." T3 only names the
*negative* branch (rule not met by rung 8 ⇒ F4 terminal); it says nothing about the epistemic
weight of the *positive* branch, and T2 treats the positive branch as sufficient for
`accepted_rung`, full stop.

**Required repair (R1).** T2 should not accept a rung on E3 alone. Bind D1 (the ratio of
observed relative change to `1/(2*sqrt(n_prev))`) and D2 (skewness / one-sided exceedance
count) into the acceptance condition — e.g., "accepted only if E3 is met *and* D1's ratio is
within a declared band of 1 at every row *and* D2 shows no material one-sided exceedance excess" —
or explicitly downgrade `accepted_rung` to a *provisional* status pending a stated D1/D2
threshold, rather than a status EXP-ICINV-4d33aa's SR3 v3 gate can consume directly.

**Counterexample / mutation (cheapest control, no new compute).** Simulate 13 independent
columns of i.i.d. Student-t(df=5) draws (finite variance, heavy tail, easy to generate) at
n = 12, 24, 48, 96, ..., 1536 and run E2/E3/T1/T2/T3 verbatim against the simulation. This is
a **null-object control in the sense `docs/inventor-protocol.md` §3 requires**: it holds the
convergence-rate mechanism fixed and varies only the tail shape. Prediction under my objection:
the simulated heavy-tailed ladder *also* eventually satisfies E3 (T2 fires, `accepted_rung`
becomes non-null) at a rung within reach of the declared ladder, while D2's skewness/exceedance
diagnostic on the *same* simulated data shows the anomaly the real data's fb=11/fb=22 pattern
hints at. If that prediction holds, it is a clean, cheap (minutes, pure simulation) demonstration
that T2 as currently gated cannot tell Explanation A from Explanation B, and the repair in R1
is necessary, not merely tidy.

### F2 (Q2 — is T1 = rung 8 reverse-engineered?). Not literally fitted to the data, but chosen with a one-sided reachability calculation and no stated stopping criterion

Three separate observations, escalating:

1. **No power calculation under the disfavoured explanation.** `reachability_and_cost_derived_not_measured`
   computes, and only computes, the probability of *passing* E3 at each future rung **under
   HEUR-INSTR-4 (the favoured explanation)**. It never computes the probability of *failing to
   detect* Explanation B at the same rung — i.e., there is no stated Type-II-style calculation
   ("if the truth is a heavy-tailed distribution with parameter X, T1 has probability Y of
   nonetheless satisfying E3 by rung 8"). Without that companion number, choosing the terminal
   rung by "where does the favoured story's pass probability get comfortably high" is the same
   *shape* of hazard as fitting a threshold to the data you want to pass, even though the
   *mechanism* (a pre-declared doubling count) is legitimately different from moving a band.
   The amendment states the reachability numbers honestly and labels them "derived... not
   measured," but never asks the complementary question, and nothing in `validation_required_before_approval`
   asks V1 to supply it either.

2. **No stated stopping criterion for "how many more doublings."** The only argument offered
   for T1 = 1536 rather than, say, 768 (reachability ≈ 0.51, a coin flip) or 3072 (reachability
   materially above 0.93) is that the seed *values* within a rung are "determined by the rung
   sizes and are not chosen" (E6, `to:`). That is true of the seed values, but it is **not** an
   argument for the *number of rungs to add* — that count (5 further doublings) is a genuine free
   choice the Coordinator made, and the amendment gives no criterion for it (not budget: the cost
   section shows the full ladder to 1536 costs ~11% of the 14400s budget, so there was headroom
   to go further; not a stated power target either). The nearest thing to a criterion is that 1536
   is where the favoured-hypothesis pass probability crosses into the 90s. That is worth naming
   plainly as unexplained, even though I cannot prove it was chosen *because* of that number.

3. **Independent re-derivation of the reachability table finds it partially wrong, in the same
   error class the decision itself caught and fixed elsewhere.** I recomputed
   `p_all13(n_prev) = [2*Φ(0.05 / (1/(2*sqrt(n_prev)))) − 1]^13` for every `n_prev` in the
   corrected nested sequence `DEC-20260810-5aeeaa` itself derives (0.1443, 0.1021, 0.0722,
   0.0510, 0.0361, 0.0255, 0.0180 for `n_prev` = 12, 24, 48, 96, 192, 384, 768):

   | `n_prev` | my recomputed `p_all13` | value claimed for the transition starting there |
   |---|---|---|
   | 24 | 2.98e-6 | **1.2e-4** (claimed for "24→48" — off by ~40×) |
   | 48 | 1.64e-4 | **0.006** (claimed for "48→96" — off by ~36×) |
   | 96 | 5.79e-3 | *(no entry for "96→192" appears in the table at all)* |
   | 192 | 9.47e-2 | 0.095 (claimed for "192→384" — matches to 3 s.f.) |
   | 384 | 5.13e-1 | 0.51 (claimed for "384→768" — matches) |
   | 768 | 9.30e-1 | 0.93 (claimed for "768→1536" — matches) |

   Three of five entries match my recomputation of their own labeled transition almost exactly;
   the other two are each off by more than an order of magnitude from their own label, but land
   close to the value that belongs to the **next** transition — and the missing "96→192" entry
   is exactly the transition whose correct value (5.79e-3) would fill the gap if the first two
   labels were shifted forward by one slot. This is the identical *shape* of error —
   "the value belonging to the next doubling reported under the earlier label" — that
   `DEC-20260810-5aeeaa.adjudication_item_1.arithmetic_check_of_the_input_offered_by_the_archiving_session`
   explicitly diagnosed and corrected in a *different* input to this same decision ("every later
   value is the value belonging to the NEXT doubling"). It appears to recur, apparently uncaught,
   one level downstream, in the decision's own follow-on reachability table — which the amendment
   then repeats byte-for-byte as `reachability_and_cost_derived_not_measured`.

   **Consequence, stated at its correct strength and no further.** This does *not* change the
   qualitative story for the entries I can trace a benign account for: the true reachability at
   24→48 is even smaller than claimed (2.98e-6, not 1.2e-4), which only reinforces "the rule was
   effectively unreachable at 48 seeds"; and the terminal 768→1536 entry — the one figure my Q2
   charge most needed to check — **is not affected** (0.930 matches the claimed 0.93 under a
   straightforward, correctly-indexed computation). But the 48→96 entry (claimed 0.006, recomputed
   1.64e-4) is a **future, not-yet-measured** transition whose reachability is materially
   understated (by ~36×) in the version a reader will use to judge how much extension is
   "reasonable," and the whole exercise shows the "derived by exact arithmetic... not measured"
   framing cannot currently be taken on faith. **Nobody is currently tasked with independently
   re-deriving this table** — V1's charge is skewness/tail-weight of the *existing* 48-seed data,
   not this probability table.

**Required repair (R2).** (i) Add, alongside the existing reachability table, the complementary
probability of falsely satisfying E3 by rung 8 under a stated heavy-tailed alternative (even a
single concrete alternative, e.g. Student-t(df=5) with matched variance, computed or simulated),
so T1's placement can be defended on power, not just on reachability under the favoured story.
(ii) Independently re-derive the full reachability table (restore the missing `n_prev=96` entry;
recheck `n_prev=24` and `n_prev=48`) before this table is relied upon for approval, and correct or
withdraw the two entries flagged above.

### F3 (Q3 — are the fb=11/fb=22 exceedances rigorously dismissed?). Hedged rather than flatly dismissed, but the "expected count 2.4" benchmark is likely the wrong reference class

I independently verified the cited numbers against
`experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/sr3v3-reference-sampling.json`
(rung 3, `n_seeds=48`): fb=11 `max_per_seed_ratio=3.335762761329043` against
`interval_high=3.261372894567769` (matches the amendment's "3.3358... against 3.2614"); fb=22
`max_per_seed_ratio=4.823059054262121` against `interval_high=4.5122533718618385` (matches
"4.8231... against 4.5123"). The amendment's own text is already hedged — "the COUNT is
consistent and proves nothing" and "the one-sided pattern... proves nothing **alone**" — not a
flat "nothing to see here," and it does note both exceeding rows are also the rows failing
stability, with fb=22 carrying the largest sd (0.4675) and the worst rung1→2 change (0.3932).
So the charge that it "pre-judges the answer it wants" is not well supported by the literal
text; the hedge is honest about the analysis it presents.

**But the reference-class calculation it presents is likely biased toward "nothing to see."**
The "expected 13*48/260 = 2.4" figure treats each of the 624 per-seed-row observations as an
*independent, out-of-sample* draw against a *fixed, known* population interval. That is not
what is being measured: the interval at each row is `mean ± z*sd` **fit from the same 48 seeds**
whose own extremes are then checked against it — an in-sample (internally-Studentized) check,
not an out-of-sample one. This is the standard regression-diagnostics distinction between
internally- and externally-Studentized residuals: an extreme observation directly inflates the
sample sd used to build its own bound, which *mechanically suppresses* the in-sample exceedance
rate relative to the nominal tail probability for finite n. If that circularity is material at
n = 48 (plausible; the effect scales roughly as 1/n per point), the **true null-expected count
under in-sample checking is lower than 2.4**, which would make observing 2 exceedances, both
one-sided, on the two rows that also fail stability, *more* surprising than the amendment credits
— i.e., the framing may understate the anomaly rather than overstate it, which is the opposite
direction from "pre-judging toward the answer it wants," but is still a gap in the rigor of the
dismissal.

Separately, the amendment notes the correlation between "row exceeds" and "row fails stability"
qualitatively but never tests it. A Fisher's-exact or permutation test on the 13-row table
("row has ≥1 exceedance" × "row fails E3 at rung 2→3") is a one-line, zero-marginal-cost
computation on data already on disk.

**Required repair (R3, hand to V1).** (i) Recompute the null-expected exceedance count via
leave-one-out (jackknife) cross-validation — refit each row's interval on 47 of its 48 seeds and
check whether the held-out seed's ratio falls outside — which removes the in-sample circularity
and gives a genuine out-of-sample exceedance rate, from data already collected, at zero
additional compute. (ii) Run the exceedance-vs-stability-failure correlation test across the 13
rows explicitly, rather than leaving it as a qualitative aside.

### F4 (Q4 — cheapest control that beats waiting for 1536 seeds). A bootstrap/tail-index reanalysis of the existing 48-seed sample, at zero marginal compute

Per F1, the discriminating signal between Explanation A and B lives in tail shape and rate of
convergence, not in whether E3 eventually passes — and both of those are estimable *today*,
from `sr3v3-reference-sampling.json`'s already-collected rung 1–3 data, without drawing a single
additional seed:

1. **Leave-one-out (jackknife) exceedance rate** (F3 above) — corrects the in-sample circularity
   and gives an honest out-of-sample tail-coverage estimate at the *current* sample size.
2. **Bootstrap confidence intervals on skewness and excess kurtosis**, per row, from the 48
   per-seed ratios — quantifies whether the point estimates D2 will report are distinguishable
   from zero (symmetric, light-tailed) noise.
3. **A tail-index fit** (Hill estimator or a peak-over-threshold GPD fit) on the upper tail of
   each row's 48 ratios — a direct estimate of whether the implied tail is compatible with a
   distribution whose 519/520 quantile sits near the Gaussian-implied `mean + 2.89*sd`, or
   whether it is heavier.
4. **The Fisher's-exact correlation test** named in F3.

All four are pure reanalysis of `sr3v3-reference-sampling.json`, runnable in the same session
that reviews it, and directly answer the question V1 is charged with ("skewness and tail weight
... whether the two upper-side exceedances are consistent with the Gaussian rule") **faster and
more directly than waiting for empirical convergence at 96–1536 seeds would**, since convergence
at higher n mixes together "the point estimate stabilized" (which F1 shows happens under both
explanations) with "the tail shape was actually Gaussian" (which only the diagnostics test).
`validation_required_before_approval.V1` already asks for exactly this analysis on the existing
data — my addition is naming the specific, cheap, already-standard techniques ((1) and (3)
particularly) that make it rigorous rather than a subjective "look asymmetric or heavy-tailed"
read.

### F5 (Q5 — is the 0.5% permissive-direction disclosure adequate?). Arithmetic verified and correct; but "changes NO acceptance region" is contradicted by the amendment's own next paragraph

I independently recomputed the `c4(n)` unbiasing constant
(`c4(n) = sqrt(2/(n-1)) * Γ(n/2)/Γ((n-1)/2)`): `c4(48) = 0.994695`, `c4(1536) = 0.999837`,
matching the amendment's 0.99473 / 0.99984 to the stated precision, and the implied widening
of `1/c4` from rung 3 to rung 8 is 0.514%, matching the claimed "about 0.5%." **The arithmetic
is right and the direction is disclosed correctly** — this is not a fabricated or mis-signed
effect.

**But the framing overclaims.** `E6.what_this_does_not_change` states, in full caps, "IT CHANGES
NO ACCEPTANCE REGION," and the *very next block*, `the_one_direction_of_effect_disclosed_rather_than_hidden`,
states "a LONGER LADDER PRODUCES A MARGINALLY WIDER INTERVAL ON AVERAGE" — a change to the
acceptance region, by the amendment's own admission, just a small, honestly-quantified,
non-data-dependent one. These two claims are in direct tension as written. The fix is textual —
qualify the absolute claim rather than contradict it two paragraphs later — but the deeper point
is that **this is the third of three separately-disclosed effects (F1's "eventual pass regardless
of which hypothesis is true," F2's "terminal rung chosen where the favoured hypothesis's pass
probability is high," and this 0.5% mechanical widening) that all point the same direction: toward
making eventual "stability" both more likely and slightly easier to satisfy as the ladder
lengthens.** No single one is a rule violation — SR4 ("NO WIDENING") is written against
*data-dependent* widening after a failure, and none of these three is data-dependent — but their
directional consistency is exactly the pattern one would expect from a design subtly biased toward
its own preferred outcome, even without any single step crossing a bright line. I recommend this
be named explicitly in the amendment as a cumulative disclosure, not three independent footnotes.

One additional internal-consistency point, offered narrowly: the amendment refuses to apply the
`c4(n)` correction on the grounds that doing so "would change the frozen estimator E1 after
seeing data, which is precisely what is forbidden" — but `c4(n)` is a closed-form, purely
`n`-indexed constant with no free parameter chosen with data in view, exactly analogous to how
`z` itself is "computed at run time from the frozen coverage" and is *not* treated as forbidden
transcription or widening. The amendment is filed, by its own account, "before the affected data
[rungs 4–8] is generated" — the same condition (c) it uses to license E6/E7 in the first place. If
that condition licenses extending the ladder now, it arguably also licenses deciding the `c4(n)`
question now, one way or the other, rather than defaulting to "leave the known bias in, in the
permissive direction, because touching the formula is forbidden." I do not think this is a
required repair — leaving E1 exactly as frozen is defensible and the effect is genuinely tiny —
but the stated *reason* for not correcting it is weaker than the amendment credits, and should not
be relied on as a precedent for refusing a future, larger correction.

---

## Required controls (R1–R5, consolidated)

- **R1.** Make E9's D1/D2 diagnostics *binding* on `accepted_rung`, not merely reported — e.g.,
  "accepted only if E3 is met and D1's shrinkage ratio and D2's exceedance pattern also clear a
  stated bound" — or explicitly relabel a rung that only clears E3 as *provisional*.
- **R2.** (i) Compute or simulate the probability of falsely satisfying E3 by rung 8 under a
  stated heavy-tailed alternative, alongside the existing favoured-hypothesis reachability table.
  (ii) Independently re-derive the full reachability table (`n_prev` = 12, 24, 48, 96, 192, 384,
  768); restore the missing 96→192 entry; correct or explain the 24→48 and 48→96 entries flagged
  in F2.
- **R3.** Hand V1 the leave-one-out (jackknife) exceedance-rate reanalysis and the row-level
  exceedance-vs-stability-failure correlation test, both computable now from
  `sr3v3-reference-sampling.json` alone.
- **R4.** Run the null-object control named in F1 (simulate a matched-variance heavy-tailed
  process — e.g. Student-t(df=5) — through the identical E2/E3/T1/T2/T3 pipeline) and report
  whether it also reaches `accepted_rung` within the declared ladder, and whether D2 flags it.
- **R5.** Correct `E6.what_this_does_not_change`'s "IT CHANGES NO ACCEPTANCE REGION" to
  acknowledge the disclosed ~0.5% `c4(n)` effect, and state the three compounding
  permissive-direction effects (F1, F2, F5) together rather than as isolated footnotes.

None of R1–R5 requires abandoning the extension or reopening E6/E7's basic mechanism; all are
repairs to the *acceptance and reporting logic* layered on top of a mechanism I found to be
legitimately different in kind from interval-widening. This is why the verdict above is a
qualified dissent on the current text, not a rejection of the line of repair.

## Baseline comparison

Not applicable in the usual Pollard-rho/BSGS sense: this experiment characterises an instrument
(a sampling-distribution estimator for a downstream admissibility gate), proposes no algorithm,
and claims no ECDLP-relevant speedup. `claim_tier: toy`, `sota_delta: 0` on every axis, exactly
as the amendment states, and I found nothing that inflates that scope. `dominated_by` is
`not_applicable_no_algorithm_proposed`, consistent with the campaign's own convention for
instrument-only contracts (`RT-20260810-3f7ca3`, GOAL-ENDO-001 BATCH-de621d).

## What I did not attempt

- Any independent verdict on HEUR-INSTR-4 vs `competing_explanation_not_excluded` itself
  (Explanation A vs B on the *existing* 48-seed data) — that is V1's charge, not mine, and my
  task card asks me to attack E6/E7 and the freeze-question argument, not to pre-empt V1's
  statistical finding. F1, F3 and F4 name analyses V1 should consider; they do not substitute
  for V1's own re-derivation.
- Re-deriving `sd_sample_n_minus_1`, `interval_high/low`, or `half_width` for any row beyond the
  fb=11/fb=22 spot-check in F3 (which matched the run record exactly).
- Anything about EXP-ICINV-4d33aa's SR3 v3 gate on its own merits, B1/B2, or any curve-side
  question — out of scope and untouched, per the amendment's own `what_this_amendment_does_not_do`.
- Approving, rejecting, or changing any status. This report changes nothing; `experiments/`,
  `ledger/`, and the amendment file are unedited by this task.

---

```yaml
red_team_report:
  id: RT-20260811-35ab34
  task_id: null  # no TASK-* handoff for this V2 review exists under ledger/handoffs/ at
                  # snapshot 2b9af4d611aeb6034485f7d958271281f1182e53; not fabricated.
  goal_id: GOAL-ENDO-001
  batch_id: BATCH-d7e255
  experiment_id: EXP-INSTR-36c8cf
  target_of_review: experiments/EXP-INSTR-36c8cf/amendments/v2.yaml
  snapshot_commit: 2b9af4d611aeb6034485f7d958271281f1182e53
  verdict: qualified_dissent_repairs_required_before_approval
  claim_under_review: >-
    Changes E6 (five further doubling rungs, 96/192/384/768/1536, estimator formula and
    coverage unchanged) and E7 (declared terminal rung T1=1536, declared terminal outcome T3)
    are jointly offered as making the extension of a failed 5% seed-ladder stability rule
    (E3, wired to falsification criterion F4) discipline-preserving rather than optional
    stopping in a uniform.
  objections:
    - id: F1
      severity: material
      statement: >-
        E3's stopping/acceptance trigger (T2) is satisfied by both HEUR-INSTR-4 (ordinary
        noise) and competing_explanation_not_excluded (heavy-tailed but finite-variance),
        given enough seeds, since 1/(2*sqrt(n_prev)) shrinkage is a general
        finite-variance consistency fact, not specific to Gaussian noise. Passing E3 at
        rung 8 therefore does not by itself discriminate the two hypotheses the amendment
        says it is choosing between; only the non-gating E9 D1/D2 diagnostics can, and
        T2 accepts a rung without requiring them to clear.
      verdict_impact: >-
        blocks approval of the current text; repaired by making D1/D2 binding on
        accepted_rung (R1), not by abandoning the ladder extension.
    - id: F2
      severity: material
      statement: >-
        T1's placement (5 further doublings, to 1536) is justified only by a reachability
        table computed under the favoured hypothesis (~93% pass probability at 768->1536),
        with no companion calculation of the probability of falsely reaching stability
        under the disfavoured heavy-tail explanation, and no stated stopping criterion
        for the doubling count beyond "this is where the favoured story's pass probability
        gets comfortably high." Independent recomputation of that reachability table
        (p_all13(n_prev) = [2*Phi(0.05/(1/(2*sqrt(n_prev))))-1]^13) finds 3 of 5 entries
        match exactly, 2 of 5 (24->48, 48->96) are off by 36-40x from their own labeled
        transition and land close to the NEXT transition's value, and the 96->192 entry
        is missing entirely -- the same "value belongs to the next doubling" error class
        DEC-20260810-5aeeaa explicitly caught and fixed in a different input to the same
        decision. The terminal 768->1536 entry (0.93) is NOT affected and checks out.
      verdict_impact: >-
        does not overturn T1's placement by itself (the terminal-rung figure is correct),
        but the table cannot currently be taken on faith and nobody is tasked with
        re-deriving it; requires R2 before relying on this table for approval.
    - id: F3
      severity: minor_but_unaddressed
      statement: >-
        The amendment's "expected exceedance count 2.4" benchmark for the fb=11/fb=22
        upper-side exceedances treats a self-fit (in-sample) interval check as if it were
        an out-of-sample check against a fixed population interval, which mechanically
        suppresses the true null-expected exceedance rate at n=48. This likely UNDERSTATES
        the anomaly rather than overstating it -- opposite direction from "pre-judging
        toward the null" -- but the amendment's own hedge ("proves nothing alone") is
        correctly cautious rather than falsely dismissive; the gap is rigor, not bias
        toward a conclusion.
      verdict_impact: >-
        hand to V1 as R3 (leave-one-out exceedance rate; Fisher's-exact correlation test
        between exceedance and stability-failure across the 13 rows).
    - id: F4
      severity: informational
      statement: >-
        A bootstrap/jackknife/tail-index reanalysis of the ALREADY-COLLECTED 48-seed
        sample (sr3v3-reference-sampling.json) can estimate tail shape and out-of-sample
        exceedance rate today, at zero marginal compute, and is a faster, more direct
        route to the A-vs-B discrimination V1 is charged with than waiting for empirical
        convergence at 96-1536 seeds, since convergence conflates "point estimate
        stabilized" (happens under both explanations per F1) with "tail shape is Gaussian"
        (only the diagnostics test this).
      verdict_impact: names R3/R4 as concrete, cheap, pre-existing-data analyses for V1.
    - id: F5
      severity: material
      statement: >-
        The disclosed c4(n) bias-correction arithmetic (c4(48)=0.994695, c4(1536)=0.999837,
        ~0.514% widening) is independently verified and correct, and the permissive
        direction is honestly disclosed. But E6.what_this_does_not_change states "IT
        CHANGES NO ACCEPTANCE REGION" in the same block whose own next paragraph discloses
        a ~0.5% widening -- a direct textual contradiction, not merely an imprecision. This
        compounds with F1 and F2: three separately-disclosed, individually-non-violating
        effects that all point toward making eventual "stability" more reachable, evaluated
        in isolation rather than together.
      verdict_impact: >-
        requires R5 (textual correction; state the three effects together). Does not by
        itself invalidate the extension.
  required_controls:
    - >-
      R1. Bind E9 D1 (shrinkage-ratio) and D2 (skewness/exceedance-asymmetry) into the T2
      acceptance condition, or explicitly downgrade a rung that only clears E3 to
      provisional, before EXP-ICINV-4d33aa's SR3 v3 gate may consume accepted_rung.
    - >-
      R2. (i) Compute or simulate the probability of falsely satisfying E3 by rung 8 under
      a stated heavy-tailed alternative (e.g. Student-t, df=5, matched variance), alongside
      the existing favoured-hypothesis reachability table. (ii) Independently re-derive the
      full p_all13(n_prev) reachability table for n_prev in {12,24,48,96,192,384,768};
      restore the missing 96->192 entry; correct or explain the 24->48 and 48->96 entries.
    - >-
      R3. Leave-one-out (jackknife) exceedance-rate reanalysis and a Fisher's-exact /
      permutation correlation test between "row has an out-of-band exceedance" and "row
      fails the E3 stability rule," both computable now from the committed
      sr3v3-reference-sampling.json with zero new compute; hand to V1.
    - >-
      R4. Null-object control: run the identical E2/E3/T1/T2/T3 pipeline against a
      simulated matched-variance heavy-tailed process (e.g. Student-t, df=5) and report
      whether it also reaches accepted_rung within the declared ladder, and whether D2
      flags it -- this directly tests whether T2 as specified can discriminate the two
      live explanations at all.
    - >-
      R5. Correct "IT CHANGES NO ACCEPTANCE REGION" (E6.what_this_does_not_change) to
      acknowledge the disclosed ~0.5% c4(n) effect, and state the compounding of F1, F2
      and F5 explicitly rather than as three isolated footnotes.
  counterexample_or_mutation: >-
    Simulate 13 independent Student-t(df=5) columns (finite variance, heavy tail, matched to
    the observed per-row scale) through E2/E3/T1/T2/T3 verbatim. Prediction: the simulated
    heavy-tailed ladder also eventually satisfies E3 (accepted_rung becomes non-null) within
    the declared 8-rung ladder, demonstrating that E3-passing alone does not separate
    HEUR-INSTR-4 from competing_explanation_not_excluded; the separation, if it exists, must
    come from D2, which does not currently gate anything.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS sense -- this contract characterises an instrument
    (a downstream admissibility gate's reference sampling distribution), proposes no
    algorithm, and claims no ECDLP-relevant speedup. claim_tier toy, sota_delta 0 on every
    axis, consistent with the amendment's own scope statement; nothing found here inflates
    that scope. dominated_by is not_applicable_no_algorithm_proposed, consistent with prior
    instrument-only red-team reports in this campaign (RT-20260810-3f7ca3).
  heuristic_challenges:
    - >-
      HEUR-INSTR-4 (numbered, stated, given a falsification condition tied to E9 D1) is
      correctly declared as a heuristic and not assumed true. The objection is not that it
      is conditional -- a conditional heuristic is not itself an objection per this role's
      prohibitions -- but that its own declared validation route (E3 stability, per
      specification.yaml's heuristic_under_test_note) is satisfied by the alternative it is
      meant to be tested against, given finite variance (F1).
    - >-
      HEUR-INSTR-3 (Gaussian tail adequacy at 259/260 coverage, frozen in amendment v1 G3)
      is the heuristic actually load-bearing for gate correctness, and amendment v1's own
      text already partially conflates its validation with "the rung-wise half-widths of
      E2" (stability), the same conflation F1 identifies as unrepaired in v2's T2. This
      defect predates amendment v2 but becomes operationally consequential only once T2
      determines when a rung is accepted.
  cost_model_challenges:
    - >-
      The ~1.6e3 s / ~11% of the 14400 s budget estimate for the full 8-rung ladder is
      correctly labeled a linear-in-seeds extrapolation from one 128.234 s run on an
      oversubscribed host, and is not treated as measured. Not disputed here.
    - >-
      Not a cost-model gap so much as a SEQUENCING gap: R3/R4 (bootstrap/jackknife
      reanalysis of already-collected data, and a synthetic null-object simulation) are
      strictly cheaper than the ~1.6e3 s of new compute the ladder extension requires, and
      could resolve much of the A-vs-B mechanism question before any of that compute is
      spent. The amendment does not sequence them first.
  reduction_and_scope_challenges:
    - >-
      Scope is not inflated. claim_tier toy is held throughout; no curve-side, within-class,
      between-class, or ECDLP conclusion is asserted anywhere in v2; B1/B2 blockers are
      correctly left untouched; EXP-ICINV-4d33aa stays paused and unedited by this file.
      Verified against the amendment's own what_this_amendment_does_not_do block.
  proof_architecture_challenges:
    - >-
      Quantifier order: E3/T2 is stated as "the interval half-width changes by less than
      5% ... at EVERY one of the thirteen rows" (universal over rows, existential over the
      rung at which it first holds). The failure is one quantifier deeper: T2 silently
      treats "exists a rung at which this universal holds" as sufficient to conclude
      "the reference distribution is Gaussian-tailed at 259/260 coverage" -- a claim the
      stated quantifiers do not license and that only D1/D2 (non-binding) could support.
    - >-
      Observation-fiber attack: holding "E3 passes at rung r" fixed and varying the true
      per-row distribution (Gaussian vs finite-variance heavy-tailed) places instances on
      both sides of "HEUR-INSTR-2/4 validated" -- both distributions can produce a passing
      E3 at large enough r. The missing separator is exactly D1/D2, which the amendment
      already collects but does not gate on.
  narrowest_supported_statement: >-
    Amendment v2 changes E6/E7 are mechanistically distinct from the interval-widening
    defect this campaign already corrected in EXP-ICINV-4d33aa (no acceptance-boundary
    movement in response to observed failure, filed before the governed data exists, a
    bounded and pre-committed terminal outcome). They are NOT YET sufficient, as specified,
    to deliver what the amendment claims for them: satisfying E3 at any rung up to and
    including the declared terminal rung 1536 does not by itself discriminate HEUR-INSTR-4
    from competing_explanation_not_excluded, because both predict eventual E3-passage under
    finite variance, and the diagnostics that could discriminate (E9 D1/D2) do not gate
    T2's accept/stop decision. The terminal-rung reachability figure most relevant to this
    review (93% at 768->1536) is independently verified correct; two earlier entries in the
    same table (24->48, 48->96) are independently found to be in error by 36-40x, in the
    same error class the decision itself caught elsewhere, though this does not change the
    qualitative "unreachable at 48 seeds" conclusion those entries support. This is a
    finding about E6/E7's acceptance and reporting logic, not a finding about HEUR-INSTR-4,
    H-INSTR-444c7b, H-ICINV-6c7920, or any curve, class, isogeny, or prime, at any scale, in
    either direction.
  next_concrete_action: >-
    Before any Coordinator approval decision on amendment v2: (1) run R3 and R4 -- both
    zero-marginal-cost reanalyses of data already on disk (jackknife exceedance rate,
    exceedance/stability-failure correlation test, and a Student-t(df=5) null-object
    simulation through the identical E2/E3/T1/T2/T3 pipeline) -- and report whether the
    null-object control also reaches accepted_rung within 8 rungs; (2) independently
    re-derive the reachability table per R2 and correct the flagged entries or explain the
    discrepancy; (3) revise E7's T2 so that accepted_rung requires D1/D2 to clear a stated
    bound, not E3 alone, or explicitly relabel an E3-only pass as provisional; (4) correct
    the "IT CHANGES NO ACCEPTANCE REGION" overclaim in E6. Absent these, this report is a
    dissent under the amendment's own validation_required_before_approval V2 clause and
    should block approval of the current text pending a revised E7, per that clause's own
    terms ("A DISSENT FROM EITHER BLOCKS APPROVAL... it stands until a new Coordinator
    decision supersedes it on the merits").
  artifact_paths:
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/validation_v2_redteam_report.md
  records_read_at_snapshot:
    - experiments/EXP-INSTR-36c8cf/amendments/v2.yaml
    - experiments/EXP-INSTR-36c8cf/amendments/v1.yaml
    - experiments/EXP-INSTR-36c8cf/specification.yaml
    - ledger/decisions/DEC-20260810-5aeeaa.yaml
    - experiments/EXP-ICINV-4d33aa/amendments/v2.yaml
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/sr3v3-interval-stability.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/sr3v3-reference-sampling.json
    - AGENTS.md
    - agents/red-team.md
    - .claude/agents/red-team.md
  independent_arithmetic_performed:
    - >-
      Recomputed c4(n) for n in {12,24,48,96,192,384,768,1536} via
      sqrt(2/(n-1))*Gamma(n/2)/Gamma((n-1)/2); confirmed c4(48)=0.994695, c4(1536)=0.999837,
      and the ~0.514% implied widening of 1/c4 from rung 3 to rung 8, matching the
      amendment's stated ~0.5%.
    - >-
      Recomputed p_all13(n_prev) = [2*Phi(0.05/(1/(2*sqrt(n_prev))))-1]^13 for n_prev in
      {12,24,48,96,192,384,768} against the amendment's reachability_and_cost_derived_not_measured
      table; found 3 of 5 entries match to 3 significant figures and 2 of 5 are off by
      36-40x from their own labeled transition (see F2).
    - >-
      Confirmed fb=11 and fb=22 rung-3 (n_seeds=48) figures directly from
      sr3v3-reference-sampling.json: max_per_seed_ratio 3.335762761329043 vs
      interval_high 3.261372894567769 (fb=11); max_per_seed_ratio 4.823059054262121 vs
      interval_high 4.5122533718618385 (fb=22) -- both match the amendment's cited figures
      exactly.
  claim_tier: toy
  sota_delta: 0
  dominated_by: not_applicable_no_algorithm_proposed
  inference:
    requested_policy: review-adversarial
    resolved_model_id: claude-sonnet-5
    reasoning_effort: xhigh
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness cannot resolve the policy aliases in
      orchestration/model-policies.yaml; every alias falls back to the one model the session
      runs on (AGENTS.md rule 11; CLAUDE.md "Model policy note"). Recorded, never silently
      substituted.
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: >-
      No python3 -m orchestration.adapter doctor --probe receipt was obtained for this
      session. The identifier above is the session's declared identity, not a probe result.
    independent_session: true
    independence_limitation: >-
      This review and DEC-20260810-5aeeaa / amendment v2 resolve to models on the same
      backend (this harness has only one). "Independent" here means independent context and
      a fresh adversarial reading of a committed snapshot, not independent judgement from a
      different model -- the standing limitation on every review in this campaign under the
      suspended closure quorum, recorded rather than worked around.
  authority_note: >-
    This report changes no research status and approves or rejects nothing. amendment v2,
    DEC-20260810-5aeeaa, and every other cited record are unedited and uncommitted by this
    task. Approval, amendment, or withdrawal of EXP-INSTR-36c8cf amendment v2 is a
    successor Coordinator act after both V1 and this V2 report are read; per the amendment's
    own text, a dissent from either blocks approval until superseded on the merits. Nothing
    here is durable evidence until a Coordinator archives it.
```
