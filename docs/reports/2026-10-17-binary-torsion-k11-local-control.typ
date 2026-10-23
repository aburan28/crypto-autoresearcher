#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "Arial", size: 10pt)
= Same-width random control for the weighted binary base
_17 October 2026 · target-blind input preparation on one certified GF(2^61) curve_

*Question.* Can the 316-column weighted k11 base be paired with a random control using the same 11-bit coordinate block and exact membership cardinality?

#image("2026-10-17-binary-torsion-k11-local-control.svg", width: 100%)

*Construction.* The selected offset-4096 block has 1,024 torsion pairs. Sage and the producer independently found 511 liftable pairs; SHA-256 ranking under a fixed domain and seed selected 316. Both bases contain 632 accepted raw coordinates and require 11,328 eight-block membership-forbidding clauses. Their projected-column overlap is 194.

*Cost boundary.* The weighted scan attempted 1,276 raw coordinates; the local control scanned all 2,048. Charge each construction. Neither base has measured relation yield, solver degree or time, useful rank, full index-calculus cost or a speed claim.

*Next check.* Encode both bases on the same four target channels under one frozen solver protocol and verify full-point certificates, rank and complete costs. Source and replay: `research/icperf_binary_torsion_k11_local_control_20261017/`.
