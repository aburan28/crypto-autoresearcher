# Three lattice routes into ECDLP index calculus

User request, 2026-10-15: Explore the annotated approaches: (1) pairing reduction followed by lattice sieving, (2) endomorphism and isogeny lattices for factor bases and relation generation, (3) lattice-assisted polynomial solving using point-decomposition constraints.

This is an ideas/design search, not a request to launch a new scientific trial or to promote a research result. The earlier request authorizes publication and tracking in Crypto Auto Researcher. Preserve all prior runs and four open research tracks #2152–#2155 under parent #2151. Work from main 4446b91c2faf5760da623a3ea20d561f1acf56ca.

Deliver a substantive mathematical exploration of all three routes with primary-source provenance, exact assumptions, deductions distinguished from retrieved results, candidate mechanisms and minimal discriminating tests. Publication includes an editable diagram and an inspected PDF. Novelty remains unverified; no end-to-end speedup or ECDLP recovery is claimed.

Particular questions to examine:

- Embedding degree ord_r(q) depends on the working field and subgroup order. What can a same-field isogeny actually change in pairing/finite-field index calculus?
- If a known endomorphism acts as a scalar on a cyclic prime-order subgroup, which orbit-derived relation rows add rank after action constraints are included? Distinguish solver work-sharing from independent equations.
- Can relation yield and saturation be measured per new independent verified row, with every phase and exceptional denominator tracked?
- For an interval factor base of width B and m summands, how does expected relation scarcity B^m/r compete with the lattice determinant/root-size requirement? Can auxiliary equations be independent rather than multiples of the input polynomial?
- Use actual finite-field point recovery and subgroup checks in any proposed test: a zero of a summation polynomial need not supply rational points in the chosen subgroup.

No new GOAL is requested; no existing hypothesis or goal status is changed. Any proposed experiment stays unapproved until fully executable and canonically admitted. No inference backend probe or independent scientific review is claimed without actual receipts.
