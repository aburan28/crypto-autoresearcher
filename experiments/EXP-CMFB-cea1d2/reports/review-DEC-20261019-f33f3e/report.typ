#set page(margin: 1.7cm, numbering: "1")
#set text(size: 9.5pt)
#set heading(numbering: "1.")
#show raw: set text(size: 8pt)

= Evidence review report: EXP-CMFB-cea1d2 (DEC-20261019-f33f3e)

*Decision report for the Coordinator's evidence review.* Source written without a shell; the calling session renders `fig_review.svg`, `fig_review.png` and this PDF from `plot.py` and `graph_data.json`. Numbers are read from `RUN-CMFB-2010d3/raw-result.json` by key, from the two review reports, or are arithmetic on those values (marked _derived_). No number here was produced by running code in this review.

#block(fill: rgb("#fff3cd"), inset: 8pt, stroke: 0.6pt)[
*Correction (owner review P2, CORR-20261019-a89bfa).* Below, the coverage-ratio bound min(1, mu)/(1 - exp(-mu)) <= 1.582 is called a theorem or a ceiling for every base. Read it as follows. The exact identity sum_r c(r) = binomial(B+2,3) and the exact bound coverage <= min(1, mu) are proved; the multiplicity distribution is left free, so the ratio to a specified positive baseline coverage c0 is bounded by min(1, mu)/c0. The value 1.582 comes from substituting the Poisson occupancy c0 = 1 - exp(-mu), which is heuristic H2: a model-conditional estimate, not a universal finite-instance ratio theorem, and no end-to-end cost result. The empirical small-x coverage comparison keeps its stated scope. The archived EV, DEC and hypothesis text are unedited; this box and CORR-20261019-a89bfa supply the corrected reading.
]

== Decision, strength, tier

#table(columns: (auto, 1fr), stroke: 0.4pt,
  [Decision], [*refine* (DEC-20261019-f33f3e). Not official until the ledger archive commit is verified by the dispatcher.],
  [Evidence], [EV-CMFB-e3d1ec: direction *supports* H-CMFB-9b2eed (a null prediction), strength *preliminary*, claim tier *toy*, proof status `empirical_only` (the 1.582 coverage ceiling is a separate derivation, KN-FIND-007).],
  [Hypothesis], [H-CMFB-9b2eed: specified to *analyzed* (not supported).],
  [Experiment, runs], [EXP-CMFB-cea1d2; RUN-CMFB-2373be (t1), RUN-CMFB-5905c0 (t2), RUN-CMFB-66b0fe (t3), RUN-CMFB-3dc120 (t4, C16 and C20), RUN-CMFB-42a578 (t5, C24 FAM), RUN-CMFB-e13f0e (t6, C24 N-A), RUN-CMFB-c71d35 (t7, C24 N-B), RUN-CMFB-2010d3 (t8, analysis).],
  [Reviews], [VAL-20261019-1b97f5 (task TASK-20261019-bbb351, verdict passed); RT-20261019-520123 (verdict conclusion_requires_narrowing). Review plan, written after both verdicts: `experiments/EXP-CMFB-cea1d2/reviews/review_plan.yaml`.],
  [Question], [RQ-CMFB-33610e (active; no direction closed).],
)

== Exact scoped claim

No coverage difference between the small-x liftable-window factor base and a matched random base exceeding the predefined resolution delta = 0.5 percent was observed over the tested instances (107 prime-order curves with 2^14 < p <= 2^25: 27 FAM members of p = 5t^2 + 19t + 19, 40 other D = -19 crater-type curves, 40 random curves), base (the first ceil((6N)^(1/3)) abscissae with f(x) a nonzero square, one canonical-sign point each, integral Weierstrass chart), counting convention (m = 3, unsigned multisets, targets uniform over Z_N, exact counting, 200 matched random bases per member) and resource budget (16 minutes wall, one pass, seeds 7001 to 7010). At C24 (2^22 < p <= 2^25; FAM 13 of 13 members in the band) every recorded 95 percent interval of the mean coverage ratio minus 1 lies inside +-0.04 percent; at C20 inside [-0.074, +0.057] percent under the contract-text powered set. C16 (FAM n = 4) is underpowered and enters no conclusion.

This is a statement at resolution 0.5 percent for the stated arms, cells, chart, base and convention, not a statement that no effect exists, and not that no factor base can beat a random one (a Sidon-type base reaches +10.7 percent, EV-FBG-001). The coverage ceiling (ratio at most 1.582) is the theorem KN-FIND-007, not a result of this run. Untested: the CM structure (endomorphism chain, isogeny pullback, canonical lift, other models, joint windows, the floor curve), the signed x-only convention, growth in N, decomposition cost, relation rank, linear algebra. No ECDLP speed, rho comparison or pair-46-scale claim; no cross-method ranking is made, so section 5a pricing does not apply.

== Graph

#figure(image("fig_review.svg", width: 100%), caption: [(a) recorded T with 95 percent interval per arm and cell against the grey band delta = +-0.5 percent; hollow markers are C16 (underpowered under every reading). (b) zoom on C20 and C24. (c) minimum detectable effect as recorded by the code (factor sqrt(3) x 1.0025 = 1.736) against the contract text, with the 0.25 percent powered threshold (defect D1). (d) planted B+1 base: known excess with the gate tolerance against the observed pooled excess with its standard error, detections of 8 curves (RUN-CMFB-66b0fe). (e) I10 null-spread ratio: recorded against the superseded 0.49/sqrt(N) reference, and against the frozen 1.4/sqrt(N) as recomputed by the validator and by the red team (defect D2). Sources: RUN-CMFB-2010d3 raw-result.json (tables, cells, sensitivity), VAL-20261019-1b97f5, RT-20261019-520123; data in `graph_data.json`; script `plot.py`.])

== Observation

The run is valid and complete (8 of 8 trials; 72 of 72 artifact hashes recomputed; all 26,331 coverage counts recounted by independent code with 0 mismatches; all eight trials rebuilt from scratch with identical raw results; VAL M4, M5, M9). Recorded T in percent, with sample size n:

#text(size: 7.5pt)[
#table(columns: (auto, auto, auto, auto, auto, auto, auto, auto), stroke: 0.3pt, align: center,
  [*Arm*], [*Cell*], [*n*], [*T (%)*], [*95 % interval (%)*], [*rand. p*], [*MDE code / contract (%)*], [*Holm p recorded / contract text*],
  [FAM], [C16], [4], [-0.174], [[-0.174, -0.034]], [0.411], [1.332 / 0.767], [none / none],
  [FAM], [C20], [10], [-0.030], [[-0.074, +0.048]], [0.441], [0.243 / 0.140], [none / 1.0],
  [FAM], [C24], [13], [-0.022], [[-0.038, -0.006]], [0.031], [0.065 / 0.037], [0.0936 / 0.1872],
  [N-A], [C16], [8], [-0.085], [[-0.405, +0.263]], [0.686], [1.318 / 0.759], [none / none],
  [N-A], [C20], [16], [-0.009], [[-0.061, +0.039]], [0.843], [0.268 / 0.154], [none / 1.0],
  [N-A], [C24], [16], [-0.000], [[-0.024, +0.027]], [0.969], [0.063 / 0.037], [0.9691 / 1.0],
  [N-B], [C16], [8], [-0.009], [[-0.186, +0.166]], [0.969], [1.537 / 0.885], [none / none],
  [N-B], [C20], [16], [+0.010], [[-0.038, +0.057]], [0.795], [0.245 / 0.141], [none / 1.0],
  [N-B], [C24], [16], [+0.016], [[-0.001, +0.035]], [0.079], [0.057 / 0.033], [0.1589 / 0.3972],
)]
Contract-text Holm values are _derived_ from the recorded randomization p with six tests (C20 and C24 powered): 6 x 0.0312 = 0.1872, 5 x 0.0794 = 0.3972, all others 1.0 (equal to VAL M7). The contract-text MDE column is VAL D1 and RT-O2, equal to recorded divided by 1.7364. Run IDs by row: C16 and C20 rows RUN-CMFB-3dc120; C24 FAM RUN-CMFB-42a578, N-A RUN-CMFB-e13f0e, N-B RUN-CMFB-c71d35; analysis RUN-CMFB-2010d3.

Gates: planted base detected 7 of 8 (C16), 8 of 8 (C20), 8 of 8 (C24), pooled ratio 1.02667 vs 1.03035, 1.01091 vs 1.01247, 1.00525 vs 1.00521, all within tolerance; qr_window R_pool 1.9940 to 2.0009 and R_wrong 0.9970 to 1.0006 in all nine pools; M0 holds on every base. Recorded classification NULL_AT_RESOLUTION, no Holm rejection, three C24 contrasts include 0, growth not assessable.

== Comparison

Every interval is inside the predefined +-0.5 percent band (decision rule R3), and in the cells the contract text calls powered inside +-0.08 percent. The instrument could have failed: the planted base was recovered at +0.525 percent against a known +0.521 percent at C24. The classification is the same under the recorded powered set {C24} and the contract-text set {C20, C24}. The nine null-spread ratios against 1.4/sqrt(N) are 0.815 to 0.971, inside the accepted band [0.75, 1.33]; the recorded 2.39 to 2.77 compare against a superseded reference. The smallest of nine recorded randomization p (0.031, FAM C24, a deficit) has probability about 0.25 as a minimum under the null (_derived_: 1 - 0.969^9). Against the preregistered prediction T = 0 the data agree; against the preregistered success criterion (outcome NULL_AT_RESOLUTION) the run meets it.

== Inference

The data support H1, exchangeability of the small-x window with a random base for exact m = 3 coverage, at the tested scope, with about thirteen times finer resolution than the declared delta at C24 (0.5 / 0.038, _derived_). They do not separate E1, E2 and E3 because no arm shows an effect to attribute. 'Constant-only' follows from the conservation ceiling, a theorem independent of the run; the measured content is the narrower exchangeability of this base. The tested base selects abscissae by the integer size of x and never uses the CM structure; a w-orbit base with labels l x lambda^j is constructible (red team, lambda = 2/v mod N for FAM) and was not run. The FAM sign is negative in all three cells; at C24 recorded Holm p is 0.094 (0.187 under the contract text), not a detected deficit, recorded as exploratory.

*Why refine and not support.* The status a `supported` hypothesis would carry is narrower than the sentence the contract attaches ('constant-only, retire the channel'); the recorded powered set, MDE and Holm values are not the contract's (D1) and no archived analysis applies the contract text yet; the Coordinator's determination that D1 does not fire I9 is a judgment on which the run's standing depends; and the observation is a single unreplicated pass. The data are not read as disagreeing with the null.

== Limitation

Toy sizes 2^14 < p <= 2^25; no transfer to 2^52 or the 53-bit pair; one confirmatory pass, gate numbers seen before the run, planted-gate margins thin at C16 and C20 and one rung only; one powered cell by the code and two by the contract text, no growth arm; FAM is exhaustive in band; the from-scratch rebuild shows determinism, not replication; a coupling growing as N^eps with eps above about 0.13 and below 0.04 percent at 2^24 is unconstrained at 2^52 (red team). Defects of the frozen analysis code, recorded and not corrected: D1 (MDE inflation sqrt(3) x 1.0025 against 'no inflation factor': powered {C24} instead of {C20, C24}, FAM C24 Holm 0.0936 instead of 0.1872, class unchanged) and D2 (I10 against the superseded 0.49/sqrt(N): false positive in 9 of 9). The review plan was written after both verdicts, the blind re-derivation was not blind, two reviewers worked the same quantity, and the reviewed snapshot is a producer-session head. Scan efficiency is validated as an implementation and is immaterial to cost. Distance remaining to matched rho: no measured value; the red team's analytic, unmeasured estimate of index calculus over rho is 88 to 3400 at N = 2^24 across the 0, 0.1 and 1 GAE band with the order holding, quoted as context and not adopted; the small-x base equals the index-calculus baseline (a random base) within 0.04 percent at C24, so no improvement over the baseline was measured.

== Next actions

+ Superseding analysis, zero compute (RC-1): contract-text MDE, powered set, Holm, I10 against 1.4/sqrt(N), per-member z-scores; new script and run id, companion CORR-\* record, recorded t8 untouched. This is the one next action for the question.
+ Then a scoped `support` decision on H-CMFB-9b2eed (strength preliminary, wording narrowed per the corrected reading of `decision_impact`), if the new analysis agrees.
+ Commission the design (not approval) of RC-2, a CM-coupled w-orbit base on the same instrument, with the signed convention (RC-3) and a graded dose-response (RC-5) folded in; check overlap with H-CMFB-7d4e1a and H-CMFB-c5e29b first. Low to medium priority; does not displace exponent-targeting work.
+ Not commissioned now: RC-4 (C28 growth cell).
+ Ledger archive of the named paths, validation and independence checks, push, ready-for-review PR naming EV-CMFB-e3d1ec and DEC-20261019-f33f3e.

== Earlier run reports and graphs

Earlier run report (observations only): `experiments/EXP-CMFB-cea1d2/reports/run-20261019T0541Z/` (`report.typ`, `report.pdf`, `fig_run_summary.svg`, `fig_run_summary.png`, `plot.py`).

Canonical graphs checked and left unchanged: `reports/run-20261019T0541Z/fig_run_summary.svg` and `.png` (recorded t8 values; unchanged because the recorded t8 is untouched; the review's view is `fig_review.svg`). `knowledge/frontiers/ecdlp/` holds frontier rows (YAML) and no graph; no row changes because no measured bound or ranking is recorded. No file under `runs/`, `claims/`, `implementation/`, `specification.yaml`, `trial-plan.json` or `reports/run-20261019T0541Z/` was edited. The superseding analysis of action 1 will need its own graph.
