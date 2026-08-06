# PREREGISTRATION — TASK-20260803-d6ebce

RANK 1 of GOAL-AES-003 / BATCH-007: characterise, and if possible derive, the
active-word preservation structure of the yoyo statistic at r <= 4.

Written and frozen BEFORE any measurement arm was run, with the single
exception recorded in "Prior acts" below. Times are UTC.

## Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    executor-implementation names a GPT-5.6-family policy alias in
    orchestration/model-policies.yaml. This harness is Claude Code; subagent
    frontmatter resolves only Claude models, so the policy resolved to
    claude-opus-5. Recorded, not silently substituted (CLAUDE.md model policy
    note).
  model_verified: false
  model_verified_reason: >-
    No `python3 -m orchestration.adapter doctor --probe` was run in this task.
    The resolved model identifier is self-reported configuration, not a
    probe-verified backend fact.
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

## Prior acts before this document was frozen

1. Clock stamp (mandatory first act), 2026-08-03T18:05:51Z.
2. Instrument verification: sha256 of
   `.../BATCH-004/tasks/TASK-20260803-367b1b/yoyo_sbox_v2` and its source.
3. ONE timing/scoping invocation of the frozen binary,
   `yoyo_sbox_v2 arm TIMING aes 4 1 1 24 1 1 2`, to measure throughput for
   budget planning. It is a real measurement and is reported in RESULTS.json as
   `TIMING`, not discarded. It reproduces the already-known amask=1 reading and
   was run before the predictions below were written down. Every prediction
   below other than the amask=1 case is therefore genuinely out of sample; the
   amask=1 case is not, and is labelled as such in RESULTS.json.

## What is already on disk (paths searched)

Claims about what has and has not been measured are empirical claims about this
repository (CORR-20260803-c92db5). Paths actually searched for this section:

- `coordination/goals/GOAL-AES-003/batches/BATCH-002/tasks/*/` (arm_A3, A3b)
- `coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b/`
  (incl. `runs/`, `src/`, `RESULTS.json`)
- `coordination/goals/GOAL-AES-003/batches/BATCH-005/tasks/TASK-20260803-48a239/runs/*.json`
- `coordination/goals/GOAL-AES-003/batches/BATCH-006/tasks/TASK-20260803-0764fc/`
  and `.../TASK-20260803-a13de8/validation_report.yaml`
- repo-wide grep for the two instrument sha256 values.

Found, and therefore NOT re-measured as if new:

- amask=1, r=4 by-word structure `[0,N,N,N]` (BATCH-004/005/006).
- amask=2, r=4 giving `[N,0,N,N]`, and amask=15 giving W=0 on every trial
  (BATCH-006 validator, `TASK-20260803-a13de8/validation_report.yaml`).
- NINE r=5 arms at amask=1, smask=1, log2N=30, in
  `BATCH-005/tasks/TASK-20260803-48a239/runs/D-*.json`, with by-word vectors
  such as `[4,4,2,4]`, `[6,5,1,2]`, `[5,5,5,7]`. These already show r=5 hits
  landing on ALL FOUR words including the active word 0.

Open before this task, to my search: single-word amask=4 and amask=8; every
multi-word amask other than 15; every smask other than 1; any r=5 arm at an
amask other than 1; and any derivation of the structure at all.

## The derivation, stated as a prediction BEFORE measuring

Notation. State = 4x4 bytes, index `i = 4*c + row` (column-major, as in the
instrument). `PW[j] = {4*((j+row)%4)+row}` is plaintext word j (a forward
ShiftRows diagonal); `CW[j] = {4*((j-row)%4)+row}` is ciphertext word j (an
inverse diagonal). Write `S' = SR . SB`. The instrument's cipher is

    E^r = ARK_r . S' . [ARK_i . MC . S']_{i=r-1..1} . ARK_0

Chain of intermediate states for the pair:

    p -ARK0-> x -S'-> y_1 -MC-> z_1 -ARK1-> w_1 -S'-> y_2 -MC-> z_2 -> ...

Four elementary lemmas, each used explicitly below.

- **L1 (diagonal-to-column).** `SR` sends cell `(row,c)` to `(row,c-row)`, so it
  maps `PW[j]` onto column j, and its inverse maps `CW[j]` onto column j.
  Hence `S'` carries diagonal j of its input onto column j of its output, and
  a column j of a post-`SR` state pulls back to the antidiagonal `CW[j]` of the
  pre-`SR` state.
- **L2 (transparency of bytewise maps).** `SB`, `SB^-1` and `ARK` act bytewise
  and bijectively, so "the two states agree at position i" is preserved in both
  directions. They move the ZERO PATTERN unchanged; they do NOT preserve the
  difference VALUE.
- **L3 (column transparency of MC).** `MC` is invertible and acts within each
  column, so a column of the difference is zero iff the corresponding column of
  the image difference is zero, and the difference value is carried linearly.
- **L4 (exchange invariance).** The yoyo swap sets `c0'[i]=c1[i]`,
  `c1'[i]=c0[i]`. Therefore `c0'[i] XOR c1'[i] = c0[i] XOR c1[i]`: the pair
  DIFFERENCE at the swap point is unchanged by the swap, for any swap set.

**Step 1 (swap pushback).** Swapping ciphertext word j is, by L2, a swap of the
same positions of `SR(SB(w_{r-1}))`; by L1 that is a swap of column j of
`SB(w_{r-1})`, hence by L2 of column j of `w_{r-1}`, hence of column j of
`z_{r-1} = MC(y_{r-1})`, hence by L3 of column j of `y_{r-1} = SR(SB(w_{r-2}))`,
hence by L1+L2 of diagonal `PW[j]` of `w_{r-2}`, hence of diagonal `PW[j]` of
`z_{r-2}`. The pushback stops there: a diagonal crosses all four columns, so it
does not commute back through the next `MC`.

**Step 2 (forward zero pattern).** `p0` and `p1` differ exactly on the diagonals
in the active set A, each with at least one differing byte (the instrument
rejects a draw leaving an active word unchanged). By L2 and L1, `Δ(y_1)` is
supported on the columns in A, nonzero in each. By L3, `Δ(z_1)` has column j
nonzero iff j in A. By L2+L1 again, `Δ(y_2)` has its antidiagonal `CW[j]`
nonzero iff j in A.

**Step 3 (backward test).** Plaintext word j is preserved iff `q0 XOR q1` is
zero on `PW[j]`, iff (L2, L1) column j of `Δ(y_1')` is zero, iff (L3) column j
of `Δ(z_1')` is zero.

**Step 4 (join).** By Step 1 the swap acts at `z_{r-2}`, and by L4
`Δ(z_{r-2}') = Δ(z_{r-2})`.

- r = 3: swap point is `z_1` itself, so `Δ(z_1') = Δ(z_1)` and Step 3 gives
  preserved(j) iff j not in A, by Step 2. Zero S-box layers crossed.
- r = 4: swap point is `z_2`. `Δ(y_2') = MC^-1(Δ(z_2')) = MC^-1(Δ(z_2)) =
  Δ(y_2)`, an exact equality of difference VALUES because only the linear L3
  was crossed. Then one `SB^-1` layer is crossed, which by L2 preserves the
  zero pattern, and column j of `Δ(z_1') = Δ(w_1')` is zero iff `CW[j]` of
  `Δ(y_2)` is zero, iff j not in A by Step 2.
- r = 2: swap point is the plaintext itself; L4 gives `Δ(p') = Δ(p)` and the
  result is immediate.
- r = 5: swap point is `z_3`. `Δ(y_3') = MC^-1(Δ(z_3))` is known, and the zero
  pattern of `Δ(z_2')` follows by L2. **The argument then requires
  `Δ(y_2') = MC^-1(Δ(z_2'))`, and `MC^-1` is linear in the difference VALUE
  while crossing `SB^-1` gave us only the zero PATTERN. That is the exact step
  that breaks, and it breaks at r=5 and not before.**

### Proposition 1 (pre-registered prediction)

For the instrument's cipher with ANY bijective S-box, ANY key, ANY r in
{1,2,3,4}, ANY nonempty active set A, and ANY nondegenerate swap set (any
`smask` in 1..14), on EVERY trial:

  W = 4 - |A|, and plaintext word j is preserved iff j is not in A.

Consequences to be tested:

- P1. `W_ge1_by_word[j] = nontrivial_trials` for every j not in A, and `0` for
  every j in A. `whist` is a point mass at `W = 4-|A|`.
- P2. `W_ge1_nontrivial = nontrivial_trials` whenever |A| <= 3, and `0` when
  A is all four words (amask=15).
- P3. The reading does not depend on `smask` at all.
- P4. The reading does not depend on the S-box (bijectivity is all that is
  used) or on the key.
- P5. At r=5 the structure fails; hits become rare and are NOT confined to the
  non-active words.

### Pre-registered per-arm predictions at r <= 4 (N = nontrivial_trials)

| amask | active words | predicted `W_ge1_by_word` | predicted whist mass |
|---|---|---|---|
| 1 | {0} | [0,N,N,N] | W=3 |
| 2 | {1} | [N,0,N,N] | W=3 |
| 4 | {2} | [N,N,0,N] | W=3 |
| 8 | {3} | [N,N,N,0] | W=3 |
| 3 | {0,1} | [0,0,N,N] | W=2 |
| 5 | {0,2} | [0,N,0,N] | W=2 |
| 6 | {1,2} | [N,0,0,N] | W=2 |
| 9 | {0,3} | [0,N,N,0] | W=2 |
| 12 | {2,3} | [N,N,0,0] | W=2 |
| 7 | {0,1,2} | [0,0,0,N] | W=1 |
| 15 | all | [0,0,0,0] | W=0 |

## What reading would show the rule is NARROWER than stated

Any of the following falsifies Proposition 1 as stated and is to be reported as
such rather than explained away:

- N1. Any `W_ge1_by_word[j] > 0` for j in A, or `< nontrivial_trials` for j not
  in A, at r <= 4. This would mean the rule is not "exactly the active words".
- N2. A multi-word amask that does not give the predicted point mass at
  `W = 4-|A|` — e.g. amask=3 reading rate 1.0 on W>=1 but with a nonconstant
  by-word vector. This would make the rule single-word-only.
- N3. Any dependence on `smask` (P3 fails). This would mean the swap matters,
  which Proposition 1 says it does not, and would break Step 1 or L4.
- N4. Any dependence on the S-box or key (P4 fails). This would mean the
  derivation's use of bijectivity alone is insufficient.
- N5. Determinism surviving at r=5 (P5 fails). This would mean Step 4's break
  point is misidentified, and the derivation's round bound would be wrong even
  though its r<=4 conclusion held.

A reading in which r=1 differs from r=2..4 is expected to be uninteresting
(r=1 is degenerate) but is reported either way.

## Arms to be run

Frozen instrument only, invoked as
`yoyo_sbox_v2 arm <name> <sboxspec> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads>`,
2 threads (a second producer runs concurrently).

- S0: `geom`, `pin aes <seed>`, `pin rand:<seed>` — geometry and the FIPS-197
  C.1 known-answer pin.
- S1 amask sweep at r=4, smask=1, log2N=24: amask in
  {1,2,4,8,3,5,6,9,12,7,15}.
- S2 round boundary at amask=2, smask=1: r in {1,2,3} at log2N=24 (r=4 comes
  from S1), r=5 at log2N=31.
- S3 smask dependence at r=4, amask=2, log2N=24: smask in {2,4,7,13}.
- S4 S-box and key dependence at r=4, log2N=24: a drawn S-box `rand:<seed>` at
  amask=4 and at amask=15, and two arms at a different `seed` (which changes
  the key; note the instrument derives the key from `seed`, so a key change is
  not independent of the trial stream — this confound is recorded, not hidden).
- S5 r=5 at a second condition if budget permits.

Hard cap 30 runs. Budget 5400 s from 2026-08-03T18:05:51Z, binding stop
2026-08-03T19:35:51Z. Work not reached at the stop will be NAMED as dropped.

## Scope

TOY TIER. Reduced-round AES-128 in a software T-table reimplementation, one
machine. Nothing here is a statement about full-round or deployed AES, and no
comparison to published cryptanalysis is made in either direction (RQ-AES-003
R3). The "excess 2^30" figure at r <= 4 is the ARITHMETIC CEILING of the
statistic — rate 1.0 divided by a modeled null of 2^-30 — and is never quoted
here as a magnitude.

---

# ADDENDUM A — frozen 2026-08-03T18:23Z, before the last two arms

Sections S0-S4 are complete (24 arm invocations, plus geom and two pins). Two
things force an addendum. Both are recorded here BEFORE the arms that test them
are run.

## A.1 Budget: the run cap binds, and work is being dropped

`maximum_runs: 30`. I have executed 28 invocations of the frozen instrument: 24
`arm` invocations, 1 `geom`, 2 `pin`, and 1 crashed `pin` (see A.3). To stay
inside 30 under the STRICTEST reading — every instrument invocation is a run —
only TWO arms remain. I take that strict reading rather than the convenient one
in which pins do not count.

The two remaining arms are spent on:

- **B1**: r=2, amask=2, smask=2, log2N=24 — because arm `S2-r2` returned
  `nontrivial_trials = 0` (see A.2), so r=2 currently has NO measured by-word
  vector at all.
- **B2**: r=5, amask=2, smask=1, log2N=31 — the round-boundary deliverable.

**DROPPED on the run cap, named as required**: an r=5 arm under a drawn S-box;
an r=5 arm under a second key; an r=2 multi-word arm; any r=6 arm; and a
larger-N confirmation of any r<=4 cell beyond 2^24. Note that r=5 under drawn
S-boxes and under three keys is ALREADY on disk and is cited rather than
re-measured: `BATCH-005/tasks/TASK-20260803-48a239/runs/D-{AES,R1,R2}-K{1,2,3}.json`,
nine arms at r=5, amask=1, smask=1, log2N=30, where `D-R1` and `D-R2` are drawn
S-boxes and K1/K2/K3 are three keys.

## A.2 An unanticipated observation, and what it predicts

Arm `S2-r2` (r=2, amask=2, smask=1) recorded `trivial_swaps_excluded =
16777216` — EVERY trial was a trivial swap, so the arm has no measurable
by-word vector. This was not anticipated in the table above.

It is, however, an immediate corollary of Step 1 rather than a defect: at r=2
the pushback makes the ciphertext-word-j swap EQUAL to a swap of plaintext
diagonal j. With amask=2 the pair agrees on diagonal 0 by construction, so a
swap of word 0 exchanges bytes that already agree, which the instrument
correctly classifies as trivial and excludes.

That turns the trivial-swap rate into a quantitative test of Step 1, the most
load-bearing step of the derivation. Predictions, stated now:

- **T1 (new arm B1).** r=2, amask=2, smask=2: the swapped diagonal is the
  ACTIVE one, so trivial swaps should be essentially absent — rate on the order
  of 2^-32, i.e. an expected count near zero in 2^24 trials — and the by-word
  vector should be `[N,0,N,N]` with `whist` a point mass at W=3.
- **T2 (post-hoc, on data already in hand, labelled as such).** At r=1 the
  pushback stops one layer earlier: `E^1 = ARK_1 . SR . SB . ARK_0` has no
  preceding `SR`, so a ciphertext-word-j swap is a swap of COLUMN j of the
  plaintext, not a diagonal. Column j meets each diagonal in exactly one byte,
  so with a single active word exactly one swapped byte can differ and the
  trivial rate should be about 2^-8. Observed in `S2-r1`: 65457 / 16777216 =
  0.00390, and 2^-8 = 0.00391.
- **T3 (post-hoc, labelled as such).** At r=3 the swap is diagonal j of `z_1`,
  which meets the single active column in one byte, so again about 2^-8.
  Observed in `S2-r3`: 65956 / 16777216 = 0.00393.
- **T4 (post-hoc, labelled as such).** At r=4 the swap is diagonal j of `z_2`,
  where all four columns of the difference are generically nonzero, so the
  trivial rate should be about 2^-32 and no trivial swap should appear in 2^24
  trials. Observed: `trivial_swaps_excluded = 0` in every S1/S3/S4 arm.

T2, T3 and T4 are checked against measurements that already existed when they
were written. They are corroborations, not predictions, and are not to be
counted as out-of-sample confirmations.

## A.3 Protocol deviation, recorded

My driver `run_arms.sh` initially invoked `yoyo_sbox_v2 pin rand:20260803702`
without the required seed argument. The instrument read a NULL argv[3] and
segfaulted (exit 139). This is an `implementation_error` in MY driver, not in
the frozen instrument, which was not modified. The driver was corrected and the
pin re-run successfully. The crashed invocation is counted against the run cap
in A.1 and is reported in RESULTS.json rather than discarded.

## A.4 Prediction for B2 (r=5)

Restating P5 concretely for the one r=5 arm being run: at r=5, `W_ge1` should
be a rare event of order tens of hits in 2^31 trials rather than rate 1.0, and
the hits should NOT be confined to the three non-active words — in particular
`W_ge1_by_word[1]` should be nonzero for amask=2. If instead r=5 shows
`[N,0,N,N]` at rate 1.0, Proposition 1's round bound is wrong (falsifier N5).
