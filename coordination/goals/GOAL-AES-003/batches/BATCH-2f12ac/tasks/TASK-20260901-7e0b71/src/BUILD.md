# BUILD.md — TASK-20260901-7e0b71 (BATCH-2f12ac, GOAL-AES-003)

## Environment

- Host: Adams-MacBook-Pro.local, arm64, Darwin 25.6.0 (macOS 26.6), 14 CPUs, 48 GiB RAM.
- Python: 3.12.8 (stdlib only; no third-party imports anywhere in this task).
- C compiler: Apple clang version 17.0.0 (clang-1700.0.13.5), target arm64.
- Git: worktree branch `aes003-batch2f12ac-20260901`, HEAD
  `17fa491fb231eb1dfb702c5b2c255ea0a7c6ac22` at session start; dirty-tree state = only this
  task's write_scope files (verified at start, 0 other modifications).

## Lineage

Instrumented derivative of `coordination/goals/GOAL-AES-003/batches/BATCH-fe0bdc/tasks/
TASK-20260901-f5d3a4/src/affarm046.c` (the pinned affarm046 lineage), whose round-function
expressions are expression-identical to the campaign build BATCH-b41ba9 probe_sbox.c and
whose arm conventions follow BATCH-015 rc8probe_freshfeistel.c (stream-identical at equal
seats, per IDEA-20260901-363851 assumptions, source-read this session). Reporting fields
needed for the Gate-0 field-by-field match are ported expression-identically from
rc8probe_freshfeistel.c: FNV-1a 64 plaintext-stream digest (init 1469598103934665603,
prime 1099511628211, over 8-byte LE words of (p0,p1)), hit log (cap 64, in-thread indices,
`hit_trials_logged` = thread-0 count quirk), key_stream_seeds (constants 0x517CC1B727220A95,
0x6A09E667F3BCC908), stream-gap arithmetic (Newton inverse of the splitmix64 step), and
`null_expectation_analytic` = (N - trivial)*4/2^32 at %.10f.

## Build command

```sh
cc -O2 -pthread -Wall -o src/affarm046e src/affarm046e.c
```

Compiled clean (no warnings) before any run. SHA-256 core validated against Python hashlib
on three vectors ("abc", empty, 4096-byte multi-block) before use (build-phase test, not a
run; test file under /tmp, outside write_scope by design).

## Pre-run convention verification (build phase, not runs)

The committed receipt's stream/key fields were recomputed in Python from the pinned formulas
and match L1-AES-R5-P30 exactly: thread_seeds [11400714758317678269, 4354685486758533762],
key_stream_seeds [4284374398386231716, 9614918541733233340], key_hex
bdf3823182ad657dab3d556b3886ba72 (seed 531001, armid 1).

## Run commands (in order; each stamped in budget_stamps.jsonl; 7 record runs / 8 invocations = cap)

- R1 (BLOCKING): `src/affarm046e pin 363851` -> runs/R1_pin.json (+.timing.txt/.err).
- R2 (BLOCKING): `src/affarm046e pinidentity 363851` -> runs/R2_pinidentity.json.
- R3: `src/affarm046e freeze 363851` -> C output -> `python3 src/freeze_digest.py
  runs/R3_freeze_c_output.json runs/R3_table_freeze.json` (folded smoke self-checks inside;
  preregistered assertions applied by the script).
- R4 (GATE 0, BLOCKING): `/usr/bin/time -l src/affarm046e arm GATE0-J5-1-AES-R5-P30 5 1 1 30
  531001 1 2 aes` -> runs/R4_gate0_j5.json; then `python3 src/gate0_cmp.py
  runs/R4_gate0_j5.json <committed L1-AES-R5-P30.json> runs/R4_gate0_cmp.json`.
  Exit 5 => HALT F4/invalid_measurement.
- R5: `/usr/bin/time -l src/affarm046e arm R6DEAD-REF-AES-R6-P30 6 1 1 30 531001 1 4 aes`
  -> runs/R5_r6_reference.json. Hits >= 9 => HALT, report for F6 escalation.
- R6: determinism double, identical command line twice:
  `/usr/bin/time -l src/affarm046e arm DET-AES-R5-P20 5 1 1 20 531001 1 4 aes` ->
  runs/R6_det_a.json and runs/R6_det_b.json; `python3 src/det_cmp.py runs/R6_det_a.json
  runs/R6_det_b.json runs/R6_det_cmp.json`.
- R7: re-run freeze + `python3 src/freeze_digest.py runs/R7_freeze_c_output.json
  runs/R7_freeze_rerun.json --reverify runs/R3_table_freeze.json runs/R7_digest_reverify.json`.
- Analysis (not a run): `python3 src/decision_analysis.py runs/decision_analysis.json`.

Timing capture: `/usr/bin/time -l <cmd> > runs/X.json 2> runs/X.timing.txt`; program stderr
merges into the timing file on failure (a failed run's JSON then will not parse — itself the
failure signal); `runs/X.err` created empty per arm to record the no-stderr convention.

## Interior-k arm surface decision (disclosed, Stage-0 scope)

The frozen family's tables for ALL k in {0,1,2,4,8,12,16} are built, checked, and digested
by the freeze mode. ARM runs at interior k in {1,2,4,8,12} are REFUSED by this Stage-0 build:
the pinned co-variation convention ("SubWord uses the current global SBOX") names a single
global table for the key schedule, which is undefined for position-dependent S_k until the
Coordinator pins which table SubWord uses at interior points. This is a Stage-1 question for
the dispatching Coordinator, not resolvable by executor choice; Stage 0 runs no interior arm,
so nothing in this batch depends on it. k=0 and k=16 arm seats are fully surfaced (both
endpoints are exactly the committed receipts' conventions).

## Determinism

The arm receipt is a deterministic function of (name, rounds, amask, smask, log2N, seed,
arm_id, threads, table): per-thread splitmix64 streams with the campaign seed formula,
trial partition N/nthr with the remainder on thread 0, sequential aggregation in thread
order. Different thread counts change the stream partition (documented, not claimed
identical). R6 verifies byte-identity modulo the two timing fields.

## Budget

Declared wall clock 7200 s (binding stop in budget_stamps.jsonl); maximum 8 runs
(7 record runs; R6 = two invocations; 8 binary invocations total = cap); memory budget
4 GiB (O(1) per trial; histograms only; hit detail capped at 64).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model);
model_verified: false; fallback_used: true (session-backend transport under inference
amendment DEC-20260831-0d1eeb); degraded_requirements: []; amendment: DEC-20260831-0d1eeb;
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c.
