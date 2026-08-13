# TASK-20260813-85e343 — INDEPENDENT RED TEAM

    goal / batch    GOAL-MLKEM-005 / BATCH-6b6e78
    role            red-team
    policy          review-adversarial     effort xhigh
    state           queued
    depends_on      TASK-20260813-2ce014, TASK-20260813-48240d
    review_required false
    archived_by     TASK-20260813-3dfbdb
    budget          7200 s, 4 GB, 1 run
    independence    INDEPENDENT SESSION REQUIRED
    claim tier      TOY

## The target is the ASSUMPTION, and you BUILD rather than propose

The criterion family in this goal has been broken **four times by four
structurally different routes**: a change of arithmetic route, a `1e-10` additive
perturbation, a one-line change of family, and a re-declaration of the argument
set. The fifth target is `A-1` itself.

**PRIMARY — THE ASSUMPTION'S USABLE CONTENT.** PREREG-2's `P-HASH` predicts that
`X_hash` — which reads every entry of `A` and carries **no** lattice information —
is precision-**invariant**, hence that `A-1` cannot separate it from a real
object. **BUILD A SECOND, STRUCTURALLY DIFFERENT INSTANCE**: an object certified
exactly non-constant on its own declared fibre, precision-invariant, carrying no
usable lattice information, and **not** a scaled digest. If you cannot build one,
**report the search and its cost** — that is a real result and it is reported as
such.

**SECOND — THE FALSIFIERS' REACHABILITY.** For **each** of `FC-1`, `FC-2a`,
`FC-2b`, `FC-3a`, `FC-3b`, state whether the declared instrument could have
reached it **at all** before the run, and at what parameter value. `AM-18(d)`
forced this discipline on guards; apply it to the falsifiers. **A falsifier that
could not fire is not a falsifier.** PREREG-2 §7.2 already concedes that
`T-UNSTATABLE` is nearly foreclosed by an archived artifact — check whether the
same is true of the others. (`O-6` is this goal's recorded cost of a VOID row that
was unreachable by a factor of 71.3 before anything ran.)

**THIRD — THE `precision_degenerate` RULE AND THE WINDOW.** §1.3 exempts cells
where `rho(binary64) == 0` exactly; §1.4's `[1/2, 2]` is the only calibrated
constant in the whole falsifier. Does the exemption remove the only cells where
`A-1.2` could have failed? Does a defensible different window change any verdict?

**FOURTH — THE DERIVATION.** PREREG-2 §2.9's exact route for `X_gso_k` is the
Coordinator's own derivation and no one has checked it against anything but the
producer's own numbers. **Break it if it is breakable**: a case where
`I_k + A A^T` is not the leading Gram block, a lattice where the row order
differs, an overflow, a wrong `k`.

**FIFTH — THE TERMINATION BRANCH.** Is the branch reported the branch the frozen
clause fires? Was the precedence rule applied and `R3-OUT-V` evaluated first? Was
any infrastructure or coverage outcome narrated into a science branch (§7.6)?

## And attack §7.5, THE REPAIR BAR, as a specification

Is it satisfiable at all? Is any of its six conditions **vacuous**? Does it in
practice forbid **every** repair — which would make it a lane closure by the back
door, the failure mode symmetric with unbounded repair, in a document that claims
to bar both?

## Also required

* **The arrangement in which the lead's check could not have failed is named in
  both directions** — could-not-FIRE and could-not-PASS — and whether it ran in
  that arrangement is **stated**.
* **At least one null or nearby-object control is BUILT, not proposed**, packaged
  as a re-executable probe with its recorded output.
* **The cheapest falsification of every headline is stated with its cost.**
* `AM-10`'s replication and `AM-11`'s dispersion requirements apply to **every**
  statistic anyone in this batch proposes, including any you propose. `AM-11` in
  particular: is anything **parameter-determined** admitted anywhere in this
  batch's re-executed code path?
* **State, per artifact read, whether it was read COMMITTED or UNCOMMITTED.**
  Every producer artifact is committed before you run, at `TASK-20260813-48240d`;
  if you had to read one uncommitted, that is a finding.
* A probe on your own frames is reported **as a probe**: not pre-registered, at
  the scale actually run, **never** a rescoring of any frozen verdict — of this
  batch or of any prior one.
* **Where a measurement goes against your own thesis, report it at the same
  weight as your objections.** The `BATCH-4ed139` red team's fired twice, and that
  is why its adverse findings were credited.

## Artifacts and declared gap G-1

    reviews/TASK-20260813-85e343/red_team_report.md
    reviews/TASK-20260813-85e343/probes/...           (every probe you build)

**LIST EVERY PROBE PATH EXPLICITLY IN YOUR REPORT.** The queue declares one path
for you today and that will not be enough; the ledger archive's declared set must
be extended by **exactly** your probe paths before it stages (`G-1`). The
`BATCH-4ed139` red team flagged this itself, as its `O-9`, and that is why that
archive verified at 46 of 46.

## Binding

**COMMIT NOTHING.** Your report and probes sit uncommitted across a dispatch
window (PD-4, open) and are the **sole carriers** of their own evidence. **Do not
restate `KN-FIND-9d44b4`'s promoted content as a new result of this batch**
(PREREG-2 §9 lists exactly what that is). PREREG-2 §§10 and 10.1 bind in full:
`AM-3` is **not** retired and nothing you find here retires it; `BATCH-a44d08` is
**not** rescored; `BATCH-4ed139` is **not** revalidated; the full NOT-CITABLE list
applies. **Premature closure is a failure mode symmetric with overclaiming, and
unbounded repair is its mirror image.** A count of screened-and-rejected criteria
is a fatigue report; a closure needs a named obstruction, an argument and forward
guidance. Closing the admissibility-gate LANE retires the **LANE**, never the
goal. **CLAIM TIER TOY.** `knowledge/INDEX.md` is not written, regenerated or
staged.
