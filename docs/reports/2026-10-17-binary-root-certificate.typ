#set page(paper: "us-letter", margin: 0.7in)
#set text(font: "Arial", size: 10pt)
#let title = "Binary m8 root-to-relation certificate check"
= #title
_17 October 2026 · ordinary binary curve over GF(2^61)_

*Question.* Does the archived planted 446-bit assignment for one torsion-coordinate m8 XCNF channel yield an exact curve-point relation?

#image("2026-10-17-binary-root-certificate.svg", width: 100%)

*Method.* Decode eight accepted factor-base coordinates and six intermediate coordinates. Check seven three-point field equations independently of the XCNF emitter. Lift each factor-base coordinate to both points, enumerate 256 sign choices, require equality to the selected raw target, and cofactor-project the resulting signed row into the certified prime subgroup.

*Recorded result.* One sign assignment sums to the raw target; its projected row has +1 in columns 0–7 and no other nonzero coefficients. Two single-bit perturbations keep base membership but fail the field equations. A separate Sage replay verifies this certificate's field equations, point sum and projected row; the earlier chain replay checks the target channels and torsion duplicate orbit.

*Limit.* This is a planted correctness control. There is no selected-formula solver search, relation yield, degree-of-regularity observation, rank measurement, linear algebra, target recovery, or complete IC cost here. The requested cross-family m=2–8 end-to-end improvement remains unmeasured.

*Artifacts.* `research/icperf_binary_root_certificate_20261017/certificate.json`; `research/icperf_binary_root_certificate_20261017/sage_replay.json`; `research/icperf_binary_circuit_xcnf_20261017/manifest.json`.
