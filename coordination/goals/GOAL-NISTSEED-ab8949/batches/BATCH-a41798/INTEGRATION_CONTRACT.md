# BATCH-a41798: additive ECPP integration contract

Status: prospective source-only engineering contract. Scientific runs: zero. This contract grants no scientific approval, VM execution, original-program execution, storage operation, mathematical evaluation or official scientific transition.

Owner decision: DEC-20261027-ebc794. Producer: TASK-20261027-275b12. Producer snapshot: TASK-20261027-2ce9dc. Independent engineering validation: TASK-20261027-344233. Validation snapshot: TASK-20261027-5d6999. Administrative design archive: TASK-20261027-67715c.

## Purpose and unchanged objective

Complete the remaining integration around the archived V9 one-index runner/checker and the existing public101 A/A producer so a later Coordinator can specify and assess the full 21-order packet. Pursue exhaustively the commonality behind the eleven reconstructed omissions, retaining the complete candidate universe, public seed/draft provenance, field-matched published controls and every negative, failed, censored or inconclusive observation. Goal completion still requires a committed independently reviewed historically sourced procedure accounting for omissions and controls, or a prospectively frozen independently validated predictive property on its declared holdout domain. Tooling, compatibility controls, an approved packet or a 21-order ECPP split alone satisfies neither criterion. Alternative mechanisms, unvisited/censored domains and provenance uncertainty remain explicit.

T-5464 is the distinct accepted post-A/A integration phase. T-5065 remains terminal at its original cap. T-5370 remains separate. No earlier attempt or cap is reset.

## Bound inputs and literature review

Use all 23 exact inputs at source commit 4c7298e5212f523642c782483cd28f4bd5000d66 in coordination/goals/GOAL-NISTSEED-ab8949/integration-admission-20261027/source-inputs.json. The Coordinator independently read and rehashed those local bytes and found all matches. Parent-supplied publication is d08f94dc75715cf0902419c0fe19b538ff278ef4. Verify Git publication again before dispatch; this contract does not fabricate it.

Additional source pins at that source tree:

- research/nist_seed_ecpp_compat_20261024/qemu_controls.py: 255b415ebf5a8eaa5514a02fbd0fb9886f27a2065f8686586a2c336e9f9372e7
- research/nist_seed_ecpp_compat_20261024/qemu_init.c: 1c5a2a11ecabf081a61fdf79f04ae343ea0348dbf7fa08d5ad1be738ca5e56e0
- research/nist_seed_ecpp_compat_20261024/guest_framing.py: ce4f7a8b320826c09d9b947d306883d83b695b83ebfc496ec1d3e38ca6a76bf5
- research/nist_seed_ecpp_compat_20261024/certificate_admission.py: 6cf50c95da246c7033dbb2cda8f8d70c07e2d5e366c1f1c9f163e7b115740c68
- experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_schema.json: c8f4f81ef3a092b3ea9360d568802b0b7e346245d02cae7e4f7a01e4af3d3087
- agents/executor.md: 89eda99ea575b966c5780762d2d13810fd6ed5abe1a5dc76a57ed51680784cc7
- agents/validator.md: 33947db8c7cc8663ac79f1eff4b183e75d0546915feb23e77654cd03a249c9d2
- orchestration/model-policies.yaml: a5a86d0e2be07f3c4e0ee67cfacad1cf667228046e832f24fb4e480ec0dc7a92
- tools/research_dispatch.py: 5919013342391e9b9ec30811c0f4c458e78030915c1afd8b799340b14fadb437

These additional hashes were computed by the author from read-only bytes. The operator verifies their committed publication before dispatch. A mismatch is a source-binding refusal, never permission to silently update expected hashes.

The author read research/nist_seed_ecpp_source_20261024/report.md, the frozen cohort draft, V9 sources, completed A/A source/report, current capsule helpers, the supplied problem records and exact runtime/cohort bindings (provenance internal; verified_by TASK-20261027-0ccc98 Coordinator). The acquired-source report's current-mirror and historical-byte/caller limitations remain binding. No archive or thesis was reacquired here.

Primary implementation references retrieved and read by that Coordinator:

- [Python try statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement): recovery needs its own exception guard.
- [Python stdout redirection](https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stdout): Python stream redirection changes global state and does not capture subprocess output.
- [Python tar members](https://docs.python.org/3/library/tarfile.html#tarfile.TarInfo): enumerate regular members and inspect without extraction.

No knowledge-retrieval MCP tool was available. No corpus-wide novelty or absence claim is made. This is implementation design using the acquired exact sources, rather than a new mathematical search.

## Immutable inputs and write ownership

All existing files under implementation/, aa-admission/, compatibility research, runtime payloads and existing integration helpers are read-only. Add all producer code, schemas, tests, reports and engineering diagrams under experiments/EXP-NISTSEED-6886da/integration/tasks/TASK-20261027-275b12/. Do not duplicate the A/A producer, rewrite the V9 runner/checker, change global configuration, repair another agent's edits or change a scientific record. You are not alone in the codebase.

The frozen cohort is exactly the existing cohort-inputs.json byte sequence, SHA-256 93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545. Preserve its ordered 21 full UIDs and complete row identity, 11 omitted and 10 published. Never derive identity from field size, filter failed rows, relabel P-224 representatives as extra seed decisions, or replace the candidate universe with a reduced set.

Preserve exact original Data inventory, factor parameters, runtime/kernel/program/input bindings, fresh process RNG, full proving and N-1/N+1 routes, disabled distributed/debug modes and exact guest argv. Prover argv is /program -l /ecpp/ -f /input -Fc -C /tmp/certificate. Checker argv is /program -f /input. Preserve all existing limits. No source or binary instrumentation is authorized.

## Required additive architecture

Provide integrated_runner.py, integrated_checker.py, integration_schema.json and test_integration.py in the owned task directory. Imports of the new modules must not import the compatibility execution library, launch a process, construct a VM or perform storage activity. Actual legacy execution remains a deferred explicit boundary reserved for a later approved packet. This engineering task must always inject a whole-boundary fake before any execution-capable route is reached.

The wrapper may call the source-bound V9 run_trial library through that injected seam; it must not invoke V9 main. Keep the V9 successful artifacts byte-for-byte intact. For V9 exceptions escaping before emission, add an independently schema-identified integration failure envelope and recovery record. Never overwrite or invent a V9 raw-result.json, observation.json or success record to make the old checker pass.

The integrated checker must not import integrated_runner, trust its classification, or use a producer-computed digest as its expected source identity. Reuse frozen checker pure validation components where appropriate, but independently derive integration custody, framing, counters and supplemental tokens. Calling V9 check is permitted only for its applicable intact path and does not replace additional integration obligations. The malformed-custody path must not call V9's strict success parser as a prerequisite to retaining the observation.

## Quiet supervisor and raw capture

The original five supervisor files remain owned by the supervisor. Never modify, append to or truncate them. V9 verify_supervisor requires exactly those five files before entry. Therefore driver capture handles must initially point to a distinct fresh wrapper-owned capture directory outside that five-file trial directory. The future trial plan must declare both paths. Validate distinctness, ownership, ancestors and symlink safety before opening captures.

Capture driver stdout/stderr without printing JSON or a traceback to supervisor stdout/stderr. Flush and close captures after the boundary finishes or raises, then place the exact bytes at driver.stdout.log and driver.stderr.log in the trial directory only after V9 preflight/use has ended. The wrapper must remain quiet through finalization. If an OS-level capture is used, restore descriptors reliably; if Python redirection is used, retain the existing subprocess capture explicitly and document its scope. No concurrency or background writes are allowed. Rehash the five supervisor files after finalization and require equality with their pre-bound identities. A mock end-to-end CLI test must inspect the actual outer stdout/stderr bytes after process exit.

Keep the finalization order explicit: close all child and driver captures; preserve any original V9 envelopes; independently generate supplemental trace if raw serial exists; create the existing deterministic raw capsule and inventory; write the new integration envelope binding all declared outer sidecars and capsule/inventory bytes. Do not create recursive self-hashes. Excluded runtime-cache bytes remain reconstructible only through separately verified frozen kernel/payload/catalog and image identities. Never silently omit partial raw captures or unexpected regular files in the driver-owned tree.

Reuse integration/capsule.py and capsule_check.py. The integrated checker independently checks exact live membership, file sizes/digests, capsule bytes and inventory, member path safety, duplicates, regular-file types and driver inventory consistency. It must reject changed, missing, extra, symlinked, traversing or inconsistently indexed artifacts. It must not extract an unchecked archive. If capsule construction fails, preserve captures and an explicit incomplete-finalization record; do not claim custody-valid or scientific admission.

The existing raw capsule does not contain every outer integration sidecar. The new integration envelope must separately bind the original V9 outer envelopes when present, copied/external binding identity, driver captures, capsule and inventory, supplemental trace, counter evidence and failure/recovery sidecars. Name exactly which digest covers each artifact.

## Malformed framing: recovery and independent checking

Handle absent, truncated, duplicate, misordered and malformed guest or certificate sentinels independently in the runner recovery path and checker. Each secondary read, JSON parse, status recovery, framing parse and trace derivation has its own bounded guard so the original and recovery errors remain distinguishable. A second parser exception must not erase already captured raw bytes or prevent an integration failure record when the output filesystem is writable.

Censored malformed output can be accepted only as an integrity-checked retained observation: custody_valid true, scientific_admission false, classification INDETERMINATE, explicit framing state and raw offsets/digests. Static source/runtime/cohort/prior-corpus/binding/supervisor identity and exact inventory checks still apply before this decision. Missing or corrupted identity/custody is a checker refusal, not an accepted censored record. Missing status is recorded as unavailable; do not fabricate elapsed time, status, body, certificate count or a well-formed substitute stream.

Do not label an unparseable fragment a complete program body or certificate. Retain raw bytes and distinguish strict-frame-derived fields from optional partial-token observations. Labels and supplemental traces remain descriptive printed-token observations, with unprinted state UNOBSERVED.

Successful admission retains every V9 static, prior-mapping, trace, root/grammar/step-count and raw checker-body check. Additionally, independently require both prover and checker complete framing, qemu_exit 33, child_exit zero, no watchdog reason, exact sentinel counts/order, expected ABI, exact input/program/init/configuration and certificate custody. Require exactly one prime label and one root-bound certificate. In particular, never trust an injected vm_valid=True to compensate for a malformed checker frame. A malformed successful-looking record must fail scientific admission even when its custody is valid.

## Counter semantics

Keep the frozen V9 named_orders_executed literal unchanged and label it legacy_selected_work_field. Do not sum it as actual program starts. Introduce integration accounting with each value tied to evidence path, digest and where relevant byte offset, stage and evidence kind. Synthetic fixture evidence is explicitly synthetic and never contributes to real execution totals.

Separate these quantities:

1. selected_cohort_indices: the single requested frozen index after identity validation; selected work is not execution.
2. boundary_calls_attempted: increment immediately before the deferred whole-boundary call; distinguish injected fake calls from real calls.
3. prover/checker_launch_intent: hash-validated started.json records. qemu_controls.vm writes these before subprocess.run.
4. prover/checker_guest_init_observed: exact retained ABI/begin evidence. qemu_init.c prints guest begin before fork and execv, so this is not original-program entry.
5. prover/checker_program_output_observed: only a source-backed original-program output signature in raw serial can provide a positive observation. Retain its source rule and raw location. Do not infer it from generic sentinels, nonempty serial or planned work.
6. prover/checker_stage_completed: strict complete frame plus reconciled primitive status; report successful and failed child exits separately.
7. certificate_admitted: all independent successful-admission requirements passed.

If successful exec or program entry has no discriminating retained event, its exact count is unknown. Report an observed lower bound with its evidence, plus unobserved/ambiguous count; never substitute zero or one for an unknown actual-start count. A partial token may establish activity without establishing completion. Preserve all distinctions in the schema and aggregate flow. The current task's real VM/program/cohort execution totals must be zero, while mock boundary-call counts remain separate.

## Existing A/A producer and supplemental trace

Reuse aa-admission/aa_fixture_producer.py, hash d481423ee4562c345d575f1dbd8f57a1dd5184e2c599c813a2f91154e790ef18, and its schema. The existing producer's default boundary is forbidden here. Inject a whole-boundary fake before build_pair, preserve separate validity checks before aa_compare, and bind the existing semantic/custody separation. No new producer, arbitrary-input path, out-of-range cohort index or cohort-derived A/A fixture is permitted. Actual future A/A execution requires the later scientific/control packet and its own declared raw custody.

Reuse printed_trace.py as a supplemental source-bound extractor. Retain offsets, raw bytes, repetitions, incomplete lines, unknown intervening text and arithmetic-shape flags. The checker independently regenerates it from retained serial. No unprinted attempt, hidden factorization or mathematical classification is inferred.

## Mock controls and completion gates

Use deterministic synthetic byte fixtures and temporary directories under task-local ownership. Globally guard process-launch, VM, original-program, scientific-library and storage seams during tests; only a local subprocess used to test the new quiet CLI with an explicit fake is permitted, and it must not execute any compatibility CLI. Report this local test process separately from legacy execution. No benchmark or mathematical measurement is requested.

The suite must exercise the actual additive driver-to-checker path, not merely helper calls. Retain distinct named results for: valid complete mocked admission; early exception with no child; launch-intent-only failure; guest-init-before-exec failure; exception after partial serial; malformed begin/exit/completion/ABI markers; duplicate and misordered markers; truncated certificate; identical invalid A/A controls; valid existing A/A comparator path; original-program output without completion; watchdog/nonzero child; malformed checker frame with success-looking rows; incorrect checker step/root; changed UID/order/label/index; frozen source/runtime/config/argv/input mismatch; copied binding or supervisor-log mutation; changed/missing/extra/symlinked raw member; capsule/inventory tampering; supplemental trace mutation; invented start count; reused/aliased output; and recovery-parser failure. Mutations must fail at the intended gate rather than an unrelated setup error. Preserve valid ordinary controls alongside every rejected case.

Deliver exact source pins and full UID/order preservation checks; strict integration schema validation; test commands, tool versions, stdout/stderr and actual pass/fail counts; real-boundary guard totals; every failed attempt and revision history; implementation limitations and remaining scientific admission work. The report may assert engineering observations only. Include an engineering custody diagram source, rendering and PDF; these explain artifact flow and grant no research claim. Check the existing canonical research graphs and record that this engineering work adds no mathematical or attack-cost edge.

After snapshot, the independent validator first derives framing/counter expectations from this contract and frozen qemu_controls.py/qemu_init.c before reading the producer's report or code. It then attacks the implementation with independent synthetic mutations. Review owns all engineering joints and changes no status. A break returns a precise additive correction requirement; do not overwrite the reviewed snapshot or expand scope silently.

## Storage, archival and later admission

No storage operation is authorized. The recorded canonical-store HeadObject 403 remains an access condition. Do not change credentials, profiles, buckets or invent upload manifests. Keep synthetic test artifacts within repository thresholds; if a required artifact exceeds policy and cannot lawfully be stored, report the exact obstruction rather than committing it. Future raw capsules require an actual authorized durable artifact-store route before launch.

Every producer artifact belongs to TASK-20261027-2ce9dc. Every independent engineering report belongs to TASK-20261027-5d6999. Archives run alone, stage exact declared paths, bind actual content and Git facts, and are pushed and reviewed under repository PR rules. No prospective receipt is a completed archive. The later full experiment still requires experiment.protocol/v1, all controls or justified exceptions, the variable ledger, sampling/analysis and checkpoint policies, experiment.export/v1, complete supervisor/trial archive coverage, independent replay/review, preapproval true, committed approval and ready-state confirmation.
