# PREREGISTRATION -- TASK-20260802-4500d4

Independent re-execution of the segment-3 four-zero-matrix arms of
GOAL-AES-003 BATCH-002 (producer task TASK-20260802-142a4b), which were
measured after that batch's reviewers had been dispatched and which
EV-AES-d8a13e explicitly excludes as carrying no weight.

**Written and frozen BEFORE any counting run was started.** The matrix
verification (section 2) was run before this file, because a singular M1 would
have ended the task; it is a property of the matrix, not of the object under
test, and it constrains no prediction below. All predicted values in section 4
were fixed before the first invocation of the counting engine.

Claim tier: TOY. Nothing here is a statement about full-round or deployed AES,
and no comparison to published cryptanalysis is made or implied in either
direction (RQ-AES-003 R3).

## 1. Object measured

Identical to the object BATCH-002's `cnt.c` measures; its source was read to
extract the conventions and no line of it was copied, compiled or executed.

- State: 4x4 bytes, column-major words, byte `4*c + t` = row `t` of column `c`.
- Input set: the full 2^32 coset of the diagonal `D_0` = state bytes
  {0, 5, 10, 15}, the remaining 12 bytes held at a fixed `base`.
- Cipher: `r`-round AES-shaped SPN, C1 convention -- AddRoundKey, then `r-1`
  rounds of SubBytes/ShiftRows/MixColumns(M)/AddRoundKey, then a final round
  with SubBytes/ShiftRows/AddRoundKey and NO mixing layer. AES-128 key
  schedule, AES S-box, ShiftRows row rotations.
- Mixing layer: configurable `M` over GF(2^8), modulus 0x11b, applied
  column-wise, `M[row][col]` read row-major from a 32-hex-character string.
- Projection: `pi_{j0}(c)` reads the four bytes at
  `ID_{j0} = {4*((j0 - t) mod 4) + t : t = 0..3}`, placing byte `t` at bit `8t`.
- Reported statistic: `n = sum_v C(m_v, 2)` over the 2^32 projected values,
  where `m_v` is the number of coset elements projecting to `v`; plus the
  occupancy histogram, `N` (must equal 2^32), and `max_occ`.

## 2. Matrix verification (completed before this file was frozen)

By `gfverify.py`, written for this task, with determinant computed twice by
independent methods (Leibniz over all 24 permutations of S_4, and the product
of Gauss-Jordan pivots) and the inverse checked both ways.

| matrix | hex | rank | det (Leibniz) | det (pivots) | non-singular | zero entries |
|---|---|---|---|---|---|---|
| M1 | `00030101010203000101000303000102` | 4 | 20 | 20 | YES | (0,0) (1,3) (2,2) (3,1) |
| M0 | `00030101010203010101020303010102` | 4 | 29 | 29 | YES | (0,0) |
| AES_MC | `02030101010203010101020303010102` | 4 | 1 | 1 | YES | none |

M1 inverse (mine, computed without reading BATCH-002's `matrices.json`):

```
[  0, 123, 246, 141]
[141, 123, 123,   0]
[246, 141,   0, 123]
[123,   0, 141, 123]
```

`M1 * M1^-1 = I` and `M1^-1 * M1 = I` both verified. **M1 IS NON-SINGULAR, so
the finding does not collapse on this ground.** M1 is an MDS-*substitute*, not
an MDS matrix: it contains zero entries, and a true MDS matrix cannot. Its four
zeros sit at exactly `M1[(-c) mod 4][c]` for `c = 0..3`, i.e. one per column,
which is why the derivation's section-3.5 fact 2 ("MC has no zero entry") is
FALSE for M1 for every `j0`, not merely unnecessary.

## 3. The frozen rule under test

CORR-20260802-46b73b, r=5 half: the no-zero-entry condition on the mixing layer
is DISPENSABLE at r=5; the correct hypothesis is a non-singular
column-preserving mixing layer, and the mod-8 conclusion survives deleting
fact 2 outright. This prediction is frozen. If it needs adjustment I stop and
request an amendment; I do not edit it and I do not re-score runs against a
changed version.

## 4. Predictions

Primary, for every r=5 arm below, under any key, any base and any j0:

> **n mod 8 = 0.**

Exact-value predictions where BATCH-002 published a number under the same key,
base, matrix and j0 (these test my engine against theirs, not the rule):

| arm | r | matrix | j0 | key | predicted n |
|---|---|---|---|---|---|
| ANCHOR | 4 | M0 | 0 | B2 key | exactly 547608330240, histogram {0: 4278190080, 256: 16777216}, max_occ 256 |
| A1 | 5 | M1 | 0 | B2 key | exactly 1098070622208, max_occ 2816 |
| A2 | 5 | M1 | 1 | B2 key | exactly 1097141846016, max_occ 2304 |
| A3 | 5 | M1 | 0 | MINE | no exact prediction; n mod 8 = 0, n of order 1.0e12-1.2e12 |
| A4 | 5 | M1 | 2 | MINE | no exact prediction; n mod 8 = 0, n of order 1.0e12-1.2e12 |

The ANCHOR is the one number in this campaign that an independent validator has
already reproduced on its own engine (OBS-B2-3). Reproducing it to the digit
establishes that my byte order, coset layout, projection index convention and
round convention agree with BATCH-002's before any M1 number is compared.

Order-of-magnitude note for A3/A4: a random-permutation null over this object
gives n ~ 2^31 ~ 2.1e9; BATCH-002's AES_MC r=5 arm read 2147411968, consistent
with that null, while its M1 arms read ~1.1e12. The order-of-magnitude
expectation is a sanity band only and no conclusion rests on it.

## 5. What would FALSIFY the round-split rule

**Any r=5 arm under M1 that returns `n mod 8 != 0` with `N = 2^32` and the
counter-integrity check passing falsifies the r=5 half of
CORR-20260802-46b73b.** One such arm is enough. It would mean the correction
record is wrong to call the no-zero-entry condition dispensable at r=5, and I
report that plainly and without softening.

Readings that are NOT falsification and must not be reported as such:

- A timeout, crash, OOM or halt at `binding_stop_utc` -- that is resource
  exhaustion; the arm is simply not measured.
- `counter_integrity_ok = false`, `max_occ` at the counter ceiling, or
  `N != 2^32` -- that is an INVALID measurement, never a number. BATCH-001 had
  an arm invalidated exactly this way.
- A disagreement with BATCH-002's exact value while `n mod 8 = 0` still holds --
  that is an implementation defect in one of the two engines, reported as such,
  and it leaves the rule's mod-8 statement intact.
- Anything observed at r=4, which is the other half of the split rule and is
  not what these arms test.

## 6. Counter width, chosen deliberately

Counters are `uint16` (ceiling 65535). BATCH-002 reports `max_occ` 2816 and
2304 for the two M1 arms and 256 for the r=4 M0 anchor, all far below the
ceiling; `uint8` would overflow on every one of them. Two independent overflow
detectors run on every arm and both must pass:

1. per-window exact conservation -- `sum_b b * hist[b]` over the window must
   equal the number of increments the scan performed into that window;
2. `max_occ < 65535`.

Accumulation of `n` and of `sum m^2` is in `unsigned __int128`; `n <=
C(2^32,2) < 2^63` so the reported decimal cannot wrap. If either detector
fails the arm is recorded `invalid_measurement` with its reason and no number
from it is used.

## 7. Independence requirements I bind myself to

- The counting engine is mine, written for this task. BATCH-002's `cnt.c` was
  read for conventions only and is neither compiled nor executed here.
- BATCH-002's two M1 arms share key and base and differ only in j0, so they are
  two projections of the SAME 2^32 ciphertexts -- the same independence defect
  its M0 arms had. **At least one arm here (A3, and A4 if budget allows) uses a
  key and base I generate myself**, from a recorded deterministic seed, so that
  at least one M1 reading is not a projection of BATCH-002's ciphertext set.
- Parallelism differs by construction: BATCH-002 partitions the VALUE space and
  has every thread scan the whole input; I partition the VALUE-WINDOW space and
  give each thread a private counter array, so there is no shared writable
  state at all.

## 8. Budget and drop order

3000 s wall clock, 8 GB, from `budget_stamps.jsonl`. Two other producers run
concurrently on a 4-core machine, so I use at most 2 threads. If the clock runs
out, arms are dropped from the BOTTOM of this list and each dropped arm is
NAMED in RESULTS.json:

1. matrix verification (done)
2. ANCHOR (r=4 M0 j0=0, B2 key)
3. A1 (r=5 M1 j0=0, B2 key)
4. A2 (r=5 M1 j0=1, B2 key)
5. A3 (r=5 M1 j0=0, MY key) -- the independent-key requirement
6. A4 (r=5 M1 j0=2, MY key)
7. A5 (r=4 M1 j0=0, B2 key), optional strengthening of the r=4 half only

If the clock forces a choice between A2 and A3, **A3 wins**: the dispatch card
makes an independent-key arm mandatory and a second same-key projection
optional.

## 9. Inference

```yaml
policy: executor-implementation
requested_policy: executor-implementation
resolved_model: claude-opus-5
fallback_used: true
fallback_note: >-
  orchestration/model-policies.yaml names GPT-5.6-family aliases this harness
  cannot resolve; .claude/agents subagents run model: inherit.
model_verified: false
model_verified_note: no adapter probe is available in this harness
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```
