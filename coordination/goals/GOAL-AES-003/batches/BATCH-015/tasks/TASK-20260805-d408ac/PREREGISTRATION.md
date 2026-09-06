# PREREGISTRATION — TASK-20260805-d408ac (BATCH-015, GOAL-AES-003)

**Written 2026-08-31, AFTER `budget_stamps.jsonl` (opening stamp) and
`src/rc8probe_freshfeistel.c` (construction, built; one functional test of each
mode in /tmp only — NO task run output exists yet in `runs/`), and BEFORE any
run output file. Completion-gate ordering: this file's mtime predates every
file under `runs/`.**

Order of artifact creation: `budget_stamps.jsonl` (opening) →
`src/rc8probe_freshfeistel.c` → build + /tmp functional test (no run outputs)
→ this file → run 1 selfcheck → run 2 smoke → run 3 calibration → exposure
decision → runs 4-6 measurement arms → `RESULTS.json`.

**Toy tier.** Everything below concerns a reduced-round (r=5) AES-shaped SPN
probe (one key, one probe geometry amask=1 smask=1) against a new,
independently-constructed toy oracle, at exposures up to 2^33 trials on one
machine. Nothing here is about full-round or deployed AES, and no comparison
is made to published cryptanalysis in either direction (RQ-AES-003 R3).

---

## 0. What this task is and is not

This is not a rerun of BATCH-009. `P1-R5-PAIR`'s reading (14 hits,
`nontrivial_trials=1073741824`, `null_expectation_analytic=1.0`, key
`bdf3823182ad657dab3d556b3886ba72`, seed 531001, armid 1, threads 2) is FROZEN
and was verified by this task DIRECTLY from the immutable source file
`coordination/goals/GOAL-AES-003/batches/BATCH-009/tasks/TASK-20260803-a0a7b9/runs/P1-R5-PAIR.json`
(field values read before this file was written; not taken from citation).
What is new this batch is a THIRD substitute-oracle arm for the
cipher-substitution comparison — the first one that (a) costs O(1) memory per
query (closing the perm128 memory-architecture gap named in EV-AES-837cd8's
unresolved_confounds), (b) APPROXIMATES an ideal random permutation (unlike
BATCH-014's deliberately non-ideal RC-D construction), and (c) is RESAMPLED
WITH A FRESH RANDOM KEY EVERY TRIAL (the opposite of RC-D's fixed key,
matching perm128's per-trial fresh-permutation semantics, EV-AES-e4c091
OBS-B9-2). A matched live 5-round AES arm is run by THIS instrument at the
same exposure as a harness-equivalence gate and matched comparator.

## 1. The construction (exact)

- **Block:** 128 bits, split into two 64-bit halves (little-endian byte
  packing of in[0..7] -> L, in[8..15] -> R).
- **Network:** balanced Feistel ladder, `FF_ROUNDS = 16` rounds:
  `for i in 0..15: (L,R) <- (R, L xor F(R, RK[i]))`; decryption runs the
  ladder backwards with the same F. Bijectivity is structural (any round
  function gives a permutation), inversion is the exact algebraic inverse,
  and memory is O(1) per query (RK lives on the worker stack, no stored pair
  table — unlike perm128, whose dom/rng arrays cost 8.590 GB at 2^26 per
  EV-AES-837cd8 OBS-B12-5).
- **Round function F(x,k):** SipRound-based keyed mix. Initialize the 4-word
  SipHash state from (x,k) with SipHash's public IV constants
  (`v0 = k ^ 0x736f6d6570736575`, `v1 = x ^ 0x646f72616e646f6d`,
  `v2 = k ^ 0x6c7967656e657261`, `v3 = x ^ 0x7465646279746573`), apply TWO
  SipRounds (add/rotate/xor only — the compression round of SipHash-2-4), and
  finalize `F = v0 ^ v1 ^ v2 ^ v3`. No multiplication, no GF(2^8) arithmetic,
  no table lookup, no byte-array permutation — and NOT the murmur3-fmix64
  multiply/xor-shift mix of BATCH-014's RC-D oracle (verbatim reuse of RC-D's
  round function is contract-prohibited).
- **Per-trial key derivation (THE defining property of this task):** each
  trial draws `k0 = sm64(&kst)`, `k1 = sm64(&kst)` — two consecutive draws
  from a DEDICATED per-thread splitmix64 key stream (state `kst`, seeded
  `seed ^ armid*0x517CC1B727220A95 ^ (t+1)*0x6A09E667F3BCC908`, constants
  disjoint from the plaintext-stream and AES-key constants) — then derives 16
  round subkeys by `st = k0 ^ rotl64(k1,27) ^ 0x6A09E667F3BCC908; RK[i] =
  sm64(&st)`, and uses THAT key's permutation for this trial's oracle queries
  only. There is NO global key state (contrast RC-D's global fixed `RK[]`).
  Freshness is verified, not asserted: (i) within-thread PROOF — splitmix64's
  state advances by an odd constant on a single 2^64 cycle and its output mix
  is a bijection, so consecutive 128-bit key pairs cannot repeat within 2^64
  steps >> any trial count here; (ii) empirical keycheck — run 1 verifies all
  4,194,304 keys drawn by 4 simulated thread streams are pairwise distinct;
  (iii) every measurement arm logs its first 4 per-trial keys per thread and
  an order-sensitive digest over ALL drawn keys.
- **Live arm:** 5-round AES itself, code copied byte-for-byte from
  rc8probe.c (BATCH-007) including its FIPS-197 C.1 KAT + round-trip pin
  gate, same seed-derived key derivation — the comparison's live side. The
  AES-vocabulary prohibition applies to the SUBSTITUTE oracle, which shares
  none of it (src/INDEPENDENCE_AUDIT.md).

### 1.1 What is held fixed (matching BATCH-009's own N1/P1 comparison)

| Held fixed | Value |
|---|---|
| probe geometry PW/CW (forward/inverse ShiftRows-diagonal masks) | byte-identical code, from rc8probe.c |
| active-word mask `amask` | 1 |
| swap mask `smask` | 1 |
| plaintext draw + rejection loop, trivial-swap exclusion, W computation | byte-identical code path to rc8probe.c's worker |
| seed, arm id | 531001, 1 (same as P1-R5-PAIR / N1-IDEAL-P30) |
| AES-arm key derivation from seed (`seed ^ 0xA5A5...`, splitmix64) | byte-identical code path (reproduces key bdf3823182ad657dab3d556b3886ba72, verified numerically before this file) |
| RNG family | splitmix64, the campaign's own |
| thread count | **2 — deliberately matching BATCH-009** (BATCH-014 used 4, a disclosed deviation; this task returns to 2 so BATCH-009's recorded plaintext_stream_digest can be verified by equality) |
| plaintext stream digest formula | yoyo_sbox_v4.c's exact FNV-1a 64 over 8-byte words (BATCH-009's own formula; BATCH-014's byte-wise variant could not be cross-compared — this closes that V3 gap) |

## 2. Statistical-quality argument (why this approximates ideal at the target exposure)

Full version with citations in `src/CONSTRUCTION_JUSTIFICATION.md`. Summary:

1. **Queries per permutation instance = 4.** Because the key is resampled
   EVERY trial, each trial consumes exactly 4 oracle queries (2 forward, 2
   inverse) against ONE permutation instance. The 2^30-2^33 exposure is a
   count of INDEPENDENT permutation draws, not queries against a single
   permutation. This is the regime the construction must be ideal in.
2. **Round-count floor is far below 16.** For a balanced Feistel on 2n bits
   with ideal independent random round functions: 3 rounds suffice for PRP
   security and 4 for strong-PRP security (needed here, since the transcript
   includes inverse queries), per the Luby-Rackoff line of results; concrete
   bounds of the Patarin type bound the q-query distinguishing advantage by
   on the order of q^4/2^{2n} for 4+ rounds (provenance `recalled` for all
   external results — marked per AGENTS.md rule 9, never presented as checked
   sources). At q = 4, n = 64 this is ~2^-120 per trial; a union bound over
   2^33 trials keeps the total << 2^-100. 16 rounds leaves a wide margin and
   matches RC-D's geometry for comparability.
3. **Honest caveats (working assumption, not proof).** (a) The round
   functions are keyed SipRound mixes, not ideal random functions; the
   step "round-function family ~ random function family" is the standard
   Luby-Rackoff heuristic and is a WORKING ASSUMPTION at this toy scale,
   sanity-checked empirically (run 1 qualcheck: output-byte uniformity
   chi-square under fresh keys, 2-point injectivity, round-trip inversion,
   key distinctness) rather than proven. (b) The family has at most 2^128
   keys, hence support <= 2^128 permutations vs (2^128)! — it is NOT
   statistically close to uniform over all permutations; the claim is
   transcript-level closeness on the 4-query transcript each trial consumes,
   which is exactly the level at which perm128 served (per-trial
   transcript-exact; cross-trial birthday bound 2^-56 per EV-AES-e4c091).
   Nothing in this task claims indistinguishability from ideal as an
   established fact.

## 3. Exposure decision (measured, not assumed)

Target: 2^30 trials for BOTH the matched live arm and the substitute arm
(where ~14 events are expected under BATCH-009's measured rate of 14 per
2^30), plus 2^33 (8x, ~8 analytic-null events) for the substitute arm if
budget allows — mirroring BATCH-009's own N1/N2 two-level design. Procedure:

1. Run 1 (selfcheck) includes 2^20 rate probes for BOTH oracles at the arm
   thread count. MEASURED (recorded here as the pre-run basis, will be
   re-stamped from the archived run file): AES 11,954,624.7 trials/s,
   fresh-Feistel 9,210,720.0 trials/s, 2 threads (functional-test values;
   run 1's archived values govern).
2. Run 2: 2^20 smoke arm (fresh-Feistel) — sanity + stream check only, hit
   count discarded. Run 3: 2^26 fresh-Feistel calibration arm; extrapolate
   linearly.
3. Commit to 2^30 for runs 4 (live AES) and 5 (fresh-Feistel M1) only if the
   extrapolation fits with >= 600 s margin inside the binding stop; else run
   the largest power-of-two exposure that fits with margin and disclose the
   shortfall plainly in RESULTS.json — never silently truncated by a timeout.
4. Run 6 (M2, 2^33) is executed only if, after run 5, the extrapolated cost
   fits with >= 600 s margin; else disclosed as not reached.

## 4. Gates (must pass before any reading is trusted)

- **G1 (run 1):** selfcheck_pass — FIPS-197 C.1 KAT + AES round-trip pin;
  fresh-feistel round-trip + 2-point injectivity under 4096 fresh keys;
  keycheck 4,194,304 keys pairwise distinct; qualcheck battery within gates.
- **G2 (run 4, live arm):** L1-AES-R5-P30 must read EXACTLY
  `W_ge1_nontrivial = 14` AND `plaintext_stream_digest =
  ["de8dee29c9310a13","01089d650f48ca1b"]` — both values read directly from
  BATCH-009's P1-R5-PAIR.json before this file was written. A mismatch is
  `invalid_measurement` (harness non-equivalence; an infrastructure finding
  under AGENTS.md rule 5, NOT evidence against any hypothesis) and voids the
  comparison.
- **G3 (run 5):** M1's plaintext_stream_digest equals the same two recorded
  digests — byte-identical plaintext stream to BATCH-009's arms, verified by
  digest equality (closing BATCH-014's V3 gap).
- **G4 (runs 5/6):** logged first-4 per-trial keys per thread are pairwise
  distinct, key_stream_digest reported, keycheck (run 1) had 0 duplicates —
  the fresh-key property demonstrated on the actual measurement runs.

## 5. RANK 1 — the frozen decision rule (structural mirror of EV-AES-e4c091's / BATCH-014's Rank-1 rule)

Let `x` = `W_ge1_nontrivial` of the fresh-Feistel arm, `m` = its
`null_expectation_analytic` (= nontrivial_trials × 4 × 2^-32, the campaign's
standard 128-bit-block analytic null). `R = x/m` with an exact (Garwood)
Poisson 95% CI on x mapped through 1/m. Expected counts under the null:
m(2^30) ≈ 1.0; m(2^33) ≈ 8.0. Under BATCH-009's measured AES rate (14 per
2^30), the substitute arm would read ≈ 14 at 2^30 and ≈ 112 at 2^33 if it
carried the AES-level excess.

The live-vs-substitute comparison uses the same exact conditional-binomial
(Poisson-ratio) test the campaign has used since BATCH-009: condition on
n = x_aes + x_sub, x_aes ~ Binomial(n, p0) with EXPOSURE-WEIGHTED
p0 = m_aes/(m_aes + m_sub) (= nontriv_aes/(nontriv_aes + nontriv_sub)
exactly); p-value = 2×min(P(X ≥ x_aes), P(X ≤ x_aes)) capped at 1 (this
machinery reproduces EV-AES-e4c091's published p = 9.765625e-4 for 14 vs 1 —
the analysis script self-checks against those published figures BEFORE
computing any new statistic, as BATCH-014's did). Rate-ratio CI from the
Clopper-Pearson CI on p mapped through (p/(1-p))×(m_sub/m_aes).

**Preregistered outcomes, mutually exclusive, decided in this order:**

- **OUTCOME-A'' — the excess does NOT reappear under the ideal-approximating
  substitute.** R's 95% CI contains 1, AND the exact test of the live arm
  against the substitute at matched exposure gives p < 0.01.
- **OUTCOME-B'' — the excess REAPPEARS.** R's 95% CI lower bound > 1, AND
  the exact test does NOT reject at p < 0.01. If this occurs it is written
  in the FIRST LINE of RESULTS.json, unsoftened.
- **OUTCOME-C'' — ambiguous.** Anything else, including partial elevation;
  reported with both intervals and no interpretation beyond the arithmetic.

**What falsifies what:** OUTCOME-B'' falsifies the extension "the r=5
excess's absence under cipher substitution holds on an independent,
O(1)-memory, ideal-approximating substitute at decisive exposure" — i.e. the
absence measured in BATCH-009/014 depended on perm128's exact idealness or
on BATCH-009's specific instrument, and this construction does not share it.
OUTCOME-A'' corroborates the absence on this construction at this exposure;
it does not establish absence for all ideal-approximating constructions. A
G2/G3 failure voids the comparison and is reported as infrastructure, not as
a reading in either direction. M2 (if reached) is compared to the live arm
with the exposure-weighted p0 and reported SEPARATELY, never pooled with M1
(M1's trial stream is a prefix of M2's — the OBS-B9-5 non-independence
class); M1 and M2 also share the fresh-key stream prefix for the same reason.

## 6. Prediction (recorded so it can be wrong)

OUTCOME-A'' (absence stays), at roughly 2:1 odds. Basis: BATCH-009
(ideal-permutation substitute, OUTCOME-A), BATCH-011/012 (underpowered but
never elevated), and BATCH-014 (deterministic non-ideal Feistel, OUTCOME-A'
at both exposures) all read absence; but per-trial resampling is genuinely
new semantics no prior arm exercised, and a fresh permutation per trial is
the closest object yet to perm128's own regime — if any substitute were to
re-elevate, this is the one most like the original.

## 7. Run plan (maximum_runs = 6)

1. `selfcheck 531001 2` — G1 gate battery + rate probes.
2. `arm SMOKE-FF-2p20 freshfeistel 0 1 1 20 531001 1 2` — sanity, hit count discarded.
3. `arm CALIB-FF-2p26 freshfeistel 0 1 1 26 531001 1 2` — timing calibration.
4. `arm L1-AES-R5-P30 aes 5 1 1 30 531001 1 2` — matched live arm, gates G2.
5. `arm M1-FF-P30 freshfeistel 0 1 1 30 531001 1 2` — primary substitute arm, gate G3/G4.
6. `arm M2-FF-P33 freshfeistel 0 1 1 33 531001 1 2` — 8x exposure, only if §3 budget test passes.

## 8. Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: accounts/fireworks/models/qwen3p8-max
  fallback_used: false
  model_verified: false
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

Model policy executor-implementation satisfied by the model serving this
subagent per Coordinator amendment DEC-20260831-0d1eeb.

**Parse statement:** this file is prose + YAML for human/audit reading; the
authoritative machine-parseable record is RESULTS.json, which will be parsed
whole with Python's json module before the task finishes and will state so
inside itself.
