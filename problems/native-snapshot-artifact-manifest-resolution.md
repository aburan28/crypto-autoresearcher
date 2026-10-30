# Native snapshot verifier does not resolve repository artifact manifests

- **Status:** open
- **Kind:** implementation gap in archival metadata integration
- **Affected work:** [EXP-PFIVE-e26798](../experiments/EXP-PFIVE-e26798/protocol.json), raw snapshot TASK-20261029-d2ad88 in [BATCH-449a28](../coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-449a28/dispatch_queue.json)
- **Next action owner:** Coordinator; implementation task not yet assigned
- **Last updated:** 2026-10-29

## Problem

The native Git snapshot verifier cannot certify a declared run artifact stored through `.artifacts.json`, although repository policy requires that storage format for large data. This blocks completion of the native snapshot/review dependency chain when a run emits policy-selected data. It does not invalidate independently checked mathematical output or prevent publishing the bytes and their hash manifest.

The native supervisor first seals a receipt naming the physical `.gz` path and both stored/content hashes. The newer repository publisher moves those bytes to S3 and commits `.artifacts.json` plus `.gitignore`, retaining the hydrated `.gz` locally. `GitRepositoryVerifier._stored_path` recognizes only a direct Git blob or the legacy `.gz`, `.blob.json`, and `.gz.blob.json` forms. Its `content_at_commit` check rejects a logical path whose bytes are represented only by the new manifest.

## Evidence and uncertainty

- **Observed:** read-only inspection at source commit56d1907ed04b of [research_dispatch.py](../tools/research_dispatch.py), particularly `_stored_path`, `_verify_content_only` and `verify_archive`, finds no `.artifacts.json` resolution. `content_at_commit` uses `allow_generated_skip=False` and requires every declared source/archive artifact.
- **Observed:** [artifact publisher](../tools/artifacts/artifacts.py) explicitly retains hydrated bytes, stages the manifest/ignore files, and removes published payloads from the Git index. Its directory mode enumerates tracked files; new outputs must be passed as explicit file paths.
- **Derived:** retaining hydrated receipt-bound files can preserve native execution coverage after publication, but cannot supply a missing Git blob to snapshot verification. Adding a legacy pointer beside the hydrated gzip makes the old logical resolver ambiguous. Modifying a sealed execution receipt would violate immutable custody.
- **Missing capability:** manifest-aware native archive verification, including unambiguous physical/logical resolution and exact hash binding at the declared archive commit.
- **What this does not establish:** no mathematical obstruction, failed cryptanalysis hypothesis, lost raw data, or blanket inability to publish. Actual S3 publication/readback must be recorded separately; code inspection is not a storage upload.

## What would unblock it

- [ ] Native verification recognizes a committed `.artifacts.json` entry at the declared archive commit and binds its exact stored-byte digest to the unchanged run receipt, with no fallback to untrusted working-tree metadata.
- [ ] Integrity regressions reject wrong hashes, absent manifest entries, duplicate stored forms, path traversal and changed archive manifests; valid legacy forms continue to pass.
- [ ] A completed native run is published through the normal artifact tool, retrieved with matching hashes, and its declared snapshot verifies without changing any sealed scientific output or receipt.

These conditions establish transport/custody compatibility only. Independent scientific review and hypothesis decisions remain separate.

## Next discriminating step

- **Action:** build a small temporary Git/S3-compatible-store regression fixture spanning native sealing, manifest publication and `content_at_commit` verification. Preserve the pre-fix refusal before testing a scoped implementation.
- **Inputs and controls:** one direct JSON, one gzip subject to the64KiB data policy, one legacy pointer, one missing object and deliberate hash/path corruptions. No elliptic-curve producer is needed.
- **Limits and stopping:** finite software integrity fixtures only; stop on ambiguous resolution or a mismatch. No scientific rerun is authorized by this problem record.
- **Outcomes:** a successful integration check permits a fresh native archival reconciliation; a failure keeps the exact custody gap open. In either case retain existing receipt bytes and storage manifests.
- **Recheck trigger:** a manifest-aware native archive implementation and its checked regression evidence.

## Resolution and history

2026-10-29: identified during publication planning for the five prime-field leads. Publish retained outputs normally and record a transport receipt; do not mark the native producer snapshot complete merely because the manifest was committed. The older interrupted trial has a separate missing native archival-ID binding and remains explicitly incomplete. Unresolved.
