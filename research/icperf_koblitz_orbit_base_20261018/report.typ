#set page(paper: "a4", margin: 13mm)
#set text(font: "Libertinus Serif", size: 9pt)
#set heading(numbering: "1.")

= Target-blind Koblitz Frobenius-orbit factor-base input screen

_2026-10-18. Exact finite input construction; no solver or end-to-end cost claim._

== Fixed public input and method

The certified curve is $y^2 + x y = x^3 + x^2 + 1$ over `GF(2^73)`, represented by $z^73 + z^25 + 1$. Its target prime subgroup has order `r = 5,384,682,420,498,870,703` (`log2(r) ≈ 62.224`), with cofactor 1,754. The fixture and independent subgroup certificate are in `research/icperf_koblitz_subgroup_fixtures_20261017/`.

The producer examined raw $x$ coordinates 1 through 512 before any target selection. Each liftable point $P$ was projected to $F = [1754]P$. It kept one representative per distinct full Frobenius $x$ orbit. For each 73-element orbit it computed the exact minimal polynomial over F₂. It greedily chose five orbits to minimize the nonzero coefficient count of their product, with ties resolved by raw $x$. The base has 365 materialized representatives and implicit negatives; its five raw seed coordinates are 498, 442, 41, 299, and 25.

== Exact finite observations

Of 512 raw coordinates, 278 did not lift, none projected to the identity, and 14 duplicated an earlier projected $x$ orbit, leaving 220 distinct candidates. The selected membership polynomial has degree 365 and 157 nonzero F₂ coefficients. Its supported exponents have maximum binary Hamming weight 7. The first five eligible orbits give 211 terms; 32 seeded five-orbit controls from the same pool give 163 to 203 terms, median 185. These are algebraic input counts, not solver timings or a performance claim.

#image("../../docs/reports/2026-10-18-koblitz-orbit-base.svg", width: 92%)

The one-process construction wall was 39.628324 seconds, a descriptive setup observation. The exact bytes, selected points, controls, and source hash are in `research/icperf_koblitz_orbit_base_20261018/base.json`. Sage independently replays group identities, the finite candidate pool, polynomial coefficients, selection, and controls in `sage_replay.json`.

The 365 coordinates have at most 730 signed points. For an unordered eight-term sum with repetition, the exact multiset ceiling is $binom(737, 8) = 2,078,085,779,887,029,220$, or 0.385925412 times $r$. The upper fraction across all arities one through eight is 0.390154731. Even a perfect solver on one unshifted five-orbit base cannot cover every subgroup target. Six full orbits have 438 coordinates and pass this necessary count threshold, but actual coverage remains unmeasured; shifts, extra bases and retries must be charged.

== Group and phase binding

The subgroup Frobenius action is $tau(P) = [lambda]P$ with `lambda = 1,069,606,243,985,175,817 (mod r)`. The producer checked `lambda^2 - lambda + 2 = 0 (mod r)`, `lambda^73 = 1 (mod r)`, the generator identity, and all selected full-point identities. A later relation must retain its five unknown orbit logs and every relative phase. The raw points were chosen by $x$ and cofactor projected; the construction supplies no discrete logarithms.

== Limits and next check

The 157-term equation has degree 365. Its term count gives no measured degree of regularity, sparse solver cost, relation yield, useful rank, linear algebra, target work, or complete index-calculus time. The earlier complete Koblitz comparison uses a different curve and a 45-bit target subgroup, so it is not a timing baseline for this 62-bit subgroup. If a later solver uses raw-point predicates, it must include the cofactor and relevant torsion target channels.

A frozen experiment should retain this sparse five-orbit base and equal-size orbit controls, then construct a six-orbit arm before assessing target coverage. Compare chain-of-$S_3$ and direct $S_8$ seven-summand systems, and chain or $S_9$ eight-summand systems. Continue through natural relations, rank, target reconstruction, all charged costs, and matched rho before selecting an end-to-end winner. Timeouts remain censored.

_Source and provenance:_ `tools/icperf_koblitz_orbit_base.py`, `research/icperf_koblitz_orbit_base_20261018/{base.json,sage_replay.py,sage_replay.json}`, and `docs/reports/2026-10-18-koblitz-orbit-base.md`. All are internal artifacts. The canonical ECDLP frontier graph remains unchanged because no reviewed attack-cost edge was established.
