# RED TEAM REPORT — TASK-20260815-19c716

```yaml
red_team_report:
  id: RT-20260815-19c716
  id_note: >-
    RT-* is not a ledger record class and mints nothing; this identifier
    mirrors the task id, matching this goal's own established precedent
    (RT-20260815-85e02a for TASK-20260815-85e02a). tools/allocate_id.py
    registers no --next type for it, so no scan-free minting path applies and
    no collision surface is created.
  task_id: TASK-20260815-19c716
  goal_id: GOAL-MLKEM-005
  batch_id: BATCH-0d5018
  role: red-team
  archived_by: TASK-20260815-fa0ead

  contract_source: >-
    THERE IS NO TASK-CARD FILE AND NO ledger/handoffs/ ENVELOPE FOR THIS TASK,
    AND NONE WAS INVENTED. Verified directly:
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/tasks/ contains only
    TASK-20260815-f14d3c (the producer), and `ls ledger/handoffs/ | grep
    19c716` returns nothing. The binding contract for this review is the
    `handoff` block of TASK-20260815-19c716 inside
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/dispatch_queue.json,
    read from the committed working tree (that file is clean on this branch;
    `git status --porcelain -- coordination/goals/GOAL-MLKEM-005/` reports only
    this review's own untracked write_scope directory). Recorded as a fact
    rather than papered over.

  claim_under_review: >-
    TASK-20260815-f14d3c's own per-basis d=512 precision bisections and
    full-BKZ-tour reattempts, snapshot-archived alone by TASK-20260815-02b01b at
    commit 856ff0a6ee4d3998e72aca570a4e5d31d577b952 (parent
    b325e87382477c1fb3cf4aa59626ccdb1ad3b110): (1) two genuine, separate,
    1-bit-resolution isolated-LLL-step bisections within the CTRL-1 (69,100]
    window, determining 75 bits at (d=512, beta=55, seed=452658293) and 73 bits
    at (d=512, beta=70, seed=915347894); (2) a full BKZ tour re-attempted at
    each cell's OWN newly-bisected precision under
    PER_BASIS_FEASIBILITY_CAP_V3=14400s, giving ERROR
    (`ReductionError: infinite loop in babai`) at 2502.74s for beta=55 and
    NOT_COMPUTED (cap exceeded, SIGTERM, returncode -15) at 14400.08s for
    beta=70; (3) n_cells_completed = 0 of 2; (4) explicit statements that
    CTRL-3's costlier full-tour-level precision search was NOT performed, that
    (d=512, beta=40) was not re-attempted, and that (d=256, *) was not touched.
    CLAIM TIER TOY throughout. The producer makes no ML-KEM security statement
    and no C1/C2 statement, and this review makes none either.

  verdict: >-
    THE PACKAGE IS ACCEPTED AS AN HONEST, INTERNALLY CONSISTENT, NOTARIZED
    MEASUREMENT, AND ITS HEADLINE READING IS REJECTED AS TOO BROAD.
    The specific failure mode this task exists to catch — a precision shared or
    borrowed between the two bases — IS NOT PRESENT: the two bisections are
    genuinely independent, replay correctly from each basis's own trials alone,
    use disjoint seeds, and each reattempt used its own basis's own value
    (probe2, section A: replay_matches_report true for both, seed_sets_disjoint
    true, no_cross_basis_precision_reuse true). CTRL-2 IS SATISFIED. CTRL-3's
    first half is satisfied PROCEDURALLY for both cells but produced a
    mathematical outcome for only ONE of them, and CTRL-3's costlier half is
    honestly left undone and correctly labelled as such. No cell cleared, so
    there are no certificate or basis-quality figures to challenge.
    WHAT MUST NOT BE READ FROM IT: "0/2 cells cleared" is NOT "two measured
    failures." It is ONE measured full-tour failure at a precision the goal's
    own promoted finding KN-FIND-f54a82 already predicts is calibrated at the
    wrong level, plus ONE non-measurement (a wall-clock timeout, which
    AGENTS.md rule 5 and CLAUDE.md rule 3 make infrastructure signal and never
    negative mathematical evidence). And the same recorded numbers, decomposed,
    contain a large, monotone, MEASURED precision response at the full-tour
    level that the writeup does not compute and reads with the opposite sign.
    DEC-20260815-201633's escalation conditional is therefore NOT DISCHARGED by
    this batch, and naming DEC-20260814-4ac30a's escalation branches ripe on
    this record would be premature closure in the exact sense
    docs/inventor-protocol.md section 4 defines.

  notarization_chain_check: >-
    CHECKED IN BOTH DIRECTIONS WITH GIT PLUMBING, INDEPENDENTLY, WITHOUT
    RELYING ON THE DISPATCHING SESSION'S PRE-DISPATCH VERIFICATION. Raw output:
    probes/probe1_notarization_chain_both_directions_output.json.
    FORWARD (declared -> commit): `git cat-file -t 856ff0a6e` = commit;
    `git rev-parse 856ff0a6e^` = b325e87382477c1fb3cf4aa59626ccdb1ad3b110,
    equal to the declared parent_sha; `git merge-base --is-ancestor 856ff0a6e
    origin/main` exits 0 and likewise against HEAD (217da33ae);
    `git diff-tree --no-commit-id --name-status -r 856ff0a6e` shows exactly 13
    additions and 0 other changes, and that set equals the declared
    archive.path_sha256 key set EXACTLY (declared_not_changed: [],
    changed_not_declared: []). All 13 declared digests were recomputed from
    `git show 856ff0a6e:<path>` by this session: 13 match, 0 mismatch, 0
    missing, 0 non-hash sentinels.
    BACKWARD (commit -> the bytes I actually read): every one of the 12
    producer artifacts is BYTE-IDENTICAL between the commit blob and the
    working-tree file this review read, so nothing here was reviewed as
    working-tree-only material (agents/red-team.md prohibition honoured). The
    13th path, the snapshot receipt itself, DIVERGES between commit
    (f06b674ce0666da8af0bfbb9c3f7ecdfb47a7b8f1b9824eb88184e3481cef3f0, 11060
    bytes) and working tree
    (c2ebf8c4a5880a6a5454efc416e160f9b2950b1873f85ce81e1efb2cdd2e0d51, 11389
    bytes). That divergence is EXPECTED, DISCLOSED, AND BENIGN: follow-up
    commit 6470beac9540a229948eca3a1337387fa7e96f0b wrote the snapshot's own
    commit_sha back into the receipt, and the working-tree bytes match HEAD
    exactly (both c2ebf8c4a...), so the receipt is committed, not dirty. The
    declared digest is correctly the pre-6470beac9 value, which is what a
    commit-bound verification requires.
    `git log --all --oneline -- <producer dir>` returns exactly two commits
    ever: fe43a68ee (task_card.md only) and 856ff0a6e (the 13 files). NO
    DISCREPANCY FOUND IN THE CHAIN.
    ONE STALE NOTE, NON-BLOCKING: dispatch_queue.json's own
    archive.path_sha256_note (TASK-20260815-02b01b) still asserts that the
    receipt's own key "holds a deliberate non-hash sentinel that fails
    tools/research_dispatch.py validation loudly and by name." It does not; it
    holds the correct 64-hex digest, which this review verified against the
    commit blob. The note's instruction was carried out and the note was not
    updated. Harmless as provenance, misleading as a statement of current
    state; flagged so the ledger archive does not act on it.

  objections:

    - id: OBJ-1-THE-PER-BASIS-INDEPENDENCE-QUESTION-IS-ANSWERED-CLEAN-BUT-THE-AXIS-IS-MISNAMED
      severity: high
      verdict_on_the_named_failure_mode: NOT PRESENT — the bisections are genuinely independent.
      text: >-
        The completion_gate's primary challenge is answered in the producer's
        favour and this review states that plainly before objecting. Each
        bisection replays exactly from its OWN recorded trials under the
        script's own loop (probe2 A): beta=55 probes 69,100,84,76,72,74,75 and
        must return 75; beta=70 probes 69,100,84,76,72,74,73 and must return
        73. The recorded probe orders match the replayed orders element for
        element, the seed sets are disjoint and each equals its own expected
        seed (452658293 / 915347894), endpoint_reproduction_ok is true at both,
        fallback_used is false at both, and each reattempt cell carries
        mpfr_bits_used equal to ITS OWN basis's precision_used_for_reattempt.
        A borrowed value could not have replayed; nothing is shared.
        THE OBJECTION IS TO WHAT THE TWO NUMBERS ARE CALLED. In
        `worker_bisect()` (stage0_d512_beta5570_precision_bisection_and_reattempt.py
        lines 112-158) `beta` appears on exactly three lines: the function
        signature, the `result` label dict, and
        `np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0])`. The object
        bisected is `A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)` in
        both cases — no `BKZ.Param`, no block size, no beta anywhere in the
        computation. AT THE ISOLATED-LLL-STEP LEVEL, beta IS A SEED LABEL AND
        NOTHING ELSE. The identical property holds in the CTRL-1 probe this
        harness is copied from (BATCH-279acb .../probes/probe1_d512_beta_generality.py,
        `worker()` at line 55: beta only at the signature, the result label, and
        the same `default_rng` line; basis at line 69 is the same q-ary call),
        even though that probe's own docstring line 7 asks whether "a
        beta-specific minimum" could differ — a question its instrument cannot
        reach.
        CONSEQUENCE: "75 bits at beta=55" and "73 bits at beta=70" are two iid
        draws from ONE distribution — the minimum adequate isolated-step mpfr
        precision for a random q-ary lattice at d=512, k=256, q=3329 — that
        differ by seed, not by beta. Together with the beta=40 draw's 69 bits,
        the goal has three iid samples: {69, 73, 75}. THE CALIBRATION AXIS IS
        PER-DRAW, NOT PER-(d, beta). That is not a re-litigation of
        KN-FIND-ead2ac, which is binding-carried here in full and which this
        review AFFIRMS: it is a sharpening of that finding's own scope in the
        direction of MORE hazard, not less. KN-FIND-ead2ac's second recurrence
        axis, stated in its own title and one-sentence finding as "within a
        fixed dimension across `beta`", is measured by an instrument in which
        beta does not participate; the recurrence it observed is across DRAWS.
        That matters because PREREG-8 Stage 1 requires
        `one_basis_per_draw: true` and `>= 8` draws per cleared cell
        (experiments/EXP-MLKEM-42ea04/specification.yaml lines 99-100, 298), so
        the non-transfer recurs per draw, not merely across the three beta
        values. See COST-1.
      falsification_route: >-
        Read stage0_d512_beta5570_precision_bisection_and_reattempt.py lines
        112-143 and probe1_d512_beta_generality.py lines 55-95 and find any use
        of `beta` in the computation other than the `default_rng` seed vector
        and the result label. If one exists, this objection fails. Or: run the
        isolated-step bisection twice at the SAME beta with two different
        draw_index values and show the minimum is stable — that would restore
        beta as the operative axis and refute the per-draw reading.
      supporting_artifacts: [probes/probe2_arithmetic_independence_and_noise_floor_output.json]

    - id: OBJ-2-THE-HEADLINE-COUNTS-A-TIMEOUT-AS-A-FAILURE
      severity: critical
      text: >-
        `n_cells_completed: 0`, `n_cells_not_computed_or_error: 2`. The producer
        itself is careful here — run_manifest.yaml classifies beta=55 as
        `negative_observation` and beta=70 as `resource_exhaustion`, ANOM-3
        discloses the cap hit as first-of-its-kind, and writeup.md Observation 3
        says the timeout is "never evidence in either direction." That is
        correct and this review does not object to the producer's own wording.
        THE OBJECTION IS TO THE CONDITIONAL WAITING DOWNSTREAM.
        DEC-20260815-201633's `escalation_branch_ruling` (lines 206-212) says:
        "If THAT follow-up also fails to clear either of the two remaining
        cells at their OWN properly-calibrated precision, the obstruction is
        then measured closer to ... the scope the escalation branches require."
        "Did not clear" and "failed to clear" are not the same predicate, and
        the consequent draws on the latter. (d=512, beta=70) did not fail: it
        was not measured. Under AGENTS.md rule 5 and CLAUDE.md rule 3 it
        contributes exactly zero to any obstruction measurement.
        THE TRUE STATE OF THE OBSTRUCTION AFTER THIS BATCH, counted across the
        goal's whole history: full-tour outcomes at an own-basis-bisected
        isolated-step precision exist for exactly TWO cells — (d=512, beta=40)
        at 69 bits (BATCH-279acb, ERROR) and (d=512, beta=55) at 75 bits (this
        batch, ERROR). (d=512, beta=70) has NEVER produced a full-tour
        mathematical outcome at any precision that was adequate for its own
        basis. Two measured failures, both at the isolated-step minimum, which
        KN-FIND-f54a82 — this goal's own promoted finding — already says is the
        wrong calibration target. That is a fifth recurrence of a known
        methodological pattern, not a measurement of "the corrected
        construction is exhausted at d=512," which is what the escalation
        branches assert.
      falsification_route: >-
        Produce a full-tour outcome for (d=512, beta=70) at a precision
        adequate for its own basis that terminates with a mathematical status
        (COMPLETED or ERROR) rather than a cap kill. Until then this objection
        stands on the record's own `subprocess_timed_out: true`,
        `subprocess_returncode: -15`.

    - id: OBJ-3-THE-EXPERIMENT-WAS-DESIGNED-TO-TEST-THE-PRECISION-MOST-LIKELY-TO-FAIL
      severity: critical
      text: >-
        Task card completion_gate item (b) requires each cell be re-attempted
        "at ITS OWN bisected precision from step (a)/(a') -- never the other
        basis's own value." The bisection returns the MINIMUM adequate
        isolated-step precision, i.e. the value sitting one bit above the
        failure boundary of a DIFFERENT, cheaper operation. The full tour was
        therefore run at the least conservative precision in the entire tested
        window, and it was run there by contract, not by the executor's choice.
        Given KN-FIND-f54a82 (promoted, binding-carried, and cited by the
        writeup itself at lines 136-141), the beta=55 outcome was PREDICTED
        BEFORE THE RUN by the goal's own knowledge base. 2502.74s bought a
        fifth confirmation of a known pattern.
        The informative variant cost the same and was excluded by the card:
        the SAME cell, SAME seed, SAME construction, at 100 bits — a value this
        very run measured as COMPLETED at the isolated step for BOTH bases
        (bisection_d512_beta55_results.json trial 2; bisection_d512_beta70_results.json
        trial 2), and which sits in the SAME 2-limb 64-bit mpfr regime as 73/75
        bits according to the goal's own stated cost model (dispatch_queue.json
        budget_justification for TASK-20260815-f14d3c names "the 64-bit
        GMP/mpfr limb-boundary concern at 129+ bits", so 65-128 bits is one
        regime).
        THIS IS THE HIDDEN ASSUMPTION THE HANDOFF ASKED FOR: that the
        isolated-step minimum is the right precision at which to test the full
        tour. The goal's own promoted finding says it is not, and the task card
        nonetheless made it mandatory. It is a design objection against the
        CARD, not against the executor, who executed the card exactly.
      falsification_route: >-
        Run RT-CTRL-1 below. If (d=512, beta=55) at 100 bits raises the
        identical ReductionError at a comparable depth, the choice of the
        minimum was harmless and this objection is materially weakened.

    - id: OBJ-4-THE-SAME-NUMBERS-CONTAIN-A-LARGE-MEASURED-PRECISION-RESPONSE-READ-WITH-THE-OPPOSITE-SIGN
      severity: critical
      text: >-
        THE REVERSAL agents/red-team.md item 8 and docs/inventor-protocol.md
        section 4's `resource_check` require. Full arithmetic and per-field
        provenance: probes/probe3_precision_response_at_full_tour_level_output.json.
        Define the post-outer-LLL residual = subprocess_wall_clock_seconds -
        outer_lll_reduction_elapsed_seconds. It is an UPPER bound on BKZ-tour
        time (it also contains interpreter startup, basis generation, GSO.Mat
        construction and update_gso), and it is the identical derived quantity
        in every row, so rows compare to each other. Same cell, same seed, same
        construction, precision the only change:
          (d=512, beta=55): 69 bits -> residual 5.55s, died at bkz.py:123, the
            FIRST self.lll_obj() call, BEFORE any tour began (traceback, 3
            frames). 75 bits -> residual 2089.11s, entered tour(), ran
            svp_reduction with two levels of recursive svp_preprocessing, died
            at bkz.py:186 (10 frames). RATIO 376.4x, and a qualitative change
            from "never entered a tour" to "2089s of real tour work."
          (d=512, beta=70): 69 bits -> residual 5.42s, died at bkz.py:123,
            never entered a tour. 73 bits -> residual >= ~13,992s and STILL
            RUNNING when killed. RATIO >= 2581x (LOWER bound; the outer-LLL
            subtraction here uses the mean of the 7 outer-LLL timings this same
            run measured on the SAME basis, 408.15s, because the killed worker
            never wrote its own — flagged `estimated: true` in the probe).
        READ CORRECTLY, THE ISOLATED-STEP CALIBRATION DID EXACTLY WHAT IT WAS
        SUPPOSED TO DO. It got both cells past bkz.py:123 — which is precisely
        the operation the isolated-step probe tests, as the prior Red Team's
        OBJ-1 established by source inspection — and into real tour work. The
        pipeline now dies at a DIFFERENT operation: the WINDOWED
        `self.lll_obj(lll_start, lll_start, kappa + block_size)` at bkz.py:186
        inside svp_preprocessing, which has never been calibrated at any
        precision by anyone. writeup.md Observation 2 records this as "a
        fourth-plus recurrence of the isolated-step-vs-full-tour permissiveness
        pattern" — true, and it is also a measured 376x-to->2581x advance in
        pipeline depth driven by +4 to +6 bits. The record computes neither
        ratio and neither residual.
        This is the artifact-tell question inverted and it comes out POSITIVE:
        the parameter that is supposed to destroy the failure is precision, the
        failure IS decaying as precision rises, and the decay is measured. What
        is missing is the second point on that curve at the level where the
        claim lives.
      falsification_route: >-
        Recompute the residuals from the committed JSON; if the subtraction is
        wrong, the objection falls. Or show that the beta=70 outer-LLL estimate
        is materially off — but the beta=70 ratio survives any plausible
        substitution, since even charging the full 14400.08s to outer LLL is
        impossible (the bisection measured that operation at 396-428s on this
        exact basis, seven times).

    - id: OBJ-5-A-RUN-RECORD-WAS-DELETED-AND-THEN-CITED-AS-CORROBORATION
      severity: medium
      text: >-
        run_manifest.yaml `provenance.artifacts_deleted_before_this_attempt`
        lists six first-attempt files deleted before the second attempt,
        including `bisection_d512_beta55_results.json (partial/first-attempt
        version)`. writeup.md lines 14-18 and run_manifest.yaml lines 26-31 then
        USE the deleted data as corroboration: the first attempt "determined 75
        bits, matching this second attempt's own re-derivation below" /
        "reproduced identically by this second attempt below."
        THAT CORROBORATION IS UNVERIFIABLE. probe1 and probe2 section I confirm
        exactly two commits ever touched the producer directory — fe43a68ee
        (task_card.md only) and 856ff0a6e (the 13 second-attempt files). The
        first attempt's artifacts exist in no commit on any branch and cannot
        be recovered. An infrastructure-failed run is still a run: AGENTS.md
        "Artifact policy" requires each run to retain its raw machine-readable
        results and its validity status and reason, and core rule 4 makes
        results immutable records that corrections supersede rather than
        replace. The correct handling was to preserve the partial artifacts
        under a `failed_infrastructure` label, not to delete them.
        MITIGATION, STATED FAIRLY: the deletion is fully and prominently
        disclosed, the second attempt is complete and self-contained, and the
        deleted data is load-bearing for NO reported figure — only for a
        corroboration remark. The remedy is to strike or mark the "matching /
        reproduced identically" claim as unverifiable, not to rerun anything.
      falsification_route: >-
        `git log --all --diff-filter=A -- <producer dir>/bisection_d512_beta55_results.json`
        returning a commit predating 856ff0a6e would refute this. It returns
        only 856ff0a6e.

    - id: OBJ-6-THE-RUN-RECORD-DROPPED-THE-SELF-DECLARED-DIGEST-MAP-ITS-PREDECESSOR-CARRIED
      severity: medium
      text: >-
        TASK-20260815-6e4c02's run_manifest.yaml carries an `artifact_sha256`
        map; TASK-20260815-f14d3c's does not (probe2 H:
        run_manifest_declares_artifact_sha256 false,
        predecessor_declared_artifact_sha256 true — the check is a case-insensitive
        search for "sha256" across the whole file). This is a regression in the
        integrity surface, and it is not cosmetic: the prior Red Team was able
        to cross-check the producer's OWN declared digests against the commit
        blobs, independently of the archiving session's arithmetic. This review
        cannot, because the producer declared none. Every digest in this
        package now traces to a single writer, the snapshot receipt. The chain
        still verifies — it just has one fewer independent witness than the
        batch it supersedes.
      falsification_route: >-
        `grep -i sha256 <producer dir>/run_manifest.yaml` returning any digest
        map refutes this. It returns nothing.

  required_controls:

    - id: RT-CTRL-1-CHEAPEST-DECISIVE-NOT-RUN-BY-THIS-REVIEW
      status: NOT RUN (this review executed no fpylll and no lattice computation of any kind)
      description: >-
        THE CHEAPEST AVAILABLE CONTROL THAT WOULD FALSIFY OR MATERIALLY NARROW
        THE REPORTED OUTCOME, answering the completion_gate item explicitly.
        ONE run: the full BKZ tour at (d=512, beta=55, seed=452658293),
        byte-identical construction and seed formula, `mpfr_bits = 100`.
        WHY 100: this run's own bisection measured 100 bits COMPLETED at the
        isolated step at this exact basis, so it is inside the already-validated
        window and requires no new assumption; and per the producer's own
        budget_justification the 64-bit mpfr limb boundary is at 129+ bits, so
        100 bits sits in the SAME 2-limb regime as 75 bits and should carry no
        step change in per-operation cost.
        COST: one cell, expected of the same order as the 2502.74s already
        spent at 75 bits, hard-capped. Report the outcome at BOTH the 3600s
        mark (the frozen specification's own Stage-0 cap) and the 14400s mark.
        WHAT IT DISCRIMINATES, all three at once: (a) CTRL-3's real question —
        does a precision comfortably above the isolated-step minimum clear the
        tour, or does the tour fail regardless of precision inside the 2-limb
        regime; (b) whether the beta=55 ERROR is a precision artifact or a
        property of the construction; (c) whether a fixed-margin precision can
        replace per-draw bisection entirely (see COST-1).
        EITHER OUTCOME IS DECISIVE. Clears -> the first completed d=512
        main-grid cell in this goal's history. Errors identically -> the
        obstruction is measured, for the first time, at a precision that is NOT
        the isolated-step minimum, which is the exact scope
        DEC-20260814-4ac30a's escalation branches presuppose and have never had.
      is_a_full_tour_level_precision_search_the_cheapest_control: >-
        NO, AND THE COMPLETION_GATE ASKS THIS DIRECTLY. CTRL-3's costlier half
        as specified — bisecting `bkz(par, tracer=True)` itself at increasing
        precision — needs ~7 trials per basis, each up to the 14400s cap, i.e.
        up to ~100,800s per basis and ~201,600s for both. RT-CTRL-1 is ONE
        trial at the top of the already-known-good window and falsifies-or-
        narrows on its own. Stronger: RT-CTRL-1 can VOID the expensive control.
        If 100 bits also ERRORs, a tour-level bisection over [75, 100] is
        provably empty (both endpoints fail) and would burn ~100,800s to
        rediscover that; the correct next move would instead be to cross the
        limb boundary (129+ bits) or to accept the obstruction. RT-CTRL-1 is
        therefore not merely cheaper than CTRL-3's costlier half — it is a
        PREREQUISITE for it being worth running at all.

    - id: RT-CTRL-2-INSTRUMENT-FIX-ZERO-ADDITIONAL-LATTICE-COMPUTE
      status: NOT RUN
      description: >-
        MUST LAND BEFORE ANY FURTHER CAPPED RUN. The 14400s beta=70 cell was
        63.9% of this task's entire compute (14400.08 / 22545.08) and yielded
        exactly one bit: "> 14400s". Three fixes, all essentially free:
        (a) CPU TIME. `run_capped_subprocess()` already holds a
        `psutil.Process` handle and calls `.memory_info()` every 0.5s; it never
        calls `.cpu_times()` (probe2 H: psutil_memory_info_called_in_script
        true, psutil_cpu_times_called_in_script false). No CPU-time figure
        exists anywhere in the results (cpu_time_recorded_anywhere_in_results
        false). The one verdict in this package that is a PURE wall-clock
        judgement is the one metric that host contention corrupts — see COST-3.
        (b) TOUR PROGRESS. `bkz(par, tracer=True)` was passed but the worker
        writes its JSON only at line 239, after the call returns. On SIGTERM
        nothing is persisted; probe2 H finds no signal handler, no atexit, no
        per-tour flush, and `run_main_cell()` additionally DROPS the captured
        `stdout_tail` for a timed-out cell (stdout_tail_retained_for_timed_out_cell
        false; the recorded stderr_tail is the empty string). A SIGTERM handler
        dumping `bkz.trace`'s tour count, or a per-tour flush, converts the next
        timeout from one bit into a tours-per-hour cost curve — which is exactly
        the quantity a Stage-1 sizing decision needs and does not have.
        (c) HOST LOAD. environment.json records nproc and free memory at start
        but no load average or CPU-percent (host_load_recorded_in_environment_json
        false). See COST-3 for why this run's own data shows it matters.

    - id: RT-CTRL-3-NULL-AND-NEARBY-OBJECT-THE-PRIOR-CTRL-4-N-A-RULING-MUST-BE-REVISITED
      status: NOT RUN
      description: >-
        BATCH-279acb's CTRL-4 declared a null-object control N/A because "this
        is an infrastructure feasibility/timing measurement ... there is no
        signal that should decay." That ruling was defensible while the task was
        "measure a timing." It is no longer, because this batch's own objective
        text says the outcome "measures the obstruction closer to ... the scope
        the escalation branches require" — and once a package claims to measure
        an obstruction, docs/inventor-protocol.md section 3 (controls before
        belief) and section 4 (the obstruction is measured, and read twice) both
        engage. There IS a signal and it IS decaying: see OBJ-4.
        Two distinct controls are needed, and neither has ever been run:
        (i) NULL OBJECT, PARTLY ALREADY IN HAND. The object under test IS the
        null object: `IntegerMatrix.random(d, "qary", k=d//2, q=3329)`, a
        structureless random q-ary lattice. So the honest statement is not "we
        lack a null" but "we have ONLY the null," and every d=512 obstruction
        this goal has measured is a property of fpylll 0.6.4's mpfr path on
        generic random q-ary lattices, on one host. That directly indicates
        DEC-20260814-4ac30a's "upstream fplll bug report" branch over its
        "construction is exhausted" reading, and it is stated in
        KN-FIND-f54a82 section 4.3 as an open limitation — but nowhere in this
        producer's writeup.
        (ii) NEARBY OBJECT, THE ONE THAT ACTUALLY GATES STAGE 1. PREREG-8's
        Stage 1 reduces REAL ML-KEM module lattices — ring Z_q[X]/(X^n+1),
        module rank 2, real CBD eta1=3/eta2=2, real FIPS 203 Compress_d/
        Decompress_d (specification.yaml lines 79-93). Stage 0's feasibility
        gate reduces a generic q-ary lattice. Numerical stability of the
        Babai/LLL step depends on the GSO profile, and a module-LWE basis and a
        random q-ary basis of the same (d, q, k) do not share one. THE GATE IS
        MEASURED ON A DIFFERENT OBJECT FROM THE ONE IT GATES, in both
        directions: a Stage-0 failure on random q-ary does not establish
        Stage-1 infeasibility on module lattices, and a Stage-0 pass would not
        establish feasibility either. Cost: one isolated-step bisection
        (~2800s) plus one tour (<= cap) on an ML-KEM-shaped d=512 basis, using
        the instance-generation code Stage 1 needs anyway. THIS CONTROL IS
        REQUIRED BEFORE ANY ESCALATION BRANCH IS NAMED RIPE, because "the
        corrected construction is exhausted at d=512" measured on random q-ary
        bases would not license dropping a d=512 ML-KEM cell.

    - id: RT-CTRL-4-MONOTONICITY-CLOSURE-LOW-PRIORITY
      status: NOT RUN
      description: >-
        `bisect_precision_d512b()` assumes success is monotone in precision. The
        script's own comment at lines 377-380 shows the author was aware of
        monotonicity at the ENDPOINTS ("cannot bisect a monotone boundary that
        does not hold") but the interior was never tested. What is actually
        measured is "74 fails and 75 succeeds" (beta=55) and "72 fails and 73
        succeeds" (beta=70); "minimum" is an inference from monotonicity.
        Untested values strictly below the reported minima: {70, 71, 73} at
        beta=55 and {70, 71} at beta=70 (probe2 B). Closing the gap costs 5
        trials, 1177.7s + 826.9s = 2004.6s at this run's own measured per-trial
        rates.
        RANKED LAST DELIBERATELY: if RT-CTRL-1 shows the tour needs a
        comfortable margin rather than a minimum, the exact minimum stops
        mattering and this 2004.6s is not worth spending. Named so that
        "determined minimum" is not read as "exhaustively verified minimum" in
        the meantime.

  counterexample_or_mutation: >-
    THE CHEAPEST DISCRIMINATING MUTATION IS A ONE-TOKEN CHANGE TO THE
    PRODUCER'S OWN SCRIPT: in `main()`, replace `precision_used` for the
    reattempt with `FALLBACK_PRECISION_BITS` (100), which the script already
    defines at line 79 and already documents as "the nearest KNOWN-SUCCEEDING
    value at both exact instances." No new code, no new construction, no new
    seed, no new assumption. That single edit converts the experiment from
    "confirm KN-FIND-f54a82 a fifth time" into "test whether precision at the
    tour level is the operative variable," and it is RT-CTRL-1.
    A SECOND, MORE DIAGNOSTIC MUTATION, if RT-CTRL-1 errors: wrap
    `bkz(par, tracer=True)` in a handler that records `kappa`, `block_size` and
    `lll_start` at the ReductionError, then re-run ONLY the windowed
    `lll_obj(lll_start, lll_start, kappa + block_size)` call at rising
    precision on the captured state. This bisects the operation that is
    ACTUALLY failing (bkz.py:186) rather than the one the current harness
    bisects (the full-range call at bkz.py:123, which both cells now pass), at
    the price of one tour run to capture the state plus cheap windowed retries
    — far below CTRL-3's costlier half.

  baseline_comparison: >-
    NOT APPLICABLE IN THE POLLARD-RHO / BSGS / SPECIALIZED-ATTACK SENSE, checked
    rather than skipped, and independently concurred with rather than restated:
    this is a Stage-0 lattice-reduction feasibility gate, not a discrete-log
    attack, and no solve, relation, rank, memory-vs-time, source-recovery,
    target-descent or scalar-orientation axis is claimed or attempted anywhere
    in the producer's artifacts (grep-checked across writeup.md, run_manifest.yaml,
    and all three results JSON: no comparative performance claim of any kind).
    THE APPLICABLE COMPARATOR IS INTRA-GOAL, and it is the comparison the
    package does not make: TASK-20260815-6e4c02's own three d=512 cells at the
    borrowed 69 bits versus this task's two cells at their own bisected
    precisions. Made in OBJ-4 and probe3.
    ALSO ABSENT AND WORTH NAMING: no external lattice baseline (BKZ 2.0
    simulator, core-SVP / Lattice Estimator cost model) has ever been engaged
    by this goal, correctly, because no cell has completed and there is no
    measured cost to compare. That remains the honest position and should be
    stated as such rather than left implicit.
    dominated_by: "n/a (no result claimed) — the producer asserts no
    improvement over anything, so there is no frontier row to check. This is a
    checked null, not an unchecked one: every axis (time, memory,
    data/queries) is inapplicable because no attack, solve or speedup is
    claimed."
    sota_delta: "no attack; infrastructure feasibility measurement only."

  heuristic_challenges: []
  heuristic_challenges_note: >-
    NOT APPLICABLE, CHECKED. No numbered heuristic, random-model justification,
    asymptotic claim or exponent-first result exists anywhere in this task.
    H-MLKEM-7d9bcc's HEUR-* assumptions are untouched and remain unevaluated by
    any data this task produced; T-PROJNOISE-NODATA fires; PREREG-8 section 4.3
    item 1's FORBIDS clause is honoured throughout, confirmed by direct
    inspection of writeup.md, run_manifest.yaml and all three results JSON — no
    C1/C2 statement appears anywhere, in either direction. The exemplar-style
    challenge list of docs/target-result-profile.md does not engage an
    infrastructure feasibility measurement.

  cost_model_challenges:

    - id: COST-1-THE-OMITTED-COST-FOUND-PER-DRAW-CALIBRATION-IS-NOWHERE-IN-THE-STAGE-1-BUDGET
      severity: critical
      text: >-
        THE COMPLETION_GATE'S REQUIRED SEARCH FOR AN OMITTED OR UNDERCOUNTED
        COST: FOUND, and it is large. Per OBJ-1 the calibration axis is
        per-draw. Per specification.yaml lines 99-100 and 298, Stage 1 requires
        `one_basis_per_draw: true` and `>= 8` independent draws per cleared
        cell across up to 6 cells, plus NULL-3 at 64 draws per cleared cell
        (lines 151, 314-317). If the current design's per-draw bisection is
        carried into Stage 1, the calibration cost is, using THIS run's own
        measured d=512 bisection rate of ~2800s per draw as an upper-bound rate:
          main arm:  6 cells x 8 draws x ~2800s  ~= 134,400s
          NULL-3:    6 cells x 64 draws x ~2800s ~= 1,075,200s
          total                                   ~= 1,209,600s  (~336 hours)
        against a frozen total_cpu_hours ceiling of 576 hours / 2,073,600s
        (specification.yaml line 312-317). That is a ~58% increase, and NOT ONE
        SECOND OF IT APPEARS IN THE SPEC'S BUDGET, in any decision record, or
        in any batch's budget_justification. LABELLED HONESTLY: this is
        arithmetic extrapolated from d=512 rates, not a measurement; d=256
        cells would be cheaper. It is an order-of-magnitude sizing check, and
        it is the number a Stage-1 sizing decision must not be made without.
        THE KN-LIT-7593 CHARGE, WHICH THIS REVIEW'S BRIEF NAMES EXPLICITLY: the
        bisection is a precomputation that eliminates the "which precision"
        dimension for the reattempt. Its cost IS charged inside this task
        (5642.26s of bisection = 25.0% of the task's 22545.08s compute, honestly
        reported). It is NOT charged in the forward model, where it must recur
        per draw. An eliminated dimension is not a saving until the invariant's
        own cost is in the total.
        THE REVERSAL, WHICH IS WHY RT-CTRL-1 MATTERS TWICE OVER: read as a
        resource rather than a cost, the three measured minima {69, 73, 75} are
        tightly clustered, 100 bits cleared the isolated step at 3 of 3 bases
        tested, and 69-128 bits is ONE 2-limb mpfr regime by the goal's own
        stated cost model. A FIXED-MARGIN PRECISION WOULD DELETE THE ENTIRE
        PER-DRAW CALIBRATION DIMENSION — all ~1,209,600s of it — at the price of
        whatever running at 100-128 bits instead of ~73 actually costs per
        operation. That price is UNMEASURED, and measuring it is one run.
        Charging it is mandatory before the saving is credited.

    - id: COST-2-PER_BASIS_FEASIBILITY_CAP_V3-CHECKED-AGAINST-ITS-OWN-JUSTIFICATION-AND-AGAINST-COST-3
      severity: high
      text: >-
        THE COMPLETION_GATE'S REQUIRED CAP CHECK, in three parts.
        (a) INTERNAL CONSISTENCY WITH ITS OWN budget_justification: HOLDS, with
        one measured breach of its own stated worst case. The justification
        sizes the bisection at "at most 7 trials PER BASIS" and "at the largest
        isolated-LLL-step trial cost observed to date ... (395.65s) ... 7 trials
        cost at most 2769.55s per basis." Both bases ran exactly 7 trials —
        correct, and notably BETTER than CTRL-2's own estimate, which said "a
        further ~5-6 trials per cell ... roughly 2000-2400s" and silently
        omitted the 2 endpoint-reconfirmation trials that the reused
        `bisect_precision_d512b()` design always runs first; the producer caught
        that and budgeted 7. But at beta=70 the largest single trial was
        433.96s, 9.68% ABOVE the 395.65s the justification used as an upper
        bound, and the basis total was 2894.31s, 124.76s (4.5%) above the
        justification's own stated worst case of 2769.55s (probe2 E). It stayed
        inside the real 3600s budget, so nothing broke. What is falsified is the
        SIZING METHOD: "largest cost observed to date x n_trials" is
        demonstrably not an upper bound on this host, and the same method style
        underpins PER_BASIS_FEASIBILITY_CAP_V3 itself and will underpin Stage-1
        sizing.
        (b) DISCLOSURE: GENUINE. The reuse is disclosed at length in
        dispatch_queue.json's budget_justification, in the script's own comment
        at lines 84-90, and in writeup.md — with COST-3's
        "adequate-and-untested-as-binding" wording quoted verbatim rather than
        paraphrased away. The ex-ante reasoning was sound: no new data existed
        at the time, and the predicted precisions (73, 75) did stay well below
        the 129-bit limb boundary the justification worried about.
        (c) COST-3 IS NOW DISCHARGED, IN THE DIRECTION THAT MATTERS MOST. The
        cap is no longer untested-as-binding: it BOUND, at beta=70, for the
        first time in this goal's history, and it bound on the single most
        expensive cell ever run here. That converts the cap from a formality
        into a load-bearing parameter of the result, and it means the next
        sizing decision cannot reuse it on the same "never approached" grounds.
        It also means the cap now determines what the goal knows: a different
        cap would have produced a different record.

    - id: COST-3-THE-ONE-WALL-CLOCK-VERDICT-RESTS-ON-AN-UNMEASURED-NOISE-FLOOR-THAT-THIS-RUN-ITSELF-MEASURES
      severity: high
      text: >-
        THE RECORD CONTAINS A BUILT-IN TIMING NULL AND NOBODY READ IT.
        `outer_lll_reduction_elapsed_seconds` runs BEFORE `FPLLL.set_precision()`
        and does not use beta at all, so within one basis it is THE SAME
        COMPUTATION REPEATED ONCE PER TRIAL. Its spread is therefore a direct,
        free measurement of host timing noise (probe2 D):
          beta=55 block (trials 1-7): 384.82, 387.99, 382.24, 391.02, 387.39,
            387.98, 388.00 -> mean 387.06, sd 2.58, spread 2.27%, drift +0.83%.
          beta=70 block (trials 8-14): 396.64, 402.71, 402.45, 404.31, 402.90,
            419.62, 428.39 -> mean 408.15, sd 10.54, spread 7.78%, MONOTONE
            DRIFT +8.00% first to last.
          cross-block level shift: +5.45%.
        An identical computation got 5.45% slower between the first and second
        half of the run and drifted a further 8% within the second half. The
        cause is not recorded and cannot be recovered: environment.json has no
        load average, no CPU-percent, no steal time, and no CPU-time figure
        exists anywhere (probe2 H). The producer's OWN ANOM-2 discloses that the
        executor session's shell polling loops were running and being killed
        roughly hourly on the same 4-vCPU host throughout — a plausible source
        it explicitly declines to quantify.
        WHY THIS IS LOAD-BEARING RATHER THAN PEDANTIC: the drifting block is
        immediately followed by the ONE verdict in this package that is a pure
        wall-clock judgement — (d=512, beta=70) NOT_COMPUTED at 14400.08s. Every
        other outcome in the package is a deterministic COMPLETED/ERROR status
        that noise cannot flip. That one is not. The fix costs nothing:
        `.cpu_times()` on the psutil handle the polling loop already holds
        (RT-CTRL-2a). Until then, every wall-clock number in this record carries
        an unstated environmental error bar of at least 5-8%, and the record
        presents all of them without one.

    - id: COST-4-THE-OPERATING-CAP-IS-4x-THE-FROZEN-SPECIFICATION-S-OWN-STAGE-0-CAP-WITH-NO-AMENDMENT
      severity: high
      text: >-
        experiments/EXP-MLKEM-42ea04/specification.yaml states
        PER_BASIS_FEASIBILITY_CAP = 3600s TWICE — as
        CTRL-STAGE0-FEASIBILITY's pass_condition (line 123: "Cell completes
        within PER_BASIS_FEASIBILITY_CAP = 3600s; a cell that does not is
        dropped and reported NOT_COMPUTED") and as a stopping rule (line 333).
        It separately states PER_BASIS_STAGE1_CAP = 14400s for a single STAGE-1
        basis reduction (line 339). This Stage-0 task ran at 14400s — the
        Stage-1 number — a 4.0x relaxation of the spec's own Stage-0 rule. The
        string "PER_BASIS_FEASIBILITY_CAP_V2/V3" appears nowhere in
        specification.yaml (probe2 G: amendment_to_specification_yaml_found
        false); the V2/V3 escalation lives only in batch-local decisions and
        goal checkpoints.
        THE CONCRETE COST OF THE DIVERGENCE IN THIS RUN: 10,800.08s — 47.9% of
        this task's entire 22,545.08s compute — was spent past the
        specification's own Stage-0 stopping rule, and produced no information.
        By the spec's own rule, (d=512, beta=70) was a dropped NOT_COMPUTED cell
        at 3600s. (d=512, beta=55) errored at 2502.74s and is INSIDE the spec's
        cap, so its result is unaffected.
        Separately: specification.yaml `budget.wall_clock_seconds_per_run:
        14400` with "A single RUN-* record here corresponds to one ...
        script invocation"; this task's single invocation ran 22,589s outer
        (1.57x). And `maximum_runs: 16` allocates "Stage 0 (1)" — this batch
        alone consumed two producer script invocations (the VM-rebooted first
        dispatch and the second), and Stage-0 producer scripts have now run
        across BATCH-3b9962, BATCH-d1a736, BATCH-279acb and BATCH-0d5018. The
        run-budget accounting has never been reconciled against the spec.
        STATED FAIRLY, AND THIS MATTERS: EXP-MLKEM-42ea04 is
        `review_required` / `approved_by: null`, so this is NOT a violation of
        an approved protocol, and a larger cap can only help a cell PASS —
        it cannot manufacture a negative. But PREREG-8 is binding-carried into
        this batch in full, and 3600s is the number the eventual go/no-go will
        be read against. The escalation 3600 -> 7200 -> 14400 has now run three
        batches without an amendment and without buying a single completed
        cell. Either amend specification.yaml with the rationale, or report
        Stage-0 outcomes at BOTH marks. Do not let a fourth batch inherit it
        silently.

    - id: COST-5-TOTAL-EXPECTED-COST-AND-WALL-CLOCK-RECONCILIATION-CHECKED-CLEAR
      severity: low
      text: >-
        Per-attempt vs total-expected-cost bookkeeping: CLEAR. 0 of 2 successes
        gives no probability to invert; the producer computes and implies no
        total-expected-cost figure, correctly.
        Wall-clock reconciliation: CLEAR, with the small gap named. The four
        phase wall-clocks (2747.941 + 2894.315 + 2502.742 + 14400.084) sum to
        22545.082s against a reported `total_script_wall_clock_seconds` of
        22545.084s — agreement to 2.4 ms. Outer UTC elapsed (17:14:00Z ->
        23:30:29Z) is 22589s, so 43.92s (0.194%) of interpreter startup and
        teardown falls outside `t_script_start` and is not counted. The writeup
        labels the figure "(self-reported)", which is the honest wording. No
        double-count and no phantom buffer of the kind the prior batch's OBJ-4
        found: THIS package is clean on that axis and this review says so
        explicitly rather than leaving it unstated. Per-basis orchestration
        overhead between trials is 12.5 ms and 2.3 ms respectively.
        Memory: peak RSS 141.38 / 142.42 MB against a 16 GB allowance;
        no memory axis is at issue anywhere.

  reduction_and_scope_challenges:

    - id: SCOPE-1-SCOPE-DISCIPLINE-INDEPENDENTLY-CONFIRMED-CLEAN
      text: >-
        Every named out-of-scope item is confirmed honoured by direct inspection
        of the committed script and all outputs: (d=512, beta=40) is not
        attempted (BASES contains only beta 55 and 70; the results JSON carries
        an explicit note); no `d=256` or `256` cell appears anywhere in the
        script, stdout, stderr or any results file; no full-tour-level precision
        search is performed (the reattempt runs at exactly one precision per
        cell and the writeup says so at lines 140-141 and 226); no Stage-1
        activity, no >= 8-draw grid, no 2^20 target generation, no
        NULL-1/2/3/SENS control; no hypothesis or experiment status is touched;
        no C1/C2 or ML-KEM-security statement appears in any artifact. The
        invalidation triggers that could have fired did not: both bases
        reproduced ERROR at 69 / COMPLETED at 100 with the exact expected seeds,
        `endpoint_reproduction_ok: true`, `invalidation_note: null`,
        `fallback_used: false`.
    - id: SCOPE-2-NO-CITED-REDUCTION-AND-NO-SCHEME-SCOPE-LIST
      text: >-
        NOT APPLICABLE, CHECKED. No published reduction is cited and no
        affected-vs-safe scheme list exists, correctly. No scope inflation
        found. The one scope statement that IS missing is the transfer
        assumption in RT-CTRL-3(ii): the writeup never states that the object
        measured is a generic random q-ary lattice rather than an ML-KEM module
        lattice. KN-FIND-f54a82 section 4.3 states it; this package does not
        carry it forward, and the ledger archive should.

  proof_architecture_challenges: []
  proof_architecture_challenges_note: >-
    NOT APPLICABLE AS A proof_search_map AUDIT — no theorem, asymptotic bound,
    certificate family, reduction or closure argument is proposed, so
    docs/inventor-protocol.md section 8 / KN-TECH-080 do not engage. ONE
    transform does apply informally and is recorded rather than skipped: the
    OBSERVATION-FIBER attack. The observable "does BKZ complete at d=512 under
    mpfr" is held fixed while the underlying object varies from a random q-ary
    lattice to an ML-KEM module lattice, and this goal has never checked whether
    the observable separates them. That is RT-CTRL-3(ii), and it is the reason
    a Stage-0 verdict of either sign does not transfer to Stage 1 on this
    record.

  narrowest_supported_statement: >-
    WHAT TASK-20260815-f14d3c ACTUALLY SHOWS, AT ITS TRUE WIDTH:
    "On one host, fpylll 0.6.4, against `IntegerMatrix.random(512, 'qary',
    k=256, q=3329)` bases drawn from SEED_ROOT=715923 at
    default_rng([715923,0,512,beta,0,0]): the minimum mpfr precision adequate
    for the ISOLATED LLL/GSO preprocessing step is 75 bits at seed 452658293
    and 73 bits at seed 915347894, each determined by a genuine, independent,
    1-bit-resolution bisection between a re-confirmed failing endpoint (69
    bits) and a re-confirmed succeeding endpoint (100 bits), under an untested
    interior monotonicity assumption. At 75 bits the seed-452658293 basis's
    full BKZ tour (block_size 55) passed the initial full-range lll_obj() call,
    entered a real tour, and raised ReductionError('infinite loop in babai')
    inside svp_preprocessing's windowed lll_obj() call after 2502.74s. At 73
    bits the seed-915347894 basis's full BKZ tour (block_size 70) was still
    running, without completing and without raising any exception, when it was
    hard-killed at a 14400s cap; nothing further about that cell was measured."
    WHAT IT DOES NOT SUPPORT:
    (1) that "0/2 cells cleared" is two measured failures — one is a timeout,
    which is infrastructure signal and never negative mathematical evidence;
    (2) that 75 and 73 bits are per-beta quantities — beta does not enter the
    bisected computation, so they are per-draw quantities, and the goal has
    three iid samples {69, 73, 75}, not three beta-indexed constants;
    (3) that "the corrected (mpfr, ROW_EXPO-free) construction is exhausted at
    d=512" — no d=512 cell has EVER been run at any precision above its own
    isolated-step minimum, at any beta, in this goal's history;
    (4) that DEC-20260815-201633's escalation conditional is discharged — its
    antecedent requires both remaining cells to FAIL at their own properly
    calibrated precision, and one of them did not fail, it was not measured;
    (5) anything whatever about ML-KEM security, any FIPS 203 parameter set,
    any attack cost, C1, C2, or H-MLKEM-7d9bcc's truth in either direction.
    CLAIM TIER TOY, UNCONDITIONALLY.
    AND WHAT IS NEWLY OPEN, WHICH THE RECORD DOES NOT SAY: at the FULL-TOUR
    level, precision is measurably the operative variable. +6 bits at
    (d=512, beta=55) moved the post-outer-LLL residual from 5.55s to 2089.11s
    (376.4x) and moved the failure from "before any tour began" to "10 frames
    deep inside a real tour"; +4 bits at (d=512, beta=70) moved it from 5.42s to
    >= ~13,992s. Whether one further step, to a precision still inside the same
    2-limb mpfr regime, clears the tour is UNTESTED BY ANYONE and is one run
    away.

  premature_closure_finding: >-
    NO LANE IS FORECLOSED BY THE PRODUCER ITSELF, AND THIS REVIEW SAYS SO
    PLAINLY: writeup.md declines to draw the escalation or Stage-1 conclusion,
    run_manifest.yaml's executor_assessment explicitly defers it, and the
    NOT_COMPUTED cell is reported as "never as evidence in either direction."
    That is correct conduct and it is the reason this package is accepted as a
    measurement.
    THE RISK IS ENTIRELY DOWNSTREAM, AND IT IS SPECIFIC. DEC-20260815-201633's
    escalation_branch_ruling pre-wrote the consequent, and the ledger archive
    (TASK-20260815-fa0ead) is the session that will apply it. Applying it on
    this record would close a lane on an obstruction (i) counted from one
    measured failure plus one timeout, (ii) measured only at a precision the
    goal's own promoted KN-FIND-f54a82 says is the wrong calibration target,
    (iii) measured on a generic random q-ary lattice rather than the ML-KEM
    module lattice the gate exists to gate, and (iv) contradicted in direction
    by a 376x-to->2581x precision response present in the same run's own
    numbers. Under docs/inventor-protocol.md section 4 that is a fatigue report
    about the calibration search wearing a number, not a statement about the
    problem, and its honest status is `unverified`.
    FORWARD GUIDANCE, as section 4 requires of anyone claiming a closure:
    what remains open is (a) the full tour at any precision above the
    isolated-step minimum inside the 2-limb regime, at every d=512 cell;
    (b) the windowed lll_obj() call at bkz.py:186, which is now the failing
    operation and has never been calibrated at any precision; (c) the entire
    ML-KEM-shaped-basis question, at every dimension; (d) the fixed-margin
    strategy that would delete per-draw calibration from Stage 1's cost model.
    None of these is expensive, and none has been attempted.
    OBSTRUCTION BLOCK, AS THE PROTOCOL REQUIRES IT BE MEASURED RATHER THAN
    ASSERTED — quantity: post-outer-LLL residual wall clock to
    ReductionError('infinite loop in babai') for a full BKZ tour, d=512, random
    q-ary basis, fpylll 0.6.4, one host. Values: 268.49s at (beta=40, 69 bits);
    2089.11s at (beta=55, 75 bits); 5.55s / 5.42s at (beta=55/70, 69 bits
    borrowed); >= ~13,992s and non-terminating at (beta=70, 73 bits). Runs:
    TASK-20260815-6e4c02, TASK-20260815-f14d3c. Error bars: at least 5-8%
    environmental, per COST-3, plus an estimated outer-LLL subtraction for the
    beta=70 row. Scope claimed: exactly these five (cell, precision) points,
    this lattice family, this build, this host — nothing wider.
    resource_check: EXAMINED, AND A READING WAS FOUND. Two, in fact: the
    per-draw precision spread reads as an argument for a fixed margin that
    deletes ~1,209,600s of Stage-1 calibration (COST-1), and the residual
    survival growth reads as a measured precision response rather than a
    recurrence of a negative pattern (OBJ-4). Both are candidates for the
    ranking and neither is evidence; neither changes any status on its own.
    spawned_ids: none minted by this review — this report changes no status and
    mints no ledger record.

  next_concrete_action: >-
    RUN RT-CTRL-1 BEFORE TASK-20260815-fa0ead APPLIES DEC-20260815-201633's
    ESCALATION CONDITIONAL, AND BEFORE ANY STAGE-1 SIZING OR ESCALATION-BRANCH
    DETERMINATION IS MADE FROM THIS BATCH.
    Exactly: one full BKZ tour at (d=512, beta=55), seed 452658293,
    byte-identical construction, `mpfr_bits = 100`, with RT-CTRL-2's
    zero-compute instrument fixes applied first (psutil `.cpu_times()` in the
    existing polling loop; a SIGTERM handler or per-tour flush persisting
    `bkz.trace`'s tour count; loadavg captured into environment.json), and the
    outcome reported at BOTH the 3600s and 14400s marks per COST-4. One run.
    Same order of cost as the 2502.74s already spent. It is the single cheapest
    experiment in this space that can produce the first completed d=512
    main-grid cell in this goal's history OR measure the obstruction, for the
    first time, at a precision that is not the isolated-step minimum — which is
    the scope DEC-20260814-4ac30a's escalation branches presuppose and have
    never had.
    THIS REVIEW RECOMMENDS NO CLAIM ABOUT ML-KEM SECURITY, NO STAGE-1 SIZING,
    AND NO ESCALATION-BRANCH DETERMINATION. It recommends that none be made
    from this record yet, and names the one run that would change that.

  prohibitions_compliance: >-
    This review changed no research status, no hypothesis, no experiment
    approval, and no raw producer artifact; `git status --porcelain` shows no
    modification anywhere outside this task's own write_scope, and this session
    made no commit of any kind. It wrote nothing to knowledge/INDEX.md and
    regenerated nothing. It does not call any bounded failure an impossibility
    result — every objection narrows rather than broadens what may be concluded.
    It makes no ML-KEM security statement and no C1/C2 statement in either
    direction. CLAIM TIER STAYS TOY. PREREG-8, DEC-20260814-4ac30a,
    DEC-20260814-8ec2e5, EV-MLKEM-e4189c, DEC-20260815-201633, KN-FIND-ead2ac
    and KN-FIND-f54a82 are carried in full and none is re-litigated: OBJ-1
    AFFIRMS KN-FIND-ead2ac's finding and sharpens the scope of its own stated
    recurrence axis in the direction of more hazard, which is a scoping
    observation about an instrument, not a dispute with the finding.
    THIS REVIEW EXECUTED NO fpylll AND NO LATTICE COMPUTATION OF ANY KIND. Every
    timing, precision, status and traceback figure in this report is recomputed
    arithmetic over the producer's own committed recorded fields, with each
    derived quantity's definition and each substituted field's assumption stated
    at the point of use. No measurement, timing, citation or run is fabricated.

  probes_written_declared_gap_g1: >-
    DECLARED GAP G-1 CLOSED EXPLICITLY. Exactly 7 files were written by this
    review, all inside its assigned write_scope and all listed in
    artifact_paths below: this report plus 3 probe scripts and their 3 recorded
    outputs. No __pycache__, .pyc, temporary or scratch file remains (the probes
    write no temporary files by construction; verified by directory listing).
    dispatch_queue.json's artifact_paths for TASK-20260815-19c716 currently
    declares only red_team_report.md and MUST be extended to all 7 before the
    ledger archive stages this directory.

  artifact_paths:
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/red-team/TASK-20260815-19c716/red_team_report.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/red-team/TASK-20260815-19c716/probes/probe1_notarization_chain_both_directions.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/red-team/TASK-20260815-19c716/probes/probe1_notarization_chain_both_directions_output.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/red-team/TASK-20260815-19c716/probes/probe2_arithmetic_independence_and_noise_floor.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/red-team/TASK-20260815-19c716/probes/probe2_arithmetic_independence_and_noise_floor_output.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/red-team/TASK-20260815-19c716/probes/probe3_precision_response_at_full_tour_level.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/red-team/TASK-20260815-19c716/probes/probe3_precision_response_at_full_tour_level_output.json

  budget_actual:
    wall_clock_seconds_allowed: 12000
    wall_clock_seconds_used_approx: 2100
    memory_gb_allowed: 16
    maximum_runs_allowed: 1
    runs_used: 1
    runs_note: >-
      One analysis session; three read-only probe executions of pure-Python
      arithmetic over committed git blobs, no lattice computation, negligible
      memory. Host was moderately loaded (14 cores, load ~9-10) and shared with
      the concurrent Validator session TASK-20260815-57bc79; this had no
      bearing on any figure, since none of this review's outputs is a timing
      measurement of its own.

  inference_provenance:
    requested_policy: review-adversarial
    requested_reasoning_effort: xhigh
    resolved_model_identifier_self_report: >-
      claude-opus-5[1m] — reported verbatim from this session's own runtime
      system context ("You are powered by the model named Opus 5 (1M context).
      The exact model ID is claude-opus-5[1m]."), not inferred, guessed, or
      reconstructed from a marketing name, and NOT read from any configuration
      file.
    committed_binding_target_read_for_reference_only: >-
      KEPT DELIBERATELY SEPARATE FROM THE SELF-REPORT ABOVE AND NOT CONFLATED
      WITH IT. orchestration/model-bindings.yaml currently carries another
      session's UNCOMMITTED working-tree edits (`git status` shows it modified);
      it was treated as read-for-reference-only and was never written by this
      session. No value from it is recorded here as this session's resolved
      model.
    reasoning_effort_basis: >-
      xhigh, bound by .claude/agents/red-team.md line 16 (`effort: xhigh`) and
      confirmed by `python3 tools/check_runtime_bindings.py --list`, which
      reports `red-team  policy=review-adversarial  effort=xhigh` with
      `claude_code  .claude/agents/red-team.md  effort:agent file`. Derived from
      orchestration/roles.yaml default_policy review-adversarial, not chosen by
      this session. review-adversarial at xhigh was honoured in full; had it not
      been, this review would have refused rather than downgraded.
    runtime: claude_code
    session_kind: native authenticated session
    fallback_allowed: false
    fallback_used: false
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: >-
      No adapter probe receipt exists for this session; AUTORESEARCH_POLICY and
      AUTORESEARCH_BACKEND are both unset (checked directly: `env | grep -i
      autoresearch` returns nothing). Same gap every producer and review in this
      goal's history records, for the same reason.
    amazon_bedrock_selected_configured_probed_contacted_or_used: false
    amazon_bedrock_note: >-
      AWS_BEARER_TOKEN_BEDROCK IS PRESENT in this session's environment and
      CLAUDE_CODE_USE_BEDROCK IS UNSET (both verified directly). Bedrock is
      refused under AGENTS.md rule 16 as a cost guardrail: no provider, backend,
      endpoint, model identifier or probe containing `bedrock` was selected,
      configured, probed, contacted or used by this session at any point.
    independent_session: true
    independence_kind: >-
      This session is NOT the producer. TASK-20260815-f14d3c ran in a different
      session (run_end 2026-08-15T23:30:29Z) on a different host (Linux, 4
      vCPUs, per environment.json) and, per its own run_manifest.yaml
      `model_answering`, on claude-sonnet-5 — a DIFFERENT resolved model from
      this review's claude-opus-5[1m]. So is BATCH-279acb's Red Team
      (claude-sonnet-5, per its own report). That is a genuine, if partial,
      independence gain and is recorded as such, not overstated: it is one
      vendor's model family reviewing another model in the same family, and
      AGENTS.md rule 12's independence requirement is procedural here, not
      model-level.
    correlated_judgement_disclosure: >-
      THE SIBLING VALIDATOR REVIEW TASK-20260815-57bc79 IS RUNNING CONCURRENTLY
      ON THE SAME MODEL FAMILY AS THIS REVIEW. ANY AGREEMENT BETWEEN THE TWO IS
      CORRELATED SAME-MODEL JUDGEMENT AND MUST NOT BE RECORDED AS
      DISTINCT-MODEL CORROBORATION, in a completion_quorum attestation or
      anywhere else. This session did not read
      coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/reviews/ or any
      file belonging to that task at any point, per its own instruction, and
      received no message from it.
    agent_bus_checked: >-
      `python3 tools/agent_bus.py inbox --as red-team` and `--as red-team-2`
      both return "no unread" — checked on wake and before reporting done, per
      AGENTS.md "Inter-agent messaging".
```
