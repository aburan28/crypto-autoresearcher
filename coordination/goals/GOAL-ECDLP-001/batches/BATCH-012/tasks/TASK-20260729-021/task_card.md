# TASK-20260729-021 — Independent red-team review of the EXP-YIELD-002 result

**Mirror.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/dispatch_queue.json`.
Where this file and that queue disagree, **the queue governs**.

| | |
|---|---|
| **Role** | red-team |
| **Depends on** | TASK-20260729-018, TASK-20260729-019 |
| **Archived by** | TASK-20260729-022 |
| **Budget** | 2400 s, 2 GB, `maximum_runs: 1` (no experimental run) |
| **Inference** | requested policy `review-adversarial`, effort `xhigh`, **independent session required** |

## Objective

Try to falsify the reading this result invites, **in whichever direction it
points**.

- **If the repaired null landed on `P_pred`**: attack the inference that this
  confirms the BATCH-011 diagnostic, and police every sentence that would
  over-read it into a statement about decomposition yield.
- **If it missed**: attack the inference that the VOID is therefore a
  measurement fault, and police every sentence that would over-read a simulator
  defect into a refutation of `P_pred`.

## Artifact paths

- `.../BATCH-012/reviews/TASK-20260729-021/red_team_report.yaml` — numbered
  objections, each BLOCKING or NONFATAL, plus a `required_controls` list for
  anything left undischarged, each with a resume condition.
- `.../BATCH-012/reviews/TASK-20260729-021/falsification_review.md` — the
  pre-stated narrowest sentence per outcome and the named refutation artifact.

## Constraints

- **Independent session**: no shared lineage with TASK-20260729-014, -016, -018
  or -020. **Model independence is not available and must not be claimed**
  (`INT-BATCH012-D`). Review only durable committed artifacts and verify the
  snapshot commit yourself.
- **Police the prohibitions by name — this is the batch most likely to breach
  them.** Nothing here may un-fire or re-dispose `INV-4`; nothing may compute or
  quote any efficiency `E`, any yield ratio, or `E ≈ 0.85`, as a measurement;
  nothing may move `H-YIELD-001` or `H-STR-002` in either direction; nothing may
  determine `INV-5`; nothing may touch, re-charge, flag or defend any cost model
  — the counterfactual branch is **`O-6`, not `O-4`**, and even a fully repaired
  null yields no cost-model consequence. Name any sentence that comes close.
- **Attack the hit, if there was one.** A repaired control landing on its own
  prediction is the *least* surprising possible outcome of a derivation two
  sessions already checked arithmetically. State what it adds beyond the
  derivation, whether the agreement could be produced by a simulator built to
  reproduce the formula it is tested against, and what would have had to happen
  for the test to fail.
- **Attack the miss, if there was one, just as hard.** Before any record
  concludes `P_pred` is wrong, enumerate the alternatives — simulator defect,
  bin-accounting difference from the BATCH-011 process, a second-order term at
  the fixed replicate count, seed pathology, a mis-resolved per-cell quantity —
  and mark each EXCLUDED or NOT EXCLUDED by the package. A miss on a single
  unreplicated curve-free run set licenses no `reject_scoped` on anything.
- **Pre-state the narrowest supported sentence for each outcome** — hit, miss,
  and mixed across cells or across denominator readings — each verbatim-adoptable
  and each with the decision label it would justify. `reject_scoped` on a single
  unreplicated empirical-only run set is forbidden; the correct pair is `weaken`
  plus a named replication.
- Name the strongest available refutation artifact in the order counterexample
  certificate → derivation note → declared `empirical_only`, and say which this
  batch can actually produce. An undeclared basis is the failure, not the lack
  of a proof.
- **Pareto honesty** where any reading could be taken as favourable:
  `dominated_by` and a quantitative `sota_delta`, with the frontier rows
  actually checked listed. An unchecked `dominated_by: null` is a fabrication
  under core rule 9.
- Distinguish absence of evidence from impossibility. **Declare no lane dead** —
  the decomposition-yield question remains open whatever this batch returns.
- Zero curve compute beyond hand arithmetic. Change no official state. **Make no
  commit.** Name every objection line not reached inside the cap.

## Completion gate

`T1`–`T9` as listed in the queue entry.
