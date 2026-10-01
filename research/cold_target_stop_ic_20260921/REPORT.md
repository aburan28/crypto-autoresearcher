# Cold-start target-certificate stopping: RUN-KIC-56c897

Independent review passed for the exact finite receipt and certificates. The complete 72-process run is snapshotted; every process, target certificate and mandatory baseline prefix comparison passed its declared execution checks. The frozen rho predicate did not pass.

The candidate keeps the reviewed R1 factor base, K=75, eta=1/256, original table capacity, arithmetic, relation generation and one-worker settings. It carries each row's right-hand side and row-combination weights through elimination, then stops at the first pivot in the final target-variable column. Its certificate cancels every factor-base unknown and normalizes the target coefficient to one. The charged process independently checks the certificate, all admitted relation group identities, and the final target equation. It reports TARGET_IDENTIFIED and actual ranks; it does not claim to have computed factor-base logs.

| Arm | Median cold-process wall (s) | Median child CPU (s) | Median peak RSS (decimal MB) | Maximum peak RSS (decimal MB) |
| --- | ---: | ---: | ---: | ---: |
| Original-capacity full-rank IC | 4.678058 | 4.479542 | 437.789 | 439.714 |
| Target-certificate IC | 4.194146 | 4.063194 | 437.879 | 438.911 |
| Matched signed-Frobenius rho | 1.025491 | 0.919164 | 45.597 | 174.637 |

The median of the 24 matched candidate/baseline wall ratios is 0.935764, an observed 6.4% reduction; the CPU ratio is 0.929981. The peak-RSS ratio is 1.000019, effectively unchanged on this panel. These paired statistics are not ratios of the marginal medians in the table.

The candidate/rho paired median is 4.153067, with the preregistered 10,000-resample paired-bootstrap 95% interval [2.900413, 5.707114]. The original full-rank IC/rho paired median on these same targets is 4.499827. Both primary speed conditions fail. This panel is disjoint from earlier runs, so its absolute rho ratio must not be used to rank variants measured on different target panels.

All 24 candidates returned checked certificates and matched the baseline's exact relation-generation prefix. Candidate stopping lengths range from 71 to 76, with median 74; baseline admitted relations have median 79.5. Candidate median ranks are rank(A)=73 and rank([A|b])=74. The target is determined while factor-base variables may remain unresolved. No saving was inferred from the old posthoc prefix diagnostic: these are fresh measurements of the implemented stopping rule.

For each accepted relation A f + b d = a mod r, b is the last stored coefficient and a is separately stored coefficient_a. The certificate verifies wA=0, wb=1 and wa=d. Independent Python checks use the original rows and weights. The native fixed suite at moduli 17 and 21044858204113 includes early-target, zero-column, target-unit, duplicate, rescaling, inconsistency and corrupted-certificate cases, plus the K75 row74 construction. All 14 native tests and eight certificate-checker tests passed before solver controls. Three untimed N13 solver controls then verified answer 17, point [7518,47], exact prefixes and certificates.

Primary wall runs from process launch through per-PID wait4 reap and includes every charged certificate and group check. Nested stage timings are descriptive only: collection_ms includes certificate_validation_ms, while the inherited charged_total_ms is a subtotal that omits separately timed reference validation. It is never substituted for complete process wall. Builds are recorded separately. The 8 GiB memory guard is cooperative sampling, and no OS-cache, thermal or background-load invariance is asserted.

The next composition protocol, RUN-KIC-a15078, separately fixes a larger-table, target-certificate ARM candidate and both existing and strengthened rho references. Its source/control/measurement gates and independent review are separate from this run; no composition speedup is assumed here.

Evidence:

- [Frozen protocol](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_target_stop_ic_20260921/protocol.json)
- [Candidate patch](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_target_stop_ic_20260921/artifacts/RUN-KIC-56c897/candidate.patch)
- [Certificate checker](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_target_stop_ic_20260921/artifacts/RUN-KIC-56c897/certificate_checker.py)
- [Prefix checker](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_target_stop_ic_20260921/artifacts/RUN-KIC-56c897/prefix_checker.py)
- [Producer analysis](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_target_stop_ic_20260921/artifacts/RUN-KIC-56c897/analysis.md)
- [Raw process index](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_target_stop_ic_20260921/artifacts/RUN-KIC-56c897/receipts/processes.jsonl)
- [Snapshot receipt](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_target_stop_ic_20260921/snapshot_receipt.json)
- [Independent validation report](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_target_stop_ic_20260921/review/report.json)
- [Coordinator disposition](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/ledger/decisions/DEC-20260921-377204.md)
- [Predeclared review plan](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_target_stop_ic_20260921/review_plan.json)

Implementation commit e97ea5c876; measurement admission 4182f53268; producer snapshot f773f13879. Sole scientific session 24417 exited zero. No hypothesis or goal status has changed, and nothing has been published remotely.
