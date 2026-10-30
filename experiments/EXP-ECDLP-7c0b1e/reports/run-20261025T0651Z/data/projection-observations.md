# Fresh-curve projection scale and local basis audit

Arithmetic reanalysis of sealed `EXP-ECDLP-7c0b1e/RUN-ECDLP-0b7dd5`. All 256 producer slot hashes and all five reconstructed stream hashes match; the projection union is 24 distinct curves, 144 rows (138 applicable, 6 NA). This is same-session assistance, not formally independent scientific review. No new trials were run.

Each table entry is the equal-curve arithmetic mean of **observed entropy minus the mean of 99 sign-pair-matched null outcomes**, in bits. Pair is H(φ(X+Y)|φ(X),φ(Y)); D0 is H(φ(2X)|φ(X)); D1 is H(φ(2X+P)|φ(X)). Negative values mean less conditional entropy than this matched reference. These are descriptive differences, without significance tests or inferential p-values.

| Feature | subgroup bits | stratum | applicable curves | pair gap | D0 gap | D1 gap |
|---|---:|---|---:|---:|---:|---:|
| x_mod_7 | 8 | ordinary | 4 | -0.005020983 | -0.018615615 | -0.006751180 |
| x_mod_7 | 8 | power5 | 4 | -0.004117841 | 0.011181434 | -0.009453724 |
| x_mod_7 | 10 | ordinary | 4 | -0.002280115 | -0.023190411 | -0.001013860 |
| x_mod_7 | 10 | power5 | 4 | -0.002187682 | -0.002796746 | 0.002462764 |
| x_mod_7 | 12 | ordinary | 4 | -0.000370594 | -0.002480201 | 0.000673142 |
| x_mod_7 | 12 | power5 | 4 | -0.000367207 | 0.001102577 | -0.000925029 |
| power_residue_5 | 8 | ordinary | 2 | -0.010459325 | -0.023888341 | -0.000622882 |
| power_residue_5 | 8 | power5 | 4 | -0.005774494 | 0.027375019 | 0.003856990 |
| power_residue_5 | 10 | ordinary | 1 | -0.002121642 | 0.000162753 | 0.010828895 |
| power_residue_5 | 10 | power5 | 4 | -0.003480665 | -0.002404865 | -0.010654439 |
| power_residue_5 | 12 | ordinary | 3 | -0.000613992 | 0.000988535 | -0.002154474 |
| power_residue_5 | 12 | power5 | 4 | -0.000508599 | -0.001061238 | -0.000816283 |
| x_hash_7 | 8 | ordinary | 4 | -0.000493746 | -0.058379596 | 0.014073897 |
| x_hash_7 | 8 | power5 | 4 | 0.002606843 | -0.011366024 | -0.004671653 |
| x_hash_7 | 10 | ordinary | 4 | 0.000140143 | -0.005479224 | -0.007193768 |
| x_hash_7 | 10 | power5 | 4 | 0.000067863 | 0.007961021 | 0.002785949 |
| x_hash_7 | 12 | ordinary | 4 | -0.000003737 | 0.003650297 | 0.000687618 |
| x_hash_7 | 12 | power5 | 4 | -0.000000472 | 0.000668977 | -0.001444457 |

`ordinary` is an unrestricted stratum; `power5` forces p≡1 (mod 5). Fifth-power applicability is not assumed: the six `power_residue_5` NA rows are the ordinary fixtures r8-0, r8-2, r10-0, r10-1, r10-3, r12-0, each explicitly reporting “5 does not divide p−1.” All six remain in the sealed raw output.

Pair gaps persist broadly with much smaller magnitudes on these fresh larger curves. `x_mod_7` is negative on 23/24 curves, ranging −0.012337674879 to +0.002601225378 bits (pilot range supplied in session: −0.065459 to −0.001195). `power_residue_5` is negative on all 18 applicable curves, ranging −0.013632709925 to −0.000369461456 bits (the sole applicable pilot row was −0.206438). At 12 subgroup bits, x-mod gaps range −0.000596211494 to −0.000239733980; fifth-power gaps range −0.000877389496 to −0.000369461456. The 12-bit hash-control pair range is −0.000032296307 to +0.000011097062. These are observed finite-population magnitudes, not an asymptotic fit or an attack advantage.

D0 and D1 gaps have mixed signs across curves for each primary feature. Across all fresh curves, x-mod D0 ranges −0.060755071683 to +0.039736849389 and D1 −0.078574630057 to +0.078316928624; fifth-power D0 ranges −0.059754626789 to +0.056518837705 and D1 −0.022658695812 to +0.040446259341. The hash control also has larger mixed-sign unary gaps at the smallest sizes. No general unary improvement persists with one sign.

All 99 null outcomes per applicable family remain in raw data. There are 13,662 unrestricted and 11,286 matched outcome triples (74,844 scalar entries): 8,910 unrestricted and 6,534 matched outcomes were actually measured. Full-point and constant null values are analytic zeros; Kummer matched values reuse the observed entropies because matched relabeling only permutes its image labels. These repeated controls are not measured null draws. Kummer unrestricted values and both families for x-mod, fifth-power and hash were measured by exhaustive census. Recorded visit counts agree with these distinctions.

Full-point/constant controls are exactly zero; Kummer agrees with pair (1−1/r)², D0=0 and D1=(r−1)/r, with zero matched gaps within floating arithmetic. All retained null lengths/finiteness and recorded-gap arithmetic checked (maximum discrepancy 5.83e-16 bits). No unexpected projection-control or data failure was found. Exact population enumeration removes sampling error from the observed entropies; the 99 permutations are Monte Carlo null outcomes and are not new curve replications.

The basis audit is one global 504-row output, not 504 curve replications. The enlarged rational grammar tests 625 matrices before filtering, 496 invertible: 16 make AND alone parity-pure, 32 preserve both independent pins, and 0 satisfy both. Thus the pilot’s 48-matrix AND failure does not extend to the larger grammar. The rational positive-control basis [[1,2],[1,0]] makes AND even, while failing a pin.

The characteristic-two certificate serializes equal 32-term degree-eight polynomials in 20 variables and an empty residual, using ordinary exponents (no x²=x reduction). It establishes the declared local invariant B(g·f)=det(A)det(B)det(C)B(f): fixed AND has nonzero B, while parity-pure arity-three tensors have B=0. This excludes the fixed local AND interface under the declared independent invertible leg gauges. It does not cover block regrouping, internal contractions/pin absorption, sums, alternate encodings, or global ECDLP complexity. The certificate is not proof-assistant checked.

`projection-summary.json` supplies per-curve observed values, matched means, matched min/max ranges, primary gaps, secondary unrestricted gaps, grouped ranges, full NA listings and custody hashes. Raw encoded labels and all null arrays remain in the sealed parts. Features share curves and labels; none of these tables establishes novelty, decoder success or universal closure.

Custody metadata note: sealed `parts-manifest.json` is 79,505 bytes. The actual canonical artifact-policy audit confirms this JSON metadata file is allowed below the 1 MiB non-code threshold; `.json` is not a listed 64 KiB data suffix. All 348 declared artifacts pass that policy unchanged, and the archive verifier binds 349 paths including its receipt. No sealed bytes were changed.
