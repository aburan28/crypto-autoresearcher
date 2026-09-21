---
id: KN-TECH-bb7e9f
type: technique
title: Splice-and-cut matching quantities - a free word that the observable has not yet consumed makes its half of the MITM degenerate
tags: [methodology, meet-in-the-middle, splice-and-cut, mitm, preimage, chunk-separation, matching-point, word-schedule, arx, merkle-damgard, md4, md5, controls, pre-registration, obstruction, design-pitfall]
confidence: verified_by_execution
complexity: >-
  Not an algorithm. The obstruction costs a whole batch when it is missed and
  seconds of algebra when it is checked: the detecting control is one
  two-directional spot-check at a scale (k1=k2=4, 256 pairs) far below any
  declared-scale run.
applicability: >-
  Any meet-in-the-middle / splice-and-cut / partial-matching construction that
  splits an iterated compression function at an interior step and declares a
  matching quantity on the boundary state - MD4/MD5-style ARX Merkle-Damgard
  word schedules directly, and by the same argument any chunk separation whose
  neutral words are chosen from a fixed step-to-word schedule.
source_refs: [EV-MDFIVE-ab007d, H-MDFIVE-bf7767, DEC-20260821-1215e5, EXP-MDFIVE-88f7d1, GOAL-MD5-001, BATCH-af29f6, KN-TECH-9d21c4, KN-TECH-080, KN-TECH-056]
added: "2026-08-21"
superseded_by: null
---

## The rule

In a splice-and-cut / chunk-separation MITM, **the declared matching quantity
must be a state component that BOTH free words have already influenced at the
matching point.** If the observable is computed strictly before one chunk's own
free word is consumed by the word schedule, that word's channel of the joint
search is provably non-discriminating: the matching-window observable and the
full-target observable are mathematically independent of it, *regardless of how
the observable is chosen within that component and regardless of how wide the
matching window is made*.

The search then still runs, still terminates, still reports a large
speedup over its naive all-pairs baseline, and still locates the *other* free
word correctly. What it does not do is what it was built to do. It measures a
one-effective-free-word locator while reporting a two-free-word joint MITM, and
every derived quantity — the speedup ratio, the matching-window collision
distribution, a nearby-object cost ratio between two primitives sharing the
schedule — inherits the degeneracy without any of them looking wrong.

This is the meet-in-the-middle instance of `KN-TECH-9d21c4`'s step 4 (derive the
contrast's forced value before measuring it). Here the forced value is not a
sign but a *constancy*: the observable's value as a function of one declared
input is constant by construction, so the statistic computed over that input
carries no information about the question.

## The worked instance

Measured in `GOAL-MD5-001` / `BATCH-af29f6` against MD4 and MD5 Round 1
(`EV-MDFIVE-ab007d`, obstruction block; ruling in `DEC-20260821-1215e5` F-2).

The frozen construction (`H-MDFIVE-bf7767`, `EXP-MDFIVE-88f7d1`):

- Round 1 uses message words `X[0..15]` exactly once, in strict index order:
  step `k+1` uses word `k`. Split point `S = 9`.
- chunk1 = steps 1..9, forward from the IV, free word = **word8** (used at
  step 9).
- chunk2 = steps 10..16, computed backward from a declared Round-1 output state
  `Y`, free word = **word9** (first used at step 10).
- Declared matching quantity: the low 20 bits of "register A immediately after
  step 9", with a 12-bit matching window.

The mechanism text asserted that chunk2's backward-computed value of that
quantity "is a function of free word9". **It is not, and cannot be.** Word9 is
first consumed at step 10, so nothing computed at or before step 9 depends on
it. The backward derivation of the after-step-9 state from the after-step-10
state recovers that register as a pass-through, fixed before word9 is ever read.

The algebra, in the instrument's own terms
(`harness/run_md4_ceiling.py` at `BATCH-af29f6`'s snapshot):

- `forward_step((a,b,c,d), xk, s, t)` returns `(d, new_a, b, c)` — a rotating
  role convention in which **tuple position 1 is the register just updated**, and
  it is the only component that depends on `xk`.
- `backward_step(state_next, xk, s, t)` returns `(old_a, old_b, old_c, old_d)`
  where `old_b, old_c, old_d = c2, d2, a2` are pass-throughs of `state_next` and
  only `old_a = rotr(rotated, s) - F(old_b,old_c,old_d) - xk - t` depends on
  `xk`. **Tuple position 0 is the only component that depends on the word
  supplied.**

Both sides read tuple position 1 of the state after step 9, so the comparison is
*self-consistent* — which is exactly why every correctness control passed. It is
the quantity, not the code, that was wrong.

### Why the correctness controls could not catch it

Every mechanical control in that batch passed exactly and none of them could
have failed:

- RFC 1320/1321 test vectors passed — they test the primitive, not the split.
- The exact step-inversion regression fixture (`HEUR-H2`, >=10,000 random
  tuples) passed — inversion *is* exact; that was never the defect.
- The `k1=k2=6` brute-force-equality control passed 64/64 — and was **vacuous**:
  the naive all-pairs baseline reads the identical word9-independent tuple
  position that the MITM search reads, so the two implementations are guaranteed
  to agree whether or not the intended construction works. A control that
  compares two readers of the same degenerate observable measures agreement, not
  correctness.

The observable signature was loud but only legible in hindsight: the
matching-window collision count was **constant across 1000 independently drawn
targets, variance exactly 0**, against a Poisson(lambda=256) prediction — 112
standard deviations out. A zero-variance statistic where a distribution was
predicted is the tell.

### The four independent reconfirmations

The finding is a derivation, not a statistical inference, and it was
independently re-derived — not merely re-read — by three roles across four
methods, with zero disagreement (`EV-MDFIVE-ab007d` `strength_note`,
`proof_refs`):

1. **Executor** (`TASK-20260821-de817d`): algebraic trace of `backward_step`'s
   return tuple plus a 20-sample empirical sweep over the declared window.
2. **Red team** (`TASK-20260821-67a1b6`, independent session): from-scratch hand
   derivation of the return-tuple algebra, plus a stronger 50-sample sweep over
   the **full 32-bit range** with a **word8 positive control** (50/50 distinct
   values), confirming the apparatus itself discriminates and only word9's
   channel is dead.
3. **Validator** (`TASK-20260821-1601d6`, independent session), method (a):
   independent from-scratch Round-1 simulators that, by construction, never
   reference word9 when computing the after-step-9 register — a definitional
   confirmation requiring no empirical test.
4. **Validator**, method (b): independent 20-sample sweep of the module's own
   `backward_step` plus a 10-target false-positive spot check against the full
   16-step forward computation.

## The cheap control that detects it

**Before any declared-scale run, run a two-directional dependence spot-check at
a scale where it costs nothing** — `k1 = k2 = 4` (256 pairs) is ample. Red-team
recommendation D1, `BATCH-af29f6` `red-team-report.yaml`; adopted as a mandatory
`proof_obligations` entry and a hard executor gate by `DEC-20260821-84a8f1`.

The check has four parts, and the fourth is the one usually missing:

1. Hold free word B fixed; vary free word A across its window. The declared
   matching observable **must take more than one value**.
2. Hold free word A fixed; vary free word B across its window. The declared
   matching observable **must take more than one value**.
3. Both directions must be run **on the same observable, read through the same
   code path, that the declared-scale run will use** — not on a
   nearby quantity that happens to be more convenient to instrument.
4. **Vary both words simultaneously only as a supplement, never as the check.**
   A joint sweep passes cleanly on a construction that is degenerate in one
   word, because the other word's variation supplies all the observed movement.
   This is the failure the one-directional-looking control does not see.

Failure in either direction is a **stop**, not a caveat: the declared-scale run
should not be executed, because it cannot measure the declared quantity. This
would have caught the instance above at negligible cost, before any compute was
spent, and its absence from the original `proof_search_map` is part of what
`DEC-20260821-1215e5` closed out.

## Open, not settled: the mirror-image trap

`EV-MDFIVE-ab007d`'s `resource_check` reads the obstruction as a diagnostic
resource — it identifies which output position of a chained backward composition
carries a supplied word's dependency (tuple position 0) versus which is a
pass-through (position 1) — and names "read position 0 instead" as a candidate
repair.

**That repair has a mirror-image risk which is NOT settled and must not be
adopted without running the control above.** Reading the same algebra the other
way round: at `S = 9`, word8 influences only tuple position 1 of the
after-step-9 state (it is consumed at step 9, which updates that register), and
word9 influences only tuple position 0 (recovered by inverting step 10). The two
free words therefore appear to influence **disjoint components** of the boundary
state, and swapping position 1 for position 0 would relocate the degeneracy onto
word8 rather than cure it. If that reading is right, *no single-register
matching quantity at a one-step-separated split is jointly discriminating*, and
the repairs that could work are structurally different:

- match on **both** components (a window on position 0 and a window on
  position 1), so each free word is filtered by the component it actually
  reaches; or
- **increase the separation** between the two free words, so backward
  propagation through the intervening fixed-word steps spreads the second word's
  influence into the register the first word updated.

This paragraph is a **coordinator reading of the module algebra
(`provenance: internal`, derived at `TASK-20260821-bc91f0`), not a measured or
independently reconfirmed result.** It is recorded here because adopting the
position-0 swap uncritically is the most likely way to repeat the batch, and
because the control above settles it either way in seconds. Do not cite this
section as established; cite it as the thing to check first.

## Scope

- The **measured** obstruction is claimed only over the exact frozen
  construction tested: MD4/MD5 Round 1, `S = 9`, matching quantity = register A
  immediately after step 9 read from `backward_step`'s tuple position 1
  (`EV-MDFIVE-ab007d` `obstruction.scope`). It is **not** claimed over
  splice-and-cut / MITM chunk separation in general, over other split points, or
  over other matching-quantity choices — those are untested, not ruled out.
- The **rule** at the top of this entry is a design constraint derived from the
  word schedule's own structure, not an empirical claim about MD4 or MD5. It
  says what to check, not what the answer will be.
- Nothing here bears on full 48-step MD4 or full 64-step MD5 preimage
  resistance, and nothing here supports or undermines any reported literature
  complexity figure (2^96 / 2^102 / 2^116.9 / 2^123.4 all remain UNVERIFIED
  provenance in this corpus).
- **ANOM-1 caveat, binding forward** (`DEC-20260821-1215e5` F-4): any record
  citing `RUN-MDFIVE-primary-md4-v2`, `RUN-MDFIVE-h1-md4`, or
  `RUN-MDFIVE-md5-conditional` raw metrics — the 2048 chunk evaluations, the
  1,048,576 naive baseline, the derived "512x", the R = 1.0 — must carry this
  entry's obstruction forward with it. Those numbers are correct measurements of
  a degenerate instrument. In particular **R = 1.0 is close to mechanically
  forced** by the schedule MD4 and MD5 share, and is not evidence of MD4/MD5
  equivalence at any scale.
- The `BATCH-af29f6` throughput figures must **not** be projected toward the
  goal's ~2^64-block instrument-class gap (`DEC-20260821-1215e5` F-8). That
  projection becomes admissible only once a non-degenerate instrument's measured
  throughput and k1/k2 scaling exist.

## For the dependent goals

`GOAL-SHA2-001`, `GOAL-SHA3-001`, `GOAL-BLAKE-001`, `GOAL-ASCON-001` and
`GOAL-SIMSPK-001` build splice-and-cut / MITM instruments against ARX and
Merkle-Damgard word schedules of the same shape. They may cite this entry as a
**demonstrated design pitfall to avoid in their own construction**, and they may
adopt the two-directional spot-check as a pre-run obligation. They may **not**
cite `BATCH-af29f6`'s 512x or R = 1.0 numbers as evidence of a genuine
two-free-word MITM speedup or of MD4/MD5 divergence
(`DEC-20260821-1215e5` F-2/F-4; `GOAL-MD5-001.next_action`).

## Citations

| Reference | Provenance | Relied on for | Verified by |
|---|---|---|---|
| `EV-MDFIVE-ab007d` (obstruction block, `strength_note`, `proof_refs`, O-1..O-5) | internal | the measured obstruction, its value, scope, and the four reconfirmations | `TASK-20260821-fb3f3c` (committed ledger archive) |
| `H-MDFIVE-bf7767` (mechanism, `proof_search_map`, `status: weakened`) | internal | the falsified mechanism statement and the frozen construction's parameters | `TASK-20260821-a288f8` (froze it); `DEC-20260821-1215e5` F-2 (weakened it) |
| `DEC-20260821-1215e5` (F-2, F-3, F-4, F-6, F-8) | internal | the rulings this entry carries forward, including the binding caveat and the cost-projection prohibition | coordinator, `TASK-20260821-fb3f3c` |
| `BATCH-af29f6` `red-team-report.yaml` (D1, `required_controls`) | internal | the two-directional spot-check recommendation | `TASK-20260821-67a1b6` (independent session) |
| `BATCH-af29f6` `validation-report.yaml` (`anom_1_independent_assessment`) | internal | reconfirmations 3 and 4 | `TASK-20260821-1601d6` (independent session) |
| `harness/run_md4_ceiling.py` (`forward_step`, `backward_step`) | internal | the tuple-position algebra quoted above, and the mirror-image reading | read directly at `TASK-20260821-bc91f0`; the position-1 fact is additionally in `EV-MDFIVE-ab007d` `proof_status_basis`, the mirror-image reading is NOT |
| RFC 1320 (MD4), RFC 1321 (MD5) — Round 1 word schedule | retrieved | step-to-word order (step k+1 uses word k) | `TASK-20260821-de817d` (rfc1320, sha256-pinned); `TASK-20260821-420070` (rfc1321, sha256-pinned) |
| Aoki, Sasaki, "Preimage Attacks on One-Block MD4, 63-Step MD5 and More", FSE 2009 | **recalled** | pointer only, for a reader wanting the splice-and-cut technique family's origin | null — **no agent in this program has read this source.** It supports nothing in this entry |
| `KN-TECH-9d21c4` (null sufficiency, step 4) | internal | the general form this entry instantiates | corpus entry |
| `KN-TECH-080` (proof_search_map, audits 1 and 2) | internal | where the missing obligation belongs in a proposal | corpus entry |
