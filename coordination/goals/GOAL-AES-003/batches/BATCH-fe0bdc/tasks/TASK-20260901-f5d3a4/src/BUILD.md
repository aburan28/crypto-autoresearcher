# BUILD.md — TASK-20260901-f5d3a4

## Environment

- Host: Adams-MacBook-Pro.local, arm64-apple-darwin25.6.0 (Darwin 25.6.0, xnu-12377.161.13), 14 CPUs, 48 GiB RAM.
- Python: 3.12.8 (stdlib only; no third-party imports anywhere in this task).
- C compiler: Apple clang version 17.0.0 (clang-1700.0.13.5), target arm64.
- Git: worktree branch `aes003-batchfe0bdc-20260901`, HEAD `b85b601a13074e226eebd375756c45db4e8df3b2`
  at session start; dirty-tree state = only this task's write_scope files (verified at start, 0
  other modifications).

## Build commands

```sh
cc -O2 -pthread -o src/affarm046 src/affarm046.c
```

(no warnings expected; binary is task-local, never installed)

## Run commands (in order; each stamped in budget_stamps.jsonl)

- RUN 1 (BLOCKING): `python3 src/gate0.py runs/gate0.json` — stdout -> runs/gate0.stdout.
  Exit 0 = pass; exit 5 = F1 halt.
- RUN 2: `python3 src/census046.py runs/census.json` — stdout -> runs/census.stdout;
  writes runs/census.json.digest.txt (sha256 of census.json, finalized before the arm).
  Exit 0 = table matches; exit 6 = F3.
- RUN 3: `python3 src/bridge.py runs/keyed_bridge.json` — stdout -> runs/keyed_bridge.stdout.
  Exit 0 = bridge 100%; exit 7 = deviation.
- RUN 4: build + `src/affarm046 pin 46060901` + `src/affarm046 pinidentity 46060901` +
  `src/affarm046 geom` + determinism double-run at log2N=16 (arm CAL-DET, 1 thread) +
  calibration rate arm at log2N=22 (arm CAL-RATE, 8 threads) +
  `python3 src/cal_crosscheck.py <seed> 1 6 1 1 65536` exact Python replication of the
  1-thread log2N=16 arm; source diff vs the campaign build -> runs/source_diff.txt;
  combined receipt -> runs/build_pin_cal.json.
- RUN 5: `/usr/bin/time -l src/affarm046 arm FIXTURE-R6-A0-S0 6 1 1 30 46063001 1 <threads> identity`
  -> runs/fixture_arm.json (stdout), runs/fixture_arm.timing.txt, runs/fixture_arm.err.
- RUN 6: `python3 src/analyze.py` -> runs/decision_analysis.json, runs/parse_check.txt.

## Determinism

The arm receipt is a deterministic function of (name, rounds, amask, smask, log2N, seed,
arm_id, threads): per-thread splitmix64 streams with the campaign seed formula
`seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15`, trial partition N/nthr. RUN 4
verifies byte-identical receipts for two invocations of an identical configuration.
Different thread counts change the stream partition (documented, not claimed identical).

## Budget

Declared wall clock 3600 s (binding stop recorded in budget_stamps.jsonl); maximum 6 runs;
memory budget 4 GiB (census matrices are 128x128 bit-integers; arm is O(1) per trial).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model);
model_verified: false; fallback_used: true (session-backend transport under inference
amendment DEC-20260831-0d1eeb); degraded_requirements: []; amendment: DEC-20260831-0d1eeb;
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c.
