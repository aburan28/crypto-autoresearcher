#set document(title: "Decision report DEC-20261023-2e7447", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.8cm), numbering: "1 / 1")
#set text(size: 9pt)
#set par(justify: false, leading: 0.58em)
#show heading.where(level: 2): set text(size: 10.5pt)
#let vb(body) = block(fill: luma(244), inset: 6pt, radius: 3pt, width: 100%, body)

= Decision report: DEC-20261023-2e7447
GOAL-CZLIFT-1516d5 · RQ-CZLIFT-b9f765 · H-CZLIFT-fba874 · EXP-CZLIFT-1a3453 · review plan REVIEW-CZLIFT-1A3453-EVIDENCE-20261023 · 2026-10-23

== Status
This decision takes effect only when the ledger archive TASK-20261023-4d7449 commits and the post-commit verifier accepts it. Until then nothing here is official. This is a toy-tier spectral measurement, not a performance measurement. No benchmark, frontier row or exponent moves.

== Decision
#vb[*REFINE.* The run set is valid. It supports the narrow single-character statement below on the 42 power-bearing records, weakly, at preliminary strength and toy tier. It does not discriminate on the hypothesis title. H-CZLIFT-fba874 moves from *approved* to *analyzed*: it is not supported, weakened or rejected. #raw("decision_impact.on_positive") of EXP-CZLIFT-1a3453 is *not* invoked. A successor hypothesis and contract will restate the claim at the instrument's real scope, measure the detection floor, and target the exponent-relevant scaling of Fourier mass with n.]

- *Evidence:* EV-CZLIFT-764f54. Direction supports (narrow scope only). *Strength:* preliminary. *Claim tier:* toy (p ≤ 571, 10-bit fields; n ≤ 613; precision 5).
- *Runs:* RUN-CZLIFT-037e5f (seed 20261009) and RUN-CZLIFT-d37ca4 (seed 20261010), both `output_validated` at commit 3d48a8e6 (clean).
- *Review:* VAL-20261022-55676f (TASK-20261022-8ebef8, passed; J1-J3 hold, PTM-1 holds with scope restriction). RT-20261023-dcb217 (TASK-20261023-792040; R1 breaks, R2 breaks, PTM-1 breaks on the recorded scope and holds on the 42 power-bearing records).
- *Earlier records:* approval DEC-20261009-296cee; observation DEC-20261009-6aef7a.
- *Knowledge:* KN-OPEN-d3a6f0 promoted (Fourier mass of torsion-section digit characters; it sharpens KN-OPEN-3417fc).

*Scoped claim (verbatim from DEC-20261023-2e7447):*
#vb[#"On the 42 power-bearing records of RUN-CZLIFT-037e5f and RUN-CZLIFT-d37ca4, no single-digit function a_i(x(s_tor([k]P))) or a_i(y(s_tor([k]P))), i = 0..4, has half-range normalised correlation tau >= rho_min(p,n) = sqrt((ln((p-1)n) + 12)/h), h = (n-1)/2, with any single pair (nontrivial additive character of F_p, character of Z/n). The records are 33 CM-canonical class-number-one integer models and 9 random curves with one naive integer lift, 53 <= p <= 571, 47 <= n <= 613, one random generator per record and precision 5. rho_min is 0.28-0.98 (median 0.50), about 1.44x higher for generator-covariant even x-digit leaks at n < 109. No improvement meeting the predefined threshold was observed over these instances, parameters, solver and budget. The 30 records with n <= 41 carry no information. Nothing follows for nonlinear or pseudorandom encodings, multiplicative characters, weaker or sparser leaks, other models, lifts or generators, or larger n."]

== Observation
Validity was checked first. The plan has 2 trials and both runs exist. The manifests are schema-complete, and the hashes bind the runs to the contract frozen in 172ec3c94f. Every metric was recomputed from the raw rows. An independent implementation replays all 72 records to 8e-14, with all 2160 spike counts equal. The uniform control is clean, so no invalidation rule fires.

- On both seeds every spike count is 0: higher digits, digit 0, shuffled and uniform (36 records × 10 digit rows per seed).
- Closest real approach: -3.942 (RUN-CZLIFT-037e5f, D=-3, p=571, n=541, y2) and -4.070 (RUN-CZLIFT-d37ca4, D=-163, p=347, n=383, x4).
- Blind records: 30 of 72 (all with n ≤ 41) have h ≤ T, so X ≤ h ≤ T for any digit sequence. Power-bearing records: 42 (n ≥ 47; 33 CM, 9 random), with `rho_min` 0.284-0.978 and median 0.502.
- PTM-1 (planted floor(pk/n)) spikes on 42/42 power-bearing records and 0/30 blind ones.
- CHIRP and INV, which determine k, fire on 0/72 records under the frozen rule, and LEGMSB stays ≤ 0.68 T everywhere. Digit 0, which determines k up to sign, is white on 72/72.
- CM D=-3 y-digits show a structural t = 0 elevation from the order-3 automorphism: mean excess +2.60 real and +3.65 shuffled.

#figure(image("graph.svg", width: 96%), caption: [Panel A: the per-record maximum of X over the higher digits (x1-x4, y1-y4; coloured by run, shaped by arm, hollow if blind) and over digit 0 (grey ×), against n. Each record's threshold T(p,n) is drawn as a black tick, and the trivial bound h = (n-1)/2 as a dashed line. The planted PTM-1 leak reaches X = 0.999h. Panel B: the detection floor `rho_min = sqrt(T/h)` per record and the observed `tau_max = sqrt(X_max/h)` of the higher digits. Data: `plot_data.json` (values from both `raw-result.json` files and `rt_scope_output.json`, cross-checked by `plot.py`); regenerate with `plot.py`.])

== Comparison
#table(columns: (1.3fr, 2.6fr, 1.1fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*comparison*], [*result*], [*grade*],
  [frozen criteria], [Success met on both seeds; falsification not met; no invalidation rule fires.], [as frozen],
  [real vs uniform], [Uniform row max = ln N - 0.92 + 0.90 G on 420 rows. Real higher digits outside D=-3 y have mean excess -0.29, against -0.28 for uniform.], [randomized],
  [real vs shuffled], [The control shares the t = 0 term and samples from the full range, reintroducing the negation mirror; on D=-3 it inherits `mu_6` orbits. Per-row spike probability is up to 0.167 against a stated e^-12, and P(zero on both seeds) is about 0.47. The bias runs toward the hypothesis.], [not isolated],
  [D=-3 real vs symmetry-matched null], [DC mean rank 0.44; non-DC +0.14 above the matched mean; Fisher chi^2 = 76.0 on 78 dof. No hidden excess.], [explained],
  [real vs planted PTM-1], [Detected on 42/42 power-bearing records: the instrument has power for gross linear leaks.], [power shown],
  [CM arm vs random arm], [0 spikes on both arms, but 33 vs 9 power-bearing records and one naive lift each.], [not isolated],
)

== Inference
- The data exclude exactly the single-pair class in the scoped claim. On the pair j = 0 the excluded event is a digit-value bias, not a dependence on k.
- On the title claim ("no p-adic digit of the torsion section correlates with the discrete logarithm") the evidence does not discriminate. Digit 0 carries k and is white, and so is a uniform digit. On that claim the experiment is inconclusive, not supportive.
- The clause "exactly as for the same digits re-indexed by a random permutation" held by chance, under a control biased toward the hypothesis.
- Resource reading. `s_tor` is a computable homomorphism, so digit characters have exact shift-query access, and their Fourier mass tau is the parameter of a Fourier-learning hidden-number attack (about tau^-2 polylog(n) evaluations). The red team estimates the breakeven against rho at about n^-1/4 up to polylog factors, roughly 2^-53 at 256-bit n. This experiment's floor is tau ≥ 0.28 at n ≤ 613. The measurement is not an obstruction and closes no lane. The exponent-relevant unknown is filed as KN-OPEN-d3a6f0.

== Limitation
- Toy tier: p ≤ 571 and n ≤ 613. No transfer to larger n or cryptographic sizes, and no statement about any deployed curve.
- Narrow class: one digit at a time, additive characters, single pairs, the half range, one generator per record and one Weierstrass model per curve. Precision 5 gives digits 0-4.
- Strength is capped at preliminary by the not-isolated shuffled comparison and by the unnumbered random-model null, which fails on D=-3 y-digits, digit 0 and the shuffled series.
- The falsification rule has two readings (per row and per digit aggregate). This is moot for zero counts and load-bearing for any successor.
- The leak-class power figures are single seeded instances from the red team, and the breakeven is an order-of-magnitude estimate.
- This report was composed without a shell. The session renders graph.svg and report.pdf. The subagent harness refused the .md writes, so the session writes analysis.md and KN-OPEN-d3a6f0.md verbatim from the coordinator handback.

== Linked reports
- Validation: #link("../validation-20261022/validation_report.yaml")[`reports/validation-20261022/validation_report.yaml`] (VAL-20261022-55676f).
- Red team: #link("../redteam-20261023/redteam_report.yaml")[`reports/redteam-20261023/redteam_report.yaml`] (RT-20261023-dcb217).
- Analysis: #link("../../analysis.md")[experiments/EXP-CZLIFT-1a3453/analysis.md].
- Run reports: this experiment has no `reports/run-*` directory. Its run records are under `runs/RUN-CZLIFT-037e5f/` and `runs/RUN-CZLIFT-d37ca4/`.

== Canonical graphs checked
knowledge/frontiers/ecdlp/generic-rho/KR-RHO-53c89f.yaml and knowledge/frontiers/ecdlp/index-calculus/KR-IC-cd159a.yaml were checked and left *unchanged*: there is no cost claim and no exponent moves. The only new graph is graph.svg in this folder.

== Next actions
- *NA-1 (session, mechanical):* `--check` EV-CZLIFT-764f54, DEC-20261023-2e7447 and KN-OPEN-d3a6f0. Write analysis.md and KN-OPEN-d3a6f0.md from the handback. Run plot.py, which cross-checks every value and writes graph.svg. Compile this file to report.pdf and inspect it. Regenerate knowledge/INDEX.md and run `tools/validate_ledger.py`.
- *NA-2:* Run the ledger archive TASK-20261023-4d7449 alone, staging the exact paths listed in DEC-20261023-2e7447. Verify it, push, and open or refresh a ready PR titled "evidence: EV-CZLIFT-764f54/DEC-20261023-2e7447" that names KN-OPEN-d3a6f0.
- *NA-3:* GOAL-CZLIFT-1516d5 stays active. Checkpoint it with exactly one next action, NA-4 being this lane's proposal.
- *NA-4 (refine successor):* A refined hypothesis on the growth exponent of the maximal full-range Fourier mass of digit characters of `s_tor`, against n^-1/2 (random) and n^-1/4 (breakeven). The successor contract needs:
  - power-bearing records only, with per-record `rho_min` published;
  - a symmetry-matched null, with j = 0 removed from the spike count;
  - comparison per row and per pair;
  - planted-leak power curves;
  - generator covariance;
  - n up to about 10^4-10^5;
  - a numbered HEUR null with validation rows at the same scale;
  - a Legendre arm, plus a digit-0 Weil-bound nearby-object control;
  - two or more lifts per random curve.
- *NA-5 (synthesis, RQ-CZLIFT-b9f765 wording):*
  - Qualify "a computable canonical section would be a full break": `s_tor` exists, is computable, and is an isomorphism, so any gain must come from the encoding.
  - Do not list EXP-CZLIFT-1a3453 as closing the canonical-section clause.
  - Require a detection floor and blind zone for every spectral instrument.
  - Name the coordinate model and the digit encoding of the section.
- *NA-6 (candidate):* Attempt a Weil-type bound for the digit-1 character sum via the Greenberg transform (KN-OPEN-d3a6f0 Q2), going through the KN-TECH-080 gate first.
