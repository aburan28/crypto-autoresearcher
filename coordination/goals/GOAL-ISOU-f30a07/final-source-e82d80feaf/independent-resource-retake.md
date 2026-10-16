# Independent resource and trace source retake at e82d80feaf

Review task: `TASK-20261016-ed10a6`.

Archival task: `TASK-20261016-9b1e68`.

Native agent identity: `/root/frontier_coordinator_resume/cm_norm_independent_review`.

Date: 2026-10-16, America/Los_Angeles.

All three assigned joints **hold at static source and test-definition scope** for published crypto commit `e82d80feaf82d3730576ccd9137911b336f9dab8`. The post-acknowledgement zero-RSS exception is removed, and the missing negative-monitor controls are now defined through the real supervisor loop. The trace changes preserve the arithmetic predicates, explicitly fail requested evidence errors, and record replay-core completion separately from later public admission. I found no additional actionable defect within those scoped joints.

This retake does not claim that a test, binary, benchmark, scientific target, or independent mathematical replay ran or passed. None was executed here. I read no new raw monitor, compact, trace, interruption, clean-build, or custody control payload, no control PASS summary, and no live target output. Repository files were not modified and no artifact was uploaded or transferred. Only this authorized temporary report was written for Coordinator archival.

My prior review of source 9a2e133099 missed that its `resources_released` condition accepted zero RSS after acknowledgement. The explicitly allowed Coordinator addendum identified that gap and required this repair and retake. The earlier positive resource verdict must not be used as evidence that the old source handled that case. This review independently traces the repaired source and new test definitions; it does not rewrite the earlier report or turn the repair into a mathematical result.

## Frozen provenance and boundaries

I read the exact review plan and manifest first. The plan was readable at harness commit `7e8d8bcf0e`, at `coordination/goals/GOAL-ISOU-f30a07/final-source-e82d80feaf/review-plan.yaml`. The crypto checkout HEAD was exactly `e82d80feaf82d3730576ccd9137911b336f9dab8`. All thirteen named source/test files matched the frozen manifest before their contents were used.

The compact producer and independent norm/point verifier hashes are byte-identical to the prior review. This is not a new independent mathematical proof or a new arithmetic review. The scope here is the three exact resource/control/trace joints below. The source comparison against 9a2e133099 also showed no changes to the field arithmetic, rational-map checker, polynomial arithmetic, or challenge admission source inspected for this retake. Supporting challenge excerpts were read at the exact e82 commit.

The selected inference policy was native `review-adversarial` with requested `xhigh` effort. The actual served model, served effort, and native runtime session UUID are not exposed and remain unknown. No API or provider substitution was used. The same reviewer's own prior report and the permitted Coordinator zero-RSS addendum were used explicitly; no sibling review was read.

## resource_monitoring_and_ack — holds

The production entry [supervisor.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/supervisor.rs:163) delegates to a private `run_with_sampler` with the platform `resident_bytes` function. The injected sampler is an internal dependency, not a production CLI or environment override.

At lines 248–257, the supervisor identifies both `challenge __judge` and `compact-cm __worker` as acknowledgement-gated operations. The repaired predicate at lines 274–276 is:

```rust
sample_resident(child.id()).filter(|rss| resource_ready.is_none() || *rss > 0)
```

For either gated worker, `Some(0)` now enters the unavailable-telemetry branch both before and after release. It cannot reset the unavailable timer merely because an earlier positive sample existed. `None` follows that same branch. A usable positive sample updates the sampled peak, checks the 8 GiB cap, and only then creates the initially absent ready file at lines 277–292. Memory excess therefore does not authorize work first.

Persistent unavailable telemetry while the child remains live increments the unavailable counter, starts a grace timer, and after the documented 100 ms grace sets `monitor_unavailable`, kills, and waits for the child at lines 294–307. A later usable sample within that grace resets the timer. Short unavailable periods remain explicitly tolerated by this sampling protocol; the implementation does not claim continuous observation or an operating-system-enforced memory cap.

The compact worker waits for the ready file before invoking its operation in [compact_cm.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/compact_cm.rs:608). The challenge worker does the same before `worker(...)` in [challenge.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/challenge.rs:399). These normal public wrappers construct their own worker arguments and fresh paths. Their public option parsers do not admit a caller's RSS sampler or `--rss-ready` override.

The done marker is checked at `supervisor.rs:270–272`. The compact and challenge workers create it only after their protected operation has returned or been caught as a failure. It permits RSS polling to stop during exit cleanup. The wall-clock watchdog is checked before that marker on each loop, so it remains active during cleanup. This is the scope of the sampled algebra envelope, not a claim to monitor every cleanup allocation.

Supervisor acceptance at `supervisor.rs:326–365` requires successful child exit, parsed PASS, and no recorded timeout, memory excess, or monitor-unavailable state. A failed resource status cannot be overridden by an inner mathematical result. The compact wrapper propagates that outer status at `compact_cm.rs:696–730`. Public challenge judging separately rejects/censors a non-PASS resource receipt and rejects a zero sampled peak at `challenge.rs:338–355`.

The generic supervisor can reuse a sealed receipt in an existing directory, but these public compact and judge paths require a fresh outer directory before calling it. That reuse branch is not a normal-public-path substitute for new monitoring.

Direct internal worker invocation still has the previously recorded narrower meaning: a caller can reach an internal path using an existing acknowledgement file, but that invocation does not create the qualifying outer public resource receipt and does not match a frozen public scientific argv. This review does not treat internal helper invocation as an authenticated external security boundary or as demonstrated public scientific admission.

## negative_resource_control_coverage — holds for definitions

The new native test at [supervisor.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/supervisor.rs:407) explicitly defines all four required cases through the same `run_with_sampler` loop:

| State | Injected samples | Required acknowledgement and progress evidence |
|---|---|---|
| Before acknowledgement, missing | Always `None` | Ready and entered markers absent; peak zero |
| Before acknowledgement, zero | Always `Some(0)` | Ready and entered markers absent; peak zero |
| After acknowledgement, missing | Positive until entered, then `None` | Ready and entered markers present; positive retained peak |
| After acknowledgement, zero | Positive until entered, then `Some(0)` | Ready and entered markers present; positive retained peak |

The fixture is an actual child shell process, defined at lines 425–427, which waits on the same acknowledgement-file convention, writes an entered marker, and then remains in an active loop. It performs no cryptographic fixture computation. Its fourth and sixth arguments are the ready and entered paths supplied at lines 440–450. Thus the after-acknowledgement cases cannot switch to loss before the fixture actually records entry: the sampler returns `Some(4096)` until that marker exists, at lines 451–458.

Each case requires exactly `RESOURCE_MONITOR_UNAVAILABLE`, not merely an arbitrary non-PASS result, at lines 460–463. It then checks the ready/entered markers, expected peak, and a positive unavailable-sample count. Since the fixture otherwise remains alive and emits no success record, that status requires the supervisor's monitored kill/wait path rather than natural successful exit or the separate five-second wall timeout. The checks establish both withholding before release and termination after release in the definitions; they are stronger than an exit-code-only assertion.

The after-acknowledgement cases also define a positive-progress observation before introducing loss. The byte-identical compact CLI test continues to define successful public supervision and a positive sampled peak at `tools/isogeny-cli/tests/compact_cm_cli.rs:68–81`. These cover positive release/progress and a normal successful command definition. There is no distinct new fixture for a temporary loss followed by recovery; the recovery transition is visible in the source timer reset, and a separate recovery test is not among this plan's named required objects.

The sampler value 4096 is synthetic test input, not a measured process RSS value. The emitted fixture metadata labels both synthetic injection and absence of cryptographic work at lines 476–483. The real supervised child/process termination is distinct from the synthetic telemetry. The controls are compiled only under `cfg(all(test, unix))`; this source coverage is therefore a Unix test-definition result, not executed cross-platform validation. No new raw fixture outputs or test summary were read.

This closes the missing-definition finding from my 9a review and specifically reaches the post-acknowledgement zero condition named by the Coordinator addendum. Whether these controls pass in a clean build remains an execution/custody matter outside this retake.

## trace_scope_and_unchanged_acceptance — holds

The existing `verify_kernel` signature is preserved as a no-op observer wrapper at [verification_kernel.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/p192_p224_large_degree_isogenies_20261009/verification_kernel.rs:174). Its new observer form retains the original degree, squarefree, torsion, subgroup inverse/composition, and codomain computations and rejection predicates. The former `ok_or(...)?` inverse failure is expressed as an equivalent `match` with an error event. The observer does not return a mathematical verdict or replacement field value.

The generated replay dispatchers in [build.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/build.rs:79) start a trace session before their own setup/loading/parsing and finish it after the selected field engine returns. The replay body adds scoped stage observations around existing operations; the diff preserves their arithmetic arguments, comparisons, record fields, fixed transport seeds and scalar values. Enumeration supplies deterministic attempt/map/seed/transport stage indices. No changed field, polynomial, map-substitution, or compact norm predicates were found in the inspected diff.

When `ISOGENY_REPLAY_TRACE` is absent, `Session::start` returns an inactive session and observer events have no active trace. Existing no-op consumers retain their mathematical behavior. This does not assert zero timing overhead: stage wrappers and formatting can still cost time, and any later timing comparison needs its separately frozen overhead/A/A controls.

When tracing is requested, [replay_trace.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/replay_trace.rs:119) requires an absolute path and `create_new(true)` with an available parent. It does not overwrite an old trace or silently disable evidence. Initial/stage write and flush failures use explicit `expect`/`require` failure paths. The record writer at lines 27–43 writes a schema, fixed stage name/index, event, parent identity, PID, and monotonic operational elapsed time, adds a newline, and flushes. It records no private points or arbitrary environment contents.

Successful stage closure writes end only after the associated operation succeeds. Normal session finish writes the core total end followed by `COMPLETED`. Error drops record error events for unfinished nested frames and an ERROR terminal when those writes remain possible. A trace I/O failure propagates as failure; cleanup logs any further I/O failure rather than treating missing evidence as success. The `take()` operations before fallible finish writes avoid retrying an already-consumed stage as a second successful close.

The definitions cover the relevant evidence failures:

- `replay_trace_cli.rs:347–359` rejects existing, unavailable-parent, relative, and directory trace paths and checks that the pre-existing sentinel stays byte-identical.
- `replay_trace.rs:327–361` injects a read-only descriptor directly into test-only state, requiring finish to fail, active state to clear, and retained bytes to remain unchanged. It does not add a production evidence override.
- `replay_trace.rs:239–319` creates a real test child, waits until a flushed begin is readable, kills/waits for it, and requires exactly the total and unfinished-stage begins with no completion record. No cryptographic work occurs in that fixture.
- `replay_trace_cli.rs:206–234` compares the mathematical verification bytes, score, source identity, and deterministic trace structure between fixed trace-off/on definitions.
- `replay_trace_cli.rs:235–346` pairs the existing adversarial mutations and malformed input, recomputing affected outer map hashes, and requires identical non-success outcomes. Kernel/map failures also require error/terminal records where replay was reached.

A hard kill during an event write can leave an incomplete final line. Only complete, parseable, flushed records in the retained prefix establish event evidence. There is no asserted power-loss durability or guarantee of a terminal record after external termination. An unfinished begin describes activity reached, not a completed phase duration.

### Core completion and public admission

The trace's total is the replay core, not the entire public command. In the public judge, bounded submission preflight/snapshot work occurs in the parent; child document validation also occurs before entering the replay dispatcher. Preflight refusal may therefore produce no replay trace at all. This is consistent with tracing the replay core and must not be read as full-process phase accounting.

The core trace's `COMPLETED` at `replay_trace.rs:156–163` states only that this instrumented dispatcher returned normally and wrote its trace terminal. The challenge worker still validates fresh replay rows after that return at `challenge.rs:283–313`. The outer judge then requires the resource receipt, positive sampled peak, and exact status/season/degree/source/map binding at `challenge.rs:338–365` before constructing an `ACCEPTED` entry at lines 367–374. Trace terminal status is not among these admission predicates.

For example, an outer watchdog failure during post-core process handling cannot be reversed by an existing COMPLETED line. A later output-binding or row-binding failure likewise remains a rejection. Conversely, a preflight rejection does not imply that the instrumented algebra failed; it may never have started. Existing trace files, core terminals, saved scores, and raw PASS fragments are not substitute public challenge entries.

The published trace tests define valid trace-on/off equality, error paths, and interruption behavior. They do not define a separate executed test result for the combination of a core COMPLETED trace and failed outer admission; the rejection ordering above is established here by source tracing only. No such runtime event or target outcome is inferred.

## Recommendation and remaining verification

The reviewed source repairs the specifically identified normal-public-path RSS gap and supplies the required negative resource control definitions. No further source correction is required by this static retake. Archive this report and its attestation, preserve the earlier review/addendum, and keep subsequent clean execution and custody evidence as separate records.

This recommendation authorizes no scientific run and certifies no test receipt, clean build, binary identity, upload custody, release publication, timing result, or map admission. It does not reinstate an unexecuted M8191 instance or reinterpret any censored expanded-map run. The original implementation verification, scientific `/run`, resource, independent replay, custody, and official-state gates remain unchanged.

## Manifest matches

All entries below matched the plan's frozen source manifest:

```text
b82ff8fec77a12c3e6a2be543a1605c945fbcb715669cc2ab0bd1d42f25dda7d  tools/isogeny-cli/src/compact_cm.rs
277af787edfa8cd11e5d28b461f628afcda6afa88cd14501f625d84b24ef13d4  tools/isogeny-cli/src/compact_cm_verify.rs
c6020c16bcac00e4a8844e3a567353e805e162ec1f1a178883f6291dcb3d56f0  tools/isogeny-cli/src/supervisor.rs
210ae728bd0ead95889e619af2f1df929c7fc07393251b68d768dfcb8c215171  tools/isogeny-cli/src/replay.rs
30fa162ab24097380e5635c3cd720680e53a76510c89dbf1bd166ddb673166a3  tools/isogeny-cli/src/replay_trace.rs
32acd0fafb0405978923eb1294907cdceb443392b0d4e6768c210d7d323849e1  tools/isogeny-cli/src/main.rs
d4206de30915bd73c7d52340b145897ea2ffccd7c945b2e0ed5e95dc01171b9b  tools/isogeny-cli/build.rs
d91e463be410dfe6a87361df209c1008f42ed63169db14ba985a893d205c5c76  tools/isogeny-cli/src/verification_field.rs
8af87ece402ca0c6839e27fa68696fb8ac0daa8952cf03d36b0dca9ef70860dc  tools/isogeny-cli/src/verification_map.rs
8a9ef6e767da684ecc9038b17e273094bc598e7af9500ed47f89d0dc4e1e54de  research/p192_p224_large_degree_isogenies_20261009/verification_kernel.rs
0e2fc2d8dd3e7b7680919770afc919b7b627a3d39ff1aa24e2d4f7b95038b63d  research/p192_p224_large_degree_isogenies_20261009/verification_poly.rs
1320cf930ee75475c285e7da88358db009513f862ef2c83708de8a01b5ac0445  tools/isogeny-cli/tests/compact_cm_cli.rs
3016825aa3213f733767298886c545157b1168bf9c3e17d46602883ce7251898  tools/isogeny-cli/tests/replay_trace_cli.rs
```

## Machine-readable attestation

Extract this fenced YAML into the Coordinator-owned attestation file for the repository checker. Each exact assigned joint has an allowed verdict enum. No checker composition or test command was executed in this retake.

```yaml
review_attestation:
  task_id: TASK-20261016-ed10a6
  archived_by: TASK-20261016-9b1e68
  native_agent_identity: /root/frontier_coordinator_resume/cm_norm_independent_review
  native_agent_session_id: unknown_not_exposed
  review_kind: independent_resource_and_trace_source_retake
  source_commit: e82d80feaf82d3730576ccd9137911b336f9dab8
  plan_commit: 7e8d8bcf0e
  joints_owned:
    - resource_monitoring_and_ack
    - negative_resource_control_coverage
    - trace_scope_and_unchanged_acceptance
  verdicts:
    resource_monitoring_and_ack: holds
    negative_resource_control_coverage: holds
    trace_scope_and_unchanged_acceptance: holds
  verdict_scope:
    resource_monitoring_and_ack: Static normal-public compact construct/verify and challenge judge paths; documented sampled envelope and grace, not every internal invocation.
    negative_resource_control_coverage: Source definitions cover None/zero before/after acknowledgement and positive release/progress; execution and cross-platform validation unverified.
    trace_scope_and_unchanged_acceptance: Static observer, trace error/interruption, unchanged arithmetic-predicate and separate-public-admission reasoning; no runtime or timing claim.
  sources_read:
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/final-source-e82d80feaf/review-plan.yaml
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/final-source-e82d80feaf/source-files.sha256
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/compact-m8191-draft/implementation-review-9a2e133099/coordinator-addendum.md
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/replay-profile-50341/HANDOFF.md
    - /private/tmp/isou-cm-source-review-9a2-final.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/supervisor.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/replay.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/replay_trace.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/main.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/build.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/challenge.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/research/p192_p224_large_degree_isogenies_20261009/verification_kernel.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/tests/replay_trace_cli.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/tests/compact_cm_cli.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/tests/challenge_cli.rs
  sources_read_scope:
    plan: Working-tree plan and exact 7e8d8bcf0e plan read before source.
    frozen_manifest: All thirteen exact file hashes matched; hash comparison does not imply re-reading every unchanged file.
    supervisor: Diff and relevant production loop plus full new control definition.
    trace: Full replay_trace source, replay body and diff, generated dispatch source, observer additions, and full public replay_trace test definition.
    challenge: Pinned e82 preflight, document validation, worker, judge, and handshake/option excerpts.
    compact: Byte-identical files and prior same-reviewer analysis reused; no new independent mathematical proof.
    unchanged_support: Pinned diff checks for field, polynomial, rational-map, compact, and challenge source.
    test_searches: Only committed source/test definitions searched; compact and challenge tests included in the bounded symbol search.
    prior_review: Same native reviewer's prior 9a report and same-session source knowledge explicitly reused.
    permitted_handoff: Frozen implementation instructions only; no linked run or raw evidence path opened.
  source_provenance:
    source_and_plan: internal
    verified_by: /root/frontier_coordinator_resume/cm_norm_independent_review
  read_sibling_reports: false
  blind_from_respected: true
  own_prior_review_used: TASK-20261016-3d848c
  coordinator_addendum_used: post_acknowledgement_zero_rss_correction
  new_independent_mathematical_proof_claimed: false
  new_raw_control_payloads_read: false
  new_pass_summaries_read: false
  clean_build_or_custody_receipts_read: false
  live_target_outputs_read: false
  requested_policy: review-adversarial
  requested_effort: xhigh
  actual_served_model: unknown_not_exposed
  actual_served_effort: unknown_not_exposed
  provider_or_api_substitution_used: false
  test_binary_benchmark_or_target_execution: false
  repository_modified: false
  artifacts_uploaded_or_transferred: false
  actionable_source_findings: []
  recommendation: Archive this static retake; reviewed source gaps are repaired, with clean execution and all scientific/custody gates still separate.
  core_trace_completed_implies_public_admission: false
  scientific_execution_approval: none
  custody_gate_change: none
  official_state_transition: none
```
