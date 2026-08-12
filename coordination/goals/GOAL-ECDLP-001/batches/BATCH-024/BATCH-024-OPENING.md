# BATCH-024 OPENING

- **Goal:** GOAL-ECDLP-001 (sub-goal SG-ECDLP-001), question RQ-ECDLP-002
- **Opened by:** DEC-20260801-009, 2026-08-01
- **Queue:** `coordination/goals/GOAL-ECDLP-001/batches/BATCH-024/dispatch_queue.json`
- **Experiment:** EXP-DEP-001 — **Hypothesis:** H-DEP-001 (`specified`)
- **Tasks:** TASK-20260801-033 through TASK-20260801-046
- **Status:** GOAL-ECDLP-001 stays `active`. BATCH-024 is the **twenty-fourth**
  batch against `campaign_budget.maximum_batches = 50`, so **no pause condition
  fires** — stated explicitly rather than left implicit.

## 1. The single next action being executed

BATCH-024 executes, as written, the single `next_action` recorded in
`ledger/goals/GOAL-ECDLP-001.yaml` at the BATCH-023 close (DEC-20260801-008):
**run RT049-CTRL-1, the dependence-only plant, before any replication, under a
new experiment id and a new frozen contract, never as an edit of the immutable
hash-bound EXP-EQD-001 artifacts.**

## 2. Why this experiment

BATCH-023 measured no detectable departure of the deterministic factor base's
fibre invariants from a random base's — six of six failing to reject at a
family-wise level of 0.0582 — and the independent red team then showed the
result **bounds far less than it appears to**.

The only alternative class against which any power was ever measured is an
**e_1-marginal plant**: the frozen driver replaces `out1[idx]` and returns
`e2.copy()`. **No rung of that ladder moves DEPENDENCE at fixed marginals.** The
certified power is therefore against the **wrong alternative class**, and a
copula-type deviation of **arbitrary magnitude** remains entirely unexcluded.
Since the real base is a **small-x window** — max x = 1052 against p = 46663 —
that is exactly the shape a structured base would produce.

**Why not the replication first.** Running the mandatory second-seed replication
first would *replicate a measurement whose power against the relevant
alternative class is unknown*, producing a second number of the same unknown
informativeness. This batch decides whether EV-EQD-001's non-rejection is a
meaningful bound on the **joint law** or only on the **e_1 marginal**, and that
answer determines what the replication should even be testing. Cost is not a
reason to defer: the whole archived BATCH-023 calibration ran in 59.19 s at
176 MB peak RSS.

**The cost of this ordering, stated not hidden.** Ranking this ahead of
OPEN-BATCH023-A defers the program's oldest debt — the direct smoothness
measurement of HEUR-DS-1 — by one more batch. That is a real cost. It is ranked
*immediately* behind, not dropped, for one reason: it needs a fresh
design-and-review cycle, whereas CTRL-1 is a bounded calibration arm over an
existing validated apparatus.

## 3. The design (RT049-CTRL-1 as specified)

- **OBJ-PLANT-DEP-rho** (primary, class C1): take a **correct null arm**, leave
  `e_1` untouched, and reorder `e_2` by a Gaussian copula to a target Spearman
  rho. `e_2` is a **permutation of its own multiset**, so **both marginals are
  bit-identical by construction**. Ladder:
  `[0.0025, 0.005, 0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 1.00]`.
- **OBJ-PLANT-DEP-CELL-eps** (class C2): exchange `e_2` between record pairs in
  **different e_1 bins**, moving a fraction `eps` of half-tuples — the same
  units as the BATCH-023 `delta` ladder, so the two floors are a **ratio**, not
  an impression. Ladder: `[0.005, 0.01, 0.02, 0.05, 0.10, 0.25]`.
- **OBJ-PLANT-DEP-BLOCK-q** (class C3): coarse two-stratum block reordering, as
  a **shape check** on C1 and C2. Ladder: `[0.05, 0.25, 1.00]`.
- **CTRL-DEP-MARG — MANDATORY INTEGRITY CHECK.** Every planted arm records
  sha256 digests of the sorted `e_1` and `e_2` arrays plus K = 16 and K = 64
  one-dimensional marginal histograms on source and plant. **A mismatch is
  instrument failure and never a result.**
- **R_REPS = 200**, not 20 — the coarseness of the 20-of-20 bar was a real
  limitation last batch — with **exact Clopper-Pearson intervals** for all four
  statistics at both cells. `DET-DEP-1` requires rate ≥ 0.95 **and** one-sided
  95% lower bound ≥ 0.90.
- **Thresholds are the ARCHIVED EXP-EQD-001 CAL-1 thresholds, used unchanged**,
  and the map and statistics are **imported read-only** from the hash-bound
  EXP-EQD-001 driver (`CTRL-DEP-EQDHASH`). This is a power measurement of the
  test EV-EQD-001 *actually performed*; a re-implementation would characterize a
  different test. **No EXP-EQD-001 file is written, edited, renamed or staged.**
- **Cells:** `generate_instance(2301, 16)` and `generate_instance(2301, 20)` —
  the *same* instances, deliberately, for comparability. **This is therefore not
  a replication and can never count toward `replicated`.**

### The design trap that was avoided in the contract

`DESIGN-TRAP-1`: permuting `e_2` *within strata that coincide with the
chi-square bins* leaves the K × K contingency table **exactly invariant**. Such
a measurement returns the nominal false-rejection rate at every rung **by
construction** and would look like a finding of zero power while measuring
nothing. The copula construction moves mass **across** bins; `DIAG-DEP-RHO`
measures the induced dependence separately as the decision-variable variation
check.

## 4. The reading, declared in advance in BOTH directions

The whole branch structure is frozen in `specification.yaml` **before any
datum**; `RR-DEP-1` may only substitute measured numbers. Precedence:
D-0, D-1, D-5, then exactly one of D-2, D-3, D-4.

| Branch | Condition | Reading |
|---|---|---|
| **D-2** | `rho_det` on the ladder and `rho_det ≤ rho_star = 0.05` | EV-EQD-001's reading amended **UPWARD** by the superseding record EV-EQD-002. Disposition `replicate`. |
| **D-3** | Neither the copula nor the cell family reaches the bar at **any** rung at both cells | EV-EQD-001's reading amended **DOWNWARD** to "the two marginals are not distinguishable and the joint was not effectively tested". Disposition `weaken`, **with a mandatory counterexample certificate**. `reject_scoped` forbidden. |
| **D-4** | Detects, but only above `rho_star` | Measured floors recorded as numbers, with the ratio `eps_det / 0.02`. Disposition `refine`. |
| **D-0 / D-1 / D-5** | Integrity, artifact tell, apparatus failure | Rule **suspended**; `inconclusive` on the instrument; EV-EQD-001 not amended in either direction. |

**EV-EQD-001 is immutable and is never edited.** Either way it is superseded
**by addition** through **EV-EQD-002**.

## 5. The three process disciplines, all carried

1. **Attainability.** `ATTAIN-RR-DEP-1` freezes with an argument **in measured
   numbers** showing some achievable measurement lands in every branch, with
   each branch classified DEMONSTRATED-REACHABLE or REACHABLE-IN-PRINCIPLE. It
   is a **named** duty of TASK-20260801-040 with its own deliverable file and
   the reviewer's rejection is a **REVISE**. It caught two fatal defects at
   BATCH-022 and confirmed reachability by direct conjunction evaluation at
   BATCH-023.
2. **Calibration-first.** The calibration arm runs before the reading rule is
   frozen; `ATS-DEP-1` keeps that from becoming tuning — the rule is hash-bound
   *before* calibration, calibration supplies a **number and never a choice**,
   the calibration arm never sees real data (structural tripwire), and the
   driver is authored complete and hash-bound at calibration time so the
   measurement arm must run the identical file.
3. **Decision-variable variation — and, new and most important, the power
   certificate must be against the RIGHT alternative class.** `ALT-CLASS-DEP-1`
   states which classes each statistic will have power against and which remain
   uncertified, and a **third named reviewer duty** checks it against the driver
   source. This is the exact defect the batch exists to repair.

### One declared pre-disclosure

`DEP-CAL-D`, the comonotone attainability anchor, is measured in the calibration
stage and its outcome partially foreshadows the substantive result. This is
**declared** (`ATS-DEP-1.6`), and it is admissible only because the entire branch
structure, cuts, ladders, detection bar and statistic family are hash-bound
*before any datum*. Concealing it would have been the dishonest option; running
it after the freeze would have left attainability unverifiable.

## 6. The alternative-class declaration (ALT-CLASS-DEP-1)

**CERTIFIED AGAINST**, conditional on a valid run: **C1** global monotone rank
dependence at exactly preserved marginals (copula reordering), at the rungs
measured and only those; **C2** local joint-cell mass transfer at exactly
preserved marginals (cross-e_1-bin `e_2` exchange), at the fractions measured;
**C3** coarse two-stratum block reordering at exactly preserved marginals.
**Carried forward, not re-measured:** **C0**, uniform re-randomization of the
`e_1` coordinate on a `delta` fraction (certified `delta = 0.05`, branch-level
floor `delta = 0.02` per EV-EQD-001).

**UNCERTIFIED AFTER THIS EXPERIMENT — this list is part of the result:**
**U1** any dependence deviation both arms *share* (two-sample cancellation);
**U2** any deviation on joint cells too sparse for K = 16/64 to resolve, or below
the smallest CELL rung; **U3** any dependence invisible to a rank correlation and
not expressible as cell-mass transfer (higher-order/conditional dependence with
zero rank correlation and balanced cell margins); **U4** any `e_2`-marginal-only
deviation finer than 1/64 of the field — already a declared EV-EQD-001 blind
spot, not closed here; **U5** any object other than the two frozen toy instances,
any other Bfb, arity, intermediate, enumeration or field size; **U6** the
separation of "deterministic selection rule" from "small-x window" (RT049-B6),
which this experiment does not attack and against which the L1 cancellation
argument does **not** protect.

*No deliverable may describe this apparatus as having power against "dependence"
without naming which of C1, C2, C3 the claim rests on and without carrying
U1–U6.*

### U1 deserves to be read, not skimmed

**A two-sample design is blind BY CONSTRUCTION to any deviation both arms
share.** The chi-square is a test of homogeneity with *pooled* expectation and
the KS statistic compares the two empirical CDFs to each other, so any feature
common to the real and the null arm enters the pooled total and **cancels
identically**.

This is **a permanent structural limit of this entire comparison family — not a
limitation of this run, and not something a bigger ladder, more replicates or a
finer grid can fix.** No amount of power against C1, C2 or C3 touches it. If the
fibre invariants of *any* 512-point factor base on these curves are
systematically non-generic in a way that matters for smoothness, **neither
BATCH-023 nor BATCH-024 can see it**, and the same will be true of RT049-CTRL-5
and of every successor built on a matched-null two-sample comparison. Closing U1
requires a **different design** — an absolute comparison against a theoretical
reference, which is the question HEUR-DS-1 actually needs and which
OPEN-BATCH023-A still owes.

Whoever picks up this campaign next should read U1 before reading any detection
rate in this batch.

## 7. Open items — what this batch discharges and what it does not

| Item | Disposition in BATCH-024 |
|---|---|
| RT049-B1 / wrong alternative class | **The object of this batch** — discharged only by a valid run |
| RT049-CTRL-4 / KN-CAND-BATCH023-A route (a) | Artifact **specified** (`DIAG-DEP-DUP` → `duplicate_decomposition.json`, `dup_residual` pre-registered at 0). Running it **creates** the artifact; promotion is judged at the close |
| RANK 6 cheap repairs | **Discharged**: CTRL-DEP-S3 samples uniformly at random (not a prefix); `git_status_prerun.txt` archived; RT049-B5 gets its one cheap check (**rate measured, not explained**) |
| OPEN-BATCH023-B | **Second half repaired outright** (no branch keys on a ledger status; reviewer must verify at freeze). **First half mitigated only** — the one-owner rule in `research_dispatch.py` blocks committing a transition at its gate; pre-declared retrospective entries instead. **Stays open on that half.** |
| OPEN-BATCH022-A | **Mitigated, not repaired** — `manifest.yaml` + five companions used; the indexing defect stands |
| OPEN-BATCH022-B | **Mitigated, not fixed** — ids re-checked free; mandatory freshness re-check at the close |
| **OPEN-BATCH023-A** (smoothness) | **NOT DISCHARGED.** No experiment in this campaign has yet factored an integer and **this one will not either**. Ranked first behind the single action |
| **RT049-B6** (determinism vs small-x window) | **NOT ATTACKED.** Its arm is RT049-CTRL-2, not run here |
| **RT049-CTRL-5** (real replication) | **NOT RUN**, and deliberately excluded by the same-instance design |
| **RT049-CTRL-3** (finer *e_1-delta* ladder) | **NOT RUN** — R_REPS = 200 here is on *dependence* ladders; the e_1-class resolution stays coarse by ≈ 4× |
| **OPEN-BATCH024-A** (new) | Supersession is discoverable only forward; EV-EQD-001 gains no back-pointer. **Filed, not repaired** |

## 8. Claim ceiling and standing caveats

Toy tier only (16 and 20 bits). No crypto-scale, medium-scale, asymptotic or
affected-scheme claim under any branch. No `support` for H-DEP-001, H-EQD-001,
H-SMTH-001, H-DS-001 or HEUR-DS-1. **HEUR-DS-1 is neither validated nor refuted
at any tier** — this batch is *one step further removed* from it than BATCH-023
was, because it characterizes the instrument rather than the input. No
`reject_scoped`, no `reject_scoped`-as-impossibility, no S1_met/F1_met/F2_met/
structure_gate_passed, `dominated_by` may not be null, gates **G1–G4 remain
OPEN**. Equally forbidden: calling BATCH-023 or this batch vacuous, which is
premature closure under `docs/inventor-protocol.md` §4.

**Model independence:** every session here resolves to claude-opus-5.
Independence is **procedural**, not model-level; `model_verified` is false
everywhere; **nothing in BATCH-024 is admissible toward the AGENTS.md rule 13
three-model closure quorum.**

## 9. Declared ids

`EXP-DEP-001`, `H-DEP-001`, `DEC-20260801-009` (open), `DEC-20260801-010`
(close), `EV-DEP-001`, `EV-EQD-002`, `TASK-20260801-033`–`046`. All verified free
in the current tree immediately before writing; the close ids carry a
**mandatory freshness re-check** at TASK-20260801-046 under OPEN-BATCH022-B —
renumber **our** record, never the other party's.
