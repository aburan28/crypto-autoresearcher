# Target-blind 896-element prime coset search

**Status:** exact input preparation and independent Sage replay, 2026-10-17 UTC. This is a substantive factor-base search round on one certified 63-bit prime-order curve. It measures no natural decomposition, degree of regularity, Gröbner cost, useful relation rank, target logarithm, or end-to-end speed. The [editable chart source](2026-10-17-prime-coset-896-search-chart.py), [SVG](2026-10-17-prime-coset-896-search.svg), and [PDF](2026-10-17-prime-coset-896-search.pdf) show the full frozen seed scan. The [scan record](../../research/icperf_prime_coset_896_20261017/scan.json) retains all point lists and preparation receipts; its SHA-256 is `ea1959cee947aa1c740c158250de10c1a73f718b481d5194150f462fa8e395e0`.

## Question and frozen method

The previous [788-element coset input](2026-10-17-prime-coset-quadratic.md) realizes 380 x-coordinate columns. Its signed eight-term multiset count covers at most 31.048916% of uniformly drawn subgroup targets before collisions. For the [certified prime curve](../../research/icperf_prime_fixtures_20261017/n63_seed20261017.json), `r=9223372018953067627` and the smallest base size whose optimistic eight-term count reaches `r` is **441**: `C(887,8)<r≤C(889,8)`. The same field admits `d=896 | p−1`, with `p=9223372021248595841`.

Before viewing any candidate output, the [scan program](../../tools/icperf_prime_coset_896_scan.py) fixed divisor 896, target size 441, `kind=subgroup`, and the **16 consecutive seeds 20261017…20261032**. The existing [explicit-divisor constructor](../../tools/icperf_explicit_base.py) generated each full coset and retained every on-curve point, exact coset parameters, root-draw count, source/input hashes, git/dirty-state receipt, constructor wall/CPU time and process peak RSS. Missing lifts are exactly reconstructible from the 896-element coset and the accepted list; the Sage replay performs that reconstruction. Each attempt is included in the write-once record, including candidates below the threshold. Selection uses the largest realized point count, breaking ties toward the lowest seed. It uses no target or decomposition result.

## Observed preparation and exact counting

| Seed suffix | Realized columns | Above 441 count threshold? | Root draws |
| ---: | ---: | :---: | ---: |
| 17 | 452 | yes | 2 |
| 18 | 450 | yes | 1 |
| 19 | 438 | no | 1 |
| 20 | 452 | yes | 1 |
| 21 | 440 | no | 1 |
| 22 | 446 | yes | 6 |
| 23 | 444 | yes | 2 |
| 24 | 424 | no | 1 |
| 25 | 455 | yes | 2 |
| 26 | 459 | yes | 5 |
| **27** | **475** | **yes** | **2** |
| 28 | 439 | no | 1 |
| 29 | 440 | no | 4 |
| 30 | 417 | no | 1 |
| 31 | 411 | no | 5 |
| 32 | 446 | yes | 1 |

Nine of 16 candidates clear the **necessary counting threshold**. Seed `20261027` has the largest realized base: 475 distinct on-curve x-coordinates, with point digest `8eefb8a3ab4fa01757759a92b8ef77f53d01168ec223a2f89193a972492108ca`. Its signed eight-term multiset upper count is `C(957,8)=16,944,744,476,780,007,525`, or 1.837153 times `r`. Distinct multisets may sum to the same point, so this ratio cannot establish full target coverage. For seven summands on this *same* 475-column base, the uniform-target coverage ceiling is only 1.535760%; direct `S8` remains a seven-summand arm, while eight summands require `S9` or a chained formulation.

The 16-attempt scan took **18.765831 s wall and 0.829370 s process CPU** on this host. The sum of individually timed constructor calls is 0.370852 s wall, which excludes each call's fixture check, point-list verification, git subprocesses and interpreter overhead. The scan wall time includes those repeated checks but excludes the separate Sage replay, source development, earlier field/curve selection and any future solver or target work. Its process peak RSS observations are in the record (maximum 34,865,152 bytes). These are descriptive setup measurements under current host load, not a controlled candidate-versus-baseline speed comparison. A complete panel must charge the entire seed search or demonstrate actual reuse across targets.

The independent [Sage replay source](../../tools/icperf_prime_coset_896_sage_verify.py) read the frozen record, checked the 896-order root in each attempt, enumerated **14,336** coset x-values, independently tested their curve liftability, checked every stored point and point-list digest, and recomputed the selection and count threshold. Its [write-once result](../../research/icperf_prime_coset_896_20261017/sage_replay.json) binds the scan and checker hashes and reports seed `20261027`, size 475. SageMath 10.10.rc0 emitted only a version-function deprecation warning during this replay.

## Algebraic input implication and remaining comparison

The prior [quadratic-lift implementation](../../tools/icperf_prime_coset_quadratic.py) uses a 12-gate addition chain for exponent 788. Calling its generic `lift_system` and `serialize` functions on the selected 896-coset point list and the sum of its first eight points, with seed `20261017`, gives an **unreviewed local structural diagnostic**: 11 multiplication gates per x, direct input 15 variables / 16 equations / 118 monomial occurrences / maximum degree 896, and lifted input 103 / 104 / 294 / maximum degree 4. The fixed binary chain for 896 is `[1,2,3,6,7,14,28,56,112,224,448,896]`. These counts need a frozen system record, independent planted-equation replay and matched solver execution before any inference about degree of regularity or cost. The larger base also increases relation and linear-algebra work; a shorter gate chain alone is not an end-to-end improvement.

| Stage | Current evidence | Remaining requirement |
| --- | --- | --- |
| Curve and base setup | Certified 63-bit curve; complete target-blind 16-seed scan; independent exact point replay. | Charge field selection, all seed attempts and validation in cold and genuine amortized cost. |
| Algebraic input | Locally derived m=8 direct/lifted counts for the selected base. | Frozen exact system, independent equations/point check, bounded direct/lifted and equal-realized-size control solves across m=2…8; observed degree, time and RSS. |
| Relations and rank | None from this base. | Natural certified relations, misses, duplicate/sign handling and independent marginal rank. |
| Target and rho | Optimistic signed-multiset counts only. | Unseen same-point target recovery, all retries/shifts/bases and phases, independent replay, matched IC baseline and rho. |

The next discriminating test should compare the selected 475-point base with an equal-realized-size random and small-x base on the **same curve and targets**, preserving the 380-point predecessor as a separate size/cost arm. It must distinguish direct `S8` (seven summands) from eight-summand `S9` or chained `S3`. Start with an approved bounded formulation/solver check and point certificates; progress to complete relation/rank/target accounting only on a frozen protocol. Censored runs remain censored. The [full-width measurement problem](../../problems/full-width-ic-arity-grid-unmeasured.md) remains open.

**Graph custody:** the [canonical ECDLP frontier](../../knowledge/frontiers/ecdlp/README.md) was checked. This search adds no reviewed whole-cost result, so its graph source and rendering remain unchanged. All numerical findings here have `internal` provenance from the linked record, source and Sage replay; the 441 threshold and signed-multiset counts are exact derivations, and the algebraic input counts are explicitly unreviewed local diagnostics.
