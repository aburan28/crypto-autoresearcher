---
id: KN-TECH-c3d80e
type: technique
title: Two-way dependence is a threshold, not a property - the separation law for splice-and-cut matching points, and why a non-constancy gate cannot discharge a near-injectivity premise
tags: [methodology, meet-in-the-middle, splice-and-cut, mitm, preimage, chunk-separation, matching-point, word-schedule, arx, merkle-damgard, md4, md5, controls, pre-registration, gate-design, injectivity, null-object, design-pitfall, obstruction]
confidence: verified_by_execution
complexity: >-
  Not an algorithm. Two design laws and three pre-run checks, all of which cost
  seconds or nothing at all - a step-distance comparison with no compute, a
  static per-F-application mask check with no search, and a distinct-count
  criterion that a gate already computes and then throws away.
applicability: >-
  Any meet-in-the-middle / splice-and-cut / partial-matching construction that
  splits an iterated compression function at an interior step, chooses two
  neutral words from a fixed step-to-word schedule, and declares a windowed
  matching quantity on the boundary state. MD4/MD5-style ARX Merkle-Damgard
  schedules directly; by the same argument any chunk separation over a fixed
  schedule. The second law (non-constancy is not near-injectivity) applies to
  ANY gate whose pass criterion is a distinctness threshold.
source_refs: [EV-MDFIVE-24e077, DEC-20260822-40bf14, H-MDFIVE-0ca596, EXP-MDFIVE-a8e71e, IDEA-20260821-ea35d1, DEC-20260821-333267, GOAL-MD5-001, BATCH-7215fa, KN-TECH-bb7e9f, KN-TECH-9d21c4, KN-TECH-080, KN-TECH-056]
extends: KN-TECH-bb7e9f
supersedes_section:
  entry: KN-TECH-bb7e9f
  section: "Open, not settled - the mirror-image trap"
  status: settled
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MD5-001/batches/BATCH-7215fa/reviews/TASK-20260821-2de43d/red-team-report.yaml#blind_rederivation
  - coordination/goals/GOAL-MD5-001/batches/BATCH-7215fa/reviews/TASK-20260821-2de43d/red-team-report.yaml#per_joint_verdicts[R2].worked_attack_output
  - coordination/goals/GOAL-MD5-001/batches/BATCH-7215fa/reviews/TASK-20260821-26ba34/validation-report.yaml#per_joint[V3]
  - coordination/goals/GOAL-MD5-001/batches/BATCH-7215fa/tasks/TASK-20260821-372d67/runs/RUN-MDFIVE-b5-gate_and_controls/raw-result.json
claim_tier: analyzed
added: "2026-08-22"
superseded_by: null
---

## What this entry adds, and what it settles

`KN-TECH-bb7e9f` records the rule that a splice-and-cut matching quantity must
be a state component **both** free words have already influenced, and closes
with a section headed *"Open, not settled - the mirror-image trap"*: a
Coordinator reading of module source suggesting that at a one-step-separated
split the two free words influence **disjoint** components, so the obvious
repair (read the other tuple position) would relocate the degeneracy rather
than cure it. That section is explicitly marked as an unsettled reading of one
implementation.

**It is now settled**, by a third derivation taken from RFC 1320's step table
alone, blind to every implementation in this program, and confirmed empirically
by differential probing before any producer artifact was opened
(`TASK-20260821-2de43d`). This entry records the settled form, which is
stronger and more general than the paragraph it replaces, together with a
second law the same batch bought at the cost of a stopped run.

`KN-TECH-bb7e9f` is **not edited and is not marked superseded as a whole** -
only that one section is superseded, the rest of it stands, and the file is
byte-bound inside a completed content_first archive. Read both.

## Law 1 - two-way dependence is a threshold in the SEPARATION, and the split point is irrelevant

For a Round-1 schedule consuming `X[0..15]` once each in index order, write the
state as a rolling tuple `T = (T0,T1,T2,T3)` with
`newA = rotl(T0 + F(T1,T2,T3) + X[t], s_t)` and `T' = (T3, newA, T1, T2)`. Let
the forward chunk's free word be consumed at step `i`, the backward chunk's at
step `j > i`, and let the split be at `S`.

- **Forward taint sets.** `E_d` = tuple positions of `state_{i+1+d}` depending on
  `X[i]`: `E_0 = {1}`, `E_1 = {1,2}`, `E_2 = {1,2,3}`, `E_d = {0,1,2,3}` for
  `d >= 3`.
- **Backward taint sets.** `D_r` = tuple positions of `state_{j-r}` depending on
  `X[j]`: `D_0 = {0}`, `D_1 = {0,3}`, `D_2 = {0,2,3}`, `D_r = {0,1,2,3}` for
  `r >= 3`.
- **The split point cancels.** `d = S - i - 1` and `r = j - S`, so
  `d + r = j - i - 1`, **independent of `S`**.
- **The threshold.** `E_d ∩ D_r` is non-empty for *every* legal split point iff
  `j - i >= 4`, and empty for *every* legal split point iff `j - i <= 3`.

Three consequences, and the second and third are the ones records get wrong:

1. **No choice of split point or component can rescue a separation below 4.**
   The batch-4 instance (`KN-TECH-bb7e9f`'s worked example) was unsalvageable at
   `j - i = 1` by any component index, and the mirror-image trap is real: reading
   tuple position 0 instead of 1 relocates the degeneracy onto the *other* word.
   Verified as a null object - the literal position-0 repair scores
   `d_fwd = 1` against `d_bwd = 16` and the gate correctly fails it.
2. **There is a third regime nobody names.** The *union* `E_d ∪ D_r` covers all
   four positions already at `j - i = 3`, one step before the *intersection*
   becomes non-empty. So at `j - i = 3` every component is tainted by exactly
   one free word - **no jointly dependent component and no clean component
   exists**. "Disjointness is the only obstruction" is false there.
3. **Above the threshold the component index stops being load-bearing.** At
   `j - i = 10` with `S = 8`, `d = 5` and `r = 4`, so all four components are
   jointly dependent and any of them passes a dependence gate identically. A
   design presented as "new separation AND new component" is doing all its work
   in the separation, and the gate has *no* discriminating power over the
   component at that separation. Say which half of a two-part correction is
   load-bearing, or a later reader will credit the wrong half.

**Provenance and scope.** Derived from RFC 1320's step table alone and
empirically confirmed by single-bit differential probing (4000 trials per
direction, union of changed positions matching the derived sets at every
distance); the split-independence and threshold were confirmed by exhaustive
enumeration over every legal `S` for `j - i = 1..8`. Three agents in this
program now concur, one of them blind to the others' implementations. This is a
**full-word algebraic** statement about the word schedule and holds for any
correct implementation of it.

## Law 2 - joint dependence does NOT imply a usable matching filter, and a `>= 2` gate cannot tell the difference

This is the law that cost a batch, and it is the reusable part.

A dependence gate that passes on `distinct >= 2` certifies **non-constancy**.
The arithmetic downstream of such a gate - "expected non-planted matches
`2^(k1+k2-k)`", "raw candidate count at most `1 + 2^(k1+k2)/2^k`" - requires
**near-injectivity** of the per-side observable maps. *Non-constancy does not
imply near-injectivity*, so a `>= 2` gate cannot discharge the premise those
numbers rest on, however prominently it is named as their discharge.

The failure has an exact shape, and the shape is what makes it predictable:

> The match condition of any MITM **factorizes** - that is what makes it a MITM.
> So the raw pre-certificate candidate set is a **level set of a factorized
> condition**, i.e. the **Cartesian product** of the two per-side fibers over
> the matched value. Its size is the **PRODUCT of the two fiber
> multiplicities**, not a sum of independent `2^-k` coincidences.

Measured instance (`BATCH-7215fa`, MD4 Round 1, separation 10, `k1 = k2 = 6`,
`m = 12`, `k = 20`, one fixed-word seed): raw candidate count **8**, against a
model expecting `1.0039` and a control ceiling of 4. The 8 is exactly
`4 x 2` - the forward and backward fiber multiplicities over the single shared
20-bit value - and 7 of the 8 fail the certificate. Both multiplicities were
already visible in numbers the gate had computed and recorded as a PASS
(forward `33/64` distinct at 32-bit and `6/64` inside the 12-bit window;
backward `24/64`). Reached independently and blind from two directions - one
reviewer from the fiber product, the other from the forward image's
non-injectivity.

**The predictive corollary, which is the point of writing this down.** Because
the count is a product of two quantities a gate already measures, the failure a
downstream control discovers *after* the search is derivable *before* it. A
gate that reports its per-side distinct counts is one comparison away from
predicting its own downstream candidate inflation.

Two further calibration lessons from the same measurement:

- **Label control thresholds `MEASURED` or `MODELED` too, not only claims.** The
  ceiling of 4 was an unlabelled modeled figure operating as a hard stop inside
  a package that scrupulously labelled every speed ratio. Over 120 fixed-word
  seeds the actual quantity ranged 2..928 with median 32, 92 percent exceeding
  the ceiling and *no* seed at the modeled value.
- **A miscalibrated threshold is not repaired by fixing the object.** The
  nearby object (MD5), whose forward map is fully injective at 32 bits at all
  120 of those seeds, *still* exceeded the ceiling at 59 of 120. The quantity
  was right; the uniformity model calibrating it was wrong.

## Law 3 - in an MD4-family Round 1, check that the free word's variation SURVIVES F before assuming it arrives

Necessary is not sufficient, and the gap has a name. Verifying that the free
word reaches all three arguments of the `F` producing the matching register is a
**necessary** condition and was correctly verified; the observable still
collapsed to 6 of 64 values.

MD4's `F(x,y,z) = XY v not(X)Z` is a **bitwise multiplexer**: bit `i` of `F` is
`y_i` if `x_i = 1` else `z_i`, so **F is constant in `x` at every bit where
`y_i = z_i`**. At one measured seed the free word's varying bits entering `F`
were `0x00001800` against a mask `y^z = 0x5c0be734` and `0x00004000` against
`0x7b7a00ae` - **zero visible bits at both applications**. MD5's step adds the
varying register *outside* `F` through `+= b`, a full 32-bit modular addition,
so no bit of it can be annihilated; measured, MD5's forward map is injective at
32 bits at every seed sampled where MD4's is injective at 6 of 120.

**This mechanism is offered as a lead, not as settled.** A second reading of
the same measurement is on record from an independent reviewer - that MD4's
Round-1 *shift table* keeps the free word's bits out of the low nine bits of the
matching register (the surviving window values were all congruent to 98 mod
512). The two may be two views of one mechanism or two mechanisms; **nothing in
that batch discriminates them**, and the entry says so rather than choosing.

## The four checks, in the order they cost the least

1. **Step-distance check. Zero compute.** Compute `j - i` and refuse any
   construction below 4 outright. No search, no gate, no run.
2. **Prediction-versus-observation adjudication. Zero compute.** Whenever an
   observed integer departs from its own pre-registered predicted integer beyond
   a declared tolerance, require an explicit recorded adjudication *even when
   the pass criterion is met*. In the worked instance the gate reported
   `distinct_fwd_12bit = 4` against a pre-registered prediction of 16 and scored
   PASS on a criterion of `>= 2`; comparing those two numbers - both already on
   the page - would have halted the batch before any control ran.
3. **Static `y^z` mask check. Sub-millisecond, no search.** For each `F`
   application on the path from the free word to the declared component, compute
   `(y XOR z)` and check that the free word's varying bits survive the
   multiplexer mask. Predicts the collapse before anything is searched.
4. **Injectivity criterion, at both resolutions.** Replace or supplement
   `distinct >= 2` with `distinct >= (1 - eps) * 2^k` for a declared `eps`, at
   32-bit *and* at window resolution, on **both** sides separately. And quantify
   over fixed-word seeds: a gate run at one seed answers "there exists a seed
   such that...", not "for all...", and the two differ by two orders of
   magnitude in the reported quantity.

**Null-object control, as standard.** Repeat every distinct-count measurement
with `F` replaced by a same-shape, same-arity non-multiplexer mixer. A
measurement that does not move under that substitution is not measuring the
construction. In the worked instance the substitution restored `64/64` against
MD4's `33/64` and `6/64`, which is what turns "the observable collapsed" from an
artifact report into a statement about `F`.

**Diagnostic vocabulary, because the wrong word sends the successor to the
wrong knob.** A channel that takes one value is **degenerate**; a channel that
takes 33 of 64 values is **lossy**. Different failure modes, different remedies.
A contract whose pre-registered vocabulary contains only the first will
misdiagnose the second.

## Limits of applicability

- Claim tier **`analyzed`**, never `supported`. `EV-MDFIVE-24e077` and
  `DEC-20260822-40bf14` cap it and three of four promotion gates are unmet
  there.
- **Law 1 transfers; Laws 2 and 3 carry scope.** The taint calculus and the
  threshold are full-word algebraic facts about MD4's Round-1 word schedule.
  Law 2's *shape* (level set of a factorized condition = product of fibers) is
  general to MITM; its measured multiplicities are not. Law 3's mechanism is
  MD4-family and is explicitly unsettled between two readings.
- **Joint FULL-WORD dependence does not imply WINDOWED distinguishability**, and
  this is the gap the calculus cannot see. At `m = 12` the dependence was
  seed-contingent: the forward window image reached 1 - full degeneracy
  recurrence on the *corrected* construction - at some fixed-word seeds.
- Every measured number here is from one bounded toy instrument: MD4 and MD5
  Round 1 (16 of 48 and 64 steps), 2 of 16 message words free, `k1 = k2` in
  `{4,6}`, `m = 12`, `k = 20`, single-core unoptimized CPython. The 120-seed and
  six-seed distributions are **reviewer-derived scratchpad computations with no
  run records** and are cited as scope evidence, never as run measurements.
- **NOTHING here bears on MD4's or MD5's preimage or collision resistance**, on
  the full primitives, on SHA-2, or on any published complexity figure, and
  nothing projects toward any instrument-class cost gap. The instrument recovers
  a *planted* pair by construction.
- **This is not a closure of anything.** In the worked instance 9 of 120 seeds
  passed the failing control and 6 gave a fully injective forward map, so a
  passing construction demonstrably exists inside the same parameter family. Do
  not cite this entry as evidence that a Round-1 splice-and-cut lane is
  obstructed.
- Novelty is **unverified**. Nothing here is claimed as novel, new, or first,
  and no external work is relied on - the two nearest references remain
  `recalled` and support nothing.
