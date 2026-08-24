# PREREGISTRATION — TASK-20260805-b95720 (BATCH-014, GOAL-AES-003, RC-D)

**Written 2026-08-05, AFTER `budget_stamps.jsonl` and `src/rc8probe_feistel.c` /
`src/INDEPENDENCE_AUDIT.md` (construction + determinism self-check + a 2^20
and a 2^26 timing smoke test), and BEFORE any exposure-decisive measurement
arm was run.** Order of artifact creation: `budget_stamps.jsonl` →
`src/rc8probe_feistel.c` → determinism self-check (`detcheck`) →
`src/INDEPENDENCE_AUDIT.md` → timing smoke tests (2^20, 2^26, no yoyo-hit
counting decision made from them) → this file → the real measurement arm(s)
→ `RESULTS.json`.

**Toy tier.** Everything below concerns a reduced-round software SPN probe
(the matched `P1-R5-PAIR` reading, frozen from EV-AES-e4c091 /
`BATCH-009/TASK-20260803-a0a7b9/runs/P1-R5-PAIR.json`) against a new,
independently-constructed toy oracle, at exposures up to 2^33 trials on one
machine. Nothing here is about full-round or deployed AES, and no comparison
is made to published cryptanalysis in either direction.

---

## 0. What this task is and is not

This is **not** a rerun of BATCH-009. `P1-R5-PAIR`'s reading (14 hits,
`nontrivial_trials=1073741824`, `null_expectation_analytic=1.0`, key
`bdf3823182ad657dab3d556b3886ba72`, seed 531001, armid 1) is FROZEN and taken
as-is from the immutable BATCH-009 run artifact; it is not recomputed here
and this task does not touch `experiments/` or BATCH-009's files. What is new
this batch is a **second null-object arm** substituting a keyed, deterministic
Feistel PRP for the cipher, to test residual limitation U4 named in
EV-AES-e4c091: whether OUTCOME-A depended on the substitute being an IDEAL
random permutation specifically, or holds for any sufficiently
non-AES/structureless-relative-to-AES deterministic substitute too.

## 1. The object being substituted

### 1.1 What is held fixed (matching BATCH-009's own N1/P1 comparison)

| Held fixed | Value |
|---|---|
| probe geometry PW/CW (forward/inverse ShiftRows-diagonal masks) | byte-identical code, from `rc8probe.c` |
| active-word mask `amask` | 1 |
| swap mask `smask` | 1 |
| plaintext draw + rejection loop, trivial-swap exclusion, W computation | byte-identical code path to `rc8probe.c`'s worker |
| seed, arm id | 531001, 1 (same as `P1-R5-PAIR` / `N1-IDEAL-P30`) |
| key derivation from seed (`seed ^ 0xA5A5...`, splitmix64) | byte-identical code path |
| RNG family for plaintext generation | splitmix64, the campaign's own |

**Disclosed deviation:** thread count is 4 here (all 4 host cores), not 2 as
in BATCH-009's arms. This is a pure performance/parallelization parameter:
`seed_thread` for thread `t` is `seed XOR (armid*C1) XOR ((t+1)*C2)`, computed
independently per thread with no cross-thread state, so changing the thread
count changes which sub-stream of the plaintext generator each thread walks
but not the definition of the measured statistic. It is recorded here, before
any run, as a deviation from BATCH-009's exact arm parameters, not discovered
after the fact.

### 1.2 What is substituted

The map itself, exactly as in BATCH-009. Not an ideal (lazily-sampled,
injectivity-rejected) random bijection this time, but a **keyed, deterministic
Feistel-network PRP**, fixed for the whole run:

- 128-bit block, split into two 64-bit halves.
- 16 rounds of a balanced Feistel ladder: `(L,R) <- (R, L xor F(R, RK[i]))`.
- Round function `F` is a 64-bit integer avalanche mix (murmur3-fmix64-style:
  add subkey, xor-shift, multiply by an odd 64-bit constant, xor-shift,
  multiply by a second odd 64-bit constant, xor-shift, add subkey again).
- 16 round subkeys `RK[0..15]` are derived ONCE per process invocation from
  the 128-bit master key via splitmix64, before any trial runs, and never
  resampled. Determinism (same key -> same subkeys -> same permutation on
  every call) is verified mechanically by `rc8probe_feistel detcheck` BEFORE
  any measurement arm — see §2 below and `runs/detcheck.json`.
- Inversion is the exact algebraic inverse (run the Feistel ladder backwards),
  not a stored table: **O(1) memory per query**, unlike BATCH-012's `perm128`
  ideal-permutation architecture (EV-AES-837cd8), which this task does not
  reuse or import.
- Full construction, and the explicit side-by-side against AES's actual
  S-box/MixColumns/ShiftRows tables, in `src/INDEPENDENCE_AUDIT.md`.

### 1.3 Why this addresses U4, and what would make it unfair

**Addresses U4 because:** an ideal permutation is *maximally* structureless —
every output is uniform and independent of every other, subject only to
injectivity. A deterministic Feistel PRP with a fixed, modest round count is
a **weaker, more "realistic" kind of non-AES substitute**: it has an actual
algebraic structure (Feistel network), a fixed round function evaluated
identically on every query, and no injectivity bookkeeping — closer in kind
to "a plausible non-AES 128-bit block cipher" than to "the uniform measure on
all bijections." If OUTCOME-A (excess absent) reappears here too, that is one
more data point against the excess being an idealness-specific artifact. If
the excess reappears under this oracle (i.e. this arm reads elevated, unlike
BATCH-009's ideal-permutation arm), that would suggest idealness specifically
mattered to BATCH-009's null reading — a materially different observation
that must be reported exactly as it comes out, per Rank-1 rule in §4.

**Unfair, and would have to be disclosed as invalidating, if:**

- **(V1)** the construction were not actually deterministic (same key/input
  giving different outputs across calls, or resampled per trial). Checked
  mechanically by `detcheck` before any measurement arm; see §2.
- **(V2)** the round function or key schedule shared code or tables with
  AES's S-box, GF(2^8) arithmetic, or ShiftRows permutation. Addressed by
  `src/INDEPENDENCE_AUDIT.md`'s explicit side-by-side.
- **(V3)** the plaintext-generation / probe-geometry / W-counting code path
  differed from `rc8probe.c`'s in any respect other than the oracle calls.
  The worker function in `src/rc8probe_feistel.c` is a direct line-for-line
  adaptation of `rc8probe.c`'s worker with only `enc_r`/`dec_r`'s bodies
  changed; this is stated for independent review, not proven by an automated
  digest match against BATCH-009's differently-shaped digest field (BATCH-009
  used a different digest formula; a byte-for-byte plaintext-stream match
  was not re-derived this task — see boundaries in RESULTS.json).
- **(V4)** — a residual limitation this task cannot fully exclude, mirroring
  U4's own logic one level down: 16 rounds of THIS SPECIFIC Feistel
  construction is one point in the space of "non-AES deterministic PRPs," not
  all of it. A different round function, round count, or network shape might
  behave differently. This is recorded as a residual limitation of THIS
  record, not a defense.

## 2. Determinism gate (must pass before any measurement arm runs)

`rc8probe_feistel detcheck <seed>` must report
`same_key_same_input_same_output: true`,
`decrypt_inverts_encrypt: true`, and
`round_key_schedule_reproducible: true`
over 4096 random trial inputs plus an independent second derivation of the
round-key schedule from the same key. **Gate: an arm is `invalid_measurement`
if this check has not passed for the key in use before the arm runs.**
Result, run before any exposure-decisive arm: `runs/detcheck.json`.

## 3. Exposure decision (measured, not assumed)

BATCH-009's matched primary arm (`N1-IDEAL-P30`) ran 2^30 trials. This task's
budget requires demonstrating that 2^30 trials of the new oracle finish
within the remaining wall-clock budget BEFORE committing to it. Procedure,
in order:

1. Run a small smoke arm (2^20 trials) — sanity-check only, not
   decision-relevant, discard the hit count.
2. Run a timing-calibration arm at 2^26 trials, 4 threads, and record its
   wall-clock time. Extrapolate the per-trial cost linearly to 2^30 and 2^33.
3. If the extrapolated 2^30 cost fits comfortably (with margin) inside the
   wall-clock remaining under `binding_stop_utc`, run the real 2^30 arm
   (`M1-FEISTEL-P30`) as the primary matched-exposure arm. This is the
   headline comparison against `P1-R5-PAIR`'s 14 hits.
4. If after `M1-FEISTEL-P30` completes there is still comfortable budget
   margin, run a second, higher-exposure arm (`M2-FEISTEL-P33`) at 2^33
   trials, SAME seed/armid as M1 (so M2's trial stream is a superset prefix
   of M1's, exactly as BATCH-009's own N1/N2 pair was) — reported
   **separately**, never pooled with M1, per the pooling defect EV-AES-e4c091
   OBS-B9-5 already flagged for exactly this non-independence.
5. If the measured 2^26 cost extrapolates to MORE than the remaining budget
   for 2^30, the largest power-of-two exposure that fits with margin is run
   instead, and the shortfall relative to 2^30 is disclosed plainly in
   `RESULTS.json`, never silently truncated by a timeout.

Actual measured 2^26 timing, extrapolation, and the exposure decision taken
are recorded verbatim (not reconstructed after the fact) in `RESULTS.json`'s
`exposure_decision` block, with the raw timing figures.

## 4. RANK 1 — the frozen decision rule (mirrors EV-AES-e4c091's Rank-1 rule exactly)

Let `x` = `W_ge1_nontrivial` of the Feistel-oracle arm and `m` = its
`null_expectation_analytic` (`= nontrivial_trials * 4 * 2^-32`, the same
formula used throughout this campaign for a 128-bit block). Define
`R_feistel = x/m`, with an exact (Garwood) Poisson 95% CI on `x` mapped
through `1/m`. `R_5 = 14/1.0 = 14` is the FROZEN r=5 reading from
`P1-R5-PAIR` (EV-AES-e4c091 OBS-B9-3; `analysis` re-derives it here only to
recompute the comparison statistic against the new arm, never to re-measure
`P1-R5-PAIR` itself).

The r=5 vs Feistel-oracle comparison uses the same exact conditional-binomial
(Poisson ratio) test EV-AES-e4c091 used, at matched exposure between
`P1-R5-PAIR` (nontrivial_trials=1073741824, m=1.0) and `M1-FEISTEL-P30`
(nontrivial_trials as measured, its own m).

**Preregistered outcomes, mutually exclusive, decided in this order —
identical in structure to EV-AES-e4c091's Rank-1 rule, applied to the new
oracle:**

- **OUTCOME-A' — the excess does NOT reappear under the Feistel oracle either.**
  `R_feistel`'s 95% CI contains 1, **and** the exact test of r=5 against the
  Feistel-oracle arm at matched exposure gives p < 0.01.
  *Reading:* consistent with U4 being resolved in the direction that
  idealness specifically was not doing the work in BATCH-009 — the absence
  also holds under a deterministic, non-ideal, independently-constructed
  substitute. This is an observation about these two arms, not a closure of
  U4 in general (see §1.3 V4).

- **OUTCOME-B' — the excess REAPPEARS under the Feistel oracle.**
  `R_feistel`'s 95% CI lower bound > 1, **and** the exact test of r=5 against
  the Feistel-oracle arm does **not** reject at p < 0.01.
  *Reading:* consistent with idealness specifically mattering to BATCH-009's
  OUTCOME-A — a materially different observation from BATCH-009's, and if it
  occurs it is written in the FIRST LINE of `RESULTS.json`, unsoftened.

- **OUTCOME-C' — ambiguous.** Anything else, including partial elevation.
  Reported as ambiguous with both intervals and no interpretation beyond the
  arithmetic.

No evidence strength, hypothesis status, or promotion recommendation is
assigned under any outcome. These are readings, exactly as EV-AES-e4c091
insisted for its own Rank-1 rule.

**Power note, disclosed in advance:** at 2^30 trials the analytic null
expectation is ~1 event; BATCH-009's own N1 arm at this exposure was
explicitly "a modest count" per EV-AES-e4c091's own strength_basis. If
`M2-FEISTEL-P33` is reached, its ~8-event expectation gives the tighter
interval, exactly as BATCH-009's N2 did; if it is not reached, that shortfall
is disclosed and M1 alone is the primary reading.

## 5. Prediction (recorded so it can be wrong)

No campaign prior specifically addresses a deterministic-non-ideal-PRP
substitute; the honest prior here is weaker than BATCH-009's own (which could
cite three prefix-counter near-nulls across every prior arm as weak evidence).
I predict OUTCOME-A' (excess absent under this oracle too) at roughly
even-to-2:1 odds, weaker than BATCH-009's stated 4:1 for its own prediction,
because a *deterministic* PRP with a specific, if unrelated, round structure
is a genuinely different kind of object from an ideal permutation, and U4 was
named precisely because this distinction was not tested before.

## 6. Inference block

```yaml
inference:
  policy: coordinator-orchestration-code
  requested_policy: coordinator-orchestration-code
  resolved_model: claude-sonnet-5
  fallback_used: true
  model_verified: false
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

**Parse statement:** this file is prose + YAML for human/audit reading; the
authoritative machine-parseable record is `RESULTS.json`, which is parsed
whole with Python's `json` module before the task finishes, and states so
inside itself.
