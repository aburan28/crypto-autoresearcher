# BATCH-a33cda — opening report

**Goal** GOAL-ICPERF-e6b6a4 (ECC area `ICPERF`; campaign budget unlimited by policy)
**Opening decision** `DEC-20260915-428a17`
**Queue** `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-a33cda/dispatch_queue.json`
**Review round** `REVIEW-ICPERF-20260915-a33cda`
**Opened** 2026-09-15
**Runs performed by the opening** 0

This file is the readable account of the batch. The queue is the operative
record and the decision is the authority; where they differ, they win.

## What this batch is for

Repair the point-decomposition instrument, and have the repair independently
accepted, so that two empty columns of the `RQ-ICPERF-94c86e` boundary table
become recordable.

That is item (1) of the five-item ranking that BATCH-51e2aa's own review wrote
into the goal head (`DEC-20260915-87360d`, over `EV-ICPERF-390707`). It is
first for a reason that is measured rather than argued: `RUN-ICPERF-305ca3`
spent an eight-hour executor budget and returned a **zero** Gröbner column for
two independent instrument reasons, and one of them — a parse error in the
emitted Macaulay2 script — no memory limit could have rescued. Every other
ranked item either consumes the same instrument or reports through the same
reduction, so running one of them first risks buying that outcome again at
greater cost.

The payoff is also measured, not hoped for. In joint V2 of the closing review, a
validator computed the `n15l5-1-S` basis with **Singular slimgb in 167.4 s** and
**Macaulay2 F4 in 49.97 s**, the two agreeing on `gb_size = 43`, `maxdeg = 2`,
non-unit. The Gröbner column is reachable on this host, inside the contracted
budget, and the frozen instrument did not record it.

**What an acceptance would and would not assert.** It is a fitness statement
about this repository's harness. It moves no column of the boundary table, and
it supports no claim about any curve. It makes one column measurable.

## The five defects, and the one that is not gating

`EXP-ICPERF-e21835` repairs exactly the defects an independent session measured,
in a successor code tree, leaving the frozen tree byte-identical.

| id | site | what an independent session measured | gating |
|---|---|---|---|
| D1 | `convert.py`, `magma_to_m2` | The emitted script binds `gens_`; Macaulay2 reads the trailing underscore as its subscript operator, so all 32 Macaulay2 cells died at parse. | yes (A1) |
| D2 | `bench.py`, the `limits` closure | `RLIMIT_AS` caps address space, which is not a memory limit for a garbage-collected algebra system: Macaulay2 reserved 5.996 GiB of address space against 2.575 GiB resident. | yes (A3, A4) |
| D3 | `summary.py`, three sites | A loop-variable leak, plus two non-uniform reporting sites, which is how a producer's own summary reported predictions as holding that were partly unevaluated. | yes (A6) |
| D4 | `bench.py`, `environment()` | The version probe inherits stdin, so `Singular --version` waits for input that never arrives and the run cannot name its own Singular. | yes (A5) |
| D5 | `bench.py`, pure-CNF rows | `stats` is empty or absent for three engines of six, so a prediction stated in conflicts is evaluable for two. | **no** (A7) |

D5 is non-gating on purpose: whether a given solver prints usable counters is
not in the executor's power, so acceptance requires the counters *or* a recorded
reason per engine. Three further candidate changes are **excluded** with reasons
recorded in the contract's `defects_deliberately_not_repaired` — the null
objects' constant-term mismatch, flagging the degenerate `n15l5-8-S`, and adding
the Singular `slimgb` configuration. Each is a change to the *row's* protocol
rather than a defect repair, and each is carried forward as a named item
(`C-NULL2`, `CH-6`, `AP-2`) rather than dropped.

## Why a successor contract rather than an amendment

The repair could have landed as an additive amendment to `EXP-ICPERF-66fd51`
with a versioned code directory. It did not, for three reasons recorded as
`R-ARCH`:

1. **The changes are not additive to the protocol.** Replacing `RLIMIT_AS` with
   a resident-set watchdog, and moving the ceiling from 6 GB to 8 GiB, changes
   `budget.enforcement` and `budget.maximum_memory_gb` — two frozen scientific
   parameters, not two absent ones. An amendment that changes the *kind* and the
   *value* of a declared resource limit is a protocol rewrite in an amendment's
   clothes.
2. **A contract with two code trees cannot say which run used which.** The
   frozen `inputs.code` names four files and both existing run manifests point
   there; that field cannot be edited to name a `code_v2/`.
3. **The frozen bytes are the evidence for the defect claims.** They are the
   object `EV-ICPERF-390707` reported on.

The cost is accepted and stated rather than hidden: two copies of `binec.py` now
exist, and a future fix to the curve arithmetic must be applied twice or the
divergence recorded. The resolution is already named in the goal's own objective
(2) — promotion into `tools/` once a validator has run the code. This batch's
acceptance is that validator pass.

## Records this batch opens

| record | status | note |
|---|---|---|
| `DEC-20260915-428a17` | recorded | the opening decision and its ranking |
| `H-ICPERF-2c57cc` | `specified` | discharges `H-ICPERF-cc4847`'s restatement debt |
| `EXP-ICPERF-e21835` | **approved** | the repair and its pre-registered acceptance table |
| `EXP-ICPERF-13f001` | `draft`, `approved_by: null` | the row that will consume the repaired instrument |
| `REVIEW-ICPERF-20260915-a33cda` | frozen before any reviewer runs | six joints, one blind |

**The restatement debt, discharged.** `H-ICPERF-cc4847` recorded two wordings it
owed a successor. `H-ICPERF-2c57cc` pays both: Q1 now reads "a valid
decomposition **on E or on its quadratic twist**, with the side **recorded**",
which is what the twist finding forced; and Q6 **drops the mechanism
attribution outright**, because the closing review's relabelling control failed
and a null-object comparison provably cannot recover the attribution. Q2, Q3, Q4
and Q5's Gröbner clause are carried **unchanged** — they were unmeasured, not
refuted, and core rule 5 does not let an instrument failure stand in for
negative evidence.

**Why `EXP-ICPERF-13f001` is drafted but not approved.** Standing user
authorization already covers approval, so nothing here waits on a user; what
separates the two contracts is protocol completeness, which is the Coordinator's
own responsibility. The row contract has five named gaps, three substantive: the
slimgb configuration does not exist, the side classifier does not exist, and its
per-engine plan cannot be sized until the accepted instrument's Gröbner
behaviour is measured. It is drafted now so the repair has a declared consumer
and its acceptance criteria have a purpose.

## The review round, and its disclosed weakness

Six joints, each owned by exactly one reviewer, with the plan frozen and the
Coordinator's prior recorded **before either reviewer runs**.

- `TASK-20260915-3f4b52` — **R1** the Macaulay2 report line end to end, **R2**
  the memory limit is a resident-set limit and is not double counting, **R3** the
  reduction reports what it cannot evaluate and moves no number, **R4** the
  environment probe measured in both directions (the defect *and* the repair),
  **R5** scope, custody and manifest completeness; plus proves-too-much object 1.
- `TASK-20260915-abf147` — **R6** a blind re-derivation of the Gröbner quantity
  from the upstream instance alone; plus proves-too-much object 2.

**Two reviewers rather than one, and why R6 is blind.** The most useful thing
about the existing `gb_size = 43` agreement is also its weakness: Macaulay2 and
Singular read two files emitted by **one** converter, so their agreement cannot
detect a converter defect. Recomputing from the producer's own artifacts would
reproduce a wrong-but-self-consistent conversion faithfully. R6's read scope is
therefore deliberately narrow — it excludes both code trees, every emitted
script, the main review plan (which records the expected value) and the sibling
reviewer's directory — and the reviewer writes its four values down *before*
reading `acceptance.json` at all. Disagreement is a finding, localised to one of
two named conversions, and is not to be resolved by adopting the producer's.

**Proves-too-much.** The acceptance procedure is run against the **unrepaired**
tree, where every criterion must fail in its own defect's specific way. An
acceptance that passes the instrument it exists to reject has measured nothing.

**The round's principal weakness, disclosed.** Three of the four gating defects
are in code this Coordinator wrote, and this Coordinator wrote the review plan
and will compose the round. That concentration is recorded in the plan's
`blindness` block and is only partly mitigated — by the executor rather than the
Coordinator writing the repair, and by R6's blindness on the one load-bearing
quantity.

## Order of work

```
TASK-20260915-1942e2  coordinator  completed  this design
TASK-20260915-6d72a0  coordinator  READY      snapshot the design before anyone reads it
TASK-20260915-4f4027  executor                the repair + RUN-ICPERF-a4a24b acceptance run
TASK-20260915-7da7f1  coordinator             snapshot the run before either reviewer reads it
TASK-20260915-3f4b52  validator               R1-R5 + proves-too-much object 1
TASK-20260915-abf147  validator               R6 (blind) + proves-too-much object 2
TASK-20260915-efa91b  coordinator             EV-ICPERF-433fa5, DEC-20260915-927eaa, checkpoint
```

`max_concurrent` is **1**. That is machine headroom, not a research budget: four
CPUs, ~15 GB RAM, and every producing task here is either a timing measurement
or an 8 GiB-watchdogged algebra computation. BATCH-51e2aa recorded the cost of
getting this wrong — its own Macaulay2 phase drove the load average to 4.55 and
a review joint had to be split out to keep a measurement clean.

Every producing card carries explicit `dispatch_preconditions`, which are the
**dispatcher's** obligations and not the worker's: `archived_by` bound before
launch, declared inputs committed *and pushed*, and a claimed lane with a quiet
machine. `CORR-20260915-6708e4` records a violation of exactly these on another
lane of this goal.

Every archive in this batch declares `binding_mode: content_at_commit`
(`CORR-20260915-654160`). This is the first batch designed that way, and it is
the right default here: a batch that repairs an instrument holds records that
*must* move afterwards — a contract advancing to `completed`, a draft contract to
`approved`, a goal head reranked at every checkpoint. Under `content_first` every
one of those legitimate moves would report this archive as corrupt.

## What was deferred, and what would bring it back

Nothing in the ranking was dropped. Each deferred item carries its evidence,
its test boundary and a revisit condition in `DEC-20260915-428a17`:

- **(2) The exhaustive side-classified V³ table** (`IDEA-20260915-3f1964`) is the
  strongest deferred item and the closest to ready — the enumeration already
  exists as validator artifacts, covers all 60 instances and agrees with the
  solvers 60/60. It is second only because it is *independent* of the repair, so
  ordering it second costs nothing, whereas anything consuming the instrument is
  blocked. Open it as the next batch or a second lane.
- **(3) Why the 30 shipped U targets contain one decomposable target** where the
  measured fractions predict 5.57 (`P(X ≤ 1) = 0.0148`). Cheap and genuinely
  open, but it changes no column — it changes what "U instance" may mean. Until
  then every U-instance statement in this goal is scoped to 30 specific files,
  and `H-ICPERF-2c57cc` says so in terms.
- **(4) Structure versus variable order** (`IDEA-20260915-7ef636`). This is the
  deferral to watch, because it could be mistaken for burying the previous
  round's most informative result. It is not: the finding is **applied in full**
  — Q6 drops the attribution and the row contract removes it from the reported
  prediction. What is deferred is the new 2×2 experiment, and only because it
  needs the same quiet machine and the same repaired reduction item (1)
  delivers. What remains open, stated plainly: whether WDSat's advantage on the
  descended system is a property of the descended structure, of the emitted
  variable order, or of both. This goal has measured evidence for the **order**
  half only.
- **(5) The measured generic baseline** (rho and BSGS on these groups, this
  host). A different column of the same row; behind on machine headroom, since a
  timing measurement cannot share a host with a timing benchmark. Its
  corrections are already recorded: carry √n not √(2n), use r not #E, and treat
  n = 15 as unusable for any asymptotic constant at ~7 equivalence classes. The
  goal's first completion criterion requires it, so it cannot be dropped.

## Disclosed gaps in this batch's own setup

- **BATCH-51e2aa has no goal checkpoint shard.** That is a gap in the *previous*
  batch's archive and is not repaired here: writing a checkpoint for a batch
  whose ledger archive already completed would leave it owned by no archival
  task. BATCH-a33cda's checkpoint is a declared artifact of
  `TASK-20260915-efa91b`.
- **The acceptance rests on one instance** (`n15l5-1-S`) for the Gröbner path. A
  repair accepted there could still fail at l = 6, where F4 may not finish at
  all. The row contract's budget already expects l = 6 Gröbner rows to be
  censored.
- **The 8 GiB resident-set limit is a limit, not a measurement of what F4
  needs.** An equivalent 6 GiB RSS cap would also have killed the `n15l5`
  Gröbner row — honestly, which the 6 GB `RLIMIT_AS` did not. A row the new
  watchdog kills is a budget stop with its limit recorded, and is never negative
  evidence.
- **This batch's design task was interrupted.** The dispatched coordinator
  session that authored the five records was terminated by a host activity
  timeout after writing them and before writing the queue, this report, or the
  goal-head update; it also left three records carrying a block scalar inside a
  flow mapping, which YAML forbids. The top-level session completed the three
  missing artifacts and repaired the three files without changing any wording.
  This is the second subagent session lost to a host timeout in this campaign.
  It is an infrastructure fact and never a research one, and it is recorded in
  the queue's receipt for `TASK-20260915-1942e2` rather than smoothed over.
