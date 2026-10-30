# Matched shifted-cover observations, 2026-10-30

The full five-pair panel completed 15,654,912 collection branches and the same
number of separately reconstructed replay branches. All ten cells passed;
source bytes were unchanged after execution. These are finite observations on
two fixed public p4099 curves, not a speedup, novelty or general rank claim.

| Fixed case | Active atoms | h=0 rows / equations | Shifted rows / equations | Old rank | Matched h=0 rank | Shifted combined rank | Additional rank |
|---|---:|---:|---:|---:|---:|---:|---:|
| b16, h3279 | 14 | 64 / 7 | 37 / 4 | 9 | 9 | 13 | 4 |
| b16, h3343 | 14 | 57 / 6 | 7 / 1 | 9 | 9 | 10 | 1 |
| b16, h3437 | 14 | 41 / 5 | 20 / 2 | 9 | 9 | 11 | 2 |
| b16, h3769 | 14 | 24 / 3 | 65 / 8 | 9 | 9 | 15 | 6 |
| b13, h3437 | 15 | 74 / 8 | 98 / 10 | 13 | 13 | 15 | 2 |

Rank means coefficient rank on the same fifteen original projected unknowns.
Each pair uses exactly the same active subset for constraints and residual
acceptance; the original curve, sixteen native coefficient columns, source
order, completed-zero policy and pole(3,3) cubic law remain fixed. The five
shifts include every nonzero membership-maximizing tie from the complete prior
cover survey; no relation yield selected them. Each b16 arm attempted1,490,944
branches; each b13 arm attempted1,863,680. Replay is charged separately. The
reported gain is rank(M plus new rows)-rank(M); there are no outside columns
in this panel. Accepted witnesses alone overcount information.

Native source: `c461dbb653a2c83c78d2a7614d387eef8f6324c6`.
Frozen protocol canonical SHA256:
`d55c58e0a3b0a5c54d0c7248288aa97b4ad8bee9731c473701c7e4e61108ebb1`.
Actual checkpoint transport and root release preceded execution. The process
exited0, with no timeout; wall1870.714s, user CPU1856.542s, system CPU9.722s,
peak RSS221,827,072bytes. These are shared-host diagnostics, wall_valid=false.
Producer operation counters are partial; no complete collection/elimination
cost, calibrated rate or IC/rho comparison has been established.

Evidence: [analysis](runs/b2-fixed-panel-802e2a/analysis.json),
[unified export](runs/b2-fixed-panel-802e2a/export.json),
[execution](runs/b2-fixed-panel-802e2a/execution.json),
[report source](reports/b2-fixed-panel-802e2a/report.typ),
[inspected two-page PDF](reports/b2-fixed-panel-802e2a/report.pdf), and
[graph](reports/b2-fixed-panel-802e2a/observations.svg). Raw data were committed
and pushed in9506b8b94 before the report. Twenty lossless gzip files are backed
by content-addressed S3 manifests and original-byte hashes. All export bindings
were checked after archival. The checker independently reconstructs geometry,
all branch statuses, point equations, ranks, kernels and old-kernel syndromes;
this is an implementation check, not staffed scientific review.

## Derived usable certificates

The two full-rank cells, b16 h3769 and b13 h3437, yield explicit unit-vector
row-combination certificates for all fifteen projected atoms each. All thirty
scalar values pass a separate original-curve public multiplication check.
`database/atom-log-certificates.json` is hydrated through its sibling artifact
manifest; [the builder](../prime_field_progress_20261030/certify_bases.py)
binds every source to the native export and retains full original-row weights.
This analysis performs no new collection, scalar search or target generation.
The D1 study retains the original rank9/13 matrices, without these logs.

## Remaining leads

Compare independently chosen targets next, retaining all coincidences and
first-recovery prefix ranks. A target recovered with augmented rank below16
still leaves base uncertainty; rank16 identifies the entire augmented system.
The frozen D1 panel tests that distinction directly. Future cover selection can
use old-kernel syndromes and marginal rank per charged collection-and-elimination
cost, with a prospective selection/holdout split rather than fitting a selector
to this five-case outcome. Natural outside-point cancellation, reusable
many-target operators and unequal-infinity pole completion remain separate,
unexecuted leads in this iteration.

Translated covers and the explanation of repeated divisors are prior work:
see the previous B1/cover reports, prym_leads_20261027 README and matrix review,
and PKM2016 sections3.1–3.2. No historical graph or official research status is
changed by these observations. The graph here covers this exact new panel.

## Combined archive index

The fresh [v3 generation receipt](database/v3-fixed-panel/generation.json)
binds the original v2 parent, this panel and the completed independent-target
panel. It preserves8198 cover frames and all historical rows, adds487 subset
rows and807 target rows, and retains4 isolated-target certificates with their
public-multiple collision explanations. SQLite integrity, foreign keys and
certificate/dense-score cross-checks pass. The original parent is unchanged;
large database bytes are losslessly archived through the sibling S3 manifest.
See [D1 observations](../prime_field_d1_execution_20261030/RESULTS.md) for the
target and post-hoc partial-relation scopes.
