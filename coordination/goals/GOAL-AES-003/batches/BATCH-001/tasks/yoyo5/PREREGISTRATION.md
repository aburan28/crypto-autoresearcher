# YOYO-5 PRE-REGISTRATION (IMMUTABLE)

Written 2026-08-02, **before any cipher call in this session**.
Session start stamp: `2026-08-02T02:08:31Z`. Halt boundary: start + 2700 s =
`2026-08-02T02:53:31Z`.

**This file is frozen at the moment of writing. It is not edited afterwards.**
Any correction appears as a separate `PREREG-AMENDMENT-*.md` with its own UTC
stamp, never as an edit here.

Role: Executor. Nothing here is a claim about AES security. `claim_tier: toy`
(reduced-round, own-instrument). No literature comparison is made in either
direction; novelty is out of scope and is not assessed.

---

## 0. Status of the governing contract

There is **no `experiments/<EXP-ID>/specification.yaml` with `status: approved`
and non-null `approved_by`** for this object. The governing input is a task
message. Under the Executor contract this is a `specification_error` for a
*ledger* experiment. This session therefore runs as an **exploratory scratchpad
probe**: nothing is written to the repo or the ledger, no
`experiments/.../runs/<RUN-ID>/` package is created, no evidence record is
produced. The pre-registration discipline is applied in full anyway.

Missing-from-a-formal-contract fields (reported, not repaired):
`experiment_id`, `status`, `approved_by`, `budget.memory_gb`,
`budget.maximum_runs`, `stopping_rules`, `required_artifacts`,
`certificate.kind`.

**Certificate discipline**: pure measurement run. `certificate.kind: none`, set
explicitly. No solve, no relation, no key recovery is claimed or required.

---

## 1. Conventions, frozen

Reduced-round convention is the campaign's pinned one (`aes_reduced.py`
C1/C2/C3), i.e.

```
E_K^r(p) = ARK_r . SR . SB . [ ARK_i . MC . SR . SB ]_{i=r-1..1} . ARK_0 (p)
```

round keys = first `r+1` of the untruncated FIPS-197 AES-128 expansion; final
round drops MixColumns; initial ARK is not counted as a round. State is
column-major, `state[row r][col c] = byte[4c+r]`.

Decryption `D_K^r` is the exact inverse of `E_K^r` under the same round keys.

**Word structure, derived before measurement (this is algebra about the
instrument, not an observation):**

- Because the first keyed operation is `ARK_0` and the next is `SB` then `SR`,
  the natural *plaintext words* are the **forward diagonals**
  `PW[j] = { 4*((j+r) mod 4) + r : r = 0..3 }`, i.e.
  `PW[0]={0,5,10,15}`, `PW[1]={4,9,14,3}`, `PW[2]={8,13,2,7}`,
  `PW[3]={12,1,6,11}`. These are the sets that ShiftRows gathers into one
  column.
- Because the last operations are `SB`, `SR`, `ARK_r`, the natural *ciphertext
  words* are the **inverse-ShiftRows diagonals**
  `CW[j] = { 4*((j-r) mod 4) + r : r = 0..3 }`, i.e.
  `CW[0]={0,13,10,7}`, `CW[1]={4,1,14,11}`, `CW[2]={8,5,2,15}`,
  `CW[3]={12,9,6,3}`. (Same sets as `DIAGP` in the campaign's `sq.c`.)

**Derived positive-control theorem (pre-run, not measured).** Put
`u = SR(p ⊕ RK_0)` and `w = SR^{-1}(c ⊕ RK_r)`. Then for `r = 2`,

```
w[col j] = S( MC( S( u[col j] ) ) ⊕ RK_1[col j] )
```

column-wise and **independently across the four columns**: two-round AES is,
in word coordinates, four parallel independent bijections `F_j : u_j -> w_j`.
Swapping ciphertext word `j` between two ciphertexts therefore swaps exactly
`u_j` between the two corresponding plaintexts, and the zero-difference pattern
over plaintext words is **preserved exactly**, for every swap mask. This is the
positive control; it must read exactly, deterministically, or the instrument is
broken (V1).

---

## 2. The object, frozen

Parameters of one **trial**: key `K`, round count `r`, active plaintext-word
mask `A ⊆ {0,1,2,3}` (nonempty), swap mask `S ⊆ {0,1,2,3}` with
`S ∉ {∅, {0,1,2,3}}`, and a seed.

1. Draw `p0` uniformly at random. Draw `p1` by re-randomising, uniformly and
   independently, every byte lying in a word of `A`, rejecting the case where
   the resulting word-difference is zero in some word of `A` (so every word of
   `A` is genuinely active). Bytes outside `A` are equal in `p0`, `p1`.
2. `c0 = E_K^r(p0)`, `c1 = E_K^r(p1)`.
3. Form `c0'`, `c1'` by exchanging, for every `j ∈ S`, the bytes of ciphertext
   word `CW[j]` between `c0` and `c1`. (`c0'` takes `c1`'s word `j`, and vice
   versa; all other bytes unchanged.)
4. `p0' = D_K^r(c0')`, `p1' = D_K^r(c1')`.
5. Record `d = p0' ⊕ p1'`.

**Primary statistic** `Z = #{ i ∈ 0..15 : d[i] = 0 }` — the number of *cells*
(bytes) with zero difference in the decrypted pair. Range `0..16`. The full
17-bin histogram of `Z` is reported for every arm; never only the mode.

**Secondary statistic** `W = #{ j : d restricted to PW[j] is all-zero }`, the
number of zero-difference plaintext *words*. Range `0..4`. Full 5-bin histogram
reported.

`S ∈ {∅, {0,1,2,3}}` is excluded as **degenerate by construction**: those
swaps map the pair to itself or to its transposition, so `d` equals the
original difference and `Z`, `W` are trivially maximal. Recorded here so that
a maximal reading can never be mistaken for a finding.

---

## 3. The null, and the resolution

**PRP null (the meaningful null).** `E_K^r` replaced by a random permutation of
the 128-bit block, realised as full 10-round AES-128 under an independent key
(and its exact inverse), everything else in the pipeline byte-identical.
Matched data complexity, matched trial count, matched code path.

Under a random permutation with `S ∉ {∅, full}`, `p0'` and `p1'` are
essentially independent uniform blocks, so

```
Z ~ Binomial(16, 2^-8)
```

with (computed before any run, from the binomial):

| k | P(Z = k) | P(Z >= k) |
|---|---|---|
| 0 | 0.9392980958938164 | 1 |
| 1 | 0.05893635111490613 | 6.070190410618359e-02 |
| 2 | 1.7334220916148861e-03 | 1.7655529912774595e-03 |
| 3 | 3.172275723216785e-05 | 3.2130864459e-05 |
| 4 | 4.043096509982177e-07 | 4.0810e-07 |
| 5 | 3.805267303512637e-09 | 3.842e-09 |
| 6 | 2.7358130940286933e-11 | 2.76e-11 |

and `W ~ Binomial(4, 2^-32)`, so `P(W >= 1) = 9.313e-10 = 2^-30`.

**Resolution.** With `N` trials per arm the smallest per-trial event
probability that is detected with >=95% probability is `3/N`; the resolution in
bits is `log2(N/3)`. Every arm reports its achieved `N` and this number. An arm
whose resolution does not cover the null probability of the event it reports is
labelled **underpowered** in the same line as the number.

**Discriminating power is checked, not assumed.** Before belief, the same
statistic must separate the `r = 2` positive control from the PRP control by
many orders of magnitude. If a statistic returns readings for AES and for the
PRP that are within its own resolution, it is declared **non-discriminating**
and the arm is reported as carrying no information — the campaign has been
bitten by a statistic reading 0.4995 vs 0.4996.

---

## 4. Pre-registered predictions

Frozen. Not adjusted after runs begin. Not re-scored against any later model.

- **PR-0 (pinning).** The C AES-NI encryption path, the C software reference,
  `aes_reduced.py`, and pycryptodome agree bit-for-bit at every round count
  used, in BOTH directions, on the FIPS-197 known-answer vector and on random
  vectors. Decryption is pinned by the same standard: `D(E(x)) = x` and
  cross-implementation equality of `D` on random ciphertexts at every `r`.
- **PR-1 (positive control, deterministic).** `r = 2`, `A = {0}`, any admissible
  `S`: `W = 3` and `Z >= 12` in **every** trial, with `Z = 12` typical (bytes
  outside `PW[0]` all zero; the four bytes of `PW[0]` zero only by accident).
  Exactly: `W = 3` in 100% of trials.
- **PR-2 (the object).** If the object is real to depth `r*`, then for every
  `r <= r*` the observed `Z`-histogram differs from `Binomial(16, 2^-8)` by an
  amount larger than the arm's resolution, and in particular
  `P(W >= 1) >> 2^-30`. The falsifiable content is **the exact largest `r` at
  which the AES arm departs from the PRP arm by more than the resolution**.
- **PR-3 (the specific 5-round claim under test).** At `r = 5`, `A = {0}`, the
  distribution of `Z` is **not** `Binomial(16, 2^-8)`. This is the claim the
  session exists to test. Its negation — agreement with the binomial to within
  the achieved resolution — is a complete result and is to be reported as the
  death round with its resolution.
- **PR-4 (decay requirement / artifact tell).** At `r = 10` the AES arm must
  read as the PRP arm does. A signal **flat across round counts**, in
  particular one present at `r = 10`, is the canonical instrument fault and
  fires V4 — it is not a finding.
- **PR-5 (monotone death).** The excess over the null is expected to be
  non-increasing in `r`. A non-monotone reading (dead at `r`, alive at `r + 1`)
  is reported as an anomaly and treated as suspect, not as a finding.

### Decision rule, frozen

For each arm `(r, A, S)` report: `N`, the full 17-bin `Z` histogram, the full
5-bin `W` histogram, the same for the PRP arm at identical `N`, the exact
binomial null probability of the observed `Z >= k` tail for the largest `k`
observed, and the resolution in bits. "Alive at `r`" means the AES arm's
reading has null probability below `2^-20` **after** multiplying by the number
of arms tested (a Bonferroni factor recorded explicitly) **and** the PRP arm at
the same `N` does not show it **and** the reading is not flat across rounds.
No other statistic may be substituted after the fact.

---

## 5. VOID conditions

If any of these fires, the affected readings are **VOID**, classified
`invalid_measurement`, and are **not** reported as a negative observation.

- **V1**: PR-1 fails (`r = 2` positive control does not read `W = 3` in 100% of
  trials). Instrument broken. **Checked first; execution stops if it fires.**
- **V2**: PR-0 fails — any cross-implementation disagreement, in either
  direction, at any round count.
- **V3**: `D_K^r(E_K^r(x)) != x` for any tested `x`, `r`. Decryption path
  broken.
- **V4**: The AES arm's excess is flat across `r` including `r = 10` (artifact
  tell).
- **V5**: The PRP control arm departs from `Binomial(16, 2^-8)` by more than
  its own resolution. That would mean the harness, not the cipher, produces the
  reading; every AES reading in the session becomes uninterpretable.
- **V6**: Trial construction degenerate — any trial in which `p0 = p1`, or in
  which `S` is empty or full, or in which a word of `A` has zero difference.
  Counted and reported; a nonzero count voids the arm.
- **V7**: Wall-clock halt at `2026-08-02T02:53:31Z`. Runs not started are
  reported as not run. **A budget halt is never reported as a null result and
  never as evidence about AES.**

---

## 6. Planned run grid (as intended before execution)

Priority order, executed top-down until the halt boundary.

1. **PIN** — four-way agreement, both directions, `r = 1..10` (blocks all).
2. **PC** — PR-1 at `r = 2`, `A = {0}`, all 14 admissible `S`, >= 10^4 trials.
3. **PRP control** — `r`-matched, `N` matched, `A = {0}`, `S = {0}`.
4. **AES sweep** — `r ∈ {3,4,5,6}`, `A = {0}`, `S = {0}`, `N >= 2^30`.
5. **`r = 10`** decay check (PR-4).
6. **Swap-mask sweep** — all 14 admissible `S` at `r ∈ {3,4,5}`.
7. **Active-mask sweep** — `A ∈ {{0},{0,1},{0,1,2},{0,1,2,3}}` at `r ∈ {4,5}`.
8. **Iterated yoyo** — re-encrypt `(p0', p1')` and repeat the swap for up to 8
   generations, recording `Z` per generation. Run only if budget remains.

Achieved `N` is budget-limited; any shortfall is reported as achieved
resolution, not smoothed over.

## 7. Sources of randomness, frozen

Master seed **`20260802`**. All keys, plaintexts and per-trial randomness in
the C program come from a documented deterministic `splitmix64` stream seeded
from `master_seed`, `arm_index` and `thread_index`; every arm records its exact
seed. No `rand()`, no `xorshift64` (prior-campaign confounder). Any run reported
as a signal is repeated with a different master seed and different keys before
it is reported at all.

## 8. What this session may not do

- May not conclude that a heuristic is validated or refuted.
- May not declare a hypothesis supported, rejected, or closed.
- May not assess novelty, in either direction.
- May not infer anything about full-round or deployed AES.
- May not report a budget halt or an infrastructure failure as mathematical
  evidence.
