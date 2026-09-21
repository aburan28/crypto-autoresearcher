# BUILD.md — TASK-20260902-525d16 (BATCH-e5d753, GOAL-AES-003) — Stage S1

## Environment

- Host: Adams-MacBook-Pro.local, Apple M4 Pro, 14 CPUs, 48 GiB RAM.
- macOS product version: 26.6 (Darwin).
- Python: 3.12.8 (stdlib only: json/hashlib/math/sys/datetime/re/subprocess).
- C compiler: NOT used this task — the frozen build is reused byte-exactly,
  zero source change, no recompilation (AMEND-1 raised-cap option declined in
  IDEA-20260902-9e84ac integrity_gate_amend1.raised_cap_option).
- Git: worktree branch `aes003-shape2-batch-20260902`; dirty-tree state =
  only this task's write_scope files (untracked) plus the snapshot-bound S0
  package of TASK-20260902-987716; no git add/commit by this producer.
- Shell timeout wrapper: `/opt/homebrew/bin/timeout 3600` around every
  binary invocation (per handoff).

## S0 gate check (MANDATORY FIRST STEP)

Read the snapshot-bound S0 outcome FIRST:
`coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/RESULTS.json`
field `s0_outcome_ordered_cascade` = **PASS-S0**. The file's sha256
`4b43926475863a985cc15be8900223e6411b2a71b1a192eee1334e5810cd5a2c` matches the
snapshot receipt `archives/TASK-20260902-e19f39/snapshot-receipt.json` binding
for that path. No S0 halt branch fired; interior arms admitted.

## Instrument lineage (UNCHANGED)

Copied byte-exactly from the S0 re-verified frozen build at
`coordination/goals/GOAL-AES-003/batches/BATCH-e5d753/tasks/TASK-20260902-987716/src/`
(itself byte-identical to the BATCH-7b798d snapshot-bound build, S0-2):

- `src/affarm046ex.c`  sha256 `ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37`
- `src/affarm046ex`    sha256 `74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702`

Both hashes match the snapshot-bound hashes in
`TASK-20260902-987716/runs/S1_buildid.json` (verified at copy time, stamped in
budget_stamps.jsonl as `instrument_copied`). HIT_LOG_CAP = 256 per thread,
PIN-T0. The instrument was NOT modified; had any modification seemed needed,
the task would HALT and report instead (per handoff).

Support scripts (fresh for this task; NOT part of the instrument):
- `freeze_digest.py` — copied UNMODIFIED from TASK-20260902-987716/src/
  (sha256 `c29e876b76a4a4ba6cf200d36a56ae1bc8faf8c0bdacbc40df5c30024a2b2814`);
  used for the S1-7 post-arm table-freeze digest re-verification vs the
  committed R3_table_freeze.json. Exit 6/7 => SH2-GATE-FAIL halt.
- `s1_analysis.py` — fresh: per-receipt modes (reseat / grid / detcmp) so the
  k=16 re-seat is ANALYZED FIRST within S1, then k=1, k=2, k=4, k=8 (binding
  order), each immediately after its arm and before the next arm is invoked.
  Implements the AMEND-1 counter-identity suite (PREREGISTRATION.md section 2
  of TASK-20260902-987716, with the corrected zhist convention per DEV-S0-1:
  the true internal identity is sum(zhist) == nontrivial_trials,
  affarm046ex.c:458-459), the re-seat gate (band [6,30] or SH2-RESEAT-FAIL),
  per-point bands/Garwood CIs/excess ratios under the frozen excess_E = 2^30
  convention, and the overflow-positive determinism comparison modulo the
  preregistered timing strip set. Exit 12 => SH2-GATE-FAIL; 13 =>
  SH2-RESEAT-FAIL; 14 => determinism receipt realized overflow == 0 (run the
  pre-registered k=0 fallback double and re-invoke detcmp).
- `assemble_results.py` — fresh: assembles RESULTS.json and
  runs/verdict_partial.json from the artifacts.

## Run commands (in binding order; each stamped in budget_stamps.jsonl)

Seat tuples per PREREGISTRATION.md section 6 (amask=1, smask=1, threads=4,
PIN-T0; r=5; seeds 531001). Arm labels are executor-chosen receipt-echo
fields only (DEV-S0-4 precedent); stream derivation depends only on
seed/armid/thread index.

- S1-1 KNOWN-ALIVE RE-SEAT, ANALYZED FIRST within S1:
  `timeout 3600 /usr/bin/time -l src/affarm046ex arm T1K16RESEAT-AES-R5-P30 5 1 1 30 531001 8 4 aes`
  -> runs/T1_k16_reseat.json (+ .timing.txt; .err empty placeholder per
  lineage convention); then IMMEDIATELY
  `python3 src/s1_analysis.py reseat runs/T1_k16_reseat.json runs/T1_k16_analysis.json`
  (exit 13 => SH2-RESEAT-FAIL: interior readings recorded but NO verdict
  inputs admitted; exit 12 => SH2-GATE-FAIL halt) BEFORE any interior arm.
- S1-2 AMEND-1 RE-RUN primary k=1:
  `timeout 3600 /usr/bin/time -l src/affarm046ex arm T2K1-S1-R5-P30 5 1 1 30 531001 2 4 s1`
  -> runs/T2_k1.*; then `python3 src/s1_analysis.py grid 1 runs/T2_k1.json runs/T2_k1_analysis.json`
- S1-3 AMEND-1 RE-RUN k=2:
  `timeout 3600 /usr/bin/time -l src/affarm046ex arm T3K2-S2-R5-P30 5 1 1 30 531001 3 4 s2`
  -> runs/T3_k2.*; then `python3 src/s1_analysis.py grid 2 runs/T3_k2.json runs/T3_k2_analysis.json`
- S1-4 LOAD-BEARING TRANSITION LOCATOR k=4 (FIRST-EVER measurement):
  `timeout 3600 /usr/bin/time -l src/affarm046ex arm T4K4-S4-R5-P30 5 1 1 30 531001 4 4 s4`
  -> runs/T4_k4.*; then `python3 src/s1_analysis.py grid 4 runs/T4_k4.json runs/T4_k4_analysis.json`
- S1-5 AMEND-1 RE-RUN floor point k=8:
  `timeout 3600 /usr/bin/time -l src/affarm046ex arm T5K8-S8-R5-P30 5 1 1 30 531001 6 4 s8`
  -> runs/T5_k8.*; then `python3 src/s1_analysis.py grid 8 runs/T5_k8.json runs/T5_k8_analysis.json`
- S1-6 DETERMINISM DOUBLE on an overflow-positive receipt (R3), identical
  command twice:
  `timeout 3600 /usr/bin/time -l src/affarm046ex arm T6DETOVF-S1-R5-P20 5 1 1 20 531001 2 4 s1`
  -> runs/T6_det_a.* then runs/T6_det_b.*; then
  `python3 src/s1_analysis.py detcmp runs/T6_det_a.json runs/T6_det_b.json runs/T6_det_cmp.json`
  (byte-identical modulo the strip set {elapsed_seconds_measured,
  measured_rate_trials_per_sec}; counter identities on the double receipt;
  realized overflow > 0 required — exit 14 triggers the pre-registered k=0
  fallback double: `arm T6DETOVF-S0-R5-P20 5 1 1 20 531001 5 4 identity`
  twice, regime deviation recorded per rule 8).
- S1-7 post-arm digest re-verification + source-diff audit:
  `timeout 3600 /usr/bin/time -l src/affarm046ex freeze 363851`
  -> runs/T7_freeze_c_output.json (+ runs/T7_freeze.timing.txt, extra artifact
  per artifact policy); then
  `python3 src/freeze_digest.py runs/T7_freeze_c_output.json runs/T7_freeze_rerun.json --reverify ../../../BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json runs/T7_digest_reverify.json`
  (exit 7 => SH2-GATE-FAIL halt); and the post-arm source-diff audit:
  `diff` of src/affarm046ex.c vs the S0 re-verified build source + post-arm
  sha256 of source and binary vs the copy-time hashes -> must be EMPTY ->
  runs/source_diff_raw_postarm.txt.
- Assembly: `python3 src/assemble_results.py` -> RESULTS.json +
  runs/verdict_partial.json.

Stderr convention (lineage, DEV-S0-3 precedent): every invocation redirects
stderr (including the /usr/bin/time -l resource report) into
`runs/X.timing.txt`; `runs/X.err` is created as an empty placeholder file
exactly as in the BATCH-7b798d / TASK-20260902-987716 lineage.

## Budget

Declared wall clock 10000 s TOTAL for S1 (binding stop, stamped in
budget_stamps.jsonl); maximum 8 binary invocations (planned exactly 8:
5 grid arms + 2 determinism invocations + 1 post-arm freeze); memory 4 GiB
(lineage-observed RSS ~1.6 MiB; O(1) per trial). Binding baseline per the
handoff convention: ~27 min per 2^30 4-thread arm (S0 measured 78.7-95.2 s on
this host — OPTIMISTIC-RELATIVE, disclosed, never charged as the baseline).
Budget exhaustion is resource_exhaustion, never a reading (rule 5). The
pre-registered k=0 determinism fallback (if triggered) would require 2
additional invocations beyond the 8-invocation cap; that contingency is
reported as a budget/contingency event, not absorbed silently (predicted
probability ~ e^-12400, effectively zero).

## Scope discipline

Toy tier. No deployed-AES claims. No published-cryptanalysis comparisons in
either direction. NO X statistic, NO rho-exclusion, NO k=3/5/6, NO k=12, NO
third seeds, NO 2^32 arms, NO second seeds (S2 belongs to
TASK-20260902-c33c1f), NO SH2 verdict composition (branch 5 requires the S2
second seeds; verdict_partial.json records readings and the branches
evaluated so far only). No git add/commit. No status/strength/promotion
interpretation — observations only.

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
(session-reported; no adapter probe was executed in this session);
model_verified: false; fallback_used: true (session-backend transport under
inference amendment DEC-20260831-0d1eeb); degraded_requirements: [];
amendment: DEC-20260831-0d1eeb; independent_session_required: true (per
handoff).
