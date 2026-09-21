# PREREGISTRATION -- TASK-20260901-e2e66e (BATCH-803af6, GOAL-AES-003)

Battery arm **B4 -- EXCLUSION-TOGGLE AUDIT** of IDEA-20260901-02f7c4, executed ONLY.
Written BEFORE any run output exists in this task directory (mtime-gated).
Frozen spec: `ledger/proposals/IDEA-20260901-02f7c4.yaml`. Frozen contract: task card
TASK-20260901-e2e66e in `coordination/goals/GOAL-AES-003/batches/BATCH-803af6/dispatch_queue.json`.

Toy tier. The cipher is a FIXTURE; the object under test is the pipeline's trivial-trial
exclusion. An excess where the prediction says null is an artifact indictment, never a
discovery (record's lossy_projection_test sharp edge). No hypothesis status, evidence
strength, or promotion interpretation in any deliverable of this task.

## 1. Verbatim from the idea record (frozen predictions)

### B4 design (record `object` field, battery B4)

> B4 EXCLUSION-TOGGLE AUDIT - one AES r=5 arm and one null-object arm, each run in two
> builds: the standard build with the trivial-trial exclusion enabled, and a build with it
> deliberately disabled. Pre-registered exact prediction: disabling raises the W>=1 count by
> exactly the number of trivial trials (expected ~N x 2^-32 at |S|=1, each forcing W=3), so
> the signed delta verifies the exclusion logic arithmetically rather than by code reading
> alone.

### PR-4 (record `predictions`)

> - id: PR-4
>   metric: B4 - signed W>=1 count delta between exclusion-disabled and exclusion-enabled
>   builds, on one AES r=5 arm and one null arm
>   direction: different
>   minimum_effect: Delta equals the identified trivial-trial count exactly, trial-by-trial,
>   on both arms (the trivial trials force W=3, so each contributes exactly one W>=1 event
>   when included). Any other delta indicts the exclusion implementation.

### C4 (record `claim`)

> (C4) B4 PASS. The exclusion-toggle delta equals the trivial-trial count on both arms,
> within exact arithmetic (the trivial trials are identifiable in the raw receipts, so the
> delta is checkable trial-by-trial, not just in expectation).

### F3 (record `falsification_conditions`)

> F3 (B4 FAILURE). The exclusion-toggle delta differs from the identified trivial-trial
> count. The exclusion logic is wrong in at least one build; every arm in the campaign that
> relied on the exclusion is potentially miscounted at the ~2^-32 level; repair dispatched;
> recorded as an instrument defect with the signed delta and the trial-level audit trail.

### Decision-rule fragments that bind this task (record `preregistered_decision_rule`)

> B4 failure -> exclusion defect -> repair, then re-run the affected arms of whichever ideas
> already ran. Budget halts are resource_exhaustion, never passes.

> Timeouts, crashes and infrastructure failures are never negative mathematical evidence
> (rule 5), and in this record they are additionally never PASSes. (`interpretation_limits`)

## 2. The exclusion toggle -- location, identified and cited

Instrument: `rc8probe_freshfeistel.c`, built by TASK-20260805-d408ac (BATCH-015),
`coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/src/rc8probe_freshfeistel.c`.
Its harness machinery (including the trivial-swap exclusion) is disclosed in that file's
header (lines 23-29) as copied from `rc8probe.c` (BATCH-007, TASK-20260803-e55757).

The exclusion lives in `worker()`'s trial loop and consists of TWO conditional branches:

1. **Word-count gate** -- BATCH-015 `rc8probe_freshfeistel.c:441`:
   `if(z){ W++; if(!trivial) J->wword[j]++; }`
   (a trivial trial's zero-W-words do not enter the per-word hit counts)
2. **Trial skip** -- BATCH-015 `rc8probe_freshfeistel.c:443`:
   `if(trivial){ J->trivial++; continue; }`
   (a trivial trial is counted as trivial, then skipped: it does not enter `whist`,
   `wge1`, or the hit log)

Triviality is decided at BATCH-015 `rc8probe_freshfeistel.c:421-428`: a trial is trivial
iff `c0[i] == c1[i]` on every byte of the smask-selected CW diagonals (the swap region),
i.e. the yoyo swap is a no-op for that trial.

Lineage confirmation (BATCH-014 instrument, read per task read_scope):
`coordination/goals/GOAL-AES-003/batches/BATCH-014/tasks/TASK-20260805-b95720/src/rc8probe_feistel.c`
carries the identical structure at lines 196 and 198 (same two branches), confirming the
toggle's location is stable across the campaign harness lineage.

## 3. Build plan

Two builds from two source files derived from the BATCH-015 instrument:

- `src/rc8probe_b4_on.c`  -- `#define EXCLUDE_TRIVIAL 1` (standard campaign build, exclusion ENABLED)
- `src/rc8probe_b4_off.c` -- `#define EXCLUDE_TRIVIAL 0` (audit build, exclusion DISABLED)

The toggle is applied at exactly the two exclusion sites (and nowhere else):

- word-count gate becomes `if(z){ W++; if(!EXCLUDE_TRIVIAL || !trivial) J->wword[j]++; }`
- trial skip becomes `if(trivial){ J->trivial++; <trivial-index log>; if(EXCLUDE_TRIVIAL) continue; }`

With `EXCLUDE_TRIVIAL=1` the counting behavior is byte-identical to the standard campaign
build; this is verified by the equivalence gate of section 5, not asserted.

RECEIPT AUGMENTATION, APPLIED IDENTICALLY TO BOTH BUILDS (so that trivial trials are
individually identifiable in the raw receipts -- the record's confounders field requires
this: "a receipt format that does not identify trivial trials makes B4 a new run rather
than a toggle -- verified before promising"):

- per-thread log of trivial-trial indices with their computed W value (cap 64/thread,
  overflow counter), emitted as `trivial_trials: [[thread, t, W], ...]`;
- hit-log entries gain the trial's W value: `hit_trials: [[thread, t, W], ...]`;
- receipt fields `exclude_trivial_build` (1/0), `trivial_log_cap`, `trivial_log_overflow`.

These augmentations are present in BOTH sources verbatim; they are shared instrumentation,
not a build difference. The audit requirement "the DISABLED build differs ONLY in the
exclusion flag" is checked by `diff` of the two sources and documented in
`src/INDEPENDENCE_AUDIT.md`; the expected diff is exactly the one `#define EXCLUDE_TRIVIAL`
line (plus the file-self-identifying comment token described there).

Build: `cc -O3 -pthread -o <bin> <src> -lm` (Apple clang 17.0.0, arm64-apple-darwin,
same toolchain as BATCH-015's recorded build).

## 4. Arms, exposure, budget, commands

Campaign-standard arm spec of this seat (BATCH-015 L1/M1, frozen comparator P1-R5-PAIR of
EV-AES-e4c091 OBS-B9-3): `amask=1 smask=1 seed=531001 armid=1 threads=2`. B4 uses exactly
this spec so the ENABLED builds can be checked field-by-field against the committed
immutable receipts (section 5). Threads=2 matches the comparator seat and preserves
determinism; 8 threads were permitted by the task card but are not needed at measured rates.

EXPOSURE: **2^30** all four arms. Basis: the record's B4 description says "the audit uses
the campaign's standard exposure", and 2^30 is the campaign-standard exposure of this
comparator seat (P1-R5-PAIR, L1-AES-R5-P30, M1-FF-P30); the task card default is also 2^30.
Expected trivial-trial count at 2^30 is ~2^30 x 2^-32 = 0.25 per arm; the record's own
minimal_test accepts the low-trivial regime ("the prediction is zero-or-one trivial trials
and the delta must match exactly"). POWER DISCLOSURE (pre-registered): if an arm realizes
zero trivial trials, its signed-delta check passes exactly but vacuously (0 = 0), and this
will be reported as a power limitation of that arm's audit, not smoothed over.
FALLBACK (pre-registered): if measured rates on this machine force it, exposure drops to
2^28 (explicitly sufficient per the record's minimal_test) and actual exposure is reported
honestly. Budget halts are resource_exhaustion, never passes.

NULL OBJECT ARM: the fresh-key-per-trial 16-round SipRound-Feistel oracle
(`freshfeistel`) of the BATCH-015 instrument -- the campaign's O(1)-memory
ideal-APPROXIMATING null object of this instrument lineage (its null reading is committed:
M1-FF-P30 read 1 hit at 2^30, OUTCOME-A'', TASK-20260805-d408ac). SCOPE DISCLOSURE: this is
the ideal-approximating null, not the perm128 lazily-sampled ideal permutation of
EV-AES-e4c091 OBS-B9-2 (that oracle lives in a different instrument lineage, outside this
task's read_scope, and cannot be expressed as "two builds differing only in the exclusion
flag" of this instrument). The B4 delta arithmetic is oracle-independent: triviality is a
property of the ciphertext pair under the swap, so the audit applies to the exclusion logic
itself; which null object instantiates the null arm is stated here, not hidden.

Run budget: wall_clock 3600 s, memory 4 GB, MAXIMUM 6 runs (a run = one binary invocation,
per TASK-20260805-d408ac's counting convention; the analysis script is arithmetic on
already-written run JSONs, not a run). Planned runs, in order:

| # | run id      | command (binary in src/)                                                        | purpose |
|---|-------------|----------------------------------------------------------------------------------|---------|
| 1 | SMOKE-B4-ON-2p20  | `rc8probe_b4_on  arm SMOKE-B4-ON-2p20  aes 5 1 1 20 531001 1 2`             | build sanity, receipt parse, rate measurement |
| 2 | SMOKE-B4-OFF-2p20 | `rc8probe_b4_off arm SMOKE-B4-OFF-2p20 aes 5 1 1 20 531001 1 2`             | cross-build stream-identity + delta arithmetic at 2^20 |
| 3 | B4-AES-ON-P30  | `rc8probe_b4_on  arm B4-AES-ON-P30  aes          5 1 1 30 531001 1 2` | AES r=5 arm, exclusion ENABLED |
| 4 | B4-AES-OFF-P30 | `rc8probe_b4_off arm B4-AES-OFF-P30 aes          5 1 1 30 531001 1 2` | AES r=5 arm, exclusion DISABLED |
| 5 | B4-FF-ON-P30   | `rc8probe_b4_on  arm B4-FF-ON-P30   freshfeistel 0 1 1 30 531001 1 2` | null arm, exclusion ENABLED |
| 6 | B4-FF-OFF-P30  | `rc8probe_b4_off arm B4-FF-OFF-P30  freshfeistel 0 1 1 30 531001 1 2` | null arm, exclusion DISABLED |

Every run wrapped in `/usr/bin/time -l`, stdout -> `runs/<id>.json`, timing ->
`runs/<id>.timing.txt`, stderr -> `runs/<id>.err`. No run may start after the binding stop
(2026-09-01T18:19:18Z per budget_stamps.jsonl); halting at the stop is full compliance.

Determinism statement: per-thread plaintext/key streams are deterministic functions of
(seed, armid, thread index, thread count); jobs are per-thread with no shared mutable
state; aggregate counters are order-independent sums. Enabled and disabled runs of one arm
use IDENTICAL (seed, armid, threads, log2N), hence traverse identical trial streams.

## 5. Equivalence gate for the ENABLED builds (pre-registered, from committed immutable receipts)

Source receipts (read directly this session, before any run):
`.../BATCH-015/tasks/TASK-20260805-d408ac/runs/L1-AES-R5-P30.json` and `.../M1-FF-P30.json`
(reproducing frozen comparator P1-R5-PAIR of EV-AES-e4c091 OBS-B9-3 / BATCH-009).

ENABLED AES arm (B4-AES-ON-P30) must reproduce L1-AES-R5-P30 field-by-field:
- thread_seeds `[11400714758317678269, 4354685486758533762]`
- plaintext_stream_digest `["de8dee29c9310a13", "01089d650f48ca1b"]`
- trivial_swaps_excluded 0, nontrivial_trials 1073741824, W_ge1 14
- whist `[1073741810, 14, 0, 0, 0]`, W_ge1_by_word `[4, 4, 2, 4]`
- hit (thread,t) pairs exactly the 14 committed indices:
  `[0,52735906],[0,178745786],[0,266298850],[0,273520598],[0,339544647],[0,523527834],`
  `[1,67724771],[1,90384281],[1,147208629],[1,286947500],[1,336820358],[1,440575768],`
  `[1,451495737],[1,490333025]`
  (this receipt's hit entries carry an extra W element; the gate compares (thread,t))

ENABLED FF arm (B4-FF-ON-P30) must reproduce M1-FF-P30 field-by-field:
- plaintext_stream_digest as above; key_stream_digest `["160833933c3e4152","b928f0e742831efe"]`
- trivial 0, W_ge1 1, whist `[1073741823, 1, 0, 0, 0]`, W_ge1_by_word `[1, 0, 0, 0]`
- hit (thread,t) exactly `[[1, 270788492]]`

If an ENABLED build fails this gate, the toggle is NOT minimal (the audit build modified
standard behavior) -- HALT the audit, report as implementation failure (rule 5; never a
C4 verdict), and do not proceed to the OFF arms' interpretation.

## 6. Exact arithmetic predictions (pre-registered; checked trial-by-trial per arm)

For each arm X in {AES, FF}, with ON = enabled build run, OFF = disabled build run, and
T_X the trivial-trial count:

P1. stream identity: `plaintext_stream_digest(ON) == plaintext_stream_digest(OFF)`
    (and `key_stream_digest` equal for FF).
P2. trivial count identity: `trivial_swaps_excluded(ON) == trivial(OFF) == T_X`
    (both builds detect triviality identically; the flag only changes what is done with it).
P3. signed W>=1 delta: `W_ge1(OFF) - W_ge1(ON) == T_X` exactly.
P4. trial-by-trial set identity: hit (thread,t) sets satisfy `hits(ON) subset hits(OFF)`
    and `hits(OFF) \ hits(ON) == trivial_trials_X` exactly (as sets of (thread,t));
    every logged trivial trial has `W == 3`.
P5. histogram identity: `whist(OFF)[3] - whist(ON)[3] == T_X`; `whist(OFF)[k] == whist(ON)[k]`
    for k != 3 (each trivial trial forces W=3 at amask=1: the swap is a no-op, so
    q0=p0, q1=p1, d=p0^p1 is supported exactly on the one resampled PW diagonal and
    nonzero there, leaving exactly three all-zero PW diagonals).
P6. per-word identity: `W_ge1_by_word(OFF) - W_ge1_by_word(ON) == [0, T_X, T_X, T_X]`
    (amask=1 resamples PW diagonal 0; the three zero diagonals of a trivial trial are 1,2,3).
P7. accounting: `sum(whist(OFF)) == 2^30` (OFF counts every trial); `sum(whist(ON)) == 2^30 - T_X`.

**C4 verdict rule (from the record): C4 PASS iff P3 holds exactly on BOTH arms, with P4's
trial-by-trial identity satisfied on both arms. Any other delta is F3 (exclusion defect,
artifact indictment, recorded with the signed delta and trial-level audit trail). P1-P2 and
P5-P7 are supporting identities; a mismatch confined to them while P3/P4 hold is recorded
as an unexpected observation and investigated in the analysis, never silently absorbed.**

## 7. Deviations

Any deviation from this document or the frozen spec is recorded in RESULTS.json with its
reason (constraint of the task card), never silently absorbed.

## 8. Inference block

- policy: executor-implementation
- requested_policy: executor-implementation
- resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
- model_verified: false
- fallback_used: true (session-backend transport under inference amendment DEC-20260831-0d1eeb)
- degraded_requirements: []
- amendment: DEC-20260831-0d1eeb
- standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
