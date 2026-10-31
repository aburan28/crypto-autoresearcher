# Actual parameter-sweep observations

EXP-ECDLP-f50061 / RUN-ECDLP-e69a23: observed parameter sweep

Planned native child slots: 5248; attempts: {'confirmed': 5248}.

Child outcomes: {'completed': 5248}.

Retained parsed target rows: 335872; target statuses: {'censored': 107, 'solved': 335765}.

Independent public verifier slices passed: 9/9; exact A/A incomplete/mismatched cells: 0.

Shared rho: planned 128, confirmed 128, unattempted 0, unresolved 0.

Primary comparisons defined: 23/32; undefined outcomes remain displayed.

Postrun operation: completed; scientific validity: not_assessed.

Bootstrap: 10000 replicates; seed 17203111389885848843.

Primary metric: full_native_group_additions_m64. Ratios are harvest/reference, paired by curve and preserving both replicates.

| Setting | Reference | Geometric mean ratio | Pointwise 95% interval | Coverage |
|---|---|---:|---|---|
| dpminus1_cap1 | static_small | 0.965419 | [0.960223, 0.969975] | 64 curves, 2 replicates |
| dpminus1_cap1 | static_full | 0.965419 | [0.960223, 0.969975] | 64 curves, 2 replicates |
| dpminus1_cap1 | static_filled | 0.896497 | [0.884777, 0.908752] | 64 curves, 2 replicates |
| dpminus1_cap1 | rho_reference | 0.258807 | [0.252903, 0.265587] | 64 curves, 2 replicates |
| dpminus1_cap2 | static_small | 0.951081 | [0.94031, 0.960507] | 64 curves, 2 replicates |
| dpminus1_cap2 | static_full | 0.804478 | [0.788965, 0.82046] | 64 curves, 2 replicates |
| dpminus1_cap2 | static_filled | 0.577377 | [0.550767, 0.606928] | 64 curves, 2 replicates |
| dpminus1_cap2 | rho_reference | 0.254964 | [0.249732, 0.260552] | 64 curves, 2 replicates |
| dp0_cap1 | static_small | 0.919039 | [0.903153, 0.933201] | 64 curves, 2 replicates |
| dp0_cap1 | static_full | 0.919039 | [0.903153, 0.933201] | 64 curves, 2 replicates |
| dp0_cap1 | static_filled | 0.952929 | [0.938914, 0.96689] | 64 curves, 2 replicates |
| dp0_cap1 | rho_reference | 0.31231 | [0.287945, 0.341749] | 64 curves, 2 replicates |
| dp0_cap2 | static_small | 0.84214 | [0.815667, 0.86618] | 64 curves, 2 replicates |
| dp0_cap2 | static_full | 0.876457 | [0.861843, 0.893305] | 64 curves, 2 replicates |
| dp0_cap2 | static_filled | 0.753016 | [0.725675, 0.782807] | 64 curves, 2 replicates |
| dp0_cap2 | rho_reference | 0.286178 | [0.267451, 0.308343] | 64 curves, 2 replicates |
| dp0_cap4 | static_small | 0.830004 | [0.797803, 0.859339] | 64 curves, 2 replicates |
| dp0_cap4 | static_full | 0.731884 | [0.710107, 0.754387] | 64 curves, 2 replicates |
| dp0_cap4 | static_filled | 0.42496 | [0.396577, 0.457168] | 64 curves, 2 replicates |
| dp0_cap4 | rho_reference | 0.282054 | [0.264985, 0.302213] | 64 curves, 2 replicates |
| dpplus1_cap1 | static_small | undefined | undefined | Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped. |
| dpplus1_cap1 | static_full | undefined | undefined | Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped. |
| dpplus1_cap1 | static_filled | undefined | undefined | Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped. |
| dpplus1_cap1 | rho_reference | undefined | undefined | Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped. |
| dpplus1_cap2 | static_small | undefined | undefined | Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped. |
| dpplus1_cap2 | static_full | undefined | undefined | Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped. |
| dpplus1_cap2 | static_filled | undefined | undefined | Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped. |
| dpplus1_cap2 | rho_reference | 0.644986 | [0.539073, 0.783927] | 64 curves, 2 replicates |
| dpplus1_cap4 | static_small | undefined | undefined | Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped. |
| dpplus1_cap4 | static_full | undefined | undefined | Entire paired64curve/tworeplicate panel required; failures/censoring/missing rows are not dropped. |
| dpplus1_cap4 | static_filled | 0.672726 | [0.63741, 0.711332] | 64 curves, 2 replicates |
| dpplus1_cap4 | rho_reference | 0.586566 | [0.498393, 0.699147] | 64 curves, 2 replicates |

Exploratory comparisons reuse the original public 64-curve cohort, with two replicates per curve; all settings are displayed. Intervals are pointwise 95% curve-cluster bootstrap intervals, not familywise discovery or selection qualification. Full-native primary counts add disjoint fixture validation, setup and 64 target deltas; solver-API secondary counts use setup plus target deltas. These are emitted native counter families, not an exhaustive price for sorting, ordinary modular work, JSON, hashing or other uncounted work. Correct public equations and causal traces do not independently replay or attest native counter execution. CPU/RSS and wall observations are diagnostics; all clocks remain unqualified (wall_valid=false). No runtime exponent inference or end-to-end attack qualification is made by this report.

All primary and secondary comparisons appear in comparisons.csv. Missing costs are empty fields. Raw streams, parser findings, censoring and partial costs remain in the frozen per-child analysis and raw collection.

Protocol body SHA-256: `f882380374559faae1b50d86c1583c06c36738fc5dce43d2861fadaa6204b812`. Exact report inputs are hash-bound in report-inputs.json.
