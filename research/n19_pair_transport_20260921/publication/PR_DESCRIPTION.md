## What this publishes

This additive research archive makes the cold single-target IC benchmarks, exact Koblitz factor-base geometry, SAT controls, and native pair-transport comparison reviewable together. It includes frozen protocols, implementations, actual process receipts, raw archives, independent reviews, additive corrections, and Coordinator decisions. It does not change a production cryptographic API or claim an IC/rho crossover.

## Results and scope

| Package | Experiment/run evidence | Accepted finite result |
|---|---|---|
| Cold IC baseline and implementation iterations | `RUN-KIC-e3dbed`, `RUN-KIC-8b5038`, `RUN-KIC-56c897`, `RUN-KIC-a15078` | Allocation, pair-table capacity, target-certificate stopping, and matched ARM arithmetic controls. The latest N53 paired whole-process IC/rho ratio remains **3.2946**, not a speedup over rho. |
| N7 affine-domain SAT control | `EXP-KIC-424885` / `RUN-KIC-c2b1b7` | Correct finite control results; the frozen timing/propagation effect was not met. Filtering collapsed the intended affine-plane structure. |
| Complete-admissible N19 affine plane | `EXP-KIC-3df18c` / `RUN-KIC-234d11` | Exhaustive fixed-pool search selects a 152-point base with **6,189/6,909 exact-three coverage**, retaining **99.44%** of the unconstrained pool winner's coverage. |
| N19 same-base SAT pilot | `EXP-KIC-c3c732` / `RUN-KIC-859f34` | Native MITM completes 8/8 cases; all 24 scientific CMS calls are explicitly **INDETERMINATE** under the fixed cap. Reviewer-constructed satisfying assignments validate the positive formulas; they are not solver completions or timing samples. |
| Native orbit-canonical pair lookup | `EXP-KIC-7bcef8` / `RUN-KIC-278e3e` | All 144 native workers are valid. The primary paired wall ratio is **0.750927**, descriptive bootstrap interval **[0.655143, 0.864423]**. Exact inverse witness recovery is checked over the full finite membership/control domain. |

The final comparison uses eight fixed targets with six technical repetitions per method, not 144 independent targets. Its direct-native timing boundary differs from the earlier Python-wrapped pilot. Logical pair-table payload falls from 133,164 to 16,408 bytes; this is not an eightfold process-RSS reduction. A full cold IC job may reuse one table across its relation attempts, so the fresh-PDP construction gain cannot be multiplied by relation count.

## Review entry points

- [Latest pair-transport report](research/n19_pair_transport_20260921/REPORT.md) and [decision](ledger/decisions/DEC-20260921-c084cb.md).
- [Affine-plane search report](research/admissible_affine_factor_base_20260921/REPORT.md).
- [N19 SAT pilot report](research/n19_affine_sat_20260921/REPORT.md).
- [Matched cold IC/rho report](research/cold_arm_composition_ic_20260921/REPORT.md).
- [Publication authorization](research/n19_pair_transport_20260921/publication/authorization.json) and [archive/schema readback](research/n19_pair_transport_20260921/publication/archive_and_schema_readback.json).

## Validation and review limits

- Publication readback verifies **21 completed archive bindings / 865 bound-path checks**, including the archived and current committed blobs; no mismatches.
- All **16 new canonical hypothesis/question/proposal/experiment/run records** pass scoped schema checks.
- Changed-tree merge hygiene and run-record immutability are checked against current `origin/main`; hosted CI is separate.
- Independent source and permanently blind reviews support the later geometry, SAT, and pair-transport packages. Their exact read sets, model provenance, and finite inference limits are recorded. Older review-schema limits and failed attempts remain preserved rather than rewritten.
- This is an artifact-heavy archive: raw outputs, source snapshots, and host-specific macOS/arm64 binaries are intentional. Compatible host dependencies are documented; portable or reproducible builds are not claimed. Two historical JSON analysis artifacts are approximately 61 MiB each.
- Earlier full-ledger checks recorded unrelated AES-manifest errors. Scoped publication validation is not a full-corpus PASS; CI should report any current base-relative regressions.

The user explicitly approved publishing this full branch, including the earlier cold-IC, geometry, and SAT records, to this public repository. Historical local-only/publication-pending notes remain immutable statements from before that approval. This is a **draft PR**, with no merge or scientific-status promotion requested.
