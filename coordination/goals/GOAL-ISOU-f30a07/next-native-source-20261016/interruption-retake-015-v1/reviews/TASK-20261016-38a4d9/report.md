Independent Validator TASK-20261016-38a4d9: **holds** on the sole assigned joint, `interruption_invocation_retention_binding`, within the new logging supplement's source, invocation, retention and custody scope. This is a private independent review of prospective plan `319cc51b9f`, exact snapshot `c332aef9d2466049a38335b6bb22c9a230ee406d`, and external evidence Git commit `f6440f5c8f93db43ed33adf991a58df7648ff6c9`. It does not decide official source admission or evidence strength.

I derived the source contract and actual raw outcomes before semantically reading producer source-bindings, metadata.py, correct-log-count.py or manifests. The frozen required plan/protocol already state anticipated outcomes; I treated those as the contract and recomputed observations from the original source and raw logs. The timestamped note saved at 2026-10-16T22:49:06.525258+00:00 is `pre-summary-derivation.md`, 24,542 bytes, SHA256 `6286249a7be28c9986c521efc218ecceb344e5a4229b8dcf49202fc73912b8d4`. An initial 25-versus-27 member wording error was corrected before any producer semantic read; the inventory preserves that inspection correction and both note hashes. The finalized note has remained unchanged through findings.

The original `015fa7bb504ef63953e0e04e464bb266f4f207bf:tools/isogeny-cli/src/replay_trace.rs` equals the retained 12,224 byte source (SHA256 `30fa162ab24097380e5635c3cd720680e53a76510c89dbf1bd166ddb673166a3`). Source `Trace::record` serializes the event, writes its newline and flushes before returning. `Session::start` creates an absolute absent trace and emits total/begin, id0, parent null; `stage` emits interruption_fixture_wait/begin, id1, parent0. The ignored helper checks CONTROL_CHILD, starts those objects and sleeps 10 seconds before any finish. The named parent uses the current unit executable with `--exact replay_trace::tests::interruption_worker --ignored --nocapture`, polls at 5 ms for at most 5 seconds, calls kill (its Result is discarded), waits, asserts the visible begin and exactly two ordered begin records, and writes control.json. UNIT_EVIDENCE presence selects a fresh retained directory and prevents cleanup. Its absence leads to deletion. Normal finish/drop paths could emit end/terminal or error events; the retained interrupted runs have neither. Flush visibility is checked; fsync/durable-media guarantees are outside this fixture.

The frozen launcher uses `--exact replay_trace::tests::flushed_begin_survives_bounded_child_interruption --nocapture --test-threads=1`, reference then candidate, with before/after executable checks. It unsets inherited CONTROL_CHILD and REPLAY_TRACE, sets the fresh per-arm UNIT_EVIDENCE root and LC_ALL=C, and uses 20 second gtimeout plus 5 second hard grace and `/usr/bin/time -l`. Inspection of this exact launcher and source finds only the two selected parents and their ignored logging helpers; the helper body contains Session/stage/sleep. A global host process audit was not performed. No test or scientific executable was invoked by this reviewer.

| Observation independently derived from original raw files | Reference | Candidate |
|---|---:|---:|
| Selected named parent / passed |1 /1|1 /1|
| Failed / ignored / measured |0 /0 /0|0 /0 /0|
| Filtered tests |85|85|
| Parent exit / stderr bytes |0 /0|0 /0|
| Retained raw files |16|16|
| Ordered trace records |total/begin; fixture/begin|total/begin; fixture/begin|
| Child PID in both rows |14894|14915|
| End or terminal records |0|0|
| Child exit code in control.json |null|null|
| OS wall seconds / max RSS bytes |0.03 /2,850,816|0.03 /2,818,048|

Both controls record observed-before-kill=true, unfinished-stage-marked-complete=false and cryptographic_work=false. Both child stdout files contain only `running1test` with no completion line; child stderr is empty. Null status.code() is retained exactly: the source calls kill and wait, but the stored schema does not measure a particular terminating signal. The OS `signals received:0` row is not child signal telemetry. Operational 0.03 second timing and rounded CPU receipts support fixture accounting, with no algorithm-speed implication. The parent receipts place reference at 22:24:08 UTC and candidate at 22:24:10 UTC on 2026-10-16, inside launcher 22:24:07--22:24:11.

The current reference native unit file is 37,614,112 bytes, SHA256 `bf48ea22df2d8e1c2b94f1462cde3d1c4f64737d4cf6d3bca4623d5b4bef0a9c`; candidate is 37,609,376 bytes, SHA256 `cdb325a657f6da2d77bb4be8d8084b4d25f3552ba891bb622bf3fdff4e4f457e`. Both match prospective bindings and the new before/after raw receipts. Original clean logs name these exact unit paths; source/tree markers match 015 / tree 5af766cd338b7a4639ab52337564ebe9267a4b23; before/after statuses are empty. Separate feature argument files and current Cargo fingerprints agree: reference has no features and candidate has cached-fixed-modulus-reduction, with empty rustflags. Current dependency files include replay_trace.rs. The source manifest default is empty. This is a bounded source/build/log/fingerprint chain; it is not a hermetic rebuild, nor does a hash observed now create an older invocation-time receipt. The unit files are distinct from the four installed scientific binaries.

Every external Git object in the producer's 140 path map was independently read as exact Git bytes, checked against its Git blob SHA1 and SHA256/size, and compared with the worktree; all 140 match and the path set is exact. Protected objects were handled as opaque bytes. All 32 raw files match the corresponding original external output files and the raw manifest. The original clean archive matches its c6f Git blob and hashes to `09347071c8857216ae1597898d345307fc2a4086930c4252150cc0c6e2081f76`; all 25 selected original build/source members match the retained inputs. The three exact snapshot path hashes and parent commit match. Required review plans/handoff/input objects match prospective319. Original frozen 151 launcher/protocol/bindings equal retained and current copies. The current dispatch queue has later completion/archive and prospective review-scope metadata, so it differs from 151; its retained invocation input still equals 151 exactly. This drift is disclosed and is not used to rewrite the frozen launch contract.

The new archive is 683,995 bytes, SHA256 `3e6ccad8ab3441f53e5f5781dc15272218884b241f300f0da0fa418d481a6044`. It contains 112 ordinary members; every member's bytes and hash/size match its worktree file. The 111 payload manifest entries plus the manifest itself form the exact archive member set. All complete retained readback bytes at the declared hash-addressed cache path equal the archive. Raw transfer command/output logs retain the exact logical evidence name, push --no-cache, uploaded=true/replaced=false/cached=false, pull path and fetched hash, remote-verification text, cmp, and exit0. I did not perform a network transfer or a new remote observation. The transport client currently hashes to the retained before/after `aab28a781f807f4f3ef364336b04d2ff18a2bb8483e1c6d1494baf5c1c3a561a`; its source/build provenance remains unestablished. That source question is separate from the directly rehashed complete readback equality.

Failures remain visible. The initial claim push was rejected fetch-first with exit 2; later merge/publication receipts are separate. Original metadata verification stdout reports INCOMPLETE for both arms despite process exit 0. Auditing metadata.py shows its mistaken 128 filtered expectation. Auditing the separate correction shows it reads existing raw logs, requires exactly one selected successful parent, and preserves the observed 85 filtered without launching native tests. My independent 85 count and event recomputation were saved first. The original and corrected protected control JSONs remain semantically unread. Full publication whitespace check exit 2 has 10 notices across 4 raw logs; original bytes remain unchanged, and authored-style logs are empty. Producer source-bindings also asserts a JavaScript tagged-template parse failure; the only listed diagnostic narrative, metadata-attempts.md, is protected and hash-only, so I do not claim independent verification of that exact diagnostic. A checker DeprecationWarning was preserved without changing its source.

Only after the raw note did I read the expressly allowed prior 06cc13 report. It is byte-identical to 6045fa6c57054541c5a18566fc7c5ca15357147b, SHA256 `b4a06acd8c86e21578a34110c4c03e628d85195d2eb04d67b2f6166afcb01be8`. Its original resource/build/custody verdict stays inconclusive. Its old absent 015 retention and old missing unit invocation hashes have not been recovered or relabelled; e82 evidence is not substituted. Its complete root failure (4,161 passed, 1 failed, 117 ignored, exit 101) and separate filtered module pass (14 passed, 4,265 filtered, exit 0) are disclosed prior engineering inputs, outside this narrow rerun-free review. The filtered pass does not supply a complete root pass. No source, build, default, threshold or historical finding was changed by this reviewer, and declarations alone are not treated as establishing a new such change.

All 22 declared protected paths stayed excluded from semantic reads through this attestation. Opaque hashing covers direct/Git/archive representations; report.md, report.typ and report.pdf archive aliases were also kept opaque even where only their direct names were listed. The inventory separates 39 protected opaque representations from 453 unique nonprotected source/metadata paths, including their modes, phases, hashes, sizes and first/last inspection times. The sole prior report is expressly disclosed and is not a same-round sibling. No same-round sibling report or Coordinator parent discussion was read. Large dumps that exceeded display limits were followed with focused relevant source/log and prior-qualification excerpts; byte/hash coverage is accounted separately from displayed semantic excerpts.

The unchanged independence checker was run only on the original base plan with its automatically discovered prospective additive widening and this private standalone attestation. It composed one addendum, widened the protection by 18 paths to 22, and passed. The checker is a declaration-consistency check; it does not authenticate truthfulness, provider identity, the producer's global process history, scientific correctness or official admission.

Requested runtime is native Codex, review-adversarial/xhigh; capability floor low is a separate policy field. Actual served model and actual effort are unexposed and recorded unknown. No provider substitution or offline adapter was used. Reviewer counts are zero for scientific runs, native/control tests, new builds, target operations, benchmarks, network custody operations and repository mutations. All writes are private inspection/review artifacts under the assigned temporary directory. Publication, claims/releases and official gate decisions remain outside this invocation.

The following YAML blocks are byte-identical to the standalone companions.

```yaml
validation_report:
  task_id: TASK-20261016-38a4d9
  status: complete_private_review
  verdict: holds
  joint_verdicts:
    interruption_invocation_retention_binding: holds
  scope: The new exact native interruption parent/helper invocations and retained raw/custody binding only. Official
    source admission, evidence strength and science decisions are outside this verdict.
  source_raw_first_note:
    path: /private/tmp/TASK-20261016-38a4d9-independent/pre-summary-derivation.md
    sha256: 6286249a7be28c9986c521efc218ecceb344e5a4229b8dcf49202fc73912b8d4
    bytes: 24542
    saved_before_semantic_producer_maps_checkers_manifests: true
  bindings:
    prospective_plan_commit: 319cc51b9f
    snapshot_content_commit: c332aef9d2466049a38335b6bb22c9a230ee406d
    snapshot_three_path_hashes_match: true
    snapshot_parent_matches: true
    source_commit: 015fa7bb504ef63953e0e04e464bb266f4f207bf
    source_tree: 5af766cd338b7a4639ab52337564ebe9267a4b23
    replay_trace_sha256: 30fa162ab24097380e5635c3cd720680e53a76510c89dbf1bd166ddb673166a3
    external_evidence_commit: f6440f5c8f93db43ed33adf991a58df7648ff6c9
    external_git_blobs: 140
    external_git_blob_hashes_sizes_and_worktree_equality: all_match
    new_archive_sha256: 3e6ccad8ab3441f53e5f5781dc15272218884b241f300f0da0fa418d481a6044
    new_archive_bytes: 683995
    ordinary_members: 112
    payload_manifest_entries: 111
    member_hash_size_worktree_equalities: all_match
    complete_readback_bytes_equal: true
    raw_files: 32
    raw_manifest_equalities: all_match
    original_external_raw32_equal_retained_copies: true
    old_archive_sha256: 09347071c8857216ae1597898d345307fc2a4086930c4252150cc0c6e2081f76
    old_build_members_checked: 25
    old_build_members_match: true
  native_observations:
    reference:
      selected_parent: replay_trace::tests::flushed_begin_survives_bounded_child_interruption
      passed: 1
      failed: 0
      ignored: 0
      measured: 0
      filtered: 85
      parent_exit: 0
      raw_files: 16
      trace_events:
      - stage: total
        event: begin
        stage_id: 0
        parent_id: null
        pid: 14894
        status: null
      - stage: interruption_fixture_wait
        event: begin
        stage_id: 1
        parent_id: 0
        pid: 14894
        status: null
      end_or_terminal_records: 0
      control:
        child_exit_code: null
        cryptographic_work: false
        flushed_begin_observed_before_kill: true
        schema: isogeny-trace-interruption-control/v1
        unfinished_stage_marked_complete: false
      current_unit_executable:
        bytes: 37614112
        sha256: bf48ea22df2d8e1c2b94f1462cde3d1c4f64737d4cf6d3bca4623d5b4bef0a9c
      current_cargo_fingerprint_features: []
      new_invocation_before_after_hashes_match: true
      child_stdout: running1test only; no completion line
      child_stderr_bytes: 0
    candidate:
      selected_parent: replay_trace::tests::flushed_begin_survives_bounded_child_interruption
      passed: 1
      failed: 0
      ignored: 0
      measured: 0
      filtered: 85
      parent_exit: 0
      raw_files: 16
      trace_events:
      - stage: total
        event: begin
        stage_id: 0
        parent_id: null
        pid: 14915
        status: null
      - stage: interruption_fixture_wait
        event: begin
        stage_id: 1
        parent_id: 0
        pid: 14915
        status: null
      end_or_terminal_records: 0
      control:
        child_exit_code: null
        cryptographic_work: false
        flushed_begin_observed_before_kill: true
        schema: isogeny-trace-interruption-control/v1
        unfinished_stage_marked_complete: false
      current_unit_executable:
        bytes: 37609376
        sha256: cdb325a657f6da2d77bb4be8d8084b4d25f3552ba891bb622bf3fdff4e4f457e
      current_cargo_fingerprint_features:
      - cached-fixed-modulus-reduction
      new_invocation_before_after_hashes_match: true
      child_stdout: running1test only; no completion line
      child_stderr_bytes: 0
  preserved_failures_and_limits:
    initial_claim_push: Original fetch-first rejection with exit2 retained; merge/success receipts separate. Reviewer
      performed neither.
    initial_metadata_checker: Original logs report INCOMPLETE for exact parent count in both arms. metadata.py mistakenly
      requires128filtered. Process exit0 did not mean semantic completeness.
    corrected_metadata_checker: Source audits existing raw logs, selects exactlyoneparent and retains actual85filtered.
      It does not run tests. Reviewer recomputation predates reading it. Original protected control JSONs remain
      hash-only.
    publication_whitespace: Full check exit2 with10notices in4raw logs retained. Authored-style stdout/stderr empty;
      producer reports authored exit0. Original raw bytes not rewritten.
    tagged_template_parse_failure: Producer assertion only; exact narrative diagnostic remains protected/hash-only,
      so not independently confirmed.
    current_dispatch_queue_drift: Archived queue equals151. Current queue differs through completion/archive and
      prospective review scope metadata; no frozen launcher/protocol/binding drift.
    old_retention: Original missing frozen015raw and old unit invocation hashes remain absent; new receipts do not
      recover history.
    store_client: Current hash matches before/after aab28a781f807f4f3ef364336b04d2ff18a2bb8483e1c6d1494baf5c1c3a561a;
      source/build provenance not independently established.
    kill_signal: Source calls kill and wait; child_exit_code is null. Specific terminating signal not measured.
    flush_durability: File::flush before begin visibility; fsync/durable-media guarantee not established.
    unit_provenance: Original clean source/build logs, exact unit paths and feature arguments plus current fingerprint/d
      files support bounded linkage. Current hashes are not old invocation-time hashes or a hermetic rebuild.
    global_execution_audit: Exact retained launcher/source/log scope contains two parents and their two logging
      helpers. No global host process audit was performed.
    prior_review: Unchanged disclosed06cc13 read after raw note, SHA256b4a06acd8c86e21578a34110c4c03e628d85195d2eb04d67b2f6166afcb01be8;
      original resource verdict remains inconclusive.
    root_gate: 'As disclosed by prior report: complete4161passed/1failed/117ignored exit101, and separate filtered14passed/4265filtered
      exit0. Neither rerun nor replaced by this review.'
  independence:
    same_round_sibling_reports_read: false
    semantic_protected_reads: 0
    declared_protected_paths: 22
    protected_opaque_representations: 39
    protected_archive_report_aliases_also_excluded: true
    checker:
      checker_path: /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/tools/check_review_independence.py
      checker_sha256: ccb6fa518bec26e7d8ee625a19cc22a15800362a5a50a78185cee93eb25a38a7
      plan: /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-plan.yaml
      automatic_addenda_discovered: 1
      additive_blind_paths: 18
      total_protected_paths: 22
      standalone_attestation_only: true
      exit_code: 0
      result: 'PASS: 1 report(s), every joint owned and attested, blindness respected, controls declared'
      warning: 'DeprecationWarning: maxsplit is passed as positional argument at line293'
      no_checker_or_plan_mutations: true
  reviewer_execution:
    scientific_runs: 0
    control_test_invocations: 0
    new_builds: 0
    targets: 0
    benchmarks: 0
    network_custody_operations: 0
    repository_mutations: 0
    provider_substitution: false
  runtime_provenance:
    runtime: native Codex
    requested_policy: review-adversarial
    requested_effort: xhigh
    capability_floor: low
    actual_served_model: null
    actual_served_effort: null
    provider_substitution: false
  validated_at_utc: '2026-10-16T22:53:49.976663+00:00'
  source_read_inventory:
    path: /private/tmp/TASK-20261016-38a4d9-independent/source-read-inventory.json
    sha256: db10d37a7a241ab038c5a501664fdfe4dfd43a5d94a1d022a836d9fa8cada2ef
    bytes: 464308
```

```yaml
review_attestation:
  task_id: TASK-20261016-38a4d9
  joints_owned:
  - interruption_invocation_retention_binding
  joint_verdicts:
    interruption_invocation_retention_binding: holds
  verdict: holds
  read_sibling_reports: false
  blind_from_respected: true
  sources_read:
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/PROTOCOL.md
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/PROTOCOL.md@1517801dfce137ba966bced3b16dfb50a82ddc61
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/archives/TASK-20261016-0b8b61/receipt.md@c332aef9d2466049a38335b6bb22c9a230ee406d
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/bindings.json
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/bindings.json@1517801dfce137ba966bced3b16dfb50a82ddc61
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/claims/TASK-20261016-38a4d9.1.claim.json@59a9093b96
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/dispatch_queue.json
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/dispatch_queue.json@1517801dfce137ba966bced3b16dfb50a82ddc61
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/execution/TASK-20261016-7b4402/source-bindings.json
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/execution/TASK-20261016-7b4402/source-bindings.json@c332aef9d2466049a38335b6bb22c9a230ee406d
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/handoffs/TASK-20261016-38a4d9.yaml
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/handoffs/TASK-20261016-38a4d9.yaml@319cc51b9f
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/native-command.sh
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/native-command.sh@1517801dfce137ba966bced3b16dfb50a82ddc61
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-inputs-38a4d9.json
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-inputs-38a4d9.json@319cc51b9f
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-plan-clarification-38a4d9.yaml
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-plan-clarification-38a4d9.yaml@319cc51b9f
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-plan-composed-38a4d9.yaml
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-plan-composed-38a4d9.yaml@319cc51b9f
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-plan.yaml
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-plan.yaml@319cc51b9f
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/reviews/TASK-20261016-06cc13/report.md
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/reviews/TASK-20261016-06cc13/report.md@6045fa6c57054541c5a18566fc7c5ca15357147b
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/orchestration/fast_yaml.py
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/tools/check_review_independence.py
  - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/tools/fast_yaml.py
  - /Volumes/SSD990-2/crypto/.claude/worktrees/agent-affd575914239114f/target/release/crypto
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./candidate/build-command.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./candidate/build.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./candidate/build.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./candidate/feature-arguments.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./candidate/git-status-after.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./candidate/git-status-before.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./candidate/tests.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./candidate/tests.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./candidate/tests.stdout
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./explicit-build-environment.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./flags.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./host.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./os.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./reference/build-command.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./reference/build.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./reference/build.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./reference/feature-arguments.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./reference/git-status-after.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./reference/git-status-before.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./reference/tests.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./reference/tests.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./reference/tests.stdout
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./rustc.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./source-commit.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz!./source-tree.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/clean-retake-015fa7bb504e/native-controls.tar.gz@c6fb2a332ad42f0be2b30f1c0b0b6e1ec04221f8
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/.gitattributes
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/.gitattributes@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/archive-info.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/archive-info.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/authored-style.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/authored-style.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/authored-style.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/authored-style.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/branch-sync-hygiene.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/branch-sync-hygiene.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/branch-sync-hygiene.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/branch-sync-hygiene.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/branch-sync.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/branch-sync.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/branch-sync.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/branch-sync.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim-initial.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim-initial.exit-code.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim-push.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim-push.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim-push.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim-push.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim-reconciled-push.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim-reconciled-push.exit-code.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/claim.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/correct-log-count.py
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/correct-log-count.py@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody-check.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody-check.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody-check.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody-check.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/ended-utc.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/ended-utc.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/pull.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/pull.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/pull.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/pull.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/push.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/push.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/push.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/push.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/readback.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/readback.sha256@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/started-utc.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/started-utc.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/store-client-after.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/store-client-after.sha256@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/store-client-before.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/store-client-before.sha256@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/store-index.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/store-index.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/transfer.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/transfer.exit-code.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/verification.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/verification.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/verify.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/verify.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/verify.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/custody/verify.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/frozen-goal-diff.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/frozen-goal-diff.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/PROTOCOL.md
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/PROTOCOL.md@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/bindings.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/bindings.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/dispatch_queue.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/dispatch_queue.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/native-command.sh
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/native-command.sh@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/build-command.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/build-command.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/build.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/build.exit@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/build.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/build.stderr@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/feature-arguments.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/feature-arguments.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/git-status-after.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/git-status-after.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/git-status-before.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/git-status-before.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/tests.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/tests.exit@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/tests.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/tests.stderr@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/tests.stdout
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/candidate/tests.stdout@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/explicit-build-environment.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/explicit-build-environment.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/flags.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/flags.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/host.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/host.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/os.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/os.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/build-command.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/build-command.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/build.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/build.exit@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/build.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/build.stderr@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/feature-arguments.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/feature-arguments.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/git-status-after.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/git-status-after.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/git-status-before.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/git-status-before.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/tests.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/tests.exit@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/tests.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/tests.stderr@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/tests.stdout
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/reference/tests.stdout@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/rustc.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/rustc.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/source-commit.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/source-commit.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/source-tree.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/original-clean-build/source-tree.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/replay_trace.rs
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/inputs/replay_trace.rs@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher-argv.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher-argv.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher-ended-utc.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher-ended-utc.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher-started-utc.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher-started-utc.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher.exit-code.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/launcher.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-correction.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-correction.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-correction.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-correction.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-prepare.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-prepare.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-prepare.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-prepare.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-verify.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-verify.exit-code.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-verify.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-verify.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-verify.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-verify.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata.py
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata.py@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!.gitattributes
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!branch-sync-hygiene.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!branch-sync-hygiene.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!branch-sync.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!branch-sync.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!claim-initial.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!claim-push.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!claim-push.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!claim-reconciled-push.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!claim.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!claim.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!correct-log-count.py
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!frozen-goal-diff.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/PROTOCOL.md
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/bindings.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/dispatch_queue.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/native-command.sh
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/candidate/build-command.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/candidate/build.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/candidate/build.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/candidate/feature-arguments.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/candidate/git-status-after.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/candidate/git-status-before.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/candidate/tests.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/candidate/tests.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/candidate/tests.stdout
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/explicit-build-environment.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/flags.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/host.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/os.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/reference/build-command.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/reference/build.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/reference/build.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/reference/feature-arguments.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/reference/git-status-after.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/reference/git-status-before.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/reference/tests.exit
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/reference/tests.stderr
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/reference/tests.stdout
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/rustc.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/source-commit.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/original-clean-build/source-tree.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!inputs/replay_trace.rs
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!launcher-argv.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!launcher-ended-utc.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!launcher-started-utc.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!launcher.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!launcher.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!launcher.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata-correction.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata-correction.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata-prepare.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata-prepare.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata-verify.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata-verify.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata-verify.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata.py
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!package.py
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!payload-manifest.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!pdf-preview.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!pdf-preview.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!pdfinfo.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!post-sync-binding-check.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!provenance-before.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw-manifest.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/build-features.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/environment.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/executable-after.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/executable-before.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/finished-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/native-argv.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/os-time.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/parent.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/parent.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/retained/child.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/retained/child.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/retained/control.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/retained/interrupted.jsonl
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/source-commit.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/candidate/started-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/build-features.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/environment.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/executable-after.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/executable-before.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/finished-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/native-argv.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/os-time.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/parent.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/parent.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/retained/child.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/retained/child.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/retained/control.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/retained/interrupted.jsonl
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/source-commit.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!raw/reference/started-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!render.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!render.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!transfer-command.sh
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!write-report.py
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/package.py
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/package.py@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/package.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/package.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/package.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/package.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/payload-manifest.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/payload-manifest.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/pdf-preview.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/pdf-preview.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/pdf-preview.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/pdf-preview.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/pdfinfo.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/pdfinfo.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/post-sync-binding-check.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/post-sync-binding-check.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/provenance-before.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/provenance-before.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-style.exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-style.exit-code.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-style.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-style.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-style.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-style.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw-manifest.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw-manifest.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/build-features.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/build-features.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/environment.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/environment.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/executable-after.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/executable-after.sha256@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/executable-before.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/executable-before.sha256@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/exit-code.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/finished-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/finished-at.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/native-argv.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/native-argv.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/os-time.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/os-time.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/parent.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/parent.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/parent.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/parent.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/retained/child.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/retained/child.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/retained/child.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/retained/child.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/retained/control.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/retained/control.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/retained/interrupted.jsonl
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/retained/interrupted.jsonl@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/source-commit.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/source-commit.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/started-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/candidate/started-at.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/build-features.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/build-features.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/environment.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/environment.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/executable-after.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/executable-after.sha256@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/executable-before.sha256
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/executable-before.sha256@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/exit-code.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/finished-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/finished-at.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/native-argv.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/native-argv.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/os-time.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/os-time.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/parent.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/parent.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/parent.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/parent.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/retained/child.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/retained/child.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/retained/child.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/retained/child.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/retained/control.json
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/retained/control.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/retained/interrupted.jsonl
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/retained/interrupted.jsonl@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/source-commit.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/source-commit.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/started-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/raw/reference/started-at.txt@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/render.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/render.stderr.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/render.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/render.stdout.log@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/transfer-command.sh
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/transfer-command.sh@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/verify-custody.py
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/verify-custody.py@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/write-report.py
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/write-report.py@f6440f5c8f93db43ed33adf991a58df7648ff6c9
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015@015fa7bb504ef63953e0e04e464bb266f4f207bf:tools/isogeny-cli/Cargo.toml
  - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015@015fa7bb504ef63953e0e04e464bb266f4f207bf:tools/isogeny-cli/src/replay_trace.rs
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/clean-retake-v1/candidate/target/release/.fingerprint/isogeny-cli-091b88e44789ba98/test-bin-isogeny.json
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/clean-retake-v1/candidate/target/release/deps/isogeny-091b88e44789ba98
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/clean-retake-v1/candidate/target/release/deps/isogeny-091b88e44789ba98.d
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/clean-retake-v1/reference/target/release/.fingerprint/isogeny-cli-8734bd11e3dad22d/test-bin-isogeny.json
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/clean-retake-v1/reference/target/release/deps/isogeny-8734bd11e3dad22d
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/clean-retake-v1/reference/target/release/deps/isogeny-8734bd11e3dad22d.d
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/build-features.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/environment.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/executable-after.sha256
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/executable-before.sha256
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/finished-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/native-argv.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/os-time.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/parent.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/parent.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/retained/child.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/retained/child.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/retained/control.json
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/retained/interrupted.jsonl
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/source-commit.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/candidate/started-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/custody-readback-cache/sha256/3e/3e6ccad8ab3441f53e5f5781dc15272218884b241f300f0da0fa418d481a6044
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/build-features.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/environment.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/executable-after.sha256
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/executable-before.sha256
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/exit-code.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/finished-at.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/native-argv.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/os-time.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/parent.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/parent.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/retained/child.stderr.log
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/retained/child.stdout.log
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/retained/control.json
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/retained/interrupted.jsonl
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/source-commit.txt
  - /Volumes/SSD990-2/crypto/isogeny-fixed-modulus-builds-20261016/interruption-retake-015-v1/reference/started-at.txt
  - /opt/homebrew/bin/gtimeout
  - /private/tmp/interruption-supplement-reviewer-task.txt
  source_read_modes_and_phases: Complete per-read mode/hash/size/timestamps in source-read-inventory.json; sources_read
    includes semantic and nonprotected opaque metadata reads. Protected opaque reads are disclosed only in protected_hash_only_inventory.
  protected_hash_only_inventory:
    declared_protected_paths:
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/execution/TASK-20261016-7b4402/implementation-receipt.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/control-check-v2.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/control-check.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/flow.svg
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-attempts.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!control-check-v2.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!control-check.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!flow.svg
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata-attempts.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!preview/page-1.png
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!preview/page-2.png
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!visual-data.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!visual-inspection.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/preview/page-1.png
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/preview/page-2.png
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-check.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-note.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/report.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/report.pdf
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/report.typ
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/visual-data.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/visual-inspection.json
    actually_hashed_paths_and_aliases:
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/execution/TASK-20261016-7b4402/implementation-receipt.md
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/execution/TASK-20261016-7b4402/implementation-receipt.md@c332aef9d2466049a38335b6bb22c9a230ee406d
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/control-check-v2.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/control-check-v2.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/control-check.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/control-check.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/flow.svg
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/flow.svg@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-attempts.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/metadata-attempts.md@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!control-check-v2.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!control-check.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!flow.svg
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!metadata-attempts.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!preview/page-1.png
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!preview/page-2.png
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!report.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!report.pdf
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!report.typ
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!visual-data.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/native-controls.tar.gz!visual-inspection.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/preview/page-1.png
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/preview/page-1.png@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/preview/page-2.png
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/preview/page-2.png@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-check.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-check.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-note.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/publication-note.md@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/report.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/report.md@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/report.pdf
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/report.pdf@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/report.typ
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/report.typ@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/visual-data.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/visual-data.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/visual-inspection.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/isogeny_world_frontier_20261016/replay-optimization-v1/interruption-retake-015-v1/visual-inspection.json@f6440f5c8f93db43ed33adf991a58df7648ff6c9
    semantic_reads: false
    hashes_sizes_and_representations: source-read-inventory.json protected_hash_only and independently_verified_bindings
  source_raw_first:
    procedure:
    - Read frozen assignment/plans/protocol/bindings/launcher.
    - Derive source015 Session/stage/flush/retention/parent/helper/kill/wait semantics directly from Git source
      and retained original source.
    - Inspect original32raw files, old build/source inputs, raw custody command/output logs and current binary/fingerprint
      files; independently recompute test counts, events and byte identities.
    - Save timestamped hashed pre-summary-derivation.md and raw recomputations before semantic producer source-bindings,
      metadata.py, correct-log-count.py or manifests.
    - Then audit producer assertions, preserved failure logs, all140Git blobs,112archive members and readback; keep
      protected contents excluded through attestation.
    hashed_note:
      path: /private/tmp/TASK-20261016-38a4d9-independent/pre-summary-derivation.md
      sha256: 6286249a7be28c9986c521efc218ecceb344e5a4229b8dcf49202fc73912b8d4
      bytes: 24542
      saved_before_semantic_producer_maps_checkers_manifests: true
    initial_note_counter_correction_disclosed: true
    anticipated_contract_in_required_plan_was_not_treated_as_observed_result: true
  prior_control_inspections:
    prior_report: /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/reviews/TASK-20261016-06cc13/report.md
    prior_report_read_after_hashed_note: true
    prior_is_same_round_sibling: false
    prior_report_unchanged_sha256: b4a06acd8c86e21578a34110c4c03e628d85195d2eb04d67b2f6166afcb01be8
    prior_resource_joint_remains: inconclusive
    old_complete_root_failure_and_filtered_pass: Disclosed prior engineering inputs, not rerun or independently
      expanded in this narrow review.
    proves_too_much_controls:
    - Passing stdout alone is insufficient; the new raw32files are separately retained and bound.
    - Old e82trace is not relabelled015; old missing retention is not recovered.
    - Null child_exit_code does not measure signal9.
    - Filtered module pass does not replace complete root FAIL.
  exact_scope:
    prospective_plan_commit: 319cc51b9f
    snapshot_content_commit: c332aef9d2466049a38335b6bb22c9a230ee406d
    ownership_claim_published_at: 59a9093b96
    external_evidence_commit: f6440f5c8f93db43ed33adf991a58df7648ff6c9
    source_commit: 015fa7bb504ef63953e0e04e464bb266f4f207bf
    external_git_blobs_checked: 140
    ordinary_archive_members_checked: 112
    raw_files_checked: 32
    readback_bytes_checked: 683995
  source_read_inventory:
    path: /private/tmp/TASK-20261016-38a4d9-independent/source-read-inventory.json
    sha256: db10d37a7a241ab038c5a501664fdfe4dfd43a5d94a1d022a836d9fa8cada2ef
    bytes: 464308
  runtime_provenance:
    runtime: native Codex
    requested_policy: review-adversarial
    requested_effort: xhigh
    capability_floor: low
    actual_served_model: null
    actual_served_effort: null
    provider_substitution: false
  requested_policy: review-adversarial
  requested_effort: xhigh
  capability_floor: low
  actual_served_model: null
  actual_served_effort: null
  provider_substitution: false
  executions:
    scientific: 0
    control_tests: 0
    builds: 0
    benchmarks: 0
    targets: 0
    network_custody_operations: 0
    repository_mutations: 0
    allowed_metadata_checks: Read-only source/Git/hash/tar/JSON/log tools and unchanged check_review_independence.py
      only.
  limitations:
  - Current native binary hashes and fingerprints are not historical invocation-time unit hashes or a hermetic rebuild.
  - Source/build provenance of the store client is not independently established; full retained readback-byte equality
    was independently checked.
  - Null child_exit_code does not expose the terminating signal; File::flush is not fsync.
  - The JavaScript parse failure is asserted by producer source-bindings; protected metadata-attempts.md was hashed
    only, so its exact diagnostic is not independently confirmed.
  - The current dispatch queue has later completion/review scope metadata; the archived frozen queue bytes match151.
  - This verdict owns only the new invocation/retention binding; no official source admission, evidence-strength,
    root-gate or scientific/performance decision.
  signed_by: Fresh independent native Codex Validator invocation for TASK-20261016-38a4d9
  attested_at_utc: '2026-10-16T22:53:49.699560+00:00'
  unchanged_independence_check:
    checker_path: /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/tools/check_review_independence.py
    checker_sha256: ccb6fa518bec26e7d8ee625a19cc22a15800362a5a50a78185cee93eb25a38a7
    plan: /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/next-native-source-20261016/interruption-retake-015-v1/review-plan.yaml
    automatic_addenda_discovered: 1
    additive_blind_paths: 18
    total_protected_paths: 22
    standalone_attestation_only: true
    exit_code: 0
    result: 'PASS: 1 report(s), every joint owned and attested, blindness respected, controls declared'
    warning: 'DeprecationWarning: maxsplit is passed as positional argument at line293'
    no_checker_or_plan_mutations: true
```
