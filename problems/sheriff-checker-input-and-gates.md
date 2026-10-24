# Deep sheriff sweep misclassifies several checker failures

- **Status:** open
- **Kind:** validation instrument and environment gap
- **Affected work:** [`tools/sheriff.py`](../tools/sheriff.py), the published-main deep sweep case `SHF-20261024-46b7da`, and any claim that the sweep alone cleared all registered sessions or cryptanalysis Lean targets
- **Next action owner:** sheriff checker maintainer for implementation; independent Validator for controls and exact-head replay
- **Last updated:** 2026-10-24

## Problem

The deep sweep detects real coverage gaps but also reports failures caused by its own input preparation and obsolete commands. Its `ecbench-sessions-integrity` checker sends tracked gzip-only directories to `ecbench verify`, which opens the uncompressed filenames. On the 2026-10-24 published-main snapshot the checker reported 388 passes, 53 failures, and 176 sessions not run before its 3,600-second budget. A traced missing-file case passed 528 of 528 bound records after temporary decompression. Independent source-hashed replays then covered all 617 committed ecbench/v1 directories: 603 complete, bound, zero-problem integrity passes, ten explicitly interrupted and unbound archives, and four declared-complete scratch pilots missing `spec.json` and `host.json`. One temporary replay initially omitted nested `exec/` files and falsely failed a complete session; its corrected audit passed, with the original failed receipt retained. The four missing-input archives remain a separate custody gap in crypto, not a sheriff checker failure.

Two configured cryptanalysis Lean commands point to files absent from the pinned tree and exit 127. The factor-base archive command initially failed before checking data because its Python environment lacked NumPy; an isolated rerun at the same source head verified 2,681 archives with zero problems. The formal-target checker timed out after 27 receipts and left one untracked generated Lean audit file in the worktree. That file was preserved with its hash in the case and removed from the audited checkout. A separate pinned, byte-equivalent target sweep verified all 84 registered formal targets, but it does not repair the deep sweep's timeout or establish historical execution.

The sweep's failed statuses must therefore be interpreted per checker. They are not theorem counterexamples or evidence that compressed archive bytes are invalid. The factor-base citation-reference checker and the full ledger validator have independent failures that still require their own review.

## Evidence and uncertainty

- The exact pinned heads, checker statuses, canary result, and worktree-change flag are in [`sweep.json`](../research/sheriff/SHF-20261024-46b7da/sweep.json).
- [`findings.yaml`](../research/sheriff/SHF-20261024-46b7da/findings.yaml) cites the missing-file trace, both normalized session batches and nested-evidence correction, absent Lean paths, NumPy rerun, and preserved temporary Lean file.
- Passing `ecbench verify --replay 0` checks archive integrity and recorded outputs. It does not independently repeat the original timing or prove prescribed execution.

## Resolution gate

- [ ] Normalize tracked gzip inputs and nested evidence in a temporary directory, retain original-byte hashes, and audit completion and records binding separately from local consistency.
- [ ] Replace absent cryptanalysis Lean paths with current source-bound gates and test an expected-pass and expected-fail fixture.
- [ ] Provision required checker dependencies or classify missing environments as coverage gaps, then rerun the factor-base archive verifier.
- [ ] Write formal target audit snippets only under scratch and clean them on timeout. Bound the checker so it can report partial coverage without changing the source worktree.
- [ ] Recheck the exact published heads with a passing canary and record per-session outcomes, timeouts, and unreviewed records. Independently review any remaining scientific claim before changing its status.

## Next discriminating step

Implement the gzip-normalized ecbench checker with one passing compressed fixture, one nested-evidence fixture, one malformed archive, and one interrupted unbound fixture; run those controls before another full sweep. A corrected instrument result would clear only the instrument gap. The four scratch pilots still need their exact hashed source inputs. The ledger, factor-base citation references, theorem statement fidelity, execution binding, and performance comparisons remain separate gates.
