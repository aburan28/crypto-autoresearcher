#set document(title: "Decision report DEC-20261023-147f9f", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.8cm), numbering: "1 / 1")
#set text(size: 9pt)
#set par(justify: false, leading: 0.58em)
#show heading.where(level: 2): set text(size: 10.5pt)
#let vb(body) = block(fill: luma(244), inset: 6pt, radius: 3pt, width: 100%, body)

= Decision report: DEC-20261023-147f9f
#"EXP-CZLIFT-17b7eb · H-CZLIFT-889c9d · RQ-CZLIFT-b9f765 · GOAL-CZLIFT-1516d5 · review plan REVIEW-CZLIFT-17B7EB-EVIDENCE-20261023 · 2026-10-23"

== Status
#"Not official until the ledger archive TASK-20261023-4d7449 commits these records and the post-commit verifier accepts that commit. The ledger archive also stages the review reports this decision composes. This is not a performance measurement: no benchmark or index-calculus baseline row applies."

== Decision
- *Decision:* #"support (one transition). H-CZLIFT-889c9d moves approved -> supported, at toy tier, in the scoped form below only."
- *Evidence strength:* #"replicated (EV-CZLIFT-712fe4). Not strong, because clause 3 rests on a pooled statistic with a post-observation null correction and low power against confined leaks."
- *Claim tier:* #"toy (p <= 1373, at most 11 bits; exact p-adic arithmetic at precision p^8)."
- *Proof status:* #"derivation. The rule is a Serre-Tate/Kummer theorem: red-team R1, redteam_report.yaml key joint_findings.R1.derivation_two_sides_identical. Prior art: Belding 2007, arXiv:math/0703906, section 7, retrieved by TASK-20261023-856638."
- *Knowledge promotion:* #"KN-FIND-3c7e19, framed as known theory with calibrated instruments (novelty: none)."
- *Records:* #"EV-CZLIFT-712fe4, DEC-20261023-147f9f, CORR-20261023-1869c3, CORR-20261023-9f2176, RUN-CZLIFT-041d05, RUN-CZLIFT-6709c9, TASK-20261022-282b02 (validation), TASK-20261023-856638 (red team), TASK-20261023-4d7449 (ledger archive), DEC-20261009-a3797d (approval), DEC-20261009-9f9254 (observation)."

*Exact scoped claim* #"(verbatim from DEC-20261023-147f9f, field scoped_claim):"
#vb[#"Scope: the 29 class-number-one CM anomalous curves with 7 <= p <= 1373 (D in {-3, -11, -19, -43, -67, -163}); unramified integral short-Weierstrass Z_p-lifts in the four sampled classes (v_p(Δj) in {1, 2, 3, ∞} at e = 1, {3, 6, ∞} at e = 3); precision p^8; the naive, Teichmuller and one-digit Hensel sections. (1) The degeneracy flag v_p(z([p]P^)) >= 2 agreed with v_p(Δj) >= 2e on 14,616/14,616 rows. This calibrates two code-independent instruments against a statement that follows from Serre-Tate/Kummer theory (prior art: Belding 2007, section 7); it is not independent evidence for it. At j = 0 the threshold is pinned only to (3, 6]. (2) Smart's ratio recovered d on 2,052/2,052 rows per seed with v_p(Δj) < 2e. (3) On degenerate lifts the pooled next-digit success count was consistent with the random-section null on both seeds. Matching null 1/(p+1): 93 and 87 against 86.84 expected, z = +0.68, +0.02. Exact lift-conditioned nulls: z = +1.54, +0.75. The rate is not 1/p per cell for deterministic sections: on j = 0 lifts with A ≡ 0 mod p^2 the Teichmuller section never succeeds on d in mu_6 \\ {±1} (rate 0 at p = 7). Evidence: EV-CZLIFT-712fe4. Runs: RUN-CZLIFT-041d05, RUN-CZLIFT-6709c9. Review tasks: TASK-20261022-282b02, TASK-20261023-856638."]

== Observation
#"Validity. Both planned trials ran (2 of 2) to output_validated, with seeds 20261009 and 20261010 as frozen. Commit dcaa880ab6, clean tree. Each run has 29 curves and 7,308 rows. Manifest metrics equal raw-result metrics. The validator's independent replay matches 14,616/14,616 rows, and its sealed blind re-derivation (J3) agrees. Validation verdict failed on J2 only: a definition mismatch on the degenerate-rate fields, outcome-invariant, now corrected by CORR-20261023-1869c3 and CORR-20261023-9f2176."

#figure(image("graph.svg", width: 100%), caption: [#"Panel A: pooled next-digit successes on the 5,256 degenerate rows per seed, as z against the null of each definition (CORR-20261023-9f2176), with the frozen |z| <= 4 band. Panel B: per-section z (1,752 rows per section and seed) against 1/p on the producer definition (open markers; validator) and against the exact null conditioned on the actual lifts (filled; red team). Panel C: successes at p > 500, both seeds pooled (1,200 rows per section), against the null and two leak alternatives (post hoc red-team reading). Panel D: the exact-1.0 predictions: rule agreement per run, Smart recovery on non-degenerate rows per run, and the red-team full-fiber sweep (review data, not a frozen run). Runs RUN-CZLIFT-041d05 (seed 20261009) and RUN-CZLIFT-6709c9 (seed 20261010). Data: plot_data.json; drawn by plot.py."])

#table(columns: (2.6fr, 1fr, 1fr, 2fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*quantity*], [*041d05*], [*6709c9*], [*source*],
  [#"rule agreement (flag vs j-distance rule)"], [#"7,308/7,308"], [#"7,308/7,308"], [#"manifest"],
  [#"Smart recovers d, v_p(dj) < 2e"], [#"2,052/2,052"], [#"2,052/2,052"], [#"manifest; validator"],
  [#"degenerate rows / next-digit successes"], [#"5,256 / 93"], [#"5,256 / 87"], [#"validator j2_recompute"],
  [#"z, all v >= 2, frozen 1/p (pooled SE)"], [#"-0.0191"], [#"-0.6463"], [#"validator; CORR-20261023-1869c3"],
  [#"z, all v >= 2, matching 1/(p+1)"], [#"+0.684"], [#"+0.018"], [#"rt_r2_nulls_output.json"],
  [#"z, exact null given actual lifts"], [#"+1.539"], [#"+0.751"], [#"rt_r2_actual_lifts_output.json"],
  [#"Teichmuller z vs 1/p / vs exact null"], [#"-2.741 / -1.480"], [#"-1.835 / -0.843"], [#"validator; red team"],
  [#"naive z vs exact null"], [#"+1.592"], [#"+1.487"], [#"rt_r2_actual_lifts_output.json"],
  [#"hensel_random z vs exact null"], [#"+2.322"], [#"+0.602"], [#"rt_r2_actual_lifts_output.json"],
)
#"Further observations. Teichmuller has 0 successes on every d in mu_6 minus {+1, -1} on canonical and isomorphic j = 0 lifts, at all 11 primes from 7 to 919, and its exact rate at p = 7 is 0 (rt_r2_exact_output.json). The red-team full-fiber sweep covered 12,778 lifts: 0 rule disagreements, 0 point- or section-dependent flags, and one degenerate class mod p^2 per curve. One pert_p-labelled lift per seed (D = -43, p = 11) has v_p(dj) = 2 = 2e and gives 36 degenerate rows, flagged in advance by the j-distance instrument (validator D2)."

== Comparison
- #"Preregistered criteria. The success criterion is met on both seeds under every definition-and-null pairing (max |z| = 1.539). The falsification criterion is not triggered. The frozen criterion is read as written; the matching null is reported beside it and does not replace it."
- #"Recorded prior (written before the red team ran). The prior expected the rule to hold as a Serre-Tate restatement, the non-split recovery to be Smart's theorem, and the split-lift rate to sit at 1/p. The first two parts were concurred with. The third was partly overturned: 1/(p+1) is the matching null, and the rate does not hold per cell for deterministic sections."
- #"Controls. pert_p on its stated object recovers d on 2,052/2,052 rows per seed. The isomorphic re-model matches canonical. d = +-1 was excluded, with no small-p excess (p <= 19: 56 against 60.26 and 60.76)."
- #"Power. Per seed, the pooled test detects a uniform leak lambda/(p+1) at lambda >= 1.42 (50 %) and 1.52 (80 %). Against a 1/sqrt(p) leak confined to one section at p > 500, its power is 0.05. 68.5 % of the null mass comes from p <= 19."

== Inference
- #"Clauses 1 and 2 are true by derivation. The flag and the rule are one predicate on every unramified Z_p-lift of an ordinary anomalous curve. Agreement shows the instruments are correct; it is not a discovery. The prior art is Belding 2007, section 7."
- #"Clause 3 holds pooled only. The pooled next-digit rate matches the random-section null. For deterministic sections it fails per cell (counterexample: the Teichmuller section at p = 7), and the shortfall is a CM-automorphism deficit, not a leak. The next digit succeeds exactly when the section is d-homogeneous mod p^2 (4,214/4,214 rows)."
- #"The mechanism's recovery sentence needs the operative condition 'P has no torsion lift in E^(Q_p)', which equals 'E^[p] non-split' only because #E(F_p) = p. The red-team PTM-1 test on non-anomalous CM curves shows the detached sentence proves too much."
- #"Why support rather than refine. Every measurable prediction holds, and the scoped claim differs only in wording the frozen criteria never tested. Why replicated rather than strong: clause 3 rests on a pooled, post-hoc-corrected, low-power statistic, and the pert_p generator deviated (D2). No other gate applies: asymptotic_claim is null, so the coordinator.md promotion gates do not; the result is not surprising, so first-observation replicate does not; and it is not a breakthrough, closure or contradiction, so AGENTS.md rule 12 does not."

== Limitation
- #"Toy tier only: 29 class-number-one CM curves, p <= 1373, precision p^8, unramified lifts, three sections. Nothing transfers to non-anomalous curves, non-CM anomalous curves (red-team data only, p <= 211), ramified lifts, higher class number or cryptographic sizes."
- #"The j = 0 threshold 2e = 6 is not measured: over Z_p only (3, 6] is pinned."
- #"The large-p and single-section exclusions (panel C) are post hoc red-team readings, not frozen criteria."
- #"Deterministic sections are overdispersed (relative sd about sqrt(11/p)), so an i.i.d. binomial SE understates their variance unless the null is conditioned on the lift."
- #"Rows omit (P, d) and the lift coefficients, so replays depend on the producer's RNG draw order. check.py is not independent of the producer; independence rests on the validator's and the red team's own code."
- #"Katz (LNM 868) is a pointer verified bibliographically only. Smart 1999 is verified bibliographically and by its abstract, and is not cited for the canonical-lift statement."
- #"naive shows a same-sign excess over its exact null on both seeds (+1.59, +1.49). It is unexplained and below threshold, and at p > 500 naive has 1 success against 1.39 expected."

== Reviews composed
- #"Validation VAL-20261022-3232db (TASK-20261022-282b02): J1 holds, J2 breaks (definitional), J3 holds, PTM-1 holds."
  #link("../validation-20261022/validation_report.yaml")[#"reports/validation-20261022/validation_report.yaml"]
- #"Red team RT-20261023-0b2a4f (TASK-20261023-856638): R1 breaks (theorem plus prior art), R2 breaks (matching null 1/(p+1); j = 0 automorphism effect), PTM-1 holds."
  #link("../redteam-20261023/redteam_report.yaml")[#"reports/redteam-20261023/redteam_report.yaml"]
- #"Run reports: this experiment has no reports/run-*/ directory. The runs are read through their manifests and receipts under runs/RUN-CZLIFT-041d05/ and runs/RUN-CZLIFT-6709c9/."

== Next actions
+ #"Session: write analysis.md from the Coordinator's handback and confirm KN-FIND-3c7e19 is free. Run plot.py, compile this report and inspect it. Run tools/validate_ledger.py and tools/build_knowledge_index.py; INDEX.md is gitignored and is not staged."
+ #"Ledger archive TASK-20261023-4d7449, run alone, staging exactly the declared paths. Verify it, push, and open or refresh the ready PR naming EV-CZLIFT-712fe4, DEC-20261023-147f9f, KN-FIND-3c7e19 and CORR-20261023-9f2176."
+ #"Checkpoint GOAL-CZLIFT-1516d5 with one next action: compose the evidence decisions for EXP-CZLIFT-ae0a13, EXP-CZLIFT-a255fc, EXP-CZLIFT-ed8113 and EXP-CZLIFT-1a3453."
+ #"In the EXP-CZLIFT-ae0a13 review, apply exact per-(lift, section) nulls, the mu_6/mu_4 automorphism control and a large-p per-section statistic before any claim that no section leaks."
+ #"Bind every future CZLIFT contract to four requirements: record the lift coefficients and (P, d) per row, state the matching null for each definition, preregister a large-p per-section statistic, and measure section d-homogeneity mod p^2 directly."
+ #"Curate Belding 2007 (arXiv:math/0703906) as a KN-LIT entry, by an agent that reads section 7."

== Canonical graphs checked
#"knowledge/frontiers/ecdlp/ is the canonical graph set. No canonical graph depends on this decision: it records known theory at toy tier, with no cost claim and no frontier movement. The session lists the graphs it checks, unchanged, in the archive receipt."
