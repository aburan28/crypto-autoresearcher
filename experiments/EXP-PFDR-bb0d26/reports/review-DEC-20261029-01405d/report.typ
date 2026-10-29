#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set par(justify: false)
= #"Decision report: DEC-20261029-01405d (EXP-PFDR-bb0d26, H-PFDR-727bfc)"

#"Evidence review of the five frozen runs of EXP-PFDR-bb0d26 (runbook session RBS-PFDR-bb0d26), composed by the Coordinator (TASK-20261029-5a5213) from review round REVIEW-PFDR-bb0d26-20261029. No run was launched for this review. Toy scope only: nothing here is a cost, exponent, attack, real-curve, security or asymptotic statement."

== #"Decision"
#table(columns: (auto, 1fr),
  [*#"decision"*], [#"support (scoped)"],
  [*#"evidence strength"*], [#"strong (predefined frozen protocol, controls passed, 50 to 1440 curves per cell, artifacts retained, stable effect; not replicated: no fresh-curve census)"],
  [*#"claim tier"*], [#"toy (max log2 p = 28)"],
  [*#"proof status"*], [#"empirical_only (declared); no certificates (no solve or relation is claimed)"],
  [*#"evidence / decision"*], [#"EV-PFDR-07d608 / DEC-20261029-01405d"],
  [*#"runs"*], [#"RUN-PFDR-e44a19, RUN-PFDR-4d8c71, RUN-PFDR-cd03e2 (citable as recorded); RUN-PFDR-243425, RUN-PFDR-089edc (scoped citability, see below)"],
  [*#"review tasks"*], [#"TASK-20261029-958053 (validator: J1 replay, J2 validity, J3 kernel), TASK-20261029-e5fe6b (blind re-derivation, J4), TASK-20261029-ff0453 (red team, J5 and proves-too-much); composition TASK-20261029-5a5213; archive TASK-20261029-25fc17"],
  [*#"review plan"*], [#"experiments/EXP-PFDR-bb0d26/review/review-plan.yaml and coordinator-prior.yaml, frozen in commit 1eddb4740b before any reviewer ran"],
)

*#"Scoped claim."* #"For x-labels of proper (relation-free) rank-r log-GAP half-boxes (r in {1, 2, 3}; fixed origin; one representative per +-c; lexicographic fill; T minimal by vector count) of n in {256, 512, 1024, 2048, 4096} labels, on generated prime-order ordinary curves of 20, 24 and 28 bits (main seed block 8,100,000 + c; 50 to 1440 curves per cell), the exact pair-sum (h = 2) coincidence count matches the matched uniform-label null within the preregistered 5% tolerance in 44 of the 45 toy cells: |kappa - 1| < 0.05 with every curve-cluster 95% interval inside [0.90, 1.10]. The observed |kappa - 1| is at most 0.041 overall and at most 0.009 at n >= 1024. Cell b20-r3-n4096 is not assessed, relation-bearing log-GAPs are untested, and support is for the 5% tolerance, not for exact random-set behaviour."

*#"Citability."* #"DEC-20261029-5554ee ruled RUN-PFDR-243425 and RUN-PFDR-089edc scoped, because no exact audit replay had been made of them. In this round, J1 made an exact audit replay of both under CPython 3.11.15 (the recorded interpreter version, uv build). Every measurement output was byte-identical, and the ruling's float tolerance was never needed. This decision does not overturn the ruling; whether to lift it is next action NA-6."

*#"Status transitions."* #"H-PFDR-727bfc: specified (file value) -> approved (DEC-20261022-f1efde, pre-run) -> execution recorded as observations (DEC-20261022-9aec2b, no status move) -> analyzed -> supported, scoped as above. The hypothesis file now reads supported, with approval_decision DEC-20261022-f1efde. EXP-PFDR-bb0d26: completed -> analyzed. This move is recorded in the decision only: the frozen specification is not edited, because trial-plan.json binds its bytes by sha256 and its own invalidation rule forbids post-approval byte changes."

#image("graph.svg", width: 100%)
#align(center)[#text(size: 8.5pt)[#"Figure 1. Top: kappa = S/M with the producer's curve-cluster bootstrap 95% interval for each of the 44 powered cells of RUN-PFDR-089edc analysis.json (dimensionless; 50 to 1440 curves per cell; colour = bit size), against the preregistered null band |kappa - 1| < 0.05 (0.95 to 1.05) and the interval band [0.90, 1.10]. Bottom: plant_kappa of the planted label AP per cell against the P2 threshold 1.15. b20-r3-n4096 is invalid (46 of 50 curves) and not shown. Source: RUN-PFDR-089edc (scoped citability per DEC-20261029-5554ee; exact 3.11.15 audit replay made in this round's J1); drawn by plot.py from plot_data.json."]]

== #"Observation"
- #"Run set valid: five runs in plan order, 53/53 receipt hashes, check.py exit 0 on all five under 3.11.15, and 1580 curves on the seed rule. There are 6657 job records: 6653 ok, 4 degenerate and 0 failed_infrastructure. census-toy-rep has 0 jobs because no cell was flagged (J2)."
- #"J1: analyze-main, analyze-final, selftest and census-toy-rep replay byte-identically under CPython 3.11.15. The 3.13.17 control reproduces the audit's float drift (2 summary leaves, 479 analysis leaves, within rel 1e-9, no non-float leaf). J3: 838/838 fields recounted by disjoint code on 15 ok and 4 degenerate nonce-sampled jobs."
- #"Recorded reading (RUN-PFDR-089edc): outcome O-NULL, headline SUPPORT_SCOPED, calibration n 44, mean -0.26757, sd 0.97357, pass; 44 cells null, b20-r3-n4096 invalid. Largest |kappa - 1| is 0.0414 (b28-r1-n256, CI [1.00996, 1.07428]); lowest CI bound 0.93684 (b28-r2-n512); largest |z| 3.131 (b24-r1-n2048). Smallest plant_kappa is 1.2885 (b20-r2-n4096) and smallest plant_z 21.9 (b24-r2-n256)."
- #"The four degenerate jobs of b20-r3-n4096 (c = 6, 30, 42, 47) each carry a short relation among the seeded base points (sup-norm 8 to 14), which exhausts the half-box. Every ok job has duplicate_skips 0."
- #"Not preregistered: across the 44 cells the log-GAP z values have sum of z^2 = 71.4 on 44 (p about 0.006), and six cells have |z| > 2. The A/A arms on the same cells give 44.9 (z_cal) and 40.5 (even/odd) on 44."

== #"Comparison"
#table(columns: (auto, 1fr, 1fr),
  [*#"quantity"*], [*#"recorded (RUN-PFDR-089edc)"*], [*#"blind re-derivation (TASK-20261029-e5fe6b)"*],
  [#"S per cell"], [#"44 integers"], [#"equal in all 44 cells"],
  [#"kappa, z, z_cal"], [#"per cell"], [#"equal at 6, 3 and 3 printed decimals in all 44 cells"],
  [#"class"], [#"44 null, 1 invalid"], [#"44 null, 1 invalid (same cells)"],
  [#"ci95"], [#"producer seed (not in the specification)"], [#"own seed; max endpoint difference 0.0034 (b24-r2-n256), inside the re-deriver's variant spread of 0.0039"],
  [#"calibration"], [#"-0.26757 / 0.97357, pass"], [#"-0.26757 / 0.97357, pass"],
  [#"outcome / headline"], [#"O-NULL / SUPPORT_SCOPED"], [#"O-NULL / SUPPORT_SCOPED"],
  [#"E[C] for a uniform n-set"], [#"3 binom(n,4)/p (specification)"], [#"C(L)(n)_4/(l)_4 exactly; 3 binom(n,4)/p (1 + O(1/p)); null mean / formula in [0.995, 1.008]"],
)
- #"Against the frozen predictions: P1 met on 44/44 powered cells (not assessed at b20-r3-n4096); P2 met on 44/44; P-detect not met; calibration gate met; O-NULL rule met at 44/45 valid."
- #"Proves-too-much (red team): plant read flagged in 44/44; invalid cell never read as null; no real-curve or asymptotic sentence in any record; A/A comparisons flag 0 (44 cells, 880 leave-one-out comparisons, 44 even/odd)."
- #"Against the coordinator prior: every expected finding met and no stop condition fired. Not anticipated: the over-dispersion, the flag-power error, the low gate power and the proper-GAP selection."

== #"Inference"
- #"H1 of H-PFDR-727bfc holds at the preregistered 5% tolerance in 44 of 45 toy cells, within the scoped claim above."
- #"The null is informative. In the weakest powered cell (b28-r1-n512), a true |kappa - 1| >= 0.079 would have read non-null with 95% probability. The plant is recovered everywhere, and the A/A arms stay at nominal."
- #"The measured property is h = 2 additive energy. An additive label predicate for these label sets is not supported at these sizes, beyond planted-type label-AP substructure of about 2 to 47 labels (a scaling estimate). The specification's \"label-describable\" and \"implicit-membership route not opened\" consequences are not adopted. The IDEA-20261017-bbc53e base was not tested, and KN-OPEN-020 stays open."
- #"The over-dispersion is unexplained (chance after look-elsewhere, or a small cell-specific effect below the tolerance). It changes no class."

== #"Limitation"
- #"Toy scope only (p of 20 to 28 bits, n 256 to 4096, generated curves, x-labels). The held real-curve extension (HU-5) is untested."
- #"Relation-bearing (improper) log-GAPs are excluded, not missing at random. The four drawn ones were removed unmeasured, and b20-r3-n4096 is not assessed."
- #"The unpreregistered z over-dispersion (sum of z^2 71.4 on 44, p about 0.006) needs a look-elsewhere correction."
- #"The specification's flag-power sentence (\"above 0.95\" at a true 10% excess) is mistaken: the figure is about 0.50, given the |kappa - 1| >= 0.10 conjunct. O-NULL is protected, because a true 10% excess reads intermediate."
- #"The calibration gate is weak: P(pass) is 0.40 at a true sd of 1.3 and 0.36 at a mean shift of 0.4."
- #"There is no positive control in which group structure induces label structure."
- #"Page 1 of the run report prints commit 98ab4496, the runbook session's opening commit, not the runs' code commit 48bd193a. The diff between them is empty for this experiment."
- #"No execution proof (execution-proof-chain milestones open). Single run set; one model family served producer, reviewers and Coordinator, so session independence is attested and model independence is not claimed."

== #"Next actions"
+ #"NA-5 (first, top-level session): write analysis.md and KN-FIND-c81e5b verbatim from the composition handback, render this report, validate, then run the ledger archive TASK-20261029-25fc17 alone, push, open the PR and enable auto-merge, and checkpoint GOAL-PFDR-fd09e0."
+ #"NA-1 (lane single next action): the cheapest falsification control, by protocol amendment. Count coincidences on the four recorded degenerate triples of b20-r3-n4096 (c = 6, 30, 42, 47) against matched-size random label sets on the same curves."
+ #"NA-2: replicate the six |z| > 2 cells on the replication block (seed 8,200,000 + c), by protocol amendment."
+ #"NA-3: HU-5 (admit or decline the held real-curve extension) stays with the user."
+ #"NA-4: pointer for TASK-20261029-1bcf80. The uv CPython 3.11.15 interpreter lacks PyYAML, which manifest writing needs, so a replay contract should name it."
+ #"NA-6, NA-7, NA-8: consider lifting the scoped citability; make record-fidelity corrections as new records; measure the bbc53e base and translated boxes before any statement about them."

== #"Related reports and graphs"
- #"Earlier run report:" #link("../run-20261023T2211Z/report.pdf")[#"reports/run-20261023T2211Z/"] #"(unchanged; it records what ran and states no verdict)."
- #"Canonical graphs checked: no canonical graph source or rendering cites EXP-PFDR-bb0d26, H-PFDR-727bfc or the five runs, which agrees with the grep of DEC-20261029-5554ee. All were left unchanged. Two lead records that mention H-PFDR-727bfc (LEAD-ICP-coincidence-harvest-structured-base.yaml, coverage.tsv) are not graphs and were left unchanged."
