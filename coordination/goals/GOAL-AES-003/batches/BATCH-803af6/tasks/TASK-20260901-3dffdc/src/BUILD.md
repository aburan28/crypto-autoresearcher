# BUILD.md — TASK-20260901-3dffdc

Environment: macOS (darwin), Apple clang (system `cc`), Python 3 standard library only
(no numpy, no scipy). Machine: the BATCH-803af6 worktree host (see timing files for
actual run conditions).

## Census and anchor recomputation (pure Python, zero cipher compute)

```
python3 src/anchor_check.py runs/anchor_recompute.json    # RUN 1, BLOCKING per F1
python3 src/census.py runs/census.json                    # RUN 2
```

- `anchor_check.py` exits 0 on F1-gate pass, 5 on F1-gate fail (HALT path).
- `census.py` exits nonzero with a `{"fatal": ...}` line if any internal GF(2)
  consistency check fails (matrix identities, Mobius non-negativity/sum).

## Affine oracle (C, pthreads)

```
cc -O2 -pthread -o src/affprobe src/affprobe.c
```

Modes:

```
./src/affprobe pinidentity <seed>
./src/affprobe geom
./src/affprobe arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads>
```

Determinism: per-thread seed = `seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15`,
identical to the BATCH-b41ba9 probe_sbox.c lineage formula; thread count is therefore
part of the deterministic specification and is recorded in every arm JSON. Guards:
smask in {0,15} rejected, amask=0 rejected, rounds 1..10, log2N 1..40.

## Arm invocations used by this task

```
./src/affprobe pinidentity 20260901                                          # RUN 3
./src/affprobe arm CAL 5 1 1 20 20260901 900 8                               # RUN 4
./src/affprobe arm ANCHOR-P30 5 1 1 30 189001301 301 8                       # RUN 5
./src/affprobe arm FIXTURE-P30 <r> <amask> <smask> 30 189001301 302 8        # RUN 6
```

RUN 5 reuses the archived anchor seed/armid (189001301/301) at 8 threads so each
thread's 2^27-trial stream is an exact prefix of the archived BATCH-b41ba9 ID5 arm's
per-thread 2^29-trial streams (PREREGISTRATION.md section 4). RUN 6 parameters come
from `runs/fixture_pick.json`, written BEFORE the run per the preregistered pick rule.

Every run is wrapped: `/usr/bin/time -l <cmd> > runs/<name>.json 2> runs/<name>.timing.txt`
with program stderr separately in `runs/<name>.err` (empty expected, exit code recorded).

## Decision arithmetic

```
python3 src/analysis.py runs      # not a run: arithmetic on already-written JSONs
```

Produces `runs/decision_analysis.json`. The Garwood/exact-binomial machinery
self-checks against the published figures of EV-AES-e4c091 / BATCH-015 before any
new statistic is computed; a self-check failure aborts the verdict.

## Parse discipline

Every JSON artifact is parsed whole with `python3 -c "import json,sys; json.load(open(...))"`
after writing; RESULTS.json records the pass/fail of each and states the attestation.

## Inference block (all artifacts)

policy executor-implementation; requested_policy executor-implementation;
resolved_model_id fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session
backend); fallback_used true (session-backend transport under DEC-20260831-0d1eeb,
standing basis 0137a051eb5828789eb267fa83c8278086578d4c); model_verified false
(no adapter probe run this session); degraded_requirements [].
