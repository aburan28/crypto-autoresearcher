#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "Arial", size: 9.4pt)
= Full-point certificate interface for k11 binary inputs
_17 October 2026 · exact checking of Boolean roots against raw curve targets_

*Purpose.* Bind either 316-column k11 XCNF base and any raw channel, then turn a complete primary assignment into a full-point certificate or a scoped rejection.

#image("2026-10-17-binary-k11-root-certificate.svg", width: 100%)

*Checks.* Exact membership, seven field equations, eight curve lifts, all 256 point-sign masks, exact raw target sum and the signed projected subgroup row. Incomplete or contradictory solver models are rejected.

*Independent controls.* Two synthetic targets were constructed from eight known points, one per base and separate from archived evaluation targets. Python accepted one sign mask and one projected row for each base under all four channel labels; a bit flip failed. Sage independently checked both seven-equation chains, 256 signs each and subgroup projections. Eight all-zero archived-target inputs fail their equations.

*Boundary.* The archived target has no supplied k11 solver root. These are checker correctness controls; no relation yield, degree of regularity, useful rank, complete IC cost or speed improvement has been measured.

*Records.* `research/icperf_binary_k11_root_certificate_20261017/synthetic_controls.json` and `sage_replay.json`.
