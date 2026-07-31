# TASK-20260730-039 — Red team — Falsification and scope review

> **NON-AUTHORITATIVE MIRROR.** The authoritative card is the `tasks[]` entry
> for `TASK-20260730-039` in
> `coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/dispatch_queue.json`.
> Where this mirror and that queue disagree, **THE QUEUE GOVERNS**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-016
- **Role:** red-team · **depends_on:** TASK-20260730-037 · **archived by:**
  TASK-20260730-040
- **Budget:** 1800 s, 2 GB, maximum_runs 1 ·
  `independent_session_required: true`
- **Runs concurrently with TASK-20260730-038.** Neither touches the Git index.

## Objective

Attack the mutation test and the reading that will be made of it.

Build the strongest case that **the three mutations are too easy** — that they
break the checked identity so directly that a FAIL on them establishes almost
nothing about whether CTRL-4 would catch a realistic corruption — and that a
FAIL on cases (2) and (3) must not be allowed to **rehabilitate** a control
BATCH-015 already showed to be a constructor identity.

Then state plainly what disposition of CTRL-4 the outcomes support — **RETIRE or
REWRITE** — and record what would falsify your own recommendation.

## Re-execute something yourself

Your predecessor found the BATCH-015 defect not by reading but by **re-executing
the committed builder with a bogus `zeta3` and watching the assertion pass.** Do
the equivalent: construct at least one mutation of your own that the queue did
not specify, run it read-only against the committed checker, and report it as a
**RED-TEAM DIAGNOSTIC, not as a batch measurement and not as evidence.**

## Standing findings you must not reopen or let be reopened

BATCH-015 established that CTRL-4 condition (ii) is a constructor identity and
that the assertion passes with a non-cube-root `zeta3`. **That finding is
committed and is not reopened in either direction.** Flag as BLOCKING any
artifact or draft reading that treats a case (2) or (3) FAIL as evidence that
the factor base is phi-invariant or that CTRL-4 is informative.

Check that **case (1) is not recorded as a new result** and **case 0 is not
recorded as a result**. Flag either as BLOCKING.

DEC-20260729-004, DEC-20260730-031, EV-STR-005, the REVISE contract review, the
NOT-APPROVED determination on EXP-STR-004 and the QUEUE-AMEND-20260729-005
stand-down are **committed facts, carried and not reopened.**

## Required outputs

- **Claim-ceiling audit item by item**, naming the specific sentences a
  successor is likely to write that *would* breach it.
- **A recommended CTRL-4 disposition — RETIRE or REWRITE — with its reason and
  its falsifier.** If you recommend rewrite, state the rewritten assertion
  precisely enough that a successor could freeze it, **and pre-state the mutation
  test it would have to pass.**
- **Required controls for successors**, each with `should_it_be_dispatched`
  answered honestly and **at least one you would refuse**, so your
  recommendations are falsifiable.

## Hard prohibitions

- **You may not enlarge BATCH-016.** Any control you name is for a successor.
  Recommend no approval of EXP-STR-004.
- **Modify nothing under `harness/`.** Your diagnostics are read-only calls into
  committed code with mutated arguments and mutated returned lists.
- **Mint no `RT-*` identifier.** INT-BATCH014-N establishes that every RT
  identifier check in this program has been vacuous and that RT-20260729-036 is
  a dangling reference that must never be issued. Cite your report by path and
  task id only, and say so in its own text.
- **Make no commit.** Write nothing outside your review directory; your files
  must not be committed before the TASK-20260730-040 ledger commit.
- Session independence is required and asserted separately. **Model
  independence is not available and is never claimed (INT-BATCH016-D).**
- Bounded card: 1800 s. If you cannot finish, **stop and report a bounded
  partial review** naming exactly which checks you did not reach.

## Deliverables

- `red_team_report.yaml` — numbered objections with severities; at least one
  self-run diagnostic mutation labelled a diagnostic; recommended CTRL-4
  disposition with its falsifier; required controls with honest
  `should_it_be_dispatched` answers including at least one refusal; explicit
  claim-ceiling audit
- `falsification_review.md` — the argument in prose, including the strongest
  case that the three mutations are too easy and the strongest case against your
  own recommendation

## Completion gate

G1–G9 as stated in the queue entry.
