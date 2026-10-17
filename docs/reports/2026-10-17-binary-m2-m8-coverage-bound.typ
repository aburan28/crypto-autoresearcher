#set page(paper: "us-letter", margin: 0.65in)
#set text(font: "Arial", size: 9.3pt)
= Signed-multiset coverage ceilings for binary m=2–8
_17 October 2026 · certified prime subgroup order 576,460,752,557,211,763_

*Question.* What fraction of uniform subgroup targets could an ideal m-term oracle represent from the prepared bases, before solver or rank costs?

#image("2026-10-17-binary-m2-m8-coverage-bound.svg", width: 100%)

*Exact bound.* For B sign-folded subgroup columns, unordered length-m multisets from their 2B signed values number $binom(2 B + m - 1, m)$. Distinct group sums are no more numerous. Thus the uniform-target coverage fraction is at most $min(1, binom(2 B + m - 1, m) / r)$. Group collisions, cancellations, invalid lifts, solver failure and duplicate rows can only reduce useful yield.

*m=8 values.* Prepared B=249 direct: 17.2124%; B=265 raw x: 28.2327%; B=267 torsion φ: 29.9713%. A hypothetical B=287 reference gives 53.2229%. At m=7, B=267 has an upper fraction of 0.4432%. These are derived ceilings, not measured relation success.

*Channel accounting.* All four raw channels project under the cofactor map to one subgroup target. Solving all four is needed for complete raw-lift coverage; their projected target coverage is not multiplied by four.

*Limit.* No solver work, degree of regularity, relation yield, useful rank, complete index-calculus cost or speed improvement has been measured. Source and exact integer counts: `research/icperf_binary_coverage_bound_20261017/bound.json`.
