# Degree-five producer recovery: implementation design

Status: prospective design, not implemented or qualified. No frontier retry is authorized by this document alone; freeze its exact instrument and inputs after qualification.

The second bounded-export attempt was interrupted by node shutdown during degree-five production. See `runs/bounded-lift-terminal-002.json`. Stage-start receipts survive, but contain no matrix state. The current general job tool has no on-demand placement selector. The resumable tool accepts only native ecbench specifications on c8a.2xlarge, not an arbitrary Semaev producer. Do not mislabel this computation as an ecbench workload to pass that interface.

## Required resumable state

Implement a separate producer, preserving the qualified bounded-export source unchanged. Reconstruct the deterministic provisional monomial map from the immutable seed, then restore the relation matrix and loop position. A completed seed-phase chunk checkpoint must include: format/version, seed digest, instrument identity, N/D, working-coordinate and border counts, chunk size, phase, next variable and row offset, completed closure-round count, relation rank, exact row width, and the first rank rows of the echelon matrix. Reconstructing the provisional map can repeat work; it does not change the mathematical input.

For the closure phase, start with checkpoints at completed round boundaries. A within-round checkpoint cannot reconstruct the round's fixed low-row matrix from the evolving relation matrix: it must retain that fixed matrix and the next variable/chunk, or restart the entire round from its saved initial state. Do not skip these dependencies. A stable-rank round must retain its completion flag so restart can proceed to export without inventing convergence.

Persist only completed operations. Write a new snapshot to a temporary file, flush/fsync, close, then atomically rename. The worker uploads immutable snapshot objects and a manifest containing full hashes, lengths, input and executable identities, and progress metadata. Publish the manifest only after the objects are durable and read back with matching hashes. Restore the newest fully verified compatible manifest; never select a partial file or an unverified latest pointer. Retain at least one prior complete checkpoint until the new checkpoint is verified. Do not overwrite prior attempt evidence.

Use streamed serialization with bounded buffers. Include checkpoint I/O buffers and concurrent live matrices in memory admission. Account for ephemeral disk needed for old/new snapshot files and transfer staging; the prior 10 GiB pod limit is not automatically sufficient. Avoid a second full matrix copy merely to serialize. Upload must finish or explicitly fail before deleting a checkpoint. An interruption during serialization/upload should leave a usable prior checkpoint.

## Restore and correctness gates

Reject wrong seed, executable, dimensions, chunk schedule, invalid phase/offset, rank beyond coordinate count, short/trailing data, nonzero padding, and content-hash mismatch before using state. Shape checks do not prove matrix provenance; hashes bind a trusted producer's completed snapshot. The final certificate must still pass the original independent checker against the original system and a fresh exact count. A resumed producer's successful exit is not certification.

Required qualification: uninterrupted versus stop/restore byte equality on existing generic and Semaev fixtures; interruption after each seed chunk boundary and completed closure round; stable-round export restore; fresh and restored killed-constant outcomes; malformed/truncated/wrong-input snapshots; interrupted upload and manifest publication; repeated restore with no skipped/duplicated scientific inputs; original checker acceptance and exact count comparisons. Include a fixture with multiple closure rounds and multiple chunks. Record all failures as well as successes. Checkpoint timings remain L0 telemetry only.

## Deployment gate and scope

First qualify local restore with an explicit frozen control protocol. Then qualify cloud checkpoint publication, complete GET/hash restoration in a new pod, and original-checker acceptance on a bounded fixture. Only then freeze a new frontier continuation with new request/job identity, inherited exact n47 random00 input, retained failed attempts, resource admission, checkpoint interval, and finite interruption handling. If these gates fail, preserve the degree-six objective and report the exact gap. Forty unfinished local inputs and eleven unfinished panel inputs remain in scope; this recovery work does not replace them.
