// Decision report for DEC-20261029-8d9b43: second independent review round of EXP-PFDR-bb0d26.
// Source written by the Coordinator. Figures and PDF are rendered by the top-level session
// from graph-data.json in this directory (fig-exclusion.svg, fig-power.svg).
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.7cm), numbering: "1 / 1")
#set text(size: 9.5pt)
#set par(justify: true, leading: 0.55em)
#set heading(numbering: none)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 11pt)
#show raw: set text(size: 8.5pt)

= Second review of EXP-PFDR-bb0d26 (H-PFDR-727bfc): decision `DEC-20261029-8d9b43`

Goal `GOAL-PFDR-fd09e0` · question `RQ-PFDR-ae2fba` · round `BATCH-924d2c` (plan
`coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-924d2c/review-plan.yaml`, opened by `DEC-20261029-8b2734`) ·
evidence `EV-PFDR-28183c` · archive `TASK-20261029-d7284b` · recorded 2026-10-29. First round (merged earlier):
`DEC-20261029-01405d`, `EV-PFDR-07d608`, `KN-FIND-c81e5b`. The two rounds did not see each other.

#table(
  columns: (auto, 1fr),
  stroke: 0.4pt,
  inset: 4pt,
  [*Decision*], [`support`: concurrence with `DEC-20261029-01405d` on the scoped claim. *No status transition.*
    H-PFDR-727bfc stays *supported* and EXP-PFDR-bb0d26 stays *analyzed*, as `DEC-20261029-01405d` recorded.],
  [*Evidence*], [`EV-PFDR-28183c` (second record on the same runs): direction *supports*, strength *preliminary*,
    claim tier *toy*, proof status `empirical_only`.],
  [*Disagreement*], [Strength. `EV-PFDR-07d608` grades the evidence strong; this decision rules preliminary (R-2). It
    decides two correction records, ids pending: CORR-A changes the strength of `EV-PFDR-07d608` to preliminary, and
    CORR-B records that the promotion basis of `KN-FIND-c81e5b` is unmet pending replication (its content is
    unchanged). Rule 12 is not engaged (R-5).],
  [*Runs*], [`RUN-PFDR-e44a19`, `RUN-PFDR-4d8c71`, `RUN-PFDR-243425`, `RUN-PFDR-cd03e2`, `RUN-PFDR-089edc`.],
  [*Reviews*], [J1 blind re-derivation `TASK-20261029-2c7b52` (holds); J2a and J2b `TASK-20261029-e54312` (both
    hold); J3a and J3b with the proves-too-much objects `TASK-20261029-11526b` (J3a breaks on the power clause; J3b
    breaks on wording).],
)

== Exact scoped claim (`EV-PFDR-28183c`, inside `EV-PFDR-07d608`'s)

On generated prime-order ordinary toy curves $E slash FF_p$ with $p$ of 20, 24 and 28 bits (main seed block
8,100,000 + c, $j != 0, 1728$; `RUN-PFDR-4d8c71`, `RUN-PFDR-089edc`), consider $x$-label sets of rank $r <= 3$
log-GAPs built as specified, with independent random base points and injective boxes, of size $256 <= n <= 4096$.
Their pooled pair-sum coincidence count matches that of uniform label sets on the same curves within the per-cell
95% interval at the 44 assessable cells: $|kappa - 1| <= x_c$, with $x_c <= 0.0743$, $x_c <= 0.0052$ at
$n >= 2048$ and $x_c <= 0.0012$ at $n = 4096$. The cell b20-r3-n4096 is not assessable. H1 as operationalised is not
contradicted. The literal random-model statement, label-describability, membership predicates and larger $n$ or $p$
are not addressed. The claim rests on one main seed block.

== Observation

- *Reading.* `RUN-PFDR-089edc` reads O-NULL and `SUPPORT_SCOPED`, with 44 cells null and 1 invalid. Calibration:
  n 44, mean −0.268, sd 0.974. The largest $|z|$ is 3.13. Every interval lies inside $[0.90, 1.10]$ (Figure 1).
- *This round.*
  - J1 re-derives every decision field blind, and none moves across 1536 ambiguity combinations.
  - The mechanical compare against the record makes 353 comparisons at relative 1e-9 with 0 mismatches.
  - J2 replays byte-identically under 3.11.17, recounts 33 jobs by disjoint code and certifies all 1580 curve orders
    with PARI.
  - J3 finds that the flag power at $plus.minus 10%$ is 0.50 at all cells, while P(read null) ≤ 0.0033 (Figure 2).
  - PTM-1 reaches O-STRUCT, and PTM-2 at 1.15, PTM-3 and PTM-5 are flagged.
  - PTM-4a and PTM-4c (label-describable sets) read null at 8/8 cells.
- *Unexpected observations:*
  - 4 degenerate curves at b20-r3-n4096 against 0.73 to 0.89 expected;
  - $sum z^2 = 71.4$ across cells, not coherent across halves;
  - the b28-r1-n256 interval excludes 1;
  - six intervals exclude 1;
  - the counting floor at dense cells.

#figure(image("fig-exclusion.svg", width: 100%),
  caption: [Per-cell $kappa$ with the recorded curve-cluster bootstrap 95% interval (`RUN-PFDR-089edc`), shown
  against 1.0 and the null-class band $[0.90, 1.10]$. Sample size is $n_"curves"$ per cell. The invalid cell is
  marked. The panel of $x_c$ uses a log scale.])

== Comparison with the first round (`REVIEW-PFDR-bb0d26-20261029`)

- *Concurs.*
  - Validity, and the blind and byte-exact reproduction of the reading.
  - The scope: proper log-GAPs, 44/45 cells, $h = 2$ only, the 5% tolerance.
  - The flag-power correction (about 0.50; O-NULL protected).
  - The refusal of the label-describable and KN-OPEN-020 wording.
  - The over-dispersion of $z$ and the six cells with $|z| > 2$.
- *Adds.*
  - Label-describable null controls built as objects (the first round argued the point).
  - Boundary sensitivity objects: PTM-2 at 1.10 and 1.15, PTM-3 and its counting floor, PTM-5.
  - The replication path exercised through O-STRUCT.
  - Per-cell $x_c$ and absolute per-set bounds.
  - A 1536-combination ambiguity sweep.
  - PARI certification of all 1580 curves, 33 recounts (27 with $n >= 1024$) and 31 adversarial kernel cases.
  - The citation-pointer correction and the degenerate-count excess.
- *First round adds.*
  - Exact replay under the recorded 3.11.15, including census-toy-rep.
  - Calibration-gate power.
  - Shared-curve correlation.
  - The missing group-to-label control.
- *Differs.*
  - Strength grade: strong there, preliminary here.
  - This round's pre-committed mapping (a general power shortfall leads to analyzed) was never adopted there.
- *Prior.* J1 and J2 matched the prior. J3a was a miss of magnitude and mechanism, and both rounds' priors missed
  it. J3b matched and was wider than expected.

#figure(image("fig-power.svg", width: 100%),
  caption: [The frozen rule's flag power at a true +10% departure (0.50 at every cell), the power of the $z$
  conjunct alone, the design's claimed 0.95, and PTM-2 at 1.10 empirical rates. Lower panel: P(read null | true
  $plus.minus 10%$) on a log scale (maximum 0.0033). Source: `TASK-20261029-11526b` `power-table.json`.])

== Inference

- *Status.* The status follows the agreed substance. Taken alone, this round's mapping would have recorded analyzed.
  Its premise, that a departure could hide in the null, is refuted by both rounds. A local rule of a round unaware of
  the other does not reverse a valid, reviewed support. So there is no transition (R-3), and the departure is
  disclosed.
- *Strength.* The strength follows the shared hierarchy, in which replicated (an effect reproduced from a clean run)
  ranks below strong. One census, toy scale, a weak calibration gate, a mis-stated flag power and an unexplained
  over-dispersion lead to preliminary, as the precedent `EV-PFDR-f6b76c` did. Reviews reproduce analyses, not runs
  (R-2).
- *Knowledge.* `KN-FIND-c81e5b`'s content is correct and scoped. Its promotion basis is unmet under the promotion
  rule, which CORR-B discloses. A full-grid replication reading O-NULL would regularize it (R-4).
- *Not supported.* F1 to F6 are not supported, and RC-1 and RC-2 stand (`EV-PFDR-28183c`).

== Limitation

- Toy scale, one main seed block and one run set. The cryptographic regime, where E[C] is far below 1, is not
  covered.
- Injective boxes only.
- One model served every session. J1's blindness rests on instruction and a tree without history.
- The independence checker fails on the committed batch only because J1's `sources_read` entries are objects.
- R-2 is a grading judgement against a sibling Coordinator act, made by the composer of the other round. It is
  disclosed as such.
- The PDF exceeds the 64 KiB in-repository limit, so its source and SVGs are archived with a STORE-BLOCKED note.

== Next actions (deduplicated against `DEC-20261029-01405d`; nothing launched)

+ Top-level session: write this round's analysis at `batches/BATCH-924d2c/analysis.md`, render the report,
  validate, and run `TASK-20261029-d7284b` alone without staging the hypothesis file. Then push, open the PR,
  enable auto-merge and checkpoint the goal.
+ Allocate ids for CORR-A and CORR-B, write them, and archive them alone.
+ Widen `DEC-20261029-01405d` NA-2 (replication on block 8,200,000 + c) to the full 45-cell grid. Its amendment
  pre-registers a flag rule below the alternative with correctly computed power, $x_c$ as primary, and the
  unexpected signals as secondaries. Once approved, it runs as `/run EXP-PFDR-bb0d26` under that amendment.
+ Add a seeding-convention relation-rate check to `DEC-20261029-01405d` NA-1 (the degenerate-triple recount).
+ Design $p$-scaling at $n = 256$ (bits 28 upward) for the absolute structural count per set.
+ KN-TECH candidates: conjunction-rule power at the boundary; $kappa$ has no separator for label-describability;
  the counting floor.
+ Ideation on an observable that separates label-describable sets (complements `DEC-20261029-01405d` NA-8).
+ Inputs to `DEC-20261029-01405d` NA-6 and NA-7: the 3.11.17 replay, RC-1 and RC-2. Refresh the lead atlas.
+ Reconcile the independence checker with mapping-form `sources_read`. Handle the export ruling.

Earlier reports (linked, not edited): `experiments/EXP-PFDR-bb0d26/reports/run-20261023T2211Z/`,
`run-20261022T1218Z/` (render-blocked) and `review-DEC-20261029-01405d/`. No canonical graph changes
(`DEC-20261029-8d9b43 visual_record`).
