# All four binary m8 target-channel inputs — 2026-10-17

## Question and scope

Can the selected ordinary-binary m8 chained formulation be serialized for every raw target channel, for both the torsion-coordinate factor base and the classical raw-x control? The curve is `y²+xy=x³+31` over `GF(2^61)` with modulus `z^61+z^5+z²+z+1`, prime subgroup order `576460752557211763`, and cofactor 4. The target channels are the four raw preimages of one fixed prime-subgroup target under multiplication by 4. This is deterministic input preparation and correctness checking, with no solver search.

## Method and recorded result

The [emitter](../../tools/icperf_binary_all_channels_xcnf.py) reuses the two selected-channel files by digest from the prior [XCNF manifest](../../research/icperf_binary_circuit_xcnf_20261017/manifest.json) and freezes six new channel variants. The [new manifest](../../research/icperf_binary_all_channels_xcnf_20261017/manifest.json) binds the chain, both bases, source, target constants, formula hashes and exact clause/gate counts. Every arm has seven three-point equations and eight exact precomputed membership predicates. The [independent parser](../../tools/icperf_binary_all_channels_xcnf_verify.py) checked all eight serialized files, gate definitions, membership truth tables and 24 seeded comparisons of the 427 output bits against direct field formulas. The prior planted full-assignment check is retained on the selected torsion arm. The [verification record](../../research/icperf_binary_all_channels_xcnf_20261017/verification.json) contains the per-arm receipts.

| Base / channel | Live AND + XOR gates | CNF clauses | XOR rows | Gzip bytes |
| --- | ---: | ---: | ---: | ---: |
| torsion φ / 0 | 86,113 | 79,626 | 61,020 | 652,319 |
| torsion φ / 1 | 85,965 | 79,626 | 60,872 | 651,387 |
| torsion φ / 2 | 86,114 | 79,626 | 61,021 | 652,334 |
| torsion φ / 3 | 85,966 | 79,626 | 60,873 | 651,378 |
| raw x / 0 | 137,306 | 130,029 | 94,764 | 1,056,770 |
| raw x / 1 | 137,604 | 130,179 | 95,012 | 1,058,955 |
| raw x / 2 | 137,583 | 130,329 | 94,941 | 1,058,780 |
| raw x / 3 | 137,427 | 129,879 | 94,935 | 1,057,477 |

These are exact structural counts of one fixed encoding. The torsion arm uses 267 projected columns and 10-bit coordinate blocks; the raw-x arm uses 265 columns and 9-bit blocks. Their sizes therefore do not provide a matched solver or end-to-end advantage. The six new gzip files total 5,130,311 bytes; the eight referenced files total 6,839,400 bytes. The [record-derived chart](2026-10-17-binary-all-channels-xcnf.svg) has editable [source](2026-10-17-binary-all-channels-xcnf-chart.py) and is embedded in the [PDF](2026-10-17-binary-all-channels-xcnf.pdf).

## Limits and next check

Only channel 0 has an archived satisfying planted assignment and a [full-point certificate](2026-10-17-binary-root-certificate.md). The six new channel files have parser and direct-formula checks, not satisfying-assignment certificates. The Boolean formulas constrain coordinates but do not encode point signs, exceptional/pole cases or a projected relation row; candidate roots require the external certificate check. The next discriminating test is an approved, bounded selected-arm solver run with all four channels, matched realized-column and encoding controls, and full accounting of misses and duplicate rows. Observed solving degree, relation yield, useful rank, linear algebra, target recovery and complete IC time remain unmeasured. No canonical performance graph changes because these are input counts, not measured runtimes.
