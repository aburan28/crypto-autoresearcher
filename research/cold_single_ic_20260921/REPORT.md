# Cold-start single-target IC: RUN-KIC-e3dbed

**Review status:** producer measurements are complete and committed; the independent primary review and separate post-hoc diagnostics are complete. The cold-start rho target has not been met by this run.

This experiment directly measured one fresh process per public known-answer target on the fixed Koblitz curve over GF(2^53), subgroup order 21,044,858,204,113. It used one computational worker in both algorithms, rebuilt every IC support table, retained all correctness evidence, and used the same ARM PMULL arithmetic backend in IC and signed-Frobenius rho. No target or factor-log precomputation was reused across processes.

The code changes are a common guarded ARM multiplication/squaring port for both algorithms and a candidate change that avoids reserving an unused full-pair HashMap in the signed-expanded IC path. All other candidate mathematics is unchanged. The common port passed 13 existing/new correctness tests, including independent bitwise multiplication and reduction controls at degrees 13 and 53. Three untimed conformance processes then matched the expected public answer, and the two IC variants had identical mathematical transcripts.

## Frozen experiment

The 96 scientific processes comprised 48 calibration processes and 24 untouched direct/rho pairs. Calibration compared 12 unmodified allocation controls at eta 1/128 with 36 allocation-only candidates at eta 1/128, 1/256, 1/512. All 12 same-density allocation control pairs matched on factor base, relation hashes, rows, ranks and answer. All 96 processes completed validly; no target was dropped, replaced or rerun.

| Calibration configuration | Orbit columns | Median whole-process seconds | Median peak RSS (decimal MB) |
|---|---:|---:|---:|
| Common ARM baseline, original allocation | 94 | 4.719426 | 898.646 |
| Allocation-only candidate, eta 1/128 | 94 | 4.620453 | 832.233 |
| Allocation-only candidate, eta 1/256 | 75 | 4.620417 | 438.755 |
| Allocation-only candidate, eta 1/512 | 60 | 6.409626 | 411.591 |

The frozen mechanical selector chose eta 1/256 (75 columns). Its median differed from eta 1/128 by only about 37 microseconds, so this is effectively a calibration tie; no robust density winner is inferred. The 75-column compact-array payload is 369,098,752 bytes versus 738,197,504 bytes at 94 columns. The allocation-only 94-column control has an observed paired median time ratio 0.979975 against its baseline, but calibration always put baseline first; this is not a confirmatory speed claim.

## Held-out result

| Arm | Median process seconds | Median child CPU seconds | Maximum peak RSS (decimal MB) | Median paired wall ratio vs rho |
|---|---:|---:|---:|---:|
| Signed-Frobenius rho | 1.324306 | 1.301499 | 174.621 | 1.000000 |
| Selected 75-column IC | 4.787709 | 4.505071 | 439.894 | 3.511028 |

The ratio column is the median of 24 matched per-target ratios, not the ratio of the two marginal medians. The deterministic 10,000-resample paired-bootstrap 95% interval is [2.757893, 6.672955]. Both the median < 0.95 gate and the upper interval endpoint < 1 gate failed. The producer field `eligible_for_independent_review:false` denotes failure of the finite positive-signal predicate; the independent primary review has passed and confirms this finite non-confirmation.

## Where the measured time went

For the selected IC held-out arm, median support setup was 1.562 seconds. Median collection was 2.475 seconds, including 2.329 seconds in the query kernel. The median linear solve was 0.000311 seconds. Independent base validation, relation reference validation and final solution validation remain charged and separately available in raw receipts. These are component medians; they must not be summed as though they were one measured process.

The separately sealed post-hoc review found that measured setup alone exceeded matched rho wall time in 18 of 24 cases; the median paired setup/rho ratio was 1.173159. This holds measured setup fixed in a counterfactual and is not a lower bound for a future implementation.

Exact rank checks of all 1,964 saved rows found a target-determining prefix before full rank in every transcript. The median earliest prefix was 73 rows (range 70–75), versus 79.5 rows for full rank (range 76–107). The paired prefix gap had median 7.5 rows and range 1–35. Zero target-column, target-unit-row, duplicate-row and nonzero-rescaling controls passed. No target-only solver or runtime saving was measured; implementing RHS-aware elimination and a valid early stopping rule is a concrete successor candidate.

The next frozen experiment is RUN-KIC-8b5038 in `research/cold_capacity_ic_20260921`: keep the 75-column base, arithmetic, Bloom size, and one-worker boundary fixed while doubling only active signed-expanded table slots. It uses 24 new targets and all six three-arm orders. Target-only stopping and the ARM specialized query port remain subsequent candidates with separate controls required.

## Measurement and custody limits

Primary wall time is the observed spawn-to-wait4-reap interval. It includes child setup, collection, validation and output; parent fsync/hash work is measured separately. Reap checks request 1 ms sleeps, which are not a guaranteed scheduling bound. CPU and peak RSS come from wait4 for each child. The 8 GiB resource boundary is cooperative sampling, not an OS-enforced address-space cap. No affinity or OS-cache-flush claim is made. Source/toolchain builds are recorded separately, without being hidden in an amortized per-target number.

All earlier preparation errors are retained: a failed literal executable-placeholder invocation, an absent candidate path before Popen, and an incorrect early parser. They ran no scientific cases. A racing second parent was rejected by the existing per-case directory guard before spawning any scientific child; the sole admitted runner completed the exact 96-case order.

This is a finite public-synthetic known-answer implementation study. It asserts no private/imported target capability, key recovery, asymptotic advantage, SOTA status, hypothesis promotion or research-goal completion.

## Canonical records

- [Frozen protocol](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/protocol.json)
- [Hardware fairness amendment](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/hardware_fairness_amendment.json)
- [Common ARM source patch](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/common_arm_port.patch)
- [Allocation-only candidate patch](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/candidate.patch)
- [Producer analysis](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/analysis.md)
- [Raw-process index](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/processes.jsonl)
- [Execution receipt](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/execution_receipt.json)
- [Verified snapshot receipt](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/snapshot_receipt.json)
- [Independent validation report](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/review/report.json)
- [Post-hoc diagnostic results](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/review/TASK-20260921-6ae79e/posthoc_diagnostics.json)
- [Coordinator disposition](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/ledger/decisions/DEC-20260921-6572be.md)
- [Original independent review plan](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/review_plan.json)
- [Post-hoc review addendum](/Volumes/SSD990/crypto-autoresearcher/.worktrees/cold-single-ic-20260921/research/cold_single_ic_20260921/review_diagnostic_addendum.json)

Local branch: `codex/cold-single-ic-20260921`. Producer snapshot: `b3eb7ce341`. Review admission: `16ba894e7a`. No remote push or PR has been made.
