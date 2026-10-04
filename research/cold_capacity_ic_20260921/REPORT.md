# Cold-start capacity experiment: RUN-KIC-8b5038

Independent review passed for this exact finite receipt. All 72 frozen processes completed validly. The larger table has a measured time/memory tradeoff on this panel and does not meet the rho target.

The fixed N=53 / a=0 / K=75 / eta=1/256 IC source differs from the reviewed R1 baseline by one added capacity expression. Signed-expanded hash slots increase from 16,777,216 to 33,554,432; field arithmetic, base construction, Bloom sizing, relation policy, RNG, one-worker settings, and rho are fixed. Fresh public known-answer targets are disjoint from R1. All six baseline/candidate/rho orders run four times over 24 targets, with no calibration or selection.

| Arm | Median cold-process wall (s) | Median child CPU (s) | Median peak RSS (decimal MB) | Maximum peak RSS (decimal MB) |
| --- | ---: | ---: | ---: | ---: |
| Original-capacity IC | 4.467309 | 4.424039 | 438.821 | 439.599 |
| Doubled-capacity IC | 3.928168 | 3.908679 | 773.276 | 775.193 |
| Matched signed-Frobenius rho | 1.143202 | 1.128977 | 88.097 | 174.637 |

Across matched targets, candidate/baseline median ratios are 0.870771 for wall, 0.872526 for CPU, and 1.762315 for peak RSS. The observed wall reduction is 12.9%, with 76.2% greater peak RSS. These are separate cost dimensions; the candidate does not dominate its IC baseline across time and memory.

The primary candidate/rho median paired wall ratio is 3.561202; the frozen 10,000-resample paired-bootstrap 95% interval is [2.622217, 4.396155]. The required median below 0.95 and upper endpoint below 1.00 both fail. The original-capacity IC/rho median paired ratio on these same targets is 4.068411. Ratios of marginal medians are different statistics and are not substituted for paired ratios.

Median IC setup changes from 1.475692 to 0.855095 seconds. Median query time is 2.173575 versus 2.201514 seconds, and median collection is 2.385577 versus 2.572536 seconds. These are component medians, not additive components of one observed process. The source-derived extra table-array payload is 320 MiB; actual RSS is separately measured. Changed table traversal may change first-hit witnesses and relation trajectories, as declared before measurement.

The independent N=13 test harness checks the complete x domain and returned positive/negative witness group identities. Both capacities have identical base/domain/lookup digests, with 131 active entries in 512 versus 1,024 slots. Candidate tests passed 11/11. The three untimed solver controls recovered scalar 17 and point [7518,47] with the common ARM PMULL backend. Parent wall/CPU/RSS from these controls is discarded; raw internal solver stage timings are diagnostic and excluded from the scientific analysis.

The primary boundary runs from process launch to per-PID wait4 reap, including fresh table construction, collection, verification and child output. All cases use one computational worker and fresh solver processes/directories. No solver precomputation is shared. CPU and maximum RSS are per child. The 8 GiB memory guard is a cooperative 50 ms footprint sampler; neither OS-cache eviction nor thermal invariance is claimed. Builds are separately recorded and excluded from per-target ratios.

The next already-frozen experiment, RUN-KIC-56c897, tests target-certificate stopping using the original R1 capacity. It is independent of this capacity outcome. It must charge certificate recomputation, every relation group check and final target validation, and must preserve the common generation prefix. That successor has its own measurements and review; no result is pooled into this capacity experiment.

Evidence:

- [Protocol](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_capacity_ic_20260921/protocol.json)
- [Exact production patch](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_capacity_ic_20260921/artifacts/RUN-KIC-8b5038/candidate.patch)
- [Source reconstruction index](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_capacity_ic_20260921/source_custody_index.json)
- [Producer analysis](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_capacity_ic_20260921/artifacts/RUN-KIC-8b5038/analysis.md)
- [Raw process index](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_capacity_ic_20260921/artifacts/RUN-KIC-8b5038/receipts/processes.jsonl)
- [Snapshot receipt](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_capacity_ic_20260921/snapshot_receipt.json)
- [Independent validation report](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_capacity_ic_20260921/review/report.json)
- [Coordinator disposition](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/ledger/decisions/DEC-20260921-a15c3b.md)
- [Predeclared review plan](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_capacity_ic_20260921/review_plan.json)

Implementation commit: 554b848cde. Measurement admission: 3f6714bee7. Producer snapshot: 6daebb5e1e. The sole scientific runner was executor session 90481, which exited zero. No remote publication or scientific-status promotion has occurred.
