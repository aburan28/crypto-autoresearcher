#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "Arial", size: 9.3pt)
= Weighted k11 torsion-coordinate factor base
_17 October 2026 · target-blind input preparation over GF(2^61)_

*Question.* Can a paired Hamming cut bring a compact torsion-coordinate base near the first B for which the m=8 signed-multiset count reaches the prime-subgroup order?

#image("2026-10-17-binary-torsion-k11-weighted.svg", width: 100%)

*Frozen construction.* Four offsets 2048, 4096, 6144, 8192; retain `t=c⊕v` when the ten high bits of the eleven-bit free vector have weight at most five. The low bit is free, preserving every accepted `t,t⊕1` torsion pair. The predeclared choice minimizes the realized-column distance to the count threshold of 311, then offset.

*Observed input counts.* Each scan checks 1,276 candidate coordinates. The four projected-column counts are 294, 316, 321 and 304; offset 4096 supplies the selected 316. A deterministic equal-column paired-random control also has 316. Independent Sage replay checked all scans, selected projected points, pair signs, random control and 64 three-point formula controls.

*Derived count.* Compared with the prior B=267 base, the selected base has 18.35% more columns and 3.8186 times as many length-eight signed multisets. This is a count before group collisions, solver restrictions and duplicate relation rows; it is not relation yield or an end-to-end cost gain.

*Circuit input.* The selected k11 seven-equation circuit has 454 primary bits, 25,789 live AND gates and 62,655 live XOR gates, plus 11,328 exact membership-forbidding clauses. The prior k10 input has 446 primary bits, 25,093 AND, 61,020 XOR and 3,920 membership clauses. Three seeded direct field checks pass. Gate and clause counts do not price solver time.

*Next check.* Materialize matched selected/control formulations and measure solving degree, runtime, verified relations, useful rank and complete IC cost on frozen targets. The 11-bit cardinality predicate and four raw target channels must be priced.

*Artifacts.* `research/icperf_binary_torsion_k11_weighted_20261017/base.json`, `sage_replay.json` and `circuit_support.json`.
