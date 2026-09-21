# RED TEAM REPORT — TASK-20260814-fe02ff

```yaml
red_team_report:
  id: RT-20260814-fe02ff
  task_id: TASK-20260814-fe02ff
  claim_under_review: >
    TASK-20260814-ffd791's own report (writeup.md, environment.json,
    run_manifest.yaml, stage0_results.json, committed at snapshot
    dc61fe376a7108b4dd58110f856db5c7589cde86): PREREG-8 section 1 (fpylll
    install/callable, CBD/FIPS-203 re-derivation, batched-vs-scalar Babai
    exactness) ALL PASSED; PREREG-8 section 2 (Stage 0) found 0/6 main-grid
    (d,beta) cells cleared -- every cell failed identically with
    fpylll.util.ReductionError('infinite loop in babai'), characterized as
    "a genuine incompatibility between this host's fpylll 0.6.4 / fplll
    build and BKZ's own internal LLL preprocessing," "not resolved by the
    one alternative precision setting that could be tested to a definite
    result [mpfr]"; termination branch T-PROJNOISE-NODATA fires for the
    whole package; the producer recommends NOT dispatching Stage 1 as
    written and instead investigating the fpylll/fplll root cause (upstream
    issue tracker, alternate build/version, alternate basis construction)
    before any further Stage-0 re-run.
  objections:
    - id: OBJ-1-ROOT-CAUSE-MISATTRIBUTED
      severity: critical
      text: >
        The producer's own root-cause characterization is not supported by
        this session's own independent, reproducible testing. Reading
        fpylll 0.6.4's own installed source
        (/usr/local/lib/python3.11/dist-packages/fpylll/algorithms/bkz.py,
        BKZReduction.__init__) shows that when handed a raw IntegerMatrix
        (exactly what stage0_feasibility.py's worker_main_cell does),
        BKZReduction ALWAYS builds its own internal GSO with
        `GSO.Mat(A, flags=GSO.ROW_EXPO)` -- and this session confirmed live
        (probes 1/3/4/5/6) that GSO.Mat's float_type defaults to "double"
        with NO precision escalation, regardless of what float_type any
        earlier, separate LLL.reduction(A) call used (LLL.reduction's own
        method=None default resolves to fplll's precision-escalating
        "wrapper" strategy, which is almost certainly why the standalone
        pre-reduction call in worker_main_cell succeeds while BKZReduction's
        own internal, un-escalated LLL call fails moments later).
        This session (probe3) reproduced the EXACT reported failure
        (d=256, beta=40, seed_used=1398073216, matching the producer's own
        reported seed bit-for-bit) using ONLY BKZReduction's own internal
        construction, with ZERO reference to BKZ.Param or any strategies
        file -- decisively ruling out DEV-1 (the strategies-file
        substitution) as a cause (see OBJ-2). This session then (probe5)
        constructed an EXPLICIT, correctly-configured higher-precision
        GSO.Mat (float_type="mpfr", FPLLL.set_precision(212) called first
        per GSO.Mat's own docstring instructions, no GSO.ROW_EXPO since
        documented incompatible with mpfr) and passed it directly into
        BKZReduction -- on the SAME (d=256, beta=40, seed=1398073216)
        instance the producer reports failing. The internal LLL step that
        fails under the default construction SUCCEEDS in 0.0038s under this
        explicit-precision construction (probe5_result_d256_mpfr212.json).
        This directly contradicts the producer's own environment.json claim
        ("float_type_mpfr: FAILED -- identical ReductionError... effectively
        instantly. Rules out a simple default-precision explanation.").
        Because the producer's own mpfr diagnostic is disclosed as
        "out-of-band" with NO surviving script or artifact anywhere in this
        task's write_scope (only a one-sentence summary in environment.json),
        this session cannot inspect what code path that diagnostic actually
        exercised -- but the most parsimonious explanation for "FAILED,
        effectively instantly, identical exception" is that it made the
        SAME mistake the main-grid worker itself makes: applying
        float_type="mpfr" to a call that never propagates into
        BKZReduction's own internal GSO construction (e.g., passing mpfr to
        the outer LLL.reduction(A) call while still handing the raw,
        already-processed IntegerMatrix to BKZReduction(A) afterward, which
        silently rebuilds its own double-precision GSO from scratch and
        discards the outer call's precision setting entirely). This is a
        plausible, concrete, and testable hypothesis for why an
        apparently-negative mpfr control produced a false negative; it is
        not asserted as certain because the diagnostic's own code does not
        survive to inspect.
    - id: OBJ-2-STRATEGIES-FILE-RULED-OUT
      severity: informational (closes part (b) of the task handoff cleanly)
      text: >
        DEV-1 (substituting the OS package strategies path
        /usr/share/libfplll8/strategies/default.json for the wheel's own
        absent baked-in path) is NOT implicated. probe3 reproduces the exact
        failure by calling ONLY `GSO.Mat(A, flags=GSO.ROW_EXPO)` +
        `LLL.Reduction(M, flags=LLL.DEFAULT)` + `lll_obj()` directly --
        the exact call BKZReduction.__call__ makes at bkz.py line 123 --
        with NO BKZ.Param object ever constructed and NO strategies file
        ever opened or referenced anywhere in the probe. The failure occurs
        during BKZ's own internal LLL preprocessing step, which
        (independently confirmed by reading fplll's own pruning/strategy
        consumption point, deferred to block-enumeration inside tour(), never
        reached here) has no dependency on the strategies file at all. The
        producer's own run_manifest.yaml already labels DEV-1 "severity: low,
        affects_result_validity: false" -- this session's own independent
        test confirms that labeling is correct, not merely asserted.
    - id: OBJ-3-BASIS-CONSTRUCTION-IS-STANDARD
      severity: informational (closes part (a)'s basis-construction half)
      text: >
        `IntegerMatrix.random(d, "qary", k=d // 2, q=3329)` is not a bug or
        non-standard usage. fpylll's OWN installed docstring for
        IntegerMatrix.random gives `IntegerMatrix.random(10, "qary", k=8,
        q=127)` as its canonical worked example -- the producer's call is
        the textbook pattern with different (still entirely reasonable)
        numeric parameters. The defect part (a) asked this review to hunt
        for is real, but it is in the BKZReduction wrapping (OBJ-1), not in
        the basis construction line.
    - id: OBJ-4-FREE-FUNCTION-NOT-A-SAFE-ALTERNATIVE
      severity: medium
      text: >
        The producer's own toy-floor sweep uses the top-level free function
        `fpylll.BKZ.reduction(A, par)` (float_type=None, documented as
        "automatic choice") rather than the OOP BKZReduction class the
        main-grid worker uses. This session tested (probe7) whether that
        free function auto-resolves the precision issue at d=224, beta=40
        (a dimension confirmed failing under BKZReduction). It does NOT:
        the free function hits the identical underlying "infinite loop in
        babai" fplll-internal condition -- but through a code path that does
        not cleanly raise a catchable Python exception. It throws an
        UNCAUGHT C++ std::runtime_error that calls std::terminate() and
        aborts the whole process, only rescued into a catchable
        `RuntimeError: Aborted` by cysignals' own signal-to-exception
        machinery (DEV-2's installed dependency). Two implications: (i) this
        further confirms the underlying condition is a genuine,
        cross-entry-point numerical/precision limitation of double-precision
        fplll at this lattice scale, not an artifact specific to the
        BKZReduction class's own construction; (ii) the free function is
        NOT a safe drop-in fix and should not be recommended as one --
        it trades a clean, catchable ReductionError for an uncaught abort
        that a less carefully signal-hardened harness could crash on
        silently. The correct, validated fix remains OBJ-1's explicit
        GSO.Mat construction.
    - id: OBJ-5-FOLLOWUP-RECOMMENDATION-POINTS-THE-WRONG-DIRECTION
      severity: high
      text: >
        Because OBJ-1 falsifies the producer's own "not resolved by the one
        precision setting that could be tested" claim, the producer's
        follow-up recommendation ("the blocking question for any follow-up
        is a genuine infrastructure root-cause investigation... filing/
        checking this exact exception against the fpylll/fplll upstream
        issue tracker... testing an entirely different fpylll/fplll build
        or version... sizing is not the bottleneck") is not well-supported
        as stated. This session's own reproducible finding points to a
        cheaper, already in-scope, already-attempted-but-apparently-
        mis-executed fix (explicit precision management via fpylll's own
        documented GSO.Mat(float_type=...) parameter) rather than an
        upstream bug report or a different fplll build. This does not mean
        Stage 1 should be dispatched as currently written (see
        narrowest_supported_statement) -- it means the CORRECT next action
        is "re-run Stage 0 with an explicit-precision GSO construction and
        remeasure real per-cell cost," not "investigate whether this is a
        fixable fpylll bug," because this session has already shown it is
        fixable by ordinary fpylll usage, at a cost this task's own scope
        did not measure (see cost_model_challenges).
  required_controls:
    - >
      Re-run stage0_feasibility.py's worker_main_cell with BKZReduction
      constructed from an EXPLICIT, adequately-precise GSO.Mat (not a raw
      IntegerMatrix) across all 6 (d,beta) cells, under the SAME
      PER_BASIS_FEASIBILITY_CAP=3600s, and report real per-cell
      wall-clock/tours/delta -- this session's own probe6 (launched, see
      artifact_paths) targets exactly this at the cheapest real grid cell
      (d=256, beta=40) but a full 6-cell sweep at the correct minimal
      adequate precision was out of this review's own budget.
    - >
      Determine the MINIMUM adequate mpfr precision (this session used 212
      bits somewhat arbitrarily, well above what may be strictly needed;
      bisecting between ~64 and 212 bits would materially change per-cell
      cost, since mpfr cost scales with precision) before quoting any
      Stage-1 budget re-derivation from an mpfr-based fix.
    - >
      Re-run the toy-floor sweep with TOY_ETA=eta1=3 (the alternative,
      more-conservative CBD parameter the producer's own writeup flags as
      unresolved by PREREG-8's own text) as a sensitivity check on the
      selected toy-floor d=12 -- the producer's own choice (eta2=2) is
      disclosed, not hidden, but it is also the choice that "gives faster,
      LESS conservative timings" per the producer's own words, i.e. it is
      the more favorable of the two readings for clearing a larger d; this
      is worth an explicit, cheap (900s-capped) confirmatory run before any
      later Stage-1 sizing decision leans on d=12.
    - >
      Re-derive PREREG-8 section 6's own budget ceiling (currently based on
      DOUBLE-precision "general background knowledge") under an mpfr-cost
      assumption before any Stage-1 dispatch decision, since OBJ-1/OBJ-5
      show double precision does not complete at all on this class of
      instance at d in {256,512} -- the relevant per-basis cost for sizing
      is now the (materially higher, unmeasured-to-completion by either the
      producer or this review) mpfr cost, not the double-precision estimate
      PREREG-8 section 6.2 cites.
  counterexample_or_mutation: >
    Probes 3 and 5 together are the counterexample to the producer's own
    "genuine, unfixable incompatibility" framing: probe3 shows the failure
    reproduces with zero reference to BKZ.Param/strategies (ruling out
    DEV-1), and probe5 shows the SAME exact failing (d, beta, seed) instance
    succeeds cleanly (0.0038s for the internal LLL step) once BKZReduction
    is handed an explicitly-configured higher-precision GSO.Mat instead of
    a raw IntegerMatrix. This is a genuine mutation of the producer's own
    code (one construction choice changed, nothing else) that flips the
    outcome from ERROR to COMPLETED at the exact instance in question.
  baseline_comparison: >
    NOT APPLICABLE at this task's own claim tier and scope, and this is
    stated here rather than left silently unaddressed. This task produces
    NO C1/C2 finding, no discrete-log solve, no relation, and no claim about
    ML-KEM security or attack cost (PREREG-8 section 8 and this task's own
    FORBIDS clause under T-PROJNOISE-NODATA bar exactly that). There is
    therefore no headline "gain" to compare against Pollard-rho, BSGS, or a
    specialized lattice-reduction baseline -- this is an infrastructure
    feasibility report, and the correct baseline question (is fpylll BKZ at
    d in {256,512} feasible at all on this host, at what real per-basis
    cost) is exactly what Stage 0 exists to answer and what this review's
    own OBJ-1/OBJ-5 show was NOT correctly answered by the producer's report
    as written.
  heuristic_challenges: []
  cost_model_challenges:
    - id: COST-1-CAPS-APPLIED-CORRECTLY
      text: >
        CHECKED, CLEAR. PER_BASIS_FEASIBILITY_CAP=3600s and
        TOY_FLOOR_FEASIBILITY_CAP=900s match PREREG-8 section 6.3's own
        frozen numbers exactly and are applied exactly as coded in
        stage0_feasibility.py (`PER_BASIS_FEASIBILITY_CAP = 3600`,
        `TOY_FLOOR_FEASIBILITY_CAP = 900`, enforced via
        run_capped_subprocess's own hard wall-clock kill, polled at 0.5s
        intervals, SIGTERM then SIGKILL fallback) -- not loosened, not
        tightened, no silent per-cell exception. The task-level component
        estimates in the dispatch_queue.json budget_justification
        (fpylll install <=1800s, CBD/compression <=120s, batched-Babai
        <=120s) are TASK-DISPATCH sizing estimates, not PREREG-8 section
        6.3 caps themselves -- PREREG-8's own text does not itemize those
        three components separately, only PER_BASIS_FEASIBILITY_CAP and
        TOY_FLOOR_FEASIBILITY_CAP are its own frozen numbers, and both were
        checked directly against the code, not merely against the writeup's
        prose.
    - id: COST-2-OUT-OF-BAND-DIAGNOSTIC-DISCLOSED-BUT-NOT-SUMMED
      severity: low
      text: >
        The ~650s "out-of-band" float_type diagnostic (mpfr/dd/qd near-
        instant, long-double run ~630s then SIGKILLed) is honestly disclosed
        in run_manifest.yaml as excluded from the official Stage-0 script
        timer, but writeup.md's own "Budget accounting" table total row does
        not explicitly add it back in. This is IMMATERIAL here (3466 + 650 =
        4116s, still far under the 25200s task cap), but it is an omitted
        line in the disclosed total, checked and found non-material rather
        than left unaddressed.
    - id: COST-3-REDUNDANT-INTERNAL-LLL-CALL-UNATTRIBUTED
      severity: low
      text: >
        BKZReduction.__init__, when given a raw IntegerMatrix that has
        ALREADY been through the worker's own explicit `LLL.reduction(A)`
        call, redundantly re-runs `LLL.reduction(A)` a SECOND time inside
        its own constructor (`if M is None and L is None: LLL.reduction(A)`
        -- confirmed by reading the installed bkz.py source). This second
        call's own wall-clock time falls in the gap BETWEEN
        worker_main_cell's own `lll_elapsed` timer (stops after the first,
        explicit call) and `bkz_elapsed` timer (starts after
        `BKZReduction(A)` has already been constructed) -- i.e. it is spent
        but attributed to neither internal sub-timer. This does NOT affect
        the headline per-cell figures actually reported (those are the
        PARENT's own overall subprocess wall-clock, which correctly
        includes everything), and the ERROR cells never reach the success
        branch that reports the two sub-timers at all -- so this is a
        latent bookkeeping gap that would only bite a FUTURE successful
        cell's own internal breakdown, not a live defect in what was
        actually reported here.
    - id: COST-4-MPFR-FIX-COST-IS-UNMEASURED-AND-LIKELY-LARGE
      severity: high
      text: >
        This is the material cost gap. OBJ-1 shows the LLL-step failure is
        fixable with explicit mpfr precision, but this session's own probe6
        (a FULL bkz(par, tracer=True) tour at d=256, beta=40, mpfr-212 bits,
        the exact cell the producer reports failing in 70.2s under double
        precision) had NOT completed, errored, or shown any sign of
        stalling/looping after ~684s (~11.4 minutes) of essentially
        continuous, steady single-core CPU consumption -- at which point
        this review MANUALLY TERMINATED it (SIGTERM then SIGKILL) to keep
        this review's own overall 5400s task budget under control, rather
        than letting it run to its own self-declared 2400s bound (see
        probe6_result_d256_b40_mpfr212.json). This is an honest, disclosed
        early stop, not a fabricated timing or a silently discarded result
        -- the process never reached its own json.dump call, so no
        fabricated completion figure is reported anywhere. A companion probe
        (probe2, full tour at the cheaper d=224) also did not complete
        within a 120s exploratory bound and was terminated rather than
        fabricated. Both observations point the same direction: a full
        mpfr-precision BKZ tour at these dimensions is genuinely, materially
        more expensive than the double-precision estimate PREREG-8 section
        6.2 cites ("well under a minute to on the order of an hour"), which
        assumed double precision throughout. ANY Stage-1 sizing decision
        that treats "the fix is free once precision is corrected" would be
        wrong; the honest state is "the LLL-step ROOT CAUSE is understood
        and fixable, but the FIXED per-basis COST at d in {256,512} is not
        yet measured by either the producer's report or this review, and
        preliminary evidence suggests it is substantially larger than the
        PREREG-8 section 6.2 double-precision estimate." This directly
        engages CLAUDE.md's own bookkeeping requirement (total expected
        cost, not per-attempt cost alone) -- the "attempt succeeds" question
        (OBJ-1) and the "what does a successful attempt cost" question
        (COST-4) are separate, and this task's own report answers neither
        for the fixed construction.
  reduction_and_scope_challenges:
    - >
      No corollary or reduction is claimed anywhere in this task's own
      scope (PREREG-8 sections 1-2 only); T-PROJNOISE-NODATA's own FORBIDS
      clause is respected in writeup.md (no C1/C2 statement, no ML-KEM
      security claim). No scope-inflation objection applies to what was
      actually claimed. The objection in this report is entirely about
      whether the STATED REASON for T-PROJNOISE-NODATA firing ("genuine
      incompatibility... not resolved by the one precision setting tested")
      is itself correct, not about whether the branch's own licensed
      scope was respected -- it was.
  proof_architecture_challenges: []
  narrowest_supported_statement: >
    T-PROJNOISE-NODATA firing for the whole package, as actually configured
    and actually run (raw IntegerMatrix -> BKZReduction, default
    float_type="double", strategies file at the OS package path), is
    CORRECT and this review does not challenge it: 0/6 main-grid cells
    genuinely did not reach a completed reduction under exactly that
    construction, exactly as reported, and PREREG-8 section 2.3/4.3(1)(b)'s
    own decision rule is correctly applied to that observation. What this
    review challenges is narrower and sits one level up: the producer's own
    CHARACTERIZATION of WHY (an unfixable, upstream fplll/fpylll
    incompatibility, "not resolved by the one precision setting that could
    be tested") is not supported by this session's own independent,
    reproducible testing on the SAME host, SAME commit, SAME seed formula,
    and SAME failing instances -- an explicitly-configured higher-precision
    GSO.Mat resolves the isolated failing call cleanly and near-instantly.
    The producer's own bottom-line ACTION recommendation ("do not dispatch
    Stage 1 as written") is still reasonable on this review's own evidence,
    but for a DIFFERENT and narrower reason than stated: not because the
    reduction "does not run at all on this environment's current build,"
    but because (a) the fix is a precision-construction change this task's
    own scope did not attempt correctly, and (b) even once fixed, the real
    per-basis cost under that fix is UNMEASURED and this session's own
    bounded probing suggests it is materially larger than PREREG-8's own
    double-precision cost estimate -- which itself would need a fresh
    Stage-0 remeasurement, at the corrected construction, before any
    Stage-1 grid is sized. Do not read this report as licensing "Stage 0
    actually cleared" or "C1/C2 are now testable" -- neither is true on the
    evidence gathered here; this report narrows WHY Stage 0 failed and
    WHAT the cheapest next step is, nothing more.
  next_concrete_action: >
    Before any Stage-1 sizing decision: dispatch a small, cheap,
    SEPARATELY-SCOPED follow-up task (not this review, which holds no
    write authority to modify stage0_feasibility.py or re-run it as an
    official measurement) that (1) fixes worker_main_cell to construct
    BKZReduction from an explicitly-configured GSO.Mat instead of a raw
    IntegerMatrix, (2) determines the minimum adequate precision by
    bisection rather than an arbitrary 212-bit choice, (3) re-runs all 6
    main-grid cells under PER_BASIS_FEASIBILITY_CAP=3600s with that fix, and
    (4) reports whatever real per-cell wall-clock/tours/delta numbers result
    -- honestly, including NOT_COMPUTED for any cell that still exceeds the
    cap even under the fix. Only THAT task's own output, not this review,
    should be used to decide whether/how Stage 1 is eventually sized.
  artifact_paths:
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/red_team_report.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe1_reproduce_baseline.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe1_result_d256_b40.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe2_fix_via_explicit_gso.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe2_result_d224_mpfr212.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe3_isolate_lll_step_no_strategies.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe3_result_d256_b40.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe4_dimension_scan.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe4_result.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe5_precision_fix_at_cheapest_failing_d.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe5_result_d224_mpfr212.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe5_result_d256_mpfr212.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe6_full_bkz_with_precision_fix.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe6_stdout.log
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe6_stderr.log
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe6_result_d256_b40_mpfr212.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe7_free_function_auto_precision.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/probe7_result_d224_b40.json
```

---

## Narrative summary (for a human/coordinator reader; the YAML block above is the binding record)

### 1. Chain-of-custody / notarization check (completion gate 1)

Verified with git plumbing, in this worktree, in both directions:

- `coordination/.../TASK-20260814-dfaa60/prereg.md` is **absent** at
  `07107b594a8531edc7c6b47ee6bb84c607ba1cba` (TASK-20260814-518949's parent)
  — only `task_card.md` exists there — and **present** at the notarizing
  commit `cf9520cf5507dff126632e2598fc90e689e996c2`.
- Zero producer/measurement artifacts under
  `TASK-20260814-ffd791/` exist at `cf9520cf...` itself (confirmed empty
  `git ls-tree`).
- All 12 of TASK-20260814-ffd791's own artifacts are **absent** at
  `e9894ed0dccd9f555ab13307afdc6d3b8f0361d9` (cb26de's parent, except
  `task_card.md`, added by the intervening dispatch commit `e9894ed0d`
  itself — not a producer/measurement artifact) and **all first appear** at
  `dc61fe376a7108b4dd58110f856db5c7589cde86` (cb26de, the specified snapshot
  commit).
- Spot-checked three declared `path_sha256` values
  (`stage0_results.json`, `writeup.md`, `prereg.md`) against
  `git show <sha>:<path> | sha256sum` — all three match exactly.
- Confirmed `dc61fe376a7108b4dd58110f856db5c7589cde86` is an ancestor of
  this worktree's HEAD (`6add9cbb7...`) before starting.

All artifacts this report cites were read **COMMITTED** (worktree
confirmed clean via `git status --porcelain` for every path read, aside
from this review's own new, uncommitted `reviews/TASK-20260814-fe02ff/`
directory).

### 2. The central finding

`fpylll` 0.6.4 happens to be genuinely installed in this review's own
execution environment (same container/commit as the producer), so this
review did not have to take the producer's report on faith — it reproduced
the failure, isolated its exact cause, and tested a fix, live:

1. **probe1** reproduces the producer's exact (d=256, beta=40) failure,
   including the identical `seed_used=1398073216` — independently
   confirming `SEED_ROOT=715923` / the `default_rng([...])` formula was
   genuinely used, not merely declared (a required completion-gate check).
2. **probe3** reproduces the identical failure using *only* the exact
   internal call `BKZReduction.__call__` makes
   (`GSO.Mat(A, flags=GSO.ROW_EXPO)` → `LLL.Reduction(...)` → `lll_obj()`),
   with **zero reference to `BKZ.Param` or any strategies file** —
   decisively ruling out DEV-1 (the OS-package strategies-file
   substitution) as a cause.
3. **probe4** scans dimension and finds the failure threshold: d=192
   succeeds (double precision, ~11s), d=224 fails — a genuine,
   dimension-dependent numerical phenomenon, not a fluke.
4. **probe5** constructs an explicit, correctly-configured mpfr GSO
   (`FPLLL.set_precision(212)` then `GSO.Mat(A, float_type="mpfr")`, no
   `ROW_EXPO`) and passes it directly into `BKZReduction` — on the *exact*
   failing instances at both d=224 and d=256/beta=40 (seed matching the
   producer's own). The internal LLL step that fails under the default
   construction **succeeds in 0.003–0.004 s** under this construction.
5. **probe7** shows the top-level free function `BKZ.reduction()` (used
   successfully by the producer's own toy-floor sweep, at much smaller d)
   is *not* a safe alternative at d=224: it hits the same underlying
   condition but via an uncaught C++ abort, only rescued into a Python
   exception by `cysignals` (DEV-2).
6. **probe6 / probe2** (full `bkz(par, tracer=True)` tours, not just the
   isolated LLL step, under the same mpfr fix) show the corrected
   construction is **far from free**: at d=224 a full tour exceeded a 120s
   exploratory bound and was terminated; at d=256/beta=40 it ran for ~684s
   (~11.4 minutes) of steady, continuous single-core CPU consumption with
   no error and no sign of stalling, at which point this review manually
   terminated it (SIGTERM/SIGKILL) to protect its own overall budget,
   rather than letting it run to its own self-declared 2400s bound. Neither
   process ever reached its own `json.dump` call — both outcomes are
   recorded honestly as manual early terminations, not fabricated
   completions or invented timings, in
   `probe6_result_d256_b40_mpfr212.json` / `probe6_stdout.log` and
   `probe2_result_d224_mpfr212.json`.

### 3. What this changes and what it does not

This does **not** overturn the producer's reported observation (0/6 cells
cleared, as actually configured) or the correctness of
`T-PROJNOISE-NODATA` firing for that observation. It overturns the
producer's own **causal explanation** for the observation and, with it,
the specific direction of the producer's own follow-up recommendation
(upstream bug-hunting / alternate build investigation). The cheaper,
already-native-fpylll fix this session validated should be tried, and
re-measured for real cost, before any upstream investigation — but the
resulting per-basis cost is not yet known to fit under
`PER_BASIS_FEASIBILITY_CAP=3600s`, so "Stage 1 is now unblocked" is
**not** a supported conclusion either.

### 4. Every probe path (declared gap G-1)

All under `coordination/goals/GOAL-MLKEM-005/batches/BATCH-3b9962/reviews/TASK-20260814-fe02ff/probes/`:

- `probe1_reproduce_baseline.py`, `probe1_result_d256_b40.json`
- `probe2_fix_via_explicit_gso.py`, `probe2_result_d224_mpfr212.json`
- `probe3_isolate_lll_step_no_strategies.py`, `probe3_result_d256_b40.json`
- `probe4_dimension_scan.py`, `probe4_result.json`
- `probe5_precision_fix_at_cheapest_failing_d.py`,
  `probe5_result_d224_mpfr212.json`, `probe5_result_d256_mpfr212.json`
- `probe6_full_bkz_with_precision_fix.py`, `probe6_stdout.log`,
  `probe6_stderr.log`, `probe6_result_d256_b40_mpfr212.json`
- `probe7_free_function_auto_precision.py`, `probe7_result_d224_b40.json`
