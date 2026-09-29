# TASK-20260812-696cd4 — INDEPENDENT RED TEAM

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           red-team
    policy         review-adversarial      effort xhigh
    state          queued
    depends_on     TASK-20260812-56b9da, TASK-20260812-b581a8,
                   TASK-20260812-78a6e3, TASK-20260812-4b8ede,
                   TASK-20260812-0e930c, TASK-20260812-b53c2f
    archived_by    TASK-20260812-655fe9   (ledger archive, runs alone)
    budget         7200 s wall clock, 4 GB, 1 run
    claim tier     TOY

## Objective

Attack G-VAR2 where its own pre-registration says it is weakest, and price the
cheapest falsifier of every headline. **BUILD the object rather than proposing
it.**

## Why the primary target is what it is

This criterion's predecessor has now been broken **three times by three
structurally different routes**: a change of arithmetic route (wave 1, S1-1), a
1e-10 additive perturbation of the observable (wave 2, S2-1 / O-2), and a
one-line change of family (wave 2, S2-2 / RT-R1). PREREG-1 §3.5 names the fourth
route in advance and concedes it before any measurement:

> The fibre clause **moves** a free parameter; it does not remove one. The
> family was undeclared and is now declared; the arithmetic route was undeclared
> and is now declared; the **declared argument set** is now the free parameter.

**PRIMARY TARGET — the declared argument set.** Build a candidate that is
non-constant on its own declared fibre while still carrying no usable lattice
information, or a re-declaration of an existing candidate's arguments that flips
its verdict. If you cannot build one, **report the search and its cost** — that
is a real result and it is reported as such.

## Second and third targets

* **`tau_var = 1e-3` and the degenerate-scale rule.** The threshold is calibrated
  on committed numbers (PREREG-1 §3.4). The rule decides every beta-free
  candidate by VAR-F alone (§3.2). Check the case §3.2 names: whether the rule
  refuses everything beta-free, making VAR-F decorative.
* **The termination branch.** Check that the branch reported is the branch the
  **frozen** clause fires; that the precedence rule was applied; that R2-OUT-V
  was evaluated first; and that no infrastructure outcome was narrated into a
  science branch (§7.4).

## Per-producer obligations

For the lead **and all three riders**: name the arrangement in which its check
could not have failed, **in both directions** (could-not-FIRE and
could-not-PASS), and state whether it ran in that arrangement.

* **Rider (ii)** specifically on its `n = 1` claim: check that no false-refusal
  **rate** is reported, estimated or implied anywhere, and that the
  informativeness half is demonstrated rather than asserted.
* **Rider (iii)** specifically on its framing: check that it is nowhere presented
  as resolving a doubt, and that a missing-dependency outcome, if any, is nowhere
  treated as evidence about `lam1n`, `hkz`, the 48 reductions or the reported
  max violation of 0.0.

## Deliverables

    reviews/TASK-20260812-696cd4/red_team_report.md
    reviews/TASK-20260812-696cd4/probes/...   (at least one BUILT, re-executable
                                               probe with its recorded output)

**Every probe path is listed explicitly in the report** so the ledger archive can
declare it. An undeclared probe cannot be committed and its evidence is lost.

## Discipline

State the cheapest falsification of every headline **with its cost**. Apply
AM-10's replication and AM-11's dispersion requirements to every statistic anyone
in this batch proposes, including yours. Report a probe **as** a probe: not
pre-registered, at the scale actually run, never a rescoring of a frozen verdict.
State, per artifact read, whether it was read **committed or uncommitted**. Every
producer artifact in this batch is committed before you run — the lead at
`-b581a8`, the three riders at `-b53c2f` (queue gap G-2, closed). If you had to
read any producer artifact uncommitted, that is a finding. Your own report and
probes remain uncommitted across a dispatch window (PD-4 proper, open).

**Where a measurement goes against your own thesis, report it at the same weight
as your objections.** The BATCH-cbe023 red team's fired twice and that is why its
adverse findings were credited; wave 1's fired six times.

**Premature closure is a failure mode symmetric with overclaiming.** A count of
screened-and-rejected mechanisms is a fatigue report; a closure needs a named
obstruction, an argument and forward guidance. Closing the admissibility-gate
LANE retires the LANE, never the goal.

INDEPENDENT SESSION. COMMIT NOTHING. Binding carries: PREREG-1 §§11 and 11.1 in
full. CLAIM TIER TOY. `knowledge/INDEX.md` is not written, regenerated or staged.
