# BUILD.md — TASK-20260901-706b1d (BATCH-7b798d, GOAL-AES-003)

## Environment

- Host: Adams-MacBook-Pro.local, arm64, Darwin 25.6.0 (macOS), 14 CPUs, 48 GiB RAM.
- Python: 3.12.8 (stdlib only: json/hashlib/math/sys/datetime).
- C compiler: Apple clang version 17.0.0 (clang-1700.0.13.5), target arm64.
- Git: worktree branch `aes003-shape-batch-20260901`, HEAD
  `bf2a16216836ae6462d750b59f3f49ffa41cfd95` at session start; dirty-tree
  state = only this task's write_scope files (untracked), verified at start.
- Shell timeout wrapper: `/opt/homebrew/bin/timeout 3600` around every arm
  invocation (per handoff).

## Lineage

PIN-T0 widened derivative of the BATCH-ace664 certified cap-256 build
`coordination/goals/GOAL-AES-003/batches/BATCH-ace664/tasks/TASK-20260901-579808/src/affarm046ex.c`
(HIT_LOG_CAP 256; itself the certified Gate-0x-identity rebuild of the
BATCH-5ed9a3 cap-64 instrument and the L1-AES-R5-P30 line). The ONLY
instrument changes are the PIN-T0 widening hunks H1-H5 audited in
`runs/source_diff.txt` / `runs/source_diff_raw.txt` (pre-arm audit, PASS):
interior sbox tokens s1/s2/s4/s8/s12, the TPOS[0] SubWord schedule reload
(DEC-20260901-fb6f11), and three additive pin-label receipt fields
(schedule_pin, schedule_pin_position, schedule_pin_decision). RNG, trial loop,
round functions, existing counters, existing receipt emissions, and the
pin/pinidentity/geom/freeze modes are untouched. The copied lineage binary was
DELETED before build; the binary here is rebuilt from this source.

Support scripts:
- `gate0x_cmp.py` — rewritten fresh for this task (schema v3): compares the
  S0-4 receipt against BOTH the certified BATCH-ace664 P2_gate0x.json receipt
  (primary) and the committed L1-AES-R5-P30 receipt (continuity), under the
  extended allowed-diff list (value list inherited; additive pin-label list
  {schedule_pin, schedule_pin_position, schedule_pin_decision}). Exit 5 =>
  SH-GATE-FAIL halt.
- `freeze_digest.py` — adapted copy of the BATCH-ace664 script (cap-256 fold
  smoke assertions, as certified there). Deltas disclosed: task labels, and
  the --reverify comparison EXTENDED to cross_k_nesting, position_order, and
  the cap-independent folded-smoke selfcheck counters, as required by this
  task's contract ("digests, bijection, nestedness, cross_k_nesting ALL
  identical"). The cap-DEPENDENT selfcheck fields (hit_detail_records,
  hit_log_overflow) are NOT compared against the committed cap-64 file
  R3_table_freeze.json and are disclosed in the cmp output instead.
- `s0_analysis.py` — fresh: S0-5 dead-anchor gate (hits <= 8; tripwire >= 9
  -> SH-F6) and S0-6 ramp-zero anchor gate (hits = 2^30, W = 3 on 100% of
  nontrivial, excess ratio 1.0 exact), with Garwood 95% CIs under the
  design-time Wilson-Hilferty convention.
- `assemble_results.py` — fresh: assembles RESULTS.json from the artifacts.
- Lineage analysis scripts not consumed by S0 (crosscheck.py, dpcore.py,
  jointlr.py, power.py, xstat.py, det_cmp.py) were copied with the build and
  then DELETED to keep the artifact set exact (disclosed).

## Build command

```sh
cc -O2 -pthread -Wall -o src/affarm046ex src/affarm046ex.c
```

Compiled clean (no warnings) before any run.

## Run commands (in order; each stamped in budget_stamps.jsonl)

- S0-1 (not an invocation): write PREREGISTRATION.md BEFORE any fresh arm
  (mtime recorded in budget_stamps.jsonl).
- S0-2 (BLOCKING): `src/affarm046ex pin 363851` -> runs/S1a_pin.json;
  `src/affarm046ex pinidentity 363851` -> runs/S1b_pinidentity.json.
- S0-3 (BLOCKING): `src/affarm046ex freeze 363851` ->
  runs/S2_freeze_c_output.json; `python3 src/freeze_digest.py
  runs/S2_freeze_c_output.json runs/S2_freeze_rerun.json --reverify
  ../../../BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json
  runs/S2_freeze_cmp.json` (exit 7 => SH-GATE-FAIL halt).
- S0-4 (BLOCKING): `src/affarm046ex arm S3GATE0X-PINT0-J5-1-AES-R5-P30 5 1 1
  30 531001 1 2 aes` -> runs/S3_gate0x.json; `python3 src/gate0x_cmp.py
  runs/S3_gate0x.json
  ../../../BATCH-ace664/tasks/TASK-20260901-579808/runs/P2_gate0x.json
  ../../../BATCH-015/tasks/TASK-20260805-d408ac/runs/L1-AES-R5-P30.json
  runs/S3_gate0x_cmp.json` (exit 5 => SH-GATE-FAIL halt).
- S0-5 (DEAD ANCHOR, analyzed FIRST among reading-bearing arms):
  `src/affarm046ex arm S4DEADANCHOR-AES-R6-P30 6 1 1 30 531004 1 4 aes` ->
  runs/S4_dead_anchor.json.
- S0-6 (RAMP-ZERO ANCHOR, BLOCKING): `src/affarm046ex arm
  S5RAMPZERO-S0-R5-P30 5 1 1 30 531001 5 4 identity` -> runs/S5_rampzero.json.
- Analysis: `python3 src/s0_analysis.py runs/S4_dead_anchor.json
  runs/S5_rampzero.json runs/S4_dead_analysis.json
  runs/S5_rampzero_analysis.json` (exit 9 => SH-F6; exit 10 =>
  SH-ANCHOR-FAIL).
- Assembly: `python3 src/assemble_results.py` -> RESULTS.json.

Every arm invocation runs as:
`timeout 3600 /usr/bin/time -l <cmd> > runs/X.json 2> runs/X.timing.txt` with
`runs/X.err` created to record stderr (lineage convention).

## Budget

Declared wall clock 9000 s TOTAL (binding stop in budget_stamps.jsonl);
maximum 8 binary invocations; memory 4 GiB (lineage-observed RSS ~1.6 MiB;
O(1) per trial). Binding baseline per the handoff convention: ~27 min per
2^30 4-thread arm, ~54 min for the 2-thread Gate-0x rebuild (campaign
hardware rates 94-155 s per arm are OPTIMISTIC-RELATIVE, disclosed). Budget
exhaustion is resource_exhaustion, never a reading (rule 5).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
(session-reported; no adapter probe was executed in this session);
model_verified: false; fallback_used: true (session-backend transport under
inference amendment DEC-20260831-0d1eeb); degraded_requirements: [];
amendment: DEC-20260831-0d1eeb; independent_session_required: true (per
handoff).
