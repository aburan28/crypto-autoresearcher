#set page(paper: "a4", margin: 17mm, footer: context [#align(center)[#counter(page).display()]])
#set text(font: "DejaVu Sans", size: 9.6pt)
#set par(justify: false, leading: .55em)
#set heading(numbering: none)
= P-192 and P-224: measured comparisons
RUN-ECDLP-d0e449 · EXP-ECDLP-5184f7 · 2026-10-11

All 39,570 scheduled jobs completed, with 400 exact integrity comparisons passing. The main result concerns 16–20-bit subgroups inside full 192/224-bit fields. The standard-size cryptographic ECDLP remains unresolved.

#table(columns: (1.1fr, 2.0fr, 2.5fr), inset: 5pt, [Case],
[S/R ratio; marginal 99.9% CI],
[Pairs / matched R fields],
[P-192],
[0.9834 \[0.9174, 1.0581\]],
[116 / 89],
[P-224],
[0.9875 \[0.9261, 1.0520\]],
[126 / 91])

P-192: practically similar generic small-subgroup work in this tested scope.
P-224: practically similar generic small-subgroup work in this tested scope.

#image("primary-comparison.svg", width: 100%)

Sources: analysis/summary.json, preparation/matching.json and attacks raw-results.jsonl. The Solinas reference is RUN-ECDLP-07aad1, a separate toy-field study. Comparisons have different scopes; this figure does not rank deployed prime security.

There are 576 independent random control fields, two fixed S primes and 3,328 unconditional main curve models. S has 512 models per prime; each of 288 random fields per case has four. R matches size; C additionally matches residue modulo 12. The frozen source commit is 6b0d33cf3d0f.

#pagebreak()
= How to read the theory
P-192 is 2^192 − 2^64 − 1, so 2^192 is congruent to 2^64 + 1 modulo p. P-224 is 2^224 − 2^96 + 1, so 2^224 is congruent to 2^96 − 1 modulo p. These are coordinate-reduction identities: useful for arithmetic, and available to both honest users and attackers.

The hidden scalar problem is Q = [x]G. In a cyclic prime-order subgroup of size ell, generic rho collision work has scale sqrt(ell). Matching subgroup orders and normalizing calls by sqrt(ell) isolates this implemented walk's dependence on the field. It does not establish the performance of every structural attack.

Over a finite field, E(F_p) is a finite group and has free integer rank zero. A prime-order subgroup has one generator. Number-field Mordell-Weil rank instead counts independent infinite-order points before reduction. More lifted generators may yield more candidate points, but do not supply their hidden finite-group scalars.

Many number fields can have F_p as a residue field. The chosen lifts use t^3−t−1 at t=2^64 and t^7−t^3+1 at t=2^32; their ranks describe these particular lifts. Exact PARI field invariants give degrees 3 and 7, signatures (1,1) and (1,3), and unit ranks 1 and 3. These are multiplicative unit ranks, not elliptic ranks or endomorphism-field invariants. Norm(a−theta)=f(a)=p makes (a−theta) an explicit principal prime ideal. The ring-of-integers quotient at that degree-one ideal is F_p; there is no characteristic-zero-field homomorphism to F_p.

A number-field reduction can preserve point addition at good reduction. An attack would also need cheap target lifting, useful coverage and enough independent scalar relations to make the full workflow cheaper than rho. This run does not measure that number-field workflow; its earlier immutable evidence stays separate.

Abstractly isomorphic cyclic groups do not automatically have efficiently computable coordinate maps. The tested degree-one isomorphisms have explicit maps (x,y) to (u^2 x,u^3 y), with known inverse encodings.

#image("field-structure.svg", width: 100%)

#pagebreak()
= Controls and confidence
Only ordinary nonsingular models enter small-subgroup attacks. The selected factor has multiplicity one, 16–20 bits and no embedding degree at most 20; anomalous and special-j cases are excluded. Maximum-cardinality matching then minimizes log-order distance, with at most 10% mismatch. All selections freeze before attacks.

The solver gets only public points, subgroup order, seeds and cap. Synthetic scalar truth stays outside its input and is used afterward. Native rho16, opaque rho16, independent native rho32 and complete BSGS are retained. Setup and verification are separate from primary search.

#image("attack-ratios.svg", width: 100%)

The primary ratio weights each matched random control field equally. Whole-field bootstrap preserves every paired curve/target/seed in its cluster. 500,000 replicates yield approximate marginal 99.9% intervals. Matching is held fixed. Three-family 99.9667% primary intervals reserve approximate joint 99.9% coverage for the wider Solinas study and these two cases; diagnostics have marginal coverage only.

P-192 reserved primary interval: \[0.9118606224458229, 1.064873264165767\]
P-224 reserved primary interval: \[0.9202148782807648, 1.0578621878292565\]

The similarity band is [1/1.2, 1.2], requiring at least 25 matched R fields and 50 pairs. This is a frozen practical comparison, not an exact equality test. All 2972 BSGS jobs match the exact setup/search accounting. 264 actual transported endpoint jobs pass their point and subgroup checks. Complete curve identities are in all-curve-identities.csv.

#pagebreak()
= Large groups and remaining uncertainty
Large prime factors have at least 128 bits. One target and one rho seed stop at 4,096 search group calls. These walks cannot resolve the typical cryptographic subgroup. A null outcome is censored and inconclusive for full ECDLP resistance.

#table(columns: (1.1fr, 2.0fr, 2.5fr), inset: 5pt, [Case / arm],
[Recovered / trials],
[99.9% upper bounded-recovery probability],
[P-192 / S],
[0 / 64],
[0.1120],
[P-192 / R],
[0 / 92],
[0.0793],
[P-192 / C],
[0 / 92],
[0.0793],
[P-224 / S],
[0 / 64],
[0.1120],
[P-224 / R],
[0 / 76],
[0.0952],
[P-224 / C],
[0 / 80],
[0.0906])

The upper probabilities describe the selected synthetic challenge distribution and this bounded solver only. They are not algorithm-independent security bounds. The exact standard coefficient/order/generator anchors have one capped target each and are not a repeated-curve population. Their primality, curve orders and nG=O were checked internally. Actual subgroup generic scales are roughly 2^96 and 2^112 operations, far above this run's caps.

Uniform curve-order audits retain exact orders, normalized traces, prime-order flags, certified small factors and residual primality flags. Factorization is partial; unresolved composite residuals are not prime or known largest factors. Binary population intervals use all S draws and one unconditional control curve per independent field, with conservative binomial-model 99.9% difference coverage; every other control row is retained descriptively. All-four-curve trace comparisons preserve field clusters.

The full-field arithmetic panel has 8700 exact-output-equal observations. Its 99.9% timing intervals cover sampled control-field variation conditional on one fixed S median and exclude S systematic timing error. Python fold ratios are descriptive prototypes; both inversion paths use the same builtin pow. P-192 inversion labels nevertheless differ by 5.61× in their medians. This substantial timing variation has an unmeasured cause and is retained in arithmetic/timing-observation.json; it supplies no algorithmic or security claim. No samples were repeated or discarded. Primary group-call results use no timing observations. report.md and analysis/summary.json contain every ratio and interval. Optimized native/assembly arithmetic is untested.

Sources, seeds, exact commands, versions and code hashes: manifest.json and contract.json. Actual phase outcomes: execution-result.json. All raw outputs are retained, including excluded engineering failures and corrections. During preparation, missing SEA data were installed after four completed order/factor/primality outputs matched exactly. That runtime amendment is retained; preparation times mix data setups and are not security comparisons. No independent scientific review, sealed bound, asymptotic result or official claim promotion was obtained. Historical/canonical graphs remain as archived because their supported content does not change.
