# EXP-SGCP-EMBED-002 V18 Independent Pre-Run Accounting Review

## Findings

1. **BLOCKER — none for the accounting gate to separate launch-plan design.** Exact identity, cleanliness, hashes, manifest, static accounting, zero budgets, historical evidence counts, and authority records are internally consistent.

2. **HIGH boundary — execution remains prohibited.** The specification is `review_required`, `approved_by=null`, all canonical resource budgets are zero, `maximum_runs=0`, the ledger has `runs=[]`, and both launch-plan and execution authority are false. This accounting `GO` cannot authorize execution.

3. **MEDIUM hidden-cost caveat — canonical feasibility is unestablished.** Source reservations permit billions of replay/proof/cache operations and up to approximately \(2.34\times10^{14}\) retained-model cells. The proposed 900-second and 4-GB per-role values are unapproved hypotheses, not demonstrated bounds.

4. **MEDIUM accounting-boundary caveat — structural counts are not end-to-end costs.** Current receipts do not provide complete group-operation, field-operation, inversion, allocator, RSS, disk-I/O, cache-traffic, or memory-bandwidth costs. Nested JSON byte receipts overlap and are explicitly nonadditive.

5. **INFORMATIONAL — recorded tests remain historical receipts.** I did not rerun the producer, verifier, tests, validator, indexer, runner, or experiment. The recorded focused, validation/index, and repository-suite results are not fresh runtime evidence.

No toy result supports an attack, asymptotic improvement, relation generator, rank result, target descent, preprocessing crossover, or advantage over Pollard rho, parallel rho, BSGS, or another ECDLP baseline.

## Exact review receipt

| Item | Independently observed |
|---|---|
| Requested checkout | `/tmp/sgcp-v18-review-c02d31e` |
| Resolved checkout | `/private/tmp/sgcp-v18-review-c02d31e` |
| HEAD | `c02d31eb67e4e24f0866ba0a045e72dbe74a3844` |
| Parent | `72b14ad6ae539c027856de5584d46352837d680c` |
| Tree | `ec44de9a448e6b81a32b4f2f54764b17f3a859ae` |
| Branch state | detached |
| Initial state | tracked tree clean, index clean, no untracked entries reported |
| Final state | tracked tree clean, index clean, no untracked entries reported |

Parent-to-HEAD hygiene:

- 14 changed paths: 5 additions, 9 modifications, 0 deletions.
- 1,079 insertions and 337 deletions.
- No rename, submodule, executable-mode, or modified-file mode changes.
- All five additions are `100644`.
- `git diff --check` reported no whitespace errors.
- No changed path is under the experiment’s `development/` or `runs/` directories, and no runner, launch plan, or execution plan was introduced.
- The substantive source diff consists of V18 schema/version routing and CLI output ingress. Mathematical and accounting logic is unchanged.

## Ten hashes

All ten SHA-256 values in `development-test-log-v18.md` match the exact committed blobs.

| Committed artifact | Recomputed SHA-256 | Result |
|---|---|---|
| `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py` | `f9dc78ca8ff3b8d41d1e99b62a5d82a09c180ef1953dbb7401171882209dcea8` | MATCH |
| `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py` | `4310f6d5eeacace558a79670c944c55961f89f0c1db4aaee4d8b20d361501199` | MATCH |
| `tests/test_sgcp_embed_family.py` | `f5360f3f1dc345c9e29fb69fc673c67208918b5c8288c31f74dbf7f4a769b01e` | MATCH |
| `experiments/EXP-SGCP-EMBED-002/hypothesis.json` | `aca55cd96f5d94116d4a8ba811937f66c5087e26a0ca3d0a9672258538c49b86` | MATCH |
| `experiments/EXP-SGCP-EMBED-002/specification.json` | `579a4bd0bc8d8af67592635b3407754c95bb4a9cf5bb0a93fe668d65391e08a8` | MATCH |
| `experiments/EXP-SGCP-EMBED-002/contract.md` | `b93084cf19634533210fd0c48fd7ea2f84f9b718b9320f5d390b363f403df2fe` | MATCH |
| `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v18.json` | `3dafb3f249225f99583d9ce90b8630e93013d40a06dfa8bd8f6312cf77b483d5` | MATCH |
| `experiments/EXP-SGCP-EMBED-002/revision-response-v18.md` | `49a37f395b36c40440f59aeb7153df853e897182c7800e8d1c5b9694424d0ba9` | MATCH |
| `experiments/EXP-SGCP-EMBED-002/source-self-review-v18.md` | `20f62ef17789fb94446dd6b0d5a489f2db13ac601d88bb9ed4d03e4990b0ef32` | MATCH |
| `experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v18.json` | `587fd50831976921101060d1cac2e2d249f193b63b77bdf1362d08e1261a5c08` | MATCH |

## Manifest recomputation

I independently implemented the committed selection rules over:

```text
git ls-tree -rz --full-tree ec44de9a448e6b81a32b4f2f54764b17f3a859ae
```

Results:

| Receipt item | Recomputed value |
|---|---:|
| Full-tree entries | 904 |
| Selected entries | 200 |
| Exact repository paths | 14 |
| Flat-directory selections | 28 |
| Static experiment selections | 154 |
| Historical exact paths | 4 |
| NUL-delimited record bytes | 12,882 |
| SHA-256 | `bbff5e614b7b813f21fc7aa6e9ab2590155aed4f37e9359838193449e0bcb227` |
| Missing exact paths | 0 |
| Invalid selected mode/type/path entries | 0 |

Every selected entry is an ASCII, control-free `100644 blob`. I also read all 200 selected blobs directly from Git:

- Total selected blob bytes: `2,554,072`.
- Git object-ID recomputation mismatches: `0`.
- Supplemental reviewer digest over sorted `path NUL SHA256(blob) NUL` records: `1ba801916e84f725c153b71796b4010972f46b3d0c58e92f7589bc9245a719bb`.

The supplemental digest is not a repository protocol receipt. The authoritative byte-binding root remains the exact Git tree.

## Accounting and budget analysis

### Grid and row budgets

The canonical arithmetic is exact:

```text
4 bit sizes × 2 seeds × 3 B values × (3 coordinate families + 4 null replicates)
= 168 rows

168 rows × 4 cap cells
= 672 cap cells
```

Development and canonical authority:

| Budget | Value |
|---|---:|
| Historical development-row ceiling | 18 |
| Historical V1 rows consumed | 17 |
| Remaining historical arithmetic capacity | 1 |
| Additional V18 curve-family rows authorized | 0 |
| Generated V18 curve-family density rows | 0 |
| Canonical runs | 0 |
| `maximum_runs` | 0 |
| Wall seconds per run | 0 |
| Total CPU hours | 0 |
| Maximum memory GB | 0 |

The unused eighteenth historical row is not current authority.

### Completed provenance/predicate vector

I independently reimplemented the deterministic curve and predicate arithmetic from the committed public definitions without importing repository modules.

| Counter | Independent derivation | Result |
|---|---|---:|
| Prime candidates | \(2(16+32+64+128)\) | 480 |
| Curve draws | \(12+49+4+15+11+8+3+10\) | 112 |
| Curve hashes | \(3\times112\) | 336 |
| Point enumerations | \(2(12+47+4+14+11+8+3+10)\) | 218 |
| Predicate hashes | \(207+138+246+303+663+519+1287+855\) | 4,218 |

Per-curve reconstruction:

| Bits | Seed | Accepted `(p,a,b,q)` | Draws | Nonsingular draws | Point enumerations | Admissible roots | Predicate hashes |
|---:|---:|---|---:|---:|---:|---:|---:|
| 5 | 101 | `(29,4,28,31)` | 12 | 12 | 24 | 15 | 207 |
| 5 | 211 | `(23,2,17,19)` | 49 | 47 | 94 | 9 | 138 |
| 6 | 101 | `(47,17,20,37)` | 4 | 4 | 8 | 18 | 246 |
| 6 | 211 | `(43,35,37,47)` | 15 | 14 | 28 | 23 | 303 |
| 7 | 101 | `(89,69,72,107)` | 11 | 11 | 22 | 53 | 663 |
| 7 | 211 | `(89,36,83,83)` | 8 | 8 | 16 | 41 | 519 |
| 8 | 101 | `(199,55,163,211)` | 3 | 3 | 6 | 105 | 1,287 |
| 8 | 211 | `(131,58,79,139)` | 10 | 10 | 20 | 69 | 855 |

This confirms the static completed-path expectation `480/112/336/218/4218`. It is not evidence that a V18 canonical path ran: there is no committed canonical V18 document or run.

### Structural reservations

For the mixed canonical grid, the source reservation formulas imply:

| Reserved structural class | Recomputed upper bound |
|---|---:|
| Expansion cells | 473,928 |
| Graph candidate evaluations | 27,496 |
| Eligible-conflict checks | 3,514,280 |
| Eligible pair-output cells | 7,056,056 |
| Predicate hashes | 232,704 |
| Curve draws | 800,000 |
| Curve hashes | 2,400,000 |
| Registered-curve point enumerations | 1,600,000 |
| Replay nodes | 1,344,000,000 |
| Primary nodes | 1,344,000,000 to 3,360,000,000 |
| Metric-cache entries | 5,432,535,808 to 9,464,535,808 |
| Retained-model calls | 2,716,268,576 to 4,732,268,576 |
| Retained-model cells | 135,146,607,524,320 to 234,199,407,524,320 |

The ranges use the canonical minimum two-million-node primary budget and the admitted five-million-node maximum. These are reservation ceilings, not measured actual work, simultaneously resident objects, bytes, or expected runtime.

### Actual-work enforcement

Static inspection confirms:

- Work charges require exact positive integers; Boolean, zero, negative, float, string, and null values reject before mutation.
- Verification state is invocation-local, thread-owned, closed on exit, and required for evidence-bearing semantic paths.
- Completed rows equality-check graph candidates, eligible conflicts, eligible-squared pair-output cells, and degree-1/2/4/8 expansion cells.
- Completed documents equality-check the five provenance/predicate counters after all semantic rows pass.
- Curve-cache misses, entries, lookups, and frozen/semantic/primary point enumerations have completed-path exactness checks.
- Replay, proof, cache, and retained-model work is incrementally charged and reservation-dominated, but much of it is not independently equality-derived.
- Interrupted work retains prior and partial counters and sets `actual_work_complete=false`.
- Invalid completed undercharges and overcharges fail closed.

### Nested byte accounting

The producer records and the verifier independently recomputes canonical-JSON byte lengths for:

- the public model;
- the private audit;
- the row payload excluding accounting and row digest;
- each public cap object;
- each private cap object.

These receipts overlap and are explicitly nonadditive. They do not measure parsed Python object size, allocator retention, caches, peak RSS, disk footprint, I/O traffic, or complete serialized publication cost.

### Scaling and strongest-baseline boundary

The static combinatorial scaling is:

- degree-eight expansion: \(\Theta(B^8)\);
- degree-four candidates: \(\Theta(B^4)\);
- conflict and pair-output reservations: \(\Theta(B^8)\);
- retained-model cells per call: \(\Theta(B^8)\), multiplied by replay/primary search ceilings.

With fixed `B∈{4,6,8}` and only 5–8-bit toy curves, no defensible cryptographic exponent or crossover can be fitted. There is no complete operation or memory basis for comparison with Pollard rho with available automorphisms/endomorphisms, parallel van Oorschot–Wiener rho, or BSGS. No baseline win is claimed.

## Historical/current evidence accounting

| Evidence | Classification | Count |
|---|---|---:|
| `DEV-SGCP-EMBED-002-SMOKE/raw-result.json` | Historical V1, noncanonical | 1 row |
| `DEV-SGCP-EMBED-002-V1/raw-result.json` | Historical V1, noncanonical | 16 rows |
| `DEV-SGCP-EMBED-002-V1/run-manifest.json` | Historical development run manifest | 1 |
| `DEV-SGCP-EMBED-002-V1/verification-v4.json` | Verification of the same 16-row result, not additional rows | 16 verified rows |
| Generated V18 curve-family density rows | Current | 0 |
| Canonical V18 runs | Current | 0 |
| Experiment `runs/` entries | Current | 0 |
| Ledger run entries | Current | 0 |

The two raw results contain 17 distinct disclosed historical rows. The verification artifact does not increase that count.

`development-test-log-v18.md` records:

- focused suite: 81 tests, `OK`;
- record validation: 20 records;
- generated index byte-identical to `ledger.json`;
- repository unittest discovery: 225 tests with one preserved immutable-run-guard failure.

Those are historical receipts bound to matching blobs. They were not rerun in this review.

## External-resource boundary

Current canonical CPU, wall-time, and memory budgets are all zero. The hypothesis’s proposed 900 seconds and 4 GB per canonical role are not approved and have no current feasibility evidence.

Before any future execution authorization, a hash-complete runner must separately bind and measure:

- generator CPU and wall time;
- verifier CPU and wall time;
- peak RSS and allocator/parser retention;
- serialized output and artifact-store bytes;
- disk and I/O traffic;
- cache behavior and memory bandwidth;
- process count and parallelism;
- hard process limits and termination classification;
- executed commit, command, environment, immutable inputs and outputs;
- publication warnings and immutable external artifact receipts.

The enormous reservation ceilings make these obligations material rather than documentary. In-process structural receipts cannot establish compliance with a 900-second or 4-GB limit.

## Authorization boundary

The committed authority state is consistent:

- specification version: 18;
- status: `review_required`;
- `approved_by`: `null`;
- ledger status: `review_required`;
- ledger runs: `[]`;
- generated V18 density rows: 0;
- canonical runs: 0;
- `maximum_runs=0`;
- launch-plan authorization: false;
- execution authorization: false.

The producer’s CLI retains the decoded output string, but both canonical and development branches terminate with `PermissionError`. Public generated-curve and legacy-row construction remain disabled; density-row construction remains restricted to the exact frozen p=19, B=4 control.

The verifier change preflights decoded output strings before input verification and passes the same string to publication. Invalid terminal syntax therefore performs no curve, predicate, graph, replay, or proof work. Valid inputs enter the unchanged invocation-local charged path. No new uncharged mathematical route is introduced.

Caller-controlled `__fspath__` callbacks can act before validation, but those caller-created effects are explicitly outside verifier-created accounting. CLI values are exact decoded strings, so that callback boundary does not arise through ordinary CLI parsing. Publication filesystem work remains external I/O, not cryptanalytic work.

No launch plan, runner, execution plan, generated V18 data, or run artifact exists in the reviewed tree or parent-to-HEAD diff.

## Final verdict

**GO**

This is an accounting-only `GO` for the exact commit and tree to count as one required review toward a separately designed launch plan. It does not authorize launch-plan design by itself, execution, a budget increase, a generated curve-family row, a canonical run, or any cryptanalytic claim.

Any future launch-plan design remains contingent on fresh independent theory and red-team `GO` decisions for these exact bytes. Execution would then require a separately reviewed hash-complete plan with hard external resource containment.

## Handoff: EXP-SGCP-EMBED-002 V18 accounting closeout

### Claim or task

Independently determine whether exact V18 commit `c02d31eb67e4e24f0866ba0a045e72dbe74a3844` preserves the zero-authority accounting boundary and is accounting-ready for the separate launch-plan-design gate.

### Status

`OBSERVATION`: accounting verdict `GO`; research status remains `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

### Assumptions

- This review applies only to commit `c02d31eb67e4e24f0866ba0a045e72dbe74a3844` and tree `ec44de9a448e6b81a32b4f2f54764b17f3a859ae`.
- Recorded test results are historical receipts and were not rerun.
- Structural reservations are not CPU, field-operation, peak-memory, I/O, or bandwidth measurements.
- No relation generation, rank, linear algebra, target descent, rho comparison, exponent, deployment, or ECDLP claim is in scope.

### Evidence so far

- Detached cleanliness and exact commit, parent, and tree matched before and after inspection.
- All ten committed SHA-256 values matched.
- The 200-entry NUL-delimited manifest recomputed exactly.
- All selected entries were valid `100644 blob` objects, and all selected blobs were read without object-ID mismatch.
- Static independent arithmetic reproduced `480/112/336/218/4218`.
- Historical evidence is exactly 17 V1 rows and one development run manifest.
- Current authority remains zero generated V18 density rows, zero canonical runs, zero resources, and `maximum_runs=0`.
- CLI changes introduce no new uncharged mathematical route.

### Failure modes

- Treating worst-case structural reservations as practical runtime or memory bounds.
- Treating historical test receipts as fresh execution evidence.
- Treating nested byte receipts as additive or as peak-memory accounting.
- Treating this accounting `GO` as theory, red-team, launch, or execution approval.
- Extrapolating 5–8-bit fixed-B toy behavior to a cryptographic ECDLP attack.

### Next concrete action

Obtain fresh independent theory and red-team reviews of the same commit and tree; do not design a launch plan unless both also return `GO`.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/development-test-log-v18.md`
- `experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v18.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v18.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
