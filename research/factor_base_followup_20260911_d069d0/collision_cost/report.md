# Execution report: TASK-20260911-e837e1

Status: `completed_valid`. Protocol SHA-256 `97da73662f6c76fc06591493fb9fdcd7936ab72b3ab47dab00fd2f933d96a8cc`.

Finite observations only. Parameters are n=19, a=b=1, binary modulus x^19+x^5+x^2+x+1, subgroup order 262543. All four bases and both existing source campaigns were frozen before this audit. No logarithms or linear systems were solved and no new relation queries were collected.

| Base | Points | Pairs with diagonals | Equal-sum collisions | Identity collisions | Zero rows | Compressed rank | Anchor rank |
|---|---:|---:|---:|---:|---:|---:|---:|
| prefix_k3 | 114 | 6555 | 2052 | 1596 | 2052 | 0 | 0 |
| prefix_k4 | 152 | 11628 | 3800 | 2850 | 3458 | 2 | 2 |
| balanced_k4 | 152 | 11628 | 3572 | 2850 | 3458 | 1 | 1 |
| two_swap_k4 | 152 | 11628 | 3572 | 2850 | 3458 | 1 | 1 |

Every public coefficient label was checked by multiplying its declared public representative. Each pair collision retained its pair indices, exact group sum and compressed row in collision_witnesses.jsonl. A differently associated four-point sum checked each equality. Canonical pivot certificates and rank-increment witnesses are in results.json. Corrupted-label, zero self-subtraction, one-slot hash alias, reverse insertion and reverse row-order checks completed. This producer replay is distinct from the required independent review after snapshot.

Cost coverage: 72 existing processes, 288 source corpora, 2359296 streamed relation receipts. Every actual first-full-column-rank milestone and original rank+32 milestone agrees with its source summary; query totals agree at corpus and process scope.

| Existing source set | Arm | Full-rank accepted count min/median/max | First-rank query ms min/median/max | Setup + first-rank query partial ms min/median/max |
|---|---|---|---|---|
| balanced_fresh | balanced_k4 | 5 / 5 / 6 | 0.014541 / 0.0295425 / 0.059042 | 93.4569 / 99.7797 / 118.381 |
| balanced_fresh | prefix_k4 | 5 / 5 / 5 | 0.016333 / 0.0334375 / 0.05725 | 94.7811 / 98.4399 / 101.579 |
| balanced_fresh | prefix_k3 | 4 / 4 / 4 | 0.015917 / 0.038667 / 0.124708 | 59.2815 / 62.4538 / 64.0887 |
| two_swap_fresh | two_swap_k4 | 5 / 5 / 6 | 0.016625 / 0.0361455 / 0.065209 | 95.5391 / 97.4323 / 99.1913 |
| two_swap_fresh | balanced_k4 | 5 / 5 / 6 | 0.019667 / 0.0337915 / 0.083541 | 96.4599 / 97.8728 / 100.981 |
| two_swap_fresh | prefix_k4 | 5 / 5 / 6 | 0.014209 / 0.033146 / 0.070458 | 96.5609 / 97.5494 / 100.149 |

All 576 milestone complete-instance totals are **unavailable (`null`)**. The measured setup plus query prefix is a partial sum: full curve setup and full one-time support setup without corpus custody, each charged once, plus exactly the retained per-relation query timers through the endpoint. Exact prefix timers for preparation, rank, group/solution/reference validation, linear solve, custody, receipt/serialization and outer wall time are unavailable. Source aggregate timers were never proportionally scaled into measured prefix timers.

Source full-process wall times and full-batch algorithm, corpus import/custody, receipt-construction, rank-diagnostics, solve-evidence and validation timers are retained separately. Component diagnostic timers can overlap the support-setup timer and are not added twice. Retained amortized allocations show the measured setup divided by four source corpora or 32768 retained relation queries; these are labeled accounting allocations rather than measured prefix costs. No cost is claimed to disappear from deployment.

Comparisons are descriptive within each existing shared source set/block/corpus. The balanced-fresh and two-swap-fresh campaigns are not spliced into a four-arm paired experiment. Production insertion_collisions sums probes minus one, so it records hash displacement rather than equal group values.

Protocol deviations: none in the frozen scientific case set. Darwin memory protection uses cooperative own-process peak-RSS checks at bounded streaming checkpoints (every 8192 receipts) and collision boundaries, with no unsupported claim of a hard address-space or external RSS enforcement. The 1800-second SIGALRM watchdog is process-liveness protection.

Output root: `/Volumes/SSD990/crypto-autoresearcher/.worktrees/factor-base-followups-20260911-d069d0/research/factor_base_followup_20260911_d069d0/collision_cost`. Exact command, input hashes, source and implementation revisions, dirty state, environment and own-process resource measurements are retained in receipt.json. Independent review and official research status decisions belong to the Coordinator after snapshot.
