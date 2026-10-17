# Exact m=2…8 inputs for the selected 896-coset base

**Status:** frozen algebraic inputs and independent planted-equation replay, 2026-10-17 UTC. The [system record](../../research/icperf_prime_coset_896_system_20261017/systems.json), SHA-256 `e5bc89daa181eac56e5a854895bfb366e5ffe3ca4d83b9e04930f232251ff72f`, contains every coefficient, exponent, target point and planted assignment for `m=2…8`. The [editable chart source](2026-10-17-prime-coset-896-system-chart.py), [SVG](2026-10-17-prime-coset-896-system.svg), and [PDF](2026-10-17-prime-coset-896-system.pdf) compare exact input counts with the earlier 788-coset candidate. No Gröbner run, observed degree of regularity, natural relation, useful rank, target logarithm, or end-to-end speed is reported.

## Fixed input and equivalence mechanism

The [target-blind 16-seed search](2026-10-17-prime-coset-896-search.md) selected a 475-point base at seed `20261027` on the certified prime-order curve with `p=9223372021248595841` and `r=9223372018953067627`. Its x-coordinates are the liftable members of a multiplicative coset of order `d=896`; the other **421** coset x-values are not curve points. The base record and its independent Sage replay identify every accepted x. A solver root satisfying the coset equation must still pass a curve lift and point-sign check.

The [builder](../../tools/icperf_prime_coset_896_system.py) calls the generic [quadratic-lift encoder](../../tools/icperf_prime_coset_quadratic.py) with the frozen base, fixed separating-form seed `20261017`, and the known sum of the first `m` base points as a correctness control. The direct system has `x^896−c` for each of the `m` summands, chained quartic Semaev `S3` equations and one separating form. The lifted system replaces each degree-896 coset equation with the 11 multiplication gates in the addition chain `1,2,3,6,7,14,28,56,112,224,448,896`, plus its terminal constant equation. Induction on the gates gives `q_e=x^e`, so projection onto the original variables recovers the direct coset condition. The S3 equations and separating form are carried over. This construction is a **chained-S3** input: direct `S8` has seven summands plus target, while direct eight-summand elimination requires `S9` or another construction.

## Serialized input counts

The table gives variables / equations / monomial occurrences. Monomial occurrences sum nonzero terms in the input polynomials; they are not Gröbner matrix entries. Direct input degree is 896 for every row, and lifted maximum input degree is four because the retained S3 chain is quartic.

| m | Direct d=896 | Lifted d=896, B=475 | Prior lifted d=788, B=380 |
| ---: | ---: | ---: | ---: |
| 2 | 3 / 4 / 16 | 25 / 26 / 60 | 27 / 28 / 64 |
| 3 | 5 / 6 / 33 | 38 / 39 / 99 | 41 / 42 / 105 |
| 4 | 7 / 8 / 50 | 51 / 52 / 138 | 55 / 56 / 146 |
| 5 | 9 / 10 / 67 | 64 / 65 / 177 | 69 / 70 / 187 |
| 6 | 11 / 12 / 84 | 77 / 78 / 216 | 83 / 84 / 228 |
| 7 | 13 / 14 / 101 | 90 / 91 / 255 | 97 / 98 / 269 |
| 8 | 15 / 16 / 118 | 103 / 104 / 294 | 111 / 112 / 310 |

The new base realizes 95 more columns while its lifted m=8 input has eight fewer variables and equations and 16 fewer monomial occurrences. This is an exact **representation** difference between unequal-size bases. It does not establish lower degree of regularity or faster solving, and a larger base may raise relation-collection or linear-algebra cost. The direct d=896 equation has a higher exponent even though the fixed square-and-multiply chain uses one fewer gate per x.

## Independent replay and boundary

The independent [Sage checker](../../tools/icperf_prime_coset_896_system_sage_verify.py) read the frozen system and base scan, checked source/input SHA-256 bindings, reconstructed the first `m` point sum at each arity, checked all gate powers and coset membership, and evaluated every serialized polynomial over `GF(p)`. Its [write-once replay](../../research/icperf_prime_coset_896_system_20261017/sage_replay.json) reports **70/70 direct and 455/455 lifted equations zero**, with an altered auxiliary value violating two lifted equations at each `m=2…8`. SageMath 10.10.rc0 emitted a version-function deprecation warning; the replay completed. These are known-point planted controls, so no unplanted relation rate follows.

| Phase | Current evidence | Remaining requirement |
| --- | --- | --- |
| Setup and base | Full 16-attempt d=896 scan, 475-point selected base and independent point replay. | Cold and reused setup prices, including rejected seeds and field selection, in a matched run. |
| Decomposition input | Exact direct/lifted systems and independent planted check for all seven arities. | Approved bounded solver trials on unplanted and planted targets, equal-realized-size random/small-x controls, observed degree/time/RSS, all-root point certificates. |
| Relations, rank and target | No natural row or unknown-target solve from this input. | Yield and misses, deduplicated marginal rank, linear algebra, unseen same-point target work and independent replay. |
| Whole-cost comparison | No candidate/baseline speed measurement. | Complete exclusive phase costs, memory, cold and genuinely amortized setup, matched best IC baseline and rho. |

The next discriminating experiment freezes a same-curve **475-point random base and 475-point small-x base**, the direct and lifted d=896 systems, the earlier 380-point d=788 arm as a separate size/cost comparison, resource limits and point-checking rules before running. Its first gate measures actual solver degree, time and RSS and retains censored attempts; any surviving arm must continue through useful rank and unknown-target recovery with full-cost accounting. The [full-width measurement problem](../../problems/full-width-ic-arity-grid-unmeasured.md) remains open.

**Graph custody:** the [canonical ECDLP frontier](../../knowledge/frontiers/ecdlp/README.md) was checked. These correctness and structural inputs do not change a reviewed cost finding, so its source and rendering remain unchanged. Provenance of the numerical claims here is `internal`: linked source, immutable input and independent Sage replay; no literature claim is inferred.
