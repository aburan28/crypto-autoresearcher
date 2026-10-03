# Membership audit TASK-20260911-1b89d4

Terminal state: `completed_valid`. Completed 8/8 frozen cases.

Observed finite raw membership is tested separately from rational-point and prime-subgroup eligibility. Every truth table enumerates all coordinate words. The emitted CNF uses exact definitional selectors; its checker verifies that each input uniquely determines every selector before evaluating the final disjunction. No solver or target logarithm is computed.

| n | width | assignments | raw words | rational x | rational points | subgroup x | subgroup points | CNF clauses | trie nodes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | 1 | 128 | 8 | 8 | 15 | 7 | 14 | 50 | 36 |
| 7 | 2 | 128 | 15 | 15 | 29 | 7 | 14 | 43 | 58 |
| 7 | 3 | 128 | 29 | 15 | 29 | 7 | 14 | 36 | 93 |
| 19 | 1 | 524288 | 20 | 1 | 1 | 0 | 0 | 362 | 210 |
| 19 | 2 | 524288 | 39 | 1 | 1 | 0 | 0 | 343 | 382 |
| 19 | 3 | 524288 | 77 | 20 | 39 | 0 | 0 | 324 | 693 |
| 19 | 4 | 524288 | 153 | 77 | 153 | 38 | 76 | 305 | 1254 |
| 19 | 5 | 524288 | 305 | 153 | 305 | 57 | 114 | 286 | 2263 |

`point_sets.json` retains every raw coordinate word, multiplicity, rotation orbit, rational/subgroup point and rejection. `negative_controls.json` retains a rejected single-window witness for every width and the invertible wrong-basis witnesses. `truth_table_hashes.json` hashes every ascending full-domain 0/1 table. `representations.json` contains the actual CNF clauses, DIMACS text and complete tries.

Construction and validation times are measured producer implementation costs, not SAT-solving or attack costs. Normal-coordinate conversion and the additional rational/subgroup work have separate measurements and operation counts. Rational/subgroup CNF sizes remain unavailable: raw membership CNF/trie sizes do not represent complete factor-base membership. Public subgroup enumeration has a separate construction cost; no point-to-scalar labels are retained.

The degree-7 control independently enumerates every y, and the degree-19 control compares against a complete public-generator cycle built with a separate addition and polynomial multiplication implementation. These internal implementation controls do not replace independent review.

The dependent 105-partition SAT integration gate is **unrun and not authorized** by this protocol. There is no full decomposition PASS, scientific status transition, asymptotic transfer, novelty claim, or fixed-target free-rotation assumption.

Implementation deviations: none to the scientific protocol. Memory protection uses bounded allocations and self peak-RSS checkpoints; no hard OS memory limit is asserted. Exact resolved model identity is unavailable and recorded null/unverified. Producer snapshot and independent review remain Coordinator work.
