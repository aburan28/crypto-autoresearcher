# BATCH-cbb416 — opening report

**Goal** `GOAL-SEMBIN-fcb7a2` (declared ECC area `SEMBIN`; campaign budget unlimited by policy)
**Opening decision** `DEC-20260916-59921c`
**Queue** `coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-cbb416/dispatch_queue.json`
**Review round** `REVIEW-SEMBIN-20260916-cbb416`
**Contract dispatched** `EXP-SEMBIN-4fa22c` v1 (approved by `DEC-20260916-6ce039`)
**Hypothesis** `H-SEMBIN-a7e721`
**Opened** 2026-09-16
**Runs performed by the opening** 0

This file is the readable account. The queue is the operative record and the
decision is the authority; where they differ, those two win.

## Why this batch exists

This is the **first** batch of `GOAL-SEMBIN-fcb7a2`. The goal has taken no
measurement and holds no run record. Three of its four completion criteria
require run evidence and one required a read; only the read criterion is met
(`DEC-20260913-8d19e5`). Authoring the hypothesis and freezing and approving the
contract on 2026-09-16 changed **reachability, not status** — a point this
campaign had to correct once already (`CORR-20260916-402547`), and which is why
this report says it again rather than counting the approval as progress.

So the batch has one purpose: get the first run-or-read evidence onto this goal.

## The ordering, which is the only interesting design choice here

**Two producers in series, and the second is `blocked` rather than queued.**

`EXP-SEMBIN-4fa22c`'s own `proof_search_map` carries an
`observation_collision_search` whose status field reads *REQUIRED BEFORE THE
FIRST RUN and not yet performed*. Nobody has performed it. Section 8 of
`docs/inventor-protocol.md` makes these audits cheap pre-compute falsification
checks, and a failed audit is frequently the useful result — so the audit runs
first, as a task with deliverables, not as a checkbox in the executor's brief.

It is expected to find something. One regex over `knowledge/`, `ledger/` and
`experiments/` — `first.fall.degree|first_fall_degree|d._F` — returned
first-fall-degree machinery in at least six places this campaign has never read,
including `experiments/EXP-ECTD-9e4248/driver/reused/macaulay.py` and
`experiments/EXP-SIG-007/src/ic_first_fall_fast.py`. **The Coordinator did not
open any of them** and makes no claim about what they contain; that list is
recorded in the audit's card explicitly as a starting point and not as a result.

Three outcomes are each cheaper before the compute than after:

1. an existing **validated** Macaulay-rank instrument makes writing a third one
   waste — and whether one may be reused is a Coordinator ruling, since the
   contract forbids importing `EXP-ICPERF`'s converter and says nothing about
   `EXP-ECTD`'s;
2. an existing measurement on a comparable object makes the planned run a
   **replication**, which is worth doing and must be framed as one;
3. an existing measurement that **contradicts** `H-SEMBIN-a7e721`'s prediction
   is worth more than the run.

The execution is therefore `blocked` behind a **Coordinator ruling on the
audit's verdict**, deliberately not behind its mere completion: dispatching the
executor the moment the audit returns would waste the audit. If the verdict is
`collision: none, recommendation: proceed`, that ruling is short and says so.
`blocked` is a task state; nothing here pauses a goal, which stays `active`.

**A disclosed limit on the audit.** `kb/` in this checkout has no `.venv`, no
`.env` and no reachable Qdrant, so `search_knowledge` **cannot be called**. The
audit searches the repository directly and reports a **recall floor**, never a
clean bill of novelty. `AGENTS.md` is explicit that absence of a search result is
not evidence that something was not tried.

## The queue

| task | role | state | what it does |
|---|---|---|---|
| `TASK-20260916-141f76` | coordinator | completed | this opening: decision, queue, review plan, checkpoint, goal head |
| `TASK-20260916-007117` | coordinator | queued | snapshot the control plane, so both producers read committed bytes rather than a working tree |
| `TASK-20260916-fc72a6` | executor | queued | the observation-collision audit — zero runs, zero measurements |
| `TASK-20260916-0c2802` | executor | **blocked** | execute `EXP-SEMBIN-4fa22c`; unblocks on a committed ruling about the audit |
| `TASK-20260916-8eb394` | coordinator | queued | snapshot both producers before any reviewer reads them |
| `TASK-20260916-90af14` | validator | queued | joints J1, J2, J5 and the proves-too-much control |
| `TASK-20260916-7be96a` | validator | queued | joints J3, J4 and the blind re-derivation |
| `TASK-20260916-6a2fcf` | coordinator | queued | ledger-archive the composed review and close the batch |

`max_concurrent` is 1. That is machine headroom, not a research budget: the
contract declares a 10 GB memory ceiling for a single degree-4 Macaulay block on
a 4-CPU, 15 GB host, and the goal head's own basis records why two producers is
the ceiling for this campaign even when nothing else is running. The ECC
unlimited-budget instruction removes the batch and wall-clock ceilings; it does
not license oversizing this number.

## What this batch cannot reach, stated before it runs

**Nothing here can refute Proposition 5.** DC-1 of `DEC-20260916-88ac73`: a
Boolean-ring Macaulay computation is structurally unable to exhibit `d_F > 4`,
because degree drops produced purely by `X^2 -> X` count toward the true degree
and are invisible to the fake one. The contract makes that a **success
criterion** (S-1) rather than a caveat, precisely so that no run discovers it
after the compute is spent. The reachable target is the proposition's
**justification** at specific instances.

And a result *presented* as contradicting Proposition 5 would need
`review-breakthrough` at `max`, which is undegradable and **cannot be served in
this environment**. Such a claim would stay un-promoted while the campaign stays
active. That is a limit on the claim, never on the campaign, and this batch does
not pre-authorize a cheaper tier for a result nobody has seen.

## The review round, written now

`REVIEW-SEMBIN-20260916-cbb416` is committed by **this opening**, before the
executor is dispatched and long before any reviewer runs. Five joints, two
owners, blindness declared, a proves-too-much control, a blind re-derivation, and
four Coordinator priors recorded in advance.

One prior belongs in this report because it changes how the batch should be read:
**the Coordinator expects the shuffled null not to separate from the target, or
to separate only weakly, and considers that about as likely as the headline
outcome.** If that is what happens, S-6 makes the null failure the run's headline
and no `d'_F` value is offered as evidence about Nagao. Writing it down now is
what stops it from reading as a disappointment later.

The plan can be written this early because its joints are the **contract's**
load-bearing steps, not the run's outputs. What the run will measure is unknown;
what it must get right in order to have measured anything is fully determined by
the frozen specification.

**A standing obligation this batch inherits.** The blind re-derivation's quantity
does not exist yet, which is its one advantage over ICPERF's — where the value to
be re-derived had already been quoted in the very document written to protect it
(`CORR-20260916-292e53`). The obligation that follows: **no card, batch note, bus
message or report in this campaign may ever quote a measured `d'_F`.** Cite the
run record. And before the blind task is dispatched, the Coordinator re-greps the
tree as it then stands, *including whatever was written as part of that
dispatch* — the omission of exactly that step is what caused the ICPERF leak.

## Inference, declared up front

Every card sets `fallback_allowed: true` **with a stated reason**, rather than
inheriting `false` from the `AGENTS.md` handoff template and being amended after
the work runs. That default is correct for the contract and false for this
machine, which holds no API credentials for any adapter backend; `BATCH-a33cda`
needed three separate after-the-fact amendments to learn it
(`DEC-20260916-7b2235`, `DEC-20260916-bec4b8`). `model_verified` is `false`
throughout and is recorded as **not obtained**, not as met.

## Ranked out of this batch, with revisit conditions

- **A second read of Nagao 2013/548 §7** on the `m!`-removing device.
  `CORR-20260916-273589` already corrected the attribution and what remains is
  historical credit rather than a measurement. Revisit if a claim here comes to
  depend on who invented the construction.
- **Extending the `n`-series above the contract's 12.** The stopping rules
  already walk `n` upward and stop at censoring, so the reachable `n` is a
  measurement rather than a design choice. Revisit when a completed pass shows
  where it actually stopped.
- **A red-team pass on the mechanism before any data exists.** There is nothing
  to falsify beyond the reasoning already recorded; the round opened here attacks
  the instrument and the controls, which is where this batch can actually be
  wrong. Revisit if the run returns a separation, at which point the mechanism
  claim becomes load-bearing and a red team has an object.

- **The odd-characteristic (p ≥ 3) nearby-object control** stays deferred with its
  arithmetic recorded rather than dropped: sized under `TASK-20260913-74b33c` and
  found largely out of reach — at `p = 3` the descended generators have total
  degree 4 with no Frobenius drop and Proposition 2's bound is `D = 3p+1 = 10`,
  which at `(n,m,k) = (9,3,3)` needs 7.5 TB by the same accounting that fits
  `p = 2` in 1.5 GB. It survives only at the smallest cells and belongs to a
  successor contract.

## What opening this batch does not do

It does not re-approve the contract or the hypothesis, does not assert that the
hypothesis is true or that the run will produce evidence, and **moves no
completion criterion**. Criterion 4 remains the only one met.
