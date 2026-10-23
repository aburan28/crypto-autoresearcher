# Weighted k11 torsion-coordinate factor base — 2026-10-17

## Question and fixed construction

Can a target-blind enlargement of the ordinary-binary torsion-coordinate base reach the smallest projected-column count whose **m=8 signed-multiset count** is at least the prime-subgroup order, while keeping the paired coordinate structure and a compact membership description? The curve is `y²+xy=x³+31` over `GF(2^61)` with modulus `z^61+z^5+z²+z+1`, subgroup order `r=576460752557211763`, cofactor 4, and `φ(P)=γ/(x(P)+γ)` for `γ⁴=31`.

The [source](../../tools/icperf_binary_torsion_k11_weighted.py) fixed four offsets `c∈{2048,4096,6144,8192}` before generation. In each affine space `t=c⊕v`, `0≤v<2048`, it keeps the pair `v,v⊕1` when the Hamming weight of the ten high free bits `v>>1` is at most five. This admits exactly 1,276 coordinate candidates per offset before curve liftability. The low bit is unrestricted, so the two-torsion action `t→t⊕1` remains paired. Exact membership is the 11-dimensional linearized affine equation, the 10-bit cardinality condition, and liftability; the first two predicates alone are not the exact point base.

The predeclared selection rule chooses the offset whose realized projected-column count is closest to `B*=311`, the first integer with `C(2B+7,8)≥r`, breaking ties by smaller offset. This threshold concerns possible signed multisets; it does not guarantee that their group sums cover every target. No target point or target relation was used in selection.

## Recorded preparation and checks

| Offset | Hamming-cut candidates | Liftable raw coordinates | Distinct projected columns |
| ---: | ---: | ---: | ---: |
| 2,048 | 1,276 | 588 | 294 |
| **4,096 (selected)** | 1,276 | 632 | **316** |
| 6,144 | 1,276 | 642 | 321 |
| 8,192 | 1,276 | 608 | 304 |

The [immutable base record](../../research/icperf_binary_torsion_k11_weighted_20261017/base.json) contains all accepted coordinates, selected raw points, projected points, pair signs, four full scan counts, the 12-term linearized polynomial, preparation resources, and a deterministic equal-column paired-random control. The selected 316-column control required 596 raw draws. On this shared arm64 host, preparation recorded 16.888097 seconds wall, 14.232136 seconds CPU and 70,959,104 bytes peak RSS; those descriptive numbers are not a controlled comparison with the earlier k10 preparation.

An [independent Sage replay](../../research/icperf_binary_torsion_k11_weighted_20261017/sage_replay.json) re-enumerated the four Hamming-cut/liftability scans, verified the selected 316 canonical points, their `[4]` prime-subgroup projections, two-torsion pair signs, the deterministic 316-column random control, and 32 true plus 32 false three-point polynomial controls. The selected count is 49 columns (18.35%) larger than the earlier [267-column k10 base](2026-10-17-binary-torsion-coordinate.md). The exact number of length-eight signed multisets is 3.8186 times larger, derived from `C(2B+7,8)`; this is an **opportunity-count ratio**, not measured relation yield or ECDLP speed.

A separate [selected-channel circuit diagnostic](../../research/icperf_binary_torsion_k11_weighted_20261017/circuit_support.json) used the same seven-equation schoolbook field circuit as the k10 input. The k11 candidate has 454 primary bits, 25,789 live AND and 62,655 live XOR gates (88,444 total), and 11,328 exact accepted-coordinate forbidding clauses across eight external variables. The earlier k10 input has 446 primary bits, 25,093 AND and 61,020 XOR (86,113 total), and 3,920 forbidding clauses. Three seeded direct field evaluations checked every equation output in the k11 circuit. These are structural input counts only; the cardinality cut, solver branching, memory, and useful relation costs are not priced by them.

The [SVG chart](2026-10-17-binary-torsion-k11-weighted.svg), editable [source](2026-10-17-binary-torsion-k11-weighted-chart.py), and inspected [PDF](2026-10-17-binary-torsion-k11-weighted.pdf) show the selected column count and threshold.

## Limits and next check

The Hamming cut adds a Boolean cardinality predicate, and the input block grows from 10 to 11 bits. The circuit counts above do not measure the descended system's observed solving degree, SAT/ANF support, relation yield, duplicate rows, useful rank, all four target channels, or complete IC cost. A fair next test freezes this 316-column base and its 316-column random control, serializes matched formulations, then measures both through the same bounded solver and full point-certificate path. The signed-multiset count is at least `r` for B=316, but group collisions and solver failures can still make actual coverage much smaller. No canonical performance graph changes.
