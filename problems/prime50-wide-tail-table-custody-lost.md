# Prime50 packed-tail full table is absent from its pinned local path

- **Status:** `open`
- **Kind:** artifact custody and infrastructure loss; cause unknown
- **Affected work:** [prime50 packed-tail engineering report](../research/icperf_prime50_packed_tails_20261017/report.md), [source snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-eb1158/archives/TASK-20261017-acf159/snapshot-receipt.json), and the [full-width IC arity grid](full-width-ic-arity-grid-unmeasured.md)
- **Next action owner:** Coordinator for a frozen restore-or-rebuild handoff; executor for the bounded rebuild and independent checker
- **Last updated:** 2026-10-17

## Problem

The 104,294,212-entry B=132, h=4 prime50 packed-tail table cannot be used for the planned wide decomposition scan because its pinned local scratch directory is absent. The construction and sampled validation remain archived, but the full 1,668,707,392-byte payload was never committed or copied to durable custody. The cause and timing of its disappearance are unknown.

The exact public curve and target-blind small-x base are fixed in the [input manifest](../research/icperf_prime50_packed_tails_20261017/input-manifest.json). This loss blocks reuse of that table for prime50 m=8 scans. It says nothing about factor-base quality, algebraic solvability, or the other curve families.

## Evidence and uncertainty

- **Observed:** The producer and independent checker recorded a full-table SHA-256 of `fa868fc324731c9bea98b7b49a177713593d158f3135cdae344b182857828b02` and 4,608 scalar replays; see the [validation record](../research/icperf_prime50_packed_tails_20261017/validation.json) and [report](../research/icperf_prime50_packed_tails_20261017/report.md). The [receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-eb1158/archives/TASK-20261017-acf159/snapshot-receipt.json) explicitly marked the full table `local_only` under `/Volumes/SSD990-2/crypto/.scratch/icperf_prime50_m8_20261017/full/`. A read-only `ls -ld` check at 2026-10-17 17:40 UTC returned `No such file or directory` for both that path and its `/Volumes/SSD990-2/crypto/.scratch` parent; the volume had 519 GiB free. A second independent agent observed the same `ENOENT`. These checks did not search every other volume or backup.
- **Derived or proved:** The archived digest, chunk hashes, source, small table and sampled replay receipts do not reconstruct the missing full payload. Restoring an arbitrary file that merely has the same name would not satisfy the committed digest.
- **Suspected explanation:** Scratch cleanup, external workspace maintenance, relocation, or another filesystem action; none has been verified. A targeted read-only search and filesystem/audit history could distinguish relocation from deletion.
- **Missing capability:** The exact full payload under durable, independently hash-checked custody, or an admitted rebuild of the same frozen input and code with a separately archived output.
- **What this evidence does not establish:** It does not invalidate the historical run/checker observations, prove a code fault, refute the index-calculus approach, or supply any complete-cost comparison.

## What would unblock it

- [ ] Locate a retained payload and verify its byte count is 1,668,707,392 and SHA-256 equals `fa868fc324731c9bea98b7b49a177713593d158f3135cdae344b182857828b02`; or run a new frozen, bounded reconstruction from the same input/source with full ordering/bounds and seeded scalar replay controls.
- [ ] Record a durable path and content hash, owner, retention rule, and independent readback from that custody location before any scan consumes the table. Preserve the original source/run receipts unchanged.

Meeting these conditions would restore a usable table for the specified prime50 control base only. The wide scan, certified relations, useful rank, linear algebra, target work, matched rho, and equal-size elite-base comparisons would remain unmeasured.

## Next discriminating step

- **Action or proof obligation:** Search likely local artifact and backup locations read-only for a payload with the exact byte count and digest. If absent, freeze a new rebuild-and-custody handoff before running the builder again.
- **Inputs and controls:** The committed input manifest, Numba producer source, table digest and chunk digests, 4,608 sampled cases, independent scalar checker, and altered-file negative control.
- **Execution limits and stop condition:** A search is read-only. A rebuild uses a new Coordinator-approved task with explicit memory, scratch, wall and retention limits; do not treat the prior 982.639-second observation as a new run or silently reuse its receipt.
- **Outcomes and next actions:** A matching restored file moves to independent readback and a new custody receipt; a bounded search with no match records absence within searched locations and triggers the rebuild; a mismatched file is rejected; an infrastructure failure remains an infrastructure outcome.
- **Recheck trigger:** A matching payload appears or the new rebuild/custody task completes.

A planned step is not a completed experiment. Apply the existing execution, review, budget and archival rules before acting on it.

## Resolution and history

2026-10-17: Opened after the pinned scratch parent and full table path returned `ENOENT` on two read-only checks. The earlier report and snapshot receipt accurately disclosed local-only custody at archive time; this later absence is a new observation. Unresolved. Completing this record or merging its PR does not establish a research result.

2026-10-17: A read-only `find` over `/Volumes/SSD990-2/crypto`, `/Volumes/SSD990-2/cryptanalysis`, and `/Volumes/SSD990/crypto`, limited to depth eight and files of exactly 1,668,707,392 bytes, exited zero with no matching path. An earlier name search through depth five in those roots also returned no `*prime50*` or `*packed*tail*` file. These bounded searches do not cover deeper paths, other volumes, backups, compressed or renamed files of different length, or paths hidden by suppressed permission errors. The next step remains a broader authorized restore search or a frozen rebuild with durable custody; no disappearance mechanism has been established.
