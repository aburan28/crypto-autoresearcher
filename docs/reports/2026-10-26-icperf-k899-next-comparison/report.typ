#set page(paper: "us-letter", margin: (x: 0.7in, y: 0.6in))
#set text(font: "New Computer Modern", size: 9.5pt)

= N83 K899: the next factor-base comparison
_Preparatory source assessment · 26 October 2026_

The current N83 Koblitz prime subgroup has order 8,569,786,107,849,059 (52.93 bits), curve `EC1N83Ce1h35c7ced6b497`. Its current rank-finder producer, run `39527997793`, uses a 16-column M38 multiplier closure derived from K600. A nested K899 base was measured only as a direct 899-column arm under an older rank-probe producer, run `39306394645`.

The older within-run comparison reports K600/K899 cold 1.1873 [1.1247, 1.2523] and rank-stage 1.5176 [1.4149, 1.6235], over 20 targets and four rank blocks. Construction of either factor base was excluded. K899 had 2.0766 times the non-rank cold work and 2.0713 times peak RSS. Direct index builds were 19.660 s and 44.263 s respectively. None of these ratios transfers to the current M38 index, and the result cannot be stacked arithmetically with later producer gains.

#figure(image("figure.svg", width: 100%), caption: [Source-reported paired ratios, run 39306394645. Both ratios exclude factor-base construction. The current rank-finder producer was not an arm of this run.])

== Next test boundary

First derive and independently certify a K899 multiplier closure compatible with the current M38 recipe; label any direct 899-column arm separately. Then freeze the current producer and held-out targets. Build both target-blind bases on the same host, charge construction and certification, and measure candidate index build against the fully charged K600 cold total before a larger paired panel. If index build alone exceeds that total on the same host, the candidate cannot win the frozen cold one-target comparison. For an admissible arm, measure rank, linear algebra, online target work and verification with matched rho; alternate arms and retain A/A, planted, censored, and failed calls. Record useful rank, matrix density, wall, CPU and RSS. Separate cold one-target and stated reuse-count totals.

The test needs a frozen `experiment.protocol/v1`, power/stopping and archive plans, preapproval, and Coordinator approval before execution. It answers one Koblitz one-arity question. Prime, ordinary binary and other arities remain open.

== Source and literature

Cryptanalysis `docs/ic/BASELINES.md`, commit `e7cf096b4e2f9020e1326e4ed0b5ac0e96cc99f9`, blob `4a444fac7f5c61992559a57601ee03c48cddab55`. The mechanism was checked against Semaev 2004 (IACR 2004/031), Faugère et al. 2012 (EUROCRYPT), and Huang et al. 2015 (DOI 10.1186/s40736-015-0012-6). Detailed provenance and links are in `README.md`. No new scientific status or quantitative claim is made.
