# Same-width random control for the weighted binary base — 2026-10-17

## Question and selection

Can the [316-column weighted k11 torsion-coordinate candidate](2026-10-17-binary-torsion-k11-weighted.md) be paired with a target-blind random control that has the **same 11-bit coordinate width** and the same number of projected log columns? The archived global-field random control has 316 columns but uses full-width coordinates. This local control isolates the weighted cut within the selected affine block; the earlier global control remains a separate breadth check.

The [producer](../../tools/icperf_binary_torsion_k11_local_control.py) enumerated all 1,024 torsion pairs in the candidate's offset-4096 affine block before any target observation. Exactly 511 pairs lift on the certified `GF(2^61)` curve; 513 do not. It SHA-256-ranked the 511 even-coordinate pairs under the fixed domain `icperf-binary-k11-local-control-v1` and seed `20261017`, took the first 316, and then sorted by coordinate. The resulting [base record](../../research/icperf_binary_torsion_k11_local_control_20261017/base.json) retains all liftable even coordinates, rejections, selected full points, subgroup projections, signs, source/input hashes and preparation resources. Selection uses neither archived raw targets nor relation outcomes.

An [independent Sage implementation](../../tools/icperf_binary_torsion_k11_local_control_sage_verify.py) re-enumerated the full block, reconstructed the hash ranking, checked every selected point and its two-torsion partner, verified prime-subgroup images and signed pair projections, and recovered the same 316 columns. Its [replay record](../../research/icperf_binary_torsion_k11_local_control_20261017/sage_replay.json) binds both source and input digests. The weighted and local-random bases share 194 of 316 projected columns; each has 122 distinct columns outside that overlap.

| Input | Raw coordinates attempted in its preparation scan | Accepted raw coordinates | Projected columns | External coordinate width |
| --- | ---: | ---: | ---: | ---: |
| Weighted Hamming cut | 1,276 | 632 | 316 | 11 bits |
| Local random subset | 2,048 | 632 | 316 | 11 bits |

Both selected sets have 632 allowed raw values among 2,048 possible 11-bit encodings, so an eight-block exact forbidding-table encoding has `8 × (2,048 − 632) = 11,328` membership clauses for either set. The local control's full-block scan must be charged as its setup cost. The [record-derived chart](2026-10-17-binary-torsion-k11-local-control.svg), editable [chart source](2026-10-17-binary-torsion-k11-local-control-chart.py), and [PDF](2026-10-17-binary-torsion-k11-local-control.pdf) visualize the construction counts.

## Boundary and next test

The matched width and cardinality remove two input differences; the selected coordinate sets and preparation costs still differ by design. This record measures neither how often a subgroup target has an eight-term representation nor any SAT/Gröbner behavior, degree of regularity, independent useful rank, final ECDLP cost or speed improvement. The next controlled run needs both bases encoded on the same four raw target channels with the same circuit and resource limits, exact full-point relation certificates, charged preparation, useful-rank and linear-algebra costs, target work and matched rho. The [full-width measurement obstruction](../../problems/full-width-ic-arity-grid-unmeasured.md) remains open. No canonical performance graph changes.
