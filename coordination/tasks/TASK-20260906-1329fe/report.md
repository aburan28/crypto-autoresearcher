# Independent validation report

The archived package is admissible as a terminal infrastructure-failure
receipt. Its scientific portion is incomplete: the process failed while
installing the Darwin `RLIMIT_AS` limit, before any eligibility, rejection,
symbolic, or finite-control stage. `passed` below therefore means that the
archive and the claimed infrastructure stop are internally consistent. It
does not mean that the deformation-jet experiment produced measurements,
certificates, a proof outcome, or evidence for or against an ECDLP claim.

```yaml
validation_report:
  id: VAL-20260909-1329fe
  id_provenance: >-
    The allocator has no validation_report type. `python3
    tools/allocate_id.py --check VAL-20260909-1329fe` returned well-formed YES
    (no VAL pattern enforced), zero occurrences, and OK. The six-hex suffix is
    bound to this task identifier; no existing identifier was reused.
  task_id: TASK-20260906-1329fe
  role: validator
  run_ids:
    - RUN-ECDLP-b7628e
  snapshot_binding:
    snapshot_task_id: TASK-20260906-cc73d8
    snapshot_manifest: coordination/tasks/TASK-20260906-cc73d8/archive-manifest.yaml
    snapshot_commit: bc94825d30045cb2856d06e3bf05ff394b7487a2
    snapshot_parent: d2fd058806204342af2b567dcf99bf27775b31e1
    reachable_from_head: true
    parent_matches_manifest: true
    changed_path_count: 20
    declared_path_count_excluding_manifest: 19
    exact_commit_scope: true
  artifact_checks:
    - check: committed_handoff
      result: passed
      detail: >-
        ledger/handoffs/TASK-20260906-1329fe.yaml is tracked and binds this
        validator to RUN-ECDLP-b7628e, the source package, and the 13 non-self
        run artifacts. It requires no experiment execution and names
        TASK-20260906-400dd5 as its ledger archive task.
    - check: snapshot_archive_commit
      result: passed
      detail: >-
        TASK-20260906-cc73d8's archive manifest declares parent
        d2fd058806204342af2b567dcf99bf27775b31e1. The actual snapshot commit
        is bc94825d30045cb2856d06e3bf05ff394b7487a2 with that exact parent, is
        reachable from HEAD, and changes exactly the 19 declared source/run
        paths plus coordination/tasks/TASK-20260906-cc73d8/archive-manifest.yaml.
    - check: snapshot_path_sha256
      result: passed
      method: >-
        SHA-256 was recomputed from the working-tree bytes and from each
        `git show bc94825d30:<path>` snapshot blob. All values matched the
        archive manifest and the dispatch archive receipt.
      rows:
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/source/direct_dual_numbers.py, sha256: f98d7856f753f3b30b6b76109d87cbc63e8d0b117e932e772a40ff2cc574015a, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/source/coefficient_reference.py, sha256: d51cc8f2c0ca344b6b00eb19d81e8dc3c78919060ccc2e1965f6869975f02389, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/source/symbolic_audit.py, sha256: 0dea3d56cee44074430bc845e0bf41f9dfc48c85dfdf3191ffe91c81da5542f2, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/source/run_audit.py, sha256: 8e66ea1e402f17bcc6a0cd7e9c591bd46fdea21a39055e34d606b72a1c3b6d6f, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/implementation.md, sha256: 55225ccef94b1309b0b54fcb80eec030589bd265c11caefebf983202da2e78cb, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/manifest.json, sha256: 060cdc1c0fda7188396068ffd3a0a21c1490a6cef578e7e2158c411ab26eb198, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/inputs.json, sha256: 899a54f57cbe6e5a7af314b232be150618343805818d8d700b2cdfa4a5d9345f, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/environment.json, sha256: 3cea978b6e4757268558350a9613a028c526e2a2d338a47d2e4ec680e3095ff3, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/symbolic-certificates.json, sha256: dbc97905b275b31ca06435249a4699bd8077d942feb9ca6b1ec5af021c5a6295, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/lemma-proof.md, sha256: 363ac9c555ab785187f78e7eb52931c081e2a50b1bf8fc500c32a9067a08b8b3, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/eligibility.csv, sha256: e4b207d72805f328ea349dce27a1086c25b8e3c8ebb7c041ec2eaf42cb5186ee, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/finite-controls.csv, sha256: 53c48bc07108e423107e34e28a03a2049d8166cc1d0afa1d3269506d8d74bc45, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/rejection-controls.json, sha256: ad00acb1dd11a4b5fd143c18991a2e455af6b86ee59a8adaebcc65fc51819e35, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/metrics.json, sha256: ae56b082091c79c0ddf7d7c54b7124e48f3c683d786aa9a887059aaa7623391f, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/execution-report.md, sha256: a5f2f595d7de3aae67af41bf7cafb451059b98eb4954414e45cd6249d066cd11, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/stdout.log, sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/stderr.log, sha256: 81321a57fd259bd8cf28a0fc8461eb689c66da96ff8699a3c99e29ccfca4246e, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/command.txt, sha256: 8ed44825e0f4095251bc1967f35d37eab92b6b965b6d85ef52e66d167d969cb8, result: match}
        - {path: experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/raw-result.json, sha256: 48344cf67e972f0fedfd3687b2afefcac2e8ee4c307fe69b22ccc15ae920d225, result: match}
    - check: archive_manifest_hash
      result: passed
      detail: >-
        The dispatch receipt's SHA-256 for
        coordination/tasks/TASK-20260906-cc73d8/archive-manifest.yaml is
        729621cffc110be9e92902b8409cd7961b2469eb60feda16784f4ba4124bdb16,
        matching both the working-tree file and the snapshot blob. The
        manifest intentionally does not self-hash its own contents.
    - check: run_manifest_artifacts
      result: passed
      detail: >-
        The run directory contains 14 files: manifest.json plus 13 artifacts.
        manifest.json contains exactly those 13 non-self artifact names and
        every internal artifact_sha256 value recomputes. Its source_sha256 map
        also recomputes for all four source modules. Self-reference is
        explicitly excluded.
    - check: run_identity_and_provenance
      result: passed_with_limitations
      detail: >-
        The experiment, task, and run identifiers agree across manifest.json,
        raw-result.json, inputs.json, metrics.json, and execution-report.md.
        implementation_commit is d2fd058806204342af2b567dcf99bf27775b31e1,
        the execution command is recorded, and the recorded source/run bytes
        are snapshot-bound. The execution manifest truthfully records
        dirty_tree=true and a status containing the untracked execution
        directory and .tmp; the snapshot supplies durability but does not turn
        the original execution into a clean-tree run.
  metric_recomputations:
    - metric: planned_row_cardinality
      result: passed_integrity_only
      recomputation: >-
        len(primes)=4 * len(families)=3 * len(u0)=2 * len(v)=2 * len(c)=2
        equals 96, matching inputs.json and metrics.json planned_rows.
    - metric: planned_control_cardinality
      result: passed_integrity_only
      recomputation: >-
        Four primes imply four planned eligibility point counts and the four
        explicitly named rejection fixtures imply four planned rejection
        checks. These match metrics.json planned_point_counts=4,
        planned_rejections=4 and rejection-controls.json planned=4.
    - metric: observed_row_and_control_counts
      result: passed_integrity_only
      recomputation: >-
        The committed snapshot has zero data rows in eligibility.csv (7-column
        header only) and zero data rows in finite-controls.csv (16-column
        header only); raw-result.json has zero rows, eligibility, rejections,
        and certificates; metrics.json has executed_rows=0,
        executed_point_counts=0 and executed_rejections=0. This confirms an
        empty terminal receipt, not a measured zero result.
    - metric: resource_and_timing_fields
      result: passed_as_disclosed_unavailable
      recomputation: >-
        cpu_seconds, peak_rss_bytes, and stage_wall_seconds are null in the
        receipt metrics because the process stopped during resource setup.
        The only recorded outer command duration is 1.18865425 seconds, and
        the report labels it as outer-tool timing rather than inner-stage cost.
    - metric: symbolic_residuals
      result: incomplete_not_executed
      recomputation: >-
        No residual values were generated. symbolic-certificates.json has six
        expected certificate keys, all status NOT_EXECUTED, and lemma-proof.md
        says the proof stage was not entered. No symbolic PASS or zero residual
        is credited.
  control_checks:
    - control: rlimit_as_setup
      result: passed_as_infrastructure_classification
      observation: >-
        stderr.log records ValueError: current limit exceeds maximum limit at
        run_audit.py:38 while calling
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3)). The
        manifest and raw result classify this as failed_infrastructure /
        infrastructure_error, with valid=false and exit_code=1.
      classification: >-
        This is an operating-system/resource-limit setup failure before the
        scientific stages. It is infrastructure evidence only, never negative
        mathematical evidence about the deformation-jet hypothesis or ECDLP.
    - control: eligibility_point_counts
      result: not_executed
      detail: >-
        Four point-count/ordinary-fiber controls were planned but the failure
        preceded the loop that calls direct.point_count; no eligibility row or
        point-count value exists.
    - control: rejection_controls
      result: not_executed
      detail: >-
        Four invalid-input predicates were planned, but rejection-controls.json
        records planned=4, executed=0, outcomes=[], status=NOT_EXECUTED.
    - control: finite_controls
      result: not_executed
      detail: >-
        The 96 finite rows were not entered. finite-controls.csv has only its
        frozen 16-column header and no row-level control results.
    - control: source_stage_order
      result: passed_for_documentary_scope
      detail: >-
        AST inspection of the committed run_audit.py places the failing
        resource.setrlimit call at line 38 before direct.point_count at line
        61, certificates at line 75, and direct/reference.calculate at lines
        86-87. The three imported helper modules have no top-level calls. This
        agrees with the exact traceback and scientific_stages_entered=false;
        it is a static/documentary check and not a rerun.
    - control: attempt_and_retry
      result: passed
      detail: >-
        command.txt records one invocation. manifest.json and raw-result.json
        agree on attempts=1, reruns=0, and no retry. The top-level run path was
        created exclusively, and no second scientific attempt is present.
    - control: post_failure_environment_probe
      result: recorded_with_limitation
      detail: >-
        environment.json records memory_limit_installed=false and a
        post-failure RLIMIT_AS probe of 9223372036854775807 for both bounds,
        while explicitly labelling that probe as read-only post-failure
        information rather than measured run telemetry. It does not establish
        a scientific or performance result.
  heuristic_validation_checks:
    - check: not_applicable
      result: not_applicable
      reason: >-
        No sampler, distribution, empirical CDF, or transfer claim ran; all
        scientific stages stopped before the first fixture.
  cost_model_checks:
    - check: not_applicable
      result: not_applicable
      reason: >-
        No scientific cost table or per-attempt measurement was produced.
        Outer command time is retained as operational metadata only.
  proof_architecture_checks:
    - check: producer_lemma_submission
      result: incomplete_not_executed
      detail: >-
        lemma-proof.md is the producer's frozen proof submission and explicitly
        says Not executed. The symbolic certificate artifact contains only
        NOT_EXECUTED statuses. No proof outcome, strictness witness, or
        independent semantic proof review is established by this receipt.
  verdict: passed
  verdict_scope: >-
    The archive and terminal failure receipt are admissible as documentary
    evidence that one attempt stopped at RLIMIT_AS setup. This verdict does
    not validate any scientific measurement, symbolic residual, control,
    lemma, hypothesis status, or ECDLP conclusion.
  scientific_evidence_status: incomplete
  limitations:
    - >-
      The RLIMIT_AS ValueError is infrastructure_error at resource setup and
      must not be converted into a mathematical negative result. A portable
      memory-limit mechanism and a new governed run are required before any
      scientific claim can be evaluated.
    - >-
      Zero rows, zero controls, empty certificate results, and null resource
      metrics are consequences of the pre-stage failure. They are unavailable
      measurements, not measured zeros and not evidence for or against the
      hypothesis.
    - >-
      The partial receipt was reconstructed after the process failed before
      its normal artifact writer, as disclosed in manifest.json and the
      execution report. Hash agreement proves the committed bytes and their
      consistency; it does not recreate normal in-process artifact production.
    - >-
      The original execution was dirty: the recorded status includes the
      untracked execution directory and .tmp. The exact source/run bytes are
      durably bound by the snapshot, but implementation_commit alone is not a
      clean checkout containing the executed package.
    - >-
      environment.json labels its RLIMIT_AS probe as post-failure and not run
      telemetry; CPU, RSS, and scientific-stage timing were not measured.
    - >-
      model_provenance has resolved_model_id=null and model_verified=false.
      This does not alter the infrastructure classification, but it prevents
      treating model metadata as a verified execution provenance claim.
    - >-
      This report is an independent integrity validation only. It performs no
      hypothesis or goal status transition, no approval, no ledger mutation,
      and no scientific execution.
  artifact_paths:
    - coordination/tasks/TASK-20260906-1329fe/report.md

review_attestation:
  task_id: TASK-20260906-1329fe
  joints_owned:
    - snapshot archive parent, reachability, exact path set, and SHA-256 bindings
    - terminal receipt identity, status, error, exit code, attempts, and retry consistency
    - planned versus observed row/control cardinality and unavailable-metric handling
    - static confirmation that RLIMIT_AS setup precedes every scientific stage
    - explicit separation of infrastructure failure from mathematical evidence
  sources_read:
    - ledger/handoffs/TASK-20260906-1329fe.yaml
    - ledger/handoffs/TASK-20260906-cc73d8.yaml
    - ledger/handoffs/TASK-20260906-400dd5.yaml
    - coordination/tasks/TASK-20260906-cc73d8/archive-manifest.yaml
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-ca460f/dispatch_queue.json
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-ca460f/claims/TASK-20260906-b7628e.1.release.json
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/source/direct_dual_numbers.py
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/source/coefficient_reference.py
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/source/symbolic_audit.py
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/source/run_audit.py
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/implementation.md
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/manifest.json
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/inputs.json
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/environment.json
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/symbolic-certificates.json
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/lemma-proof.md
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/eligibility.csv
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/finite-controls.csv
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/rejection-controls.json
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/metrics.json
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/execution-report.md
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/stdout.log
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/stderr.log
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/command.txt
    - experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e/runs/RUN-ECDLP-b7628e/raw-result.json
  read_sibling_reports: false
  blind_from_respected: null
  verdict: holds
  verdict_basis: >-
    All assigned integrity joints hold against the Coordinator-committed
    snapshot. The top-level passed verdict is limited to receipt admissibility
    for the recorded infrastructure stop; the scientific evidence status is
    incomplete and no whole-claim scientific verdict is made.
```
