# Red-team review: R3/R4 controls (RUN-INSTR-r3r4-nullobj-d3efd7)

`RT-20260811-cb3211` · GOAL-ENDO-001 · BATCH-d7e255 · EXP-INSTR-36c8cf · `TASK-20260811-bc336d`

Read at snapshot `031fab32ea3b8f4cf4ff5f5ac7ddbda5254c5d6f` (verified reachable, `git log` confirms it as HEAD of
`claude/ecdlp-endomorphism-analysis-4m2w3z`). Independently re-derived two things beyond reading — a scale-invariance
proof of the R4 pipeline, empirically confirmed by re-running `sr3v3.interval_for_rung`/`stability_check` at
`loc=0, scale=1` on the identical RNG stream, and a re-aggregation of the Gaussian arm's own `exceed_total_at_terminal`
distribution from `r4-gaussian-calibration-optional.json`, neither of which required touching the arithmetic the
parallel Validator session was checking independently.

## Direct answers

**1. Does 18.8% confirm or complicate F1?** Both, but not symmetrically, because F1 made two distinct claims that this
number separates. As a claim of *existence* ("a heavy-tailed, finite-variance alternative also reaches
`accepted_rung` within the declared 8-rung ladder"), 18.8% (94/500) is an unambiguous confirmation — not a boundary
case, not noise, and structurally exactly where the theory predicts (100% of first-accepts land at rung 7 or 8, never
earlier, consistent with "same asymptotic law, slower constant"). As a claim of *magnitude*, F1's text never
committed to a number — "eventually satisfies E3" is existential, not "usually" — so 18.8% doesn't complicate the
claim as textually written; it complicates only a stronger, unstated gloss a reader might attach to "eventually." The
steelman that this "weakens" the dissent because 81.2% correctly fails to accept is real and should be recorded, but
it proves a *different* proposition (T1=1536 has non-trivial power against *this* alternative) than the one F1
asserted (E3-passage alone doesn't discriminate). Both are true at once. On a principled threshold: there isn't one,
because neither the amendment nor V2's dissent nor this run pre-registered an acceptable false-accept rate. R2(i) —
still undischarged — is exactly the missing piece that would let a number like 18.8% be judged pass/fail; citing the
conventional 80%-power / 20%-Type-II heuristic post hoc (18.8% sits just under that line) is informative context
only, not a standard this campaign adopted in advance, and is flagged as such rather than as a verdict.

**2. Matched-variance design — circular, apples-to-apples, or neither?** Neither steelman is the sharpest answer.
`sr3v3.interval_for_rung` (mean ± z·sd) and `sr3v3.stability_check` (`rel = abs(c_hw - p_hw)/p_hw`) are exactly
invariant under positive affine transforms of the input, and so is the exceedance check (`max > mean+z·sd`).
Confirmed not just by algebra but by re-running the identical replication logic with `loc=0, scale=1` for all 13 rows
against the *same* `SeedSequence(314159265)` stream used by the real run: the first 50 replications' `accepted_rung`
sequence and `exceed_total` sequence came back **byte-identical** to the matched-variance arm. So the "own row's
observed rung-3 sd/mean" choice — specified in the handoff, not invented by the executor — is provably inert to
every headline number in this run. The circularity worry (contaminated 48-seed sd feeding back into the control) and
the apples-to-apples defense are both moot: only the *shape* (Student-t(5) vs Gaussian, both standardized) and sample
size matter. This is worth correcting in any future citation of this run, since "matched to the row's own scale,
apples-to-apples" implies the scale choice did methodological work it did not do.

**3. Does 26/26-always strengthen R1, or cut both ways?** It cuts both ways, and the run's own uninterpreted
Gaussian-arm artifact (`r4-gaussian-calibration-optional.json`) settles which reading is closer to right. Recomputed
the Gaussian arm's `exceed_total_at_terminal` distribution: mean 21.6/26 (≈83%), and **61 of 485 accepted
replications (12.6%) also hit the literal maximum, 26/26**. So a naive binding rule "reject if `exceed_total == 26`"
would carry a ~12.6% false-rejection rate against the matched-variance (approximately-true-null) arm — not the clean
bright-line separator the "100% every time" framing invites a reader to assume. What *does* survive is the
incidence-rate contrast itself (100% vs 12.6% — an 8× difference, genuinely discriminating in aggregate) and a
within-arm signal also found: the Gaussian arm's 15 *non*-accepted replications have higher mean exceedance
(25.27/26) than its accepted ones (21.5/26), i.e., exceedance and non-acceptance already correlate even under the
(approximate) null. Net effect on R1: this data supports binding *some* form of D1/D2 signal into T2 (the
correlation is real and directionally useful), but it argues against R1 being implemented as a fixed threshold at
the observed maximum — that specific rule is undermined by the same data that would be cited to justify it. This is
a genuinely open design question, not one this run (correctly, per its own scope) tries to answer.

**4. Cost/scope check.** No hidden cost or scope creep found: 68s/1800s, no EC arithmetic, `claim_tier: toy`/
`sota_delta: 0` held throughout, and the optional Gaussian arm was pre-authorized by the handoff and correctly
labeled supplementary. The one real gap is a two-line one the handoff invited but the executor didn't supply: at
n=500, SE(p̂=0.188) ≈ 1.7 percentage points (95% CI ≈ [15.4%, 22.2%]); SE(p̂=0.970) ≈ 0.76pp. 500 is amply sufficient
for the *contrast* reported (a 78-point gap swamps a 3.4-point margin) but the bare "18.8%" invites more precision
than is stated to be attached to it, and this is a cheap, missing addition.

**5. Overclaim scan.** No line asserting anything about HEUR-INSTR-4, `competing_explanation_not_excluded`, or the
amendment's fate beyond observation, in either the execution report or `ctrl_r3r4.py`'s docstrings/comments — the
authority-note and per-analysis hedges are consistently present and accurate. The one framing risk (not a textual
overclaim) is the sentence: *"this is a genuine, reproducible property of the Student-t(df=5) heavy tail at this
sample size under an in-sample-fit interval, not an artifact of this module's code"* (execution report, "R4"
section). It is true as far as it goes and was independently checked (the executor's own 200-trial spot check and
the Coordinator's snapshot-commit message separately confirm it via the Gaussian arm's non-zero variance), but by
not juxtaposing it against the Gaussian arm's own 12.6%-at-max / 83%-mean incidence in the same breath, it risks
being read as attributing more distinctiveness to the property than the run's own (uncited-in-that-paragraph) data
support.

**6. Update to RT-20260811-35ab34's narrowest_supported_statement.** That statement was structural: D1/D2 "do not
gate T2's accept/stop decision," full stop, argued analytically. This run does not change that fact (correctly — R1
is explicitly undischarged) but sharpens its *consequence*: the gap it leaves open is now known to be **empirically
material for at least one plausible alternative** (18.8% false-accept at the declared terminal rung, not negligible,
not near-certain), and the diagnostic that could close the gap is now known to be **imperfect, not just absent** — it
separates the two shapes at the aggregate/incidence level but not at the level of a simple fixed threshold on any
single replication. The narrowest statement this run's results support **on their own**: for the tested alternative
(Student-t(df=5), shape only — location/scale are provably inert to every reported statistic here, confirmed both
analytically and by a bit-identical re-run at `loc=0, scale=1`), the amendment's current, unrepaired E3-only
acceptance rule (T2) admits the alternative in 94/500 = 18.8% (95% CI ≈[15.4%, 22.2%]) of independent replications at
the declared terminal rung, versus 485/500 = 97.0% for a matched-shape Gaussian counterpart; the non-gating
exceedance diagnostic sits at its structural maximum in 100% of the alternative's accepted replications but also in
12.6% (61/485) of the Gaussian arm's accepted replications, so while it carries real discriminating signal in
aggregate, a fixed-threshold instantiation of R1 would misfire against the well-behaved arm at a non-negligible
rate — R1 remains necessary but its specific design is not yet solved by this run, and no acceptable false-accept-
rate target exists anywhere in this campaign's records against which 18.8% could be judged sufficient or
insufficient.

---

```yaml
red_team_report:
  id: RT-20260811-cb3211
  task_id: TASK-20260811-bc336d
  goal_id: GOAL-ENDO-001
  batch_id: BATCH-d7e255
  experiment_id: EXP-INSTR-36c8cf
  target_of_review: experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/
  snapshot_commit: 031fab32ea3b8f4cf4ff5f5ac7ddbda5254c5d6f
  claim_under_review: >-
    Whether R4's empirical results (18.8% accept-by-rung-8 for a Student-t(df=5)
    null-object control vs 97.0% for a matched-shape Gaussian control, with the
    non-gating exceedance diagnostic at its structural maximum in every accepted
    Student-t replication) confirm RT-20260811-35ab34 F1's prediction, and
    whether the run's framing (a "matched-variance" design; "26/26 always" as a
    property of the heavy tail) supports what it is used to support, independent
    of the underlying arithmetic (which a parallel Validator session checks).
  verdict: >-
    R3/R4 executed faithfully to their specification and stayed within scope
    (claim_tier toy, no interpretation offered, correctly). But two framing
    risks would let a reader draw stronger conclusions than the data license,
    and one design-choice defense in the task's own framing ("matched
    variance, apples-to-apples") is provably moot, not merely debatable. None
    of this blocks anything -- this run authorizes nothing and I am not
    dissenting from a claim this run does not make -- but a v3 amendment or a
    Coordinator decision citing this run's headline numbers needs the
    corrections below to avoid inheriting an artifact of framing as if it
    were a finding.
  objections:
    - id: F1-scope
      severity: material
      statement: >-
        18.8% confirms F1's claim of EXISTENCE (a heavy-tailed alternative
        reaches accepted_rung within the declared ladder, exclusively at
        rungs 7-8, matching the "slower convergence, same asymptotic law"
        theory) but does not, and was never claimed to, confirm any
        particular MAGNITUDE -- F1's text is existential ("eventually"), not
        a rate claim. No pre-registered false-accept threshold exists
        anywhere in this campaign (the gap F2 already named, via R2(i),
        remains open) against which 18.8% could be judged sufficient or
        insufficient to settle the dissent either way.
    - id: matched-variance-is-inert
      severity: material
      statement: >-
        interval_for_rung (mean +/- z*sd) and stability_check
        (rel = |c_hw-p_hw|/p_hw) are exactly invariant under positive affine
        transforms of the input, and so is the exceedance check
        (max > mean+z*sd). Confirmed empirically: re-running the identical
        replication logic with loc=0, scale=1 for all 13 rows against the
        SAME SeedSequence(314159265) stream gives byte-identical
        accepted_rung and exceed_total sequences to the matched-variance arm
        for the first 50 replications. The "matched to the row's own
        observed scale, apples-to-apples" framing (handoff wording) implies
        this choice does methodological work; it provably does not -- only
        distribution SHAPE and sample size affect any reported number. This
        should be corrected wherever this run is cited as a controlled
        comparison, not because the result is wrong but because the stated
        reason it is controlled is wrong.
    - id: exceedance-diagnostic-not-clean-binary
      severity: material
      statement: >-
        "The diagnostic that gates nothing is at its maximum every time it
        accepts" (Student-t arm, 500/500) is true but incomplete without its
        own artifact's Gaussian-arm companion: 61/485 (12.6%) of the
        Gaussian arm's ACCEPTED replications also hit the literal maximum
        (26/26), and the Gaussian arm's mean exceedance even when not
        maximal is 21.6/26 (83%). A fixed-threshold instantiation of R1
        ("reject if exceed_total==26") would misfire against the
        approximately-true-null arm at ~12.6%, not zero. The incidence-RATE
        contrast (100% vs 12.6%) is real and useful; the implied clean
        binary separator is not.
    - id: no-reported-precision
      severity: minor
      statement: >-
        18.8% (94/500) and 97.0% (485/500) are reported to 3 significant
        figures with no binomial confidence interval. SE(0.188, n=500) ~=
        1.7 percentage points (95% CI ~= [15.4%, 22.2%]); SE(0.970, n=500)
        ~= 0.76pp. The 78-point gap between arms makes this immaterial to
        the qualitative contrast, but a reader treating "18.8%" as precise
        to the decimal, rather than as a point estimate with an ~3.4-point
        margin, would be over-trusting the number as reported.
    - id: uncredited-cross-check
      severity: informational
      statement: >-
        The Gaussian arm's 97.0% accept-by-rung8 rate is a reasonably close,
        independent empirical cross-check of the amendment's own claimed
        ~93% reachability figure for the 768->1536 transition (already
        independently verified correct by RT-20260811-35ab34 F2). Not
        identical quantities (cumulative-by-rung8 vs single-transition
        probability) but directionally consistent -- a minor positive
        finding for the amendment's own arithmetic, present in this run's
        data but not narrated as such.
    - id: framing-risk-by-omission
      severity: informational
      statement: >-
        The execution report's "genuine, reproducible property of the
        Student-t(df=5) heavy tail" line (re: 26/26-always) is accurate and
        was independently double-checked (both by the executor's own
        200-trial spot check and the Coordinator's snapshot-commit message),
        but stating it without the Gaussian arm's own 12.6%-at-max
        comparison in the same breath risks a reader inferring more
        exclusivity/discriminating power for the property than the run's
        own uninterpreted data support.
  required_controls:
    - >-
      Report the binomial 95% CI alongside both accept-by-rung8 fractions
      (18.8% +/- ~3.4pp; 97.0% +/- ~1.5pp) wherever this run's headline
      numbers are cited going forward.
    - >-
      Any future citation of "26/26 always" (Student-t arm) must be
      accompanied by the Gaussian arm's own exceed_total distribution
      (mean 21.6/26, 12.6% at literal max) from the SAME run's own
      r4-gaussian-calibration-optional.json -- already collected, zero new
      compute, not currently surfaced in the execution report's own R4
      section.
    - >-
      Before a v3 amendment drafts R1 as a specific binding rule, require it
      to be evaluated against BOTH arms' diagnostic distributions (not just
      the Student-t arm's 100% figure), since a fixed threshold at the
      observed maximum has a ~12.6% false-positive rate against this run's
      own matched-shape Gaussian control.
    - >-
      Correct "matched-variance ... apples-to-apples" framing in any
      successor citation: the per-row scale/location choice is provably
      inert to every reported number in this run (proof + empirical
      re-verification above); only distributional shape and sample size
      matter. State this plainly rather than implying the scale-matching
      did comparability work.
    - >-
      R2(i) (still undischarged, per DEC-20260811-a4c7ec.next_actions)
      remains the correct place to pin down a PRE-DECLARED acceptable
      false-accept-rate target; this run's 18.8% is strong empirical
      context for R2(i) but is not a substitute for it, exactly as the
      handoff's own what_this_does_not_do already states for R2 generally.
  counterexample_or_mutation: >-
    Executed, not merely proposed: re-ran draw_null_object_replication's
    logic with loc=0, scale=1 for all 13 rows against the identical
    numpy.random.SeedSequence(314159265) stream the real run used (first 50
    replications). Result: accepted_rung and exceed_total sequences are
    BYTE-IDENTICAL to the matched-variance arm's own first 50 replications.
    This is the cheapest possible discriminating control for the
    circularity-vs-apples-to-apples question (Q2): it required no new
    committed artifact, only reading the frozen interval_for_rung/
    stability_check formulas (both exactly affine-invariant) and a
    zero-marginal-cost re-run, and it settles the debate as moot rather than
    picking a side.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS sense -- this run characterises
    an instrument's own acceptance rule against a synthetic alternative, no
    algorithm is proposed, claim_tier toy, sota_delta 0 on every axis, and
    nothing here inflates that scope. dominated_by
    not_applicable_no_algorithm_proposed, consistent with
    RT-20260811-35ab34's own framing of this same experiment thread.
  heuristic_challenges:
    - >-
      HEUR-INSTR-4's declared validation route is still E3 alone in the
      CURRENT (v2, unrepaired) amendment text; this run does not and cannot
      change that (correctly not attempted -- R1 stays undischarged, exactly
      as the execution report states).
    - >-
      The new empirical quantity this run supplies (an 18.8% false-accept
      rate against one specific alternative) has no declared
      falsification/acceptance threshold to be measured against -- an
      omission that predates this run (RT-20260811-35ab34 F2) and is not
      remedied by producing the number itself.
  cost_model_challenges:
    - >-
      No hidden cost or scope creep found. 68.008s wall / 1800s cap (3.8%),
      no EC arithmetic, 79.7MB peak RSS against an 8GB cap. The optional
      Gaussian arm was pre-authorized in the handoff, correctly labeled
      supplementary, and did not crowd out R3/R4's own required text.
    - >-
      500 replications per arm is adequate for the CONTRAST reported (a
      78-point gap against an ~3.4-point margin of error) but the bare point
      estimates are reported without their confidence interval, a minor
      completeness gap given the handoff explicitly invited "a few hundred
      is almost certainly enough" as a judgment call that should have been
      accompanied by the two-line precision argument it now retroactively
      supports.
  reduction_and_scope_challenges:
    - >-
      Scope is not inflated anywhere in this run: claim_tier toy and
      sota_delta 0 are held throughout, no hypothesis status is touched, and
      both the module and the execution report correctly and repeatedly
      disclaim interpretation against HEUR-INSTR-4 or the amendment's
      approval. Not a curve-side, within-class, or between-class claim of
      any kind; no affected-vs-safe scheme scope applies at this tier.
  proof_architecture_challenges:
    - >-
      Quantifier-order sharpening: V2's F1 argued analytically that "exists
      a rung r <= 1536 such that E3 holds at r" does not entail
      "HEUR-INSTR-4 is preferred," since both explanations can satisfy the
      existential asymptotically. This run makes the existential's
      SATISFIABILITY RATE explicit and finite: P(exists r<=8 : E3 met | true
      shape = Student-t(5)) = 0.188 (empirical, one specific alternative),
      turning an asymptotic/qualitative argument into a finite-sample
      quantitative one, without resolving what rate would be acceptable.
    - >-
      Observation-fiber attack, empirically instantiated rather than merely
      argued: holding "accepted_rung is non-null at rung <=8" fixed and
      varying the true generating shape (Gaussian vs Student-t(5)) places
      94/500 Student-t replications and 485/500 Gaussian replications in the
      SAME accepted fiber. The missing separator (D1/D2-style diagnostics)
      still does not gate T2, confirmed by construction here rather than
      argued analytically as in RT-20260811-35ab34; and the separator itself
      is shown to be imperfect (12.6% false-positive on the max-exceedance
      signal against the Gaussian arm), so the missing ingredient is not
      merely "absent" but also "not yet well-specified even if added."
  narrowest_supported_statement: >-
    RT-20260811-35ab34's structural finding (D1/D2 do not gate T2's
    accept/stop decision) is unchanged by this run -- correctly, since R1
    remains undischarged. What this run adds, on its own results,
    independent of that prior report: for the Student-t(df=5) alternative
    tested (shape only -- location/scale are provably inert to every
    reported statistic here, proved analytically from interval_for_rung/
    stability_check's affine invariance and confirmed by an independent
    byte-identical re-run at loc=0/scale=1 on the same RNG stream), the
    amendment's current, unrepaired E3-only acceptance rule (T2) admits the
    alternative in 94/500 = 18.8% (95% CI ~=[15.4%, 22.2%]) of independent
    replications at the declared terminal rung T1=1536, versus 485/500 =
    97.0% for a matched-shape Gaussian counterpart (95% CI ~=[95.5%,
    98.5%]). The non-gating exceedance diagnostic sits at its structural
    maximum (26/26) in 100% of the Student-t arm's accepted replications but
    ALSO in 61/485 = 12.6% of the Gaussian arm's accepted replications (mean
    21.6/26 even when not literally maximal), so it carries real
    discriminating signal in aggregate incidence but would not function as a
    clean binary gate at a fixed threshold. No pre-registered acceptable
    false-accept-rate exists anywhere in this campaign's records against
    which 18.8% could be judged to settle F1's dissent in either direction.
    This is a finding about this run's own numbers and framing, not a
    finding about HEUR-INSTR-4, H-INSTR-444c7b, H-ICINV-6c7920, or any
    curve, class, isogeny, or prime, at any scale, in either direction.
  next_concrete_action: >-
    Before any v3 amendment drafts R1's binding rule: (1) add the binomial
    CI to R4's reported rates in the execution report or a superseding note;
    (2) write the Gaussian arm's own exceed_total distribution
    (61/485=12.6% at max, mean 21.6/26) into the same record that cites
    "26/26 always," since it is already collected in
    r4-gaussian-calibration-optional.json and changes what a reader should
    conclude about D2's discriminating power; (3) correct the
    "matched-variance ... apples-to-apples" framing to state plainly that
    the scale/location choice is inert to every reported number (proof
    above), so a future reader does not credit that design choice with
    comparability work it did not do; (4) task R2(i) (still open) with
    supplying the missing pre-declared false-accept-rate target that alone
    would let 18.8% actually decide anything, rather than treating this
    run's number as self-interpreting.
  artifact_paths:
    - ledger/handoffs/TASK-20260811-bc336d.yaml
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/execution_report_r3r4.md
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/validation_v2_redteam_report.md
    - ledger/decisions/DEC-20260811-a4c7ec.yaml
    - experiments/EXP-INSTR-36c8cf/amendments/v2.yaml
    - harness/exp_instr_36c8cf/ctrl_r3r4.py
    - harness/exp_instr_36c8cf/sr3v3.py
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/manifest.yaml
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/r4-student-t5-nullobject.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/r4-gaussian-calibration-optional.json
  independent_arithmetic_performed:
    - >-
      Re-derived the Gaussian arm's exceed_total_at_terminal histogram from
      r4-gaussian-calibration-optional.json's own records: 61/485 (12.6%)
      accepted replications at the literal maximum (26), mean 21.6/26 across
      all 500, mean 21.5/26 among accepted vs 25.27/26 among the 15
      not-accepted -- none of these breakdowns appear in the execution
      report's own text.
    - >-
      Independently re-ran draw_null_object_replication's logic (frozen
      sr3v3.interval_for_rung / stability_check, unmodified) with loc=0,
      scale=1 substituted for the matched per-row mean/sd, against the
      identical numpy.random.SeedSequence(314159265) stream, for the first
      50 replications: accepted_rung and exceed_total sequences came back
      byte-identical to the matched-variance arm's own values, confirming
      the affine-invariance argument empirically, not just algebraically.
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
      orchestration/model-policies.yaml; every alias falls back to the one
      model the session runs on (AGENTS.md rule 11; CLAUDE.md "Model policy
      note"). Recorded, never silently substituted.
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: No adapter probe receipt exists for this session.
    independent_session: true
    independence_limitation: >-
      This review and the run/decision it reads resolve to models on the
      same backend (this harness has only one). "Independent" here means
      independent context and a fresh adversarial reading of a committed
      snapshot, not independent judgement from a different model.
  authority_note: >-
    This report changes no research status and approves or rejects nothing.
    RUN-INSTR-r3r4-nullobj-d3efd7, the execution report, amendment v2, and
    every other cited record are unedited and uncommitted by this task.
    Interpretation of R3/R4's results against HEUR-INSTR-4 or amendment v2's
    approval is a Coordinator act on a later ledger archive, after this
    report and the parallel Validator's technical check are both read.
    Nothing here is durable evidence until a Coordinator archives it; this
    report is not written to a file and is not committed, per this task's
    explicit instruction.
```
