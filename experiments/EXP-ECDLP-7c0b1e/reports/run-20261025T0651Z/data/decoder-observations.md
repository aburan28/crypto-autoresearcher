# Decoder follow-up: descriptive observations

Source: sealed `/workspace/autoresearcher-execution/experiments/EXP-ECDLP-7c0b1e/runs/RUN-ECDLP-0b7dd5`. This is same-session data analysis, not an independent scientific review. No new experiment or EC arithmetic was run, no sealed output was changed, and no private scalar-label file was read.

The 2,880 candidate cases comprise 90 kernels on 24 curves and 192 public targets, using four features, two modes and two beam widths where applicable. Six power-residue cases are structurally inapplicable because 5 does not divide p−1. All 2,880 case outcomes match the separately coded Jacobian verifier records: 69 hit cases correspond to 44 distinct targets. These are verified toy scalar witnesses, including chance-control witnesses; they do not establish a new algorithm or an advantage.

Hash custody: 347 execution-receipt artifacts checked; 288 distinct partition files checked; all five module byte streams reconstructed with matching byte counts and SHA-256. Public fixture and target hashes match the certificate. The verifier source/public-point checks are established by the sealed manifest and the parent source review; this report aligns their output flags and scalar values without repeating EC verification.

## Outcomes at the tested budgets

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

## Paired modes

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

## Size and stratum coverage

| Subgroup bits | Stratum | Cases | Hit cases | Unique recovered targets | Candidate checks |
|---|---|---|---|---|---|
| 8 | ordinary | 448 | 27 | 16 | 2016 |
| 8 | power5 | 512 | 26 | 17 | 2304 |
| 10 | ordinary | 416 | 8 | 4 | 1872 |
| 10 | power5 | 512 | 4 | 3 | 2304 |
| 12 | ordinary | 480 | 4 | 4 | 2160 |
| 12 | power5 | 512 | 0 | 0 | 2304 |

All size/stratum groups contain 32 public targets on four curves. Hit-case totals reuse targets across configurations. The 8-bit groups account for 53 of 69 hit cases and 33 of 44 unique recovered targets; the 10-bit groups account for 12 cases and seven targets, and the 12-bit groups account for four cases and four targets. The 12-bit power5 group has zero hits across 512 cases and 2,304 candidate checks. These are descriptive outcomes at unequal applicable-feature budgets, not a scaling law.

## Heldout calibration and fitted contraction

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

## Charged work and reuse

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

## Limits and full data

- The power-residue feature has 18 applicable kernels and six structural NAs; the other features have 24 kernels each. Unequal applicability changes the union budget.
- Zero hits, ties, exact/model disagreements and heldout-loss regressions are retained in the aggregate tables and the full cell table in the JSON.
- No random-guess p-value, fitted asymptotic exponent, speedup, novelty decision or security conclusion is computed here.
- [Condensed machine-readable summary](/workspace/classical-ecdlp-followup/analysis/decoder-summary.json); [sealed parts index](/workspace/autoresearcher-execution/experiments/EXP-ECDLP-7c0b1e/runs/RUN-ECDLP-0b7dd5/parts-manifest.json); [public witness verification manifest](/workspace/autoresearcher-execution/experiments/EXP-ECDLP-7c0b1e/runs/RUN-ECDLP-0b7dd5/verification-manifest.json).
