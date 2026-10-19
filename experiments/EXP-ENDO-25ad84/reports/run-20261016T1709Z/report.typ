#set page(paper: "a4", margin: (x: 1.6cm, y: 1.6cm), flipped: false)
#set text(size: 9.5pt)
#set par(justify: false)
#show heading: set text(size: 11pt)

= Run report: EXP-ENDO-25ad84 / RUN-ENDO-d7cb69

*Isogenous-model scalar-multiplication screen.* This report is descriptive. It records what the run produced and makes no verdict. Support, weakening, significance and priority belong to the evidence review (`/review-evidence`).

== Identity
- Experiment `EXP-ENDO-25ad84`, hypothesis `H-ENDO-5a33ae`, proposal `IDEA-20261016-15a6fc`, question `RQ-ENDO-476761`, goal `GOAL-ENDO-001`, approval `DEC-20261016-5cd7e2`.
- Executor task `TASK-20261016-3a809b` (claim epoch 1, released `completed`). Snapshot task `TASK-20261016-cbf19d` (not yet run).
- Run directory: `experiments/EXP-ENDO-25ad84/runs/RUN-ENDO-d7cb69/`.
- Code commit `5ce480a42265e2591c41ae6bf697839a36e2d887`, `repository_dirty: false` (manifest).
- std-curves `77fe6e3585ca2c2225b59d7df24b7c775437276f`.
- Python 3.13.16, python-flint 0.9.0, sympy 1.14.0, Linux x86_64 (cloud container). Single process.

== What ran
- Command: `tools/experiment_execution.py run` on the frozen `trial-plan.json`, launching `implementation/run.py`, which runs `python -m harness.endosweep.isomodel` with these frozen parameters:
  - `--ells 2,3,5,7,11,13 --depth 2 --max-nodes 64 --disc-bound 1048576`
  - `--samples 200 --verify-scalars 8 --max-bits 521 --seed 20261016`
- Trials requested 1, completed 1, failed 0, timed out 0. Executor coverage: `output_validated`.
- `check.py`: "ok: 136 rows, 0 with recorded errors" (it recomputes both constructed control rows).
- Wall time 4,296.5 s (manifest `wall_seconds`, measured). CPU time not recorded.
- Rows: 136 = 132 population curves (the verified prime-field registry plus std-curves, deduplicated by (p, j, n)) + 2 constructed positive controls + 2 negative controls (NIST P-256, Curve25519). Error rows: 0.

All costs below are *modelled* operation counts from `curvesweep`'s wNAF model. The figure is M_eq = M + S, with the best of the affine/Jacobian table at widths 3–7, averaged over 200 random scalars, so the S = 1 M weighting is the primary column. They are not timings.
- *Persistent* gain = 1 − (neighbour M_eq / best M_eq on E).
- *One-shot* gain additionally charges the forward chain, the dual chain, the model maps and the scalar adjustment k' = k·deg⁻¹ mod n.
- Percentages are derived as 100 × the recorded fraction.

== Graph
#figure(image("gains.svg", width: 100%), caption: [RUN-ENDO-d7cb69, recorded rows only.
Left: the cheapest model each of the 132 population curves already has on E.
Right: the best persistent (blue) and one-shot (orange) modelled saving, over the four controls and the nine population curves whose own cheapest Weierstrass class uses generic doubling.
Single deterministic run (seed 20261016, 200 scalars per cost); no spread was recorded.])

== Recorded values
#text(size: 7pt)[#include "table.typ"]

== Controls (recorded outcomes)
- *control+model* (a curve one 3-isogeny from NIST P-256):
  - best route back over the degree-3 edge to an a = −3 model;
  - persistent +15.28 %, one-shot +14.46 %;
  - verified on 8 random scalars.
- *control+ascent* (a 256-bit curve one degree-11 step below a j = 0 crater):
  - D_K = −3 reported;
  - priced unit-GLV on the reached crater, one-shot +32.5 % (recorded `glv_on_reached_crater.oneshot_gain` = 0.32505);
  - model-arm best route +9.01 % persistent, verified.
- *NIST P-256*: persistent 0.00 %, one-shot −1.70 %.
- *Curve25519*: E's own twisted Edwards a = −1 model is the baseline; best neighbour one-shot −22.5 %.
- Instrument check (no Edwards/Montgomery model reported on an odd-order curve): passed on all 136 rows.

== Population observations
- *Cheapest model already on E* (132 curves):
  - 45 have a = −3;
  - 13 are isomorphic to an a = −3 model;
  - 32 are twisted Edwards (31 with a = −1);
  - 33 are j = 0 / 1728 curves whose own unit 2-GLV is the baseline;
  - 9 use generic doubling.
- *Positive persistent gain*: 7 population curves, all among those 9:
  - other/Tom-384, mnt/mnt5/2, mnt/mnt5/3, other/BADA55-VPR-224, mnt/mnt3/1, mnt/mnt3/3, GOST 2001 test curve;
  - every route is over degree 5 or 5·5;
  - persistent +8.26 % to +15.49 %, one-shot +6.70 % to +14.52 %;
  - all 7 routes verified on 8 scalars, with no verification failures recorded.
- *Of the 9 generic-doubling curves*:
  - other/BADA55-VPR2-224 has neighbours but no cheaper class within the bound;
  - mnt/mnt1 has no rational neighbour within the bound.
- *Ascent arm*:
  - D_K is certified within |D_K| ≤ 2^20 on 48 population curves; 33 of those are D_K = −3 craters (f_E = 1).
  - No population walk reached a j = 0 / 1728 crater from a non-crater curve.
  - Non-unit small-|D_K| curves (for example mnt D_K = −19 … −211, Tom-384 −619, GOST CryptoPro-B −619, GOST 2001 test −915, Bandersnatch −8) have `f_E` recorded as `unresolved`, and no GLV was priced for them.

== Missing or out-of-scope data (stated as missing)
- *Arm C not run.* Isogeny-cycle GLV was not priced; it was declared a dominated control.
  - For the six population curves with positive gain and a recorded small D_K (Tom-384, the four mnt3/mnt5 curves, GOST 2001 test), the baseline therefore omits any chain endomorphism `harness/endosweep` may price on E. Their gains are relative to E's best *model*, not to E's best *endomorphism decomposition*.
  - other/BADA55-VPR-224 has no |D_K| ≤ 2^20.
- *No timing.* No wall-clock scalar-multiplication measurement was made.
- *No S = 0.8 M one-shot column.* The S = 0.8 M column is persistent only, as the contract states.
- *Other gaps.* Binary-field curves and curves above 521 bits were not in scope. The Doche–Icart–Kohel models were not priced.

== Files
- `plot.py` draws `gains.svg`.
- `table.py` writes `table.typ`.
- Both read only `runs/RUN-ENDO-d7cb69/raw-result.json`.
