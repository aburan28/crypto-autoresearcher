# GOAL-PATCH-terminal — GOAL-ECQ-2298dc

**Target file** `ledger/goals/GOAL-ECQ-2298dc/goal.yaml`
**Authorised by** `ledger/decisions/DEC-20260824-b7557b.yaml` (`decision: pause`,
`goal_status_set: blocked`)
**Author** coordinator, 2026-08-24
**Applied by** the orchestrating session (this Coordinator holds no shell)

This patch makes exactly two replacements. Everything else in `goal.yaml` is
left byte-identical.

**THE OBJECTIVE WAS NOT MET.** No elliptic curve over Q of Mordell-Weil rank
>= 32 was found. Rank >= 32 over Q remains an open problem; the live record is
31 (ICARM curve no. 302, posted 2026-08-23). Nothing in this patch, and nothing
in the campaign it closes out, is partial credit toward 32.

---

## PATCH 1 of 2 — `status`

### Replace this exact text (currently line 135)

```yaml
  status: active
```

### With this exact text

```yaml
  status: blocked
```

**Why `blocked` and not `paused`:** the binding constraint on C1 is an external
dependency that does not clear by spending this program's own budget. The
rank-17 elliptic K3 fibration carrying the published record ladder has never
been published; the best explicit substitute (Kihara rank 14) is paywalled
behind an encrypted PDF and this program declined to circumvent the access
control; no published model of generic rank >= 18 over Q(t) exists. The two
lanes needing nothing external were run to 100 % coverage of their frozen
regions and returned certified rank 0. Full reasoning, the counter-argument for
`paused`, and why `closed_at_budget`, `completed` and `cancelled` are all false
here: `DEC-20260824-b7557b.status_choice`.

**`blocked` asserts no success.** Per AGENTS.md, `paused`, `blocked` and
`closed_at_budget` all assert no success, and none of them may be used to
understate a criterion that was actually met. No criterion was met.

---

## PATCH 2 of 2 — `next_action`

The current value is dangling: it instructs a dispatch that has already been
performed twice (`TASK-20260824-261bb4`, then `TASK-20260824-02c3e4` under
`PA-ECQ-f5af06-v2-triage-gate-sign`).

### Replace this exact text (currently lines 262–271)

```yaml
  next_action: >-
    ONE ACTION AND ONLY ONE. Commit and push the four records authored 2026-08-24 --
    ledger/goals/GOAL-ECQ-2298dc/goal.yaml, ledger/questions/RQ-ECQ-e9b361.yaml,
    experiments/EXP-ECQ-f5af06/specification.yaml and ledger/handoffs/TASK-20260824-261bb4.yaml --
    on a branch with an open PR against main naming those four record IDs, then and only then
    dispatch TASK-20260824-261bb4 to the executor against the now-frozen contract. THE CONTRACT
    MUST EXIST IN A COMMIT BEFORE THE PRODUCER STARTS; a contract authored after execution is a
    receipt, not a protocol, and DEC-20260823-ee9162 N1(h) makes dispatch without one a blocker
    rather than an open item. Nothing else is dispatched under this goal until
    TASK-20260824-261bb4 returns and its results are reviewed.
```

### With this exact text

```yaml
  next_action: >-
    ONE ACTION AND ONLY ONE, AND THIS PROGRAM CANNOT TAKE IT. A HUMAN MUST REVIEW AND SEND
    coordination/goals/GOAL-ECQ-2298dc/inputs/DRAFT-elkies-request.md FROM A REAL ADDRESS,
    under the constraints in that file's own "Notes for whoever sends this": replace the
    signature block with a real person, keep the disclosure that an AI system drafted it, and
    do not overstate what this program has done -- the rank->=31 certification CONFIRMS AN
    EXTERNAL PARTY'S RESULT ON AN EXTERNAL PARTY'S CURVE and is not this program's. It asks
    N. D. Elkies for the explicit Weierstrass model of the rank-17 elliptic K3 fibration over
    Q(t) that carries the published record ladder (28 = 17 + 11, 29 = 17 + 12) and that he
    offered on NMBRTHRY in May 2006 and never posted.
    WHAT IT REACHES, STATED HERE SO THAT `blocked` IS NEVER READ AS "ONE EMAIL AWAY FROM 32":
    GENERIC RANK 17 OVER Q(t). IT REOPENS A LANE AND IT DOES NOT REACH C1. The remaining 15
    units of rank would still have to come from the specialisation sieve this campaign recorded
    as not plausible with its resources before any work began (odds_assessment items 3 and 4,
    IDEA-20260824-324dca). A decline or no reply is a COMPLETE ANSWER and closes that lane
    cleanly; it is explicitly NOT a reason to attempt the model's reconstruction, which
    coordination/goals/GOAL-ECQ-2298dc/inputs/SCOPING-recomputation-lane.md establishes would
    yield only rank 17 and so would not reach the objective EVEN ON COMPLETE SUCCESS.
    NOTHING IS DISPATCHED UNDER THIS GOAL. No batch, no experiment, no producer task, and no
    identifier is minted against this goal. A later session that wants to resume must first
    record in a NEW Coordinator decision that one of the three resume conditions in
    DEC-20260824-b7557b was met -- the model obtained from its author, a published model of
    generic rank >= 18 over Q(t) appearing, or a funded OSCAR step-0 lattice measurement
    reporting the free-parameter count d -- and must not resume by dispatching another search.
    NONE OF THE THREE REACHES RANK 32; each reopens a lane whose own ceiling is stated in that
    decision.
```

---

## What this patch deliberately does NOT change

- **`completion_criteria` C1 `met: false` — LEAVE IT.** It is already correct
  and it is the load-bearing field. C1 is unmet, not partially met.
- **`completion_criteria` C2 `met: false` — LEAVE IT.** C2 is also unmet. Note
  for the record (in `DEC-20260824-b7557b` at `E4`, not in this file): C2's
  stated route was additionally **mis-specified** — generic rank >= 19 over Q(t)
  is unreachable via elliptic K3 surfaces by a proven ceiling. Correcting the
  criterion text is not attempted here; an immutable record is superseded, never
  edited, and the correction lives in the decision.
- **`odds_assessment`, `state_of_the_art`, `citations`, `pause_conditions`,
  `campaign_budget`, `preregistered_baseline`, `procedure_deviation_reference`**
  — all unchanged. In particular `pause_conditions` is left alone even though
  **none of P1–P5 fired**; the terminal status rests on grounds the goal's own
  pause conditions did not enumerate, and `DEC-20260824-b7557b.status_choice.
  pause_conditions_that_fired` records that as a Coordinator judgement rather
  than dressing it as a trigger that fired.
- **`checkpoints: []`** — unchanged. No `BATCH-*` identifier was ever minted
  under this goal, so there is no batch to shard a checkpoint against, and a
  checkpoint shard is named `checkpoints/BATCH-<tok>.yaml`. This decision is
  the campaign's terminal record instead.

---

## NOT PART OF THE PATCH — three optional field updates, your call

These are **not** authorised by the mandate for this patch and are listed only
so the choice is explicit rather than accidental. Applying them is safe;
declining them leaves known-stale fields, which is exactly the defect
`DEC-20260823-ee9162` charged to the Coordinator for three consecutive batches
on `GOAL-ECQ-002` (R9(e), N1(e)). Recommended: apply all three in the same
ledger commit.

1. `decision_ids: []` → `decision_ids: [DEC-20260824-5246b7, DEC-20260824-b7557b]`
   — otherwise the goal record names none of its own decisions and a reader has
   no path from the goal to its terminal record.
2. `updated_at: '2026-08-24'` — already correct as a date; no change needed
   unless the patch is applied on a later date, in which case set it to the
   date of application.
3. `latest_verified_commit: null` — set by the archive that applies this patch,
   **after** the post-commit verifier accepts it, per the field's own note. A
   record cannot carry the sha of the commit that introduces it, so this cannot
   be filled in the same edit; it is a follow-up or it stays null.

`evidence_ids: []` is **correct and must stay empty**: no evidence record was
ever written under this goal, and no run set has been validated by an
independent validator, a red team, or the Coordinator.

---

## Apply and commit

1. `git fetch origin` and **merge** `origin/main` into the working branch —
   merge, never rebase. Record the base commit checked and the merge outcome in
   the task receipt.
2. Apply patches 1 and 2 above (and the optional updates if you take them).
3. Stage **only** `ledger/goals/GOAL-ECQ-2298dc/goal.yaml` and
   `ledger/decisions/DEC-20260824-b7557b.yaml`. This ledger archive runs alone.
4. `python3 tools/validate_ledger.py` on the merged tree; expect clean, with the
   record count moving by exactly one (the decision; the goal record already
   exists).
5. Commit naming `DEC-20260824-b7557b` and `GOAL-ECQ-2298dc`, push, and open or
   refresh a PR against `main` naming both. **A record that exists only in a
   local commit is unpublished, not durable evidence** — and a terminal goal
   status that is unpublished has not actually been recorded.
6. This file is a coordination artifact, not a ledger record. It may be
   committed alongside or omitted; the binding statement is the decision.

If step 4 fails on the decision record, **do not edit it after it is
committed** — supersede it with a new `DEC-*`.
