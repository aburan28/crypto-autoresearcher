# PREREGISTRATION — TASK-20260901-92672b (BATCH-7939d0, GOAL-AES-003, RC-D round-count decay check)

**This file is written BEFORE any run output exists.** Creation order in this
task directory: `budget_stamps.jsonl` (opening stamp) → this file →
`src/rc8probe_feistel_rk.c` + `src/BUILD.md` + `src/INDEPENDENCE_AUDIT.md` +
`src/analysis_rk.py` → builds → runs. The mtime of this file must predate the
mtime of every file under `runs/`; this is checked and recorded in
`RESULTS.json` before the task finishes.

**Toy tier.** Everything below concerns a reduced-round AES-shaped SPN probe
geometry (the frozen `P1-R5-PAIR` reading from BATCH-009, as verified
field-by-field by BATCH-015's `L1-AES-R5-P30`) against round-count variants of
BATCH-014's keyed deterministic Feistel toy oracle, at exposures up to 2^30
trials on one machine. Nothing here is about full-round or deployed AES, and
no comparison to published cryptanalysis is made in either direction.

---

## 0. What this task is and is not

This task tests whether BATCH-014's finding — the r=5 yoyo excess is ABSENT
under RC-D's keyed deterministic 16-round Feistel substitute at matched 2^30
exposure (M1-FEISTEL-P30: 0 hits vs the frozen comparator's 14) — depends on
the specific round count 16, or holds across the round-count axis of that
construction. It discharges the first of EV-AES-dec938's named U4 confounds:
"other Feistel round counts" untested.

The frozen comparator is NOT recomputed. `P1-R5-PAIR`'s reading (14 hits,
`nontrivial_trials = 1073741824`, `null_expectation_analytic = 1.0`, key
`bdf3823182ad657dab3d556b3886ba72`, seed 531001, armid 1) is taken as frozen
from BATCH-009's immutable artifact, as verified field-by-field by BATCH-015
(`L1-AES-R5-P30.json`, EV-AES-4ba350 OBS-B15-4). This task re-runs the AES arm
live and verifies its own AES JSON against that archived reading (§4).

## 1. The four variants (ONLY the round count differs)

Base source: `coordination/goals/GOAL-AES-003/batches/BATCH-014/tasks/TASK-20260805-b95720/src/rc8probe_feistel.c`
(sha256 `9b36c0e714118e11e160b9aec81c9a6c1aceecc6fb2b6c452b3dd3bbf98d8566`,
worktree HEAD `a91cb64ac68c8315eb764edfb89c9fc34d99c3b0`).

The ONLY structural edit in `src/rc8probe_feistel_rk.c` is guarding the round
count define so it can be overridden at compile time:

```c
/* archived form:            #define FEISTEL_ROUNDS 16               */
/* parameterized form (only edit):                                    */
#ifndef FEISTEL_ROUNDS
#define FEISTEL_ROUNDS 16
#endif
```

Everything else is line-for-line identical to the archived source (proven by
`diff` in `src/diff_vs_archived.txt`; audited in `src/INDEPENDENCE_AUDIT.md`).
Round function (`feistel_F`, murmur3-fmix64 family), key schedule
(`feistel_round_keys`), CLI semantics (the `rounds` argv field stays IGNORED;
the actual round count is `FEISTEL_ROUNDS`, reported as
`feistel_rounds_actual`), geometry, worker, and JSON reporting are unchanged.
Disclosed label quirk: the hardcoded `"oracle":
"keyed_deterministic_feistel16_64bit_halves"` string is NOT edited (only the
define guard is a permitted edit); for r != 16 that label is stale, and the
authoritative round count in every output is `feistel_rounds_actual`.

Exact build commands (compiler: Apple clang 17.0.0, `cc`/`gcc` are the same
tool on this host, arm64-apple-darwin25.6.0; flags match BATCH-014's archived
build line `gcc -O3 -pthread` from the source header). All commands run from
the worktree root
`/Volumes/SSD990/crypto-autoresearcher/.worktrees/aes003-batch015-20260831`
with `T = coordination/goals/GOAL-AES-003/batches/BATCH-7939d0/tasks/TASK-20260901-92672b`:

| Binary | Exact build command |
|---|---|
| r=4 variant | `gcc -O3 -pthread -DFEISTEL_ROUNDS=4 -o $T/src/rc8probe_feistel_r4 $T/src/rc8probe_feistel_rk.c` |
| r=8 variant | `gcc -O3 -pthread -DFEISTEL_ROUNDS=8 -o $T/src/rc8probe_feistel_r8 $T/src/rc8probe_feistel_rk.c` |
| r=16 variant | `gcc -O3 -pthread -DFEISTEL_ROUNDS=16 -o $T/src/rc8probe_feistel_r16 $T/src/rc8probe_feistel_rk.c` |
| r=32 variant | `gcc -O3 -pthread -DFEISTEL_ROUNDS=32 -o $T/src/rc8probe_feistel_r32 $T/src/rc8probe_feistel_rk.c` |
| verbatim RC-D control | `gcc -O3 -pthread -o $T/src/rc8probe_feistel_verbatim coordination/goals/GOAL-AES-003/batches/BATCH-014/tasks/TASK-20260805-b95720/src/rc8probe_feistel.c` (compiled in place from the archived file, no copy) |
| AES arm instrument | `gcc -O3 -pthread -o $T/src/rc8probe_freshfeistel coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/src/rc8probe_freshfeistel.c -lm` (sha256 of archived source `d163b64e6b0d6bce1f23027bb7209c0a8c5ef1984874465119f61adf3e0d450d`; its `aes` oracle branch is the byte-for-byte rc8probe.c AES code that BATCH-015 used to reproduce P1-R5-PAIR exactly) |

## 2. Binding r=16 byte-parity control (must pass before any r != 16 measurement arm)

The r=16 variant must byte-for-byte reproduce RC-D at seed 531001. Checks:

1. **detcheck parity:** `rc8probe_feistel_r16 detcheck 531001` and
   `rc8probe_feistel_verbatim detcheck 531001` must produce IDENTICAL JSON
   (sha256 equality; both hashes recorded in RESULTS.json).
2. **2^22 smoke parity:** both binaries run
   `arm SMOKE22-R16 5 1 1 22 531001 1 4` (identical argv including the arm
   name, so the JSON is comparable byte-for-byte); the two JSON outputs must
   be IDENTICAL (sha256 equality; both hashes recorded in RESULTS.json).
3. **Secondary parity expectation at full exposure (preregistered, not an
   extra run):** `F-R16-P30` (r=16 variant, 2^30, seed 531001, armid 1,
   amask=smask=1, 4 threads) is run with parameters identical to RC-D's
   archived `M1-FEISTEL-P30` except the arm-name label; its JSON is therefore
   expected to match `runs/M1-FEISTEL-P30.json` from BATCH-014 field-by-field
   on every field except `arm` (sha256 of the arm-name-normalized content
   recorded). A mismatch here, with detcheck+smoke parity passing, would
   itself be an unexpected observation recorded per rule 8.

**Gate: if (1) or (2) FAILS, all r != 16 measurement arms are STOPPED, the
divergence is documented, and the task reports an infrastructure failure —
never papered over.**

## 3. Run plan (maximum 12 runs — the budget is binding)

Every run is an invocation of an oracle binary in `detcheck` or `arm` mode,
written to `runs/`. No exploratory oracle invocations are made outside this
list. Per run: stdout → `runs/<name>.json`, stderr → `runs/<name>.err`, and
`runs/<name>.timing.txt` records start_utc/end_utc/elapsed/exit code.

| # | name | exact command | purpose |
|---|---|---|---|
| 1 | DET-R16-VERBATIM | `./$T/src/rc8probe_feistel_verbatim detcheck 531001` | parity gate, verbatim side |
| 2 | DET-R16 | `./$T/src/rc8probe_feistel_r16 detcheck 531001` | parity gate, variant side + r16 determinism |
| 3 | SMOKE22-R16-VERBATIM | `./$T/src/rc8probe_feistel_verbatim arm SMOKE22-R16 5 1 1 22 531001 1 4` | parity gate smoke, verbatim side |
| 4 | SMOKE22-R16 | `./$T/src/rc8probe_feistel_r16 arm SMOKE22-R16 5 1 1 22 531001 1 4` | parity gate smoke, variant side |
| 5 | DET-R4 | `./$T/src/rc8probe_feistel_r4 detcheck 531001` | determinism gate for r=4 arm |
| 6 | DET-R8 | `./$T/src/rc8probe_feistel_r8 detcheck 531001` | determinism gate for r=8 arm |
| 7 | DET-R32 | `./$T/src/rc8probe_feistel_r32 detcheck 531001` | determinism gate for r=32 arm |
| 8 | AES-P30 | `./$T/src/rc8probe_freshfeistel arm AES-P30 aes 5 1 1 30 531001 1 2` | live AES arm, matched 2^30 |
| 9 | F-R4-P30 | `./$T/src/rc8probe_feistel_r4 arm F-R4-P30 5 1 1 30 531001 1 4` | substitute arm r=4 |
| 10 | F-R8-P30 | `./$T/src/rc8probe_feistel_r8 arm F-R8-P30 5 1 1 30 531001 1 4` | substitute arm r=8 |
| 11 | F-R16-P30 | `./$T/src/rc8probe_feistel_r16 arm F-R16-P30 5 1 1 30 531001 1 4` | substitute arm r=16 |
| 12 | F-R32-P30 | `./$T/src/rc8probe_feistel_r32 arm F-R32-P30 5 1 1 30 531001 1 4` | substitute arm r=32 |

Ordering: runs 1–4 first (parity gate), then 5–7 (determinism gates), then 8,
then 9–12 sequentially. If the parity gate fails, runs 5–12 are not started
(the r=16 arms 2/4 themselves belong to the gate). This leaves 0 reserve runs:
any infrastructure failure consuming a rerun exceeds the cap and is reported
as scope, per §6(d). Run order 1,2,3,4 (rather than the table's grouping) is
immaterial; the table is the authoritative set.

## 4. AES arm reproduction duty

AES arm parameters: seed 531001, armid 1, amask=smask=1, log2N=30, rounds
field 5, **2 threads** — 2 threads is chosen because the archived AES readings
it is compared against (BATCH-009's `P1-R5-PAIR` and BATCH-015's
`L1-AES-R5-P30`) both used 2 threads, and thread count changes the per-thread
trial chunking (each thread walks `N/nthr` trials of its own deterministic
sub-stream), so byte-comparability requires the same thread count. RC-D's
BATCH-014 disclosure that thread count is a pure performance parameter
(independent per-thread seeds `seed ^ armid*C1 ^ (t+1)*C2`, no cross-thread
state) is adopted; this task does not vary thread count for any comparison, so
no 4-vs-8 thread smoke is needed. Code-level determinism at fixed thread
count: workers share no mutable state, per-thread seeds are a deterministic
function of (seed, armid, t), counters are summed in fixed thread order, and
JSON is emitted in fixed order — recorded in `src/INDEPENDENCE_AUDIT.md`.

Verification against the archived AES arm (stated plainly in RESULTS.json):
the AES arm JSON is compared field-by-field with BATCH-015's
`runs/L1-AES-R5-P30.json`. Preregistered expectation: ALL fields identical
except exactly three — `arm` (this task's label `AES-P30` vs `L1-AES-R5-P30`)
and `elapsed_seconds_measured` / `measured_rate_trials_per_sec` (wall-clock
timing fields emitted by the program, load-dependent, not part of the
statistical record). Any further field difference is a failed reproduction
and is reported as such. In addition, the frozen comparator values from
`P1-R5-PAIR` as recorded by BATCH-015's verified `frozen_comparator` block
(14 hits; hit-trial indices; whist; W_ge1_by_word [4,4,2,4]; thread seeds;
plaintext-stream digests `de8dee29c9310a13`/`01089d650f48ca1b`) are checked
against this task's AES JSON field-by-field.

## 5. Frozen comparison statistic (BATCH-009's matched-exposure comparator)

Identical in structure to RC-D's Rank-1 rule (BATCH-014 PREREGISTRATION.md §4)
and BATCH-015's rule (OUTCOME-A''/B''/C''), which both mirror EV-AES-e4c091's
Rank-1 rule:

- Frozen r=5 reading: `x_aes = 14`, `nontriv_aes = 1073741824`, `m_aes = 1.0`.
- Per substitute arm: `x_sub = W_ge1_nontrivial`, `m_sub = nontrivial_trials * 4 / 2^32`,
  `R_sub = x_sub / m_sub` with exact Garwood Poisson 95% CI mapped through `1/m_sub`.
- Exact conditional-binomial test: `n = x_aes + x_sub`, exposure-exact
  `p0 = m_aes / (m_aes + m_sub)` computed in exact rationals, two-sided
  `p = min(1, 2*min(P[X >= x_aes], P[X <= x_aes]))` for `X ~ Binomial(n, p0)`.
- Per-arm outcome (decided in this order):
  - **OUTCOME-A' (absence):** R_sub's Garwood 95% CI contains 1 AND p < 0.01.
  - **OUTCOME-B' (excess reappears):** R_sub's Garwood 95% CI lower bound > 1
    AND the exact test does not reject at p < 0.01.
  - **OUTCOME-C' (ambiguous):** anything else.
- Implementation: `src/analysis_rk.py`, written for this task, no scipy.
  BEFORE computing any new statistic it reproduces, as a self-check gate, the
  published figures of this comparison family: 14 vs 1 → p = 9.765625e-4,
  ratio CI [2.1300416502432444, 591.9684937326185] (EV-AES-e4c091 / BATCH-015);
  14 vs 0 at nontriv 1073741823 → p = 0.0001220703125, ratio CI lower bound
  3.3171226765018393 (BATCH-014 M1); Garwood x=1,m=1 → [0.025, 5.572] and
  x=6,m=8 → [0.275, 1.632] (EV-AES-e4c091 N1/N2). If any self-check fails the
  analysis code is fixed BEFORE it touches a run JSON (and the fix disclosed).

Cross-batch comparability: the substitute arms run at 4 threads (identical to
RC-D's M1-FEISTEL-P30) while the frozen comparator ran at 2 threads; RC-D's
own preregistration disclosed thread count as a pure performance parameter
that changes which sub-stream each thread walks but not the statistic's
definition, and RC-D's 4-thread matched comparison against the frozen 2-thread
14 was accepted as valid (EV-AES-dec938). This task adopts the same disclosure
for the same deviation.

## 6. Preregistered OUTCOME taxonomy (task level, over the four r values)

Let `x(r)` = `W_ge1_nontrivial` of arm F-R{r}-P30 at matched 2^30 exposure,
`R(r) = x(r)/m(r)`. The task-level outcome is decided AFTER all four arms
complete (or at halt, for (d)):

- **(a) ABSENCE-PERSISTS:** all four arms read OUTCOME-A'. The absence of
  yoyo excess is round-count-robust over r ∈ {4, 8, 16, 32} of this
  construction at this exposure. Per the inventor-protocol null control, if
  the statistic does not move with r, THAT is the measured result and is
  reported plainly with the per-arm R(r) point estimates.
- **(b) MONOTONIC-DECAY:** absence does not persist at all four r, and the
  statistic moves MONOTONICALLY with r — i.e. `x(4) <= x(8) <= x(16) <= x(32)`
  (or the mirror `>=` in every position) with at least one strict inequality,
  and the non-absence occurs at the end of the ordering toward which hits
  increase. Direction (decay toward high r, or toward low r) and magnitude
  (per-arm x(r), R(r), CIs, p-values) are reported.
- **(c) NON-MONOTONIC:** absence fails at some r but holds at others in a
  pattern that is not monotonic in r (e.g. excess only at an intermediate r,
  or x(r) changing direction). Reported with the full per-arm table; no
  smoothing or reinterpretation.
- **(d) INFRA/BUDGET-FAILURE:** any arm incomplete, any parity/determinism
  gate failed, or the budget stop reached before completion. This is SCOPE,
  not a result: the actual exposure reached per arm and the actual reason are
  reported; a timeout or crash is never evidence against the mathematical
  question (AGENTS.md rule 5); dropped work is never an answer (rule 8).

Edge-case rules, preregistered: if all four arms are OUTCOME-A' but x(r) still
moves within absence (e.g. 0,1,2,4), the task outcome is (a) AND the movement's
direction and magnitude are reported (never silenced). If x(r) is monotonic
but all arms are OUTCOME-A', the outcome is (a) with the trend reported, not
(b): (b) requires absence to fail somewhere. Ties (e.g. x(r) = 0 at all four r)
are outcome (a) with "no movement" stated.

## 7. Prediction (recorded so it can be wrong)

Three substitute classes (stored ideal permutation, RC-D's 16-round
deterministic Feistel, fresh-key ideal-approximating Feistel) have all read
absence at or above decisive exposure, and the affine-S-box arm is the only
construction that reproduced the excess. Naive prior: outcome (a), absence
persists at all four r. Reservations recorded in advance: (i) at r=4 the
construction is a 4-round Feistel, a genuinely weaker PRP than at r=16 — but
any round count is still a bijection evaluated at q=4 queries per trial, and
no generic 4-round Feistel distinguisher is reachable at 2^30 trials of this
probe (this is a scope statement about this instrument, not a theorem); (ii)
round-key derivation is identical for all r except for how many subkeys are
drawn (the first r outputs of the same splitmix64 stream from the same key),
so the r=4/8 arms use a PREFIX of the r=16 subkey stream and r=32 extends it —
a disclosed coupling, not an independence between variants; (iii) this is one
key, one seed, one geometry, one machine, exactly as EV-AES-dec938 bounded its
single instance. I put outcome (a) at roughly 3:1, (b)/(c) jointly at roughly
1:3, with (d) a budget tail risk.

## 8. Budget

- Declared wall clock 7200 s. Opening stamp: start 2026-09-01T15:52:39Z,
  binding stop 2026-09-01T17:52:39Z (`budget_stamps.jsonl`).
- Cost basis (measured, same host family): BATCH-014 M1-FEISTEL-P30 took
  101.93 s at 4 threads / 2^30; BATCH-015 L1-AES-R5-P30 took 89.13 s at
  2 threads / 2^30. Planned 12 runs total well under 30 min wall clock.
- HALT at the binding stop is full compliance and is infrastructure signal,
  never a negative mathematical result.
- Maximum 12 runs (enumerated in §3); 0 reserve runs.

## 9. Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: fireworks-ai/accounts/fireworks/models/qwen3p8-max
  fallback_used: true        # transport fallback to session backend (zai billing outage)
  fallback_reason: DEC-20260831-0d1eeb
  model_verified: false
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
  amendment: DEC-20260831-0d1eeb
```

**Parse statement:** this file is prose + YAML for human/audit reading; the
authoritative machine-parseable record is `RESULTS.json`, which is parsed
whole with Python's `json` module before the task finishes, and states so
inside itself.
