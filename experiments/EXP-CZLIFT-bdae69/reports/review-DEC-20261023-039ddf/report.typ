#set document(title: "Decision report DEC-20261023-039ddf", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.8cm), numbering: "1 / 1")
#set text(size: 9pt)
#set par(justify: false, leading: 0.58em)
#show heading.where(level: 2): set text(size: 10.5pt)
#let vb(body) = block(fill: luma(244), inset: 6pt, radius: 3pt, width: 100%, body)

= Decision report: DEC-20261023-039ddf
GOAL-CZLIFT-1516d5 · RQ-CZLIFT-b9f765 · EXP-CZLIFT-bdae69 · H-CZLIFT-d37231 · review plan REVIEW-CZLIFT-BDAE69-EVIDENCE-20261023 · 2026-10-23

== Status
Not official until the ledger archive TASK-20261023-4d7449 commits this decision, EV-CZLIFT-f2a401, the hypothesis update and KN-FIND-c71e5d, and the post-commit verifier accepts it. This is not a performance measurement; no benchmark or leaderboard entry applies.

== Decision
#table(columns: (1fr, 3fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*Decision*], [`reject_scoped`. One transition: H-CZLIFT-d37231 approved #sym.arrow rejected, at toy tier, as posed, at the tested instantiation (smallest primitive root), in its naive-success and homomorphism-rate clauses.],
  [*Evidence*], [EV-CZLIFT-f2a401, direction contradicts, strength *strong* (for the falsification; scientific content weak).],
  [*Claim tier*], [toy (p < 2000, at most 11 bits; precision 4; F#sub[p]#super[\*] only).],
  [*Proof basis*], [derivation (analysis.md I-1, D-1 to D-4), reproduced on 3200/3200 rows by two independent implementations.],
  [*Runs*], [RUN-CZLIFT-0cefcd (seed 20261009), RUN-CZLIFT-a5c1da (seed 20261010).],
  [*Reviews*], [VAL-20261022-8caa0c (TASK-20261022-2d255e, passed); RT-20261023-2411b8 (TASK-20261023-20d7d9; R1 breaks on the transfer clause only, R2 holds with corrected nulls, PTM-1 holds).],
  [*Knowledge*], [KN-FIND-c71e5d (scoped calibration note; token to be confirmed free by the session).],
)

*Exact scoped claim.*
#vb[Scope: toy tier, G#sub[m] only. Two seeds (20261009, 20261010), each 40 seeded primes 50 < p < 2000 with 40 pairs (1600 pairs), d in \[2, p-3\], precision 4, g the smallest primitive root as frozen in run.py. (i) The Teichmuller section is homomorphic on every sampled pair, the functional log#sub[p] applied to s(x)#super[p-1] vanishes on every sampled point, and the Smart-style ratio is never defined. (ii) The random-Hensel ratio equals d on 3 of 3200 pairs against 5.39 at mean 1/p (ratio 0.56, 95% CI 0.12 to 1.63). (iii) The naive integer section's ratio equals d on 13 and 20 of 1600 pairs (z = 7.65, 9.14), exactly on the pairs with g#super[d] mod p#super[2] < p: all 24 pairs with g#super[d] < p succeed, no pair with p ≤ g#super[d] < p#super[2] can, and the other 9 match the exact conditional null (1.37x, CI 0.63 to 2.60). (iv) The naive section is homomorphic exactly when xy < p (10 and 10 against 9.35 and 12.96); the Hensel section on 0 pairs (p#super[-3]). H-CZLIFT-d37231 is rejected as posed in its naive-success and homomorphism-rate clauses. The falsifying excess is the archimedean no-carry region (Eisenstein's logarithmic property of the Fermat quotient); it carries no discrete-log information beyond an O(log p) integer-logarithm check and is no evidence of p-adic leakage or about any elliptic curve. EV-CZLIFT-f2a401 · DEC-20261023-039ddf · RUN-CZLIFT-0cefcd · RUN-CZLIFT-a5c1da · TASK-20261022-2d255e · TASK-20261023-20d7d9.]

== Observation
Validity: 2 of 2 planned trials `output_validated`, return code 0, checker return code 0, commit ca89e1a9f0 clean, seeds as frozen. The validator matched 32 custody hashes, recomputed every frozen metric exactly, and replayed all 3200 rows independently on every field. No run claims a solve; no certificate applies.

#figure(image("graph.svg", width: 96%), caption: [Panel A: success counts per seed (n = 1600 each) for the three sections. The naive bar is split into the sub-p region (g#super[d] < p) and the rest region (g#super[d] ≥ p#super[2]); band rows never succeed. Solid line: expected count at the recorded mean 1/p; dashed line: the frozen 4-standard-error acceptance bound (7.8 and 10.6); diamond: the naive exact conditional null (red-team `r2_nulls_output.json`). Panel B: pooled observed/expected ratios with the red team's 95% intervals (`intervals_output.json`). Data: `plot_data.json`; regenerate with `plot.py`.])

#table(columns: (1.4fr, 1fr, 1fr, 1fr, 1fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*quantity (per seed)*], [*RUN-CZLIFT-0cefcd*], [*expected*], [*RUN-CZLIFT-a5c1da*], [*expected*],
  [Teichmuller success], [0 / 1600], [2.05 at 1/p], [0 / 1600], [3.33 at 1/p],
  [Teichmuller hom, vanishing], [1600, 1600], [1600 (theorem)], [1600, 1600], [1600 (theorem)],
  [naive success (z)], [13 (7.65)], [2.05 at 1/p; 11.55 exact], [20 (9.14)], [3.33 at 1/p; 17.64 exact],
  [naive sub-p / band / rest], [11/11, 0/14, 2/1575], [rest 2.48 exact], [13/13, 0/20, 7/1567], [rest 4.11 exact],
  [Hensel success (z)], [1 (-0.73)], [2.05 at 1/p], [2 (-0.73)], [3.33 at 1/p],
  [naive hom], [10], [9.35 (xy < p); 2.05 at 1/p], [10], [12.96 (xy < p); 3.33 at 1/p],
  [Hensel hom], [0], [2.2e-5 (p#super[-3])], [0], [2.3e-4 (p#super[-3])],
)
Review-side (not run evidence): generator arms over all 288 primes in (50, 2000), naive population rate as a multiple of mean 1/p: smallest root 5.03, random root 1.11, smallest root above sqrt(p) 0.956, smallest root restricted to g#super[d] ≥ p#super[2] 0.910. Elliptic integral section on the 37a1 short model y#super[2] = x#super[3] - 16x + 16 with lift (0, 4): ratio = d on 1420/1420 rows at d = 2, ..., 6; off the integral set 21, 22 and 25 successes (naive, balanced, Hensel) against 21.7 at 1/p. On y#super[2] = x#super[3] + 17 with lift (-2, 3): 287/287 at d = 2.

== Comparison
- *Frozen criteria.* Teichmuller rates 1.0: met on both seeds. Hensel |z| ≤ 4: met. Naive |z| ≤ 4: *not met on either seed*. The falsification criterion (a non-canonical section with z > 4 on both seeds) is met; the instrument-invalidity clause is not triggered. Every z variant the validator computed keeps the outcome (minimum 7.24).
- *Naive against the hypothesis's 1/p null:* pooled 33 against 5.39, ratio 6.13 (CI 4.22 to 8.61). *Against the exact null* (success iff g#super[d] mod p#super[2] < p): 33 against 29.19, ratio 1.13 (CI 0.78 to 1.59).
- *Homomorphism against "near 1/p":* naive 10 and 10 against 2.05 and 3.33 (P(≥ 10) = 5.7e-5 and 2.4e-3); against the exact xy < p rule, 9.35 and 12.96.
- *Against the recorded Coordinator prior:* "Teichmuller and Hensel hold" and "the naive falsification is a smallest-root artifact" were confirmed; "no elliptic analogue" was overturned by the red team's integral-section computation.
- *Against DEC-20261009-44c288:* its count reading (24 sub-p successes, 9 at about the random rate) agrees; its sentence "no elliptic analogue because point addition always reduces" does not.

== Inference
- *Mechanism (derivation, analysis.md I-1).* The functional reads the Fermat quotient mod p. By Eisenstein's logarithmic property, with q the Fermat quotient and g#super[d] = r + kp, the ratio is d + k/(r · q(g)) mod p, so success holds iff p divides k, i.e. iff g#super[d] mod p#super[2] < p. Sub-p pairs always succeed, band pairs never do, and rest pairs succeed at about 1/p. The naive section is homomorphic iff xy < p; the Hensel section with probability p#super[-3].
- *Status.* The hypothesis is false as posed in two clauses (naive success; homomorphism rate). The Teichmuller clause holds as a calibration; the Hensel success clause holds within the test's power (an excess up to 1.63x of 1/p is not excluded). The stated mechanism Hom(Z/(p-1), Z#sub[p]) = 0 is not refuted; the refuted part is an unnumbered random-model assumption about a structured section.
- *No leverage.* The certain instances (g#super[d] < p) are solved by an O(log p) integer logarithm; elsewhere the expected cost is about p · O(log p), dominated by Pollard rho.
- *Transfer.* Nothing here is evidence about elliptic curves. An elliptic analogue exists on the integral multiples of a small global lift (finite by Siegel's theorem, a recalled citation), so elliptic Smart-style statistics in this goal must be stratified before they are read as random rate.
- *Specification branch.* The `on_negative` branch (instrument repair, contradicted textbook fact) is not executed: the instrument is verified, and Eisenstein's property predicts the excess.
- *Negative phrasing for the clauses that held:* no Teichmuller or random-Hensel success rate exceeding the pre-registered 4-standard-error threshold over the mean 1/p was observed over the tested primes, generator rule, precision, implementation and budget.

== Limitation
- Toy tier, F#sub[p]#super[\*] only: 80 primes below 2000, precision 4, 3200 pairs.
- The hypothesis did not fix the generator; the rejection is of the smallest-root instantiation frozen in run.py. The random-root reading (expected z 0.18 ± 1.21) is review-side.
- The z statistic assumes independent rows; duplicate d draws and clumped success sets inflate its spread to about 1.1 to 1.2. No criterion outcome changes.
- The recorded vanishing flag covers 40 distinct points per seed; full-row coverage is the validator's computation.
- The elliptic analogue is a review-side computation on two curves and depends on the Weierstrass model and lift convention.
- PD-1: the independence checker flags the validator task, which held the sealed blind joint and the implementation joints together. Accepted on the seal and on the red team's independent re-derivation.
- Reviewer model identities are reported, not probe-verified.

== Next actions
+ Session: write analysis.md and KN-FIND-c71e5d.md from the handback, confirm the token is free, run `plot.py`, compile this report and inspect it, then run the ledger validator and the knowledge index build.
+ Ledger archive TASK-20261023-4d7449, run alone for this review's exact paths; verify, push, and open or refresh the ready-for-review PR naming EV-CZLIFT-f2a401, DEC-20261023-039ddf and KN-FIND-c71e5d.
+ Control C1 (red team, no new runs): for every elliptic Smart-style success statistic in GOAL-CZLIFT-1516d5 that uses a naive, integral or small-height section on a small-coefficient model (at least EXP-CZLIFT-ae0a13 and EXP-CZLIFT-f5e06c), enumerate the integral multiples of the global lift with exact rationals and split each success count into the integral set and the rest.
+ Synthesis task: record a correction of the DEC-20261009-44c288 sentence "no elliptic analogue because point addition always reduces", and use the supportable form of RQ-CZLIFT-b9f765 decision target (a) in any closure.
+ Any successor G#sub[m] calibration (none admitted now) carries red-team controls C2 to C5.
+ Checkpoint GOAL-CZLIFT-1516d5 after the archive with exactly one next action.

== Reports and graphs
- Validation: #link("../validation-20261022/validation_report.yaml")[`reports/validation-20261022/validation_report.yaml`] (VAL-20261022-8caa0c).
- Red team: #link("../redteam-20261023/redteam_report.yaml")[`reports/redteam-20261023/redteam_report.yaml`] (RT-20261023-2411b8).
- Earlier run reports: no `reports/run-*` directory exists for this experiment. Canonical graphs: none plots EXP-CZLIFT-bdae69 or H-CZLIFT-d37231 (repository search outside the ledger, experiments and coordination trees found no reference); none is changed.
