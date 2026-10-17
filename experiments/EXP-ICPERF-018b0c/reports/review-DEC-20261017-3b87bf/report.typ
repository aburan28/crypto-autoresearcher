#set page(paper: "a4", margin: (x: 18mm, y: 16mm))
#set text(font: "Arial", size: 9.5pt)
#set par(justify: true, leading: 0.62em)

= Inconclusive k11 solver-to-certificate review

*DEC-20261017-3b87bf · EV-ICPERF-54ac6b · strength: inconclusive · descriptive tier: medium.* H-ICPERF-195806 and EXP-ICPERF-018b0c concern one ordinary-binary GF(2^61) curve, a 60-bit prime subgroup, m=8 through seven chained S3 equations, and weighted versus local-random B=316 bases. This decision reports no measured end-to-end improvement.

== Observation

RUN-ICPERF-712e85 attempted two planted solver calls. Both were wall censored under a 300 s cap, with no accepted model or point certificate. Process wall was 300.015663 s (weighted) and 300.021396 s (local random), one call per arm with no recorded spread. RUN-ICPERF-1c8bfe attempted zero of 64 planned natural calls because the positive gate stopped the panel. The positive driver used 601.239487 s including 0.723282 s bundle packaging; the gated natural driver used 0.002668 s.

#image("diagram.svg", width: 100%)

*Figure.* Measured process wall against the declared 300 s cap (n=1 per arm; no uncertainty estimate) and attempted natural-call count. Sources: RUN-ICPERF-712e85 and RUN-ICPERF-1c8bfe raw files; TASK-20261017-b5d54d cost reconciliation.

== Comparison and review

The frozen positive condition required both checked planted certificates within the cap and a certified natural row. The negative condition required passed controls and proved exhaustion of all 64 natural calls. Neither condition was observed. Blind J0 reviewer TASK-20261017-93d17d reconstructed the schedule using gamma = x([r]P_source) = 70364449406991 but found that the permitted specification and fixture do not explicitly define gamma. Another literal pole choice changes admission. J1 matched prepared target coordinates under that interpretation; natural call order was unexercised. J2 found no executed accepted model. Its two false objects failed exact point checks, but the planned complete CNF/XOR/field checks were not performed. J3 and J4 hold only for bounded cost classification and inference. The old TASK-20261017-dfdf05 review remains advisory.

== Inference and limits

The instrument and finite-panel relation-feasibility predictions remain inconclusive. Wall censoring is not verified exhaustion. Natural yield, degree of regularity, useful rank, linear algebra, target solve, full index-calculus S, base advantage, and the matched-rho gap were not measured. The two arms have equal static clause and XOR counts under this encoding. Runtime dirty-tree state and runtime lock are absent; source and binary custody do not amount to execution proof. Sequential host wall samples are descriptive, with one-minute load about 23-24 before calls.

== Next action

Bind gamma symbolically and numerically in a new prospective protocol, independently regenerate the target panel, and give the reviewer complete Boolean false-object controls. Record the gamma gap in a separately scoped problem file. Keep the archived raw run and review bytes unchanged. The immutable observation report is at `reports/run-20261017T1437Z/report.md`; the replacement review is archived under TASK-20261017-46f47f and this decision under TASK-20261017-755aa4. No canonical performance graph is updated because this review yields no E2E measurement.
