# Binary m8 root-to-relation certificate check — 2026-10-17

## Question and scope

Can a primary Boolean assignment for the frozen ordinary-binary torsion-coordinate m8 XCNF input be converted into a checked curve-point relation? This is a correctness check on the archived **planted** assignment for the curve `y²+xy=x³+31` over `GF(2^61)` with modulus `z^61+z^5+z²+z+1`, prime subgroup order `576460752557211763`, and cofactor 4. It is neither a solver search nor an end-to-end index-calculus measurement.

## Method and observations

The [checker](../../tools/icperf_binary_root_certificate.py) reads the frozen [XCNF manifest](../../research/icperf_binary_circuit_xcnf_20261017/manifest.json), [torsion base](../../research/icperf_binary_torsion_coordinate_20261017/base.json), and [eight-summand chain](../../research/icperf_binary_torsion_m8_chain_20261017/chain.json). It checks parent hashes, decodes all 446 primary bits, checks eight accepted-coordinate memberships and seven field equations independently of the Boolean circuit, then lifts each coordinate to its two curve points. It enumerates 256 sign assignments and accepts only a sum equal to the selected **raw** target channel. Finally, it multiplies the point equation by the cofactor and verifies the signed 267-column projected row against the prime-subgroup target.

The immutable [certificate record](../../research/icperf_binary_root_certificate_20261017/certificate.json) records **one** exact sign assignment and **one** distinct projected row: columns 0–7 each have coefficient +1. The eight certified points equal the archived planted points. A [separate Sage replay](../../research/icperf_binary_root_certificate_20261017/sage_replay.json) verifies this extracted assignment's seven field equations, exact point sum and projected row in Sage's curve group. The earlier [independent chain replay](../../research/icperf_binary_torsion_m8_chain_20261017/sage_replay.json) checked all four target channels and the 128 even-torsion presentations of the same projected row. Two one-bit perturbations retained base membership but failed the field equations; their failures are recorded as controls. These are derived and independently replayed correctness observations, not relation yield or speed measurements.

The [diagram](2026-10-17-binary-root-certificate.svg) shows the gates; [PDF](2026-10-17-binary-root-certificate.pdf) embeds it. No canonical performance graph changes: the available values are a single planted certificate and controls, with no comparable solver timings or complete IC measurements.

## Remaining checks

An arbitrary solver assignment still requires this exact certificate check. A useful-relation measurement additionally needs all raw target channels, exceptional and pole branches, controlled sampling, distinct-rank accounting, linear algebra, target recovery, complete phase costs, and a matched baseline across the requested prime, Koblitz, and ordinary-binary subgroup sizes and m=2–8. The frozen XCNF is one selected binary m8 coordinate channel, so the certificate alone cannot establish relation yield or a speed improvement.
