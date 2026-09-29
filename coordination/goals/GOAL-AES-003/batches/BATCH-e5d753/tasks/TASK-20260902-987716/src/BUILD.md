# BUILD.md — TASK-20260902-987716 (BATCH-e5d753, GOAL-AES-003)

## Environment

- Host: Adams-MacBook-Pro.local, Apple M4 Pro, 14 CPUs, 48 GiB RAM.
- macOS product version: 26.6 (Darwin).
- Python: 3.12.8 (stdlib only: json/hashlib/math/sys/datetime/re).
- C compiler: Apple clang version 17.0.0 (clang-1700.0.13.5), target arm64.
  NOT used this task: the frozen build is reused byte-exactly, zero source
  change, no recompilation.
- Git: worktree branch `aes003-shape2-batch-20260902`, HEAD
  `e6238a68e6359751fa184444b1dbcef3f330e676` at session start; dirty-tree
  state = only this task's write_scope files (untracked), verified at start.
- Shell timeout wrapper: `/opt/homebrew/bin/timeout 3600` around every
  binary invocation (per handoff).

## Instrument lineage (UNCHANGED)

The instrument is the BATCH-7b798d PIN-T0 widened build
(`affarm046ex`, HIT_LOG_CAP 256 per thread), copied byte-exactly from
`coordination/goals/GOAL-AES-003/batches/BATCH-7b798d/tasks/TASK-20260901-706b1d/src/`
(affarm046ex.c + affarm046ex binary). S0-2 re-verified BOTH sha256 hashes
against the BATCH-7b798d snapshot receipt
(`archives/TASK-20260901-56ecb6/snapshot-receipt.json`): exact match on
source and binary (runs/S1_buildid.json). The priced Gate-0x rebuild
fallback was therefore NOT executed. `runs/source_diff.txt` records the
empty diff (zero source change).

Support scripts (fresh for this task; NOT part of the instrument):
- `freeze_digest.py` — fresh re-derivation of the lineage freeze
  digester/reverifier. Comparison vs the committed R3_table_freeze.json
  covers digests, bijection, nestedness, cross_k_nesting, position_order,
  and the cap-independent folded-smoke selfcheck counters; the cap-DEPENDENT
  selfcheck fields (hit_detail_records, hit_log_overflow) differ by
  construction (committed file cap-64, this build cap-256) and are
  disclosed, never compared as mismatches. Exit 6/7 => SH2-GATE-FAIL halt.
- `s0_analysis.py` — fresh: per-receipt modes (dead / rampzero) so the dead
  anchor is ANALYZED BEFORE any alive reading. Implements the AMEND-1
  counter-identity suite (PREREGISTRATION.md section 2), the dead-anchor
  gate (hits <= 8; tripwire >= 9 -> SH2-F6), the ramp-zero anchor gate
  (hits = 2^30, W = 3 on 100% of nontrivial, excess ratio 1.0 exact), and
  the AMEND-1 proves-too-much control on the ramp-zero receipt. Garwood 95%
  CIs under the Wilson-Hilferty design-time convention. Exit 9 => SH2-F6;
  10 => SH2-ANCHOR-FAIL; 12 => SH2-GATE-FAIL; 11 => other consistency.
- `assemble_results.py` — fresh: assembles RESULTS.json from the artifacts.

## Run commands (in order; each stamped in budget_stamps.jsonl)

- S0-1 (not an invocation): PREREGISTRATION.md written BEFORE any binary
  invocation (mtime stamped in budget_stamps.jsonl).
- S0-2 (not an invocation): sha256 identity of src/affarm046ex.c and
  src/affarm046ex vs the BATCH-7b798d snapshot receipt -> runs/S1_buildid.json
  (PASS; priced Gate-0x fallback not executed). runs/source_diff.txt records
  the empty diff vs the lineage source.
- S0-3 (BLOCKING): `timeout 3600 /usr/bin/time -l src/affarm046ex pin 363851`
  -> runs/S2a_pin.json (stderr+time -> runs/S2a_pin.timing.txt;
  runs/S2a_pin.err created empty per lineage convention);
  `timeout 3600 /usr/bin/time -l src/affarm046ex pinidentity 363851`
  -> runs/S2b_pinidentity.json (+ .timing.txt / .err likewise).
- S0-4 (BLOCKING): `timeout 3600 /usr/bin/time -l src/affarm046ex freeze 363851`
  -> runs/S3_freeze_c_output.json (+ runs/S3_freeze.timing.txt);
  `python3 src/freeze_digest.py runs/S3_freeze_c_output.json
  runs/S3_freeze_rerun.json --reverify
  ../../../BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json
  runs/S3_freeze_cmp.json` (exit 7 => SH2-GATE-FAIL halt).
- S0-5 (DEAD ANCHOR, ANALYZED FIRST among reading-bearing arms):
  `timeout 3600 /usr/bin/time -l src/affarm046ex arm
  S05DEADANCHOR-AES-R6-P30 6 1 1 30 531004 1 4 aes` ->
  runs/S4_dead_anchor.json; then immediately
  `python3 src/s0_analysis.py dead runs/S4_dead_anchor.json
  runs/S4_dead_analysis.json` (exit 9 => SH2-F6 halt; exit 12 =>
  SH2-GATE-FAIL halt) BEFORE any alive reading is invoked.
- S0-6 (RAMP-ZERO ANCHOR, BLOCKING; only if S0-5 did not trip):
  `timeout 3600 /usr/bin/time -l src/affarm046ex arm
  S06RAMPZERO-S0-R5-P30 5 1 1 30 531001 5 4 identity` ->
  runs/S5_rampzero.json; then
  `python3 src/s0_analysis.py rampzero runs/S5_rampzero.json
  runs/S5_rampzero_analysis.json` (exit 10 => SH2-ANCHOR-FAIL halt;
  exit 12 => SH2-GATE-FAIL halt, AMEND-1 proves-too-much indictment).
- Assembly: `python3 src/assemble_results.py` -> RESULTS.json.

Stderr convention (lineage): every invocation redirects stderr into
`runs/X.timing.txt` together with the `/usr/bin/time -l` resource report;
`runs/X.err` is created as an empty placeholder file exactly as in the
BATCH-7b798d lineage (whose .err files carry the empty-file sha256).

## Budget

Declared wall clock 5400 s TOTAL for S0 (binding stop in
budget_stamps.jsonl); maximum 8 binary invocations; memory 4 GiB
(lineage-observed RSS ~1.6 MiB; O(1) per trial). Binding baseline per the
handoff convention: ~27 min per 2^30 4-thread arm, ~54 min for the 2-thread
Gate-0x rebuild (campaign hardware rates ~94-155 s per arm are
OPTIMISTIC-RELATIVE, disclosed, never charged as the baseline). Budget
exhaustion is resource_exhaustion, never a reading (rule 5).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
(session-reported; no adapter probe was executed in this session);
model_verified: false; fallback_used: true (session-backend transport under
inference amendment DEC-20260831-0d1eeb); degraded_requirements: [];
amendment: DEC-20260831-0d1eeb; independent_session_required: true (per
handoff).
