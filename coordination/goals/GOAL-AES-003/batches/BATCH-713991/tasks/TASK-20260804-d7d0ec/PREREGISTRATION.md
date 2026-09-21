# PREREGISTRATION — TASK-20260804-d7d0ec

**Goal:** GOAL-AES-003 · **Batch:** BATCH-713991 · **Role:** executor
**Task:** THE ZERO-ENTRY DECAY CONTROL — does the mod-8 property under a zero-entry
mixing layer decay with round count, or is it forced at every round count by the
layer's fiber degeneracy?
**Recorded:** 2026-08-06T01:21:00Z (before the measurement arms below were run)
**Claim tier:** TOY. Nothing here is a statement about full-round or deployed AES,
and no comparison to published cryptanalysis is made in either direction
(RQ-AES-003 R3).

## 1. What is being measured

The red team's RC-1 / counterexample_or_mutation, in its nibble form: a 4x4-nibble
AES-shaped SPN over GF(2^4) (modulus x^4+x+1), the same instrument family as the
BATCH-001 validator's scaled analogue (TASK-VALIDATION-001/mini.c conventions:
cell index = 4*col+row, ShiftRows row-t rotate-left, column-preserving MixColumns,
C1 last round without MixColumns, independent uniform round keys, full 2^16
diagonal coset D_0 = cells {0,5,10,15}, projection ID_{j0} packed to 16 bits,
statistic n = sum_v C(cnt[v],2)).

Two layers, everything else identical:

| layer | matrix over GF(2^4) | zero entries | role |
|---|---|---|---|
| M1 | [[0,3,1,1],[1,2,3,0],[1,1,0,3],[3,0,1,2]] | 4: (0,0),(1,3),(2,2),(3,1) | zero-entry layer under test |
| CTRL | circulant (2,3,1,1) | 0 | no-zero-entry control |

j0 = 0 for every arm. Under M1 at j0=0 the four r=4-critical entries
M[(-c-j0) mod 4][c], c=0..3, are M[0][0], M[3][1], M[2][2], M[1][3] — ALL FOUR
ZERO (the maximally adversarial case, per OBJ-6's arithmetic in
TASK-20260802-fa1dcc). Under CTRL they are all non-zero.

## 2. Matrix verification (done before this document, own arithmetic)

Gauss-Jordan over GF(2^4), x^4+x+1, computed by me in this task (Python, then
re-verified inside the C instrument at startup):

- **M1: rank 4, det 7, non-singular, M·M⁻¹ = I** (inverse
  [[0,7,14,9],[9,7,7,0],[14,9,0,7],[7,0,9,7]]).
- **CTRL: rank 4, det 1, non-singular, M·M⁻¹ = I** (inverse
  [[14,11,13,9],[9,14,11,13],[13,9,14,11],[11,13,9,14]]).
- The BATCH-001 validator's substitute circulant (2,3,0,1) is confirmed SINGULAR
  (rank 3) — the failure that aborted its control is not repeated.

The instrument refuses to run if the matrix is singular or the inverse check
fails. This fills the three-batch-old not_executed item.

## 3. Instrument validation already performed (disclosed, not hidden)

Before this file was written, the instrument was smoke-tested and pinned against
the validator's PUBLISHED readings (so these are instrument checks, not new
measurements of the campaign question):

- CTRL r=5 j0=0, 40 trials: **40/40 n mod 8 = 0** — matches validator's
  r5_0mod8_fixed_sbox 40/40.
- CTRL r=6 j0=0, 40 trials: **1/40** (fixed S-box), **4/40** (random S-box) —
  consistent with validator's 4/40 and 3/40 (uniform predicts 5).
- M1 r=4 j0=0, 2-trial smoke: n = 2147450880, single fiber {65536:1} — matches
  the derived prediction in section 4.1 below.

The full measurement arms (section 5) were NOT run before this file.

## 4. Pre-registered predictions

### 4.1 Zero-entry layer (M1), j0=0

- **r=4: n = 2147450880 EXACTLY = C(2^16, 2), single fiber of size 2^16,
  n mod 8 = 0, in every trial.** Derived: at r=4 the collision condition is
  "column j0 of SR(Delta) = 0", one cell from each of the four columns; the
  cell from column c is forced to 0 iff a_c = a'_c, and that forcing is
  vacuous exactly when the critical entry M[(-c-j0) mod 4][c] is zero. Under M1
  at j0=0 ALL FOUR critical entries are zero, so every pair (w,w') satisfies the
  condition — the projection is constant, one fiber of size 2^16, and
  n = C(2^16,2) = 2147450880. This is the nibble analogue of the byte-scale
  M0 r=4 critical arm (n = 547608330240, histogram {0: 2^32-2^24, 256: 2^24}),
  where ONE zero entry produced 2^24 fibers of size 256; four zero entries
  collapse everything to one fiber. A mismatch here means my reading of the
  refined r=4 condition is wrong, and I record it as such.
- **r=5: n mod 8 = 0 in every trial (40/40).** The r=5 half of the round-split
  rule (CORR-20260802-46b73b): a non-singular column-preserving layer suffices;
  the k=1 class contributes 16^3·N_ord/2 (nibble: 2^12·N_ord/2), a multiple of
  2^12 hence of 8, whether or not it is empty. Also predicted: every occupancy
  is a multiple of 16 (the nibble analogue of the byte-scale multiple-of-256
  fiber signature).
- **r=6: THE QUESTION. Two hypotheses.**
  - (a) Round-structure hypothesis (the r=5 half measures real round
    structure): the property DECAYS — n mod 8 goes uniform (~5/40) and the
    16-divisibility disappears, matching the CTRL r=6 arms.
  - (b) Matrix-degeneracy hypothesis (the r=5 half is an artifact): the
    zero-entry layer forces n mod 8 = 0 at r=6 at materially above the 1-in-8
    rate, and/or the occupancy histogram remains supported on multiples of 16.

### 4.2 No-zero-entry control (CTRL), j0=0

- **r=4: n = 0 exactly in every trial (bijection).** Instrument positive
  control; validator measured 40/40.
- **r=5: n mod 8 = 0 in every trial (40/40).** Validator measured 40/40 fixed
  and 120/120 across j0.
- **r=6: n mod 8 uniform (~5/40), no 16-divisibility.** Validator measured
  4/40 fixed, 3/40 random. This is the decay reference the zero-entry layer is
  compared against.

### 4.3 Falsification criteria for the r=5 half of CORR-20260802-46b73b

- **FALSIFIED** if the zero-entry layer at r=6 reads n mod 8 = 0 in ≥ 15 of 40
  trials (uniform predicts 5; sd ≈ 2.09; 15 is ≈ 4.8σ, binomial p ≈ 1e-5) AND/OR
  the occupancy histogram is supported on multiples of 16 in ≥ 39 of 40 trials.
  Either signature means the zero-entry matrix forces the residue independently
  of round count, so the r=5 half measures the matrix, not round structure.
  This outcome is reported plainly and not softened.
- **SURVIVES** if the zero-entry r=6 zero-rate is consistent with the CTRL r=6
  rate (≤ 7/40) and the 16-divisibility is absent (≤ 2/40 trials).
- **UNDECIDED** if the rate is elevated but not decisive (8–14/40) or the two
  signatures disagree.

The r=4 half of the round-split rule is NOT under test here (it is already
split and byte-scale-verified); the r=4 M1 arm is a bonus exact check of the
refined condition at nibble scale.

## 5. Design decisions (frozen)

- 40 trials per arm, r ∈ {4,5,6}, j0 = 0, both layers: 6 arms, 240 trials.
- Fixed S-box (the campaign's pinned nibble S-box
  [6,11,5,4,2,14,7,10,9,13,15,12,3,1,0,8]) for the primary arms; one bonus
  random-bijective-S-box arm per layer at r=6 (S-box-dependence check of any
  r=6 forcing).
- Seed 88172645463325252 for every arm; trial t uses rs = seed + t·2654435761,
  so trial t in every arm shares the same key and base — the ONLY things that
  vary between arms are r and the matrix. This is the "round count is the only
  varying parameter" requirement.
- Per-trial output: n, n_mod8, n_mod16, max_occ, the sparse occupancy histogram
  {occ: count}, and whether every nonzero occupancy is a multiple of 16.
- The instrument is deterministic; every arm is reproducible from its recorded
  command and seed.

## 6. What a nibble-scale result does and does not transfer to GF(2^8)

- **Does transfer:** the round-geometry mechanism. The r=4 refined condition
  (four load-bearing entries M[(-c-j0) mod 4][c]) and the r=5 k-class counting
  (inactive columns carry a free factor 2^{4(4-k)}; k=4 orbit argument) are
  cell-width-independent by construction — the BATCH-001 validator already
  established this for the no-zero-entry layer (120/120 at nibble width).
- **Does NOT transfer automatically**: the exact fiber sizes. The byte-scale
  signature is "every fiber a multiple of 256 = 2^8"; the nibble analogue is
  "every fiber a multiple of 16 = 2^4". A nibble-scale forcing of n mod 8 = 0
  at r=6 is evidence about the MECHANISM (matrix-forced vs round-decayed) at
  nibble width; it is not a byte-scale measurement, and the byte-scale r=6
  zero-entry arm remains unmeasured. The campaign has been burned by scaled
  readings before (C9: the degree argument), so this result is reported as an
  analogue with its transfer limits stated, never as a byte-scale result.