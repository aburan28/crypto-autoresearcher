#set page(paper: "a4", margin: (x: 1.6cm, y: 1.6cm))
#set text(size: 9.5pt)
#show heading: set text(size: 11pt)

= Run report: EXP-ENDO-0e622b / RUN-ENDO-f461e9

*Combined-route re-run with the input-format term charged.* This report records observations only. It gives no verdict; the evidence review decides that.

== Identity
- *Records:* experiment `EXP-ENDO-0e622b`, a replication of hypothesis `H-ENDO-f58749` under `DEC-20261016-4f3a1a` (replicate), with correction `CORR-20261016-ac9fc8`; approval `DEC-20261016-77dce3`; goal `GOAL-ENDO-001`.
- *Tasks:* executor `TASK-20261016-1b6023` (claimed, released `completed`); snapshot `TASK-20261016-85eb9e`.
- *Run directory:* `experiments/EXP-ENDO-0e622b/runs/RUN-ENDO-f461e9/`.
- *Code:* commit `f8c927854cc9ff6053238ee3ceaa1d109195cb50`, `repository_dirty: false` (harness only).
- *Timing:* started 2026-10-16T21:34:27Z; wall 75.5 s (measured).

== What ran
- *Launcher:* `tools/experiment_execution.py run` on the frozen plan, which runs `python -m harness.endosweep.isoglv` with the frozen arguments of EXP-ENDO-7494e7.
- *Same inputs:* the same source rows (`0576225d…`) and the same two controls.
- *The one code change:* `input_format_cost` adds, to each combined route's one-shot cost, the cheaper of two evaluations of the GLV chain on the forward map's Jacobian image:
  - (a) the chain on the Jacobian input;
  - (b) E's chain on the affine P, then one more forward pass.
- *Outcome:* trials 1 requested, 1 completed; coverage `output_validated`. `check.py`: "ok: 9 rows, 0 with recorded errors"; it also fails if a combined route lacks the term.
- *Units:* modelled M_eq = M + S counts (curvesweep, S = 1 M). Gains are derived as 1 − arm / reference from recorded values.

== Graph
#figure(image("oneshot.svg", width: 100%), caption: [RUN-ENDO-f461e9, recorded rows, beside RUN-ENDO-795989's one-shot column and the frozen one-shot prediction (black, ±0.02 points). Single deterministic run; no spread.])

== Recorded values (combined route vs 2-GLV on E)
#table(columns: 8, inset: 3pt, stroke: 0.4pt + luma(200), align: (left, right, left, right, right, right, right, right),
  [*curve*], [*input-format M_eq*], [*evaluation charged*], [*alternative*], [*persistent*], [*one-shot, RUN-ENDO-795989*], [*one-shot, this run*], [*frozen prediction*],
  [GOST 2001 test], [32], [E's chain on P, then forward], [47], [+5.955 %], [+3.705 %], [+2.204 %], [+2.20 %],
  [mnt/mnt3/1], [29], [chain on Jacobian input], [32], [+11.033 %], [+7.760 %], [+5.782 %], [+5.78 %],
  [mnt/mnt3/3], [29], [chain on Jacobian input], [32], [+11.033 %], [+7.760 %], [+5.782 %], [+5.78 %],
  [mnt/mnt5/2], [32], [E's chain on P, then forward], [47], [+11.302 %], [+9.050 %], [+7.549 %], [+7.55 %],
  [mnt/mnt5/3], [32], [E's chain on P, then forward], [47], [+11.302 %], [+9.050 %], [+7.549 %], [+7.55 %],
  [other/Tom-384], [29], [chain on Jacobian input], [32], [+11.844 %], [+10.359 %], [+9.463 %], [+9.46 %],
)

== Other recorded observations
- *Combined nodes:* path and j are the same as RUN-ENDO-795989 on every row. All persistent figures are identical to RUN-ENDO-795989. Every combined route is verified on 8 scalars.
- *Combined route vs E's model, one-shot:* GOST +31.93 %, mnt3 +34.32 %, mnt5 +36.93 %, Tom-384 +40.61 %.
- *Controls:*
  - The ascent control reaches the j = 0 crater over one degree-11 step. Its input-format term is 0 (unit endomorphism), and its combined vs E's model is persistent +36.43 %, one-shot +32.57 %, as before.
  - mnt/mnt5/1 has 0 cheaper-class candidates and no combined route.
- *BADA55-VPR-224:* no |D_K| ≤ 2·10#super[6], so no GLV arm.

== Missing or out of scope
- No timing.
- No f_E certification for any neighbour. Route (b) relies on the edge being horizontal, which the independent validator checked in TASK-20261016-35d324 §A3; this run does not re-certify it.
- The six population rows are four isogeny classes.
- Peak memory is not recorded.
- The prediction was written after RUN-ENDO-795989 was seen (disclosed in DEC-20261016-77dce3).

== Files
`plot.py` draws `oneshot.svg` from `runs/RUN-ENDO-f461e9/raw-result.json` and `../EXP-ENDO-7494e7/runs/RUN-ENDO-795989/raw-result.json` only.
