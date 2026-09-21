# PREREGISTRATION — TASK-20260803-48a239 (GOAL-AES-003, BATCH-005)

**Written and frozen BEFORE any measurement arm was launched.** The only
executions performed before this file was written were verification, not
measurement: the geometry dump, the FIPS-197 C.1 pin under a fresh pin seed,
the two random-S-box pins, and the independent plain-Python reference anchor.
Those are recorded in `runs/` and are re-reported in RESULTS.json.

This is a **control task**. It is not looking for a new effect. It repairs two
named weaknesses in an effect already measured in BATCH-004
(`EV-AES-c66a80` OBS-B4-3; `DEC-20260803-baae70` limitations).

**TOY TIER.** Nothing here is a statement about full-round or deployed AES, and
no comparison to published cryptanalysis is made in either direction.

---

## 0. Instrument: REUSED, NOT REWRITTEN

I **reused** BATCH-004's binary. I did not rewrite the probe, and rewriting it
would have been the wrong act for a control task: the point of ITEM 1 is to
change **one** factor (the S-box) against a fixed key and stream, and a new
implementation would have added a second uncontrolled factor to the very
comparison being deconfounded.

| artifact | sha256 | provenance |
|---|---|---|
| `yoyo_sbox_v2` (binary, executed) | `d30e4d720317706043b263742062273d22fbe054f56a58a8b351f3bbb3fd9ff0` | byte-identical copy of BATCH-004 `TASK-20260803-367b1b/yoyo_sbox_v2` |
| `src/yoyo_sbox_v2.c` (read, not rebuilt) | `6bda2ab7f3c8e6dee358d3fcba52803e4e43f794f963bafabc51cc0de379bc9c` | BATCH-004 |
| `ref_aes.py` (executed) | `ce34acf6922738b969605418bc8efba73bd7cdcee5cb5d540ac1ef9c09bba67e` | byte-identical copy of BATCH-004 |

The binary and the reference were **copied** into this task directory so that
`ref_aes.py` would write its output beside itself rather than into a
prior-batch directory. No prior-batch file was edited or overwritten.

### Verification I performed myself before measuring

1. **Geometry.** Dumped from the binary actually executed:
   - `PW` (plaintext side, FORWARD ShiftRows diagonals):
     `[0,5,10,15] [4,9,14,3] [8,13,2,7] [12,1,6,11]`
   - `CW` (ciphertext side, INVERSE ShiftRows diagonals, `4*((j-r)%4)+r`):
     `[0,13,10,7] [4,1,14,11] [8,5,2,15] [12,9,6,3]`
   Both match the geometry this campaign requires. A replication in this
   campaign once got this wrong and read no signal.
2. **FIPS-197 pin, verified by me, under my own fresh pin seed 90210** (not
   BATCH-004's): C.1 KAT encrypt match `true`, decrypt match `true`, computed
   ciphertext `69c4e0d86a7b0430d8cdb78070b4c55a`, 5120 round-trip checks,
   0 failures, `pin_pass: true`.
3. **Random S-box pins** (`rand:20260803001`, `rand:20260803002`): bijective,
   5120 round-trips each, 0 failures, `pin_pass: true`. The FIPS-197 KAT is
   correctly reported as not applicable to these.
4. **Independent reference anchor.** The plain-Python, no-T-table `ref_aes.py`
   reproduced `enc_r` for r = 1..10 for all three S-boxes: `ANCHOR_PASS = True`,
   and it independently re-drew both random S-box tables and matched them.

---

## 1. ITEM 1 — the deconfounding design

### The defect being repaired

BATCH-004 ran three r=5 yoyo arms — AES 13.5x (27 hits), R1 11.0x (22), R2
20.5x (41) at 2^31 — under **three distinct seeds** 431001 / 431002 / 431003.
In this instrument the seed determines **both** the master key
(`key = splitmix(seed ^ 0xA5A5A5A5A5A5A5A5)`) **and** the plaintext/swap stream
(`thread_seed = seed ^ armid*C1 ^ (t+1)*C2`). So S-box, key and stream moved
together. The R1-vs-R2 difference is significant at two-sided p = 0.023 and
that design **cannot assign it to the S-box** rather than to key, stream, or
chance. Both reviewers flagged it (red team OBJ-6 / RC-3; validator; recorded
as an unresolved confound in `EV-AES-c66a80`).

### The design I chose, and why

I chose **BOTH** options the card offers, in a single balanced design:
**a fully crossed 3 (S-box) x K (seed) factorial with the SAME seed set used
across all three S-boxes.**

- Fixing `seed` and `armid` and varying only the S-box spec makes the master
  key bytes **identical** and the p0 / p1 / swap draw sequence **identical**
  across the three S-boxes, because neither the key draw nor the stream draw
  reads the S-box. Within a seed block the S-box is therefore the **only**
  factor that differs. This is exact pairing, not merely balance.
- Running K seeds per S-box simultaneously supplies the within-S-box,
  key-to-key variance that BATCH-004 had no estimate of at all.

Taking only one of the two options would have answered only half the question:
same-key-across-S-boxes isolates the S-box but leaves key-to-key spread
unmeasured, and several-keys-per-S-box measures that spread but re-introduces
stream variation into the S-box contrast. The crossed design gets both for the
same compute.

**Prediction to be checked as a design audit, not as a result:** the three arms
in a seed block must report the same `key_hex`. If they do not, the pairing
claim is false and I will say so and fall back to reporting the design as
balanced-but-unpaired.

### Arms (frozen)

r = 5, `amask = 1` (A = {0}), `smask = 1` (S = {0}), 2 threads, 2^30 trials per
arm, analytic null expectation 1.0 hits per arm.

| block | seed | armid | arms |
|---|---|---|---|
| K1 | 531001 | 1 | `D-AES-K1`, `D-R1-K1`, `D-R2-K1` |
| K2 | 531002 | 2 | `D-AES-K2`, `D-R1-K2`, `D-R2-K2` |
| K3 | 531003 | 3 | `D-AES-K3`, `D-R1-K3`, `D-R2-K3` |
| K4 | 531004 | 4 | `D-AES-K4`, `D-R1-K4`, `D-R2-K4` — **RUN ONLY IF BUDGET ALLOWS** |

Seeds are **fresh** (531xxx), not BATCH-004's 431xxx. Reusing 431001-3 at 2^30
would have produced an exact stream *prefix* of the BATCH-004 runs rather than
an independent measurement, since the thread seeds are unchanged and each
thread would simply run the first half of the same trial sequence.

Blocks are executed **in block order**, all three S-boxes within a block before
the next block starts, so that a budget halt leaves a **balanced** design over
whatever blocks completed. K1-K3 are mandatory; K4 is contingent.

### Frozen analysis and decision rules

Exposure is identical for every arm, so all tests are on raw counts.

- **T1 (primary) — S-box main effect.** Pool counts by S-box over completed
  blocks. Poisson likelihood-ratio statistic G^2 on 3 cells with equal
  exposure, 2 df, evaluated against chi-square(2). Threshold **alpha = 0.05**.
- **T2 — key main effect.** Same statistic pooling by seed block, (K-1) df.
- **T3 — full-cell homogeneity.** G^2 over all 3K cells, (3K-1) df, to detect
  overdispersion of any origin.
- **T4 — the specific BATCH-004 contrast.** Pooled R1 vs pooled R2, exact
  conditional binomial test (binomial(n = R1+R2, p = 1/2)), two-sided by
  doubling the smaller tail. This is the direct re-test of the p = 0.023
  finding.
- **T5 — per-arm liveness.** BATCH-004's frozen rule: excess factor >= 5x is
  ALIVE. At 2^30 the null is 1.0, so ALIVE means >= 5 hits.

### Predictions (frozen)

- **P1 (S-box-effect-is-real branch).** If the BATCH-004 R1-vs-R2 difference is
  a genuine property of those S-boxes, pooled rates should reproduce near
  R1 ~ 11x and R2 ~ 20.5x, T4 should be significant with the **same sign**
  (R2 > R1), and T1 should be significant.
- **P2 (confound branch).** If it was key/stream variation or chance, T1 is
  non-significant (p >= 0.05), T4 is non-significant or reverses sign, and the
  within-S-box key-to-key spread (T2/T3) is comparable to the between-S-box
  spread.
- **P3.** All arms remain ALIVE by T5 under all three S-boxes.
- **Expected central values under a common pooled rate**, from BATCH-004's
  (27+22+41)/3 = 30 per 2^31 = **15 hits per arm at 2^30**; per S-box over 3
  blocks, 45 hits.
- **Stated in advance, because it is the point of the task:** a **null** result
  on T1 and T4 **strengthens** the S-box-independence reading rather than
  weakening it. It would mean the apparent S-box effect was key variation all
  along, and that the three S-boxes are not distinguishable by this statistic
  at this exposure. It does **not** license the campaign's retired headline
  "nothing this campaign has found is specific to AES", which
  `CORR-20260803-791ca7` already scoped down; two random draws still bound the
  preserving fraction only at 0.224 (95% lower).
- **What no outcome here can establish:** anything about S-boxes not drawn,
  about round counts other than 5, about byte-width mechanisms not measured, or
  about full-round or deployed AES.

---

## 2. ITEM 2 — structure-destroyed controls at higher count

BATCH-004 ran these at 2^30 (null 1.0): `Y-AES-sd` 2 hits / 2.0x,
`Y-R1-sd` 0 / 0.0x, `Y-R2-sd` 4 / 4.0x. `Y-R2-sd` **breached** its
preregistered <= 2.5x band. The producer itself flagged that as a reason not to
lean on these controls; the validator ruled it an ordinary fluctuation (exact
tail 0.0190, look-elsewhere across three sd arms 0.056). The counts are thin
for the weight the ALIVE/DEAD verdicts place on them.

**Arms (frozen):** r = 5, `amask = 15` (all four plaintext words active, so no
diagonal-coset structure remains), `smask = 1`, **2^31 trials** (a 2x raise
over BATCH-004; 2^32 was not affordable inside 3600 s alongside ITEM 1, and
ITEM 1 is the stated priority), analytic null **2.0** hits per arm, 2 threads,
seed 531001, armid 1.

`SD31-AES`, `SD31-R1`, `SD31-R2`.

Seed 531001 / armid 1 is deliberately shared with block K1, so each sd arm
carries the **same master key** as its K1 main arm and differs from it in
`amask` alone. (The p0/p1 sequences diverge after the first trial because a
4-word re-randomisation consumes the stream differently from a 1-word one; the
key does not.)

### Frozen band and predictions

- Band carried over unchanged from BATCH-004: an sd arm is **within band** at
  excess <= 2.5x, i.e. **<= 5 hits** at 2^31.
- **P4.** All three sd arms within band. Under a true null the chance that a
  given arm exceeds 5 hits is P(X >= 6 | 2.0) = 0.0166, so a breach of any one
  of three is ~4.9% a priori — i.e. one breach among three would still be
  unsurprising and I say so **now**, before seeing them.
- **P5 (falsifier).** An sd arm at >= 5x (>= 10 hits at 2^31) would mean
  destroying the coset structure does not kill the statistic, which would
  undermine the ALIVE/DEAD verdicts the campaign has been reporting. That is
  the outcome that would hurt.
- Results are reported **beside** BATCH-004's 2^30 readings, and the two counts
  per S-box are also pooled (2^30 + 2^31 = 3 x 2^30 exposure, null 3.0).

---

## 3. ITEM 3 — the red team's control set (RC-1..RC-7)

Taken in the red team's stated order **after** items 1 and 2, as the card
directs, and as budget allows. Every item not reached will be **named** in
RESULTS.json together with what it would have settled. RC-3 and RC-6 are
subsumed by ITEMS 1 and 2 respectively; RC-1 was measured in BATCH-004's
segment 2 (unreviewed) and is not re-run here.

Planned reach order for anything left: **RC-7** (cheap: an AES-NI vs software
`enc_5` vector comparison, plus the non-T-table reference check of `enc_5`
under a random S-box, which `ref_aes.py` has already supplied above), then
stop. RC-2, RC-4, RC-5, RC-8 are expected NOT to be reached.

---

## 4. Budget and stopping

- Declared wall clock 3600 s, start 2026-08-03T02:57:59Z, **binding stop
  2026-08-03T03:57:59Z** (computed as start_epoch 1785725879 + 3600 =
  1785729479). Memory 8 GB. At most **2 threads** (one other producer runs
  concurrently).
- Section boundaries are stamped in `budget_stamps.jsonl`.
- **HALT at the binding stop**, record `halted_on_budget` truthfully, and NAME
  every piece of dropped work.
- Priority if the budget forces a choice: **ITEM 1 first**, then ITEM 2, then
  ITEM 3. Within ITEM 1, whole blocks, so the design stays balanced.
- A timeout or a halt is **resource exhaustion**, never negative evidence.
- Maximum runs 24. Planned measurement arms: 9 (mandatory) + 3 (sd) + 3
  (contingent K4) = 15, plus verification invocations.

## 5. Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    orchestration/model-policies.yaml routes this role to a GPT-5.6-family
    policy alias that Claude Code cannot resolve; subagent frontmatter supports
    only Claude models, so the resolved model is claude-opus-5.
  model_verified: false
  model_verified_reason: no adapter probe available in this harness
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```
