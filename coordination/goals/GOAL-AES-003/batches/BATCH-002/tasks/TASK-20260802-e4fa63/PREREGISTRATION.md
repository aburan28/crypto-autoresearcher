# PREREGISTRATION — TASK-20260802-e4fa63 (RANK 3, GOAL-AES-003 BATCH-002)

**Independent third re-execution of the yoyo objects at r=5 and r=6.**

Written **before any cipher call in this session**. Frozen at the moment of
writing; corrections appear only as a separate `PREREG-AMENDMENT-*.md`, never as
an edit here.

- Session clock start: `2026-08-02T17:07:28Z` (epoch 1785690448)
- Binding stop: `2026-08-02T18:07:28Z` (start + 3600 s), stamped in
  `budget_stamps.jsonl` as the first act of the session.
- Role: Executor. `claim_tier: toy`. Nothing here is a statement about
  full-round or deployed AES. No comparison to published cryptanalysis is made
  in either direction (RQ-AES-003 R3; DEC-20260731-019 ruling 3).
- Certificate discipline: this is a **pure measurement run**.
  `certificate.kind: none`, set explicitly. No solve, no relation, no key
  recovery is claimed or required.

## Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: claude-opus-5
  resolved_model_basis: >-
    self-reported by the running session's own system context; no adapter probe
    was executed, so this is not an independently verified resolution.
  fallback_used: true
  fallback_basis: >-
    orchestration/model-policies.yaml names GPT-5.6-family policy aliases that
    Claude Code cannot resolve (CLAUDE.md model policy note); every subagent in
    this harness runs `model: inherit`.
  model_verified: false
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

Consequence, stated up front: this session supplies **session independence and
implementation independence from both prior implementations**, and supplies
**no model independence**. Nothing here may count toward a closure quorum.

---

## 0. Independence declaration

The probe is written from scratch in this session. It reuses no producer
binary, no dispatcher binary and no BATCH-001 source. BATCH-001's
`yoyo5/PREREGISTRATION.md` was read **to identify which object is being
measured** — the requirement is to measure the same object — and the object
definition is restated in section 2 below in this session's own words so that
the restatement can be audited against it. No BATCH-001 code file was opened
for reuse, copied, compiled or executed.

Implementation choices that are this session's own: C with AES-NI intrinsics
(`_mm_aesenc/aesenclast/aesdec/aesdeclast/aesimc`) rather than a table-driven
software core; splitmix64 as the trial RNG; per-thread stream separation by
`seed ^ arm_id ^ thread_id`; POSIX threads.

## 1. Cipher convention, frozen

```
E_K^r(p) = ARK_r . SR . SB . [ ARK_i . MC . SR . SB ]_{i = r-1 .. 1} . ARK_0 (p)
```

Round keys are the first `r+1` words-blocks of the **untruncated** FIPS-197
AES-128 key expansion (the schedule is never re-derived for a shortened
cipher). The final round drops MixColumns. The initial AddRoundKey is not
counted as a round. State is column-major: `state[row][col] = byte[4*col+row]`.

`D_K^r` is the exact inverse of `E_K^r` under the same round keys.

## 2. Geometry, stated explicitly on BOTH sides

This is the point on which a first replication attempt in this campaign read no
signal, purely by swapping a column where the ciphertext words are
inverse-ShiftRows diagonals. It is therefore written down before any reading is
interpreted.

**Plaintext-side words = FORWARD diagonals**
`PW[j] = { 4*((j + row) mod 4) + row : row = 0..3 }`

| j | PW[j] |
|---|-------|
| 0 | {0, 5, 10, 15} |
| 1 | {4, 9, 14, 3} |
| 2 | {8, 13, 2, 7} |
| 3 | {12, 1, 6, 11} |

**Ciphertext-side words = INVERSE-ShiftRows diagonals**
`CW[j] = { 4*((j - row) mod 4) + row : row = 0..3 }`

| j | CW[j] |
|---|-------|
| 0 | {0, 13, 10, 7} |
| 1 | {4, 1, 14, 11} |
| 2 | {8, 5, 2, 15} |
| 3 | {12, 9, 6, 3} |

Reason (algebra about the instrument, not an observation): the first keyed
operation is `ARK_0` followed by `SB` then `SR`, so the sets ShiftRows gathers
into one column are the forward diagonals; the last operations are `SB`, `SR`,
`ARK_r`, so the sets that came from one column are the inverse-ShiftRows
diagonals. The probe emits both tables at run time and `RESULTS.json` records
them, so the geometry actually used is machine-checkable rather than asserted.

**A null reading in this session is not evidence unless the emitted tables
match the two tables above.**

## 3. The object, frozen

One **trial** is parameterised by key `K`, round count `r`, active
plaintext-word mask `A` (nonempty subset of {0,1,2,3}), swap mask
`S` (subset of {0,1,2,3}, `S` neither empty nor full), and a seed.

1. Draw `p0` uniformly. Form `p1` by re-randomising uniformly and
   independently every byte lying in a word of `A`, rejecting a draw in which
   some word of `A` has zero difference. Bytes outside `A` are equal in
   `p0`, `p1`.
2. `c0 = E_K^r(p0)`, `c1 = E_K^r(p1)`.
3. Form `c0'`, `c1'` by exchanging, for every `j` in `S`, the bytes of
   ciphertext word `CW[j]` between `c0` and `c1`.
4. `p0' = D_K^r(c0')`, `p1' = D_K^r(c1')`.
5. Record `d = p0' XOR p1'`.

**Primary statistic** `W = #{ j : d restricted to PW[j] is all-zero }`,
range 0..4. The reported quantity per arm is `#{trials : W >= 1}` restricted to
**non-trivial** trials, beside its null expectation. Full 5-bin histogram
always reported.

**Secondary statistic** `Z = #{ i in 0..15 : d[i] = 0 }`, range 0..16. Full
17-bin histogram always reported, never only a summary.

**Trivial trials are excluded and counted.** A trial is *trivial* if `c0` and
`c1` already agree on every byte of every swapped word `CW[j], j in S`: the
swap is then the identity, `p0' = p0`, `p1' = p1`, and `W = 3` is forced by
construction with no information content. Expected rate `2^-32` per trial for
`|S| = 1`, i.e. of the same order as the signal being measured, so failing to
exclude these would itself manufacture an excess. Count reported per arm.

**Null expectation.** Under a random permutation with `S` neither empty nor
full, `p0'` and `p1'` are essentially independent uniform blocks, so
`W ~ Binomial(4, 2^-32)` and per-trial `P(W >= 1) = 4 * 2^-32 = 2^-30`.
Expected `W>=1` count over `N` trials is `N * 2^-30`; `Z ~ Binomial(16, 2^-8)`.

**Excess factor** = (observed non-trivial `W>=1` count) / (`N * 2^-30`).

**Resolution.** With `N` trials the smallest per-trial probability detected
with >=95% probability is `3/N`; resolution in bits is `log2(N/3)`. Every arm
reports `N` and its resolution; an arm whose resolution does not cover the null
probability of the event it reports is labelled **underpowered** on the same
line as the number.

## 4. Required arms

| Arm | Object | `r` | `A` | `S` |
|-----|--------|-----|-----|-----|
| PIN | FIPS-197 C.1 KAT + `D(E(x))=x` over r=1..10 | — | — | — |
| PC | positive control, real AES | 2 | {0} | {0} |
| A1 | **main measurement**, real AES-128 | 5 | {0} | {0} |
| A1b | A1 repeated, different key and seed | 5 | {0} | {0} |
| A2 | real AES-128 | 6 | {0} | {0} |
| A3 | **MEASURED PRP null**: `E` and `D` replaced by full 10-round AES-128 under an independent key and its exact inverse, pipeline byte-identical | 10 | {0} | {0} |
| A4 | **STRUCTURE-DESTROYED control**: all four plaintext words active, so no diagonal coset structure remains | 5 | {0,1,2,3} | {0} |

Arms are executed in the order PIN, PC, A1, A3, A2, A4, A1b, and any arm not
reached before the binding stop is reported as **not run, with its reason**,
never as a null reading.

## 5. Pre-registered predictions (frozen)

- **PR-0 (pin).** The probe reproduces the FIPS-197 C.1 known-answer vector
  exactly (key `000102...0f`, plaintext `00112233445566778899aabbccddeeff`,
  ciphertext `69c4e0d86a7b0430d8cdb78070b4c55a`), and `D_K^r(E_K^r(x)) = x` for
  every `r` in 1..10 over >= 512 random (key, plaintext) vectors, with **zero**
  failures. If PR-0 fails, no measurement in this session is evidence about
  anything and every arm is VOID.
- **PR-1 (positive control, deterministic).** Arm PC reads `W = 3` in
  **100%** of non-trivial trials. Two-round AES in word coordinates is four
  parallel independent bijections, so a ciphertext-word swap swaps exactly one
  plaintext word and the zero-difference pattern is preserved exactly. A
  failure here means the instrument cannot see structure it is guaranteed to
  see, and fires V1.
- **PR-2 (r=5, the claim under test).** Arm A1 shows a `W>=1` excess factor
  **substantially above 1**; point prediction **~16x**, predicted band
  **8x to 25x**. (BATCH-001 reported 16.75x at `N=2^32` and 15.75x at
  `N=2^33` for `S={0}`, and 12.5x for `S={2}`; the "~12x" in the dispatch card
  is the low end of that spread. The prediction band is set to cover the
  spread rather than a single prior reading.)
- **PR-3 (r=6).** Arm A2 shows excess factor **~1**, predicted band
  **0x to 3x**, i.e. no usable signal, and at `N = 2^32` (null expectation 4)
  the arm is **underpowered** to distinguish 1x from 2x.
- **PR-4 (measured PRP null).** Arm A3's measured per-trial `W>=1` rate agrees
  with the analytic `2^-30` to within Poisson sampling error: predicted excess
  factor 1.0, with the two-sided 99% Poisson interval on a count of expectation
  `N*2^-30` reported beside it. **A disagreement here voids every other arm
  in the session** (V5), because it would mean the harness rather than the
  cipher produces the reading.
- **PR-5 (structure-destroyed control).** Arm A4 shows excess factor **~1 or
  below**, predicted band **0x to 3x**. Without this arm a positive A1 reading
  is uninterpretable, because an excess produced by the measurement pipeline
  rather than by the diagonal coset structure would show up here too.
- **PR-6 (death round).** The largest `r` at which the real-AES arm departs
  from the measured null by more than the arm's resolution is predicted to be
  **r = 5**. This is reported as **the death round measured by this campaign**,
  with **no comparison to any published death round in either direction**;
  this repository cannot adjudicate that question.

## 6. What reading would make me conclude the r=5 signal DOES NOT replicate

Stated before measurement, so it cannot be moved afterwards. The r=5 signal is
recorded as **not replicated by this session** if **either**:

- **(N1)** Arm A1's non-trivial `W>=1` count lies inside the two-sided 99%
  Poisson interval of the analytic expectation `N * 2^-30` — at `N = 2^32`
  (expectation 4.0) that interval is `[0, 12]`, so an observed count of **12 or
  fewer**, i.e. an excess factor at or below **3.0x**, is a non-replication; or
- **(N2)** Arm A1's count is not significantly above the **measured** PRP null
  of arm A3 at the same `N`: Poisson tail `p > 1e-3` when A1's count is scored
  against the rate measured in A3.

Both criteria are reported whatever the outcome. A non-replication under either
is a complete result and is reported as such, not as a failed run.

Two readings that are **not** non-replication and must not be reported as such:
a budget halt before arm A1 completes, and any VOID under section 7. Those are
`resource_exhaustion` and `invalid_measurement` respectively.

## 7. VOID conditions

If one fires, the affected readings are VOID, classified `invalid_measurement`,
and are never reported as a negative observation.

- **V1** PR-1 fails (r=2 positive control not 100% `W=3`). Instrument broken;
  execution stops.
- **V2** PR-0 fails: KAT mismatch, or any round-trip failure at any `r`.
- **V3** The emitted `PW`/`CW` tables differ from section 2. Wrong object built.
- **V4** The excess is flat across `r` and still present at `r = 10` (arm A3
  is simultaneously the decay check). Canonical instrument-fault tell.
- **V5** Arm A3 departs from `Binomial(16, 2^-8)` / `2^-30` by more than its own
  resolution (PR-4 fails).
- **V6** Any degenerate trial not excluded: `p0 = p1`, `S` empty or full, or a
  word of `A` with zero difference. Counted; a nonzero count of unexcluded
  degenerates voids the arm.
- **V7** Wall-clock halt at `2026-08-02T18:07:28Z`. Arms not started are
  reported as not run. **A budget halt is never a null result and never
  evidence about AES.**

## 8. Terminology, and a wording defect that is not reintroduced

The BATCH-001 validator identified that a quantity the package called a
**"distinguishing advantage" of 2^-46** is in fact a **false-positive rate**
against the control. The number was right and the word was wrong, in a way that
flattered the result. This session uses:

- **false-positive rate** `p` — the probability that the control (null) arm
  produces the reading used as the decision threshold;
- **advantage** — only in its correct sense: a test with no false negatives and
  false-positive rate `p` has distinguishing advantage `~ 1 - p`, which is close
  to **1**, not to `p`.

No quantity in this session's artifacts is labelled a distinguishing advantage
unless it is `1 - p`.

## 9. Sources of randomness, frozen

Master seed **`424242001`**. All keys, plaintexts and per-trial randomness come
from a splitmix64 stream written for this session and seeded deterministically
from `master_seed`, `arm_id` and `thread_id`; every arm records its exact seed
and its key. No use of `rand()`. Arm A1b re-runs the main measurement under a
different master seed and a different key before the reading is reported at all.

## 10. What this session may not do

- May not conclude that a heuristic is validated or refuted.
- May not declare a hypothesis supported, rejected or closed.
- May not assess novelty, in either direction.
- May not infer anything about full-round or deployed AES.
- May not compare a measured death round to any published one, in either
  direction.
- May not report a budget halt or an infrastructure failure as mathematical
  evidence.
- May not modify any BATCH-001 artifact, or write outside
  `coordination/goals/GOAL-AES-003/batches/BATCH-002/tasks/TASK-20260802-e4fa63/`.
