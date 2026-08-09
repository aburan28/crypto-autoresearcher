# BATCH-bd36fe v8 provenance and replay-control repair

This is a superseding, design-only control repair after the independent v7
review `TASK-20260809-60481d` returned `REVISE`. The v4-v7 records remain
immutable. v8 does not implement ECDLP, define a frozen experiment, authorize
an Executor, execute a run, create evidence, or change research status.

## Residual findings repaired

| v7 review finding | v8 closure |
|---|---|
| Arbitrary corrected command | `matrix_validator_metadata_xor_v8.json` records a canonical argv list and exact shell command. The validator constructs the same normalized argv and requires both fields to match byte-for-byte; the historical command remains context only. |
| Forged v6 manifest pointer | The v8 contract and manifest bind the exact v6 manifest path relative to the immutable v6 root and its SHA-256. The validator resolves that path, hashes the bytes, and passes the same exact path to the v7 predecessor gate. |
| Accepted-case filename swap | The contract contains a complete filename-to-fixture map and each file hash. The validator requires the path stem, fixture ID, contract entry, manifest entry, and file hash to agree before applying the existing v7 schema/payload checks. |
| Summary-only per-arm matrix binding | `per_arm_run_bindings_xor_v8.json` contains 400 ordered entries. Each entry binds the run ID, canonical arm-key tuple and digest, every retained run/resource field, a full arm-record digest, and a deterministic event-ledger digest derived from the immutable event template. Matrix arms must equal their corresponding records; aggregate recomputation is not sufficient. |
| Source-token relabelling | The v8 contract carries a normative key-to-path-and-hash map. The source-binding file must equal that map exactly, including semantic keys, paths, hashes, and fixture tokens; a path/hash pair cannot be relabelled under another key. |

## Predecessor and execution boundary

The v8 validator invokes the exact archived v7 fixture-only validator before
performing its five strict checks. It then applies five in-memory v8 mutations:
arbitrary command, forged predecessor manifest pointer, filename/fixture swap,
changed per-arm CPU with adjusted aggregates, and relabelled source token. All
must fail. It reads immutable v6/v7 sources and v8 control metadata and never
writes them.

The package is a synthetic control fixture. A successful `VALIDATION_PASS`
means only that the declared v7 predecessor suite and v8 provenance mutations
behave as declared. It is not an ECDLP observation, performance result,
security claim, asymptotic result, cryptographic-scale validation, experiment
specification, approval, Executor admission, run, evidence, or status
transition. A fresh independent `review-adversarial` freeze review of the
archived v8 bytes is required before any specification gate.

## Normative record encoding

The per-arm binding uses compact tuples to avoid a second, mutable copy of the
matrix schema while retaining every value needed for comparison:

```text
arm_key = [p, b_num, b_den, arm, seed, process_replica, null_replica, shard]
record = [state, terminal_reason, included_in_metrics, wall_repeats,
          [raw, stdout, stderr],
          [start_ns, stop_ns, clock_source, unit, flush_complete],
          rss_samples, cpu_seconds]
```

The validator reconstructs the complete canonical arm object from each tuple,
checks its SHA-256 against the binding, and compares all fields to the matrix
arm at the same ordinal. The event digest binds the run ID into the canonical
event template, so changing the run identity cannot silently reuse a different
event record.
