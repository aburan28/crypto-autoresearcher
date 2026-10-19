#set page(paper: "a4", margin: (x: 1.6cm, y: 1.6cm))
#set text(size: 9.5pt)
#show heading: set text(size: 11pt)

= Run report: EXP-ENDO-7494e7 / RUN-ENDO-795989

*Combined route: 2-GLV on a cheaper-model isogenous neighbour.* This report records observations only. It makes no verdict; support, weakening, significance and priority belong to the evidence review.

== Identity
- *Records:* experiment `EXP-ENDO-7494e7`, hypothesis `H-ENDO-f58749`, approval `DEC-20261016-00e9cd`, goal `GOAL-ENDO-001`. Source rows come from `RUN-ENDO-d7cb69` (sha256 `0576225d…`, checked by `run.py`).
- *Tasks:* executor `TASK-20261016-c886b3` (claimed, released `completed`); snapshot `TASK-20261016-d4363d`.
- *Run directory:* `experiments/EXP-ENDO-7494e7/runs/RUN-ENDO-795989/`.
- *Code commit* `c45d9a5969a19e7646511f6806f7ac0a02d972e4`. The manifest records `repository_dirty: true`: at launch, `harness/endosweep/isobench/` existed untracked. It is not imported by this run; independent validation `TASK-20261016-35d324` checks this.
- *Timing:* started 2026-10-16T19:42:21Z; wall time 74.7 s (measured); single process.

== What ran
- *Command:* `tools/experiment_execution.py run` on the frozen plan, which runs `python -m harness.endosweep.isoglv` with these parameters:
  - `--ells 2,3,5,7,11,13 --depth 2 --max-nodes 64 --disc-bound 2000000`
  - `--build-limit 3 --build-seconds 900 --max-candidates 12 --verify-scalars 8 --seed 20261016`
  - two controls via `--include`.
- *Outcome:* trials 1 requested, 1 completed. Coverage `output_validated`. `check.py`: "ok: 9 rows, 0 with recorded errors".
- *Arms* (all modelled M_eq = M + S in `curvesweep`'s model):
  - *GLV on E:* `curvesweep.sweep_curve` on E.
  - *Model change:* copied from RUN-ENDO-d7cb69.
  - *Combined:* `sweep_curve` on the cheapest-conversion neighbour with a cheaper Weierstrass class on which the cheapest chain element builds and passes curvesweep's GLV-2 point check. Conversion (48 M_eq for one degree-5 step) is added for the one-shot column, and the route is verified with `isomodel.verify_route` on 8 scalars.
- *Derived gains:* each is 1 − arm / reference, computed from the recorded values.

== Graph
#figure(image("arms.svg", width: 100%), caption: [RUN-ENDO-795989, recorded rows only. One-shot modelled cost per arm on the six population curves with a small D_K, plus the negative control mnt/mnt5/1 (no cheaper neighbour, so no combined bar). Single deterministic run; no spread recorded.])

== Recorded values (one-shot unless stated)
#table(columns: 9, inset: 3pt, stroke: 0.4pt + luma(200),
  align: (left, right, right, right, right, right, left, right, right),
  [*curve*], [*D_K*], [*E model*], [*model change*], [*GLV on E*], [*combined*], [*attempts (path: built)*], [*combined vs GLV on E, persistent*], [*one-shot*],
  [GOST 2001 test], [−915], [3063.9], [2858.7], [2132.5], [2053.5], [5: yes], [+5.96 %], [+3.71 %],
  [mnt/mnt3/1], [−139], [2103.7], [1836.6], [1466.5], [1352.7], [5: no, 5: no, 5: yes], [+11.03 %], [+7.76 %],
  [mnt/mnt3/3], [−139], [2103.7], [1836.6], [1466.5], [1352.7], [5: no, 5: no, 5: yes], [+11.03 %], [+7.76 %],
  [mnt/mnt5/2], [−211], [3124.4], [2696.2], [2131.4], [1938.5], [5: no, 5: no, 5: yes], [+11.30 %], [+9.05 %],
  [mnt/mnt5/3], [−211], [3124.4], [2696.2], [2131.4], [1938.5], [5: no, 5: yes], [+11.30 %], [+9.05 %],
  [other/Tom-384], [−619], [4929.5], [4213.8], [3233.8], [2898.8], [5: yes], [+11.84 %], [+10.36 %],
  [mnt/mnt5/1 (control−)], [−211], [2648.2], [2696.2], [1890.5], [–], [none (0 candidates)], [–], [–],
  [control+ ascent], [−3], [2796.5], [2652.5], [–], [1885.8], [11: yes], [vs E model +36.43 %], [+32.57 %],
  [other/BADA55-VPR-224], [none ≤ 2·10#super[6]], [2922.8], [2588.4], [–], [–], [not run (no GLV arm)], [–], [–],
)
- The model-change column is RUN-ENDO-d7cb69's `oneshot_M_eq`, so it includes its own conversion.
- The combined column is the neighbour's 2-GLV M_eq plus 48.0 M_eq of conversion.
- Recorded `model_change_vs_glv_on_E` (one-shot) on the six curves ranges from −25.2 % to −34.1 %.

== Controls (recorded outcomes)
- *control+ascent:* the walk reached the j = 0 crater over one degree-11 step. Unit 2-GLV was priced there, and the route was verified on 8 scalars. Against E's own model: persistent +36.43 %, one-shot +32.57 %.
- *mnt/mnt5/1:* already isomorphic to an a = −3 model. It recorded 0 cheaper-class candidates and no combined route. Its own GLV on E was 1890.5.

== Other observations
- On every small-D_K population curve, the combined route was found on a degree-5 neighbour and verified on 8 scalars.
- On four curves (mnt3/1, mnt3/3, mnt5/2, mnt5/3), one or two earlier degree-5 neighbours did not build the chain. In those four, 5 divides f_π.
- The neighbour's GLV cost equals the recorded GLV on E of the a = −3-isomorphic sibling in the same family: mnt3 1304.7 = mnt3/2's figure in `research/endosweep_curves_20261006`, and mnt5 1890.5 = mnt5/1. This is an observation, not an identity check.

== Missing or out of scope
- No timing in this run; the timed comparison is EXP-ENDO-33a1ee and covers BADA55-VPR-224 only.
- The conductor f_E of each neighbour is not certified.
- A failed chain build is recorded as an edge observation, not as evidence about End.
- Peak memory is not recorded.

== Files
`plot.py` draws `arms.svg` from `runs/RUN-ENDO-795989/raw-result.json` only.
