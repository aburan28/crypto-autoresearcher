# BUILD.md — TASK-20260901-579808 (BATCH-ace664, GOAL-AES-003)

## Environment

- Host: Adams-MacBook-Pro.local, arm64, Darwin 25.6.0 (macOS), 14 CPUs, 48 GiB RAM.
- Python: 3.12.8 (stdlib only; fractions/json/hashlib/re/subprocess/datetime/math).
  Note: `sys.set_int_max_str_digits(1000000)` in xstat.py/crosscheck.py/
  assemble_results.py to format the ~9e3-digit exact rationals at n = 53
  (disclosed as DEV-2 in RESULTS.json).
- C compiler: Apple clang version 17.0.0 (clang-1700.0.13.5), target arm64.
- Git: worktree branch `aes003-batchf829-20260901`, HEAD
  `b8cba58495527950e882c8a9c310da8e51d9f6a0` at session start; dirty-tree
  state = only this task's write_scope files (untracked), verified at start
  and completion.

## Lineage

Cap-256 derivative of the BATCH-5ed9a3 instrument
`coordination/goals/GOAL-AES-003/batches/BATCH-5ed9a3/tasks/TASK-20260901-ed281d/src/affarm046ex.c`
(itself the extended derivative of the Stage-0 affarm046e instrument for
IDEA-20260901-363851). The ONLY instrument change is the frozen constant
`#define HIT_LOG_CAP 64` -> `#define HIT_LOG_CAP 256` (line 341), audited in
runs/source_diff.txt (pre-arm and post-arm, PASS both). Support scripts:
det_cmp.py and freeze_digest.py copied from BATCH-5ed9a3 and relabeled;
freeze_digest.py's folded smoke self-check cap constants updated 64 -> 256
(disclosed script delta, PREREGISTRATION.md §6 item 1). gate0x_cmp.py written
fresh (extended allowed-diff list incl. hit_log_cap; G3-receipt identity
checks). Analysis code written FRESH for this task: src/dpcore.py
(common-denominator exact integer-polynomial DP), src/xstat.py (arm analysis
+ realized-composition cutoff), src/power.py (E-rho power/BF at realized N),
src/jointlr.py (joint LR with committed G5), src/crosscheck.py (DP
cross-validation against the committed G5 analysis), src/assemble_results.py
(ordered PX cascade).

## Build command

```sh
cc -O2 -pthread -Wall -o src/affarm046ex src/affarm046ex.c
```

Compiled clean (no warnings) before any run.

## Run commands (in order; each stamped in budget_stamps.jsonl; 8 completed invocations = cap)

- P0 (not an invocation): write PREREGISTRATION.md BEFORE any fresh arm
  (mtime 2026-09-01T15:14:32 local, before P1a).
- Cross-check (0 runs, analysis only): `python3 src/crosscheck.py
  ../../../BATCH-5ed9a3/tasks/TASK-20260901-ed281d/runs/G5_j5_2.json
  ../../../BATCH-5ed9a3/tasks/TASK-20260901-ed281d/runs/G5_analysis.json
  runs/crosscheck_g5.json` -> PASS (digit-for-digit reproduction).
- P1a (BLOCKING): `src/affarm046ex pin 363851` -> runs/P1a_pin.json.
- P1b (BLOCKING): `src/affarm046ex pinidentity 363851` -> runs/P1b_pinidentity.json.
- P2 (BLOCKING): `src/affarm046ex arm GATE0X256-J5-1-AES-R5-P30 5 1 1 30 531001 1 2 aes`
  -> runs/P2_gate0x.json; then `python3 src/gate0x_cmp.py runs/P2_gate0x.json
  ../../../BATCH-015/tasks/TASK-20260805-d408ac/runs/L1-AES-R5-P30.json
  ../../../BATCH-5ed9a3/tasks/TASK-20260901-ed281d/runs/G3_gate0x.json
  runs/P2_gate0x_cmp.json` (exit 5 => HALT FX5-P). First attempt killed by the
  120 s shell-tool timeout (empty receipt; DEV-1); completed on rerun.
- P3 (ANCHOR, analyzed FIRST): `src/affarm046ex arm ANCHORX-R6DEAD-AES-R6-P32 6 1 1
  32 531003 1 4 aes` -> runs/P3_anchor_r6.json; `python3 src/xstat.py
  runs/P3_anchor_r6.json runs/P3_anchor_analysis.json`.
- P4 (admitted ONLY because P3 passed): `src/affarm046ex arm J5-2-P32 5 1 1 32
  531003 1 4 aes` -> runs/P4_j5_2_p32.json; `python3 src/xstat.py
  runs/P4_j5_2_p32.json runs/P4_analysis.json`; `python3 src/power.py
  runs/P4_j5_2_p32.json runs/P4_power.json`; `python3 src/jointlr.py
  runs/P4_j5_2_p32.json ../../../BATCH-5ed9a3/tasks/TASK-20260901-ed281d/runs/G5_j5_2.json
  runs/P4_jointlr.json`.
- P5: determinism double, IDENTICAL command twice: `src/affarm046ex arm
  DETX256-AES-R5-P20 5 1 1 20 531001 1 4 aes` -> runs/P5_det_a.json,
  runs/P5_det_b.json; `python3 src/det_cmp.py runs/P5_det_a.json runs/P5_det_b.json
  runs/P5_det_cmp.json`.
- P6: `src/affarm046ex freeze 363851` -> runs/P6_freeze_c_output.json; `python3
  src/freeze_digest.py runs/P6_freeze_c_output.json runs/P6_freeze_rerun.json
  --reverify ../../../BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json
  runs/P6_digest_reverify.json`; source-diff post-arm re-verification ->
  runs/source_diff_raw_postarm.txt (appended verdict in runs/source_diff.txt).
- Assembly: `python3 src/assemble_results.py` -> RESULTS.json (verification
  load after writing; parse attestation inside).

Timing capture: `/usr/bin/time -l <cmd> > runs/X.json 2> runs/X.timing.txt`;
`runs/X.err` created empty per arm to record the no-stderr convention.

## Budget

Declared wall clock 18000 s (binding stop in budget_stamps.jsonl); maximum 8
runs (8 completed binary invocations at the cap, plus one killed P2 attempt
disclosed as DEV-1, wall-clock only); memory 4 GiB (max RSS observed
1654784 bytes ~= 1.58 MiB per /usr/bin/time -l; O(1) per trial; hit detail capped at 256 per
thread, hit_overflow = 0 on every receipt). Binding baseline: each 2^32
analysis arm charged 4x the ~27 min 2^30 4-thread handoff baseline; measured
hardware ran P3/P4 in 376.0/335.1 s (OPTIMISTIC-RELATIVE disclosure).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL
session model); model_verified: false; fallback_used: true (session-backend
transport under inference amendment DEC-20260831-0d1eeb); degraded_requirements:
[]; amendment: DEC-20260831-0d1eeb;
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c;
independent_session_required: true (per handoff).
