#set page(paper: "a4", margin: 13mm)
#set text(font: "Libertinus Serif", size: 9pt)
#set heading(numbering: "1.")

= Six-orbit Koblitz factor-base input screen

_2026-10-18. Target-blind finite input construction; no solver or ECDLP cost claim._

== Fixed input and selection

The certified curve is $y^2 + x y = x^3 + x^2 + 1$ over `GF(2^73)` with a 62.224-bit prime subgroup of order `r = 5,384,682,420,498,870,703`. The parent screen examined raw $x=1..512$ before targets were chosen and retained 220 full 73-element Frobenius orbits. This successor fixes its candidate pool and first five greedy choices, then adds one orbit minimizing the nonzero F₂ coefficient count of the membership-product polynomial, ties by raw $x$.

The sixth raw seed is 63, after 498, 442, 41, 299 and 25. The six orbits give 438 distinct subgroup $x$ coordinates and implicit point negatives. Each orbit has one unknown log plus known relative Frobenius phases.

== Exact finite observations

The degree-438 membership polynomial has 185 nonzero F₂ coefficients and maximum binary exponent weight 8. The first six eligible orbits give 209 terms. Thirty-two predetermined equal-size random controls give 205 to 253 terms, median 219. These are input counts on one fixed pool, not observed solving degree or running time.

#image("../../docs/reports/2026-10-18-koblitz-six-orbit.svg", width: 90%)

The parent scan and five-orbit step took 39.628324 seconds in its process; this incremental step took 1.736046 seconds in another. Both are descriptive setup costs. The exact record and source hashes are in `research/icperf_koblitz_orbit_six_20261018/base.json` and its parent. An independent Sage replay rescanned all 512 raw coordinates, rebuilt minimal polynomials, reproduced the six choices and controls, and checked all 438 full points, roots, phases and group identities.

== Counting limit and next test

There are at most 876 signed points. The exact eight-term multiset ceiling is $binom(883, 8) = 8,878,803,331,971,075,426$, 1.648900091 times $r$. Passing that necessary count threshold gives no actual target coverage. At seven summands, the ceiling is only 0.014939072 times $r$. Extra target shifts, bases and retries must be charged.

The next frozen comparison needs same-size controls, planted certificates, chained $S_3$ versus direct $S_8$ for seven summands, and separately labeled chained eight-summand versus direct $S_9$ formulations. Measure observed solver degree, time and memory, natural relations and rank, linear algebra, unseen-target work, cold and reusable setup, and matched strengthened-Frobenius rho. Censored runs stay censored.

_Provenance:_ Internal source, immutable input, independent Sage replay, and limits are detailed in `docs/reports/2026-10-18-koblitz-six-orbit.md`. The canonical ECDLP frontier graph gains no verified attack-cost edge from this input screen.
