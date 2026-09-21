# BATCH-026 OPENING — RR-LPF-2: REPAIR THE READING, THEN MEASURE

**Goal:** GOAL-ECDLP-001 · **Sub-goal:** SG-ECDLP-001 · **Question:** RQ-ECDLP-002
**Opened by:** DEC-20260801-011 (2026-08-01), which in the same record **closes
BATCH-025 as a one-cycle NON-EXECUTION** for the measurement arm.
**Queue:** `coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/dispatch_queue.json`
**Tasks:** TASK-20260801-061 … TASK-20260801-074 · **max_concurrent:** 3
**Goal status:** `active`. BATCH-026 is the **twenty-sixth** batch against
`campaign_budget.maximum_batches = 50`, so **no pause condition fires** — stated
explicitly rather than left implicit.

---

## 1. BATCH-025 is closed as a non-execution, and no evidence record is filed

`RUN-LPF-001-measure` **was not executed**. TASK-20260801-054 returned **REVISE**
with a `DO_NOT_APPROVE` recommendation; TASK-20260801-055 recorded
**APPROVAL_DETERMINATION: NOT APPROVED**. Under the RC-25 one-cycle cap that ends
the measurement arm. TASK-20260801-056 through TASK-20260801-060 are terminal
`blocked`.

**No evidence record exists because no measurement run exists.** EV-LPF-001 was
never written and its id remains free. **H-LPF-001 remains `specified`.** The
close is recorded by goal-record amendment at this batch's opening — the
BATCH-014/015, BATCH-022/023 and BATCH-024/025 precedent.

**The cap was enforced against convenience, and that is the part that cost
something.** The reviewer stated in terms that the repair **needs no
re-execution** and that the calibration package **remains ADMISSIBLE**. The cap
fired anyway. Accepting a REVISE as approvable because the fix looks cheap is
exactly the latitude the cap exists to remove.

### The blocking defect

**RTB-054-1.** `certification.certified_ladders.moving_rungs` in RR-LPF-1
certifies **two rungs with no recorded movement**:

| ladder | cell | frozen | recomputed | shift at the disputed rung | flag |
|---|---|---|---|---|---|
| ROUGH / `STAT-RATE-u@u_target=2` | 16 | [**0.005**, 0.01, 0.02, 0.05] | [0.01, 0.02, 0.05] | −0.882122 | `False` |
| ROUGH / `STAT-KS-DICK` | 16 | [**0.01**, 0.02, 0.05] | [0.02, 0.05] | −0.937958 | `False` |

Both are `False` under the sd reading, under the auxiliary range reading **and**
under DET-LPF-1 at 1/20. PERTURB-MOVE-1's named reviewer duty states the
consequence verbatim — *"a rung with no recorded movement that the reading rule
nevertheless certifies, is a REVISE"*. Both overstatements are in the **rough**
direction, which the file itself flags as the weaker one, and they claim power at
a γ an octave below where any movement was recorded.

A third entry errs the other way and is non-blocking (**RTB-054-3**):
SMOOTH / `u_target=3` / bits 20 omits γ = 0.001 at shift +1.572416, flag `True`.
**A mechanical regeneration repairs it too, in the same operation and by the same
rule.** That is the point of a mechanical regeneration.

**This is a transcription failure, not a measurement failure.** The archived
table is correct — the validator recomputed all 210 rows at maximum discrepancy
exactly **0.0** with zero misreported rows. The frozen *summary* of it is not.

---

## 2. Two corrections that must travel into the repair

### RTB-054-2 — the D1 structural argument is materially false as written

- **The rough half is genuinely structural and is confirmed from source.**
  `r ≤ v//q ≤ p²/q < p < q` forces `P_max = q` exactly, so `Z = 1 + ln r/ln q < 2`
  **unconditionally**. No sampling is involved.
- **The smooth half is not structural at all.** `Z = ln m / ln(max drawn prime)` is
  a **random variable** bounded only by about 32.
- **The quoted numbers do not reproduce.** D1 claims a maximum planted `Z` of
  4.957 / 4.643 over "all 6541 planted values". The top rung carries **130 820**
  plants per cell, and the regenerated maxima over the top-rung replicates are
  **5.936051910051658** and **6.031412202025096**. The quoted quantity matches no
  set the reviewer could construct, and **the per-sample `Z` arrays are not in the
  calibration package**, so it is not checkable against the archive at all.
- **The universal claim is falsified by the pipeline's own output.** At bits 20,
  γ = 0.05, replicate 0 a plant has `Z = 6.0314 > 5.7624`, and `all_statistics`
  returns plant `T_deep = 5.824044507159416` against null `5.762382565494627` —
  **the plant moved `T_deep` UP**. "Raising γ cannot change this" is also false;
  insertions scale **linearly** in γ.
- **The true statement** is a **measured near-disjointness** with an
  **eviction-to-insertion ratio of about 10:1 at γ ≤ 0.05**, from a per-plant
  exceedance rate of about 7.6 × 10⁻⁶.

**STRIKE-1 itself stands** on the measured 0/28 flags at maximum |shift|
0.3379820826156079 null sd. **What fails is the reason** — and the reason is
load-bearing, because CERT-LPF-1 forbids reporting the inertness as "low power"
and D1 was the only thing distinguishing the two. **STRIKE-2 is sound and the
reviewer strengthened it.**

### RTB-054-6 — the undeclared LIMB B limit

Recomputing `u` against the **actual sample range** moves bits-16 `u = 6` from
`R = 11.5937` (outside the band) to **`R = 6.68` (inside it)**, so **the sole
non-decidable rung is largely a definitional artifact** of `u` being defined at
`D` while samples live on `[1, p²]` with `p²/D = 0.5070` and `0.5358`.

**LIMB B is not a symmetric 8× test.** Because the uniform arm already sits at
4.571 of an 8.0 ceiling at bits 16 `u = 5`, the real arm needs to be only about
**1.75× smoother** to exit the band there. Both facts are **undeclared in
RR-LPF-1** and must travel with any LIMB B reading.

**Neither the `[1/8, 8]` band nor the `u_star_formula` may move.** Both are
hash-bound pre-datum. RR-LPF-2 **adds a declaration and changes no number.**

---

## 3. What survives and is reused — do not rebuild any of it

- **The calibration package.** `RUN-LPF-001-calib` at snapshot
  `104d32faff09207740f980be3c7dc8faa3642110` is **ADMISSIBLE** — 68 950 136
  factorizations at verified fraction **1.0**, 13 600 independently re-factored by
  a second code path with zero disagreements, all 210 movement rows reproducing at
  max discrepancy **exactly 0.0**, and a full from-scratch re-execution reproducing
  every result file identically. **The measurement arm does not need a new
  calibration.**
- **The driver.** `DRIVER_SHA256 = 786aeb0550d75fa3d0785aefbe50b121a24cacae584a4cadd79902c464722d65`,
  unmodified, six-way agreement across manifest, environment, command, execution
  report, receipt and HEAD.
- **OPEN-RR052-A is ruled.** The `STAT-TAIL-DEEP` strike **stands**, on textual
  grounds the reviewer would have given in both counterfactuals. **L-1 does not
  pre-fire; L-2, L-3 and L-4 are reachable.**
- **Attainability passes.** Every frozen probability reproduces exactly, and the
  favourable branch **could have failed** at 15–18 %.
- **Anti-tuning passes on every mechanical check.** Ancestry confirmed; the tree
  at the contract freeze holds **only** `specification.yaml`; 28/28 band edges and
  28/28 spreads recompute exactly; 12/12 branch strings whitespace-identical in the
  same order.
- **The D9 whole-ladder strike is ruled right, not overcautious.**

---

## 4. BATCH-025 is **not** a sixth instance of PATTERN-INSTR-5

**The count does not move and is not inflated.** PATTERN-INSTR-5's defect class is
*an instrument that cannot measure what it claims*. **The BATCH-025 apparatus
can.** Duties 1 and 2 passed on an executed audit; the certifying set is non-empty
at five statistic ids; no branch is unreachable by construction; both perturbation
families were re-derived from source and confirmed not invariant in law.

> *"THE APPARATUS ITSELF IS THE FIRST IN THIS CAMPAIGN THAT SURVIVED AN EXECUTED
> ATTAINABILITY AND MOVEMENT AUDIT WITH ITS CERTIFYING SET NON-EMPTY, ITS
> FAVOURABLE BRANCH FALSIFIABLE AT ABOUT 15 PERCENT ON A CORRECT NULL, AND NO
> BRANCH UNREACHABLE BY CONSTRUCTION."* — TASK-20260801-054

The new defect class is **a correct instrument with an overstated reading of its
own calibration**. Naming it as new rather than folding it into the old one is the
honest move. PATTERN-INSTR-5 stands at **four instruments across five batches with
five distinct defect classes**, exactly as DEC-20260801-010 recorded.

---

## 5. The ruling: a superseding reading rule, not a new experiment id

**RR-LPF-2, under the unchanged experiment EXP-LPF-001, in a new file
`experiments/EXP-LPF-001/reading_rule_v2.yaml`.**

When EXP-LPF-001 superseded EXP-SMTH-001, a new experiment id was held
**mandatory**, because that experiment's fatal defect (TAIL-DS-1) lived **inside
its frozen specification**, where repairing it would have destroyed the only thing
a freeze is for. **That condition is absent here, and the absence was
independently verified.** The specification's sha256 is unchanged; all twelve
branch strings are whitespace-identical; all 28 band edges and spreads recompute
exactly. **Not one reviewer finding names a defect in the specification.** Both
blocking defects and the RTB-054-6 omission are located in RR-LPF-1 — the
*substitution instrument*, whose whole function is to carry measured numbers into
forms the specification already fixed. **An error in a substitution is repaired by
re-performing the substitution correctly under a new id.**

**Immutability is satisfied.** RR-LPF-1 is not edited, moved, deleted or
re-hashed; it stays at `experiments/EXP-LPF-001/reading_rule.yaml` with sha256
`8bcb196f…c979f1d` at commit `1026150f…892fd7`, and its TASK-20260801-053 receipt
stands. RR-LPF-2 is a new record under a new id in a new file that cites
RR-LPF-1's hash and states exactly what it takes over and what it changes.

**A new EXP id would be positively harmful here.** It would orphan an ADMISSIBLE
68 950 136-factorization calibration and a hash-bound driver from their contract,
forcing either a pointless re-execution or a cross-experiment citation. More
sharply, **ATS-LPF-1's guarantee *is* the ancestry `ba1567ee → 104d32fa →
1026150f`**, and that chain is checkable only while the specification remains the
same record.

---

## 6. The four-change cap — the anti-tuning control of this batch

RR-LPF-2 is authored **after** an independent review of the measured numbers, so
ATS-LPF-1 clause 4 latitude is at its **maximum**. It may change **exactly four
things**:

| | change |
|---|---|
| **(a)** | `moving_rungs` **regenerated mechanically** from `LPF_movement_beyond_noise_flag`, with the generating operation **written into the file** |
| **(b)** | D1 restated — structural for ROUGH only, **measured** near-disjointness for SMOOTH, γ-scope narrowed |
| **(c)** | V8 restated to match, without weakening its operative content |
| **(d)** | the RTB-054-6 LIMB B declaration **added** |

**Everything else is copied** — every band edge, every spread, every branch string,
the cut 4, `[0.125, 8.0]`, both ladders, both `Bsm` ladders, the retained and
struck sets, both strikes, the D9 strike, the decidability map, every probability,
and every OPEN-RR052 and OPEN-LPF049-A ruling **as ruled**.

**Any fifth change is a REVISE whatever its merit**, including one that improves
the file. TASK-20260801-068 carries a dedicated **diff duty** to find one.

---

## 7. Two new disciplines, both discharged inside this batch

- **MECH-GEN-1** — *a derived summary of a machine-readable table may not be
  written by hand into a frozen record.* The direct lesson of RTB-054-1.
- **PERTURB-TAIL-1** — *no sentence of a reading rule may rest on a number that is
  not in an archived machine-readable array.* The direct lesson of RTB-054-2, and
  the reason TASK-20260801-063 (regeneration) and TASK-20260801-065 (validation)
  **precede** TASK-20260801-066 (authoring). Restating an unarchived number with
  another unarchived number would repeat the defect exactly.

The regeneration touches **no real object** and modifies **no hash-bound file** —
a separate auxiliary script imports the driver unmodified, asserts its sha256,
calls only the construction and statistic functions, and asserts the tripwire
false at exit. **It requires no factorization** and runs in seconds.

---

## 8. The five disciplines, carried — and two of them re-run

ATTAINABILITY · ANTI-TUNING (ATS-LPF-1) · DECISION-VARIABLE VARIATION
(DECAY-LPF-1) · ALTERNATIVE-CLASS DECLARATION (ALT-CLASS-LPF-1) ·
PERTURBATION MOVEMENT (PERTURB-MOVE-1).

**The attainability and movement duties are re-run from scratch against RR-LPF-2,
not inherited.** A regenerated `moving_rungs` **changes what is certified**, and
what is certified feeds the L-1 stop condition, the S1/S2 certified sets and every
per-rung power statement. Inheriting the BATCH-025 verdict because "only three
entries changed" is exactly the reasoning the cap exists to refuse.

---

## 9. Carried forward, each with its status

| item | status |
|---|---|
| **OPEN-BATCH023-A** | **Survives intact.** Still the single next action, unpaid across 25 batches. |
| OPEN-BATCH022-A | mitigated, not repaired — all three runs use `manifest.yaml` + five `.log`/`.json` companions |
| OPEN-BATCH022-B | mitigated, not fixed — ids re-checked free; mandatory re-check at TASK-20260801-074 |
| OPEN-BATCH023-B | second half repaired and re-verified; first half mitigated only |
| OPEN-BATCH024-A | **second and sharper instance** — RR-LPF-2 supersedes RR-LPF-1 in the same directory; partial mitigation is to **quote every superseded sentence** beside its replacement |
| OPEN-LPF049-A | ruled non-decisional (identity cut 4, zero margin recorded); binding carried |
| OPEN-RR052-B / C / D | all ruled; carried into RR-LPF-2 unchanged, D with its extension |
| ANOM-LPF052-1 | confirmed; D9 handling ruled correct; signed-(D⁺,D⁻) reporting ranked, not done |
| RT049-B6 | open, not attacked; carried as V7; sharpened — the base measured **is** the small-x window |
| KN-CAND-BATCH023-A | still withheld; route (a) undischarged, route (b) cheaper |
| KN-CAND-BATCH024-A | still withheld; **first partial negative case** now exists |
| **OPEN-BATCH026-A / B** | **new** — the derived-summary generation gap and the unarchived-claim gap; instances repaired, general cases open |

**The standing model-independence caveat applies unchanged** — every session
resolves to `claude-opus-5`, independence is **procedural and not model-level**,
`model_verified` is false everywhere, and **nothing here is admissible toward the
AGENTS.md rule 13 three-model closure quorum**.

---

## 10. Ceiling

**Toy tier only** — 16 and 20 bits, `D = 2³²` and `2⁴⁰`. No `support` for any
hypothesis under any branch. No HEUR-DS-1 validation above toy tier in either
direction. No `reject_scoped`, and in particular none as impossibility, on a
single unreplicated run. `dominated_by` may not be null. **Promotion gates G1–G4
all remain OPEN.** No exponent moves in either direction.
