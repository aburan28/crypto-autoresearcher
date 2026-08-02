# EXP-SMTH-PILOT-001 implementation note

Task: `TASK-20260801-082`

Scope: implementation only. No registered scientific run was started, and no
run or result artifact was generated. The implementation exposes only a
null-pilot entry point and a bounded synthetic self-test; it contains no curve,
factor-base, S3, source, plant, p-value, evidence, or research-state mode.

## Contract binding

The code implements the committed effective contract through
`EXP-SMTH-PILOT-001-AMEND-007`, snapshot
`1987f8d41ece5dd5eda9120903dced96c928d763`, under the implementation-only
authorization `TASK-20260801-081`.

Frozen scientific plumbing includes the 32 deterministic null arrays, exact
`i<j` enumeration, 4,186,112 factorization/reconstruction calls, the shared
`sympy.factorint`/`sympy.isprime` certificate path, four factor workers, one
ordered writer, a 4,096-record bound, 128 exact shard names, 32,704 records per
shard, deterministic gzip metadata, the 1,024-byte logical-record cap, and the
8-MiB physical shard cap. Runtime methods enforce the frozen wall, CPU, RSS,
primality, shard, and aggregate ceilings.

The seed-roster implementation records every array-domain tuple and its ordered
seed-stream SHA-256, plus the exact derivation rule and global collision count.
This compact representation is necessary to remain compatible with the frozen
32-MiB individual non-shard artifact cap; it does not store 4,186,112 seeds
verbatim.

The live-bounded pack sink writes at most `cap_bytes - bytes_written` from each
chunk. On a cap-plus-one byte it closes the producer pipe, waits for producer
termination, and removes only the exact `.partial` path. A successful EOF with
producer exit zero fsyncs and atomically renames the pack. Device accounting
implements both the 6,908,096,384-byte same-device gate and the split-device
1,610,612,736-byte worktree / 5,297,483,648-byte common-directory gates.

## Protocol deviations

None. The specification records `master_seed: 25051`, while its binding seed
formula does not include that field. The implementation records the master seed
as provenance and follows the literal six-field formula without silently adding
an extra hash input.

## Tests

All commands ran from `/private/tmp/ecdlp-breakthrough-20260801-main2` on
2026-08-01. No command invoked `run-null-pilot`.

1. `python3 -m py_compile experiments/EXP-SMTH-PILOT-001/implementation/pilot_driver.py`
   — exit 0, no output. The generated `__pycache__` test byproduct was removed;
   it is not a task artifact.
2. `python3 experiments/EXP-SMTH-PILOT-001/implementation/pilot_driver.py self-test`
   — exit 0; `status=pass`, `scientific_runs=0`. All six named tests passed:
   `bounded-pack-exact-cap`, `bounded-pack-cap-plus-one`,
   `bounded-pack-producer-failure`, `split-device-accounting`,
   `factor-certificate-controls`, and `deterministic-null-plumbing`.
3. The first ad-hoc constant-check import harness failed before assertions with
   `AttributeError: 'NoneType' object has no attribute '__dict__'` because the
   harness did not register its dynamically loaded module in `sys.modules` as
   required by `dataclasses`; this was a test-harness error, not a driver
   execution or scientific run. The corrected harness registered the module,
   checked 32 arrays, 130,816 records/array, 4,186,112 total records, 128 unique
   exact shard names from `shard-000.jsonl.gz` through
   `shard-127.jsonl.gz`, all aggregate-byte equations, and printed
   `contract-constant-checks: PASS; scientific_runs=0` with exit 0.
4. `python3 experiments/EXP-SMTH-PILOT-001/implementation/pilot_driver.py --help`
   — exit 0; the only subcommands listed were `self-test` and
   `run-null-pilot`.
5. `git diff --check` — exit 0, no output.

Across both self-test invocations during authoring, 12 bounded named synthetic
test executions passed. Including the failed and corrected constant harness,
14 bounded test executions were attempted, within the authorization maximum of
20. The registered pilot was never invoked.

Scientific run count: **0**.
