# CORRECTION: two PRE-DECLARED target values in H-ECQ-a609f8 do not match the frozen baseline

Raised by: TASK-20260823-f88f54 (executor), as a flagged anomaly.
Confirmed by: orchestrating session (Coordinator), independently, before any archive.
Fault: THE COORDINATOR'S. Not the producer's, and not the reviewers'.
Status: RECORDED. H-ECQ-a609f8 is committed and immutable; this supersedes, it does not overwrite.

## The discrepancy

`ledger/hypotheses/H-ECQ-a609f8.yaml` pre-declares three target cells. Two of the three
`incumbent` values were transcribed wrongly from
`coordination/goals/GOAL-ECQ-002/baseline/frontier_20260823.json`:

| target | frozen baseline      | pre-declared in H-ECQ-a609f8 | delta      | match |
|--------|----------------------|------------------------------|------------|-------|
| r>=12  | 69.33884136527462    | 69.33878142645636            | -5.99e-05  | NO    |
| r>=13  | 75.76026257010892    | 75.75973380404125            | -5.29e-04  | NO    |
| r>=14  | 85.18925824647027    | 85.18925824647027            |  0.00e+00  | YES   |

Curve ids (157, 158, 244) and submitters agree in both places; only the height values differ.
The frozen snapshot `118db069...cadc59` is unchanged and remains authoritative.

## Why it matters even though it changes nothing here

It changes no conclusion. The measured minimum naive height for Nagao in the declared box is
109.505165, so the gaps to target are +40.166, +33.745 and +24.316 — four to five orders of
magnitude larger than the transcription error. Every box is empty by an enormous margin and would
be empty under either set of numbers.

It matters anyway. The ENTIRE POINT of pre-declaring a target is that the number cannot move
afterwards. A pre-declared value that does not match its own frozen source is not pre-declared in
any meaningful sense — it is a number I typed. Had the result been close, this error would have
been indistinguishable from moving the goalposts, and no reviewer could have shown otherwise. The
discipline is worth nothing if it is only checked when the answer is inconvenient.

## What the producer did, which was right

It used the PRE-DECLARED values as the gate, not the baseline values, because those were the
stricter of the two (all three pre-declared values are LOWER, hence harder to clear). It did not
edit either file, did not reconcile them silently, and flagged the discrepancy for a Coordinator
correction. That is the correct handling of a contradiction between two committed records.

## Disposition

- The frozen baseline `frontier_20260823.json` is authoritative for every cell value in this
  campaign. Where H-ECQ-a609f8 disagrees, THE BASELINE WINS.
- H-ECQ-a609f8 is NOT edited. A superseding hypothesis, if one is written for the next batch,
  must take its target values by COMPUTATION FROM the frozen baseline file rather than by
  transcription, and must record the sha256 of the file it read them from.
- The ledger archive TASK-20260823-0a2461 must carry this correction into the evidence and
  decision records rather than treating it as a producer anomaly. It is a Coordinator defect and
  belongs in the same list as the missing `review_plan` of BATCH-f2341e and the three too-narrow
  declared artifact sets.

## Root cause, stated plainly

I typed three floats into a hypothesis by hand when a two-line script could have read them from
the file I had already frozen for exactly this purpose. The same class of error — hand-listing
what should have been derived — has now produced the too-narrow artifact sets, and the snapshot
archive already logged the general fix: DERIVE, DO NOT TRANSCRIBE.
