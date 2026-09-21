# TASK-20260729-048 — Ledger archive: EV-STR-004, DEC-20260729-004, the goal checkpoint and both review artifact pairs

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-014 `dispatch_queue.json`. Where they disagree, the queue governs.

- **Role:** coordinator (archival task — **runs alone**)
- **Depends on:** TASK-20260729-046, TASK-20260729-047
- **Archive kind:** ledger; `source_task_ids: [TASK-20260729-046, TASK-20260729-047]`
- **Budget:** 2400 s, 2 GB

## Declared commit set — 8 paths by default

```
.../BATCH-014/reviews/TASK-20260729-046/validation_report.yaml
.../BATCH-014/reviews/TASK-20260729-046/recount_note.md
.../BATCH-014/reviews/TASK-20260729-047/red_team_report.yaml
.../BATCH-014/reviews/TASK-20260729-047/falsification_review.md
.../BATCH-014/archives/TASK-20260729-048/ledger_commit_receipt.json
ledger/evidence/EV-STR-004.yaml
ledger/decisions/DEC-20260729-004.yaml
ledger/goals/GOAL-ECDLP-001.yaml
```

**This commit is the FIRST commit that may contain the TASK-20260729-046 and
TASK-20260729-047 artifacts.** The dispatching session committed the
post-execution review artifacts one commit early in **BATCH-012 and again in
BATCH-013** — a third occurrence is a pattern. If they are nevertheless already
committed, record it as an **integrity note in the receipt** and do **not**
enlarge or shrink the declaration after the fact.

**Conditional additions, each only by a recorded QUEUE-AMEND enlarging the
declaration *before anything is staged*:** `ledger/hypotheses/H-STR-002.yaml`
(only if the decision moves it) and `knowledge/findings/KN-FIND-010.md` +
`knowledge/INDEX.md` (only if promotion is warranted; `KN-FIND-010` is reserved
and uncreated; regenerate the index with `tools/build_knowledge_index.py`).
**The declared set and the committed set are made equal by amending the
declaration first — never by committing a different set.**

## Order of work

1. **Verify validity before interpreting anything**, and record the verdict in
   its own field: run count, manifest schema completeness, instance and seed
   integrity, raw-to-summary agreement, control comparability **including the
   matched base-row budget**, and independent certificate verification. **If the
   validator set `blocks_ledger_record: true`, do not write a decision — record
   the block and stop.**
2. A timeout, crash, memory or disk exhaustion, missing Sage binary or
   implementation failure is **infrastructure signal, never a negative
   mathematical result**. If the batch failed on infrastructure,
   **DEFER-BATCH009-001 survives intact** and the decision says so.
3. Take the decision label from the `docs/task-lifecycle.md` section 9
   vocabulary and justify it against every alternative. **If the evidence cannot
   discriminate between explanations, the decision is `inconclusive` and saying
   so plainly is the required outcome.** Under the contract's `mixed` or
   `incomplete` verdict the instrument question is `inconclusive` by the frozen
   rule.
4. **`reject_scoped` on a single unreplicated empirical-only run set is
   forbidden.** Anything stronger than `weaken` names its archived refutation
   artifact and its class. The derivation note was committed **three commits
   earlier**, so the ordering is satisfiable for what the note actually derives;
   anything it does not reach is `empirical_only` and is declared as such. **An
   undeclared basis is the failure, not the lack of a proof.**
5. **Rule explicitly on DEFER-BATCH009-001 in its own field** — DISCHARGED or
   NOT DISCHARGED, with the receipts named. Discharge is a procedural fact and
   **is not itself a result**.
6. H-STR-002 moves **only** if the evidence moves it and the decision says why;
   its `status_history` is **appended by supersession, never overwritten**.

## The ceiling binds this record

Claim tier **toy**. **No statement about H-STR-002's mechanism in either
direction** — phi is an automorphism, phi(R) is a genuine relation whenever R is
and F is phi-invariant, and no arm tested any of that. No asymptotic or scaling
claim from fourteen toy cells. Nothing about `B > 193`, `field_bits > 16`,
`j != 0` curves, generic curves, `m > 3`, or medium/cryptographic scale. No cost
claim and no matched baseline. **RT-CM-1 to RT-CM-6 remain OPEN** and must not
be described as settled, tested or addressed. No exponent moves; all four
promotion gates remain OPEN; no closure quorum is claimed or claimable.

If the record touches the relation-density penalty at all it quotes the **full
range 17.5x–4128.6x** and never 17.5x alone. Do not quote the C-20 power
sentence unaccompanied by the RT21-1 correction. Do not state or imply that the
ledger validates.

## Carry forward

Every item of the queue's `carried_defects_not_repaired_by_this_batch`, into
`DEC-20260729-004`'s own carried-defects block, unretracted and undescribed as
fixed: RT21-1; RT21-8/DEV-4; **O-4 component (d)** with its permanence under
INT-BATCH014-K; RC-F; RC-B; the five `SUP-BATCH013-*` supersessions;
INT-BATCH007-T; INT-BATCH012-D and -F; the two duplicated immutable identifiers;
the two unrenderable queues; the TASK-20260729-012 overrun; D-1 and D-2;
`DEFER-BATCH011-001`…`-005`; and EV-STR-003's UC-3 to UC-7 with the note that
**only UC-6 is repaired prospectively**.

Carry `RULE-BATCH014-SCOPE` into the ledger (INT-BATCH014-J), including which of
`RULE-BATCH013-SCOPE`'s three options this batch took, the ruling that the
instance sweep is compatible with *two arms and nothing else*, and
**INT-BATCH014-K**: the EXP-YIELD instrument lineage is CLOSED and O-4 component
(d)'s census-facing claim therefore remains untouched and unarchived on the
current record.

## Goal checkpoint

Exactly **one** `next_action`, the prior value preserved **verbatim by
supersession**. `maximum_batches = 14` is CONSUMED at this close; the first
pause condition fires again on its own terms unless a completion criterion is
met; **a fifteenth batch requires its own budget amendment on explicit user
authorization — do not self-grant one.** Record that the branch was **five
commits behind `origin/main`** at the BATCH-014 opening and that currency is
restored by **merging, never rebasing**.

## Mechanics

Run alone; check for a stale `.git/index.lock` and record what you found (a
zero-byte lock with no live git process is reported and stops the card, never
deleted silently). Stage exactly the declared paths; nothing under
`experiments/` or `harness/`; never `tools/validate_ledger_baseline.txt`; no
AppleDouble sidecar. `yaml.safe_load` everything you write and check every
scalar for the space-hash truncation defect and for a mapping key at the indent
of an open block sequence's entries. **Bind all 28 `run_ids` explicitly in
EV-STR-004** — `EV-IC-001`, `EV-STR-002` and `EV-GGM-001` all carry
`run_ids: []` against AGENTS.md rule 10. The commit message names
TASK-20260729-048, EV-STR-004, DEC-20260729-004, GOAL-ECDLP-001 and BATCH-014
literally and **states no disposition the record does not carry**. This receipt
lands in the immediately following commit (INT-BATCH007-T). An unfinished git
verification is reported as unfinished. **Fabricate nothing.**
