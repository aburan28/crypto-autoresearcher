# ATTAINABILITY CHECK — ATTAIN-RR-DEP-1

TASK-20260801-040, reviewer duty 1. Verdict carried in `contract_review.yaml`
(**REVISE / DO_NOT_APPROVE**). All arithmetic below was redone in this session
from the archived arrays; nothing is accepted from the artifact under review.

---

## 0. Method and independence

The role assigned by the queue is `reviewer`; this harness has no reviewer
subagent, so the red-team contract serves it. The reviewer authored none of the
artifacts under review. **Independence here is procedural, not model-level** —
author, executor, validator and reviewer all resolve to the same Claude model —
so every quantitative claim was recomputed and every structural claim about a
construction was re-derived from driver source and then re-tested by executing
the driver's own functions.

The attainability standard applied is the one the specification fixes: *some
achievable measurement lands in every branch*, classified
DEMONSTRATED-REACHABLE or REACHABLE-IN-PRINCIPLE, **with a branch unreachable by
construction being a REVISE**.

---

## 1. The `ATTAIN-NO-MONO-DEPENDENCE` claim, checked step by step

> "NO STEP OF THIS ARGUMENT ASSUMES THAT ANY LADDER RUNG MOVES THE JOINT LAW …
> Every reachability claim below rests on exactly two things — that a count out
> of 200 or out of 20 is an achievable integer in its range, and that the two
> MEASURED endpoint objects show this instrument attaining counts at both ends
> of that range."

Checked clause by clause, against each per-branch entry.

| Entry | Does it covertly need an intermediate rung to move the joint law? | Verdict |
|---|---|---|
| D-0 | No. Uses integer ranges of counts, digest inequality, arm sizes. | claim holds |
| D-1 | No. Uses only measured ranges of Spearman and TV, and integer counts. | claim holds |
| D-5 | No. Uses integer count ranges on 200 and on 20. | claim holds |
| D-2 | No per-rung assumption — but see §3.1 and §3.2. | claim holds, premises unsound |
| D-3 | No per-rung assumption — but see §3.1 and §3.2. | claim holds, premises unsound |
| D-4 | No per-rung assumption — but see §3.1. | claim holds, premises unsound |

**Finding.** The literal `ATTAIN-NO-MONO-DEPENDENCE` claim is **upheld**: no step
of the argument assumes per-rung movement. The declaration is honest and the
confinement of the fifteen unmeasured rungs (to a domain-of-minimisation role
and to D-1's argument) is sound reasoning.

**But the declaration is not the safeguard it is taken for.** The argument avoids
the per-rung premise by resting instead on *the two measured endpoints*, and two
of the three substantive branches lean on properties of those endpoints that do
not hold:

* one of the two "endpoints" **is a ladder rung** (§3.1); and
* half of the endpoint evidence cited comes from statistics that **cannot move at
  all** (§3.2).

An argument that discharges one unsound premise by leaning on a second is not
repaired by declaring the first discharged. `ATTAIN-NO-MONO-DEPENDENCE` is
therefore recorded as **PARTIALLY UPHELD**.

---

## 2. Branch-by-branch reachability, in recomputed numbers

Every count below was recounted by this reviewer from the raw replicate arrays
in `runs/RUN-DEP-001-calib/raw-result.json` and
`results/calib/null_replicate_statistics.json`, applying the strictly-greater
rule against the archived thresholds. **All of them reproduce the frozen file
exactly.** The operational equivalence used throughout — DET-DEP-1 ⟺ count ≥ 190
of 200 — was re-derived and independently confirmed (see `anti_tuning_check.md`
§4).

### D-0 — integrity suspension
* THR-DEP-REPRO leg fires at ≥ 9 of 200. Recounted values on the genuine
  identity null DEP-CAL-A: **0, 2, 3, 2** at bits 16 and **0, 2, 1, 0** at
  bits 20. On DEP-CAL-C a count of **6 of 200** was recounted (STAT-CHI-64,
  bits 20) — three short of firing, on a scale this instrument has been measured
  on sixteen times.
* Other legs: digest inequality over 440 measured comparisons, arm size (recounted
  `pairs_recorded_per_arm_distinct = [130816]` on all 880 calibration arms),
  `degenerate_c2_zero_draws = 0`, tripwire `real_object_touched = false`, budget.
* No leg is a tautology or a contradiction over the measured quantities.

**REACHABLE-IN-PRINCIPLE.** Concur with the file.

### D-1 — the artifact tell
* Spearman is measured over **[−0.007039, +0.008515]** (bits 16) and
  **[−0.006012, +0.007791]** (bits 20) on DEP-CAL-C, and at
  **0.9999999990401287 – 0.9999999990563962** and
  **0.9999999999679635 – 0.9999999999691521** on DEP-CAL-D. All recomputed.
* K = 16 joint TV is measured over **[0.020326, 0.026801]** and
  **[0.904270, 0.929588]** (bits 16), **[0.020716, 0.026205]** and
  **[0.912251, 0.929741]** (bits 20). All recomputed.
* A nine-term or six-term sequence drawn from ranges that wide can be
  non-monotone; the two-proportion leg has both rate arguments attainable
  (2/200 and 20/20 are measured).

**REACHABLE-IN-PRINCIPLE.** Concur with the file — and note that on this
reviewer's own mechanism analysis D-1 is not merely reachable but **likely**:
§3.3 predicts a flat TV curve across the whole CELL ladder, which is exactly
what D-1's second leg is built to catch.

### D-5 — apparatus failure
* First leg fires at a DEP-CAL-C count ≥ 9 of 200. Recounted: **2, 1, 5, 2** at
  bits 16 and **1, 6, 0, 2** at bits 20; maximum 6. REACHABLE-IN-PRINCIPLE.
* Second leg. Recounted DEP-CAL-E: **0, 0, 0, 0** of 20 at bits 16 and
  **0, 0, 0, 1** of 20 at bits 20 (STAT-KS1-E2). Under the ruling in
  `contract_review.yaml § open_rr_dep_1_a` (READING-A, decided on textual grounds
  alone) the leg is **DEMONSTRATED-REACHABLE and in fact already satisfied**.

**D-5 is reachable under either reading**, as the file says. That is not the
problem. The problem is what follows in §4.

### D-2 — the sensitive reading
* Requires rho_det on the ladder and ≤ 0.05, i.e. one of {0.0025, 0.005, 0.01,
  0.02, 0.05}, by a certifying statistic at DET-DEP-1 at both cells.
* Recomputed anchor evidence: STAT-CHI-16 and STAT-CHI-64 each **20/20** at both
  cells, at recomputed threshold ratios **703.479, 56.831** (bits 16) and
  **690.930, 57.705** (bits 20).
* This reviewer additionally ran 40 paired replicates on an exactly independent
  synthetic source and measured the C1 copula shift at rho = 0.05 as **+7.33
  null-σ** on STAT-CHI-16 — comfortably past the ≈ 2.8 σ archived threshold.
  D-2 is not merely reachable in principle; the mechanism is live.

**REACHABLE-IN-PRINCIPLE** on its own terms. Concur — with the correction that
the file's supporting sentence, "the instrument demonstrably attains counts at
both ends of the range **within the certifying set**", is only half true: the
low end is supplied by STAT-KS1-E1, which cannot move (§3.2).

### D-3 — the insensitive reading — **NOT REACHABLE**
D-3 requires `rho_det = NONE_ON_LADDER` **and** `eps_det = NONE_ON_LADDER`, i.e.
that **every** certifying statistic falls below 190/200 at **every** rung of both
ladders, *including rho = 1.00*.

1. **rho = 1.00 is the anchor, bit-identically** (§3.1). The archived measurement
   on that exact object is 20/20 for both chi-squares at both cells, at ≥ 56.8×
   threshold. `rho_det = NONE_ON_LADDER` requires those same two statistics to
   fail on the same object.
2. **The file's stated measured basis for D-3 does not support D-3.** It cites
   STAT-KS1-E1 at 3/20 and 0/20 on the anchor as showing "sub-bar counts by
   certifying statistics are demonstrably attainable … at both ends of its
   measured range". STAT-KS1-E1 is provably invariant across every plant (§3.2);
   its anchor counts are null-versus-null draws and say nothing about maximal
   monotone dependence. D-3 needs *all three* certifying statistics sub-bar, and
   the two that can move are measured at maximum on the decisive rung.
3. **D-3's mandatory counterexample certificate is unobtainable.** It requires an
   object with *maximal measured rank correlation* whose *four statistics all
   fall below the archived thresholds*. The maximal-rank-correlation object is
   the anchor, measured at 703× and 56.8× **above** threshold. The conjunction is
   measured-false on the required object. So even were D-3 somehow selected, its
   mandatory refutation artifact could not be produced.

**Classification: NOT REACHABLE on the archived evidence.** Strictly, a run in
which STAT-CHI-16 fails at rho = 1.00 is not logically impossible; but the
attainability standard here is explicitly evidential — "WITH THE MEASURED
CALIBRATION NUMBERS AND NOT WITH AN ANALYTIC ARGUMENT" — and the measured
calibration numbers on the identical object contradict D-3 by a factor of 57.
The file classifies D-3 REACHABLE-IN-PRINCIPLE on grounds that are, on
inspection, evidence about something else. **This is the defect this duty
exists to catch.**

### D-4 — the intermediate reading
* First disjunct: rho_det ∈ {0.10, 0.25, 0.50, 1.00}. The endpoints bracket it
  (2/200 and 1/200 at the destruction end; 20/20 at the comonotone end), so a
  minimum located strictly between is achievable. **REACHABLE-IN-PRINCIPLE**, and
  the file's reasoning is sound apart from its false statement that the anchor is
  not the rho = 1.00 rung.
* Second disjunct: rho_det = NONE_ON_LADDER with eps_det on DEP-LADDER-CELL.
  The first conjunct is contradicted by §3.1 and the second by §3.3. **This
  disjunct is not reachable.**
* D-4's mandated deliverable, the ratio `eps_det / 0.02`, **does not exist under
  any outcome** if §3.3 holds, because eps_det is forced to NONE_ON_LADDER.

**D-4 survives on its first disjunct only, and cannot deliver the quantity its
disposition requires.**

---

## 3. The three findings the branch table rests on

### 3.1 `plant_copula(·, ·, 1.00, ·) ≡ plant_comonotone(·, ·)`, bit-identically

`plant_copula` computes `math.sqrt(max(0.0, 1.0 - rho*rho))`, which at
`rho = 1.0` is exactly `0.0`. So `z2 = z1` exactly; `ranks_ties_by_index` of the
strictly ascending `phi_inv` grid indexed by `rank(e1)` returns `rank(e1)`; the
return value is `np.sort(e2)[ranks_ties_by_index(e1)]` — `plant_comonotone`'s
body verbatim.

Verified by execution: elementwise equality on three independent seeds, and
independent of the noise stream supplied. The joint-table comparison run for
this review returns identical rows for `C1 rho=1.0` and `ANCHOR` to the last
digit (K16 TV 0.921692, K64 TV 0.969423).

The reading rule states the opposite as fact:

> "The anchor is NOT the rho = 1.00 rung. It is a different object — noiseless
> comonotone reordering rather than a Gaussian-copula reordering at rho = 1."

At rho = 1 the Gaussian-copula reordering *is* the noiseless comonotone
reordering. There is no second object.

Consequences: (a) `ladder_rungs_executed: []` and ATS-DEP-1.6's "NOT a ladder
rung" are true of the *loop* the driver ran and false of the *object* it built —
`run_calibration` never touches `LADDER_RHO`, but it does build the rho = 1.00
rung's object; (b) the declared pre-disclosure is larger than declared, since the
archive already fixes the top rung's outcome; (c) D-3 collapses as above.

### 3.2 Both KS statistics are provably constant between a source arm and any plant arm

`STAT-KS1-E1 = stat_ks1(e1_a, e1_b)` reads only the e1 arrays, and every plant
leaves e1 bit-identical (`plant_arm` returns `e1s.copy()`; CTRL-DEP-MARG enforces
it on every arm). `STAT-KS1-E2 = stat_ks1(e2_a, e2_b)` is a function of the
*empirical distribution* of e2 only, and every plant returns a permutation of the
same e2 multiset. Both statistics therefore take **identical values** on a plant
arm and on its source arm, for every family and every rung, deterministically.

Verified by execution: bitwise equality of both KS values for copula rho = 0.5,
the comonotone anchor, cell eps = 0.25 and block q = 1.00, while STAT-CHI-16 on
the same arms moved by factors 24.9, 308.6, 1.005 and 1.119.

So of the **three** CERT-DEP-1 certifying statistics, only **two** can move at
all. Every place ATTAIN-RR-DEP-1 cites a KS count as evidence about a
dependence-only object is citing a null draw:

* D-2's "counts at both ends of the range within the certifying set";
* D-3's "STAT-KS1-E1 … failed the bar at maximal monotone dependence at both cells";
* D-3's certificate paragraph, "Two of the four statistics already satisfy it";
* `excluded_statistics_none`'s "the statistic did not fire even at maximal
  monotone dependence … RECORDED AND NOT EXPLAINED" — it has a complete
  deterministic explanation, given above.

### 3.3 C2 and C3 cannot create a deviation against a source at the independence coupling

Full derivation in `alternative_class_check.md` §3. In summary: `plant_cell` and
`plant_block` build their permutation from **e1 and fresh randomness only**,
never from e2, so under an e1-independent e2 the joint law is *exactly*
unchanged. They are dependence-**destroying**, like OBJ-PLANT-DEP-0, which the
file's own D5 block classifies correctly.

Measured, by this reviewer, 40 paired replicates through the driver's own
`statistics_of`: mean shift in null σ of STAT-CHI-16 / STAT-CHI-64 —
C2 **at its top rung eps = 0.25: +0.21 / +0.16**; C3 **at its top rung q = 1.00:
+0.15 / +0.19**; against C1 at rho = 0.05: +7.33 / +1.96.

On the real INT-2 source the archived evidence points the same way: the
*maximally* destructive member of that family (uniform permutation, DEP-CAL-C)
produces a K = 16 joint TV of 0.023457 / 0.023241 — the multinomial noise floor —
plant Spearman −0.000045 / +0.000091, and exceedance counts at the nominal level.
Every C2 and C3 rung destroys a subset of what that permutation destroys.

Hence `eps_det = NONE_ON_LADDER` is **forced by construction**, not measured as
low power, and DDV-3 over the BLOCK ladder measures the nominal rate at every
rung.

---

## 4. The precedence consequence

`contract_review.yaml § open_rr_dep_1_a` rules, on textual grounds alone, that
D-5's second leg means *any* exceedance. DEP-CAL-E is produced **only** by
`run_calibration` — verified at source; `run_measurement` computes no
apparatus-identity arm — so the leg reads a quantity already frozen in the
archive that the measurement arm cannot change. The recounted archive contains
one exceedance.

**D-5 is therefore satisfied now, and D-5 precedes D-2, D-3 and D-4.** No
achievable measurement under the currently frozen pair lands in any of the three
terminal branches.

Under the specification's own definition — "A branch that is UNREACHABLE BY
CONSTRUCTION — no achievable measurement satisfies its predicate — is a REVISE" —
this is a REVISE, independently of §3.1.

---

## 5. The explicit clause checks this duty owes

**No branch keys on a ledger status — OPEN-BATCH023-B part II: HOLDS.** Verified
branch by branch against RR-DEP-1 as frozen. D-0 reads digests, hashes, counts,
arm sizes and budget events. D-1 reads Spearman values, TV values and a
two-proportion test. D-5 reads two exceedance counts. D-2, D-3 and D-4 read
`rho_det`, `eps_det` and two frozen numeric cuts. **None reads the status field
of H-DEP-001, H-EQD-001, H-SMTH-001, H-DS-001, H-IC-001, H-STR-002 or any other
ledger record, and none reads any ledger record at all.** Dispositions do name
status consequences (`H-DEP-001 becomes analyzed`), which is their proper place.
The prospective half of the BATCH-023 repair is intact.

**THR-DEP-REPRO dead lower leg: DECLARED, not silently relied on.** Present in
both the specification and the reading rule in the same words — 0 is the minimum
attainable count and is the lower band edge, so an under-rejecting instrument is
not checked by this control and must never be reported as having passed it. The
reading rule additionally marks it "COPIED FROM THE CONTRACT AND RESTATED BECAUSE
IT IS LOAD-BEARING".

**Certified classes: EMPTY, and nothing implies otherwise.** `certified_deviation_classes_after_calibration: []`,
`certified_rung_set_after_calibration: []`, `rho_det` and `eps_det` are the
literal `UNDETERMINED_NO_LADDER_RUN`. C1, C2 and C3 are each marked UNCERTIFIED
AS AT THIS FREEZE; the anchor is stated to certify nothing; the naming obligation
states plainly that the honest form of any power statement names **no** class.
This reviewer searched the file for any statement implying a class it has not
earned and found none. On this point the file is exemplary.

---

## 6. Summary table

| Branch | File's classification | This review |
|---|---|---|
| D-0 | REACHABLE-IN-PRINCIPLE | concur |
| D-1 | REACHABLE-IN-PRINCIPLE | concur (and likely to fire) |
| D-5 leg 1 | REACHABLE-IN-PRINCIPLE | concur |
| D-5 leg 2 | DEMONSTRATED-REACHABLE (READING-A) | concur — **and already satisfied** |
| D-2 | REACHABLE-IN-PRINCIPLE | reachable, but supporting evidence half unsound (§3.2); **blocked by D-5 precedence** |
| D-3 | REACHABLE-IN-PRINCIPLE | **NOT REACHABLE** (§3.1); certificate unobtainable; **blocked by D-5** |
| D-4 disjunct 1 | REACHABLE-IN-PRINCIPLE | reachable; **blocked by D-5**; mandated ratio unobtainable (§3.3) |
| D-4 disjunct 2 | (folded into D-4) | **NOT REACHABLE** (§3.1 and §3.3) |

`unreachable_by_construction: []` as frozen is therefore **not sustained**.

---

## 7. What this check does *not* conclude

It concludes nothing about H-DEP-001, H-EQD-001, H-SMTH-001 or HEUR-DS-1 in
either direction. It does not declare any direction impossible: C1 is a sound,
genuinely dependence-creating construction, and the measurement it supports
remains worth making once the defects are repaired. It does not characterise
BATCH-023 or BATCH-024 as vacuous — the batch has produced a working instrument,
a clean calibration, and four defects caught before any budget was spent on
them, which is what a pre-registration regime is for. Claim tier: **toy**.
