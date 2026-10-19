#set page(paper: "a4", margin: (x: 1.6cm, y: 1.6cm))
#set text(size: 9.5pt)
#set par(justify: false)
#show heading: set text(size: 11pt)

= Decision report: DEC-20261016-4f3a1a (EXP-ENDO-7494e7)

*Decision: replicate H-ENDO-f58749.* Evidence `EV-ENDO-7628a0`: direction supports, strength preliminary, claim tier modelled. Read with correction `CORR-20261016-ac9fc8`. No ECDLP, rho or exponent claim changes.

== Identity
- Experiment `EXP-ENDO-7494e7`, run `RUN-ENDO-795989`, hypothesis `H-ENDO-f58749`, idea `IDEA-20261016-15a6fc`, question `RQ-ENDO-476761`, goal `GOAL-ENDO-001`.
- Approval `DEC-20261016-00e9cd`; executor `TASK-20261016-c886b3`; snapshot `TASK-20261016-d4363d` at `7f631b5a0`; independent validation `TASK-20261016-35d324` (passed); ledger archive `TASK-20261016-5c0f78`.
- Analysis: `experiments/EXP-ENDO-7494e7/analysis.md`. Earlier run report: `reports/run-20261016T1942Z/report.pdf` (its one-shot column is read with the correction).

== Scoped claim
On four isogeny classes (GOST 2001 test curve; mnt3/1 and mnt3/3; mnt5/2 and mnt5/3; Tom-384), within ell ≤ 13, depth 2, 12 candidates and the curvesweep M\_eq = M + S model at S = 1 M, the 2-GLV on a horizontal 5-isogenous neighbour with an a = −3 model has a lower modelled cost than the 2-GLV on E: persistent +5.96 % to +11.84 %, one-shot at most +2.20 % to +9.46 % once the omitted input-format cost is charged. Every route is verified on points. No timing and no ECDLP statement.

== Graph
#figure(image("decision.svg", width: 100%), caption: [Left: combined route against GLV on E, per population curve with a GLV arm. Recorded persistent (blue) and one-shot (orange) gains of RUN-ENDO-795989, and the one-shot gain with the validator's minimum omitted cost (29 or 32 M\_eq) charged (green, an upper bound). Frozen criterion: one-shot above 0 (dashed). Right: the corollary arm, model change alone against GLV on E, against the frozen band from −40 % to −20 %. Modelled M\_eq, one deterministic pass; the mnt pairs are one class each.])

== Observation
- Controls pass: control+ascent reaches the j = 0 crater over one degree-11 step, route verified 8/8, one-shot +32.57 % against E's model; mnt/mnt5/1 has 0 cheaper-class candidates and no combined route.
- Combined against GLV on E, persistent / recorded one-shot / corrected one-shot: GOST +5.96 / +3.71 / at most +2.20 %; mnt3 +11.03 / +7.76 / at most +5.78 %; mnt5 +11.30 / +9.05 / at most +7.55 %; Tom-384 +11.84 / +10.36 / at most +9.46 %.
- Model change alone against GLV on E, one-shot: −34.05 %, −25.24 %, −26.50 %, −30.31 %.
- Failed chain builds were all on descending 5-neighbours and successes all on horizontal ones (validator: proved for mnt5, observed for mnt3).
- The six positives are four isogeny classes; mnt5/2 and mnt5/3 route to j(mnt5/1), the negative control.

== Comparison
- Success criterion (a verified combined route with one-shot gain above 0 on a curve with a GLV arm): *met* on the recorded figures and *still met* under CORR-20261016-ac9fc8.
- Corollary (model change alone at most 0, predicted −0.2 to −0.4): *holds* on all six.
- Persistent prediction (0, 13 %\]: inside. One-shot lower by about 1 to 3 % of the GLV cost: recorded 1.48 to 3.27 points; corrected 2.38 to 5.25 points, a miss on three of four classes (non-gating).
- Against the index-calculus baseline and the matched rho: not applicable (known-scalar k·P cost).

== Inference
At the modelled tier a model change and the chain 2-GLV compose on four classes, on horizontal neighbours. The deciding one-shot column of the run is under-charged and its corrected signs rest on a written derivation, so the decision is a corrected-pricing re-run before support. The four classes are recorded as timed-comparison candidates, Tom-384 first.

== Limitation
- Modelled counts only; no wall-clock measurement of the combined route exists.
- Four classes, one seed, candidate cap 12, build\_limit 3; no f#sub[E] certified by the run.
- Heuristics H1–H3 are not validated.

== Next actions (ranked, recommended, not approved)
+ Fix isoglv's one-shot pricing and re-run under a new frozen contract and run id, with the corrected prediction recorded first.
+ Timed bench of the combined route against GLV on E on other/Tom-384 (optionally mnt5/2), with an A/A arm and a control.
+ ecbench independent-runner replication of EXP-ENDO-33a1ee.

All are constant-factor, known-scalar work and rank behind exponent-targeting work.

== Canonical graphs
Checked and left unchanged: `research/endosweep_curves_20261006/` (every GLV-on-E figure reproduced exactly; no graph source) and `knowledge/frontiers/ecdlp/` (no ECDLP claim moves). No canonical graph changes.

== Files
`plot.py` draws `decision.svg` from `runs/RUN-ENDO-795989/raw-result.json` and the validator's omitted-cost table (copied in CORR-20261016-ac9fc8).
