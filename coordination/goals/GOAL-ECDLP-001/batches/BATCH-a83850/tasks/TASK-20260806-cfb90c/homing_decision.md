# Homing decision — TASK-20260806-cfb90c

**Step zero, resolved before any specification work. No `experiments/EXP-ICEX-2f9337/`
directory has been created by this task.**

## (a) R-D's exact text

`DEC-20260805-bb162b` is the promoted-ledger form of
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-156658/SCOPE-DECISION.md`. The
ledger YAML (`ledger/decisions/DEC-20260805-bb162b.yaml`) states the decision,
rationale, and section-5 defect list but does not restate the two lettered revisit
conditions verbatim in its own body — they live in the source scope-decision
document it promotes, §"Revisit condition for a GOAL-ECDLP-001 binding
specifically" (lines 240–248), which is authoritative for R-D's text and is one of
the records this task's `read_scope` names. Verbatim:

> Reconsider binding this work to `GOAL-ECDLP-001` only if **either**:
> - (R-C) `GOAL-ECDLP-001.question_ids` is amended to include `RQ-ICEX-001` by a
>   committed Coordinator decision on that goal's record; or
> - (R-D) the proposal is extended to meet `GOAL-ECDLP-001.objective`'s admission
>   bar — charged descent, relation rank, verification, multi-target accounting,
>   and a BSGS row beside the rho row — **at which point it is a different and
>   much larger proposal and needs its own `IDEA-*` record.**

R-D therefore has **two conjunctive requirements**, not one:

1. **Cost-completeness**: charge descent, relation rank, verification,
   multi-target accounting, and a BSGS row (beside the existing rho row) —
   GOAL-ECDLP-001's own admission bar, verbatim in its `goal.yaml.objective`.
2. **A new `IDEA-*` record**: R-D's own text states that satisfying (1) makes the
   result "a different and much larger proposal," and that this "needs its own
   `IDEA-*` record" — i.e., satisfying R-D is not merely repairing
   `EXP-ICEX-146ff5` under its existing `source_proposal_id`, it requires a
   successor proposal record documenting the extended, larger object.

This reading is corroborated by the independent red-team review already on file
(`EV-ICEX-2be32e` / `red_team_report.md` F-14, §2 "R-D: NOT satisfied"), which
scored the rejected contract against R-D item-by-item: "descent ✔, verification
✔, multi-target ✔, BSGS row ✔, **relation rank ✘** (declared omitted, direction
stated), **own IDEA record ✘**." The reviewer independently reads R-D as two
clauses and finds both partially or wholly unmet — consistent with the parse
above, not a novel interpretation invented for this task.

## (b) Does a genuinely zero-compute redesign satisfy R-D?

**No, on R-D's own text — and the two requirements are orthogonal, not the same
thing.**

**Zero-compute addresses a different gate entirely.** "Zero declared runs, no
measured-mean arms" is what would let this work escape `GOAL-ICEX-001.next_action`'s
bar, which is explicitly a bar on *measurement* ("NO ICEX MEASUREMENT
AUTHORIZED... remain non-executing until charged SDEG/MONO/RELN measurement
packages exist" — re-read fresh from `ledger/goals/GOAL-ICEX-001.yaml` this task,
unchanged since `DEC-20260805-bb162b`/`DEC-20260806-8f7e4f`). Both the prior
red-team review and the SCOPE-DECISION document say this explicitly: "A genuine
zero-compute derivation is not barred by that text." That is a statement about
whether ICEX's *own* deferral would block the work if it were homed at ICEX. It
says nothing about R-D, which is a GOAL-ECDLP-001-specific admission condition
with its own, textually distinct, two-part test.

**R-D requirement 1 (cost-completeness) is compatible with zero-compute in
principle** — a charged cost model can in principle add closed-form terms for
relation rank (e.g. the reviewer's own suggested cheap discharge via the fixed
point of `x = 1 − e^{−mx}` from `IDEA-20260805-061f97`) without running anything.
So this half of R-D is not the blocker.

**R-D requirement 2 (a new `IDEA-*` record) is not satisfiable by this task,
structurally, regardless of compute.** Three independent reasons:

1. **Write-scope.** This task's `write_scope` is `coordination/goals/GOAL-ECDLP-001/batches/BATCH-a83850/tasks/TASK-20260806-cfb90c/`,
   `experiments/EXP-ICEX-2f9337/`, and `ledger/hypotheses/`. It does **not**
   include `ledger/proposals/`. I cannot mint the `IDEA-*` record R-D's own text
   requires without writing outside my declared scope.
2. **Role.** Minting a new proposal record is idea-generation, not
   specification. `agents/coordinator.md` / `AGENTS.md` bar the Coordinator from
   doing the idea-generator's work inline; that work must be dispatched via a
   handoff record and executed by the idea-generator role. A repaired
   `specification.yaml` that still names `source_proposal_id: IDEA-20260803-fa9839`
   (as `EXP-ICEX-146ff5` does) does not create the "different and much larger
   proposal" R-D contemplates — it is the same proposal with a cost-model patch,
   which is exactly the state the red team already scored as R-D-unmet (F-14).
3. **No such record already exists to point to instead.** I checked: no
   `IDEA-2026080[6-9]-*` record in the corpus documents an extended proposal
   charging all five GOAL-ECDLP-001 admission-bar terms as "a different and much
   larger proposal" superseding `IDEA-20260803-fa9839`. The five `IDEA-20260806-*`
   records already in the corpus (`3b91c7`, `7ea402`, `20f6ab`, `9d47e2`,
   `c5d183`) are the BATCH-9c41dd satellite proposals reviewed in
   `EV-ICEX-2be32e`, not an R-D-satisfying successor to `fa9839`.

So: making `EXP-ICEX-2f9337` zero-compute would repair the *third reason* the
prior contract was rejected (`DEC-20260806-8f7e4f`'s `third_reason`, "the contract
is NOT zero-compute") and would answer the ICEX-side measurement question. It
would **not** satisfy R-D, whose text requires a new proposal record this task
has neither the scope nor the role to produce. Treating "zero-compute" and
"R-D-satisfied" as the same condition — which the batch's own `objective` field
and this task's own `constraints` block both do ("a genuinely zero-compute
redesign... satisfies it... admits it under GOAL-ECDLP-001") — is the premise I
am rejecting here, on R-D's own text and on the independent red-team's own
reading of the same text, not on a new interpretation manufactured to produce a
stop.

## (c) Decision: STOP. Do not write `experiments/EXP-ICEX-2f9337/`.

R-D is not satisfiable within this task's scope. I am not proceeding to design a
successor contract under `GOAL-ECDLP-001`, and no file has been written under
`experiments/EXP-ICEX-2f9337/`.

**Recommended routing.** Route the repair to `GOAL-ICEX-001`, whose own
`next_action` (re-read fresh this task, `ledger/goals/GOAL-ICEX-001.yaml`,
`updated_at: 2026-07-31`) is unchanged since the prior decline: still
non-executing, still "NO ICEX MEASUREMENT AUTHORIZED," still carrying the
mandatory `DEC-20260802-a51c82` read before consuming any MONO feed at the
`N = q^n, m = n` family. That deferral is on measurement, and a genuinely
zero-compute derivation is arguably not barred by it — but, per
`DEC-20260805-bb162b`'s own routing argument and the prior red-team review, that
reading is `GOAL-ICEX-001`'s Coordinator's call to make on its own record, not
this task's to pre-empt.

**What would actually open a path back to GOAL-ECDLP-001 under R-D**, named for
whichever Coordinator next picks this up: dispatch an idea-generator handoff to
produce a new `IDEA-*` record that is honestly "a different and much larger
proposal" — charging descent, relation rank, verification, multi-target
accounting, and a BSGS row as first-class modeled terms rather than a patch to
`IDEA-20260803-fa9839` — and only then design a contract against that new
record. Alternatively, R-C (amending `GOAL-ECDLP-001.question_ids` to include
`RQ-ICEX-001` by a committed Coordinator decision) is the other disjunct in the
scope-decision's revisit condition and was not evaluated here because this task
was scoped to R-D only; a future task could weigh it, but amending a goal's
`question_ids` is itself an official goal-record transition this task does not
have write_scope for either (`ledger/goals/` is not in `write_scope`).

**No files were written except this one.** `repair_report.md` and
`experiments/EXP-ICEX-2f9337/specification.yaml` are NOT produced, per this
task's own instruction: "If you stop, do not write `experiments/EXP-ICEX-2f9337/`
at all — return with only `homing_decision.md` and say the routing question is
unresolved by design."

## Evidence read for this determination

- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-156658/SCOPE-DECISION.md`
  (source text of R-C/R-D, §"Revisit condition for a GOAL-ECDLP-001 binding
  specifically")
- `ledger/decisions/DEC-20260805-bb162b.yaml` (promoted ledger record; rationale,
  section-5 defects, disposition)
- `ledger/decisions/DEC-20260806-8f7e4f.yaml` (rejection of `EXP-ICEX-146ff5`;
  `routing_unresolved` block explicitly finds "revisit condition R-D NOT
  SATISFIED on its own text")
- `ledger/evidence/EV-ICEX-2be32e.yaml` and
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-9c41dd/reviews/TASK-20260806-7e7ce3/red_team_report.md`
  (independent red-team F-14 and §2, scoring R-D item-by-item and finding two
  clauses unmet)
- `ledger/goals/GOAL-ICEX-001.yaml` (current `next_action`, re-read fresh this
  task: unchanged, still non-executing, still bars measurement, still requires
  the `DEC-20260802-a51c82` mandatory read)
- `ledger/corrections/CORR-20260805-4b91ca.yaml` (defects D1–D4 against
  `IDEA-20260803-fa9839`, for context on what a repair would need to carry
  regardless of homing)
- `experiments/EXP-ICEX-146ff5/specification.yaml` line 5:
  `source_proposal_id: IDEA-20260803-fa9839` (confirms the rejected contract
  never acquired the "own `IDEA-*` record" R-D's second clause requires)
- Corpus check: `ledger/proposals/IDEA-2026080[6-9]-*.yaml` — no record documents
  an R-D-satisfying extended successor to `IDEA-20260803-fa9839`.

## Verdict

**STOP. Homing is unresolved by design.** R-D is not satisfied by the existing
contract, and this task cannot satisfy it either, because R-D's own text requires
a new `IDEA-*` record that is outside this task's `write_scope` and outside the
Coordinator's role to produce inline. The routing question is not GOAL-ECDLP-001's
to close; it is recommended for `GOAL-ICEX-001`'s Coordinator, on that goal's own
record, subject to that goal's own "NO ICEX MEASUREMENT AUTHORIZED" constraint and
its own reading of whether a genuine zero-compute derivation falls outside that
bar.
