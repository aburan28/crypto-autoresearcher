# Coordinator: which commit carries each artifact the ledger decision rests on

Author: orchestrating session. Written at the ledger archive's explicit request — it noted that
DEC-20260823-839fc6's `reject_scoped` rests on derivation notes living inside the review
artifacts, and that the ORDERING requirement is unverifiable from a role with no shell.

## Provenance of the 12 bound paths

| commit    | artifact |
|-----------|----------|
| ded942f32 | `review_plan.yaml` (the recorded priors) |
| 95d2a58ec | `CORRECTION-predeclared-target-values.md` |
| b07a88cc5 | `COORDINATOR-multimetric-check.md` |
| 0cb016502 | `COORDINATOR-open-items-settled.md` |
| 4e20aa677 | `orchestrator_path_sha256.json` (derived hash set) |
| ac5f28d6d | `redteam_report.md`, `objections.yaml` |
| edb41cbaf | `validation_report.md`, `verdict.yaml` |
| (this commit) | `EV-ECQ-cbc837.yaml`, `DEC-20260823-839fc6.yaml`, `BATCH-da59ec.yaml` |

## The ordering requirement is SATISFIED, and here is why that is checkable

The decision must rest on reviews that already existed, not on reviews written to fit it. The
git history establishes this without anyone's say-so:

  review_plan.yaml          ded942f32   committed BEFORE the producer was dispatched
  red team artifacts        ac5f28d6d   committed BEFORE the validator returned
  validator artifacts       edb41cbaf   committed BEFORE the ledger archive was dispatched
  EV / DEC / checkpoint     THIS commit  strictly after all of the above

`git merge-base --is-ancestor` confirms each of ac5f28d6d and edb41cbaf is an ancestor of this
commit. So every derivation the decision cites was durable before the decision existed.

## The blind-round guarantee is also checkable, and it is the stronger claim

`ac5f28d6d` (red team) landed while the validator was still running, and its commit message
deliberately carries NO content — it says only that an artifact landed. `edb41cbaf` (validator)
is likewise contentless, written while its own verdict was still forming. Anyone auditing this
batch can run `git log` over that window and confirm that no reviewer's findings were readable
to the other through commit messages. That discipline exists because GOAL-ECQ-001 leaked exactly
that way (BI-1), and in BATCH-da59ec the validator disclosed it had glimpsed the sibling commit's
SUBJECT and file names while debugging its own git state — the contentless message is precisely
why that glimpse carried no findings.

## What this note does NOT establish

It shows the artifacts existed in the right order and that commit messages leaked nothing. It says
nothing about whether the reviews are CORRECT — that is what the reviews themselves argue, and two
of their central findings (the ceiling of 15, the 1248^2 transcription) were independently
reproduced by the orchestrating session and are recorded as such in the decision.
