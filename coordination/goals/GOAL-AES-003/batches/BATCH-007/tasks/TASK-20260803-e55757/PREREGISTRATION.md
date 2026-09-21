# PREREGISTRATION — TASK-20260803-e55757

RANK 2 of BATCH-007, GOAL-AES-003. **Independent re-execution of the 27 RC-8
S-box draws.** Written and timestamped BEFORE any measurement was taken; the
budget stamp `READING_DONE_ENTERING_PREREGISTRATION` at epoch 1785781911
precedes the first compile and the first arm.

## Inference block

```
policy:            executor-implementation
requested_policy:  executor-implementation
resolved_model:    claude-opus-5
fallback_used:     true
model_verified:    false          # no adapter probe available in this harness
standing_basis:    0137a051eb5828789eb267fa83c8278086578d4c
```

`fallback_used: true` because `orchestration/model-policies.yaml` names a
GPT-5.6-family alias that Claude Code cannot resolve; the actual resolved
model is `claude-opus-5` (CLAUDE.md, Model policy note).

## Claim tier

TOY. Reduced-round AES-128 permutation, r=5, one machine, 2^30 trials per
draw, 27 drawn bijective S-boxes. Nothing here is a statement about
full-round or deployed AES, and no comparison to published cryptanalysis is
made in either direction (RQ-AES-003 R3). A timeout or a killed process is
resource exhaustion, never negative evidence.

## What is being replicated, and what "replication" means here

BATCH-006 TASK-20260803-0764fc measured, for each of 27 randomly drawn
bijective S-boxes, the yoyo statistic `W>=1` over 2^30 trials at r=5, and
classified each draw under the frozen BATCH-004 rule. It found 25 of 27
ALIVE and reported a one-sided 95% Clopper-Pearson lower bound of
**0.784700038857546** on the preserving fraction. That number rests on one
implementation (`yoyo_sbox_v2`) in one session; the BATCH-006 validator
intended to re-execute it, hit ~10.6 h against a 4800 s budget, and named
the omission (EV-AES-9794e1 `unresolved_confounds[0]`).

**The instrument is new; the objects are the same.** I use the same 27
S-box seeds (20260803701 .. 20260803727), the same arm seed 631001, armid 1,
2 threads, log2N 30, rounds 5, amask 1, smask 1. Because the S-box draw, the
key derivation, the per-thread trial split and the trial stream are all
deterministic functions of those parameters, an implementation that is
*correct* must reproduce BATCH-006's counts **exactly, integer for integer**.
This is bit-exact replication of a rare-event count on the same sample, not
an independent resampling. Replicating different draws would answer a
different question and is out of scope for this card.

Consequently the RNG (splitmix64), the Fisher-Yates-with-rejection S-box
draw, the plaintext/active-word draw with its rejection condition, the
trivial-swap exclusion, the geometry `PW[j][row]=4*((j+row)%4)+row` and
`CW[j][row]=4*((j-row) mod 4)+row`, and the thread seeding
`seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15` are all part of the
*specification of the object* and are reproduced deliberately. They are not
copied code: they are re-implemented from the documented definitions.

## How my instrument differs from `yoyo_sbox_v2`

I read `yoyo_sbox_v2.c.readonly_copy` to learn what object is measured, as
the card permits. I wrote `rc8probe.c` myself. Deliberate differences:

1. **No T-tables.** `yoyo_sbox_v2` encrypts with four 32-bit T-tables that
   fuse SubBytes+ShiftRows+MixColumns. `rc8probe` keeps the state as 16
   bytes and applies SubBytes, ShiftRows, MixColumns and AddRoundKey as
   four separate byte-level steps, with GF(2^8) products from small
   multiply tables (mul2, mul3, mul9, mul11, mul13, mul14).
2. **A different inverse cipher.** `yoyo_sbox_v2` uses the *equivalent
   inverse cipher* with InvMixColumns-transformed round keys (`dk`) and
   U-tables. `rc8probe` uses the *direct* inverse — AddRoundKey,
   InvShiftRows, InvSubBytes, InvMixColumns in the straight reversed order,
   using only the forward round keys. These are different code paths that
   must agree; if they disagree the round-trip check fails.
3. **A different AES S-box construction.** `yoyo_sbox_v2` finds the GF(2^8)
   inverse by an O(256^2) brute-force search over products. `rc8probe`
   builds log/antilog tables over the generator 0x03 and inverts by
   `antilog[255-log[x]]`, then applies the affine map by byte rotation.
   Agreement on all 256 entries is checked against the FIPS-197 pin below.
4. **A different key-expansion loop** (word-oriented over 4-byte words with
   an explicit RotWord/SubWord/Rcon, rather than the fused byte loop).

## Pins and validity checks, all BEFORE measurement

- **P1 FIPS-197 C.1 known-answer vector.** AES-128, key
  `000102030405060708090a0b0c0d0e0f`, plaintext
  `00112233445566778899aabbccddeeff`, expected ciphertext
  `69c4e0d86a7b0430d8cdb78070b4c55a`, at r=10 through the same `enc_r` used
  for measurement, and the decryption direction back to the plaintext
  through the same `dec_r`. **If P1 fails, no measurement is reported.**
- **P2 Bijectivity.** Every drawn S-box is verified to be a permutation of
  0..255 in both directions (`ISBOX[SBOX[x]]==x` and `SBOX[ISBOX[x]]==x`)
  before it is used. A non-bijective draw is refused, not measured.
- **P3 Round-trip under the drawn S-box.** For each draw, 512 random
  (key, plaintext) pairs are round-tripped at every r in 1..10 = 5120
  checks, exactly as BATCH-006 did, since `dec_r` must invert `enc_r` for
  the yoyo statistic to mean anything.
- **P4 S-box table identity.** For each seed I compare my drawn 256-byte
  table against the table BATCH-006 archived in
  `sboxes/sbox_rand_<seed>.json`. This is an independent check that the two
  implementations are drawing the *same object*, and it is reported
  separately from the measurement so that a draw mismatch cannot be confused
  with a count mismatch.
- **P5 Cross-implementation anchor at a cheap size.** Before the full runs I
  execute one arm at log2N=24 with `rand:20260803701` and confirm my probe
  and the archived `yoyo_sbox_v2` binary agree there. (This runs the other
  binary only as a *check on my own code*; every reported number comes from
  `rc8probe`.)

## The decision rule — one criterion only

Let `X` be the observed `W>=1` count on non-trivial trials and
`v = nontrivial_trials * 4 / 2^32` the matched analytic null.

> **ALIVE iff `X/v >= 5` AND the one-sided Poisson tail
> `P(K >= X | lambda = v) < 1e-6`.**

This is the strict BATCH-004 rule (BATCH-004
`TASK-20260803-367b1b/PREREGISTRATION.md` line 236-237) and, per
CORR-20260803-2cefa6, it is the **only** criterion this campaign ever froze.
BATCH-005's "at least 5x" form presents itself in its own text as a
quotation of this rule and drops the Poisson conjunct while quoting; a
defective restatement does not create a rule. **I will report exactly one
reading.** I will not compute or report a second reading, a "not DEAD"
reading, or a pooled bound; reporting two readings side by side is how this
campaign came to claim a 0.90 bound it had not earned.

The bound is the **one-sided 95% Clopper-Pearson lower bound** on
`p = ALIVE/n`, `LB = BetaInv(0.05; k, n-k+1)` for `k < n`, computed exactly
in `mpmath`/`scipy`-free form from the incomplete beta inverse; this is the
same estimator BATCH-006 used and I recompute BATCH-006's 0.784700038857546
from `k=25, n=27` as an arithmetic check on the estimator itself before
applying it to my own `k`.

## Predictions, registered now

**Primary prediction (per-draw exact agreement).** For every one of the 27
draws, my `W_ge1_nontrivial`, `trivial_swaps_excluded`, `whist` and
`W_ge1_by_word` will equal BATCH-006's **exactly**. I expect 27/27 exact
agreement on all four fields, including the by-word vectors, because the
trial stream is deterministic and both implementations claim to implement
the same permutation. This is a strong, falsifiable, all-or-nothing
prediction: any single mismatched integer refutes it.

**Derived prediction.** ALIVE count = 25, the two non-ALIVE draws are
B11 (`rand:20260803711`, X=6, tail 5.94e-4 fails the 1e-6 conjunct) and
B25 (`rand:20260803725`, X=9, tail 1.13e-6 fails the 1e-6 conjunct), and the
recomputed bound = 0.784700038857546.

### What would indicate an instrument fault rather than sampling

Sampling noise is **not an available explanation here**, because the sample
is not redrawn. Registered interpretation ladder, in advance:

- **All 27 agree exactly.** Prediction confirmed; 0.7847 becomes a
  two-implementation number.
- **A systematic disagreement** — every draw's count differs, or the counts
  differ in a patterned way (e.g. all mine larger), or `trivial_swaps_excluded`
  differs on the draws where BATCH-006 recorded 1 or 3 — is an
  **instrument fault in one of the two implementations**, and the pins tell
  me which: if P1 (FIPS-197) or P3 (round-trip) fails, the fault is mine;
  if P1 and P3 and P4 all pass and the counts still differ systematically,
  the disagreement is a real finding about the two instruments and must be
  reported as such, not reconciled.
- **One or two draws disagree while the rest match exactly** is the most
  diagnostic outcome: it cannot be a shared-convention difference (those are
  systematic) and it cannot be sampling (there is no resampling). It points
  at a data-dependent divergence — a rare byte pattern hitting different
  code paths — and I would report the exact disagreeing draws, their seeds,
  and the fact that I could not localise it within budget.
- **A P4 S-box mismatch on some seed** means I am not measuring the same
  object on that seed, and I would report that draw as NOT REPLICATED rather
  than as a count disagreement.

**If my bound differs from 0.7847, that is the finding.** I will not adopt
BATCH-006's numbers to reconcile it, and I will not assume the error is mine
by default. A replication that disagrees is informative in both directions.

## Absence claims

I make none in advance. If any claim of the form "X has never been measured
in this repository" appears in my RESULTS.json, it will carry the explicit
list of paths searched and the search commands, per CORR-20260803-c92db5.

## Budget and halt

5400 s wall, 8 GB, at most 2 threads (another producer may be running),
at most 35 runs. Start 2026-08-03T18:28:57Z (epoch 1785781737); **computed
binding stop 2026-08-03T19:58:57Z (epoch 1785787137)**. Section boundaries
are stamped in `budget_stamps.jsonl`.

BATCH-006's arms took ~162 s each at 2 threads with a T-table implementation.
My byte-oriented probe will be slower per trial, so **27 arms at 2^30 trials
may not fit.** Registered policy, in advance of knowing the throughput: I
run the arms **in the fixed order B01, B02, ... B27**, never starting an arm
that cannot finish before the stop minus a 300 s reserve for analysis, and
I **name every arm not run** with its reason in `RESULTS.json`. I will not
shrink log2N to fit more arms: a count at 2^24 is not comparable to
BATCH-006's count at 2^30, and a partial replication honestly bounded is
worth more than 27 arms measured against the wrong object. `halted_on_budget`
is recorded truthfully.

I will run `json.load` on my own `RESULTS.json` before finishing and record
that I did.
