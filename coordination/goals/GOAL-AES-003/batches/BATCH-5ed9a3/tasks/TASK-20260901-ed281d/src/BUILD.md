# BUILD.md — TASK-20260901-ed281d (BATCH-5ed9a3, GOAL-AES-003)

## Environment

- Host: Adams-MacBook-Pro.local, arm64, Darwin 25.6.0 (macOS), 14 CPUs, 48 GiB RAM.
- Python: 3.12.8 (stdlib only; fractions/json/hashlib/re/subprocess/datetime).
- C compiler: Apple clang version 17.0.0 (clang-1700.0.13.5), target arm64.
- Git: worktree branch `aes003-batch026d-20260901`, HEAD
  `efe4e61dff88fa71acc3f9ea1d4fa2eecf895e26` at session start; dirty-tree state =
  only this task's write_scope files (untracked), verified at start and completion.

## Lineage

Extended derivative of the Stage-0 instrument
`coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/src/affarm046e.c`
(itself the pinned affarm046 lineage instrument for IDEA-20260901-363851 Stage 0).
The extension is EXACTLY the additive pure-read logging block preregistered in
IDEA-20260901-026d6a.logged_additions (class-wise zero-byte counters ezdiag/ezoff
over all/miss/hit splits + per-hit zero_mask_e inside HIT_LOG_CAP = 64). No trial
stream, RNG, round function, or pre-existing counter touched — audited in
runs/source_diff.txt (FX5 PASS). Support scripts copied from the Stage-0 package
and relabeled: freeze_digest.py, det_cmp.py; gate0_cmp.py -> gate0x_cmp.py with the
KNOWN_ADDED set extended by the six new counters (PREREGISTRATION.md section 5).
Analysis code written FRESH for this task: src/xstat.py (exact rational DP),
src/assemble_results.py (preregistered decision rule).

## Build command

```sh
cc -O2 -pthread -Wall -o src/affarm046ex src/affarm046ex.c
```

Compiled clean (no warnings) before any run.

## Run commands (in order; each stamped in budget_stamps.jsonl; 8 invocations = cap)

- G1 (not an invocation): write PREREGISTRATION.md BEFORE any fresh arm.
- Stage r0 (0 runs): `python3 src/xstat.py r0 <R5_r6_reference.json> <R4_gate0_j5.json>
  runs/r0_analysis.json` on the committed BATCH-2f12ac receipts; anchor analyzed
  FIRST, restatement admitted only on R0-ANCHOR-PASS.
- G2a (BLOCKING): `src/affarm046ex pin 363851` -> runs/G2a_pin.json.
- G2b (BLOCKING): `src/affarm046ex pinidentity 363851` -> runs/G2b_pinidentity.json.
- G3 (BLOCKING): `src/affarm046ex arm GATE0X-J5-1-AES-R5-P30 5 1 1 30 531001 1 2 aes`
  -> runs/G3_gate0x.json; then `python3 src/gate0x_cmp.py runs/G3_gate0x.json
  <committed L1-AES-R5-P30.json> runs/G3_gate0x_cmp.json` (exit 5 => HALT FX5).
- G4 (ANCHOR, analyzed FIRST): `src/affarm046ex arm ANCHORX-R6DEAD-AES-R6-P30 6 1 1
  30 531002 1 4 aes` -> runs/G4_anchor_r6.json; `python3 src/xstat.py arm
  runs/G4_anchor_r6.json runs/G4_anchor_analysis.json`.
- G5 (admitted ONLY because G4 passed): `src/affarm046ex arm J5-2-AES-R5-P30 5 1 1
  30 531002 1 4 aes` -> runs/G5_j5_2.json; `python3 src/xstat.py arm runs/G5_j5_2.json
  runs/G5_analysis.json`.
- G6: determinism double, IDENTICAL command twice: `src/affarm046ex arm
  DETX-AES-R5-P20 5 1 1 20 531001 1 4 aes` -> runs/G6_det_a.json, runs/G6_det_b.json;
  `python3 src/det_cmp.py runs/G6_det_a.json runs/G6_det_b.json runs/G6_det_cmp.json`.
- G7: `src/affarm046ex freeze 363851` -> runs/G7_freeze_c_output.json; `python3
  src/freeze_digest.py runs/G7_freeze_c_output.json runs/G7_freeze_rerun.json
  --reverify <committed R3_table_freeze.json> runs/G7_digest_reverify.json`;
  source-diff audit -> runs/source_diff.txt.
- Assembly: `python3 src/assemble_results.py` -> RESULTS.json (verification load
  after writing; parse attestation inside).

Timing capture: `/usr/bin/time -l <cmd> > runs/X.json 2> runs/X.timing.txt`;
`runs/X.err` created empty per arm to record the no-stderr convention.

## Budget

Declared wall clock 7200 s (binding stop in budget_stamps.jsonl); maximum 8 runs
(8 binary invocations = 7 record runs, at the cap); memory 4 GiB (max RSS observed
1.62 MiB per /usr/bin/time -l; O(1) per trial; hit detail capped at 64).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL
session model); model_verified: false; fallback_used: true (session-backend
transport under inference amendment DEC-20260831-0d1eeb); degraded_requirements:
[]; amendment: DEC-20260831-0d1eeb;
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c;
independent_session_required: true (per handoff).
