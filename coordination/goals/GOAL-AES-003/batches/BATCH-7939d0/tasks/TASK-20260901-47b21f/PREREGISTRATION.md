# PREREGISTRATION — TASK-20260901-47b21f (BATCH-7939d0, GOAL-AES-003, RC-D second seed/key)

**Written 2026-09-01, AFTER `budget_stamps.jsonl`, the verbatim source copies
(`src/rc8probe_feistel.c`, `src/rc8probe_freshfeistel.c`), `src/BUILD.md`, and
the two binary builds — and BEFORE any run output file exists under `runs/`.**
Artifact creation order: `budget_stamps.jsonl` → source copies + `BUILD.md` →
builds → this file → determinism self-check → measurement arms →
`RESULTS.json`. The mtime of this file must predate every file in `runs/`.

**Toy tier.** Everything below concerns a reduced-round (r=5) AES-shaped SPN
probe geometry (amask=1, smask=1) measured against a 16-round keyed Feistel
toy oracle, at exposures up to 2^30 trials (and possibly 2^33) on one machine.
Nothing here is about full-round or deployed AES, and no comparison is made to
published cryptanalysis in either direction.

---

## 0. What this task is

Re-run RC-D's (BATCH-014, TASK-20260805-b95720, EV-AES-dec938) comparison
with RC-D's UNMODIFIED keyed 16-round Feistel oracle under a SECOND
preregistered seed **S2 = 531002**, at the matched decisive exposure 2^30,
against a FRESHLY RECOMPUTED live 5-round AES arm under the same new seed,
using BATCH-009's frozen matched-exposure comparator (EV-AES-e4c091's
exact conditional-binomial machinery, as carried through BATCH-014 and
BATCH-015). Question: does the BATCH-014 finding — the r=5 yoyo excess does
NOT reappear under this deterministic non-ideal Feistel substitute — hold for
a second key of the identical construction, or was it specific to seed/key
531001? This is the second of EV-AES-dec938's named U4 confounds ("other
keys/seeds" untested).

## 1. The second seed S2 = 531002, and why it is admissible

- **Value:** S2 = 531002. RC-D used S1 = 531001.
- **Admissibility:**
  - S2 ≠ 531001 (distinct seed → distinct 128-bit master key, since the key is
    derived from `seed ^ 0xA5A5A5A5A5A5A5A5` via splitmix64 in both
    instruments; distinct trial stream, since every per-thread plaintext
    stream seed is `seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15`).
  - S2 was chosen BEFORE any run of this task exists, by a rule fixed here:
    the successor integer of the campaign's existing r=5-family seed 531001.
    It is NOT derived from, chosen using, or conditioned on any observed
    statistic of any prior arm (no hit count, rate, digest, or p-value of any
    existing run entered the choice). The choice rule is mechanical and was
    written down before any S2 measurement.
  - Per the task card constraint: had a different second seed been needed, it
    would have been picked before any run output and recorded here; it was
    not needed — S2 = 531002 stands as preregistered.
- **What changes at S2 (both instruments, traced in `src/INDEPENDENCE_AUDIT.md`):**
  the AES-128 key of the live arm AND the Feistel master key (hence its 16
  round subkeys) AND the entire plaintext/trial stream. Everything else
  (round count, round function, probe geometry, masks, armid, thread count,
  exposure, statistic) is held fixed at RC-D's values.

## 2. Verbatim source and instruments

- **Substitute arm instrument:** `src/rc8probe_feistel.c` — byte-for-byte copy
  of the archived BATCH-014 source, sha256 parity MATCH
  (`9b36c0e714118e11e160b9aec81c9a6c1aceecc6fb2b6c452b3dd3bbf98d8566`),
  recorded in `src/BUILD.md` with the exact build command. ZERO code changes;
  the only varied parameter is the seed CLI field. Any modification would
  invalidate this task.
- **Live AES arm instrument:** `src/rc8probe_freshfeistel.c` — byte-for-byte
  copy of the archived BATCH-015 source, sha256 parity MATCH
  (`d163b64e6b0d6bce1f23027bb7209c0a8c5ef1984874465119f61adf3e0d450d`),
  invoked ONLY in its `aes` oracle mode (its `freshfeistel` oracle mode is
  never called by this task). Its live-AES code path is rc8probe.c's AES code
  and was verified by BATCH-015 to reproduce BATCH-009's frozen P1-R5-PAIR
  reading byte-exactly at seed 531001 (EV-AES-4ba350 OBS-B15-4), which is why
  this in-read-scope instrument carries the AES arm. Reusing RC-D's or
  BATCH-015's archived AES JSONs would be a protocol violation (trial stream
  is seed-dependent); the AES arm is RECOMPUTED under S2 here.
- **Determinism gate (must pass before any measurement arm):**
  `src/rc8probe_feistel detcheck 531002` must report
  `same_key_same_input_same_output: true`, `decrypt_inverts_encrypt: true`,
  `round_key_schedule_reproducible: true` — the same self-check RC-D ran at
  531001, re-run at the S2 key. If it fails, STOP: no measurement arms, report
  infrastructure. Result will be in `runs/detcheck-S2.json`.
- **AES-arm pin gate:** the instrument itself refuses to measure the AES arm
  unless its internal FIPS-197 C.1 KAT + round-trip pin gate passes (enforced
  in the binary, not waivable from the CLI).

## 3. Arms, parameters, and run plan (maximum 6 runs, declared budget 3600 s)

All arms: armid 1, amask=1, smask=1, **threads 4** (RC-D's exact thread
count; changing it is neither needed nor done — aggregate statistics are
order-independent sums over per-thread substreams whose seeds depend only on
(seed, armid, t), so 4 threads is deterministic, and using RC-D's value keeps
the within-task stream partition identical across both S2 arms).

| # | run | instrument & command tail | exposure |
|---|---|---|---|
| 1 | `runs/detcheck-S2.json` | `rc8probe_feistel detcheck 531002` | 4096 trials (gate) |
| 2 | `runs/AES-P30-S2.json` | `rc8probe_freshfeistel arm AES-P30-S2 aes 5 1 1 30 531002 1 4` | 2^30 |
| 3 | `runs/F16-P30-S2.json` | `rc8probe_feistel arm F16-P30-S2 5 1 1 30 531002 1 4` | 2^30 |
| 4–5 | OPTIONAL `runs/AES-P33-S2.json`, `runs/F16-P33-S2.json` | same commands with log2N=33 | 2^33 (see §4) |
| 6 | (reserve rerun, only if a run above is corrupted/invalid) | | |

Per-arm `.timing.txt` (start/end UTC, elapsed seconds, and `/usr/bin/time -l`
resource report) and `.err` (program stderr, expected empty, exit code
recorded) files accompany every arm. Runs are invoked deterministically from
the stated seeds; no run is retried except from the reserve slot, and any use
of the reserve is disclosed in RESULTS.json.

Timing basis (measured, archived, from this same binary lineage): RC-D's
2^30 Feistel arm took 101.93 s at 4 threads; BATCH-015's 2^30 AES arm took
89.13 s at 2 threads. Expected cost of runs 1–3 ≈ 4–5 minutes total, well
inside the 3600 s declared budget. (The dispatch queue's budget_note
extrapolated "~27 min/arm" from TIMING26; that note misreads the archived
figure — RC-D's measured 2^26 calibration was 6.29 s, and 101.9 s was its
ACTUAL 2^30 M1 elapsed. The archived raw timings are authoritative; this task
also re-measures elapsed per arm.)

## 4. OPTIONAL opportunistic 2^33 pair — preregistration of the condition

Per the task card, the optional pair runs ONLY if (i) it is preregistered
here — it is — AND (ii) **≥ 3600 s remain under the binding stop at the
decision point** (the moment runs 1–3 have all completed and written
outputs). This task's TOTAL declared wall clock is 3600 s, so condition (ii)
can be satisfied only if runs 1–3 plus all setup consume ~0 s; in practice it
is expected to be FALSE, and the pair is then skipped without being treated
as a shortfall (scope, not result). At the decision point this task records
in `budget_stamps.jsonl` the actual seconds remaining and the go/no-go
evaluation, and `RESULTS.json` reports which exposure was actually reached
per arm. No 2^33 arm runs unless both conditions are met at that moment.

## 5. FROZEN comparison statistic (BATCH-009's matched-exposure comparator)

Notation from the raw run JSONs: for arm Y, `x_Y` = `W_ge1_nontrivial`,
`nt_Y` = `nontrivial_trials`, `m_Y = nt_Y * 4 / 2^32` (analytic null
expectation, the campaign's standing formula for a 128-bit block).

**Primary (decision-driving) comparison — matched exposure at S2:**
AES-P30-S2 (x_A, m_A) vs F16-P30-S2 (x_F, m_F):

1. `R_F = x_F / m_F` with an exact Garwood 95% Poisson CI on x_F mapped
   through 1/m_F.
2. Exact conditional-binomial (Poisson-ratio) test: `n = x_A + x_F`,
   `p0 = m_A / (m_A + m_F)` (exposure-weighted; ≈ 1/2 at matched exposure),
   p-value = min(1, 2·min(P[Bin(n,p0) ≥ x_A], P[Bin(n,p0) ≤ x_A])) computed
   in exact rational arithmetic; Clopper–Pearson CI on the AES share mapped
   to the rate-ratio CI with scale m_F/m_A. This is exactly the machinery of
   EV-AES-e4c091 as implemented in BATCH-015's `analysis.py` (which this
   task reproduces function-for-function, self-checked against the published
   figures: 14-vs-1 → p=9.765625e-4, ratio CI [2.130, 592.0]; BATCH-014
   14-vs-0 → p=1.220703125e-4; Garwood x=1,m=1 → [0.025, 5.572];
   x=6,m=8 → [0.275, 1.632]).

**Secondary (non-decision) readings, reported plainly:**
- F16-P30-S2 against its own analytic null (R_F point + Garwood CI).
- AES-P30-S2 against its own analytic null (R_A point + Garwood CI) — this
  says whether the r=5 excess reproduces under the new key at all.
- Cross-anchor: F16-P30-S2 vs the FROZEN 531001 r=5 comparator
  (14 hits / nontrivial 1073741824, read verbatim from BATCH-009's immutable
  `P1-R5-PAIR.json` via RC-D's RESULTS.json frozen_comparator block) — a
  cross-SEED rate comparison (streams differ between seeds), labeled as such,
  mirroring RC-D's primary statistic's form but NOT decision-driving here,
  because the matched comparison at S2 is AES-S2 vs F16-S2.

**Frozen decision rule (structural mirror of EV-AES-e4c091's Rank-1 rule /
RC-D's OUTCOME-A'/B'/C' rule, with the live S2 AES arm in the comparator's
r=5 seat):**

- **OUTCOME (a) — absence persists at S2.** `R_F`'s Garwood 95% CI contains 1
  AND the primary exact test rejects at p < 0.01 (the S2 AES arm is elevated
  relative to the S2 Feistel arm — RC-D's pattern reproduces under the new
  key: excess present in AES, absent under substitution).
- **OUTCOME (b) — excess reappears at S2 (key-specific result).** `R_F`'s
  Garwood 95% CI lower bound > 1 AND the primary exact test does NOT reject
  at p < 0.01 (the S2 Feistel arm itself reads elevated, at a rate not
  distinguishable from the S2 AES arm — the BATCH-014 absence was specific to
  seed/key 531001). If this occurs it is written in the FIRST LINE of
  RESULTS.json, unsoftened.
- **OUTCOME (c) — mixed/weakened/anything else.** Including, preregistered
  explicitly: the case where the S2 AES arm itself reads at its own null
  (the r=5 excess does not reproduce under the new key) so the test cannot
  reject while `R_F`'s CI contains 1 — then the substitution comparison at S2
  is uninformative about substitution as such, the overall pattern has
  changed, and both arms' readings are reported with that statement. Also
  partial elevation (CI lower bound > 1 but test rejects, or CI contains 1
  but test does not reject while the AES arm is elevated).
- **OUTCOME (d) — infrastructure/budget failure.** Any declared arm fails to
  reach 2^30 because of crash, corruption, or the budget clock. This is
  SCOPE, never a mathematical result (AGENTS.md rules 5 and 8); the actual
  exposure reached and the reason are reported honestly, never fabricated.

Rules are applied in the order (d) → (a) → (b) → (c): (d) first because an
incomplete arm yields no reading; then (a), then (b), then (c) as the
residual. No evidence strength, hypothesis status, or promotion
recommendation is assigned under any outcome.

**Power note, disclosed in advance:** at 2^30 the analytic null expectation is
~1 event per arm; this is the same modest-count regime BATCH-009/014/015 ran
their matched comparisons in, and the same power limitation applies. If the
optional 2^33 pair runs, its ~8-event expectation gives the tighter interval;
per §4 it is expected NOT to run.

## 6. Predictions (recorded so they can be wrong)

No campaign measurement exists at seed 531002 for either arm. Two separate
unknowns: (i) whether the r=5 AES excess reproduces under a new key at all,
and (ii) whether the Feistel substitute stays at its null. The campaign's
standing pattern (one construction, one key) gives no direct prior on either
axis across keys. I predict OUTCOME (a) at roughly even odds — the excess's
absence under all three substitute classes tested so far (EV-AES-e4c091,
EV-AES-dec938, EV-AES-4ba350) suggests the absence is a property of the
comparison rather than of one key, but the AES arm's own key-sensitivity at
r=5 is genuinely unmeasured, and a key-specific excess is exactly the
confound this task exists to test. Recorded before any S2 run output exists.

## 7. Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: fireworks-ai/accounts/fireworks/models/qwen3p8-max
  fallback_used: true        # transport fallback to session backend under DEC-20260831-0d1eeb (zai billing outage)
  model_verified: false
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

**Parse statement:** this file is prose + YAML for human/audit reading; the
authoritative machine-parseable record is `RESULTS.json`, which is parsed
whole with Python's `json` module before the task finishes, and states so
inside itself.
