# Matched four-channel binary m8 formula inputs — 2026-10-17

## Question and frozen files

Can the [same-width 316-column local random control](2026-10-17-binary-torsion-k11-local-control.md) be encoded on the **same four archived raw target channels** and seven-equation torsion-coordinate circuit as the [316-column weighted candidate](2026-10-17-binary-torsion-k11-xcnf.md)? The [control emitter](../../tools/icperf_binary_torsion_k11_local_control_xcnf.py) fixes the candidate's width, offset, curve, field representation, circuit construction and target constants, changing only the target-blind accepted-coordinate set. The [manifest](../../research/icperf_binary_torsion_k11_local_control_xcnf_20261017/manifest.json) binds the control base, candidate manifest, source, chain and four gzip file hashes.

An [independent serialized-formula verifier](../../tools/icperf_binary_torsion_k11_local_control_xcnf_verify.py) checked the gzip hashes, exact target constants, every AND/XOR gate definition, every membership truth-table value in all eight external blocks of each file, and 12 seeded direct field evaluations, three per channel. The [verification record](../../research/icperf_binary_torsion_k11_local_control_xcnf_20261017/verification.json) binds its source and inputs. The four control files total 2,774,964 compressed bytes; this is artifact size, not a solver resource measurement.

| Raw target channel | Candidate live gates | Control live gates | CNF clauses per file, both | Native XOR rows per file, both |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 88,444 | 88,444 | 89,122 | 62,655 |
| 1 | 88,293 | 88,293 | 89,122 | 62,504 |
| 2 | 88,445 | 88,445 | 89,122 | 62,656 |
| 3 | 88,294 | 88,294 | 89,122 | 62,505 |

Every file in both arms has 454 primary variables and 11,328 exact membership-forbidding clauses. The [record-derived diagram](2026-10-17-binary-torsion-k11-local-control-xcnf.svg), editable [source](2026-10-17-binary-torsion-k11-local-control-xcnf-chart.py) and [PDF](2026-10-17-binary-torsion-k11-local-control-xcnf.pdf) show the matched input boundary. Identical gate counts follow because the field-equation circuit is shared; different membership clauses select different coordinate sets.

## What remains

These files contain no supplied satisfying assignment. Parsing and seeded evaluations establish encoding consistency, not representation coverage, observed degree of regularity, solver time, certificate-verified relation yield, useful rank, linear algebra, target work or complete ECDLP improvement. Exact point signs, poles and exceptional branches remain obligations of a full-point checker. Four raw channels project to one prime-subgroup target and do not multiply its coverage. A frozen trial must run both arms under the same solver limits, retain all outcomes, charge their distinct preparation scans, independently check every reported full-point relation and complete a matched-rho phase ledger. The [full-width IC measurement problem](../../problems/full-width-ic-arity-grid-unmeasured.md) stays open; no canonical performance graph changes.
