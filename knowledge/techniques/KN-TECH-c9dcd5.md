---
id: KN-TECH-c9dcd5
type: technique
title: A development check must be satisfiable in its own development world; a clause that requires a production admission on a package that fails there by design stops every stage by construction, so sweep every development predicate, and every sibling of a repaired clause, before approval
tags: [protocol-amendment, development-check, satisfiability, stop-by-construction, admission, known-answer-control, sibling-clause, differential-check, stop-and-return, governance, methodology]
confidence: reported
complexity: >-
  not a cost model - a pre-approval audit. The operative quantity is, per
  development predicate, whether a layer that implements every rule as worded
  can meet it in the development world where it is evaluated, given that
  world's declared expected failures and missing predecessors
applicability: >-
  every protocol whose implementation stage runs development checks in
  scratch worlds that differ from production (missing predecessor packages,
  checks that are not evaluable there, expected failing checker items),
  before the protocol is approved and before a stage is dispatched
source_refs: [DEC-20260925-8b2bf7, CORR-20260925-ee6929, AMD-EXP-GFPN-05ff43-20260925-admitdev, TASK-20260924-d91a96, TASK-20260925-f0b9f0, TASK-20260925-5842cf, DEC-20260924-daf670, AMD-EXP-GFPN-05ff43-20260924-readbackcover, AMD-EXP-GFPN-05ff43-20260924-failclosed, AMD-EXP-GFPN-05ff43-20260924-childend, TASK-20260924-d897a6, KN-TECH-d45927, EXP-GFPN-05ff43]
proof_status: derivation
proof_refs:
  - ledger/decisions/DEC-20260925-8b2bf7.yaml
  - ledger/corrections/CORR-20260925-ee6929.yaml
  - experiments/EXP-GFPN-05ff43/implementation-v2-r4.md
added: '2026-09-25'
superseded_by: null
---

## What this note is, and is not

A note about **protocol method**, amending `KN-TECH-d45927` by a new entry.
`KN-TECH-d45927` is not edited and is not superseded: its rules stand. Its
refinement (c) lists the stage-time stops by construction that one review
found (seven reading ambiguities) and how to avoid them. This entry adds a
kind that list does not have, which stopped a delivered implementation stage
after every other development check had been recorded as passing.

It is drawn from one experiment of one campaign (`EXP-GFPN-05ff43`,
`GOAL-GFPN-380702`): the r4 stage `TASK-20260924-d91a96`, its preserved outputs
(`TASK-20260925-f0b9f0`) and the ruling `DEC-20260925-8b2bf7`. It is **not** a
finding about any GFPN object, about D, about `H-GFPN-9a29be` or
`HEUR-GFPN-DFLAT`, or about the security of any curve, and nothing in it is a
mathematical result. Its basis is a derivation from rule text, with one
observed instance.

## 1. What happened

A development check (`readbackcover` RB-5 (d)) required that, on copies of a
development package's world, the production admission rule (RB-4) **admit** a
later package when the package's manifest was intact, and **refuse** it when
the manifest's read-back list was emptied. The production rule admits only on
a checker exit 0 for every gate package, with a regression comparison passed.
In any development world:

- the other gate packages do not exist, and the regression comparison is not
  evaluable;
- a later text (`childend` RG-3 (d)) therefore *requires* the checker on every
  development package to fail exactly three regression items.

So the admitting half could not hold on any layer, correct or not. Two earlier
texts had found this root cause and supplied a development reading for a
sibling clause (RB-5 (c), "the r4 checks pass"), and not for (d). An
independent review focused on fail-open and planned-basis refusal, and the
approving decision, did not record it. The stage met the refusal half,
recorded the admitting half as not met, and stopped (`CORR-20260925-ee6929`).

The ruling held the stop: no rule in force read (d) for development worlds,
and choosing a reading after the outcome would have let the outcome decide
what the check meant.

## 2. Rules

**(a) Sweep every development predicate for satisfiability before approval.**
For each check a stage must pass, write the development world it is evaluated
in, that world's declared expected failures and missing predecessors, and
whether a layer implementing every rule as worded can meet it. Give most
attention to checks that assert a **production** admission or verdict on a
development package, and to exact counts copied from an earlier package.
Calibrate the sweep with a **known answer** (here, RB-5 (d) itself, and the
first wording of RF-4 (c), which expected one failing item where there are
three).

**(b) When a text supplies a development reading for one clause, sweep the
siblings.** List every clause that reads the same quantity (here, the
checker's exit status, directly or through the admission rule) and read,
replace or refuse each one in the same text. A reading scoped to one phrase
does not reach a sibling that reads the same quantity through another rule.

**(c) State development admission checks differentially, and exercise the
admitting branch only where admission can hold.** "It refuses when X is
removed" is discriminating only against "the same record without X": require
that the discriminating item appear in the altered copy's admission record and
not in the original's. Exercise "it admits" on a world where every admission
predicate can hold (for example coherent development copies of passing
packages), and check that a wrapper that ignores the verdict, and one that
refuses everything, each fail the pair.

**(d) Stop and return.** Once a stop condition is recorded, run only the check
that protects the repository, write the record, and return. Checks run after
a stop are observations that no ruling can count; they spend the one-shot
checks of the stage without buying anything.

## 3. What remains untested

- **The remedy.** `AMD-EXP-GFPN-05ff43-20260925-admitdev` writes rules (c) and
  (d) as a draft; its zero-run review `TASK-20260925-5842cf` runs rule (a) as
  its first joint. Neither has returned. If the review finds another
  unsatisfiable predicate, or finds the admitting branch unsatisfiable on
  coherent copies, this note needs amending again.
- **Generality.** One lineage; the sweep has not been run on any other
  campaign's protocol.

## 4. Confidence and limits of the evidence

`reported`, not `established`.

- **The defect is a derivation from rule text** (RB-4, RB-5 (d), RG-3 (d),
  with line numbers in `DEC-20260925-8b2bf7` R-1 and R-2); its observed
  instance is the r4 stage's note. The development-evidence bundle holding the
  raw records was not opened by the deciding act.
- **The rules in section 2 are unreviewed.** They are the design of a draft,
  not a validated technique.
- **Nothing here is evidence about any mathematical object.**
