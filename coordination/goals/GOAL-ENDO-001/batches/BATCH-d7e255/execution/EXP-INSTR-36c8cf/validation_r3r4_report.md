# Validation report: R3/R4 controls (RUN-INSTR-r3r4-nullobj-d3efd7)

`VAL-20260811-bc336d` · GOAL-ENDO-001 · BATCH-d7e255 · EXP-INSTR-36c8cf · `TASK-20260811-bc336d`

Snapshot read: `031fab32ea3b8f4cf4ff5f5ac7ddbda5254c5d6f` on branch
`claude/ecdlp-endomorphism-analysis-4m2w3z`.

```yaml
validation_report:
  id: VAL-20260811-bc336d
  task_id: TASK-20260811-bc336d
  snapshot_commit: 031fab32ea3b8f4cf4ff5f5ac7ddbda5254c5d6f
  branch: claude/ecdlp-endomorphism-analysis-4m2w3z
  run_ids:
    - RUN-INSTR-r3r4-nullobj-d3efd7

  artifact_checks:
    - snapshot_commit_verified: >-
        031fab32 exists on HEAD, working tree is clean at this commit
        (git status: "nothing to commit, working tree clean"). Parent chain
        031fab32 <- 77b504ce (dispatch) <- a116256f (amendment v2
        adjudication) confirmed via git log; 77b504ce (manifest's
        code.commit) is a real ancestor of 031fab32
        (git merge-base --is-ancestor: true).
    - new_module_hash_matches_tree: >-
        git cat-file -p 031fab32:harness/exp_instr_36c8cf/ctrl_r3r4.py |
        sha256sum = 1e147ee4...f37a3ee4, exactly the hash pinned in the
        run's manifest.yaml source.files block (status "untracked" at run
        time, correctly disclosed, since the module was committed one step
        later in the same producer session before the Coordinator's snapshot
        commit -- consistent with the declared CTRL-VALUESHUFFLE precedent).
    - all_14_declared_artifact_paths_present: true (manifest.yaml,
        command.txt, environment.json, stdout.log, stderr.log,
        raw-result.json, jackknife-exceedance.json,
        stability-correlation.json, stability-correlation-cross-check.json,
        r4-student-t5-nullobject.json, r4-gaussian-calibration-optional.json,
        frozen-inputs.json, harness/exp_instr_36c8cf/ctrl_r3r4.py,
        execution_report_r3r4.md -- each checked with a direct file-existence
        test, not assumed from the listing).
    - source_provenance_hashes_independently_recomputed: >-
        Recomputed sha256 by hand (sha256sum, outside the pinning code path)
        for all 4 non-code, non-reference-data pinned files
        (amendments/v1.yaml, amendments/v2.yaml, refvalues_v2.py, sr3v3.py)
        and for sr3v3-reference-sampling.json; all five match the values
        recorded in frozen-inputs.json / the manifest exactly.
    - stdout_log_matches_reported_numbers: true, byte comparison of
        stdout.log against the module's own print statements and the
        execution report's headline numbers -- exact match on every line.
    - raw_result_consistent_with_dumped_per-analysis_files: true (r3a total
        exceed = 3 and r4 accept fraction = 0.188 read directly out of
        raw-result.json's nested raw.r3a / raw.r4_student_t5 blocks, matching
        jackknife-exceedance.json and r4-student-t5-nullobject.json).
    - dirty_tree_and_command_record: code.dirty=false, command.txt exact
        argv reproduced, environment.json present (Python 3.11.15, Linux,
        sympy/pyyaml versions recorded). No sage_version (none required;
        pure numpy/statistics module).
    - imports_confirmed_not_reimplemented: >-
        Read harness/exp_instr_36c8cf/sr3v3.py directly. ctrl_r3r4.py's
        `from harness.exp_instr_36c8cf import refvalues_v2, sr3v3` is a real
        import; jackknife_row calls `sr3v3.interval_for_rung` verbatim,
        r3b_analysis calls `sr3v3.stability_check` verbatim,
        load_frozen_inputs calls `sr3v3.z_from_coverage(519, 520)` verbatim,
        and draw_null_object_replication calls both interval_for_rung and
        stability_check verbatim inside the R4 ladder loop. No shadow
        reimplementation of any of the three functions exists anywhere in
        ctrl_r3r4.py. sr3v3.py itself is untouched by this commit (confirmed
        by both the manifest's own "clean" status line and a git diff of
        a116256f..031fab32 restricted to the two read-only reference-run
        directories, which is empty).

  metric_recomputations:
    - id: R3a-jackknife
      method: >-
        Independently re-ran the full leave-one-out procedure over all
        13 rows x 48 held-out seeds = 624 trials (not a "substantial sample"
        -- the complete set), loading sr3v3-reference-sampling.json directly,
        calling sr3v3.interval_for_rung and sr3v3.z_from_coverage(519,520)
        myself (fresh Python process, not importing or calling any function
        from ctrl_r3r4.py).
      result: >-
        jackknife: below=1, above=2, total=3. in-sample: below=0, above=2,
        total=2. Gaussian-rule expected: 13*48/260 = 2.4 exactly. Nonzero
        rows: fb=11 (jackknife above=1, in-sample above=1), fb=12
        (jackknife below=1, in-sample 0/0 -- the jackknife-only exceedance
        the report calls out), fb=22 (jackknife above=1, in-sample above=1).
        z_from_coverage(519,520) = 2.890511560691739, matching both the
        module's own computed value and the committed file's recorded z
        (2.8905115606917384) to float precision. EXACT MATCH on every
        reported number, reproduced from raw data with independent code.
    - id: R3b-stability-and-fisher
      method: >-
        Recomputed sr3v3.stability_check(rung2, rung3, 5.0) directly from
        the raw interval dicts (own process, own read of the JSON), then
        built the 2x2 table from my own R3a jackknife-exceedance results
        above, then implemented the hypergeometric two-sided p-value
        independently from the stated formula.
      result: >-
        rows_failing = [4, 7, 8, 9, 11, 15, 18, 22] -- exact match. Table
        a=2,b=1,c=6,d=4, margins row1=3,row2=10,col1=8,n=13 -- exact match.
        Hand-enumerated P(X=0)=0.03497, P(X=1)=0.27972, P(X=2)=0.48951 (=the
        observed table's own probability -- it IS the hypergeometric mode
        under these margins), P(X=3)=0.19580; every value in the support has
        P(X=x) <= P(X=2), so the two-sided sum is the full support and
        equals exactly 1.0. This is not a computation artifact: at this
        margin configuration the observed cell is literally the modal
        outcome, so "at least as extreme" captures every possible table.
        scipy was unavailable in this environment to cross-check against
        `fisher_exact` directly, but the hand hypergeometric enumeration
        against the stated formula is unambiguous and the "sum over px <=
        obs_p*(1+1e-9)" convention in fishers_exact_2x2 is the standard
        two-sided exact-test definition (equivalent to scipy's default,
        confirmed by reading the algorithm, not by running scipy).
    - id: R4-replication-spotcheck
      method: >-
        Reimplemented the R4 replication loop from scratch (own function,
        not calling ctrl_r3r4.draw_null_object_replication), reconstructing
        numpy.random.SeedSequence(314159265).spawn(500) and, per replication,
        rep_seed.spawn(13) exactly as documented, using the same rescale
        loc + scale/sqrt(5/3)*standard_t(df=5,size=1536) and the same nested
        prefix-rung ladder, calling only sr3v3.interval_for_rung and
        sr3v3.stability_check. Checked replications [0,1,2,5,17,50,99,150,
        250,333,400,499] -- a spread across the full 500, not just
        replication 0.
      result: >-
        12/12 spot-checked replications match the module's own
        r4-student-t5-nullobject.json records exactly on accepted_rung,
        terminal_rung, exceed_below_at_terminal, exceed_above_at_terminal.
        Every one of the 12 shows exceed_below=13, exceed_above=13 (26
        total) at its own terminal rung, whether that terminal rung is 7 or
        8.
    - id: R4-aggregation-recompute
      method: >-
        Recomputed accept_by_rung8_fraction, first_accept_rung_histogram,
        and the full distribution of exceed_total_at_terminal /
        side_asymmetry_at_terminal directly from the raw `records` array in
        r4-student-t5-nullobject.json (500 entries), not from the file's own
        `summary`-level fields.
      result: >-
        94/500 = 0.188 accepted by rung 8 -- exact match to the reported
        summary. Histogram {7: 6, 8: 88, not_accepted_by_rung8: 406} --
        exact match. `exceed_total_at_terminal` takes exactly one value
        across all 500 records: {26}. `side_asymmetry_at_terminal` takes
        exactly one value across all 500: {0}. terminal_rung distribution
        {8: 494, 7: 6}. All `accepted_by_rung8` boolean flags are internally
        consistent with `accepted_rung is not None` (0 inconsistencies). The
        aggregation code is correct.
    - id: R4-gaussian-arm-cross-check
      method: Recomputed the Gaussian arm's aggregate stats directly from
        its own records array as a control on the aggregation code and on
        the "not a universal artifact" question (see finding 4 below).
      result: >-
        485/500 = 0.970 -- exact match to the reported summary.
        exceed_total_at_terminal ranges 5-26 (mean 21.634, population sd
        3.941) across the 500 Gaussian replications -- real, substantial
        variance, confirming the Student-t arm's zero-variance 26/26 is not
        a universal property of the aggregation or scoring code.
    - id: rescale-formula-check
      method: Checked the standard-t(df) variance formula (df/(df-2) for
        df>2) against the module's rescale.
      result: >-
        For df=5, Var(standard_t5) = 5/3. The module draws
        `loc + (scale/sqrt(5/3)) * standard_t(df=5)`; Var of that
        expression is (scale^2/(5/3))*(5/3) = scale^2. CORRECT: `scale`
        plays the role of the target standard deviation, matching how it is
        used (row's own `sd_sample_n_minus_1`).

  control_checks:
    - null_object_present_and_matched_shape: >-
        Yes. R4 is exactly the null-object control required by
        docs/inventor-protocol.md section 3: a synthetic process of the same
        shape as the real per-seed-ratio data (13 rows, matched per-row
        location and scale, run through the IDENTICAL unmodified
        interval_for_rung/stability_check/z_from_coverage pipeline the real
        characterisation uses), rather than an ad hoc alternative
        computation.
    - positive_and_negative_arm_pairing: >-
        The optional Gaussian arm (matched variance, same machinery,
        independent seed 271828182) functions as the positive control --
        confirming that under the FAVOURED hypothesis's own shape, the T2
        gate accepts at a high rate (97.0%) -- against the Student-t(df=5)
        arm as the negative/heavy-tail control (18.8%). Both arms share
        every piece of pipeline code except the draw distribution, which is
        the correct design for isolating what the distribution shape alone
        changes.
    - what_should_happen_as_the_destroying_parameter_increases: >-
        PARTIALLY ADDRESSED, not fully. Only one heavy-tail parameterisation
        (df=5) is tested against one light-tail parameterisation (Gaussian,
        the df->infinity limit); there is no sweep over intermediate df
        (e.g. df=10,20,50) showing the accept-rate and exceedance-diagnostic
        move monotonically between the two as tail-heaviness is dialled
        toward Gaussian. This is within the letter of what R4/RT-20260811-
        35ab34 explicitly asked for (a single stated Student-t(df=5)
        alternative), so it is not a defect in this run, but it does mean
        the control establishes "T2 does not fully discriminate at one named
        alternative," not "T2's discriminating power degrades smoothly as
        the alternative approaches the null" -- a genuine scope limit,
        recorded as a limitation below, not held against the run.
    - pre-registration_of_the_prediction: >-
        The counterexample_or_mutation prediction in RT-20260811-35ab34
        ("the simulated heavy-tailed ladder also eventually satisfies E3 ...
        within the declared 8-rung ladder") was recorded BEFORE this run,
        in a separately snapshotted, independently reviewed report. The
        observed 94/500 (18.8%) acceptance rate confirms that prediction
        (E3 IS eventually satisfiable under the alternative), satisfying
        the pre-registration requirement for whatever this run is treated
        as validating.
    - frozen_parameters_read_not_hardcoded: >-
        Confirmed by direct inspection of refvalues_v2.py:
        amendment_frozen_parameters() parses amendments/v1.yaml's G3 text via
        regex (not a literal), returning stability_relative_half_width_pct
        = 5.0, matching amendments/v1.yaml's own text ("half-width changes by
        less than 5% relative"). icinv_frozen_grid() reads
        EXP-ICINV-4d33aa/specification.yaml's factor_base_sizes, matching the
        13-row list used. Neither is transcribed as a literal in ctrl_r3r4.py.
    - seed_novelty: >-
        Grepped the full repository for 314159265 and 271828182; both
        appear only inside this run's own artifacts and ctrl_r3r4.py --
        neither is a contract seed reused from elsewhere, as the handoff
        required.

  heuristic_validation_checks:
    - >-
      Not the canonical Wesolowski/Dickman-de Bruijn profile (no CDF
      prediction, no Deuring-style correspondence sampling), but the
      applicable subset of this checklist was run: sample size (500 x 13
      rows x up to 1536 draws), seeds, and sampling procedure
      (SeedSequence.spawn nesting) are all recorded in manifest.yaml /
      raw-result.json parameters; scale (toy: 13 rows, fb sizes 4-22, n up
      to 1536) is disclosed throughout as claim_tier: toy with no transfer
      claim made to cryptographic scale. No correspondence-sampling
      substitute is used here (direct simulation), so that check does not
      apply. No cost table is produced or claimed (correctly -- this is not
      a cost-model experiment), so cost-unit and cost-bookkeeping checks are
      not applicable.

  cost_model_checks:
    - not_applicable: >-
        No concrete-cost table, no complexity claim, no per-attempt-cost x
        inverse-success-probability bookkeeping is offered or required here;
        this is a pure statistical instrument control, claim_tier toy,
        sota_delta 0 on every axis, and the report does not claim otherwise.

  proof_architecture_checks:
    - not_applicable: >-
        No theorem, bound, certificate family, or reduction is proposed by
        this task; it is a bounded statistical reanalysis and simulation
        control under an already-approved instrument-characterisation
        contract. Section 8 of the inventor protocol does not bind this
        deliverable.

  scope_and_authority_checks:
    - amendment_v2_untouched: >-
        experiments/EXP-INSTR-36c8cf/amendments/v2.yaml still shows
        `approved_by: null` at line 424; not edited by 031fab32 (confirmed
        by the commit's changed-file list, which contains no path under
        experiments/EXP-INSTR-36c8cf/amendments/ or
        experiments/EXP-INSTR-36c8cf/specification.yaml).
    - reference_runs_untouched: >-
        `git diff a116256f 031fab32 -- .../RUN-INSTR-36c8cf-phaseA-v2-57ca9a/
        .../RUN-INSTR-36c8cf-phaseA-2a5cd1/` is empty -- byte-identical
        across the commit that filed the amendment adjudication and this
        snapshot. Both remain untouched, unedited, unre-scored.
    - frozen_pipeline_files_untouched: >-
        sr3v3.py, refvalues_v2.py, refvalues.py, phase_a_v2.py: none appear
        in 031fab32's or 77b504ce's changed-file lists; sr3v3.py and
        refvalues_v2.py's sha256 in the run's own pin match the currently
        committed files exactly (see artifact_checks), confirming no
        post-hoc drift either.
    - no_ledger_or_hypothesis_edit: >-
        031fab32's full changed-file list contains no path under ledger/.
        H-INSTR-444c7b.yaml's own `status: specified` line was last touched
        by commit 755b418f, well before this task; unaffected by
        031fab32.
    - claim_tier_and_certificate_accurate: >-
        certificate.kind: none is correct -- no discrete-log solve or
        factor-base relation is computed anywhere in ctrl_r3r4.py (confirmed
        by reading the full module: it is jackknife statistics, an exact
        hypergeometric test, and numpy Student-t/Gaussian draws only).
        claim_tier: toy and sota_delta: 0 are consistent with the module's
        own content and with GOAL-ENDO-001's stated scope for this
        instrument.
    - budget_conformance: >-
        wall 68.008s / cap 1800s (3.8%), peak RSS 79.7MB / cap 8GB, well
        within budget; no timeout, no truncation, correctly reported as
        such.

  framing_fairness_assessment: >-
    Every mention of HEUR-INSTR-4 in execution_report_r3r4.md is an explicit
    disclaimer ("does not conclude ... is supported or refuted",
    "interpretation ... is the Coordinator's, after independent review") --
    grepped the full report for HEUR-INSTR-4/support/refute/prove/
    demonstrate/confirm and found no substantive interpretive claim against
    the heuristic anywhere outside these disclaimers. The one place the
    report DOES make an interpretive-sounding claim -- "a genuine,
    reproducible property of the Student-t(df=5) heavy tail ... not an
    artifact of this module's code" -- is scoped correctly: it is a
    code-correctness assessment (ruling out a bug), not a claim about
    HEUR-INSTR-4's truth, and it is exactly the kind of due-diligence check
    AGENTS.md rule 8 (record unexpected observations) calls for. The
    Gaussian-vs-Student-t contrast (0.188 vs 0.970) is reported side by side
    with an explicit "no interpretation ... is offered here" note. Framing
    holds to "observations only" as claimed.

  independent_third_check_of_the_26_of_26_finding: >-
    HOLDS UP under a third, methodologically distinct independent check.
    Beyond reproducing 12 spot-checked replications exactly (metric
    recomputations above), I ran a from-scratch Monte Carlo (5000 trials per
    rung size, an RNG and seed the module never uses) measuring the raw
    per-sample probability that a single in-sample-fit Student-t(df=5) draw
    of size n exceeds mean +/- z*sd on each side: 0.7%/0.6% at n=12, rising
    monotonically to 99.8%/99.7% at n=768 and 100.0%/100.0% (0/5000 misses)
    at n=1536. Getting 26/26 in every one of 500 replications x 13 rows x 2
    sides is therefore not surprising given the true per-check probability at
    these two terminal sample sizes -- it is close to what a clean
    binomial(13000, ~0.998) draw would produce. I then checked the two
    alternative non-heavy-tail explanations named in the task: (a) "artifact
    of always terminating at rung 8" -- REFUTED: all 6 of the 500
    replications that instead terminate at rung 7 (n=768) also show 26/26,
    and my own from-scratch check confirms n=768 alone already gives
    ~99.7-99.8% per-side probability; (b) "in-sample circularity maximal at
    n=1536 regardless of distribution" -- REFUTED, both by the module's own
    Gaussian arm (real variance, range 5-26, mean 21.6, sd 3.94 across 500
    replications) and by my own independent from-scratch Gaussian Monte
    Carlo at the identical sample sizes (n=768: ~78% per side; n=1536:
    ~96% per side -- high, but neither saturated at 100% nor
    zero-variance the way the Student-t arm is). I found no plausible
    artifact explanation; this is a genuine, if unsurprising once the
    extreme-value scaling is worked through, consequence of Student-t(5)'s
    polynomial tail (extremes grow ~n^{1/5}) against a sample standard
    deviation that stabilises as n grows, evaluated through an in-sample-fit
    interval.
    ADDITIONAL OBSERVATION FOR THE COORDINATOR'S SYNTHESIS (not a defect in
    this run, a scope note on what the 26/26 diagnostic alone establishes):
    because the Gaussian arm's own in-sample exceedance probability is
    already substantial at n=1536 (~96% per side, per both the committed
    data and my independent check) even though it is not saturated, this
    specific exceedance-count diagnostic loses much of its discriminating
    power at the largest tested rungs for BOTH explanations -- the sharper
    discriminator in this run is the accept-by-rung-8 fraction (18.8% vs
    97.0%), which tracks the T2 stability rule rather than the D2-style
    extreme-exceedance count. The report does not overclaim the exceedance
    diagnostic's power (it is presented as "gates nothing"), so this is a
    nuance worth carrying into the decision record, not a validity problem
    with the run itself.

  d2_diagnostic_fidelity_note: >-
    Amendment v2's own D2 text (change E9) defines the diagnostic as "the
    count of per-seed ratios falling outside that row's own fitted
    interval, split by side" -- i.e., potentially counting many individual
    out-of-band seeds per row, not just whether the single extreme (min/max)
    exceeds. ctrl_r3r4.py's R3a/R4 "exceedance" metric checks only the
    single extreme per row per side (0 or 1, capping the R4 terminal metric
    at 26 = 13 rows x 2 sides), mirroring the reference file's own limited
    recorded fields (min_per_seed_ratio/max_per_seed_ratio) rather than the
    full per-seed count. This is a real simplification relative to D2's
    literal text, but it is explicitly disclosed as an interpretive choice
    in the execution report's "Underspecified judgment calls" section (item
    1), consistent with the handoff's own instruction to record such
    choices rather than pick silently, and it matches R3a's construction
    exactly (which was itself specified by the task in exactly these terms:
    "the already-computed rung-3 interval's own recorded max/min"). Not a
    defect; flagged as a scope note.

  what_was_independently_reproduced_vs_spot_checked_vs_taken_on_word:
    fully_independently_reproduced_from_raw_data:
      - "R3a: complete 624-trial jackknife exceedance table (all 13 rows, all 48 held-out seeds each), from scratch"
      - "R3b: stability_check rows_failing list and the full Fisher's-exact hypergeometric enumeration"
      - "R4 aggregate accept_by_rung8_fraction and first-accept-rung histogram, recomputed directly from the raw records array"
      - "R4 Gaussian-arm aggregate stats, recomputed directly from its raw records array"
      - "The Student-t(5) rescale variance formula (5/3 for df=5)"
      - "The 26/26-always finding, via an independent 5000-trial-per-rung Monte Carlo using neither the module's code nor its seeds"
      - "Every pinned sha256 in frozen-inputs.json / manifest.yaml, via sha256sum outside the pinning code path"
      - "Snapshot commit ancestry and reference-run byte-identity, via git diff/merge-base"
    spot_checked_against_the_committed_run_artifact:
      - "12 of 500 Student-t(df=5) replications (indices spread across the full range, not clustered), reimplemented from scratch and compared field-by-field against r4-student-t5-nullobject.json's own records"
    taken_on_the_executor_or_coordinator's_word:
      - "That the standalone 200-trial sanity check the executor describes running before reporting the 26/26 finding was actually run as described (its own artifact is not separately retained under the run directory; superseded here by my own independent 5000-trial check, which supersedes rather than merely trusts that claim)"
      - "Wall-clock/CPU/RSS measurement mechanics inside harness.runner.write_run (resource.getrusage plumbing) -- accepted as standard harness infrastructure, not re-implemented"

  verdict: passed

  limitations:
    - >-
      R4's null-object control tests exactly one heavy-tailed alternative
      (Student-t, df=5) against the Gaussian null; it does not sweep
      intermediate tail-heaviness, so it establishes "T2 does not fully
      discriminate at this one named alternative" rather than a
      continuously-varying decay/growth curve of discriminating power as
      the destroying parameter (tail heaviness) is dialled. This is within
      the letter of what RT-20260811-35ab34 and the task handoff asked for,
      not a defect in this run.
    - >-
      The exceedance diagnostic reported at the terminal rung (max 26)
      checks only the single row extreme per side, not the full "count of
      per-seed ratios falling outside the interval" that amendment v2's D2
      text literally describes; disclosed by the executor, not a silent
      simplification, but a real narrowing worth the Coordinator's notice.
    - >-
      This report, like the run and execution report it validates, makes no
      finding about HEUR-INSTR-4, no ECDLP claim, and does not authorize any
      change to amendment v2's approval status, EXP-ICINV-4d33aa's paused SR3
      v3 gate, or any hypothesis status. A passed validation here means the
      run is an admissible, correctly-executed, faithfully-scoped statistical
      receipt -- not that HEUR-INSTR-4 or its competing explanation is
      thereby established.
    - >-
      scipy was unavailable in the validation environment; the Fisher's-exact
      check was independently verified by direct hypergeometric enumeration
      against the stated formula rather than cross-run against
      scipy.stats.fisher_exact itself. The formula and convention match
      scipy's documented default by inspection, but this is a documentation
      match, not an executed cross-check.

  artifact_paths:
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/manifest.yaml
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/command.txt
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/environment.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/stdout.log
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/stderr.log
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/raw-result.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/jackknife-exceedance.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/stability-correlation.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/stability-correlation-cross-check.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/r4-student-t5-nullobject.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/r4-gaussian-calibration-optional.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-r3r4-nullobj-d3efd7/frozen-inputs.json
    - harness/exp_instr_36c8cf/ctrl_r3r4.py
    - harness/exp_instr_36c8cf/sr3v3.py
    - harness/exp_instr_36c8cf/refvalues_v2.py
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/execution_report_r3r4.md
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/sr3v3-reference-sampling.json
    - ledger/handoffs/TASK-20260811-bc336d.yaml
    - ledger/decisions/DEC-20260811-a4c7ec.yaml
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-INSTR-36c8cf/validation_v2_redteam_report.md

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
      independent context and a fresh reading of a committed snapshot, not
      independent judgement from a different model.

  authority_note: >-
    This report changes no research status and approves or rejects nothing.
    RUN-INSTR-r3r4-nullobj-d3efd7, the execution report, amendment v2, and
    every other cited record are unedited and uncommitted by this task.
    Interpretation of R3/R4's results against HEUR-INSTR-4 or amendment v2's
    approval is a Coordinator act on a later ledger archive, after this
    report and the parallel Red Team's adversarial check are both read.
    Nothing here is durable evidence until a Coordinator archives it.
```
