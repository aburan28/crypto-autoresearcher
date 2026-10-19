#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "Arial", size: 9.2pt)
= All four binary m8 target-channel inputs
_17 October 2026 · ordinary binary curve over GF(2^61)_

*Question.* Can the chained m8 formulation be serialized for all four raw preimages of one prime-subgroup target under the cofactor map, in both the torsion-coordinate and raw-x input representations?

#image("2026-10-17-binary-all-channels-xcnf.svg", width: 100%)

*Frozen inputs.* Eight membership-constrained XCNF formulas: two selected-channel files reused by exact digest and six new target-constant variants. The same seven three-point equations and eight coordinate-membership predicates are present in every arm. The six new gzip files total 5,130,311 bytes.

*Checks.* Independent serialized-formula parsing covers every gate, every membership truth table and all file hashes. Twenty-four seeded direct field comparisons check the 427 output bits, three assignments per arm. The selected torsion arm retains its planted satisfying assignment and separate full-point certificate.

*Boundary.* Live gate counts are structural and the arms have different column counts and coordinate widths. No selected-arm solver search, degree-of-regularity observation, relation yield, useful rank, complete IC time or speed improvement has been established. Point signs, poles and exceptional branches remain outside the XCNF inputs.

*Records.* `research/icperf_binary_all_channels_xcnf_20261017/manifest.json` and `verification.json`; chart source `docs/reports/2026-10-17-binary-all-channels-xcnf-chart.py`.
