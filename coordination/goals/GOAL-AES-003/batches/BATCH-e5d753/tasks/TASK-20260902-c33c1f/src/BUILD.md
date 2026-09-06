# BUILD.md — TASK-20260902-c33c1f (BATCH-e5d753, GOAL-AES-003)

## Environment

- Host: Adams-MacBook-Pro.local, Apple M4 Pro (Darwin), same campaign host as
  S0/S1 of this batch.
- Python: 3.12.8 (stdlib only: json/hashlib/math/sys/datetime).
- C compiler: NOT used this task — the frozen build is reused byte-exactly,
  zero source change, no recompilation.
- Git: worktree branch `aes003-shape2-batch-20260831` (branch
  `aes003-shape2-batch-20260902`), dirty-tree state = only this task's
  write_scope files (untracked).
- Shell timeout wrapper: `timeout 3600` around every binary invocation (per
  handoff).

## Instrument lineage (UNCHANGED)

The instrument is the re-verified frozen build at
`coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/src/`
(`affarm046ex`, HIT_LOG_CAP 256 per thread), copied byte-exactly into this
task's `src/` and sha256-verified against the snapshot-bound hashes carried by
TASK-20260902-525d16/RESULTS.json build_provenance (which matched the
BATCH-7b798d snapshot receipts): exact match on source, binary, and
freeze_digest.py. Instrument UNMODIFIED; not recompiled.

Support scripts (fresh for this task; NOT part of the instrument):
- `s2_analysis.py` — fresh: per-receipt mode (seed2) for the two second-seed
  arms. Implements the AMEND-1 counter-identity suite (PREREGISTRATION.md
  section 2; SAME encoding as the S0/S1 analysis scripts including the
  DEV-S0-1 corrected zhist convention), the seat checks under the corrected
  ascending-listing convention (DEV-S1-1), Garwood 95% CIs under the
  Wilson-Hilferty design-time convention, and the frozen bands. Exit
  12 => SH2-GATE-FAIL.
- `verdict_composition.py` — fresh: evaluates the full ordered 10-branch SH2
  cascade from ALL readings (S0 gates/anchors, S1 grid + gates, S2 second
  seeds) exactly as preregistered, writes runs/verdict_composition.json.
- `assemble_results.py` — fresh: assembles RESULTS.json from the artifacts.

## S1 gate check (MANDATORY FIRST STEP)

Read TASK-20260902-525d16/RESULTS.json and runs/verdict_partial.json
(snapshot-bound under archives/TASK-20260902-4be096; sha256 of the read
RESULTS.json == snapshot-bound hash e0df2b62...). S0 outcome PASS-S0; S1
branches 1-4 (SH2-GATE-FAIL, SH2-F6, SH2-ANCHOR-FAIL, SH2-RESEAT-FAIL) all
NOT_FIRED; no halt/indictment branch fired -> PROCEED to S2 arms.

## Run commands (in order; each stamped in budget_stamps.jsonl)

- S2-1 (second seed k=1): `timeout 3600 /usr/bin/time -l src/affarm046ex arm
  U1K1-SS-R5-P30 5 1 1 30 531002 9 4 s1` -> runs/U1_k1_seed2.json
  (stderr+time -> runs/U1_k1_seed2.timing.txt; runs/U1_k1_seed2.err created
  empty per lineage convention); then immediately
  `python3 src/s2_analysis.py seed2 1 runs/U1_k1_seed2.json
  runs/U1_k1_seed2_analysis.json` (exit 12 => SH2-GATE-FAIL halt on this
  receipt).
- S2-2 (second seed k=4): `timeout 3600 /usr/bin/time -l src/affarm046ex arm
  U2K4-SS-R5-P30 5 1 1 30 531002 4 4 s4` -> runs/U2_k4_seed2.json (+ .timing
  / .err likewise); then
  `python3 src/s2_analysis.py seed2 4 runs/U2_k4_seed2.json
  runs/U2_k4_seed2_analysis.json`.
- Verdict: `python3 src/verdict_composition.py` ->
  runs/verdict_composition.json (composed ONLY after both second seeds are
  read, under the fixed cascade order).
- Assembly: `python3 src/assemble_results.py` -> RESULTS.json.

Run labels (U1K1-SS-R5-P30, U2K4-SS-R5-P30) are executor-chosen
receipt-echo fields only (lineage DEV-S1-4); stream derivation depends only
on seed/armid/thread index.

Stderr convention (lineage DEV-S0-3/DEV-S1-2): every invocation redirects
stderr into `runs/X.timing.txt` together with the `/usr/bin/time -l` resource
report; `runs/X.err` is created as an empty placeholder file exactly as in
the BATCH-7b798d / S0 / S1 lineage.

## Budget

Declared wall clock 4400 s TOTAL for S2 (binding stop in
budget_stamps.jsonl); maximum 4 binary invocations (2 planned); memory 4 GiB
(lineage-observed RSS ~1.6 MiB; O(1) per trial). Binding baseline per the
handoff convention: ~27 min per 2^30 4-thread arm (campaign hardware rates
~78-86 s per arm in S1 are OPTIMISTIC-RELATIVE, disclosed, never charged as
the baseline). Budget exhaustion is resource_exhaustion, never a reading
(rule 5).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
(session-reported; no adapter probe was executed in this session);
model_verified: false; fallback_used: true (session-backend transport under
inference amendment DEC-20260831-0d1eeb); degraded_requirements: [];
amendment: DEC-20260831-0d1eeb; independent_session_required: true (per
handoff).
