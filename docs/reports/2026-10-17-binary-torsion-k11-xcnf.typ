#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "Arial", size: 9.3pt)
= Four-channel weighted k11 binary m8 inputs
_17 October 2026 · formulation inputs on the same archived raw targets as k10_

*Question.* Can the verified 316-column weighted k11 base be represented by membership-constrained XCNF for all four raw preimages of one prime-subgroup target?

#image("2026-10-17-binary-torsion-k11-xcnf.svg", width: 100%)

*Frozen files.* Four gzip XCNF inputs, 2,778,714 bytes in total. Each has eight 11-bit base variables, six 61-bit intermediates, seven three-point equations and 11,328 exact coordinate-membership clauses. Channel constants and parent input digests are bound in `manifest.json`.

*Checks.* Independent parsing verifies gate definitions, every membership truth-table value, file hashes and target constants. Twelve seeded direct field evaluations check all 427 equation bits, three assignments per channel. Selected-channel counts agree with the earlier standalone circuit diagnostic.

*Boundary.* None of the new files has a supplied satisfying assignment. Gate counts are structural, and k10/k11 have different column counts. No solver regularity, runtime, relation yield, useful rank, full index-calculus cost or speed improvement has been measured. Point signs, poles and exceptional cases still need full-point checking.

*Records.* `research/icperf_binary_torsion_k11_xcnf_20261017/manifest.json` and `verification.json`.
