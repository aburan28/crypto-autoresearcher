# Quadratic lift of a 63-bit prime-field coset input

**Status:** exact formulation and independent planted-input check, 2026-10-17 UTC. This is an input-preparation observation. No Gröbner basis of the archived m=8 system, degree of regularity, natural relation, useful rank, target logarithm, or end-to-end cost has been measured. The [editable chart source](2026-10-17-prime-coset-quadratic-chart.py), [SVG](2026-10-17-prime-coset-quadratic.svg), and [PDF](2026-10-17-prime-coset-quadratic.pdf) show structural counts only. The [serialized system](../../research/icperf_prime_coset_quadratic_20261017/system.json) is the primary record.

## Input and mechanism

The [certified 63-bit prime-order fixture](../../research/icperf_prime_fixtures_20261017/n63_seed20261017.json) has field characteristic `p=9223372021248595841` and group order `r=9223372018953067627`. The archived, target-blind [m=8 factor base](../../research/icperf_explicit_divisor_20261017/n63_m8_subgroup_seed20261017.json) contains 380 liftable x-coordinates in a multiplicative coset of order `d=788`. The other 408 coset x-coordinates do not lift to this curve. Their exclusion is a necessary point check after any root is found; `x^788=g^788` alone admits them.

The existing prime [decomposition engine](../../src/crypto_autoresearcher/index_calculus/msolve.py) uses one direct degree-788 coset equation per summand, chained Semaev `S3` equations, and a random separating linear form. The new [formulation source](../../tools/icperf_prime_coset_quadratic.py) replaces each coset equation with a fixed 12-gate square-and-multiply addition chain and a final constant equation. The gate `q_(a+b)=q_a q_b` is quadratic and forces `q_e=x^e` inductively; the terminal constraint forces the original coset equation. The S3 chain and separating form are copied unchanged. This is an equivalent projection onto the original variables over the field, before curve liftability and point-sign checks. It is a **chained S3 formulation with eight summands**, not a direct `S8` claim: direct `S8` addresses seven summands plus target; direct eight-summand elimination would require `S9` or another construction.

## Exact input counts

The [record](../../research/icperf_prime_coset_quadratic_20261017/system.json) contains every coefficient and exponent vector, the fixed addition chain, planted point sum and assignment, source and input SHA-256 bindings, and counts for `m=2…8`. “Monomial occurrences” sums the number of nonzero terms across serialized equations; it is not a Gröbner matrix size. The largest total degree of the lifted input remains four because S3 is quartic.

| m | Direct variables / equations / monomial occurrences | Lifted variables / equations / monomial occurrences | Direct → lifted maximum input degree |
| ---: | ---: | ---: | ---: |
| 2 | 3 / 4 / 16 | 27 / 28 / 64 | 788 → 4 |
| 3 | 5 / 6 / 33 | 41 / 42 / 105 | 788 → 4 |
| 4 | 7 / 8 / 50 | 55 / 56 / 146 | 788 → 4 |
| 5 | 9 / 10 / 67 | 69 / 70 / 187 | 788 → 4 |
| 6 | 11 / 12 / 84 | 83 / 84 / 228 | 788 → 4 |
| 7 | 13 / 14 / 101 | 97 / 98 / 269 | 788 → 4 |
| 8 | 15 / 16 / 118 | 111 / 112 / 310 | 788 → 4 |

At m=8 the lift adds 96 variables and 96 equations, and raises monomial occurrences from 118 to 310. The lower maximum input degree is offset by a larger algebraic system. Neither direction predicts degree of regularity or solving time without an actual solver comparison.

## Exact one-base coverage ceiling

Each of the 380 x-coordinate columns gives at most two signed points. An m-term sum is unchanged by permutation, so at most `C(2B+m−1,m)` signed multisets can produce distinct subgroup targets, with `B=380`. For a uniformly drawn target in the prime-order subgroup of size `r=9223372018953067627`, its representable fraction is therefore at most `min(1,C(760+m−1,m)/r)`. This bound ignores collisions between different multisets and is consequently optimistic. It is not an observed solver success rate. Exact integer counts can be reproduced with `math.comb(760+m-1,m)`.

| m | Maximum signed multisets | Maximum uniform-target coverage |
| ---: | ---: | ---: |
| 2 | 289,180 | 3.1353 × 10⁻¹²% |
| 3 | 73,451,720 | 7.9637 × 10⁻¹⁰% |
| 4 | 14,010,915,590 | 1.5191 × 10⁻⁷% |
| 5 | 2,140,867,902,152 | 0.0000232113% |
| 6 | 272,960,657,524,380 | 0.00295945% |
| 7 | 29,869,694,809,096,440 | 0.323848% |
| 8 | 2,863,756,989,822,121,185 | 31.048916% |

Thus direct `S8` with seven summands can represent at most 0.323848% of uniformly selected targets on this one base, even if its algebraic solver is perfect. Chained eight-summand input raises that upper bound to 31.048916%, still short of universal target coverage. Target shifts, additional bases, or another complete-target strategy must be specified and fully charged. This statement is scoped to the archived base and uniform-target model; it does not establish actual relation yield or block other base designs.

## Correctness checks and their limit

The three [software tests](../../tests/test_icperf_prime_coset_quadratic.py) passed: all x in a small field were checked for membership equivalence; the archived m=8 planted point sum satisfies both serialized systems; an altered auxiliary value fails. The independently implemented [Sage checker](../../tools/icperf_prime_coset_quadratic_sage_verify.py) read the frozen JSON, evaluated its polynomials over `GF(p)`, checked the eight curve points and their sum, and produced a [write-once replay](../../research/icperf_prime_coset_quadratic_20261017/sage_replay.json): 16/16 direct and 112/112 lifted equations vanish, while one changed auxiliary causes two nonzero lifted equations. It binds the system SHA-256 `4ed209221a30fcfe554a2adb8b782c77082910a37e13513cbe25bc7beecfc731` and checker SHA-256 in the replay. The correctness check uses a deliberately known point sum, so it does not measure unplanted decomposition yield.

As a separate backend capability check, SageMath 10.10.rc0 computed a **two-variable diagnostic** Gröbner basis over this 63-bit field for the ideal `(xy−1, x−y)`. The raw [stdout](../../research/icperf_prime_coset_quadratic_20261017/sage_capability.stdout.txt) and [stderr](../../research/icperf_prime_coset_quadratic_20261017/sage_capability.stderr.txt) are retained. The command was:

```sh
DOT_SAGE=/private/tmp/icperf-sage-dot TMPDIR=/private/tmp /Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage -c 'p=9223372021248595841; F=GF(p); R=PolynomialRing(F,names=("x","y")); x,y=R.gens(); I=R.ideal([x*y-1,x-y]); print(I.groebner_basis())'
```

Its result was `[y^2 + 9223372021248595840, x + 9223372021248595840*y]`. The standard Sage wrapper failed to initialize its cache in this sandbox; the direct binary with a writable `DOT_SAGE` resolved that environment issue. The diagnostic does not establish that this backend can solve the 111-variable m=8 system within useful resources.

## End-to-end ledger and discriminating next step

| Phase | Current evidence | Missing measurement |
| --- | --- | --- |
| Curve and base setup | Certified fixture; 380-point archived base; exact 788-element coset. | Charged field/curve search, rejected candidates, cold and genuinely reused setup. |
| Algebraic input | Exact direct/lifted m=2…8 counts and planted checks. | Observed Gröbner degree, time/RSS, all roots and point filtering on matched controls. |
| Relations and linear algebra | None for this formulation. | Natural yield, duplicate/sign handling, independent useful rank, LA time/memory. |
| Target and comparison | Known planted sum and exact one-base signed-multiset coverage ceiling only. | Unseen same-point target logarithm, any extra shifts/bases and all target work, independent replay, matched baseline and rho. |

The next discriminating experiment needs a Coordinator-approved frozen protocol comparing the direct and lifted systems on **the same 380-point base and targets**, plus an equal-realized-size random/small-x control. It should first use bounded planted and unplanted instances with explicit time, RSS and model limits; report censoring separately from unsatisfiability; check each root as a curve-point relation; then continue only if useful yield and rank justify a complete ECDLP panel. A matched whole-pipeline comparison must include all setup, relation generation, linear algebra, unseen target work, retries, verification, and rho. The [full-width measurement problem](../../problems/full-width-ic-arity-grid-unmeasured.md) remains open.

**Graph custody:** the [canonical ECDLP frontier](../../knowledge/frontiers/ecdlp/README.md) was checked. This formulation changes no reviewed complete-cost result, so its graph source and rendering remain unchanged. Provenance for claims in this report is `internal`: linked source, archived records, and the independent replay; no external literature result is inferred.
