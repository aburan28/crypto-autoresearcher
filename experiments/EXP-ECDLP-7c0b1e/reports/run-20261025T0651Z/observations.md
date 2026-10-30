# Classical ECDLP follow-up: complete observations

All five jobs in the finite frozen follow-up completed, producing 3,624 rows on 24 fresh curves. Projection pair gaps broadly persist at much smaller magnitudes; unary gaps have mixed signs. The public decoder produced verified toy witnesses, including chance-control hits, without an established advantage. The expanded local audit gives a rational AND-only positive control and a characteristic-two obstruction confined to the fixed isolated tensor.

The 69 witness cases recover 44 distinct target IDs only after pooling 12–16 configurations and 54–72 checks per target. This is not the success rate of a beam-eight decoder. No mathematical lead is globally exhausted by this finite matrix.

[Provenance and scope](HEADER.md) · [Seven-page report](report.pdf) · [Editable plots](plot.py) · [Raw run](../../runs/RUN-ECDLP-0b7dd5/).

## Fresh-curve projection scale and local basis audit

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

## Decoder follow-up: descriptive observations

Source: sealed `../../runs/RUN-ECDLP-0b7dd5`. This is same-session data analysis, not an independent scientific review. No new experiment or EC arithmetic was run, no sealed output was changed, and no private scalar-label file was read.

The 2,880 candidate cases comprise 90 kernels on 24 curves and 192 public targets, using four features, two modes and two beam widths where applicable. Six power-residue cases are structurally inapplicable because 5 does not divide p−1. All 2,880 case outcomes match the separately coded Jacobian verifier records: 69 hit cases correspond to 44 distinct targets. These are verified toy scalar witnesses, including chance-control witnesses; they do not establish a new algorithm or an advantage.

Hash custody: 347 execution-receipt artifacts checked; 288 distinct partition files checked; all five module byte streams reconstructed with matching byte counts and SHA-256. Public fixture and target hashes match the certificate. The verifier source/public-point checks are established by the sealed manifest and the parent source review; this report aligns their output flags and scalar values without repeating EC verification.

### Outcomes at the tested budgets

| Feature | Mode | Beam | Cases | Hits | Candidate checks | Σ B/r |
|---|---|---|---|---|---|---|
| constant | exact | 1 | 192 | 0 | 192 | 0.490879 |
| constant | exact | 8 | 192 | 7 | 1536 | 3.927032 |
| constant | model | 1 | 192 | 0 | 192 | 0.490879 |
| constant | model | 8 | 192 | 7 | 1536 | 3.927032 |
| power_residue_5 | exact | 1 | 144 | 0 | 144 | 0.366316 |
| power_residue_5 | exact | 8 | 144 | 8 | 1152 | 2.930530 |
| power_residue_5 | model | 1 | 144 | 0 | 144 | 0.366316 |
| power_residue_5 | model | 8 | 144 | 3 | 1152 | 2.930530 |
| x_hash_7 | exact | 1 | 192 | 1 | 192 | 0.490879 |
| x_hash_7 | exact | 8 | 192 | 12 | 1536 | 3.927032 |
| x_hash_7 | model | 1 | 192 | 2 | 192 | 0.490879 |
| x_hash_7 | model | 8 | 192 | 9 | 1536 | 3.927032 |
| x_mod_7 | exact | 1 | 192 | 0 | 192 | 0.490879 |
| x_mod_7 | exact | 8 | 192 | 13 | 1536 | 3.927032 |
| x_mod_7 | model | 1 | 192 | 2 | 192 | 0.490879 |
| x_mod_7 | model | 8 | 192 | 5 | 1536 | 3.927032 |

Every case returned exactly B distinct legal candidates. For the constant feature, B/r is the exact success probability under the ideal uniform hidden-scalar model because its guesses do not use scalar-dependent observations. For nonconstant features, ΣB/r is a candidate-count-matched uniform-guess reference only. Targets and guesses are reused across cases; these rows are not independent trials.

Constant model/exact candidate lists agree for every one of 384 paired cases. Counting both modes doubles the same constant hits. Across the two widths and both modes, the constant control checks 1685 distinct target/guess pairs (8–9 per target), recovers 7 distinct targets, and has ideal-uniform expected count 4.265411.

### Paired modes

| Feature | Beam | Targets | Both hit | Exact only | Model only | Neither | Identical lists |
|---|---|---|---|---|---|---|---|
| constant | 1 | 192 | 0 | 0 | 0 | 192 | 192 |
| constant | 8 | 192 | 7 | 0 | 0 | 185 | 192 |
| power_residue_5 | 1 | 144 | 0 | 0 | 0 | 144 | 1 |
| power_residue_5 | 8 | 144 | 1 | 7 | 2 | 134 | 0 |
| x_hash_7 | 1 | 192 | 0 | 1 | 2 | 189 | 2 |
| x_hash_7 | 8 | 192 | 1 | 11 | 8 | 172 | 0 |
| x_mod_7 | 1 | 192 | 0 | 0 | 2 | 190 | 1 |
| x_mod_7 | 8 | 192 | 0 | 13 | 5 | 174 | 0 |

The pairs hold target, feature and beam fixed. Neither mode dominates all tested feature/beam combinations. These counts are descriptive comparisons at the tested toy sizes, without significance or generalization claims.

The union 44/192 spans 12–16 configurations and 54–72 candidate checks per target. Across the study, 12,960 candidate checks reduce to 9,886 distinct target/guess pairs; distinct guesses per target range 35–60 (median 52.5). This pooled union is not a beam-8 success rate. The summary JSON gives all feature/mode/beam/subgroup-size/stratum cells, including zero-hit cells; raw per-case records remain untouched in the decoder partitions.

### Size and stratum coverage

| Subgroup bits | Stratum | Cases | Hit cases | Unique recovered targets | Candidate checks |
|---|---|---|---|---|---|
| 8 | ordinary | 448 | 27 | 16 | 2016 |
| 8 | power5 | 512 | 26 | 17 | 2304 |
| 10 | ordinary | 416 | 8 | 4 | 1872 |
| 10 | power5 | 512 | 4 | 3 | 2304 |
| 12 | ordinary | 480 | 4 | 4 | 2160 |
| 12 | power5 | 512 | 0 | 0 | 2304 |

All size/stratum groups contain 32 public targets on four curves. Hit-case totals reuse targets across configurations. The 8-bit groups account for 53 of 69 hit cases and 33 of 44 unique recovered targets; the 10-bit groups account for 12 cases and seven targets, and the 12-bit groups account for four cases and four targets. The 12-bit power5 group has zero hits across 512 cases and 2,304 candidate checks. These are descriptive outcomes at unequal applicable-feature budgets, not a scaling law.

### Heldout calibration and fitted contraction

| Feature | Bit | Kernels | Transitions | Conditional loss (bits) | Marginal loss (bits) | Conditional accuracy | Marginal accuracy | Kernels lower/higher loss |
|---|---|---|---|---|---|---|---|---|
| constant | 0 | 24 | 12288 | 0.000000 | 0.000000 | 1.0000 | 1.0000 | 0/0 |
| constant | 1 | 24 | 12288 | 0.000000 | 0.000000 | 1.0000 | 1.0000 | 0/0 |
| power_residue_5 | 0 | 18 | 9216 | 2.256225 | 2.340680 | 0.2709 | 0.2179 | 16/2 |
| power_residue_5 | 1 | 18 | 9216 | 2.301073 | 2.334765 | 0.2530 | 0.2207 | 13/5 |
| x_hash_7 | 0 | 24 | 12288 | 2.639628 | 2.805371 | 0.2298 | 0.1750 | 20/4 |
| x_hash_7 | 1 | 24 | 12288 | 2.736293 | 2.807528 | 0.2048 | 0.1706 | 16/8 |
| x_mod_7 | 0 | 24 | 12288 | 2.648769 | 2.806976 | 0.2249 | 0.1672 | 20/4 |
| x_mod_7 | 1 | 24 | 12288 | 2.746966 | 2.815707 | 0.2057 | 0.1603 | 19/5 |

Each kernel uses 2,048 training states and 512 heldout states. Each heldout state produces a bit-0 and bit-1 transition observation; the 90 kernels therefore use 184,320 training states and 46,080 heldout states, or 92,160 heldout transition observations. Calibration was recorded without tuning. Losses are empirical means, not evidence that the projected EC process is truly Markov.

| Feature | Kernels | δmax min/median/max | Zero-count state rows | Rows with <10 samples | Minimum state count |
|---|---|---|---|---|---|
| constant | 24 | 0.0000/0.0000/0.0000 | 0 | 0 | 2048 |
| power_residue_5 | 18 | 0.2833/0.5228/0.8173 | 18 | 32 | 0 |
| x_hash_7 | 24 | 0.1569/0.4240/0.8609 | 4 | 16 | 0 |
| x_mod_7 | 24 | 0.1877/0.4393/0.8685 | 4 | 18 | 0 |

Dobrushin coefficients apply only to the fitted finite kernels and their model assumptions. Sparse infinity/zero feature rows can control the worst-row coefficient. They do not bound true EC dynamics, posterior concentration or ECDLP security. Constant labels are a calibration control, not scalar information.

### Charged work and reuse

Charge 90 constructions, 90 heldout calibrations, 24 shared fixture validations, 720 feature/target view setups (2880 offsets), and all 2880 inference/verification cases. Views are identical across the four mode/beam configurations for each feature/target, while features use different public view seeds. Validation is counted once per fixture. Heldout calibration is charged study work, not online candidate work.

| Stage | Group-add calls | Scalar-mul calls | Field adds | Field multiplies | Power calls | Inversion calls | DP terms | Candidate checks |
|---|---|---|---|---|---|---|---|---|
| Validation once | 3159 | 216 | 34897 | 97471 | 2711 | 2711 | 0 | 0 |
| Training once | 689625 | 183970 | 8261532 | 32311219 | 1448550 | 503911 | 0 | 0 |
| Heldout once | 172418 | 46001 | 2066099 | 8079194 | 362052 | 126024 | 0 | 0 |
| Views once | 36761 | 2877 | 440397 | 1407727 | 48006 | 33812 | 0 | 0 |
| All inference cases | 760989 | 12960 | 9017096 | 26638150 | 828786 | 746924 | 37544384 | 12960 |
| Whole decoder study | 1662952 | 246024 | 19820021 | 68533761 | 2690105 | 1413382 | 37544384 | 12960 |

These are actual instrumented call/step counts. Scalar multiplication invokes group operations, so their call counts must not be added as disjoint primitive work. Powers, inversions and square roots similarly denote calls with implementation work recorded in field counters. These totals describe the entire tested matrix, not a single decoder and not separate cold and warm bounds. Per-configuration inference costs and per-feature setup costs are included in the summary JSON. For example, x_mod_7 beam 8 uses 156,416 group-add calls in exact mode and 18,993 in model mode across the same 192 targets, while model mode uses 8,262,912 DP multiply-add terms versus 1,701,888 in exact mode. This resource tradeoff is part of the measured configuration comparison. The decoder record contains no timed Pollard-rho or baby-step giant-step run; the B/r column is a guessing-probability reference, not a runtime comparison against a generic solver.

### Limits and full data

- The power-residue feature has 18 applicable kernels and six structural NAs; the other features have 24 kernels each. Unequal applicability changes the union budget.
- Zero hits, ties, exact/model disagreements and heldout-loss regressions are retained in the aggregate tables and the full cell table in the JSON.
- No random-guess p-value, fitted asymptotic exponent, speedup, novelty decision or security conclusion is computed here.
- [Condensed machine-readable summary](data/decoder-summary.json); [sealed parts index](../../runs/RUN-ECDLP-0b7dd5/parts-manifest.json); [public witness verification manifest](../../runs/RUN-ECDLP-0b7dd5/verification-manifest.json).

## Mathematical context and remaining construction

The [local pin/AND proof](../../../../harness/classical_ecdlp_followup/theory/pin-obstruction.md), [fifth-character and signature bounds](../../../../harness/classical_ecdlp_followup/theory/character-kernel-bound.md), and [prior art/model audit](../../../../harness/classical_ecdlp_followup/theory/prior-art-and-model.md) are scoped separately from the frozen measurements.

For a bounded cofactor, the fifth-character proof bounds the finite, nonzero single-step conditional entropy deficit at O(1/p), with explicit constants that can be vacuous at the toy sizes and a required exceptional-symbol correction. It does not explain every pair-entropy statistic or bound full-alphabet worst-row contraction. The fixed-signature counting ceiling is conditional on ideal uniform targets and the declared public interface; it gives no ECDLP lower bound.

More training alone cannot escape the fixed-signature interface. Block grouping, internal elimination, pin absorption, alternate encodings and sums escape parts of the isolated-AND obstruction. No proposed construction yet supplies a cheap EC-specific constructive rule with full-cost advantage over a strong rho baseline. The frozen matrix is complete; the mathematical leads are not exhausted. HMM/beam architectures and the repository's earlier lossy double-and-add lead require a novelty assessment before any new-algorithm claim.

## Execution and raw evidence

[Runtime extract](data/runtime-summary.json) preserves actual source metadata and stage timestamps. [Timeline SVG](figures/execution-timeline.svg) ([PDF](figures/execution-timeline.pdf)) shows three projection shards overlapping the decoder and basis audit. The command envelope is 121.795798 seconds; the complete supervisor through output checking is 124.715335 seconds. The widths do not represent a wall-time speedup claim.

The raw artifacts were published before the genuine archive receipt at commit `3e6ca92887e07e4d9a1710eddd8c450e70fc86fa`. The unchanged repository verifier validated 349 paths including the receipt; all 348 run files retain their sealed hashes. The actual canonical storage-policy audit allows every artifact as written. The 79,505-byte JSON parts manifest uses the non-code 1 MiB threshold because `.json` is not a data suffix; no compaction or change to sealed evidence was needed.

All seven report pages and four figure PDF pages were visually inspected after layout and font corrections. The analysis is same-session descriptive arithmetic, without independent scientific review or scientific status promotion.
