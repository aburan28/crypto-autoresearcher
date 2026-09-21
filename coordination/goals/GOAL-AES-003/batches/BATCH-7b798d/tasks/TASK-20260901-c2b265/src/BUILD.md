# BUILD.md — TASK-20260901-c2b265 (BATCH-7b798d, GOAL-AES-003) — Stage S1

## Environment

- Host: Adams-MacBook-Pro.local, arm64, Darwin 25.6.0 (macOS), 14 CPUs, 48 GiB RAM.
- Python: 3.12.8 (stdlib only: json/hashlib/math/sys/datetime).
- Git: worktree branch `aes003-shape-batch-20260901`, HEAD
  `8f1823eb3de5e01f9de27c45ad0aaa932ed305f5` at session start (S0 snapshot
  a1cc0a107 already bound); clean tree at start (all S0 artifacts committed).
- Shell timeout wrapper: `/opt/homebrew/bin/timeout 3600` around every arm
  invocation (per handoff).

## Instrument (REUSED UNMODIFIED — no rebuild, no source change)

Copied byte-exact from the S0 task (the snapshot-bound PIN-T0 widened build,
HIT_LOG_CAP 256):

- source: `../TASK-20260901-706b1d/src/affarm046ex.c`
  sha256 `ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37`
- binary: `../TASK-20260901-706b1d/src/affarm046ex`
  sha256 `74e3d65ca6ecdd877dda5d9e19a96a5af66740b118dbcd1dd35b78be5d102702`

My `src/` copies are identical to the S0 originals at copy time (hashes
above match both sides). The S1-6 post-arm source-diff audit re-checks this
byte-exactness AFTER all arms (must be EMPTY). No modification of the
instrument was needed or made; had any seemed needed the task contract says
HALT and report.

Support scripts:
- `s1_analysis.py` — fresh: per-point S1 analysis (hits, W breakdown, excess
  ratio vs frozen excess_E = 2^30 comparator convention EV-AES-ec53f1, run-
  internal analytic null, Garwood 95% CI under the design-time Wilson-
  Hilferty chi-squared quantile convention of IDEA-20260901-582ea9, frozen
  bands of PREREGISTRATION.md section 1, seat/consistency checks, re-seat
  band [6,30] gate for k=16, hit_log_overflow=0 gate for every analysis-
  bearing receipt).
- `det_cmp.py` — fresh: determinism-double comparator following the
  BATCH-ace664 P5 convention (byte-identity of the two receipts modulo the
  preregistered timing strip set {elapsed_seconds_measured,
  measured_rate_trials_per_sec}).
- `freeze_digest.py` — REUSED UNMODIFIED from the S0 task src/ (itself the
  adapted BATCH-ace664 script with the extended cap-independent reverify),
  for the S1-6 post-arm digest re-verification of R3_table_freeze.json. Its
  embedded task_id/idea_record labels name the S0 task; that is disclosed
  here and in the reverify output rather than modified (instrument-adjacent
  scripts are reused as-is per the handoff's no-modification rule; the
  comparison semantics are identical).
- `verdict.py` — fresh: ordered SH cascade composition
  (PREREGISTRATION.md section 5, fixed order, precedence clause).
- `assemble_results.py` — fresh: assembles RESULTS.json from the artifacts.

## Run commands (in order; each stamped in budget_stamps.jsonl)

Every arm invocation runs as:
`timeout 3600 /usr/bin/time -l <cmd> > runs/X.json 2> runs/X.timing.txt`
with `runs/X.err` created to record program stderr (lineage convention;
stderr is captured in the timing file by /usr/bin/time -l, so .err stays
empty unless the program itself fails before/around time).

- S1-1 (ANALYZED FIRST within S1): `src/affarm046ex arm T1-K16RESEAT-R5-P30
  5 1 1 30 531001 8 4 aes` -> runs/T1_k16_reseat.json; band [6,30] or
  SH-RESEAT-FAIL.
- S1-2: `src/affarm046ex arm T2-K1-R5-P30 5 1 1 30 531001 2 4 s1` ->
  runs/T2_k1.json (primary shape joint).
- S1-3: `src/affarm046ex arm T3-K2-R5-P30 5 1 1 30 531001 3 4 s2` ->
  runs/T3_k2.json (step confirmation).
- S1-4: `src/affarm046ex arm T4-K8-R5-P30 5 1 1 30 531001 6 4 s8` ->
  runs/T4_k8.json (midpoint/sentinel).
- S1-5: `src/affarm046ex arm T5-DETX256-AES-R5-P20 5 1 1 20 531001 1 4 aes`
  twice -> runs/T5_det_a.json, runs/T5_det_b.json (determinism double at
  log2N=20, threads=4, seed 531001; seat follows the BATCH-ace664 P5
  lineage convention: aes seat, armid 1 — the handoff fixes log2N/threads/
  seed/build but not the seat; lineage convention used and disclosed).
- S1-6: `src/affarm046ex freeze 363851` -> runs/T6_freeze_c_output.json;
  `python3 src/freeze_digest.py runs/T6_freeze_c_output.json
  runs/T6_freeze_rerun.json --reverify
  ../../../BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs/R3_table_freeze.json
  runs/T6_digest_reverify.json`; `diff -u
  ../TASK-20260901-706b1d/src/affarm046ex.c src/affarm046ex.c >
  runs/source_diff_raw_postarm.txt` (must be EMPTY).
- Verdict: `python3 src/verdict.py` -> runs/verdict_composition.json (only
  after ALL interior points read; fixed cascade order).
- Assembly: `python3 src/assemble_results.py` -> RESULTS.json.

Binary invocations planned: 7 (T1, T2, T3, T4, T5a, T5b, freeze) of 8 max.
No other binary invocations are made (no usage probes; the CLI was read
from source and from the S0 run record).

## Budget

Declared wall clock 7200 s TOTAL; maximum 8 binary invocations; memory 4 GB.
Binding baseline per the handoff convention: ~27 min per 2^30 4-thread arm
(campaign hardware rates 78-164 s per arm measured by S0 are
OPTIMISTIC-RELATIVE, disclosed). Budget exhaustion is resource_exhaustion,
never a reading (rule 5).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
(session-reported; no adapter probe was executed in this session);
model_verified: false; fallback_used: true (session-backend transport under
inference amendment DEC-20260831-0d1eeb); degraded_requirements: [];
amendment: DEC-20260831-0d1eeb; independent_session_required: true (per
handoff).
