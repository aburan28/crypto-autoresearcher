# EXP-SMTH-PILOT-001 implementation repair note

Tasks: `TASK-20260801-082`, repairs `TASK-20260801-095`,
`TASK-20260801-100`, `TASK-20260801-105`, and `TASK-20260801-115`

Scope: implementation only. No registered scientific run was started, and no
run or result artifact was generated. The implementation exposes only the
null-pilot entry point and bounded synthetic self-tests; it contains no curve,
factor-base, S3, source, plant, p-value, evidence, or research-state mode.

## Contract binding

The repaired code implements the effective contract through
`EXP-SMTH-PILOT-001-AMEND-009`, passed at snapshot
`82c8bcc1d0ddc9b58d270a21aa17343a5760b2f8`, under repair authorization
`TASK-20260801-094`. It preserves the earlier live-bounded pack and archive
constraints and adds the passed compact seed representation from AMEND-008/009.
The narrow successor repair binds implementation snapshot
`e4e253b7e62dfea878622f6dc9563ef3c9b75b85` and validation
`VAL-20260801-097` under authorization `TASK-20260801-099`; it changes no
scientific design, count, seed, path, cap, or research status.
The final two-defect repair binds snapshot
`badc73b3f395858ff9ca898aaaa1483cce27a25b` and validation
`VAL-20260801-102` under authorization `TASK-20260801-104`.
The descriptor-binding repair binds snapshot
`5e78665ada170acd1be4fd2d1cb82f5d3bf4c1d9` and the preserved
preconstruction failure `TASK-20260801-113` under authorization
`TASK-20260801-114`. It changes only the platform-specific path verification
and its bounded regression control; it does not alter the scientific protocol.

Frozen scientific plumbing remains 32 deterministic null arrays, exact `i<j`
enumeration, 4,186,112 factorization/reconstruction calls, the shared
`sympy.factorint`/`sympy.isprime` certificate path, four factor workers, one
ordered writer, a 4,096-record bound, 128 exact shard names, 32,704 records per
shard, deterministic gzip metadata, the 1,024-byte logical-record cap, and the
8-MiB physical shard cap.

## VAL-20260801-084 repairs

- `VAL084-B1`: the arbitrary output root was removed. The executable derives
  the checkout from its own frozen path and admits exactly the 137 literal
  repository-relative run-evidence paths. Manifest entries are repository
  relative. A fresh run refuses pre-existing evidence paths and requires the
  exact stdout/stderr redirections before any construction.
- `VAL084-B2`: every completed factor record returns worker CPU and peak RSS to
  a live process-tree monitor, which enforces cumulative CPU and a conservative
  aggregate peak-RSS bound at each record boundary and cross-checks the process
  tree at shard boundaries; per-device free
  space, physical run bytes, aggregate shard, aggregate other, aggregate
  tracked, individual other-file, process-output-handle, wall-clock,
  primality, and no-network gates are enforced and recorded. Factor workers
  install the same no-network guard.
- `VAL084-B3`: every independently reconstructed, fsynced shard triggers an
  atomic checkpoint in the required run manifest. The checkpoint contains
  verified shard hashes, next deterministic index, factorization/primality
  counts, CPU, wall, peak RSS, disk/device measurements, cell counters, and
  event history. `--resume` consumes exactly one resume, verifies every saved
  shard, reconstructs prior LPFs from certificates, removes uncheckpointed
  bytes, and continues under the same cumulative ceilings.
- `VAL084-B4`: bounded controls now exercise a literal twelve-factor list with
  a composite twelfth item, actual pre-open rejection of a 1,025-byte logical
  record, one-byte shard mutation, independent canonical-payload hashing,
  exact-cap/cap-plus-one pack behavior, and checkpoint hash verification.
- `VAL084-B5`: the feasibility result includes exact calls/checks/
  reconstructions; full process-tree CPU, wall, peak RSS and disk accounting;
  per `(bits,null_type)` factorization rates and certificate bytes; all
  checkpoint/resume/stop events; SymPy, Python, platform and Git provenance;
  and a labeled modeled full-v2 projection with the frozen linearity caveat.
- `VAL084-B6`: 52 lexicographically ordered compact descriptors expand to
  exactly 2,109,444 tuple-derived seeds: 2,093,056 IID, 16,384 K512 A/B, and
  four prime seeds. Every 16-byte seed enters an exact membership set. The
  implementation records 52 per-stream hashes, the global ordered hash
  `c3991b86bedce849dd8b13dee1550ae79405526d9b1467ff4ac30436bdc37fc6`,
  exact inserted/distinct/collision counts, and the AMEND-009 canonical payload
  hash. K512 edge commitments are explicitly separate and never counted as
  tuple-derived seeds.
- `VAL084-B7`: all top-level failures abort the current partial, reconcile
  final shards to the last verified checkpoint, and preserve a resumable
  infrastructure receipt or non-resumable integrity receipt. Synthetic worker
  and resource-cap interruptions leave no uncheckpointed final or partial
  shard.

## VAL-20260801-097 repairs

- `VAL097-B1`: every returned factor record now updates the attempt's worker
  CPU and conservative process-tree RSS receipt, constructs cumulative usage
  by adding the prior stopped attempt, and checks the cumulative wall ceiling
  before accepting the record. Failure handling overwrites the durable CPU,
  wall and peak-RSS fields with the final attempt sample plus prior charged
  usage; it no longer preserves a stale checkpoint value with `setdefault`.
  Resume reloads those stopped totals, refuses an already exhausted budget,
  and gives the monitor only the remaining CPU allowance.
- `VAL097-B2`: `classify_failure` maps certificate, seed and hash
  `IntegrityError` failures only to `invalid_integrity`; resource ceilings map
  to resource exhaustion; `BrokenProcessPool`, missing dependencies, OS,
  subprocess and interruption failures map to infrastructure; unexpected code
  faults are separately labeled implementation errors. The committed control
  creates a real child process, exits it with `os._exit(17)`, observes
  `BrokenProcessPool`, preserves the checkpointed shard, and verifies the
  infrastructure classification. The older N=0 control is honestly renamed as
  an integrity fixture.
- `VAL097-B3`: one append-only in-memory event history is atomically copied into
  every manifest checkpoint. Each event has a monotone sequence, UTC timestamp,
  type, checkpoint index, cumulative resources, resume count and outcome.
  Failure appends and persists `stop`; resume reloads it, appends and immediately
  persists `resume`; shard closure appends `checkpoint`; successful termination
  appends `complete`. Final feasibility output carries the complete history and
  typed stop, resume and checkpoint projections rather than an unconditional
  empty stop list.

The two validator-noted fixture debts are also repaired: the oversized JSONL
fixture is exactly 1,025 bytes including its newline, and the one-byte mutation
control mutates a real deterministic gzip certificate shard.

## VAL-20260801-102 repairs

- `VAL102-B1`: the three real SymPy wrapper paths now translate caught
  `ImportError`/`ModuleNotFoundError` into the dedicated
  `DependencyInfrastructureError`, which `classify_failure` maps to
  `failed_infrastructure_or_budget` / `infrastructure_error`. The bounded test
  intercepts the actual Python import used by `factor_certificate`, observes
  the dedicated exception, and verifies its durable classification; it does
  not call the classifier directly with a fabricated dependency exception.
- `VAL102-B2`: `main` no longer prints the full returned result after the run
  protocol. The protocol itself writes and fsyncs one bounded constant-size
  terminal stdout record before final accounting. It then iteratively writes
  the identical raw/feasibility receipts and terminal manifest, remeasures the
  completed fixed roster, cap-checks every observation, and stops only when the
  embedded receipt equals the post-write physical and tracked-byte measurement.
  No successful-path write follows that equality check; `main` returns without
  additional stdout bytes. The bounded temporary-roster control independently
  recomputes terminal stdout, both result files, and manifest bytes and matches
  all three durable receipts exactly.

The live-bounded pack sink still writes at most
`cap_bytes - bytes_written` from each chunk. On cap-plus-one it closes the
producer pipe, waits for termination, and removes only the exact `.partial`.
Successful EOF with producer exit zero fsyncs and atomically renames the pack.

## Protocol deviations

None. The base specification records `master_seed: 25051`, while the binding
seed formula does not include that field. The implementation records it as
provenance and follows the literal six-field formula without adding a hash
input.

## Repair tests

All commands ran from `/private/tmp/ecdlp-breakthrough-20260801-main2` on
2026-08-01. No command invoked `run-null-pilot`.

1. An AST-only syntax parse printed `ast: PASS` and created no bytecode.
2. The first full repaired `self-test` invocation passed eight named controls,
   then failed the ninth (`checkpoint-resume-interruption-cleanup`) with
   `IntegrityError: non-sequential certificate record`. The failure identified
   that abort cleanup deleted the uncheckpointed partial but did not reset the
   in-memory next index. Reconciliation was repaired to derive both next index
   and shard position solely from verified checkpoint entries. A harmless
   destructor warning (`flush of closed file`) also led to an idempotent closed
   writer flush.
3. The second full invocation
   `PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-SMTH-PILOT-001/implementation/pilot_driver.py self-test`
   exited 0 with `status=pass`, `scientific_runs=0`, and eleven passes:
   pack exact-cap, pack cap-plus-one, producer failure, split-device accounting,
   certificate controls, deterministic null plumbing, exact 137-path roster,
   process-tree/disk/handle/network controls, checkpoint/resume/interruption
   cleanup, one-byte mutation/independent hashes, and the exact 52-stream /
   2,109,444-seed contract.
4. After adding explicit RSS-cap-plus-one and worker/resource-failure controls,
   the filtered invocation
   `PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-SMTH-PILOT-001/implementation/pilot_driver.py self-test --only process-tree-disk-handle-network-controls --only worker-and-resource-failure-cleanup`
   exited 0. Both named tests passed with `scientific_runs=0`.
5. A final AST-only parse passed after the reporting and fixed-path changes.
6. After adding per-record worker CPU/RSS receipts, the filtered
   `worker-and-resource-failure-cleanup` test was rerun alone and passed with
   `scientific_runs=0`.

The repair used 23 named bounded test attempts: nine in the first interrupted
invocation, eleven in the full passing invocation, and two in the filtered
passing invocation, plus the final worker-control rerun. This is within the
authorization maximum of 30. The failed test is preserved above and was not a
scientific run.

## TASK-20260801-100 tests

No command invoked `run-null-pilot`.

1. An AST-only parse passed before execution of bounded controls.
2. The single full bounded invocation
   `PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-SMTH-PILOT-001/implementation/pilot_driver.py self-test`
   exited 0 with `status=pass`, `scientific_runs=0`, and all 14 named tests
   passing. In addition to the retained controls, it passed exact 1,025-byte
   writer rejection, real gzip mutation, cumulative nonzero pre-stop and
   post-resume charging with ordered `checkpoint,stop,resume,checkpoint`
   durability, honest integrity/resource cleanup, and a real broken worker pool
   classified as infrastructure while preserving its verified shard.
3. After adding explicit classification assertions for integrity and resource
   exhaustion, the filtered `integrity-and-resource-failure-cleanup` test was
   rerun alone and passed with `scientific_runs=0`.

This task used 15 of its authorized 20 bounded test attempts.

## TASK-20260801-105 tests

No command invoked `run-null-pilot` and no run/result path was created.

1. An AST-only syntax parse passed without bytecode output.
2. The single full invocation
   `PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-SMTH-PILOT-001/implementation/pilot_driver.py self-test`
   exited 0 with `status=pass`, `scientific_runs=0`, and all 15 named controls
   passing. The new combined release-candidate control passed both the real
   missing-SymPy wrapper classification and convergent terminal-storage receipt
   equality after terminal stdout and manifest writes.

This task used exactly 15 of its authorized 15 bounded test attempts.

## TASK-20260801-115 descriptor-binding repair

On macOS, `/dev/fd/1` and the opened target path can name distinct vnode
identities even though descriptor 1 was opened on that exact path, so
`os.path.samefile` rejected the valid archived redirection before scientific
construction. The guard now asks the kernel for the descriptor's path with
`fcntl.F_GETPATH`, resolves the expected path, and requires exact canonical
path equality. Linux is the other supported platform for this guard and uses
the kernel `/proc/self/fd/<n>` symlink as its reviewed exact-path fallback.
Other platforms fail closed rather than substituting inode identity.

No command invoked `run-null-pilot`, and the archived stdout/stderr files from
`TASK-20260801-113` were not opened for writing.

1. An AST-only syntax parse passed without bytecode output.
2. The targeted invocation
   `PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-SMTH-PILOT-001/implementation/pilot_driver.py self-test --only real-subprocess-descriptor-redirection`
   launched a real child with stdout and stderr redirected to temporary exact
   paths. On macOS the child observed the old `/dev/fd/1` `samefile` result as
   false, passed the new `F_GETPATH` guard for both descriptors, and confirmed
   that the new guard rejects a different existing path.

This task used one of its authorized ten bounded test attempts.

Scientific run count: **0**.
