# Four-channel weighted k11 binary m8 inputs — 2026-10-17

## Question and scope

Can the new [316-column weighted k11 torsion-coordinate base](2026-10-17-binary-torsion-k11-weighted.md) be encoded against the **same four archived raw target channels** used for the earlier 267-column k10 base? The curve is `y²+xy=x³+31` over `GF(2^61)` with prime subgroup order `576460752557211763` and cofactor 4. This is formulation preparation and verification, not a solver run.

## Frozen inputs and checks

The [emitter](../../tools/icperf_binary_torsion_k11_xcnf.py) fixes eight external variables of 11 bits each, six full-field intermediates, seven torsion-coordinate three-point equations, one raw target channel constant per file, and exact membership in the base's 632 accepted raw coordinates. The [manifest](../../research/icperf_binary_torsion_k11_xcnf_20261017/manifest.json) binds the new base, prior same-target chain, circuit-support record, source and four gzip file hashes. The four files total 2,778,714 compressed bytes.

An [independent serialized-formula verifier](../../tools/icperf_binary_torsion_k11_xcnf_verify.py) checked each file's header, all AND/XOR gate definitions, every one of the 2,048 coordinate-membership truth-table values in each of eight external blocks, hashes and exact target constant. It also checked 12 seeded direct field evaluations of all 427 equation bits (three per channel). The [verification record](../../research/icperf_binary_torsion_k11_xcnf_20261017/verification.json) captures the per-file counts and checks. The selected channel-0 circuit counts match the separately archived [k11 circuit diagnostic](../../research/icperf_binary_torsion_k11_weighted_20261017/circuit_support.json).

| Raw target channel | k10 live gates (B=267) | k11 live gates (B=316) | k11 CNF clauses | k11 native XOR rows | k11 gzip bytes |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 86,113 | 88,444 | 89,122 | 62,655 | 695,127 |
| 1 | 85,965 | 88,293 | 89,122 | 62,504 | 694,227 |
| 2 | 86,114 | 88,445 | 89,122 | 62,656 | 695,145 |
| 3 | 85,966 | 88,294 | 89,122 | 62,505 | 694,215 |

Every k11 file has 454 primary variables and 11,328 exact membership-forbidding clauses, versus 446 and 3,920 in the k10 files. The [record-derived chart](2026-10-17-binary-torsion-k11-xcnf.svg) has editable [source](2026-10-17-binary-torsion-k11-xcnf-chart.py) and is embedded in the [PDF](2026-10-17-binary-torsion-k11-xcnf.pdf). These structural counts show the cost of representing the larger candidate in one fixed circuit; the bases have different column counts, so the table is not a matched solver-speed comparison.

## Limits and next check

None of the four k11 files has a supplied satisfying assignment. The older k10 planted assignment is tied to its own base and is not a k11 certificate. Direct field evaluations check encoding correctness, not satisfiability, relation yield or degree of regularity. The XCNF files still leave point signs, poles and exceptional branches to a post-solver full-point checker. A controlled comparison needs a frozen run protocol, the 316-column paired-random control encoded with its own honest costs, all four channels, certificate-verified distinct relations, useful rank, linear algebra, target work and matched rho. The four channels project to one subgroup target and cannot be counted as four independent coverage gains. No canonical performance graph changes.
