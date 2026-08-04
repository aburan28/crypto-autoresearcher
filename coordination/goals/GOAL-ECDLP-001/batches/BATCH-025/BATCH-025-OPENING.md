# BATCH-025 OPENING — EXP-LPF-001: FACTOR THE INTERMEDIATES

**Goal:** GOAL-ECDLP-001 · **Sub-goal:** SG-ECDLP-001 · **Question:** RQ-ECDLP-002
**Opened by:** DEC-20260801-010 (2026-08-01), which in the same record **closes
BATCH-024 as a one-cycle NON-EXECUTION**.
**Queue:** `coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/dispatch_queue.json`
**Tasks:** TASK-20260801-047 … TASK-20260801-060 · **max_concurrent:** 3
**Goal status:** `active`. BATCH-025 is the **twenty-fifth** batch against
`campaign_budget.maximum_batches = 50`, so **no pause condition fires** — stated
explicitly rather than left implicit.

---

## 1. BATCH-024 is closed as a non-execution, and no evidence record is filed

`RUN-DEP-001-measure` **was not executed**. TASK-20260801-040 returned **REVISE**
with four blocking defects and a `DO_NOT_APPROVE` recommendation;
TASK-20260801-041 recorded **APPROVAL_DETERMINATION: NOT APPROVED**. Under the
RC-24 one-cycle cap that ends the measurement arm. TASK-20260801-042 through
TASK-20260801-046 are terminal `blocked`.

**No evidence record exists because no run exists.** EV-DEP-001 and EV-EQD-002
were never written and their ids remain free. **H-DEP-001 remains `specified`.**
EV-EQD-001 is amended in **neither** direction and is not edited. The close is
recorded by goal-record amendment at this batch's opening — the BATCH-014/015 and
BATCH-022/023 precedent.

This is a **contract-design failure caught before the measurement compute**. It is
**not** a mathematical result about H-DEP-001, H-EQD-001, H-SMTH-001, H-DS-001 or
HEUR-DS-1 in either direction, and it is **not** an infrastructure failure.
Nothing timed out and no budget was exhausted.

### The four blocking defects

| id | finding |
|---|---|
| **RTB-040-1** | `plant_copula(·,·,1.0,·)` is **bit-identically** `plant_comonotone` — `sqrt(max(0,1−1)) = 0` gives `z2 = z1` gives `sort(e2)[rank(e1)]`. The frozen rule asserts the contrary. The calibration therefore measured the **top ladder rung** at 20/20 both cells at 57×–704× threshold; **D-3 is not reachable** and its mandatory maximal-rank-correlation certificate is **unobtainable**. |
| **RTB-040-2** | `STAT-KS1-E1` and `STAT-KS1-E2` are **provably constant** between a source arm and any plant arm. The effective certifying set is **two**, not three — and the attainability argument cited those immobile statistics' non-detections as evidence *about dependence*. |
| **RTB-040-3** | **TRAP-DISTRIBUTIONAL — the finding of the batch.** In `plant_cell` and `plant_block` the permutation is built from `e_1` **and fresh randomness only, never `e_2`**, so under an `e_1`-independent `e_2` the joint law is **exactly unchanged**. Both families are dependence-**destroying** and cannot create the deviation they certify against. Measured, 40 paired replicates: C1 shifts CHI-16/CHI-64 by **+7.33/+1.96** at ρ=0.05 and **+10182/+2554** at ρ=1.0; **C2 and C3 at their top rungs** shift **+0.21/+0.16** and **+0.15/+0.19**. |
| **RTB-040-4** | D-5's second leg is satisfied on **archived, non-re-runnable** calibration data and **precedes** the substantive branches. As an unbanded existential over 160 comparisons at 2/201 each, it **false-fires with probability 0.798 on a perfectly correct apparatus**. |

**What BATCH-024 got right** is recorded too, because a close is not a verdict on
the workers: the literal DESIGN-TRAP-1 criterion *passed* on an independent
re-derivation; ATS-DEP-1 *passed* in isolation with every threshold and count
reproducing exactly; no branch was added, removed or reordered; the certified
class list was empty and nothing implied otherwise; and the one place where
post-calibration latitude existed is the one place the freezing Coordinator
declined to exercise it — **which is why the defect surfaced before the budget was
spent**.

**The lane is not closed.** C1 is sound. A dependence-*creating* C2 — transposition
targets chosen using `e_2` bins as well as `e_1` bins so that σ depends on `e_2` —
is a concrete open design, ranked first behind the single next action.

---

## 2. The pattern, named because it is now the most decision-relevant fact

**PATTERN-INSTR-5. Five consecutive instruments built for this lane have been
found incapable of measuring what they claimed.**

- **BATCH-021** — a closed-form decision variable with an **object-free
  expectation**.
- **BATCH-022** — thresholds **unsatisfiable by a correct null**, making four of
  six branches jointly unreachable.
- **BATCH-023** — a power certificate against the **wrong alternative class**.
- **BATCH-024** — **dependence-destroying plants**, plus immobile certifying
  statistics and a control that false-fires 80% of the time.

**Each was caught, none by luck, all by executing rather than reasoning** — by an
independent session recomputing every number from the raw arrays, running the
driver's own functions on synthetic arms, and re-deriving structural claims from
source. That is a real result **about the method** and it is recorded as one.

**It is not a result about ECDLP.** Five batches of instrument-building have
produced **no measurement of the quantity the campaign's exponent claims actually
rest on**. Each batch was a further step *away* from the object — the input to the
claim, then the instrument for the input, then the instrument for the instrument.
Every step was individually well-argued and the composition was a drift.

**BATCH-025 stops the regress by measuring the object.** The disciplines are what
caught the defects, so they are carried in full and a fifth is added. What changes
is the target, not the rigour.

Judged as a knowledge candidate and **withheld** — see
`DEC-20260801-010.knowledge_promotion` (filed as **KN-CAND-BATCH024-A** with two
named promotion triggers).

---

## 3. What BATCH-025 does — OPEN-BATCH023-A, paid

**HEUR-DS-1 is a claim about B-SMOOTHNESS. No experiment in this campaign has
factored a single integer.**

`EXP-LPF-001` samples **genuine half-arity Semaev partial-map intermediates** at
the two frozen toy cells, bounded by the frozen `D = 2**32` and `2**40`, and
**factors them** — largest prime factor and B-smoothness indicator for every one of
the **130816** exhaustive `i < j` half-tuples per cell — then compares the
resulting distribution against the **Dickman ρ(u)** prediction.

Both named repairs of OPEN-BATCH023-A are discharged: thresholds are calibrated
against a **measured null at the actual X** instead of the asymptotic ρ, and the
enumeration is `i < j` so the diagonal is excluded **by construction**.

### The absolute-vs-relative design statement (ABS-REL-LPF-1)

> **HEUR-DS-1 IS AN ABSOLUTE CLAIM AGAINST A THEORETICAL REFERENCE, NOT A RELATIVE
> CLAIM AGAINST A SECOND SAMPLE**, and this experiment is built on that distinction
> rather than around it. **LIMB B, the absolute limb**, is tested by
> `R(u) = p_hat(u)/ρ(u)` against the frozen band `[1/8, 8]`, with ρ **theoretical**
> and never replaced by a sample. **LIMB A, the relative limb**, is tested by
> reading each certifying statistic against the **measured** order-statistic band of
> 200 uniform-integer replicates at the same `n` and the same `X`. **The
> matched-bitlength uniform-integer arm is a CALIBRATION OF THE APPARATUS and is NOT
> THE COMPARISON** — its first duty is to measure how far a *known-uniform* sample
> departs from the asymptotic prediction at this finite X, and **if the uniform arm
> itself leaves `[1/8, 8]` at a rung, LIMB B is NOT DECIDABLE at that rung by this
> apparatus** — reported as a statement about the apparatus, never about the Semaev
> map. A two-sample comparison is **blind by construction** to any deviation both
> arms share (ALT-CLASS-DEP-1's **U1**), so **no branch may be satisfied by a
> two-sample agreement alone**, `STAT-KS2-CAL` is declared **non-certifying**, and
> no deliverable may report a two-sample agreement as evidence for HEUR-DS-1.
> **Conflating the calibration with the comparison is what made BATCH-023's result
> bound half of what it appeared to.**

The cost of the measured band is declared, not hidden: it is **uncertified class
V1** — a departure a uniform sample shares at the same magnitude and sign is
absorbed by LIMB A's band, and only LIMB B can see it.

### The BATCH-022 tail failure, repaired

`TAIL-DS-1` sets `p_ext = min_j ρ(u_j)` and passes iff `n·p_ext ≥ 1`. On a correct
sample `n·p_ext` at the maximum is asymptotically `Exp(1)`, so **P(pass) = 1/e =
0.3679 on a perfectly correct uniform sample** — and at the toy X the asymptotic ρ
*under-predicts* deep-tail smoothness, pushing it lower still, **in exactly the
direction that would be misread as a Semaev finding**.

`TAIL-LPF-1` replaces it: the statistic is the **tenth** largest
`Z_j = ln(N_j)/ln(P_max(N_j))` (rank 10, not rank 1 — an extreme order statistic
has an unstable law and that was the proximate cause), read against a **two-sided
measured band** `[2nd, 199th]` of the 200 uniform replicates with an exact
pre-datum false-fire probability of `4/201 = 0.0199`. **Attainability must be
demonstrated with measured numbers in both directions before the rule freezes** —
upward by the derivable-smooth product control, downward by the rough ladder's top
rung. A missing demonstration makes that direction uncertified; both missing
strikes the statistic.

The general rule: **the reference is theoretical and the threshold is measured.**
The analytic law enters through the *statistic*, which is what makes the comparison
absolute; the threshold is always a measured order statistic, which is what makes
the test attainable at a finite X.

---

## 4. The five disciplines

1. **Attainability** — `ATTAIN-RR-LPF-1` in measured numbers, every branch
   classified, checked as a named reviewer duty; a branch unreachable by
   construction is a REVISE. **Extended by three clauses from BATCH-024**: no
   branch keys on a ledger status; **no control leg may be an unbanded existential**
   (every aggregating leg carries an exact binomial band whose false-fire
   probability the reviewer recomputes, >0.02 being a REVISE); and **no branch may
   depend on a quantity the measurement arm cannot change**.
2. **Calibration-first with anti-tuning** — `ATS-LPF-1` hash-binds the threshold
   **rule** before the numbers exist and the **driver** across the
   calibration/measurement boundary; the object-level blindness check is mandatory,
   because RTB-040-1 shows a label-level check misses the failure.
3. **Decision-variable variation** — `DVV-LPF-1` plus `DECAY-LPF-1`, the named
   artifact tell: `p_hat(u)` must decay across the u sweep on both arms.
4. **Alternative-class declaration** — `ALT-CLASS-LPF-1`: **S1/S2/S3** certified,
   **V1–V7** uncertified, verified against **driver source**.
5. **NEW — per-rung demonstrated perturbation movement (`PERTURB-MOVE-1`)** —
   *every plant or perturbation must be demonstrated to move the statistic it is
   meant to move, by measurement at **every rung it certifies**, not at endpoints
   only*, written as machine-readable rows (family × rung × cell × statistic). A
   rung with no recorded movement is **uncertified**; a family whose top rung shows
   no movement is **struck**. At BATCH-024 the analogous control `CTRL-DEP-MONO`
   went **unevaluated** and that is exactly where the failure hid.

Both directions are measured — a **smooth** ladder and a **rough** ladder — because
intermediates smoother *or* rougher than reference are both departures, and a
one-sided instrument reported as two-sided is AP-3 in a new coat.

**The budget is gated, not hoped**: a 10 000-sample pilot per cell projects the
full cost and **aborts before bulk work** if it exceeds budget. An abort is a
**budget event** (L-0), never a result, and **silent scope reduction is forbidden**.
Every factorization is **re-verified at 100 %** — a factorization this experiment
did not verify is not a measurement.

---

## 5. Why a new experiment id

**EXP-LPF-001 supersedes EXP-SMTH-001 by addition. EXP-SMTH-001 is not edited, not
amended, not versioned and not re-scored.** It is frozen, hash-bound, `review_required`,
never approved and never run; its fatal defect is a property of its **frozen decision
rules**, and a defect in a frozen rule cannot be repaired inside the frozen file
without destroying the only thing a freeze is for.

The harder half of the argument is stated rather than avoided: when EXP-EQD-001
followed EXP-SMTH-001 the justification was that the **measured quantity differed**,
and **that justification is not available here** — EXP-LPF-001 measures exactly what
EXP-SMTH-001 was built to measure. The individuating difference is the **frozen
apparatus**, and an experiment is individuated by its frozen apparatus as much as by
its object. Filing it as an EXP-DS-001 control is independently barred by that lane's
`new_dependencies` clause.

`d_half`, the `D_formula`, `u_star_formula`, `c = 8`, `min_samples_per_bit_size`, both
`Bsm` ladders, the ρ reference table and AP-1 are **inherited as quotations**.
`DREAD-LPF-1` carries EXP-SMTH-001's flagged-but-never-adjudicated `D` reading to the
reviewer, who must confirm or reject it.

---

## 6. Carried forward

| item | status in BATCH-025 |
|---|---|
| **OPEN-BATCH023-A** | **The single next action.** Discharged only by a valid, reviewed, archived measurement run — not by this opening. |
| OPEN-BATCH022-A | Mitigated, not repaired (manifest.yaml + five `.log`/`.json` companions). |
| OPEN-BATCH022-B | Mitigated, not fixed. Every id re-checked free; mandatory re-check at TASK-20260801-060. |
| OPEN-BATCH023-B | Second half repaired and retained; first half mitigated only, blocker named. |
| OPEN-BATCH024-A | Open, **not repaired**, and its scope changed — its anticipated instance never occurred (EV-EQD-002 unwritten); it acquires a new instance in EXP-LPF-001 ⊃ EXP-SMTH-001. |
| RT049-B6 | Open, not attacked; carried as **V7**. Sharpened: the base measured here **is** that small-x window. |
| KN-CAND-BATCH023-A | Withheld. Route (a) **went unrun**, not failed. Route (b), the derivation note, is now the cheaper route. |
| **KN-CAND-BATCH024-A** | **New.** The five-failure pattern, filed and **withheld on the merits** with two named promotion triggers. |
| Model-independence caveat | Unchanged and standing. Independence is **procedural, not model-level**; nothing here is admissible toward the rule-13 quorum. |

---

## 7. Forbidden throughout

`support` for H-LPF-001 / H-SMTH-001 / H-DS-001 / H-EQD-001 / H-DEP-001 ·
**validation or refutation of HEUR-DS-1 above toy tier, in either direction** ·
`reject_scoped`, in particular reject_scoped-as-impossibility · asymptotic promotion
(G1–G4 stay **OPEN**) · S1_met / F1_met / F2_met / structure_gate_passed ·
`dominated_by: null` · any characterization of BATCH-021…024 as vacuous or worthless
(premature closure, `docs/inventor-protocol.md` §4). Do not edit any EXP-SMTH-001,
EXP-DS-001, EXP-EQD-001 or EXP-DEP-001 artifact; do not alter H-SMTH-001, H-DS-001,
H-EQD-001, H-DEP-001, H-IC-001 or H-STR-002. Leave FAEST and XEDN alone.
**Toy ceiling throughout.**
