#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: none)

= K11 common-target input preparation

*2026-10-17 UTC · ordinary-binary GF(2^61), prime subgroup order 576460752557211763.*

The proposed EXP-ICPERF-018b0c remains `review_required` and unauthorized for solver execution. Two 316-column bases were fixed before the public target schedule. Eight distinct subgroup targets each have four cofactor preimages. The preparation archived 64 seven-link XCNF inputs, one per base, target, and raw channel. Four channels represent one subgroup target.

#image("2026-10-17-icperf-k11-common-target-inputs.svg", width: 100%)

*Replay.* The serialized checker validated 64 formula structures and target constants, both complete planted Boolean models and their point certificates. Independent Sage group arithmetic checked eight subgroup points and 32 raw channels. The first local replay had a redundant compressed-size metadata mismatch; Sage also initially hit a cache sandbox permission error. Both corrections are recorded, and no input bytes were overwritten.

*Boundary.* These are target-independent inputs and positive instrument controls. Solver recovery, natural useful relations, actual regularity, marginal rank, linear algebra, unseen target work, full index-calculus cost, and matched rho are unmeasured. Full receipts and exact SHA-256 bindings are in `docs/reports/2026-10-17-icperf-k11-common-target-inputs.md` and `experiments/EXP-ICPERF-018b0c/inputs/`.
