# BATCH-156658 scope decision — GOAL-ECDLP-001 — **DECLINED (mis-bound goal; routed, not closed)**

Candidate: `ledger/proposals/IDEA-20260803-fa9839.yaml` — "the arity threshold:
charged cost model for point-decomposition index calculus vs rho".

**Disposition: DECLINE under GOAL-ECDLP-001.** BATCH-156658 is **not opened**. No
producer, review, or archive task is dispatched. No `batch.yaml`, no
`dispatch_queue.json`, no task card, and no handoff record is written under this batch
identifier. This file is the whole of the batch.

**This is a routing decline, not a merit decline.** I concur with
`analysis/SSI-ECDLP-SYNTHESIS-20260803.md` §4 that this is the highest-value
zero-compute item in the current portfolio. It is declined **here** because it belongs
to `GOAL-ICEX-001`, and binding it to `GOAL-ECDLP-001` would launder another goal's
committed deferral under this goal's banner while stripping the mandatory read that
goal attaches to exactly this parameter family. §5 records four substantive defects
found in the proposal, which any batch that does run it must repair.

---

## 1. The routing question, answered directly

**Q: Is a zero-compute cost model in scope for GOAL-ECDLP-001's objective, or does it
belong to GOAL-ICEX-001?**

**It belongs to GOAL-ICEX-001.** Four independent grounds, each checkable:

**(a) The proposal binds itself there.** `IDEA-20260803-fa9839.question_id` is
`RQ-ICEX-001`. `GOAL-ECDLP-001.question_ids` is `[RQ-ECDLP-002]` — `RQ-ICEX-001` is not
among them. `GOAL-ICEX-001.question_ids` is `[RQ-ICEX-001, RQ-ECDLP-002]`. The idea
generator routed it to ICEX; nothing in the record contradicts that.

**(b) The objectives match on ICEX and mismatch on ECDLP.** `GOAL-ICEX-001.objective`:

> Aggregate admissible G4-G6 outputs into one fully charged toy-scale index-calculus
> versus Pollard rho/BSGS exponent comparison for generic prime-field ECDLP, with
> certificates and independent review.

That *is* this proposal's deliverable. By contrast `GOAL-ECDLP-001.objective` sets an
explicit admission bar:

> Every candidate must include complete preprocessing, relation collection, linear
> algebra, target descent, verification, memory, and multi-target accounting against
> Pollard rho and BSGS.

`IDEA-20260803-fa9839` fails that bar **by its own text**: `confounders[0]` — *"THE
MODEL OMITS DESCENT"*; `assumptions[1]` — relation rank is not modelled; no
multi-target accounting appears anywhere; and `assumptions[2]` charges rho only
(`c_rho*sqrt(N)`, plain and negation-map), with no BSGS row. It charges relation
collection, linear algebra, and memory, and omits four of the seven required stages.

**(c) The proposal states the binding itself.** `dependencies[2]`: *"Feeds
GOAL-ICEX-001 directly and reduces its required measurement surface; ranks
GOAL-SDEG-001, GOAL-DREG-001 and GOAL-SIG-001 without consuming any of their budget."*
Its `predictions[deferred_measurement_ranking]` deliverable is a per-goal
threshold-convertibility statement for SDEG/DREG/SIG. That is ICEX/PATH portfolio work
end to end.

**(d) Mis-binding would strip a mandatory read.** `GOAL-ICEX-001.next_action` carries an
explicit gate:

> ONE MANDATORY READ IS ADDED: BEFORE CONSUMING ANY MONO FEED, READ DEC-20260802-a51c82.
> [...] Do NOT use `chebotarev_S2_split * (W_eff/p)^2`: on the factor-base locus the
> m=3 summation fibre splits with probability EXACTLY 1, not freq_split, so the
> correction factor is `(1 - 1/W_eff)/freq_split -> 2*(1 - 1/W_eff)`. USE THE FORMULA,
> NOT THE NUMBER [...] a per-fibre factor of 2 compounds as `2^{n-1}` in a
> Gaudry/Diem-style decomposition over `F_{q^n}` with n growing, where it would [move
> an exponent].

That gate binds precisely the parameter family this proposal uses for its
baseline-reproduction gate (`N = q^n, m = n`, subfield-line factor base). Running the
proposal under `GOAL-ECDLP-001` would run it outside the gate. §5.1 shows this is not a
formality — it collides directly with the proposal's headline point prediction.

**On ICEX's non-executing status.** `GOAL-ICEX-001.next_action` says *"remain
non-executing until charged SDEG/MONO/RELN measurement packages exist"* and *"NO ICEX
MEASUREMENT AUTHORIZED"*. That deferral is on **measurement**. A zero-compute analytic
derivation is not a measurement, so the deferral does not obviously bar this proposal.
But that reading is **GOAL-ICEX-001's Coordinator's call to make, on its own record,
preserving its own single next action** — it is not mine, and it is certainly not
mine to pre-empt by running the work under a different goal. That is the exact
"mis-binding" the dispatching session warned against, and I decline it.

**A structural reason this cannot be finessed.** `GOAL-ECDLP-001` carries exactly one
committed `next_action` — the successor Executor batch on frozen
`PA-IT-001-v3-rc45-repair-5` after `DEC-20260803-004 / EV-IT-008` — with
`current_batch_id: BATCH-046` and `dispatch_queue_path` pointing at BATCH-046. I am
forbidden from editing that goal record in this task. Opening BATCH-156658 under
GOAL-ECDLP-001 would therefore leave an unreferenced second active batch beside an
unchanged single next action: a checkpoint inconsistency that `agents/coordinator.md`
("preserve exactly one next action") exists to prevent, discovered at the next ledger
archive when neither batch could be checkpointed coherently.

## 2. What is explicitly **not** decided here

- **Not a merit decline.** The idea is well-posed, cheap, falsifiable against an
  externally known answer, and its core algebra is correct (verified in §4). Under
  AGENTS.md rule 9 and `docs/inventor-protocol.md` §4, refusing to pursue it would be
  premature closure. It is routed, not shelved.
- **Nothing about the EXP-IT-001 lane.** `GOAL-ECDLP-001`'s recorded `next_action` —
  the successor Executor batch under frozen `PA-IT-001-v3-rc45-repair-5` exercising
  live `CTRL-ANOMALOUS-TRACE1` and `CTRL_NULL_IT_PLANT` controls — is untouched, not
  reprioritized, and not delayed by this decline. No path under
  `experiments/EXP-IT-001/**` is read, written, or claimed by this file.
- **No hypothesis, evidence, decision, or goal record is edited.** `H-IT-001` remains
  `specified`. `KN-OPEN-001` remains open in both directions.

## 3. Claim ceiling (binding on anything that cites this file)

`toy` / `control`. No breakthrough, closure, novelty, SOTA, or completion claim is
authorized. Pollard rho remains the ECDLP baseline and ordinary `sota_delta` is zero.
The proposal's own `interpretation_limits` are adopted verbatim as the ceiling for any
successor: *"THIS CANNOT ESTABLISH THAT PRIME-FIELD INDEX CALCULUS FAILS, AND IT CANNOT
ESTABLISH THAT IT SUCCEEDS"*, and *"'No admissible D_trial within this model' must
NEVER be written as 'm <= 3 is impossible'."*

## 4. Core algebra: independently re-derived, correct

Recorded so the successor does not re-litigate it, and because a routing decline must
not be mistaken for a doubt about the mathematics.

With `T(m,B,D) = m! N D / B^(m-1) + c_LA B^2`:
`dT/dB = 0` gives `2 c_LA B^(m+1) = (m-1) m! N D`, hence
`B* = [(m-1) m! N D / (2 c_LA)]^(1/(m+1))` — matches. Substituting,
`m! N D = 2 c_LA B*^(m+1)/(m-1)`, so the first term is `2 c_LA B*^2/(m-1)` and
`T* = c_LA B*^2 (m+1)/(m-1) = Theta((m! N D)^(2/(m+1)))` — matches. With `D = N^d`,
`T* < N^(1/2)` iff `(2/(m+1))(1+d) < 1/2` iff `d < (m-3)/4` — matches, and `m <= 3`
admits no `D_trial >= 1`, as claimed. The discrepancy identity also checks:
`2n/(n+1) - (2 - 2/n) = (2n^2 - (2n-2)(n+1))/(n(n+1)) = 2/(n(n+1))` exactly.

## 5. Four defects found, which a successor batch must repair

**5.1 The baseline gate is stated without the correction its own goal makes mandatory.**
The model's relation-search term is `m! N D / B^(m-1)` with no per-fibre factor. At the
baseline instantiation `N = q^n, m = n` — the exact family where
`GOAL-ICEX-001.next_action` and `EV-MONO-a0a89c` say a per-fibre factor of `2` compounds
as `2^{n-1} = q^{Theta(1)}` and **would move an exponent** — the omission is not
second-order. The pre-registered point prediction "discrepancy is exactly `2/(n(n+1))`
at every n" could be confirmed or refuted for a reason the model never accounted for,
which would make the gate uninformative in both directions. The successor must either
carry the `2(1 - 1/W_eff)` correction explicitly through the baseline instantiation, or
state in writing why it does not apply and treat that statement as a reviewable claim.
`KN-FIND-c41ea9` flags the same clause as "either a real lever or a double count
against the `1/n!` conservation mean", untested.

**5.2 `B* = N^(1/(m+1))` is false wherever the threshold is non-trivial.** The
prediction `model_optimizer_exponent` asserts *"`B* = N^(1/(m+1))` exactly [...]
verified symbolically against the stationarity condition and numerically at m = 2..8 to
1e-12."* From §4, `B* ~ N^((1+d)/(m+1))`. It equals `N^(1/(m+1))` only at `d = 0`. The
headline threshold `d < (m-3)/4` is non-trivial precisely for `d > 0`. So the
proposal's own symbolic-verification prediction is false on the operating region its
headline result is about; as written it would fail its own `F3` ("the optimizer or T*
does not verify symbolically: algebra error, everything downstream is void"). Repair:
state `B* = N^((1+d)/(m+1))` and reserve `N^(1/(m+1))` for the `D_trial = N^{o(1)}`
baseline row only.

**5.3 The memory row understates memory at the operating point, by 2^21 at the
headline cell.** `target_complexity.memory_exponent` reports *"`B* = N^(1/(m+1))`
elements at the optimum [...] At m = 5 and N = 2^256 that is `2^(256/6) ~ 2^42.7`
stored elements."* By 5.2 that is the `d = 0` row. At `m = 5` the threshold is
`d < 1/2`; at `d = 1/2`, `B* = N^(1.5/6) = N^(1/4) = 2^64` elements. The proposal is
right that memory must travel beside every time row (`docs/target-result-profile.md`
requires exactly that); the row as written quotes the wrong one. Every threshold row
must carry `B*(m, d)`, not `B*(m, 0)`.

**5.4 The blocking gate is expected UNRUN, which collapses the deliverable — and this
must be pre-registered, not discovered.** `novelty_screen.literature_unverified[0]`
records that primary sources are unreachable from this environment and that the
`2 - 2/n` recollection *"MAY NOT BE USED AS EVIDENCE"*; `minimal_test.design` step (4)
requires STOP-and-report-UNRUN under AGENTS.md rule 5 if no primary source can be
obtained; step (6) emits the threshold table *"Only if (5) passes"*. The honest prior is
therefore that the batch emits **only** the symbolic optimizer verification and the
`1/n!` internal cross-check, and emits **no** threshold table, **no** `d_max(m)` rows,
**no** deferred-measurement ranking, and **no** `m <= 3 INFEASIBLE-WITHIN-MODEL`
reading — all four being downstream of step (6). A successor task card must
pre-register UNRUN as the expected outcome and forbid emitting any step-(6) artifact
under it, so that an unrun gate cannot be quietly converted into a passed one after
the outcome is observed. That failure pattern is the one `EV-IC-002` records for this
exact lane (a success criterion revised after the prior criterion was seen to fail),
and the proposal cites it as the thing it exists to avoid.

## 6. Rule-9 record

**Evidence cited.** `ledger/proposals/IDEA-20260803-fa9839.yaml`;
`ledger/goals/GOAL-ECDLP-001/goal.yaml` (`objective`, `question_ids`,
`current_batch_id: BATCH-046`, `next_action`); `ledger/goals/GOAL-ICEX-001.yaml`
(`objective`, `question_ids`, `next_action` mandatory-read clause,
`completion_criteria`); `analysis/SSI-ECDLP-SYNTHESIS-20260803.md` §§1.1, 1.2, 4;
`knowledge/findings/KN-FIND-007.md`; `ledger/evidence/EV-IC-002.yaml`;
`knowledge/open-problems/KN-OPEN-001.md`; `docs/target-result-profile.md`.

**Budget.** Zero consumed. No Executor, Validator, or Red Team session dispatched.

**Test boundary.** Scoped to the **binding of IDEA-20260803-fa9839 to GOAL-ECDLP-001**.
It decides nothing about the model's correctness (§4 finds the core algebra sound),
nothing about `KN-OPEN-001`, nothing about whether prime-field index calculus can beat
rho, and nothing about any deployed curve.

**Ranking against the alternatives not picked** (rule 9 requires the comparison):

1. **(chosen) Decline under GOAL-ECDLP-001; route to GOAL-ICEX-001 with the four
   defects attached.** Preserves ECDLP's single next action, keeps ICEX's mandatory
   read binding, and delivers §5 to whoever runs it — which is most of the value the
   batch would have produced anyway, at zero budget.
2. **Open BATCH-156658 under GOAL-ECDLP-001 anyway.** Ranked second. It would get the
   work done sooner, and the work is worth doing. Rejected because it fails
   GOAL-ECDLP-001's own candidate admission bar on four of seven required stages (§1b),
   binds `RQ-ICEX-001` to a goal that does not carry it (§1a), strips the
   `DEC-20260802-a51c82` mandatory read at exactly the parameter family where
   `EV-MONO-a0a89c` says it moves an exponent (§1d, §5.1), and would leave the goal with
   an unreferenced second active batch beside an unchanged single next action (§1,
   closing paragraph).
3. **Decline outright on merit.** Ranked last and rejected. The synthesis ranks this the
   highest-value zero-compute item in the portfolio, §4 confirms the algebra, and
   `docs/inventor-protocol.md` treats declining to search a target that looks
   unpromising as a failure mode symmetric with overclaiming. Nothing here supports
   closure.

**Remaining uncertainty.**

- Whether `GOAL-ICEX-001`'s Coordinator will read its own `next_action` deferral
  ("remain non-executing until charged SDEG/MONO/RELN measurement packages exist") as
  permitting a zero-compute analytic batch. I judge it does — the deferral is on
  measurement — but that call is not mine and I have not made it.
- Whether the `2(1 - 1/W_eff)` per-fibre correction (§5.1) belongs in the baseline
  instantiation, and whether it double-counts against the `1/n!` conservation mean.
  Unadjudicated in the corpus (`KN-FIND-c41ea9`; proposal `IDEA-20260803-ff7415`).
- Whether any primary source for the extension-field exponent is obtainable from any
  environment this programme can reach. If not, the `2 - 2/n` value stays an unverified
  recollection permanently and the baseline gate stays UNRUN permanently — which caps
  the proposal at its two internal checks indefinitely, not merely once (§5.4).

**Concrete successor.** Re-file `IDEA-20260803-fa9839` for adjudication by
`GOAL-ICEX-001` (or its parent `GOAL-PATH-001`, `GOAL-ICEX-001.parent_goal_id`) as a
**zero-compute, non-measuring analytic batch**, carrying §5.1–§5.4 as mandatory task-card
repairs and `GOAL-ICEX-001.next_action`'s `DEC-20260802-a51c82` read as a hard
precondition. That Coordinator, not this one, decides whether ICEX's deferral admits
it, and does so on ICEX's own record preserving ICEX's own single next action.

**Revisit condition for a GOAL-ECDLP-001 binding specifically.** Reconsider binding
this work to `GOAL-ECDLP-001` only if **either**:

- (R-C) `GOAL-ECDLP-001.question_ids` is amended to include `RQ-ICEX-001` by a committed
  Coordinator decision on that goal's record; or
- (R-D) the proposal is extended to meet `GOAL-ECDLP-001.objective`'s admission bar —
  charged descent, relation rank, verification, multi-target accounting, and a BSGS row
  beside the rho row — at which point it is a different and much larger proposal and
  needs its own `IDEA-*` record.

## 7. Identifier and archival hygiene

**Unconsumed identifiers.** The following were pre-allocated to this batch and are
**consumed by no record**. No `TASK-*` handoff, task card, or queue entry exists for
any of them:

`TASK-20260805-7d8509`, `TASK-20260805-fbd6a6`, `TASK-20260805-dca2b0`,
`TASK-20260805-3c5f4a`, `TASK-20260805-71f5a4`.

Per AGENTS.md rule 14 identifiers are never reused. The `GOAL-ICEX-001` successor
should mint its own with `python3 tools/allocate_id.py --next task --date <YYYYMMDD>`
and `--check` before use rather than adopting these — they were drawn against a
`GOAL-ECDLP-001 / BATCH-156658` intent that this record declines.

**Goal records untouched.** Neither `ledger/goals/GOAL-ECDLP-001/goal.yaml` nor
`ledger/goals/GOAL-ICEX-001.yaml` is edited by this task, by explicit constraint.
GOAL-ECDLP-001 keeps `current_batch_id: BATCH-046`, keeps
`dispatch_queue_path: coordination/goals/GOAL-ECDLP-001/batches/BATCH-046/dispatch_queue.json`,
and keeps its single `next_action` (the frozen `PA-IT-001-v3-rc45-repair-5` successor
Executor batch) unchanged. This decline creates no second next action and delays that
batch by nothing.

**Archival ownership of this file.** This file is a coordination record, not evidence.
It is staged by the launching session as ordinary batch-scoping scaffolding; it carries
no archive receipt and asserts no commit. Its promotion to a
`ledger/decisions/DEC-20260805-bb162b.yaml` record — with a token minted by
`tools/allocate_id.py --next decision --date 20260805` and `--check`ed, which this
session cannot do (no shell) and must not fabricate — is **owed to the next ledger
archive of whichever goal adopts the successor**. Until then this decision is durable as
a reviewable coordination artifact and is **not** an official ledger transition.

---

```yaml
coordinator_decision:
  id: DEC-20260805-bb162b              # ledger/decisions/DEC-20260805-bb162b.yaml, owed to the
                                # next ledger archive of the adopting goal. Not minted
                                # here: this session has no shell, cannot run
                                # tools/allocate_id.py --check, and will not fabricate
                                # an identifier (AGENTS.md rules 5 and 14).
  recorded_at: '2026-08-05'
  decided_by: coordinator
  goal_id: GOAL-ECDLP-001
  question_id: RQ-ECDLP-002
  subject: IDEA-20260803-fa9839
  proposed_batch_id: BATCH-156658
  decision: pause
  disposition: decline_mis_bound_goal_route_to_GOAL-ICEX-001
  rationale: >-
    Routing decline, not a merit decline. IDEA-20260803-fa9839 carries
    question_id RQ-ICEX-001, which GOAL-ECDLP-001 does not list; GOAL-ICEX-001's
    objective ("one fully charged toy-scale index-calculus versus Pollard rho/BSGS
    exponent comparison for generic prime-field ECDLP") is verbatim this proposal's
    deliverable; and the proposal states it feeds GOAL-ICEX-001 and ranks
    SDEG/DREG/SIG. It also fails GOAL-ECDLP-001's own candidate admission bar, which
    requires complete descent, verification, multi-target, and BSGS accounting - four
    of seven stages the proposal explicitly omits. Decisively, GOAL-ICEX-001's
    next_action attaches a MANDATORY read (DEC-20260802-a51c82 / EV-MONO-a0a89c) whose
    2(1 - 1/W_eff) per-fibre correction compounds as 2^(n-1) over F_{q^n} at exactly
    the N = q^n, m = n family the proposal uses for its baseline-reproduction gate;
    running it under GOAL-ECDLP-001 would strip that read from the one place it bites.
    Finally, GOAL-ECDLP-001 carries exactly one committed next_action (the frozen
    PA-IT-001-v3-rc45-repair-5 successor Executor batch) and this task may not edit
    the goal record, so opening the batch here would leave an unreferenced second
    active batch beside an unchanged single next action. The core algebra was
    independently re-derived and is CORRECT; four substantive defects were found and
    are attached to the successor.
  evidence_refs:
  - ledger/proposals/IDEA-20260803-fa9839.yaml
  - ledger/goals/GOAL-ECDLP-001/goal.yaml
  - ledger/goals/GOAL-ICEX-001.yaml
  - analysis/SSI-ECDLP-SYNTHESIS-20260803.md
  - knowledge/findings/KN-FIND-007.md
  - ledger/evidence/EV-IC-002.yaml
  - knowledge/open-problems/KN-OPEN-001.md
  - docs/target-result-profile.md
  status_changes: []
  hypothesis_status_changes: []
  experiment_approvals: []
  claim_ceiling: toy_control
  knowledge_promotion:
    promoted: false
    not_warranted_reason: >-
      No evidence record was produced and no experiment ran. A routing decline is not
      replicated or strong evidence and promotes no KN-FIND. The four defects in
      section 5 are review findings attached to a successor task card, not a
      knowledge-corpus entry; they become promotable only if a run adjudicates them.
  dominated_by: >-
    Not applicable as an attack - no algorithm is proposed and no Pareto point is
    claimed. Written explicitly rather than left null.
  sota_delta: >-
    Zero on every ECDLP cost axis. Pollard rho remains the baseline; no attack, no
    measurement, no exponent moved.
  next_actions:
  - >-
    DO NOT open BATCH-156658 under GOAL-ECDLP-001. That goal's single next_action -
    the successor Executor batch under frozen PA-IT-001-v3-rc45-repair-5 with live
    CTRL-ANOMALOUS-TRACE1 and CTRL_NULL_IT_PLANT controls - is preserved unchanged,
    untouched, and undelayed by this decline.
  - >-
    Re-file IDEA-20260803-fa9839 for adjudication by GOAL-ICEX-001 (or parent
    GOAL-PATH-001) as a zero-compute, non-measuring analytic batch. That Coordinator
    decides whether ICEX's non-executing deferral, which is on MEASUREMENT, admits an
    analytic derivation - on ICEX's own record, preserving ICEX's own single next
    action.
  - >-
    Carry section 5 defects into the successor task card as mandatory repairs -
    (5.1) the 2(1 - 1/W_eff) per-fibre correction at the N = q^n baseline;
    (5.2) B* = N^((1+d)/(m+1)), not N^(1/(m+1)), wherever d > 0;
    (5.3) every threshold row carries B*(m, d) memory, not B*(m, 0);
    (5.4) pre-register the baseline gate as expected UNRUN and forbid every step-(6)
    artifact (threshold table, d_max rows, deferred-measurement ranking, m <= 3
    INFEASIBLE-WITHIN-MODEL reading) under an unrun gate.
  - >-
    Promote this decision to ledger/decisions/DEC-20260805-bb162b.yaml at the next
    ledger archive of the adopting goal, minting the token with tools/allocate_id.py
    and --check. Until then it is a coordination record and not an official
    transition.
  inference:
    requested_policy: coordinator-orchestration-code
    resolved_model_id: claude-opus-5
    reasoning_effort: null
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness cannot resolve the policy aliases in
      orchestration/model-policies.yaml; per-role policy selection under this runtime
      is process-level. Recorded, never silently substituted (AGENTS.md rule 11).
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: >-
      No adapter probe receipt exists for this session; no
      `python3 -m orchestration.adapter doctor --probe` was run.
```
