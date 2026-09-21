# PREREGISTRATION — TASK-20260803-a0a7b9

**Written 2026-08-05, after SEARCH_RECORD.md and BEFORE any arm of this task was
compiled or run.** Order of artifact creation: `budget_stamps.jsonl` →
`SEARCH_RECORD.md` → this file → instrument v4 → runs → `RESULTS.json`.

**Toy tier.** Every statement below concerns a reduced-round software SPN probe
at ≤ 2^34 trials. Nothing here is about full-round or deployed AES, and no
comparison is made to published cryptanalysis in either direction.

---

## 0. Declared non-blindness (protocol deviation, disclosed)

I read the prior arms before writing this preregistration, exactly as BATCH-008
did, and I disclose it:

- `K-EQUIV-R5-K1-A2` (BATCH-008): r=5, aes, amask 1, smask 1, 2^30 trials, seed
  531001, armid 1, threads 2 → **W_ge1 = 14**, analytic null 1.0.
- `K-R10-NULL-P30` (BATCH-008): identical but r=10 → **W_ge1 = 1**.
- BATCH-006's 27 random-S-box r=5 arms → mean 15.48.
- EV-AES-8b8dcf OBS-B8-3: unpaired ratio interval **[2.13, 592]**, exact
  two-sided p = 9.77e-4.

I was required to read these to build a *matched* control (same seed, armid,
thread count, masks, exposure) and to compute a paired analysis against them.
The cost is that this preregistration is not blind to the effect size it is
controlling. It is nonetheless written before the control's own outcome exists,
which is the property that matters for the decision rules in §4 and §6.

---

## 1. The object being substituted, and why this is a section 3 null object

### 1.1 What is held fixed

Everything except the cipher:

| Held fixed | Value |
|---|---|
| probe geometry PW (forward ShiftRows diagonals) | `[0,5,10,15] [4,9,14,3] [8,13,2,7] [12,1,6,11]` |
| probe geometry CW (inverse ShiftRows diagonals) | `[0,13,10,7] [4,1,14,11] [8,5,2,15] [12,9,6,3]` |
| active-word mask `amask` | 1 |
| swap mask `smask` | 1 |
| plaintext draw + re-randomisation-with-rejection loop | byte-identical code path |
| trivial-swap exclusion rule | byte-identical code path |
| W computation and the k-prefix counters | byte-identical code path |
| trials, seed, arm id, thread count | 2^30, 531001, 1, 2 |
| RNG family | splitmix64, the campaign's own |

### 1.2 What is substituted

The map `E` itself. Not the S-box, not the round count, not the key: the whole
cipher is replaced by a **uniformly random bijection on 128 bits**, realised as
an exactly lazily-sampled ideal permutation.

A uniform bijection on 2^128 points cannot be stored. It does not have to be.
The probe makes exactly **four** oracle queries per trial — `E(p0)`, `E(p1)`,
`D(c0')`, `D(c1')` — so the permutation can be sampled *lazily* and exactly,
one trial at a time, keeping only that trial's own two forward pairs:

```
E(p0) = c0      c0 ← uniform 128 bits
E(p1) = c1      c1 ← uniform 128 bits, rejected if c1 == c0
c0', c1'  ← the SAME swap code as every other arm
D(c0') = p0     if c0' == c0        (consistency with the pair already sampled)
       = p1     if c0' == c1
       = q0     otherwise; q0 ← uniform 128 bits, rejected if in {p0, p1}
D(c1') = p1     if c1' == c1
       = p0     if c1' == c0
       = q1     otherwise; q1 ← uniform 128 bits, rejected if in {p0, p1, q0}
```

The rejections are exactly the injectivity constraints of a permutation, so
within a trial this is the *exact* uniform distribution over bijections
conditioned on the queries made. Note `c0' ≠ c1'` whenever the swap is
non-trivial, so `q0 ≠ q1` is a genuine constraint and is enforced.

### 1.3 Why this is fair — and what would make it unfair

**Fair, because:**

1. **It substitutes the cipher, not a component.** There is no round function,
   no key schedule, no S-box, no MixColumns and no round count in the surrogate.
   Nothing of the SPN survives. This is the substitution the batch objective
   names and the one SEARCH_RECORD.md confirms has never been made.
2. **The analytic null the campaign divides by is exactly this object's law.**
   The instrument's `null_expectation_analytic = trials · 4 · 2^-32` is derived
   from "q0 and q1 are two distinct uniform 128-bit values". This arm therefore
   *measures* the number the ALIVE/DEAD rule has always *assumed* — the measured
   PRP null that BATCH-005 RC-6 declared and skipped.
3. **Cross-trial consistency is provably irrelevant at this exposure.** Trials
   are sampled independently, i.e. the surrogate is not globally a single
   permutation. Over N ≤ 2^34 trials there are ≤ 2^36 queries in a 2^128 domain;
   the probability that any two queries across trials collide and would have
   forced a shared answer is ≤ 2^72 / 2^128 = **2^-56**. The arm is an exact
   ideal permutation up to that bound, which is ~2^26 times smaller than the
   2^-30 event being counted. This is stated as a bound, not a measurement.
4. **The plaintext stream is bit-identical to the arm it controls.** The
   surrogate draws its ciphertexts from a *second, disjoint* splitmix64 stream,
   so `p0`/`p1` are the same 128-bit pairs, in the same order, on the same
   threads, as `K-EQUIV-R5-K1-A2`. §3.1's digest check proves this rather than
   asserting it.

**Unfair, and I would have to withdraw it, if:**

- **(U1)** the two splitmix64 streams overlap. Every splitmix64 state lies on a
  single orbit of period 2^64 under `s ← s + γ`, so the ciphertext stream is a
  *shift* of the plaintext stream by some `k = (s_C − s_P)·γ^{-1} mod 2^64`
  steps. If `k` were small the ciphertexts would be recycled plaintexts. The
  instrument computes `k` for every thread and I preregister the acceptance
  condition `min(k, 2^64 − k) > 2^40` for every thread, against a per-thread
  consumption of ≤ 2^36 draws. Failing this invalidates the arm.
- **(U2)** the surrogate's own self-check fails: its k = 1, 2, 3 prefix counters
  must sit at the exact analytic prefix nulls (§3.2). A surrogate that is
  mis-sampled will show it there, at counts of 10^7 / 10^5 / 10^2 where the
  statistics are sharp, long before the 2^-30 event.
- **(U3)** the probe code path differed between the surrogate and the real arm
  in any respect other than the four oracle answers. Guarded by the
  additions-only diff and the bit-exact reproduction in §3.3.
- **(U4)** — the one I cannot fully exclude — if the r=5 excess were driven by a
  *specific interaction* between the probe geometry and 128-bit-block ciphers of
  a kind an ideal permutation does not model, the surrogate would read at the
  null while a "realistic but structureless" cipher would not. I record this as
  a residual limitation, not a defence.

### 1.4 The obvious objection: "you already have the r=10 arm"

The task card requires this to be addressed. It is a real objection and the
answer is specific.

`K-R10-NULL-P30` is **r = 10 of the same one-parameter family** whose r = 5
point is under test: same T-table SPN, same AES S-box, same FIPS-197 key
schedule, same key `bdf3823182ad657dab3d556b3886ba72`, same everything but
`rounds`. Increasing `rounds` is exactly "increasing the parameter meant to
destroy the signal" — the inventor-protocol §3 *decay check*. It is a necessary
control and the campaign has it. It is **not** a null object, because a null
object substitutes the object, and r=10 AES is not a substitution of AES; it is
more of it.

Three things this arm adds that r=10 cannot:

1. **It removes the round function entirely.** r=10 still evaluates the AES
   round function 10 times; if the excess came from the T-table/diagonal
   interaction rather than from five rounds specifically, r=10 could suppress it
   for reasons unrelated to the mechanism under test. The ideal permutation has
   no round function to suppress.
2. **It converts the analytic null into a measured one.** Every ALIVE/DEAD
   verdict in five batches divides by `4·2^-32` and no arm has ever checked that
   denominator. This arm checks it, at the exact geometry and masks used. That
   is BATCH-005 RC-6's own stated open item, verbatim.
3. **It is not confounded with the campaign's own hypothesis.** Reading r=10 at
   the null is *predicted by* the hypothesis under test (more rounds ⇒ decay).
   Using a prediction of the hypothesis as the hypothesis's control is circular.
   The ideal permutation's reading is predicted by neither branch a priori,
   which is what makes it diagnostic.

I therefore run the new control **and** keep the existing r=10 arm as the decay
check, which is what §3 asks for: a decay check *and* a null object, not one
standing in for the other.

---

## 2. Runs (all preregistered; anything added later is flagged as unpreregistered)

| id | cipher | r | amask | smask | log2N | seed | armid | thr | purpose |
|---|---|---|---|---|---|---|---|---|---|
| `N0-IDEAL-PIN` | ideal | – | – | – | – | – | – | – | surrogate self-pin, §3.2 |
| `N1-IDEAL-P30` | ideal perm | – | 1 | 1 | 30 | 531001 | 1 | 2 | **primary null object**, matched exposure to `K-EQUIV-R5-K1-A2` |
| `N2-IDEAL-P33` | ideal perm | – | 1 | 1 | 33 | 531001 | 1 | 2 | high-precision null rate (expected ≈ 8) |
| `P1-R5-PAIR` | AES SPN | 5 | 1 | 1 | 30 | 531001 | 1 | 2 | RC-11 + bit-exact repro of `K-EQUIV-R5-K1-A2` |
| `P2-R10-PAIR` | AES SPN | 10 | 1 | 1 | 30 | 531001 | 1 | 2 | RC-11 + bit-exact repro of `K-R10-NULL-P30` |
| `E0-KAT` | AES SPN | – | – | – | – | – | – | – | FIPS-197 C.1 KAT + round-trip pin of v4 |

Max runs 30; six planned. Memory: the ideal arm allocates nothing beyond the
existing per-thread job structs plus a bounded hit list; ≪ 8 GB.

Stopping rule: hard halt at `binding_stop_utc` = **2026-08-05T16:30:35Z**
regardless of state. Any arm not started by then is reported as not reached.

---

## 3. Validity gates (an arm failing these is `invalid_measurement`, never evidence)

### 3.1 Plaintext-stream identity
v4 accumulates a per-thread order-sensitive 64-bit digest of every `(p0, p1)`
pair. **Gate:** `N1-IDEAL-P30` and `P1-R5-PAIR` and `P2-R10-PAIR` must print
**identical** `plaintext_stream_digest` values. This is the proof that the null
object holds the probe input fixed.

### 3.2 Surrogate self-pin
`N1`/`N2` prefix counters at k = 1, 2, 3 must satisfy
`|obs − exp| ≤ 4·sqrt(exp)` against
`exp_k = trials·(1 − (1 − 2^-8k)^4)`. Plus (U1): every thread's stream shift
`min(k, 2^64−k) > 2^40`.

### 3.3 Instrument equivalence (BATCH-008 standard)
v3 → v4 is **additions only**. The diff is shipped. `P1-R5-PAIR` must
reproduce `K-EQUIV-R5-K1-A2` and `P2-R10-PAIR` must reproduce `K-R10-NULL-P30`
**bit-exactly** on every shared field: `key_hex`, `thread_seeds`,
`trivial_swaps_excluded`, `W_ge1_nontrivial`, `W_ge1_by_word`, `whist`,
`W_ge1_prefix_k`. Any mismatch invalidates all v4 arms.

### 3.4 Cipher pin
`E0-KAT`: FIPS-197 C.1 known-answer vector and 512×10 round-trip checks must
pass, as in v3.

---

## 4. RANK 1 — the frozen decision rule

Let `x` = `W_ge1_nontrivial` of the null object and `m` = its
`null_expectation_analytic`. Define the **null-object rate ratio**
`R_null = x/m`, with an exact (Garwood) Poisson 95% CI on `x` mapped through
`1/m`. Let `R_5 = 14/1.0 = 14` be the frozen r=5 reading at 2^30.

The r=5 vs null-object comparison uses the **exact conditional-binomial (Poisson
ratio) test** at matched exposure — the same machinery EV-AES-8b8dcf used for
[2.13, 592] — giving a two-sided p and a ratio CI.

**Preregistered outcomes, mutually exclusive, decided in this order:**

- **OUTCOME-A — the excess does NOT survive cipher substitution.**
  `R_null`'s 95% CI contains 1, **and** the exact test of r=5 against the
  null object at matched exposure gives p < 0.01.
  *Reading:* the r=5 excess is a property of the round structure and survives
  its first real control.

- **OUTCOME-B — the excess SURVIVES cipher substitution.**
  `R_null`'s 95% CI lower bound > 1, **and** the exact test of r=5 against the
  null object does **not** reject at p < 0.01.
  *Reading:* the excess is a property of the probe geometry, and five batches of
  yoyo readings are measurements of the instrument rather than of the cipher.
  **If OUTCOME-B occurs it is written in the FIRST LINE of `RESULTS.json`,
  unsoftened**, as the task card requires.

- **OUTCOME-C — ambiguous.** Anything else, including partial elevation
  (CI lower bound > 1 *and* p < 0.01, i.e. the null object is elevated but by
  less than r=5). Reported as ambiguous with both intervals and no
  interpretation beyond the arithmetic.

I assign no evidence strength, no hypothesis status and recommend no promotion
under any outcome. These are readings.

**What falsifies what, stated plainly.** OUTCOME-B falsifies the campaign's
working reading of the r=5 excess as a cipher property. OUTCOME-A does not
*confirm* that reading — it removes one specific artifact explanation
(probe geometry + counting under a structureless cipher) and leaves the others
standing. A single 2^30 arm with an expected count of 1 has weak power against
small elevations; that is why `N2` at 2^33 is run, and why the CI, not the point
estimate, is the reported quantity.

---

## 5. Prediction (recorded so it can be wrong)

I predict **OUTCOME-A**: `N1` reads 0–4 hits against an expectation of 1, and
`N2` reads within a few of 8. I hold this at maybe 4:1 and I record the odds so
that a surprise is visible as a surprise. The prior comes from §1.3 point 2 —
the analytic null *is* this object's law, and the three prefix counters at
k = 1, 2, 3 in every arm ever run (e.g. `K-EQUIV-R5-K1-A2`: 16677270 / 65454 /
280 against 16679167.75 / 65534.50 / 256.00) already sit close to their exact
nulls, which is weak prior evidence that the probe's geometry does not by itself
manufacture zero-diagonals. It is weak because the k = 3 counter, 280 against
256, is itself +1.5σ, and the k = 4 counter is the one in question.

---

## 6. RANK 2 — RC-11, the trial-index pairing

v4 logs `(thread, trial_index)` for every non-trivial W ≥ 1 hit. `P1` and `P2`
consume an identical plaintext and swap stream by construction (§3.1 proves it),
so trial index `t` on thread `j` is the **same input pair** in both arms and the
pairing is real.

Build the 2×2 table over the 2^30 paired trials:
`n11` (hit in both), `n10` (r=5 only), `n01` (r=10 only), `n00`.

- **Test:** exact McNemar, i.e. two-sided binomial(`n10 + n01`, 1/2) on the
  discordant pairs.
- **Interval:** Clopper-Pearson 95% CI on `p = n10/(n10 + n01)`, mapped to the
  rate ratio `p/(1 − p)`.

**Preregistered prediction, and the honest part of it:** I predict `n11 = 0`.
If `n11 = 0` then `n10 = 14`, `n01 = 1`, the discordant pairs are the full
counts, and the paired interval **equals the unpaired [2.13, 592] exactly** —
because the unpaired conditional-binomial test on 14 vs 1 at matched exposure
*is* the same binomial(15, 1/2) computation. In that case **RC-11 does not
sharpen the interval, and I will say so rather than dress it up.** Its value is
then that it converts an assumed pairing into a measured one and closes
OBS-B8-3's stated caveat.

**What would be a surprise, and it would be a large one:** `n11 > 0`. A trial
index that hits in both the 5-round and the 10-round arm would mean the event is
determined by the *input pair* rather than by the cipher — a direct
probe-geometry tell, and under the null of independent hits its probability is
about `14 · 1 / 2^30 ≈ 1.3e-8`. If `n11 > 0` I report it beside the OUTCOME-B
line at the top of `RESULTS.json`.

**Secondary, unpreregistered-if-added:** the hit trial indices also permit a
clustering check (per-thread balance, index uniformity). Any such check is
labelled `unpreregistered_addition` in `RESULTS.json`.

---

## 7. Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  requested_policy_source: >-
    AGENTS.md default for the executor role; the TASK-20260803-a0a7b9 handoff
    carries no inference key.
  resolved_model_id: claude-opus-5
  resolved_model_display_name: Opus 5
  fallback_used: true
  fallback_reason: >-
    executor-implementation routes to a GPT-5.6-family alias in
    orchestration/model-policies.yaml, which Claude Code cannot resolve
    (CLAUDE.md model policy note).
  model_verified: false
  reasoning_effort: null
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
  independent_session: false
```

**Parse statement:** the YAML blocks in this file were parsed whole with
`yaml.safe_load` before this task finished; see `RESULTS.json`
→ `artifact_parse_checks`.
