#set document(title: "Decision report DEC-20261023-6931ab", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.8cm), numbering: "1 / 1")
#set text(size: 9pt)
#set par(justify: false, leading: 0.58em)
#show heading.where(level: 2): set text(size: 10.5pt)
#let vb(body) = block(fill: luma(244), inset: 6pt, radius: 3pt, width: 100%, body)

= Decision report: DEC-20261023-6931ab
#"EXP-CZLIFT-14f6d5 · H-CZLIFT-27a184 · RQ-CZLIFT-b9f765 · GOAL-CZLIFT-1516d5 · 2026-10-24"

== Status
#"Written by the coordinator subagent, which has no shell. plot.py draws graph.svg from plot_data.json, and the session compiles and inspects report.pdf. The decision is not official until the ledger archive commit (TASK-20261023-4d7449) carrying EV-CZLIFT-b6fe48, DEC-20261023-6931ab, analysis.md, the H-CZLIFT-27a184 update and this folder passes post-commit verification and is pushed to the PR branch."

== Decision
- *Decision:* #"weaken (one transition: H-CZLIFT-27a184 approved -> weakened)."
- *Evidence strength:* #"preliminary (EV-CZLIFT-b6fe48). The counts alone would be strong: exhaustive, deterministic, reproduced by three implementations. The weakening rests on derivations plus post-hoc, single-implementation reviewer comparisons. The record-versus-rank-7 comparison is not isolated from discriminant."
- *Claim tier:* #"toy (16 primes p = 103..20011, at most 15 bits; naive x-height <= 3e5)."
- *Refutation basis:* #"proof_status derivation (analysis.md D1-D4), with explicit instances in the red-team outputs, not yet packaged as certificates. The discriminant ordering (E1) and the uniform-null rejection (E2) are empirical."
- *Records:* #"EV-CZLIFT-b6fe48, DEC-20261023-6931ab, H-CZLIFT-27a184, EXP-CZLIFT-14f6d5, RUN-CZLIFT-ca7450 (hmax 1e5), RUN-CZLIFT-b1dce4 (hmax 3e5), VAL-20261022-2dd0e7 (TASK-20261022-a846f4), RT-20261023-174849 (TASK-20261023-7b5dc6), TASK-20261023-4d7449 (ledger archive), DEC-20261009-44c288 (its observation reading on uniformity is superseded at clause level), EV-CZLIFT-376eee (the counting obstruction this decision leaves unchanged)."

=== Exact scoped claim
#vb[#"On the reduced minimal models y^2 + xy + y = x^3 - x^2 - 6494556985832x + 6351402068900282539 (Grunewald-Zimmert 1977, rank >= 8) and y^2 + xy + y = x^3 - x^2 - 1608154463x + 25555312501831 (Brumer-Kramer 1977, rank >= 9), the number of rational points of naive x-height <= H, with O and +-P counted, is 5 and 215 at H = 1e5 and 11 and 311 at H = 3e5. On y^2 = x^3 - 10012x + 346900 (conductor 382623908456, rank >= 7) it is 1155 and 1559 (RUN-CZLIFT-ca7450, RUN-CZLIFT-b1dce4; exact, reproduced by three implementations). Modulo the 16 primes 103..20011, no coverage cell with n >= 30 has a ratio below 0.9966, so there is no gross subgroup confinement. No record-curve H_half at p >= 1000 is possible, because n < N_p/2 there. Within this window the counts order by discriminant, not rank. The run carries no information about rank as a variable, about c_E, about uniform reduction (a run-shaped null rejects it), or about lifting. Toy tier (EV-CZLIFT-b6fe48, DEC-20261023-6931ab)."]

#table(columns: (0.9fr, 0.9fr, 3fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*clause*], [*reading*], [*basis*],
  "S1 record-curve N_E below rank 7", "holds as observation; interpretation unsupported",
  "5 / 215 < 1155 (1e5), 11 / 311 < 1559 (3e5). The count is not an isomorphism invariant: the rank-7 curve translated by t = 1e6 has 3 / 5 (D3). Rank-0 11a1 (5) and 210e2 (16) match or exceed GZ (D4). Across seven rank >= 7 curves, Spearman against log|disc| is -1.00, and against rank -0.40 (E1).",
  "S1 parenthetical 'c_E falls with coefficient height'", "not measured",
  "c_E is an isomorphism invariant, and the counts are pre-asymptotic and model-dependent. Listed-sublattice regulators (3.75, 751, 497) explain about 6.3x of the GZ deficit of 231x; the naive-height window explains about 37x.",
  "S2 median in [0.8, 1.2]; every cell in [0.5, 1.5]", "met; upper side uninformative",
  "Frozen median 1.0419 / 1.0424; hypothesis cell set 1.0389 / 1.0380 (DISC-1); cells 0.9966..1.2593. The attainable maximum is 1.071 / 1.082 (D1). The lower edge excludes confinement of index about 4 or more. GZ supplies no cell.",
  "S3 frac above 1.5 < 0.05", "cannot fail",
  "Attainable maximum 6/131 = 0.046 and 7/156 = 0.045 (D1).",
  "S4 no record-curve H_half at p >= 1000", "cannot fail",
  "distinct <= n <= 311 < 468.9 <= N_p/2 (Hasse) (D2).",
  "Mechanism 'reduce uniformly / no structure'", "contradicted as stated",
  "Median 1.0424 against a nested uniform null of 1.0008 +- 0.0017 (0/400 reach it); top-cell collisions 4969 against 6142 +- 39. The same-height-rationals null, 1.0277 +- 0.0040, explains most of the excess (E2, post hoc).",
  "Generalisation to rank-record curves", "contradicted",
  "Elkies-Watkins rows of rank >= 8..11: N_E(1e5) = 1027, 1023, 743, 665. EW r >= 9 has 2281 against 2153 for the rank-7 curve at H = 1e6. Rank labels are lower bounds.",
)

== Observation
#"Validity, checked first. Both planned trials ran (ladder-h1e5, ladder-h3e5), and none was unplanned. Receipts are output_validated with returncode 0 and check_returncode 0, and 20/20 artifact hashes are bound. argv equals the frozen plan, dirty is false, and the seed is null with deterministic enumeration, as the specification requires. VAL-20261022-2dd0e7 recomputes every frozen metric, count, coverage cell and H_half table exactly, including from an independent enumeration; the red team's positive control agrees. Control C1 (rank-7 counts equal lane 1) holds, verified by the validator; check.py does not test it. The amendments folder is empty."
#figure(image("graph.svg", width: 100%), caption: [#"Panel A: N_E(3e5) per curve against log10|disc|, coloured by rank lower bound. Run curves are recorded (RUN-CZLIFT-b1dce4); Elkies-Watkins rows and 12-curve coefficient-matched random nulls are red-team values (rt_summary_output.json). Panel B: N_E(H) against H for the run curves (recorded), the rank-7 curve and EW rows to H = 1e6 (red team), the rank-7 curve in a translated model with the same discriminant (red team), and the rank-0 objects 11a1 and 210e2. Panel C: coverage median per run (131 / 156 frozen cells) against the frozen band, the region no point set can reach, uniform-draw nulls (400 reps, 2.5-97.5 percent), the nested uniform and same-height-rationals nulls (RUN-CZLIFT-b1dce4, 400 reps, 0.5-99.5 percent), and subgroup-confinement alternatives of index 2, 3 and 4. Panels D and D': the S3 and S4 clauses against their thresholds and attainable maxima. Exact counts carry no sampling error. Data: plot_data.json; drawn by plot.py."])

#"Recorded (raw-result.json, manifests). N_E at H = 10..3e5: rank-7 7, 17, 65, 113, 187, 329, 527, 783, 1155, 1559; GZ 1 (to 1e4), 3, 5, 11; BK 1, 1, 1, 1, 3, 7, 29, 113, 215, 311. |disc| = 1.22e13, 1.05e38 and 1.59e28. Coverage median 1.0419 (131 cells) / 1.0424 (156 cells), with frac above 1.5 and frac below 0.5 both 0. BK H_half: 3e4 at p = 103 and 149, 1e5 at 211 and 293, 3e5 at 419. GZ has no H_half. The frozen success criterion reads met on both trials, and no falsification clause fires."

#"Reviewer values (read by key). Elkies-Watkins rows of rank >= 8..11 have N_E(1e5) = 1027, 1023, 743, 665. At H = 1e6: rank-7 2153, EW r8 2149, EW r9 2281. Coefficient-matched random curves have N_E(3e5) of at most 9 at rank-7 size and 1 at record sizes. Translation instances of N_E(1e5): rank-7 1155 -> 3 (t = 1e6); GZ 5 -> 29 (t = 1536898); BK 215 -> 13 (t = 1e6). Rank-0 objects: 11a1 at 5 for H >= 30 and 210e2 at 16 for H = 300..3e5. The DL-known progression kG passes the frozen criterion (1.0710 / 1.0825)."

== Comparison
- #"Frozen criterion: met on both trials; the frozen reading stands, and no amendment is made."
- #"Instrument power (D1, D2): S3, S4 and the upper edge of S2 are fixed by the counts. The evidence carried by 'criterion met' is S1 plus the lower edge of S2."
- #"S1 against its controls: the same curve in another model flips F1 (D3). Rank-0 curves pass S1 against GZ (D4). Only growth in H separates the objects: GZ goes 1, 3, 5, 11 over H = 1e4..3e5, while 11a1 and 210e2 stay flat."
- #"Counts against rank and discriminant: Spearman -1.00 against log|disc| and -0.40 against rank (N(1e5), seven curves). The BK/rank-7 ratio rises with H (0.055, 0.144, 0.186, 0.199), as a rank-helps reading predicts."
- #"Coverage against nulls: the median lies above every uniform band and outside the subgroup alternatives, inside the frozen band, and below the attainable maximum. The BK-only median of 1.0271 sits inside the same-height-rationals null."
- #"Prior (recorded in TASK-20261023-7b5dc6 before the red team ran): a regulator effect, with coverage inheriting the a255fc limit. Confirmed in direction. Model dependence and the window loss were not anticipated."

== Inference
#"Derivation note (analysis.md). D1: a cell ratio is at most min(x,1)/(1 - e^-x), with x = n/N_p. This exceeds 1.5 only for x in (0.875, 1.099), and its median over the frozen cells is at most 1.071 / 1.082. D2: H_half(p) needs distinct >= N_p/2 >= 468.9 at p >= 1000, while distinct <= n <= 311. D3: x -> x + t is a Q-isomorphism that preserves the discriminant, canonical height and c_E, but not the naive x-height, so N_E(H) at finite H is a property of the model. D4: a single-hmax count has rank-0 and rank >= 8 preimages, so it is rank-blind."
#"Reading: the two 1977 record curves carry few small-naive-height points in their reduced minimal models. The cause is large discriminants, with large regulators and a naive-height window that misses their small-canonical-height points, not higher rank buying fewer points. The hypothesis's measurable clauses hold as an observation. Its mechanism, its uniform-reduction clause and its generalisation do not. H-CZLIFT-27a184 is weakened."
#vb[#"Obstruction (EV-CZLIFT-b6fe48): q1 N_E(H) on the three named models: GZ 5 / 11, BK 215 / 311, rank-7 1155 / 1559 (exact). q2 model dependence: 3..1155 (rank-7), 5..29 (GZ), 13..215 (BK) over integral translations, and 665..1027 for EW rows of the same or higher rank. q3 coverage median 1.0419 / 1.0424, against an attainable maximum of 1.071 / 1.082, uniform 1.0008 +- 0.0017 and same-height rationals 1.0277 +- 0.0040. Measured by RUN-CZLIFT-ca7450 and RUN-CZLIFT-b1dce4 (q2, q3 computed by the red team). Scope: the three models, H <= 3e5, p = 103..20011, toy. Resource check (examined): Elkies-Watkins (small disc gives high rank with many small points) takes q1 and q2 as its hypothesis, so the lane is not closed for rank-record curves. Neither reading escapes the rank-independent counting bound of EV-CZLIFT-376eee: at least N_p/2 distinct global points, i.e. Omega(p) work against O(sqrt p) for rho."]

== Limitation
- #"Toy tier only. Three named reduced minimal models, two of them record curves. No transfer assumption is made."
- #"The adverse comparisons are post hoc, use one reviewer implementation and were not pre-registered. Red-team heights are floating point, and the regulators are of listed sublattices."
- #"Every rank label is a lower bound, including rank 7 (Elkies-Watkins footnote 3). No upper bound is established."
- #"The two trials are nested, not independent. check.py imports the driver and does not test C1. The manifests omit counts and h_half. Library versions and memory are not recorded."
- #"DISC-1 (saturation filter, upper median) is unstated in the specification, but changes no clause. The specification's LMFDB conductor bound (500000) is wrong (299,996,953); this is not load-bearing."
- #"The derivation is a written argument, not a machine-checked proof; the instances are not yet certificates."

== Review inputs
- #link("../validation-20261022/validation_report.yaml")[#"reports/validation-20261022/validation_report.yaml"] #"(VAL-20261022-2dd0e7: J1, J2, J3 and PTM-1 hold; verdict passed; DISC-1 disclosed)"
- #link("../redteam-20261023/redteam_report.yaml")[#"reports/redteam-20261023/redteam_report.yaml"] #"(RT-20261023-174849: R1, R2 and PTM-1 break; narrowest statement is an observation)"
- #"No earlier reports/run-* directory exists for this experiment; the run records are the manifests and receipts under runs/RUN-CZLIFT-ca7450 and runs/RUN-CZLIFT-b1dce4."

== Canonical graphs checked
#"knowledge/frontiers/ecdlp/index-calculus/KR-IC-cd159a.yaml (xedni and lifting to characteristic zero) was checked. It is a frontier record, not a graph, and it is unchanged: this decision is a toy-tier weaken with no cost claim and no closure. No canonical graph under knowledge/frontiers/ecdlp/ plots this quantity."

== Next actions
+ #"Session: write analysis.md from the returned text (it carries D1-D4, and should be archived no later than this decision). Run plot.py, compile and inspect report.pdf, then run tools/validate_ledger.py and tools/check_review_independence.py --batch. Run the ledger archive TASK-20261023-4d7449 alone, by exact path; verify it, merge origin/main, push, and open or refresh the ready PR 'evidence: EV-CZLIFT-b6fe48/DEC-20261023-6931ab'."
+ #"Goal checkpoint GOAL-CZLIFT-1516d5 (active). Keep one next action for the global-lift lane: the idea-generator dispatch named by DEC-20261023-26a6de, whose brief absorbs a rank-versus-discriminant arm (EW Table 2 rows r = 5..11, at least two per rank, plus the 1977 records and matched random curves; primary metric the canonical-height count N(T); translation-stability check; run-shaped coverage nulls with the per-cell cap; 210e2 as a standing proves-too-much row), ranked on merits."
+ #"Package the translation instance and the EW r >= 9 instance as certificates, re-checked by independent code (validator blind_sieve.py)."
+ #"Rank upper bounds by 2-descent, if rank labels become load-bearing."
+ #"File a correction for the specification's LMFDB conductor bound."
+ #"Synthesis task on RQ-CZLIFT-b9f765: add the record curves to scope, with every rank as a lower bound; drop 'growth exponent checks rank' for record curves; name the model for naive-height counts and add N(T); correct decision_target (a) and the 'rank is small' motivation; no 'Neron constant collapse' wording; LMFDB coverage to conductor 299,996,953."
+ #"Infrastructure ticket: define N_E, the cell filter and the median convention in specifications; an independent checker that evaluates C1; counts, h_half, library versions and memory in manifests."
