# TASK-20260801-068 — DUTY: ATTAINABILITY, RE-RUN FROM SCRATCH

RTB-068. **Not inherited from BATCH-025.** A regenerated `moving_rungs` changes
what is certified, what is certified feeds the L-1 stop condition and the S1/S2
certified sets, so the whole argument is re-run below against RR-LPF-2's lists
with measured numbers I recomputed myself.

## 1. The stop condition — L-1's second leg, checked independently

L-1 fires if "the PERTURB-MOVE-1 table records no movement at the top rung of a
ladder the reading rule certifies". This leg reads only archived calibration
data and L-1 **precedes** L-2, L-3 and L-4. If it pre-fires, L-2/L-3/L-4 are
unreachable by construction and the honest outcome is a recorded non-execution.

I enumerated the certified ladders from RR-LPF-2's regenerated table and read
each one's γ = 0.05 flag from the archive, not from the file.

**17 certified ladders. All 17 carry `LPF_movement_beyond_noise_flag: true` at
γ = 0.05.**

| ladder | bits 16 shift | bits 20 shift |
|---|---|---|
| SMOOTH / RATE-u=2 | +25.38211814958014 | +23.97639267785667 |
| SMOOTH / RATE-u=3 | +70.69803425039191 | +66.4325394132197 |
| SMOOTH / RATE-u=4 | +170.3398684821999 | +198.1358444438846 |
| SMOOTH / RATE-u=5 | +4.928982381230005 | +1.5157382944804918 |
| SMOOTH / KS-DICK | −4.277881482048617 | +11.846436987916968 |
| ROUGH / RATE-u=2 | −11.247560419591414 | −11.20630412294969 |
| ROUGH / RATE-u=3 | −5.3454001367869255 | −4.179625884671969 |
| ROUGH / RATE-u=4 | −1.7006351034527154 | −1.6050787109131792 |
| ROUGH / KS-DICK | −4.198668668884978 | (STRUCK, D9) |

Minimum |top-rung shift| over the 17 = **1.5157382944804918**, at SMOOTH /
RATE-u=5 / bits 20 / γ=0.05 — exactly the `certified_top_rung_minimum_absolute_shift`
and `_location` the file records.

**L-1's SECOND LEG IS FALSE. It does not pre-fire. L-2, L-3 and L-4 remain
reachable.** Verified against the archived flags, not against the file's
assertion.

### The author's stop-condition re-run, checked claim by claim

| claim | my finding |
|---|---|
| all seventeen certified ladders carry a true γ=0.05 flag | **CONFIRMED**, table above |
| the three differences are at γ = 0.005, 0.01 and 0.001 | **CONFIRMED** (DIFF-1 0.005, DIFF-2 0.01, DIFF-3 0.001) |
| none of the three is a top rung | **CONFIRMED** — the top rung is 0.05 and none of the three is 0.05 |
| no certified-or-STRUCK status changed | **CONFIRMED** — 28/28 statuses identical between RR-LPF-1 and RR-LPF-2, and 28/28 equal to (`certified` iff γ=0.05 flag true) |
| L-1's second leg still FALSE | **CONFIRMED INDEPENDENTLY** |

## 2. Branch by branch, band by band, with measured numbers

### L-0 — REACHABLE-IN-PRINCIPLE. Correct.
No measured object lands here, correctly: the calibration completed valid with
`LPF_factorization_verified_fraction 1.0`, the tripwire false, no budget event.
The refusal machinery was exercised (driver refuses in measure mode with no
receipt, a PENDING receipt, and an APPROVED receipt with no reading rule).
Reached by any integrity or infrastructure failure of the measurement run. It is
not demonstrable without breaking the run, and classifying it
REACHABLE-IN-PRINCIPLE rather than DEMONSTRATED is the honest label.
**Producing arm: MEASUREMENT (the run's own integrity records).**

### L-1 — REACHABLE-IN-PRINCIPLE. Correct.
Reached through the DECAY-LPF-1 leg, which the MEASUREMENT arm produces. I
recomputed the calibration's uniform-arm `p_hat(u)` 200-replicate means:
bits 16 `3.591e-01, 7.061e-02, 1.008e-02, 1.595e-03, 2.192e-04` — **strictly
decreasing**; bits 20 `3.461e-01, 6.346e-02, 8.075e-03, 8.674e-04, 1.006e-04` —
**strictly decreasing**. So the null does not fire the leg, which is the correct
behaviour for a null and shows the leg is not trivially true. The movement leg is
FALSE by construction and is stated as such; L-1 does not depend on it for
reachability. **Producing arms: decay leg MEASUREMENT; movement leg CALIBRATION
ONLY, disclosed.**

### L-5 — REACHABLE-IN-PRINCIPLE. Correct, and honestly two-thirds spent.
- Leg 1 (identity count vs cut 4): archived counts recomputed from
  `apparatus_identity_report.json` — bits-16 uniform 4/60, bits-16 synth 3/60,
  bits-20 uniform 3/60, bits-20 synth 1/60. Max 4, and 4 does not exceed 4.
  **Does not fire. CALIBRATION ONLY, cannot change.** The zero margin at bits-16
  uniform is real and is recorded rather than rounded away.
- Leg 2 (product control undetected): all seven ids detected 20/20 at both cells.
  **Does not fire. CALIBRATION ONLY, cannot change.**
- Leg 3 (Dickman reproduction > 1%): worst archived relative discrepancy
  1.5441749690432644e-05 against a 0.01 threshold; the measurement run
  recomputes it from its own solver. **MEASUREMENT ARM — the leg that keeps L-5
  reachable.**

**The honest statement is that L-5 is two-thirds spent, not unreachable, and the
file says exactly that.**

### L-2 — DEMONSTRATED-REACHABLE. Confirmed with measured numbers.
- I re-verified that every band edge is the rank-2 / rank-199 ascending order
  statistic of the archived 200-value array, for all 14 (cell, statistic) pairs.
  **All 14 verified; 0 mismatches.** Rejection is strict, so 198 of 200 LPF-CAL-A
  replicates are interior on each statistic by construction.
- R(u) over all 200 replicates at every POWERED rung, recomputed from the archived
  per-rung minima and maxima divided by the driver's own ρ at the recomputed u:
  bits 16 `1.161–1.184, 1.410–1.483, 1.876–2.226, 3.659–5.346`;
  bits 20 `1.116–1.140, 1.273–1.350, 1.516–1.785, 1.940–3.146`.
  **All wholly inside `[1/8, 8]`.** (The file writes 1.939 for a value I get as
  1.9395; a rounding difference, non-decisional.)
- Counting directly, **193 of 200** bits-16 and **191 of 200** bits-20 replicates
  are interior on all five retained ids simultaneously.
- Sub-floor plant rungs also land here: I checked every retained id at both cells
  and confirmed **no band exit** at SMOOTH γ=0.0005 and at ROUGH γ=0.0005, 0.001,
  0.002, 0.005 and 0.01.
**Producing arms: MEASUREMENT for the real arm's statistics and R(u), MEASUREMENT
for the fresh uniform arm's R(u).** Both legs read quantities the measurement
produces.

### L-3 — DEMONSTRATED-REACHABLE. Confirmed by three distinct measured objects.
I recomputed each against the archived band edges:
- OBJ-CTRL-PRODUCT: RATE-u=2 **ABOVE** band at both cells (plant mean 1.0 at
  both; shifts +502.122, +479.603).
- OBJ-PLANT-SMOOTH γ=0.001: RATE-u=4 **ABOVE** band at both cells (0.011067 vs
  upper 0.010679; 0.009085 vs upper 0.008722; +3.406, +4.036 null sd).
- OBJ-PLANT-ROUGH γ=0.02: RATE-u=2 **BELOW** band at both cells (0.353503 vs
  lower 0.356241; 0.339867 vs lower 0.342687; −4.366, −4.566 null sd).
**Both directions and both plant families.** The D2 caveat travels correctly —
the product-control shifts may not be read as effect sizes, and at bits 16
RATE-u=2's plant mean is saturated at exactly 1.0 with `plant_sd 0.0`.
**Producing arm: MEASUREMENT for every leg.**

### L-4 — DEMONSTRATED-REACHABLE. Confirmed in both of its first two clauses.
- "direction differs between cells": SMOOTH γ=0.05 on KS-DICK is **BELOW** band
  at bits 16 (−4.278) and **ABOVE** band at bits 20 (+11.846). Verified directly
  against the archived band edges.
- "departure at exactly one cell": the rank-2/rank-199 construction puts exactly
  two replicate values outside each band; the bits-16 KS-DICK minimum
  0.0474559686888454 is strictly below the bits-16 lower edge
  0.04749419031311155, while 198 of 200 bits-20 KS-DICK replicates are interior.
  The two cells are separate curve instances from disjoint streams.
- Third clause is NOT demonstrated and is labelled as such; under OPEN-RR052-B
  READING A as ruled at TASK-20260801-054, a struck statistic cannot trigger it.
  A branch is reachable if ANY clause is, and two are.
**Producing arm: MEASUREMENT for every leg.**

## 3. The three ATTAIN-LPF-1 extensions

**(i) No branch keys on a ledger status.** I read all six conditions clause by
clause. None reads the `status` field of any hypothesis, experiment, evidence,
decision or goal record. L-2/L-3/L-4's *dispositions* name status consequences
for H-LPF-001, which is their proper place and is not a condition. **HOLDS.**

**(ii) No control leg is an unbanded existential; every aggregating leg's
false-fire probability recomputed, and a value above 0.02 is a REVISE.**
I recomputed the exact binomial upper tail with `math.comb` at
`p = 4/201 = 0.019900497512437811`:

| n | cut | P(X > c) | next lower c | P | admissible? |
|---|---|---|---|---|---|
| 60 | 4 | **0.006883** | 3 | 0.031696 | yes; 4 is the unique smallest |
| 80 | 5 | **0.005322** | 4 | 0.021937 | yes; 5 is the unique smallest |
| 140 | 7 | **0.007246** | 6 | 0.022567 | yes; 7 is the unique smallest |

Every one is **below 0.02**; every next-lower candidate is above it. The written
integer 4 is the admissible cut at n=60 and is BELOW the admissible cut at n=80
and n=140, i.e. more readily firing — and firing L-5 SUSPENDS the rule and
yields no disposition in any direction, so the deviation is in the conservative
direction. RTB-054-5's corrections (0.007246, 0.022567, 0.005322 against the
frozen 0.007293, 0.022712, 0.005321) are exactly what I get; **no cut and no
admissibility verdict changes**, and RR-LPF-2 correctly records them beside the
frozen figures rather than editing them.

Other aggregating legs: L-3's false-fire on a correct null is
`5 × 2 × (2/201)² = 9.90e-04` — **below 0.02**. L-5 leg 2 aggregates
non-detection of a control detected 20/20 by all seven ids at both cells.
The per-comparison band false-fire is `4/201 = 0.0199` — **below 0.02**, and the
tie caveat makes it an upper bound, never an understatement.
**No leg above 0.02. HOLDS.** (L-4's ≈0.18 is not a false-fire of a departure
claim; it is the design's inconclusive residual, and it is disclosed as the
dominant null outcome after L-2.)

**(iii) No branch depends on a quantity the measurement arm cannot change.**
Leg by leg, naming which arm produces what: L-0 measurement; L-1 decay leg
measurement (movement leg calibration-only, FALSE, disclosed, and L-1 does not
depend on it); L-5 leg 3 measurement (legs 1 and 2 calibration-only, FALSE,
disclosed); L-2 both legs measurement; L-3 all legs measurement; L-4 all legs
measurement. **Every branch has at least one leg the measurement arm produces.
HOLDS.**

## 4. Did change (a) remove any demonstration a branch rests on?

Checked rather than assumed. The demonstrations above rest on band rejections,
interior LPF-CAL-A replicates, measured R(u) ranges, and the rank-2/rank-199
construction. **None of them reads a `moving_rungs` list**, and the three
regenerated differences are at γ = 0.005, 0.01 and 0.001 — rungs no demonstration
cites. Indeed the correction cuts the right way: L-2's `lands_here_from_the_ladders`
already listed ROUGH γ=0.005 and γ=0.01 at bits 16 as producing no band
rejection, which are precisely the rungs change (a) removed from the certified
list, so the two archived criteria now agree.

## 5. End-to-end null probability of reaching L-2, and could the favourable branch have failed?

Frozen point estimate 0.818, interval `[0.789, 0.980]`, both unchanged.
RTB-054-4 is carried unrepaired and is correctly recorded: the stated REASON
("the joint law … is not archived per replicate") is false — the per-replicate
joint law within a cell IS archived, and I used it to count 193/200 and 191/200
interior replicates. The reviewer's better estimate ≈0.85 lies **inside** the
frozen interval, so no conclusion changes and the numbers are correctly not
edited.

**Could the favourable branch have failed? YES.** On a correct null L-2 is
reached about 82–85% of the time and L-4 about 18%, so L-2 is not a branch that
could not have failed. Nor is it the BATCH-022 defect, where TAIL-DS-1 admitted a
correct null with probability 1/e = 0.368 and was unsatisfiable in the deep tail.
The design's central trade is stated plainly: both-cell agreement buys ≈0.1%
false-departure protection at the price of ≈18% inconclusive on a perfectly
correct sample, and the dominant null failure mode is L-4, not L-3.

## 6. Duty verdict

**PASS.** All six branches reachable; L-0/L-1/L-5 REACHABLE-IN-PRINCIPLE with
their spent legs disclosed; L-2/L-3/L-4 DEMONSTRATED-REACHABLE with measured
numbers I recomputed; **no branch is unreachable by construction**; all three
extensions hold; **L-1's second leg is still FALSE under the regenerated lists**,
so L-2/L-3/L-4 remain reachable and the honest outcome is NOT non-execution.
