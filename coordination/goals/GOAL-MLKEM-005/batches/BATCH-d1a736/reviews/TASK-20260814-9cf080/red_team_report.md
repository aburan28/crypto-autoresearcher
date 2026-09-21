# RED TEAM REPORT — TASK-20260814-9cf080

```yaml
red_team_report:
  id: RT-20260814-9cf080
  task_id: TASK-20260814-9cf080

  claim_under_review: >
    TASK-20260814-534f80's own corrected-construction Stage-0 re-measurement
    (stage0_v2_feasibility.py, bisection_results.json, stage0_v2_results.json,
    writeup.md, run_manifest.yaml, environment.json; committed alone, before
    either review, at snapshot commit
    1a821796f9f3cf1c41e0af41b67bd90fa1481ac9 by TASK-20260814-cfa812):
    (1) bisected, at the isolated-LLL-preprocessing-step level, ONLY at
    (d=256, beta=40), the minimum mpfr precision at which that isolated step
    completes -- 65 bits (9 trials, 618.4s of a 3600s budget, not exhausted);
    (2) re-ran PREREG-8's 6 main-grid (d,beta) cells with a construction that
    drops GSO.ROW_EXPO and builds an explicit mpfr GSO.Mat at that single
    65-bit precision, each cell individually capped at
    PER_BASIS_FEASIBILITY_CAP_V2=7200s; (3) reports 0/6 cells completing a
    full BKZ tour -- 5 ERROR (identical `ReductionError('infinite loop in
    babai')`, one surfacing as a chained `ValueError` from the tracer path)
    and 1 NOT_COMPUTED (exceeded the 7200s cap, d=256/beta=70); (4) correctly
    declines to rule on T-PROJNOISE-NODATA, change H-MLKEM-7d9bcc's or
    EXP-MLKEM-42ea04's status, or recommend a Stage-1 sizing decision, all of
    which this task card correctly reserves for the Coordinator/Validator/Red
    Team. CLAIM TIER TOY throughout; no ML-KEM security statement is made
    anywhere in the producer's own artifacts, and this review makes none
    either.

  chain_of_custody_and_notarization_check: >
    CHECKED IN BOTH DIRECTIONS WITH GIT PLUMBING, INDEPENDENTLY BY THIS
    SESSION (this session's own current HEAD at review time:
    aadf9aa81209665b087ea973df3edca43126f8b2; the snapshot commit is a
    confirmed ancestor via `git merge-base --is-ancestor
    1a821796f9f3cf1c41e0af41b67bd90fa1481ac9 HEAD`, exit 0). FORWARD: `git
    show --stat 1a821796f...` changes exactly the 12 files the snapshot
    receipt's own `extended_artifact_paths` declares (11 TASK-20260814-534f80
    producer artifacts + the receipt itself); `git log --all --oneline --
    .../stage0_v2_feasibility.py` returns exactly one commit, the snapshot
    itself. BACKWARD: `git cat-file -e
    f07b67416bf2b5fe5a21fd36b66784399e566e71:<path>` fails (path absent) for
    every one of the 6 spot-checked producer paths (stage0_v2_feasibility.py,
    bisection_results.json, stage0_v2_results.json, writeup.md,
    run_manifest.yaml, and the snapshot receipt itself), confirming the
    declared parent f07b67416b... is correct and none of these files existed
    before the snapshot commit. HASH VERIFICATION: this session independently
    recomputed sha256 for all 11 producer paths directly from `git show
    1a821796f...:<path>` and every one matches the snapshot receipt's own
    declared `path_sha256` exactly (bit-for-bit; no re-derivation or trust of
    the receipt's own arithmetic was required). NO DISCREPANCY FOUND. This
    matches the Validator's own required check (completion_gate item 1) and
    both this review and the Validator ran it independently in separate
    sessions.

  cap_compliance_check: >
    CHECKED AGAINST THE TASK CARD'S OWN EXACT NUMBERS, NOT COPIED FROM THE
    WRITEUP. BISECTION_BUDGET_SECONDS=3600 (task card: "Cap this bisection
    phase at 3600s total") -- bisection_results.json's own
    bisection_wall_clock_seconds=618.38s, not exhausted, matches the sum of
    its 9 trials' own subprocess_wall_clock_seconds (618.38s) to within
    rounding -- no hidden bisection-phase overhead. BISECTION_TRIAL_CAP=900s
    (script constant; task card only says trials are "~70-400s") -- every one
    of the 9 trials ran 68-70s, none timed out. PER_BASIS_FEASIBILITY_CAP_V2
    =7200s (task card: "each individually capped at
    PER_BASIS_FEASIBILITY_CAP_V2 = 7200 s") -- exactly one cell
    (d=256,beta=70) hit it: subprocess_wall_clock_seconds=7200.02s,
    returncode=-15 (SIGTERM), matching the script's own
    run_capped_subprocess() terminate/wait design; every other cell finished
    well under it (223-626s). OVERALL_BUDGET_SECONDS=25200s with a
    WRITE_BUFFER_SECONDS=180s reserve (task card: "STOP and report the
    remaining cells... if the task's own overall 25200s wall-clock cap is
    reached") -- this session independently reconstructed the parent's own
    running-elapsed accounting cell-by-cell from bisection_wall_clock plus
    each cell's own subprocess_wall_clock_seconds (618.38 -> 841.74 ->
    1468.20 -> 8668.22 -> 9054.18 -> 9449.68 -> 9863.26s) and confirmed the
    "remaining_before_cell < PER_BASIS_FEASIBILITY_CAP_V2" skip test would
    not have fired at any point before the 6th cell finished -- correctly
    matching n_cells_not_computed_budget_exhausted: 0 and the script actually
    attempting and finishing all 6 cells at 9863.27s (39% of 25200s). SEED
    formula SEED_ROOT=715923, default_rng([SEED_ROOT, 0, d, beta, 0, 0]) --
    this session independently recomputed all 6 main-grid seeds from the
    formula alone (not copied from the manifest) and got a bit-for-bit match
    against run_manifest.yaml's own main_grid_seeds_used for the 5 cells it
    recorded a value for (256/40: 1398073216; 256/55: 1615872610; 512/40:
    2074339090; 512/55: 452658293; 512/70: 915347894), and independently
    derived what the 6th (256/70, disclosed seed_used: null, worker
    SIGTERM-killed before json.dump) WOULD have been (342082949), consistent
    with -- though not itself confirming -- the disclosed reason it is
    missing. NO CAP OR SEED DRIFT FOUND ANYWHERE.

  objections:
    - id: OBJ-1-BISECTED-PRECISION-DOES-NOT-GENERALIZE-ACROSS-CELLS
      severity: critical
      text: >
        The task's own "determined minimum adequate mpfr precision: 65 bits"
        was bisected EXCLUSIVELY at the isolated-LLL-preprocessing-step level,
        at the single cheapest main-grid instance (d=256, beta=40), then
        applied UNCHANGED to all 6 main-grid cells including d=512 -- a
        different dimension the bisection never tested at any level. This
        review independently executed a live, discriminating control (see
        probes/probe1_bisection_generality.py, same fpylll 0.6.4 build --
        confirmed via `importlib.metadata.version("fpylll")` and by
        independently reading this host's own installed bkz.py source before
        running anything) at (d=512, beta=40), reproducing the producer's own
        exact seed (2074339090, bit-identical) via the same
        default_rng([SEED_ROOT,0,d,beta,0,0]) formula, at the isolated-step
        level: 65 bits -- ERROR (`ReductionError('infinite loop in babai')`,
        362.9s, 357.9s of which is the outer, construction-independent
        LLL.reduction(A) pre-reduction); 100 bits -- COMPLETED (365.5s
        subprocess, 0.011s inner step). This directly falsifies "65 bits is
        THE minimum adequate precision" read as a property of the corrected
        construction generally; it is a property of ONE (d,beta) instance.
        Critically, this is not merely "a different cell might need more
        bits" in the abstract: the exact ISOLATED-LLL operation this review
        tested IS, verified directly against this host's own installed
        bkz.py source (lines 34-67, `BKZReduction.__init__`), THE SAME
        OPERATION every d=512 main-grid cell's own reported traceback fails
        on. stage0_v2_feasibility.py's own worker_main_cell() passes an
        `LLL.Reduction` instance into `BKZReduction(L)`; per bkz.py's own
        `elif isinstance(A, LLL.Reduction): L = A; ...; self.lll_obj = L`
        branch (confirmed present at bkz.py line 44 in this session's own
        installed copy), `BKZReduction.__call__`'s FIRST action --
        `with tracer.context("lll"): self.lll_obj()` at bkz.py line 123,
        confirmed by this session's own `grep -n` against the installed
        source -- calls that EXACT SAME `LLL.Reduction` object. And that is
        precisely where all three d=512 main-grid cells' own tracebacks in
        stage0_v2_results.json fail: `File ".../bkz.py", line 123, in
        __call__\n    self.lll_obj()\n ... ReductionError: b'infinite loop in
        babai'`. The producer's own reported 0/6 main-grid outcome is
        therefore CONFOUNDED: at minimum the 3 d=512 cells are not evidence
        that "the corrected construction cannot clear Stage 0" -- they are
        evidence that "65 bits, calibrated only at d=256, is insufficient
        for the isolated-LLL step at d=512," a strictly narrower and
        different fact the bisection's own single-instance design could not
        have detected.
      supporting_artifacts:
        - probes/probe1_bisection_generality.py
        - probes/probe1_bisection_generality_results.json
        - >-
          probes/probe0_sanity_reproduce_bisection.py -- environment-fidelity
          sanity check, run first; independently reproduces the producer's
          own bisection endpoint at d=256 bit-identically (64 bits ERROR,
          65 bits COMPLETED, seed_used=1398073216) before this review
          trusted its own d=512 result as comparable

    - id: OBJ-2-ISOLATED-STEP-BISECTION-IS-KN-FIND-f54a82-S-OWN-HAZARD-RECURRING-A-THIRD-TIME
      severity: high
      text: >
        Even restricted to d=256, the corrected construction does not
        survive a full tour at the bisected 65 bits: the (256,40) cell fails
        223.4s in (157s beyond the outer LLL pre-reduction), deep inside
        `svp_preprocessing`'s own windowed `self.lll_obj(lll_start, ...)`
        call -- NOT the same site as the initial call the bisection tested.
        The (256,55) cell survives 576s of extra corrected-construction work
        before failing even deeper (two nested `tour`/`svp_preprocessing`
        levels). This is the isolated-step-vs-full-tour permissiveness gap
        KN-FIND-f54a82 itself names and generalizes ("any goal in this
        portfolio that tests a proposed numerical fix ... against a cheap
        sub-step ... rather than its actual full operation"), now recurring
        for a THIRD time within this same goal -- this time inside the very
        follow-up task DEC-20260814-4ac30a's own next_actions commissioned
        BECAUSE of that finding. The task card's own bisection design
        ("cheap: ~70-400s per trial, dominated by the outer LLL.reduction(A)
        call") is an honest, disclosed cost tradeoff, not a concealment --
        but it reintroduces the identical hazard at one level up: precision,
        calibrated only against the isolated step, is then trusted as
        sufficient for the full tour it is meant to unblock, without an
        explicit check.
      note: >
        Not a fabrication or negligence finding -- KN-FIND-f54a82's own
        limitations section already discloses that its lesson had not yet
        been tested against a THIRD occurrence, and writeup.md section 4
        already, honestly, declines to claim this question is answered
        ("it does not by itself determine whether a materially higher
        precision ... would behave differently"). This objection exists to
        make sure that hedge is not lost or read past by the next
        Coordinator decision.

    - id: OBJ-3-HEADLINE-WALL-CLOCK-CONFLATES-TWO-COST-DRIVERS-WITH-DIFFERENT-SCALING
      severity: medium
      text: >
        writeup.md's own section-3 table reports one "subprocess wall-clock"
        figure per ERROR cell without decomposing it into (a) the outer,
        construction-INDEPENDENT double-precision `LLL.reduction(A)`
        pre-reduction (confirmed, by this session reading
        TASK-20260814-ffd791's own committed stage0_feasibility.py line 102,
        to be identically present in the ORIGINAL default construction too --
        so this is not new cost the fix introduced, and the raw wall-clock
        IS a fair like-for-like comparison at that level) and (b) the
        residual time actually spent in the corrected-construction-specific
        machinery before erroring. Computing (total - outer) from
        stage0_v2_results.json's own fields: (256,40) residual=156.7s;
        (256,55) residual=576.4s; (512,40) residual=5.1s; (512,55)
        residual=5.2s; (512,70) residual=5.7s. The d=512 cells' residual of
        ~5s is itself strong corroborating evidence for OBJ-1 -- it is
        exactly what "fails almost immediately at the very first internal
        call" (bkz.py:123) predicts, as opposed to a genuine, sustained
        numerical struggle. This decomposition is fully present in the raw
        JSON (the `outer_lll_reduction_elapsed_seconds` field, per cell) but
        not surfaced anywhere in the writeup's own prose or table, so a
        reader relying on the table alone would not notice the asymmetry.
      resolution: >
        FOUND AND REPORTED, per this task's own completion_gate item 2
        ("at least one omitted or undercounted cost is explicitly sought").
        The raw datum was not hidden; its significance for interpreting the
        headline figure was.

    - id: OBJ-4-BISECTION-MONOTONICITY-ASSUMED-NOT-VERIFIED
      severity: low
      text: >
        The 1-bit binary search assumes pass/fail is monotone in mpfr
        precision and tests only the O(log(212-53))=9 points a bisection
        path visits, not every integer bit-width in [53,212]. The 9 observed
        points (53,62,64:ERROR; 65,67,72,92,132,212:COMPLETED) are, sorted,
        consistent with monotonicity, so nothing in this run's own data
        contradicts the assumption -- but a non-monotone "island" between two
        untested bit-widths (a known real hazard in mpfr/GMP-backed
        numerical code, where rounding-mode/representable-value boundaries
        can occasionally reintroduce instability at specific widths) cannot
        be ruled out from 9 points, and "65 bits is a genuinely determined
        minimum" is a slightly stronger claim than the data alone supports.
      resolution: >
        Low priority relative to OBJ-1/OBJ-2; noted for completeness. The
        Validator's own completion_gate already requires independently
        confirming 65 succeeds and 64 fails, which is a narrower and
        sufficient check for THIS instance; this objection is about
        generalizing "minimal" beyond the 9 tested points, not about
        reproducing them.

  required_controls:
    - id: CTRL-1-RUN-BY-THIS-REVIEW
      description: >
        Isolated-LLL-step precision sensitivity at (d=512, beta=40) --
        EXECUTED by this review (probes/probe1_bisection_generality.py,
        results in probes/probe1_bisection_generality_results.json). Result:
        falsifies "65 bits generalizes"; brackets d=512's own boundary to
        (65, 100] bits at the isolated-step level. This is the cheapest
        available discriminating control for OBJ-1 and it has already been
        run, not merely proposed.
    - id: CTRL-2-NOT-RUN-CHEAP
      description: >
        A genuine bisection (not a 2-point bracket) at d=512, beta=40,
        analogous to the producer's own d=256 procedure, to determine d=512's
        OWN minimum at the isolated-step level. Cost: a handful of
        ~360-400s-per-trial subprocess runs (each dominated by the same
        outer LLL.reduction(A) cost this review's own probe1 already paid
        twice), well under an hour total, using this same probe's own
        harness with PRECISIONS_TO_TEST replaced by a binary search between
        65 (known-failing at d=512) and 100 (known-succeeding at d=512).
    - id: CTRL-3-NOT-RUN-DECISIVE
      description: >
        Re-attempt at least one currently-ERRORing d=512 main-grid cell's
        FULL BKZ TOUR (not just the isolated step) at a precision above
        this review's own confirmed d=512 boundary (>= 100 bits, e.g. 130 or
        212). This is the decisive control: it directly tests whether
        raising precision, at a dimension-appropriate value, lets Stage 0
        clear at d=512 -- the exact question KN-FIND-f54a82's own open item
        4.1 names ("the real per-cell cost of the corrected ... construction
        is completely unmeasured") and that this whole follow-up batch was
        commissioned to answer, now sharpened to "unmeasured AT A PRECISION
        KNOWN SUFFICIENT FOR THAT DIMENSION'S OWN ISOLATED STEP," which the
        65-bit run never tested at d=512.
    - id: CTRL-4-NULL-OBJECT-CHECKED-N-A
      description: >
        No null-object control (random function / random bijection / random
        instance of the same shape) is needed here: this is an
        infrastructure feasibility/timing measurement (PREREG-8 sections
        2.2-2.3), not a distributional or statistical-signal claim, so there
        is no "signal that should decay" for a null object to falsify.
        Checked and confirmed N/A, matching EV-MLKEM-ef0261's own
        `control_comparability: NOT APPLICABLE` finding, which this review
        independently concurs with rather than merely restates.

  counterexample_or_mutation: >
    probes/probe1_bisection_generality.py IS the counterexample: a single,
    minimal, executed mutation of the producer's own construction (change
    ONLY d: 256 -> 512, everything else -- seed formula, ROW_EXPO-free mpfr
    GSO.Mat construction, isolated-lll_obj()-call shape -- held fixed) that
    converts the producer's own reported "COMPLETED" outcome at 65 bits into
    "ERROR," on this session's own live, bit-identical-seed execution against
    the same fpylll 0.6.4 build. This distinguishes "the bisected precision
    is a general property of the fix" (falsified) from "the bisected
    precision is a property of one calibration instance" (supported).

  baseline_comparison: >
    Not applicable in the Pollard-rho/BSGS/specialized-attack sense -- this
    is a Stage-0 lattice-reduction feasibility/timing gate, not a
    discrete-log attack, and PREREG-8 scopes it to timing/feasibility only
    (already independently confirmed N/A by both BATCH-3b9962 reviews and
    this review's own CTRL-4 above). The applicable intra-construction
    baseline is corrected (ROW_EXPO-free, mpfr) vs. default (ROW_EXPO-on)
    construction: both pay an identical outer double-precision
    `LLL.reduction(A)` cost (confirmed by this session reading
    TASK-20260814-ffd791's own stage0_feasibility.py line 102), so the raw
    subprocess-wall-clock figures (223-626s corrected vs. 53.7-408.9s default,
    per EV-MLKEM-ef0261) ARE comparable like-for-like at that level, even
    though OBJ-3 shows that headline figure conflates two very
    differently-scaling cost drivers once decomposed.

  heuristic_challenges: []
  heuristic_challenges_note: >
    NOT APPLICABLE. No numbered heuristic, random-model justification, or
    asymptotic_claim exists anywhere in this task or in H-MLKEM-7d9bcc (which
    DEC-20260814-4ac30a's own hypothesis_status_ruling confirms carries no
    asymptotic_claim). This is an infrastructure feasibility measurement, not
    an exponent-first heuristic-conditional result in the
    docs/target-result-profile.md sense; the exemplar-style challenge list in
    this role's own contract (heuristic inventory, random-model transfer,
    scale honesty, hidden-overhead, cost bookkeeping, reduction
    instantiation, scope inflation) is checked here and found not to apply,
    not silently skipped.

  cost_model_challenges:
    - id: COST-1-HEADLINE-FIGURE-MISREADING-RISK
      text: >
        See OBJ-3. The reported "223s-626s per corrected-construction ERROR,
        7200s cap for one NOT_COMPUTED cell" should NOT be read, by the next
        Coordinator decision (TASK-20260814-6af6d1), as "the real cost of the
        fix is now known and it is cheap-but-broken." Per OBJ-1, at least
        3/6 of those figures are costs of failing at an UNDER-PROVISIONED
        precision (confirmed insufficient even at the isolated-step level,
        this review's own probe1), not costs of a well-calibrated,
        dimension-appropriate attempt failing or succeeding.
    - id: COST-2-INVERSE-SUCCESS-PROBABILITY-BOOKKEEPING-CHECKED-CLEAR
      text: >
        No total-expected-cost figure (per-attempt cost x inverse success
        probability) is computed or implied anywhere in this task's own
        artifacts, appropriately: 0/6 successes gives no probability to
        invert, and the task correctly reports per-attempt costs only,
        without extrapolating a per-solve cost. Checked and clear -- no
        per-attempt-cost-presented-as-total-cost violation found.
    - id: COST-3-CAP-JUSTIFICATION-WENT-STALE-BUT-CONSERVATIVELY
      text: >
        The 7200s-per-cell cap's own stated justification (task card
        budget_justification: preliminary 212-bit evidence from
        ADJUDICATION.md/probe6 showing 100-684s WITHOUT resolving) does not
        match what was actually run (65 bits, which resolves to a definite
        ERROR within a few hundred seconds at 5/6 cells -- a materially
        different failure character than the open-ended non-resolution the
        cap was sized against). This went stale once the bisection result
        (65, not 212) was known, but harmlessly: the cap ended up generous
        rather than binding for 5/6 cells (conservative, not a defect). It
        WAS exactly binding for the 6th (256,70), whose NOT_COMPUTED outcome
        therefore still tells us nothing about whether a longer cap, or
        (per OBJ-1) a different precision, would have resolved it -- both
        remain open, as the writeup itself already discloses.

  reduction_and_scope_challenges: []
  reduction_and_scope_challenges_note: >
    NOT APPLICABLE. No cited reduction (OneEnd/EndRing/Isogeny-style
    corollary chain) and no affected-vs-safe scheme list exists anywhere in
    this task -- correctly, since PREREG-8 section 4.3 item 1's own FORBIDS
    clause bars any C1/C2 statement while T-PROJNOISE-NODATA fires, and
    neither the producer nor this review makes one. Checked and clear: no
    scope inflation found.

  proof_architecture_challenges: []
  proof_architecture_challenges_note: >
    NOT APPLICABLE. This is not a proof-oriented claim (no theorem, bound,
    certificate family, reduction, or closure argument); docs/inventor-
    protocol.md section 8 / KN-TECH-080's proof_search_map audits do not
    apply to an infrastructure feasibility re-measurement task. Checked and
    clear.

  narrowest_supported_statement: >
    What TASK-20260814-534f80 actually shows, stated at its true width: "The
    specific corrected construction, run at 65-bit mpfr precision -- a value
    bisected ONLY at the isolated-LLL-preprocessing-step level, at ONLY the
    single cheapest main-grid instance (d=256, beta=40) -- did not complete a
    full BKZ tour at any of PREREG-8's 6 main-grid cells within a 7200s
    per-cell cap, on this host, this fpylll 0.6.4/fplll build, this seed
    formula." This is true, reproducible (this review independently
    reproduced the bisection's own d=256 endpoints bit-identically via
    probe0 before trusting anything downstream), and honestly reported by
    the producer, who correctly declines to generalize it further. What it
    does NOT support -- and what this review's own executed probe1 directly
    falsifies -- is the broader, unstated reading "the corrected (ROW_EXPO-
    free, mpfr) construction itself cannot clear Stage 0" or "raising
    precision further would not help": the SAME isolated-LLL operation the
    d=512 main-grid cells fail on (bkz.py line 123's `self.lll_obj()`,
    confirmed identical by direct source inspection to the operation the
    bisection tested) succeeds at 100 bits and fails at 65 bits, at a
    bit-identical seed, on this review's own live execution. Whether a full
    BKZ TOUR at a higher, dimension-appropriate precision clears Stage 0 at
    d=512 (or lets d=256's own beta=55/70 cells survive past their own
    deeper failure points, per OBJ-2) remains genuinely OPEN and untested by
    anyone in this goal to date. This is narrower than "not yet fixed," and
    materially narrower than "the fix is exhausted, escalate to an upstream
    fplll bug report / alternate build / scoped-down dimension" -- the three
    options DEC-20260814-4ac30a's own next_actions names as "the live
    question" if the corrected construction fails at every cell. It did fail
    at every cell, but per OBJ-1 that failure is not yet properly separated
    from "the precision this task chose was too low for at least 4 of the 6
    cells, by evidence this task's own bisection methodology could not have
    surfaced."

  next_concrete_action: >
    Before TASK-20260814-6af6d1's own Coordinator decision reads this
    batch's 0/6 outcome as licensing DEC-20260814-4ac30a's own named "next
    escalation" (upstream fplll bug report, alternate build/version, or a
    scoped-down dimension), commission one more narrowly-scoped, strictly
    cheaper follow-up: (a) a real bisection (not a 2-point bracket) at
    d=512 to determine ITS OWN minimum adequate isolated-step precision
    (CTRL-2 above; this review's own probe1 already brackets it to (65,100]
    bits and its own harness is reusable directly); (b) re-attempt at least
    the three currently-ERRORing d=512 main-grid cells' own FULL BKZ tours
    at that dimension-appropriate precision (CTRL-3 above) before concluding
    the ROW_EXPO/mpfr fix itself is exhausted. This is strictly cheaper than
    a new fplll build or an upstream bug report (each d=512 trial costs
    ~360-410s, dominated by the same outer LLL.reduction(A) this task's own
    main-grid cells already pay), and it directly tests the one hidden
    assumption (precision generalizes across cells) this review's own
    executed control shows is false.

  artifact_paths:
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/red_team_report.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe0_sanity_reproduce_bisection.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe0_sanity_reproduce_bisection_results.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe0_stdout.log
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe1_bisection_generality.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe1_bisection_generality_results.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe1_stdout.log
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-d1a736/reviews/TASK-20260814-9cf080/probes/probe1_stderr.log

  probes_written_declared_gap_g1: >
    DECLARED GAP G-1 (per dispatch_queue.json's own artifact_paths_note for
    this task), closed here explicitly: exactly 7 probe files were written,
    all listed in artifact_paths above under probes/. No __pycache__, .pyc,
    or other scratch artifact exists under this task's write_scope (checked
    directly: `find ... -iname "__pycache__" -o -iname "*.pyc"` returned
    nothing); all _tmp_probe*.json intermediate files the probes create
    during execution are removed by the probes' own code before they exit
    (matching the producer's own convention) and none remain on disk.

  environment_fidelity_note: >
    This review's own execution environment was NOT pre-provisioned with
    fpylll at session start (`import fpylll` initially raised
    ModuleNotFoundError). This session installed `python3-fpylll` via `apt-
    get install` as root; the effective, importable fpylll that resulted
    (at /usr/local/lib/python3.11/dist-packages, NOT the apt package's own
    /usr/lib/python3/dist-packages location, which is built for a different
    Python ABI and is not what `import fpylll` resolves to) reports version
    0.6.4 -- bit-for-bit the same version, same install location, and (per
    probe0's own bit-identical reproduction of the producer's exact bisection
    endpoints, including timing in the same ~68-72s range) apparently the
    same underlying build as environment.json's own recorded producer
    environment. This review does not know the exact provisioning mechanism
    that produced this match and states the observation plainly rather than
    asserting a causal explanation it cannot verify; probe0's own bit-
    identical reproduction is the actual evidence of environment fidelity,
    not the version-string match alone. A concurrent, unrelated process
    (identified only via `ps aux`, never read: a probe script under
    TASK-20260814-1ce70d's own reviews/ write_scope, consistent with the
    independent Validator session dispatched on the same task pair) was
    observed running on this same 4-vCPU host during part of this review's
    own probe1 execution; this may have added modest wall-clock noise to
    this review's own timing figures (subprocess_wall_clock_seconds), but
    does not affect the COMPLETED/ERROR status outcomes this review's
    findings rest on, which are deterministic given the seed and precision.

  binding_carry_note: >
    PREREG-8, DEC-20260814-4ac30a, EV-MLKEM-ef0261, and KN-FIND-f54a82 are
    carried in full and not re-litigated. This review does not dispute the
    termination-branch determination, the ROW_EXPO mechanism account, or any
    prior claim-tier/scope ruling; it challenges only TASK-20260814-534f80's
    own NEW bisection-generality and cost-interpretation claims, which no
    prior record in this goal has yet tested.

  scope_and_prohibitions_compliance: >
    This review changes no research status, no hypothesis, no experiment
    approval, and no raw producer artifact. It makes no ML-KEM security
    statement. It does not call TASK-20260814-534f80's own bounded 0/6
    failure an impossibility result -- OBJ-1/OBJ-2 and the
    narrowest_supported_statement explicitly narrow, not broaden, what may
    be concluded from it, consistent with this role's own prohibition
    against treating a bounded failure as an impossibility result. Nothing
    was committed by this session; this file and its probes/ subdirectory
    are written only under this task's own declared write_scope.

  inference_provenance:
    requested_policy: review-adversarial
    resolved_model_identifier_self_report: >
      claude-sonnet-5 (configured identifier from this session's own system
      prompt: "You are powered by the model named Sonnet 5. The exact model
      ID is claude-sonnet-5." -- reported verbatim from that configured
      value, not inferred, guessed, or reconstructed from training-time
      knowledge of any marketing name).
    reasoning_effort: xhigh
    reasoning_effort_basis: >
      Bound by .claude/agents/red-team.md `effort: xhigh`, which
      orchestration/roles.yaml derives for role red-team via default_policy
      review-adversarial. Honoured by the runtime binding rather than
      independently probed by this session.
    fallback_used: false
    fallback_allowed: false
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: >
      No adapter probe receipt exists for this session; AUTORESEARCH_POLICY
      and AUTORESEARCH_BACKEND are both unset in this session's own
      environment (checked directly: `env | grep -i autoresearch` returned
      nothing) -- the identical gap every producer and review in this batch
      records for the identical reason.
    independent_session: true
    independence_kind: >
      This session did not read coordination/goals/GOAL-MLKEM-005/batches/
      BATCH-d1a736/reviews/TASK-20260814-1ce70d/ (the concurrent Validator's
      own review directory) at any point, per this task's own explicit
      instruction. A process belonging to that session was visible via `ps
      aux` (never its file contents) while this review's own probe1 ran
      concurrently on the same host; this is disclosed in
      environment_fidelity_note above as a possible timing-noise source, not
      as content this review consulted.
```
