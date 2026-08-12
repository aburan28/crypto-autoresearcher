# TT Target Supervised Development Preflight V6

## Status and claim boundary

Semantic status: `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

Stage provenance and namespace supervision status: `GO` within the stated
development model.

Full target-partition implementation status: `REVISE`.

This checkpoint does **not** freeze source advice, authorize a campaign,
produce a locator, establish index calculus, improve Pollard rho, or establish
an ECDLP breakthrough. The experiment still has no `execution_plan`.

## Review sequence and repairs

Independent reviews found and then rechecked four supervision failures:

1. V14 allowed reads outside the stage and parent-pinned runtime.
2. V15 allowed any transient path under the stage and could miss a
   create-read-delete race.
3. V16 could bind a stale vnode during batch monitor registration on APFS.
4. V17 could adopt modified post-copy bytes as its first trusted baseline.

V18 closes those findings in the reviewed stage model:

- Seatbelt denies file-data reads by default and admits only literal staged
  paths plus parent-snapshotted Python/NumPy runtime filters.
- Role and harness code is retained in parent memory and SHA-bound to the
  static audit. The matrix, target manifest, candidate bundle, and verifier
  input are also staged from parent-retained bytes.
- The first stage manifest must exactly equal the retained-byte manifest.
- The stage directory vnode is registered before enumeration. Each file vnode
  is registered immediately after open and bound by device/inode/type to its
  path.
- A second pre-run snapshot and a post-run snapshot must match the approved
  bytes and watched identities. Setup or run-time vnode events fail closed.
- Backend check expectations are parent-derived from the execution matrix and
  require exact JSON types and exact expected/observed values.
- Child `read_files` rows are diagnostic telemetry, not authority.

The final follow-up review marked the modified-baseline counterexample closed
and found no further high-severity stage provenance or monitor fail-open within
this model.

## V18 evidence

All artifacts remain outside the repository and report
`artifact_freeze_authorized=false`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `target-static-closure-audit-development-v18.json` | 2,064 | `7bd258cacbeaa388de7ba3192079538bad0b2a9d375a1d7f23e24f90061e94f2` |
| `target-generator-staged-development-v18.json` | 1,000,952 | `82249f69ccb0608a45dead5bd161a851282c873968bd6185a6b116f5bb360dce` |
| `target-verifier-staged-development-v18.json` | 8,360 | `baf574fab335c6602c91efb864b3b78f74e6279414eb6cba92ff270d86d3446c` |
| `target-generator-staging-receipt-development-v18.json` | 334,428 | `a97301e825f313929865bd1ad8942976fe3a1039da0c3daefde6a85ce3393bfc` |
| `target-verifier-staging-receipt-development-v18.json` | 333,216 | `809f73733498b81c12378b2dd43aefad67848feaf7a5ceb3fc4093ea4736f7ca` |
| `target-mutations-development-v18.json` | 6,029 | `9fb59ab8509adb9853c084c44a5e1ba238efe07e00d9c8ce65c37cb8d677de03` |
| `target-order-invariance-development-v18.json` | 2,412 | `4303834628518bbace38abaae4ce7531a90fa7f05ed450c5ceceafcea7ad5a82` |

All seven records report `valid=true`. The static harness closure is
`cc0126aa6a853a557b93cf3de300a29d2eb0b6ee9bd15ebe8ccfa00ea02beaee`.
Producer and verifier receipts report:

- retained approved manifest equals the first content snapshot;
- watched device/inode rows equal both pre-run and post-run path identities;
- zero setup mutation events and zero run mutation events;
- matching pre/post runtime closure
  `f312a51165c62d3c510945658351b960ac63713f2c6dcdb8f7df16ae00944098`;
- 1,381 and 1,380 diagnostic child read-file rows.

The parent runtime closure covers 5,819 standard-library files outside
`site-packages`, 1,295 NumPy package files, 23 NumPy dist-info files, exact
interpreter/framework nodes, two NumPy command files, the OS version plist,
and `/dev/null`. The independently derived 1,320-file NumPy distribution
closure equals the execution-matrix digest
`8a802a5be64dbec34c009c0fb7b76c3b2da97c2b92ec1ee9e66796ad6dcace94`.

## Accounting and controls

The producer emits 25 target records and reports:

```text
adds                              11,847,613
subs                               2,906,073
muls                              15,044,649
squares                                   75
inversions                             1,919
reductions                          6,105,159
comparisons                         3,227,775
hash bytes                            343,925
copied words                        2,235,640
logical traffic words             55,225,872
peak live field words                239,647
```

The verifier checks 35,379 target tuples and 100 exact ranks, with 89,097,141
logical traffic words and a 356,126-field-word peak. All 22 development
mutations fail closed, forward/reverse target schedules agree, and 54
experiment tests pass. The repository suite passes 144 tests. These controls
do not substitute for the frozen 29-mutation campaign.

## Remaining model boundary and gates

- Runtime trees are parent-hashed before and after execution, but concurrent
  same-UID runtime mutation and restoration is not excluded.
- macOS shared-cache identity is not parent-pinned. Loader presence remains a
  matrix-bound child observation under the reviewed source closure.
- The V18 result is development evidence on the pinned local backend, not a
  portable adversarial isolation theorem.
- The frozen 29-mutation generator/verifier partitions have not run.
- No source or target artifact is frozen and no `execution_plan` exists.

## Next concrete action

Write and review a runtime-boundary decision record that either adds external
runtime/shared-cache identity enforcement or explicitly freezes those two
limitations before authorizing the 29-mutation campaign.
