# TASK-20260729-016 — Independent pre-execution review of the EXP-YIELD-002 contract

**Mirror.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/dispatch_queue.json`.
Where this file and that queue disagree, **the queue governs**.

| | |
|---|---|
| **Role** | reviewer |
| **Depends on** | TASK-20260729-014, TASK-20260729-015 |
| **Archived by** | TASK-20260729-017 |
| **Budget** | 2400 s, 2 GB, `maximum_runs: 1` (runs no experiment) |
| **Inference** | requested policy `review-adversarial`, effort `xhigh`, **independent session required** |

## Objective

Return **PASS or REVISE** on the committed contract **before any draw is made**,
by re-deriving its arithmetic independently and answering five questions:

1. Can the primary criterion actually **fire** at the declared cells — and can
   it **fail** under the counterfactual that the diagnostic is wrong?
2. Are **both** denominator readings pre-registered without ambiguity, and is
   the replicate schedule fixed with its reason?
3. Is the identity-bin treatment **specified**, not declared?
4. Does the contract compute or imply **any** efficiency, yield ratio or
   cost-model consequence anywhere?
5. Does any number in it come from an unarchived source rather than from the
   committed BATCH-011 package at `2fb2bb7a111d999859612e52990eea7dc6bbac1a`?

## Exclusive write scope / artifact paths

- `.../BATCH-012/reviews/TASK-20260729-016/contract_review.yaml` — single
  `verdict` field, `PASS` or `REVISE`; numbered objections marked BLOCKING or
  NONFATAL; any pre-dispatch condition as a numbered, verbatim-adoptable
  sentence.
- `.../BATCH-012/reviews/TASK-20260729-016/feasibility_check.md` — the
  independently re-derived arithmetic.

## Constraints

- **Independent and non-originating**: no shared conversation lineage with
  TASK-20260729-014 and no access to its drafting. State the *basis* of
  independence. **Model independence is not available and must not be claimed**
  (`INT-BATCH012-D`).
- Verify the snapshot commit yourself: reachability, first parent, exact
  changed-path set, content hashes.
- **Re-derive, do not adjudicate by quotation.** Recompute at minimum
  `|S_{m−2}| e^{−C_red/N}`, the single-replicate sd, the SEM at the fixed
  replicate count, and the counterfactual standardized shift, at the four
  failing cells and at passing tuples you choose yourself.
- **Attack the second-order terms by name**: the `(N−1)`-versus-`N` bin-count
  term of order `(1 − e^{−λ})`, the identity bin, the odd-`C_red` rule, and
  pre-marking uniformly at random versus pre-marking the actual `S_{m−2}` set.
  Per term: could the criterion fire on it alone at the fixed replicate count?
  If it could, that is a design defect, not a discovery to be saved for later.
- Check scope creep in both directions, and check `confirmatory_status` is
  `exploratory_only`.
- **Zero curve compute and zero pre-emption. Do not run the repaired null.** Any
  probe outside the repository is labelled UNARCHIVED AND NOT EVIDENCE and no
  conclusion may rest on it — this batch exists because an unarchived claim
  needed archiving.
- Any pre-dispatch condition you impose must be written so the Coordinator can
  record it **verbatim in the TASK-20260729-017 receipt before dispatch**.
  `D-2` is the worked example of what happens when that recording is skipped.
- Distinguish absence of evidence from impossibility; declare no direction
  impossible. Change no official state. **Make no commit.**
- REVISE is admissible; it blocks only execution and permits at most one
  amendment cycle under `RC-12`, opened by a recorded QUEUE-AMEND.
- Bounded card: work gates in order, name what you did not reach. **`R1` must be
  reached; if it is not, the verdict defaults to REVISE.**

## Completion gate

`R1`–`R8` as listed in the queue entry.
