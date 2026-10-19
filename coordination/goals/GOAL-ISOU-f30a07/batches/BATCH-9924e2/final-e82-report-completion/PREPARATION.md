# Prepared additive report-only continuation

Status: unpublished Coordinator preparation. Publish only after primary RUN-ISOU-93b2b3 is terminal, its producer has completed the original run/observation/raw archive package, and T3233 plus the scientific goal-lanes ownership are released. Do not start an HA wrapper or edit any HA record during that ownership. This is report completion and archival, not a new scientific attempt, promotion, or change to DEC-20261016-34a9e9.

## Confirmed scope gap

The frozen final-e82 dispatch card TASK-20261016-d481d6 authorizes only EXP-ISOU-32a530/runs and its execution/TASK-20261016-d481d6 directory. Its eight source artifact paths comprise six canonical run companions, observation.md and native-evidence.tar.gz. No canonical reports path is present. The original epoch1 claim, trial plan, scientific argv, budget, source hashes, input map and all original file bytes stay intact. Canonical reporting is performed by a fresh postprocessing producer, not by retroactively enlarging that trial's claimed work.

## Publication package after terminal release

Reserve exclusive metadata paths for a new additive report amendment, its derived continuation queue and the two pending snapshot receipts; reserve the primary report directory exclusively for the report producer. Use a new bounded Conductor task for report production. Do not re-claim or redispatch the completed scientific operation.

Create an append-only directory beside final-e82, for example `final-e82-report-completion/`, containing this amendment, a provenance binding of the exact original final-e82 dispatch queue bytes/commit, the derived continuation queue, and a source/report index. Commit/push it to the existing HA branch/PR before report production. Freeze a fresh report task ID at publication; no ID or approval has been written by this temporary preparation.

The derived queue copies original cards without modifying original artifact files. Add a report-only producer R_primary, with:

- role executor, executor-mechanical inference, maximum scientific runs0, maximum workers1, bounded ordinary report tooling; estimate wall900s and memory2GiB. Report/diagram/PDF rendering is postprocessing, not a mathematical run.
- dependency TASK-20261016-d481d6 terminal delivery (regardless of mathematical verdict), review_required false: the report restates archived observations and introduces no research claim.
- read scope exactly the primary run root, original execution directory, frozen protocol/bindings, and the amendment.
- exclusive write scope `experiments/EXP-ISOU-32a530/reports/run-20261016T0912Z`.
- four exact deliverables/artifact paths: `report.md`, `flow.svg`, `report.typ`, `report.pdf` inside that directory.
- handoff.archived_by TASK-20261016-9f5b51. No handoff.execution scientific launcher and no new RUN/EXP.
- completion gate: actual terminal source bindings, all raw failures/censors retained, one-page report/PDF where practical, render and visually inspect every PDF page, diagram/text/PDF reconcile, no new mathematical or performance promotion. Tooling/render failures are retained in a report build appendix inside report.md or an explicitly added declared report-build artifact before work, never hidden or overwritten.

In the **derived queue only**, amend pending archive TASK-20261016-9f5b51 to directly depend on both TASK-20261016-d481d6 and R_primary; its source_task_ids contain both. Existing broad experiment read scope covers the reports. Every other existing dependency is preserved. The archive receipt remains at its declared original receipt path. Its content_at_commit binding must hash the eight original producer files, the four report files, and its own receipt, exactly the union computed by tools/research_dispatch.py. Every original source hash must match the producer's sealed package; missing/failed report output does not authorize pretending completeness. The source card remains archived exactly once. This is the existing supported multi-source archive contract, not a checker exception or a rewrite of the original sealed input queue.

The compact executor TASK-20261016-145d29 still depends on TASK-20261016-9f5b51. Thus the order is primary raw delivery -> report-only completion -> primary snapshot -> compact construct and dependent verify. No science is inserted, repeated, or moved ahead of the primary snapshot. Publish the derived queue path/hash as the selected continuation before root claims any successor. Do not change the epoch1 claim's queue hash retroactively.

## Required primary report content

Report exact terminal native entry/verdict and resource reason; phase table distinguishes completed, active-at-terminal and unavailable stages. Include sealed map/binary/source hashes and measurement provenance. Report actual OS CPU only if a terminal receipt exists; otherwise null. Do not infer total CPU or a speed ratio from ps samples or the historical timeout. Trace core COMPLETED and public mathematical admission are separate fields. Diagram the recorded verification flow and highlight the terminal observation accurately. Cite the original run companions, observation and raw native archive paths/hashes. This report may describe stage wall costs, with nesting and shared-host limitations, only after those bytes are terminal and sealed. No currently live stage message is source evidence.

## Compact reporting: one report per EXP/session from the first trial start

The existing compact scientific card likewise lacks a reports scope. It must produce only its already authorized run/execution files. Do not enlarge its live claim. After the compact producer is terminal and released, create a fresh report-only producer R_compact and corresponding additive queue binding before any canonical compact report write. R_compact has maximum scientific runs0 and the same postprocessing constraints. The run/research-visuals contract requires one report per EXP per session, covering every run directory written for that EXP; its directory timestamp is the first trial start. Derive one exact canonical directory from the retained constructor first-start UTC receipt; never invent starts:

- construct RUN-ISOU-bdbf5d -> `experiments/EXP-ISOU-feb102/reports/run-<actual construct YYYYMMDDTHHMMZ>`.
- verify RUN-ISOU-2b2372 is covered in that same report together with construction, even if verification starts in another minute. Include both run IDs, every run directory written for EXP-ISOU-feb102 in the session, and both phases' actual receipts. A later verification start does not create a second report directory.
- if verify never started, no verify timestamp/directory is invented; the construct report states NOT_STARTED with the exact dependency reason and original nonstart record.
- if construct itself never started, bind one canonical nonstart report path by an explicit Coordinator report-time amendment, labelled report-generation time, never experimental first-start time.

One R_compact owns that single resulting report directory with report.md/flow.svg/report.typ/report.pdf; list exact paths only when the first-start timestamp or explicit nonstart report-time amendment is bound. Add it as source and direct dependency of the still-pending TASK-20261016-19d9a7 snapshot in that later derived queue. Keep original compact scientific producer as its other source. Hash all14 original compact source artifacts, the four report files and snapshot receipt:19 paths total. No raw manifest/claim/trial rewrite. The later validator/decision/archive dependencies retain the compact snapshot gate.

## Checks before publishing and archiving

Use only actual existing multi-source archive semantics: validate the derived queue and its ready-only frontier; original frozen queue remains hash-equal. Compare every unchanged original scientific card's scientific handoff/trial binding and argv/resources with the frozen queue. Use supported goal-lanes claims for new report and snapshot tasks only. Archive via content_at_commit, verify expected file hashes from Git, update existing PR, and release every metadata/report Conductor task before root starts its next scientific wrapper. No live unbound metadata claims may be adopted by that wrapper. Report the exact published queue and Git/archive receipt hashes back to root.

Record unchanged base ledger issues separately if still present; never grow a baseline or weaken the checker to accommodate this amendment. A temporary plan is not permission to write reports yet: terminal release, publication and exclusive report scope must happen first.
