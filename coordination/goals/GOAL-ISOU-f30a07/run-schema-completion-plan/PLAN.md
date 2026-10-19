# Additive schema completion plan for three native observation receipts

GOAL-ISOU-f30a07. Conductor T3218, postprocessing/design only. No algorithm, checker, registry or run file is changed by this plan. Native instrumentation TASK-20261016-659e0a remains authorized independently.

## Established scope

The old fully-materialized log is immutable at commit7c6f4159f28871acf7fe84edbe7ff507cf03b2f2; its315 error strings are all present verbatim in the current318-error log, with zero removed and exactly three added. All163 distinct paths named by those315 errors have identical Git blobs in original main base7b1428c2fac72440930abf8d3bf626f3488ffabc and currentHEAD. tools/validate_ledger.py and tools/run_supersession_registry.yaml are also byte-identical to that main base. immutable-base-comparison.json records every blob and both tool hashes. This is an exact retained-log/blob comparison, not a fresh execution of the old base.

The three added errors are expected-top-level-run for RUN-ISOU-ea3515, RUN-ISOU-13a6b5 and RUN-ISOU-f9546d. Their manifest.yaml files contain raw receipt_kind:native_command_observation metadata and no run identity. Original run bytes and existing content_at_commit snapshots must remain unchanged. No baseline entry may be added to absorb these errors.

## Existing supported mechanism

validate_ledger.py check_run supports an exact-path registry entry routing a raw manifest to a separate complete canonical record. check_run_supersessions audits both original and replacement whole-file SHA256 and their bound identities; it does not skip run checks. The original raw manifests have missing identity fields. Existing _run_id_of treats absent identity as null and only its registry-opted _null_id_superseded_run_id recovers identity using the exact hash, original path, run-directory basename and nonempty provenance. Three read-only probes against original bytes returned the intended run IDs; ordinary unregistered parsing returned null. The evidence is in immutable-base-comparison.json. No parser change or new ignored-run exception is needed.

A future entry must explicitly use superseded_id_null:true and explain the original field is ABSENT, rather than falsely claiming the raw file serialized id:null. Identity provenance must cite frozen trial-plan run IDs, archived run-directory ownership and exact adapter digest. This uses existing semantics; replacement identity remains mandatory. Do not use malformed-YAML extraction, because these originals parse normally.

## Proposed additive files and exclusive scope

For each of the three existing run directories add only previously absent canonical-run.v2.yaml, command.txt, environment.json, stdout.log and stderr.log. Preserve manifest.yaml, raw-result.json and every native subdirectory byte. Add exactly three entries to tools/run_supersession_registry.yaml, each with both whole-file hashes, same run ID, registered date, additive_schema_completion kind, precise defect and provenance. Reserve those exact new files, the registry and a fresh postprocessing archive receipt before implementation. Canonical records may instead be stored outside run directories; companions are still required by check_run in the original discovered directory. Confirm no whole-directory seal enumerates an immutable expected-file set before adding companions; if one exists, stop and document that conflict rather than modifying its seal. Current snapshots bind selected artifacts and native tar bytes, not a newly asserted whole-directory identity.

## Canonical record contract

Required top-level run fields are id, experiment_id, status, code, environment, inputs, timing and result. Use current existing checker fields; do not modify the schema. Each record names its raw manifest and SHA in supersedes/composition sources, identifies this as retrospective schema completion only, and lists exact source paths for every value.

- RUN-ea3515: terminal failed native control exit101. Preserve successful component checks separately from failed final leaderboard assertion. No admitted overall control result.
- RUN-13a6b5: terminal completed observation, native suite exit0. This is an instrument-control run with hypothesis_id:null and certificate.kind:none; it asserts no50341 validity.
- RUN-f9546d: terminal failed observation with explicit native CENSORED/TIMEOUT, score:null and incomplete independent verification. Preserve outer raw-result INCOMPLETE/nativeexit3 and native RESULT/judgement receipts simultaneously. Do not normalize this to an accepted result.

code.commit must be the recorded executable implementation source6547d252889ac0e1089a0497bf80f05b884ab24e, alongside exact binary SHA8e0ab524008d41098a816d117d563bbefa456959bb790a78e41efc41b05e6cc1. Separately bind frozen shell adapter hash and execution checkout/source receipt; do not replace execution provenance with an archival commit. command.txt copies exact frozen argv and absolute retry roots for13a6b5/f9546d; preserve ea3515 original relative argv. No command is executed. Record any unobserved dirty state as unknown with its limitation; do not assert clean from today's checkout.

environment.json is explicitly retrospective: copy only recorded host/runtime/resource fields from committed receipts, mark unrecorded fields null/unknown, and identify each source. Do not probe today's machine and label it the execution environment. stdout.log/stderr.log are byte-identical copies of existing native.stdout.log/native.stderr.log, with source/hash and derivation note. They are companion schema copies, not new captured streams. Existing raw-result.json remains untouched. Timing distinguishes native constructor131134ms, censored replay3600019ms, coarse wrapper timestamps and unavailable total CPU; no fresh estimate fills missing data. result.certificate.kind:none, scientific_promotion:false; a map lacking completed replay does not become a verified isogeny certificate through this migration.

## Validation and archive gate

Before and after materialization, hash every original file and confirm prior native tar plus archived selected-path bindings. Run existing targeted supersession tests, checker identity audit, merge hygiene and full ledger validation. Require exactly the earlier315 error strings, no new record/run/registry error, with the three raw-shape errors removed by valid canonical replacements. A bad replacement, missing companion, altered original, mismatched ID or hash must still fail the existing checker. Do not claim the whole repository green while315 remain.

Commit source records/companions as a separate metadata-only snapshot, then append registry entries and their exact hashes in a binding commit; publish on PR2221 with corrected scope. Preserve failure and timeout observations. No scientific retry, timing improvement, claim promotion or custody-transfer authorization follows from this migration. Parent can delegate implementation of this plan as a genuinely new postprocessing operation; T3150 remains exhausted and untouched.
