#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "Arial", size: 9.4pt)
= Matched four-channel binary m8 formula inputs
_17 October 2026 · same targets and circuit for a weighted base and local random control_

*Question.* Can the 316-column random control use the weighted candidate's exact 11-bit, four-channel XCNF formulation?

#image("2026-10-17-binary-torsion-k11-local-control-xcnf.svg", width: 100%)

*Frozen inputs.* Four new gzip formulas, 2,774,964 bytes. Both arms have 316 projected columns, 632 accepted raw values, 454 primary variables and 11,328 membership clauses per file. Their seven-equation gate counts match in every channel: 88,444 / 88,293 / 88,445 / 88,294.

*Checks.* Independent serialized parsing checks hashes, target constants, gate definitions and every membership truth-table value. Twelve direct field evaluations check the 427 equation bits, three assignments per channel.

*Boundary.* No control file supplies a satisfying assignment. No solver degree or time, relation yield, rank, full index-calculus cost or speed advantage has been measured. Point signs, poles and exceptional cases still need full-point certification.

*Records.* `research/icperf_binary_torsion_k11_local_control_xcnf_20261017/manifest.json` and `verification.json`.
