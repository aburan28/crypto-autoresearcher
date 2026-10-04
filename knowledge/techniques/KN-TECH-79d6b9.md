---
id: KN-TECH-79d6b9
type: technique
title: Acceptance readings for a recording layer should be monotone, and every favourable condition must be positive evidence collected by a process the failure cannot subvert; exact-coverage readings over a path enumeration did not converge
tags: [protocol-amendment, acceptance-reading, recording-layer, fail-closed, positive-evidence, monotone-reading, exact-coverage, non-convergence, red-team, known-answer-control, fork, process-identity, governance, methodology]
confidence: reported
complexity: >-
  not a cost model - a design rule for the pre-declared readings that decide
  whether a protocol repair of a recording or verdict layer is approvable.
  The operative quantity is which conditions of a PASS or admission rule are
  established by a positive record and which are inferred from the absence
  of one; an absence-based favourable condition is where an unbounded
  enumeration of failure paths re-enters a design that is otherwise
  fail-closed
applicability: >-
  every amendment to a wrapper, recorder or checker layer around frozen code
  whose correctness is defined over the frozen code's execution paths
  (launch sites, raise points, forked children), in particular a layer that
  must show that every capped child process was recorded under its cap; and,
  by extension, any acceptance reading that asks for exact coverage of a set
  that has no finest granularity
source_refs: [DEC-20260924-afdc3b, DEC-20260924-a7453e, DEC-20260924-e6638d, DEC-20260924-650068, DEC-20260924-a789e1, DEC-20260924-8fa3d4, DEC-20260924-e52eec, DEC-20260924-1ce186, DEC-20260924-844896, CORR-20260924-862f7d, AMD-EXP-GFPN-05ff43-20260924-failclosed, AMD-EXP-GFPN-05ff43-20260924-childend, TASK-20260924-f5631b, TASK-20260924-0c2fdc, TASK-20260924-eb2540, TASK-20260924-64c8fe, EXP-GFPN-05ff43]
proof_status: empirical_only
proof_refs:
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml
  - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md
  - ledger/decisions/DEC-20260924-8fa3d4.yaml
  - ledger/decisions/DEC-20260924-844896.yaml
added: '2026-09-24'
superseded_by: null
---

## What this note is, and is not

A note about **protocol method**: how to write the pre-declared readings that
decide whether a repair of a recording, verdict or development-harness layer
may be approved. It is drawn from one experiment of one campaign
(`EXP-GFPN-05ff43`, `GOAL-GFPN-380702`). It is **not** a finding about any
GFPN object, about D, about `H-GFPN-9a29be` or `HEUR-GFPN-DFLAT`, or about the
security of any curve, and nothing in it is a mathematical result. The
experiment's measured side has not run under the repaired protocol.

## 1. The observation: exact-coverage readings did not converge

Six successive drafts of one repair lineage were each decided **not
approvable as written** because a pre-declared reading asked for exact
coverage of an enumeration, and the next, finer census found an item outside
it:

| draft | failing reading | decision | what the finer enumeration found |
|---|---|---|---|
| healthresolve | CN-1 | `DEC-20260924-afdc3b` | a third classified launch site (the callgrind child) |
| launchcover | LP-1 / LP-2 (iv) | `DEC-20260924-a7453e` | six readers of one child's record |
| consumercover | CU-2 | `DEC-20260924-e6638d` | consumers outside the class rule |
| readbackcover | RBR-1 | `DEC-20260924-650068` | a pass-through solve and failure-branch children |
| readbackfull | RLR-1, RLR-4 (b) | `DEC-20260924-a789e1` | created children with no read-back source; a zero-launch refusal |
| readbackclose | RKR-1 (b) | `DEC-20260924-8fa3d4` | children created and recorded "not created" (a raise between `fork()` and the local store; a second raise in a `finally`) |

The one draft of the lineage that was approved (`DEC-20260924-e52eec`) failed
at its gate on a recording gap (`DEC-20260924-1ce186`). The granularity grew
each round: launch sites, consumers, children, branches, implicit raise
points, bytecode boundaries, exception chaining, the fork-child path. The last
census stated that its interpreter behaviour came from documentation and
compiled bytecode. **There is no finest level at which an exact-coverage
reading over those paths is known to close**, so a seventh patch-and-census
round would predictably have failed the same way (`DEC-20260924-8fa3d4`,
disposition.change_of_approach).

A second, less obvious observation from the same record: **every exceptional
path the censuses found already ended in a failed package** (the frozen driver
has no handler, and the wrapper records the package failed), so the
record-exactness readings sat where no verdict depended on them, while the
real fail-open routes sat in the verdict rules (an infrastructure failure
admitted by a zero-launch verdict).

## 2. The design that replaced them (fail-closed, monotone, adversarially checked)

`AMD-EXP-GFPN-05ff43-20260924-failclosed` changed the kind of rule and the
kind of reading, not the number of clauses:

1. **Positive evidence.** Every recorded value that feeds a verdict is taken
   from a named positive record, or is the literal `undetermined`; nothing
   favourable is inferred from an absence.
2. **`undetermined` yields FAIL, and every FAIL of a package a dependant reads
   is a designed stop** for a new decision, never evidence.
3. **Outcome classes.** A result file written by the frozen command is
   distinguished from one the wrapper writes after an infrastructure failure;
   only the former can be a basis.
4. **Monotone readings.** Only a *fail-open counterexample* (a pass or an
   admission while a required record is missing) or a *planned-basis refusal*
   (a designed outcome the rules refuse) bars approval. A path on which the
   rules FAIL is never a bar and never orders another census.
5. **An adversary instead of an enumerator.** An independent zero-run
   red-team review, blind to the author's argument and prior, searches for
   fail-open counterexamples, and must first reproduce known answers.

## 3. What the independent review found against it (`TASK-20260924-f5631b`)

Archived by `TASK-20260924-0c2fdc`; decided in `DEC-20260924-844896`.

- **The known-answer control worked, and discriminated more finely than
  asked.** The reviewer's method flagged every named object of the previous
  draft, and separated *record-level* defects (a wrong value in a record on a
  package that fails anyway) from *package-level* fail-open routes. It also
  showed that one expectation written into the review card was not derivable:
  under the fail-closed verdict rules no raise path can reach PASS, so
  weakening the three-valued child-creation rule changes no verdict
  (`CORR-20260924-862f7d` item 2). **Lesson: grade a known-answer control at
  record level and package level separately, and derive each expected answer
  under the full rule set, not under the one clause being varied.**
- **The verdict rules held** against a search of every layer between the
  frozen launcher and the entry points for a handler that could turn a raise
  into a result.
- **One fail-open counterexample, FO-1.** A forked child that leaves the
  frozen child path through an asynchronous exception runs the caller's code
  in a process other than the installing one. The design detected that only
  through a file the escaped process writes itself; if that write fails or is
  interrupted, a record the escaped process writes elsewhere goes undetected
  and the package can PASS. No capped workload runs and no child lacks its cap
  record, but the pre-declared definition was met as worded. The root cause
  was **one absence-based favourable condition inside a design that was
  otherwise positive**: "no foreign-process file exists" was read as "no
  escape happened", contrary to the design's own first principle
  (`CORR-20260924-862f7d` item 3).
- **One planned-basis refusal, PB-1, definitional.** Replacing an older clause
  kept its designed stop but dropped the sentence that excluded those outcomes
  from the planned-basis scope; no verdict changed, but the reading as worded
  was met (`CORR-20260924-862f7d` item 4). **Lesson: when a clause is replaced,
  re-check every definition that the replaced clause's text was carrying.**
- **Fail-closed findings (never a bar):** the development harness would stop
  by construction on the reference base (three checker items fail where one
  was expected; every child's argv embeds a path that carries the development
  label). These came from expectations stated from a census table rather than
  from the checker's own items and the argv construction.
- **A premise of the design was conditional.** A PASS route the design was
  motivated to close existed only under a wrapper that records one value
  independently; on the reference base it did not (`CORR-20260924-862f7d`
  item 1). **Lesson: a route used to motivate a rule is itself a claim; have
  the review check it.**

## 4. The rule this suggests

**Audit every favourable condition of a PASS or admission rule by asking which
process produces its evidence.** If the evidence can only be produced by the
process whose misbehaviour the condition is meant to exclude, the condition is
absence-based however it is phrased, and it re-opens the unbounded enumeration
(each new guard is another condition on what the failing process fails to
write). Prefer evidence that is produced by the kernel or by the frozen code's
own terminal action, and **collected by the supervising process after the
child has been reaped**.

The remedy proposed in `AMD-EXP-GFPN-05ff43-20260924-childend` (RG-1) applies
this: each created child's end is recorded as *exec* only if a software task-clock
counter opened by the parent with enable-on-exec shows it was enabled, or as a *frozen pre-exec exit* only if the child's report and exit
status match the frozen code's own `_exit` calls; anything else is
`undetermined` and fails the package, whatever an escaped process wrote. **This
remedy is a draft under review, not a validated technique.** Its reliance on
operating-system semantics (counter enabling at exec, the children listing,
the after-fork callback) is declared and is to be shown on the host by
development checks before any package runs.

## 5. Confidence and limits of the evidence

`reported`, not `established`.

- **One campaign, one experiment, one repair lineage.** The six
  non-converging decisions and the one review are all within
  `EXP-GFPN-05ff43`. That the pattern generalises beyond this lineage is a
  judgement, marked as such.
- **One reviewer.** The review had a single owner per joint, and its context
  was independent of the author in context, authorship and inputs, not in
  model (per the `TASK-20260924-0c2fdc` receipt's session arrangement).
- **FO-1 is a constructed sequence**, reachable only through documented
  interpreter behaviour (asynchronous exceptions delivered at bytecode
  boundaries in a forked child), stated by the reviewer with recalled
  provenance. It is not an observed event.
- **The replacement design has not yet passed its own review.** The fail-closed
  design's success is not shown until a successor passes an independent
  review and its development checks run on delivered code; the note will need
  superseding if that fails.
- **Nothing here is evidence about any mathematical object.** No package of
  the repaired protocol has run.
