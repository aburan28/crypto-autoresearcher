# BUILD — TASK-20260901-47b21f (BATCH-7939d0, GOAL-AES-003, RC-D second seed/key)

Written 2026-09-01, after source copy and build, BEFORE any run output exists.

## Verbatim-source control (binding constraint 1: SOURCE IS VERBATIM)

`rc8probe_feistel.c` was copied unchanged from the archived BATCH-014 RC-D
source. Zero code changes. `cmp` reports the two files identical.

| file | sha256 |
|---|---|
| archived source `coordination/goals/GOAL-AES-003/batches/BATCH-014/tasks/TASK-20260805-b95720/src/rc8probe_feistel.c` | `9b36c0e714118e11e160b9aec81c9a6c1aceecc6fb2b6c452b3dd3bbf98d8566` |
| this task's copy `src/rc8probe_feistel.c` | `9b36c0e714118e11e160b9aec81c9a6c1aceecc6fb2b6c452b3dd3bbf98d8566` |

**PARITY: MATCH** (identical hash; `cmp` exit 0).

The ONLY varied parameter in any run of this binary is the seed CLI field
(531002 here vs 531001 in RC-D).

## AES-arm instrument (recomputed live arm under S2)

The AES arm is run with BATCH-015's archived instrument
`rc8probe_freshfeistel.c` invoked ONLY in its `aes` oracle mode. This
instrument's live-AES code path is rc8probe.c's AES code copied byte-for-byte
(BATCH-015 source header, "LIVE ARM code copied from rc8probe.c"), and
BATCH-015 verified that path reproduces BATCH-009's frozen P1-R5-PAIR reading
BYTE-EXACTLY at seed 531001 (EV-AES-4ba350 OBS-B15-4: identical 14 hits,
identical hit-trial indices, identical plaintext-stream digests, identical
thread seeds; AES key re-derives from the seed alone). It is the in-read-scope
instrument with a verified AES code path. Its `freshfeistel` oracle mode is
NEVER invoked by this task. Copied unchanged; `cmp` identical.

| file | sha256 |
|---|---|
| archived source `coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/src/rc8probe_freshfeistel.c` | `d163b64e6b0d6bce1f23027bb7209c0a8c5ef1984874465119f61adf3e0d450d` |
| this task's copy `src/rc8probe_freshfeistel.c` | `d163b64e6b0d6bce1f23027bb7209c0a8c5ef1984874465119f61adf3e0d450d` |

**PARITY: MATCH** (identical hash; `cmp` exit 0).

## Exact build commands

```
gcc -O3 -pthread -o src/rc8probe_feistel src/rc8probe_feistel.c
cc -O3 -pthread -o src/rc8probe_freshfeistel src/rc8probe_freshfeistel.c -lm
```

The first is the build command recorded in `rc8probe_feistel.c`'s own header
comment (`build: gcc -O3 -pthread -o rc8probe_feistel rc8probe_feistel.c`),
which is the only build command BATCH-014 recorded for it. The second matches
BATCH-015's recorded build command for its instrument (RESULTS.json `commands`
block: `cc -O3 -pthread -o src/rc8probe_freshfeistel src/rc8probe_freshfeistel.c -lm`).

Both built clean, zero warnings emitted to the invoking shell, exit 0, on
2026-09-01 at ~08:58 local (15:58 UTC). On this machine both `gcc` and `cc`
resolve to Apple clang version 17.0.0 (clang-1700.0.13.5),
target arm64-apple-darwin25.6.0 (same toolchain BATCH-015 recorded).

Built artifact hashes (for the record; determinism of build artifacts is not
claimed across toolchains):

| binary | sha256 |
|---|---|
| `src/rc8probe_feistel` (34272 bytes) | `7d15d04452c07b9843e2a43030ccf28d9df97c7c8cfd2538c70e68013bc90f17` |
| `src/rc8probe_freshfeistel` (51160 bytes, same size as BATCH-015's archived binary) | `f65bcfe09c62f7742faf1980bac382b18081bbabf52d561a05953bb576eed1a4` |

## CLI shapes (unchanged from the archived sources)

```
src/rc8probe_feistel detcheck <seed>
src/rc8probe_feistel arm <name> <rounds_ignored> <amask> <smask> <log2N> <seed> <armid> <threads>
src/rc8probe_freshfeistel arm <name> <oracle=aes|freshfeistel> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads>
```

RC-D baseline parameter set (BATCH-014 M1-FEISTEL-P30): seed 531001, armid 1,
amask=smask=1, log2N=30, threads 4. This task repeats it with seed 531002 only.

## Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: fireworks-ai/accounts/fireworks/models/qwen3p8-max
  fallback_used: true        # transport fallback to session backend under DEC-20260831-0d1eeb (zai billing outage)
  model_verified: false
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

Parse statement: this file is prose + tables for human/audit reading; the
authoritative machine-parseable records of this task are the JSON artifacts
under this task directory, each parsed whole before the task finishes.
