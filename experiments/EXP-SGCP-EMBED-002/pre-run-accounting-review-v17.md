# EXP-SGCP-EMBED-002 V17 Fresh Pre-Run Accounting and Evidence-Boundary Review

## Findings, severity ordered

### Blocking findings

None.

### Residual boundaries

1. **High if promoted to an attack claim — no end-to-end attack comparison exists.** V17 does not measure relation probability, failed relation attempts, relation collection, rank, sparse linear algebra, factor-base logarithms, target descent, or offline/online crossover. Its counters are structural events, not complete field/group operations or attack cost. This limitation is explicit in [contract.md:395](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/contract.md:395>), [contract.md:651](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/contract.md:651>), and [hypothesis.json:76](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/hypothesis.json:76>). No hidden cost is omitted from a claimed attack win because no attack win is claimed.

2. **Medium — the structural ceilings admit extreme resource growth.** Independent arithmetic from the committed formulas permits 1.344 billion replay nodes, 3.36 billion primary-proof nodes, 14,217,930 aggregate cache entries per cap, and 9,554,448,960 aggregate cache insertions across 672 caps. The retained-model reservation reaches 586,452,159,659,520 evaluated cells. These are ceilings, not forecasts or simultaneous-memory claims, but they expose a material CPU/RSS/cache risk that a launch plan must constrain externally. See [verify_sgcp_embed_family.py:95](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:95>) and [verify_sgcp_embed_family.py:125](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:125>).

3. **Low — all test outcomes are historical.** Static inspection reproduces 81 focused `TestCase` methods, 225 repository-wide `TestCase` methods, 27 excluded module-level pytest-style functions, and the validator’s 19 selected record paths. No pass/failure result was rerun. The index statement is a historical byte-identity assertion without its comparison command or generated-byte hash in the V17 log; it is not fresh validation evidence. The relevant ledger entry was instead checked directly from Git bytes.

4. **Low — the manifest’s own digest binds path names, not bytes.** This is deliberate and correctly disclosed. Its pathname can be included without recursion because its contents are not an input to the path-name digest. The exact Git tree supplies the byte binding. See [review-surface-manifest-v17.json:6](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v17.json:6>) and [review-surface-manifest-v17.json:69](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v17.json:69>).

5. **Low — publication and portability boundaries remain external.** Receipts are unkeyed and sequential rather than pair-atomic; POSIX three-or-more-leading-separator behavior is runtime-specific; process death, memory exhaustion, hostile same-user mutation, and durability remain outside the guarantee. These are disclosed at [protocol-amendment-v17.json:40](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v17.json:40>).

## Checkout and review boundary

| Item | Verified value |
|---|---|
| Requested path | `/tmp/sgcp-v17-review-d6b642d` |
| Physical path | `/private/tmp/sgcp-v17-review-d6b642d` |
| Commit | `d6b642defccddab7629678ee3514c48228844bfa` |
| Sole parent | `574b4c67a894e48715107e730c0b7b33b9fab1c5` |
| Tree | `f27c736a2660155521b6da913bb1e7e0f3a9bffc` |
| HEAD state | Detached, `## HEAD (no branch)` |
| Initial cleanliness | index diff 0; worktree diff 0; zero status entries |
| Final cleanliness | index diff 0; worktree diff 0; zero status entries |
| Proposed artifact | `experiments/EXP-SGCP-EMBED-002/pre-run-accounting-review-v17.md` — not written |

Inspection used Git objects, shell SHA-256, static AST/path counting, and independent arithmetic that imported no repository module. No test, producer, verifier, validator, indexer, runner, or experiment was executed. Mutable worktree file contents were not used.

## Ten-hash reproduction

All ten SHA-256 values recorded at [development-test-log-v17.md:16](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/development-test-log-v17.md:16>) reproduce from `git show <commit>:<path>` bytes.

| Artifact | Recomputed SHA-256 | Result |
|---|---|---|
| `src/sgcp_embed_family.py` | `e9ba02997893cd2307e7489b7dea15e270e584af80797ded1c7d77c1372ad454` | MATCH |
| `src/verify_sgcp_embed_family.py` | `e3ff7af6c379b9bc52ec0d1e3e6f9ef874cf258351665f897462a4ee1c93612a` | MATCH |
| `tests/test_sgcp_embed_family.py` | `f35ec050c2acfcdbb4332abf517d91d2366f1bd8217bc5ed077408691fbfd745` | MATCH |
| `hypothesis.json` | `4c5763186ae60fc63f711315d7861fb0fafb233788c59a778210035178cd2052` | MATCH |
| `specification.json` | `c31b14595d6750617c6d2f7933b850c6144d94d35fb9c8aaac3b11ba4fcb3ea9` | MATCH |
| `contract.md` | `5f7d610b3a138d54c47ff2a5c96f2ae8609547b92c05ed59e0bfaed0372c10fb` | MATCH |
| `protocol-amendment-v17.json` | `6ebdb14f160e75d9bb6b74d6d5b72797d03c0c234e8e0558c9ac63ca68a18465` | MATCH |
| `revision-response-v17.md` | `1eb21f4a7ecfa5c26ceaff8f2a47351d3bfe324225a8f3928b072af33b48db76` | MATCH |
| `source-self-review-v17.md` | `9a9c750c9271b6180110a5d8c9d53bb804fd41991b452251614eb225bde576f3` | MATCH |
| `review-surface-manifest-v17.json` | `e8e21e6de35d775efadee6f3b8584273923af8394247fd9e28e388594c5b1e39` | MATCH |

## Manifest reproduction and classification

The finite rules at [review-surface-manifest-v17.json:22](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v17.json:22>) independently produce:

| Rule class | Paths |
|---|---:|
| Repository exact paths | 7 |
| Repository globs | 28 |
| Static experiment paths | 144 |
| **Total unique existing paths** | **179** |

Canonical sorted POSIX paths joined by newline with one terminal newline hash to:

`bc8034d20ac3d092270d749b6cb363df4f8f4531bccc0dd9a6616120f51de952`

This exactly matches [review-surface-manifest-v17.json:58](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v17.json:58>). There were no duplicate or missing inventoried paths.

The manifest is a valid review-surface binding, not an execution manifest:

- It records no predicted commit or tree and declares `self_hashing: false`.
- Its own pathname is harmlessly included in the path inventory; its bytes are not hashed into that receipt.
- The exact Git tree binds its bytes and all other repository bytes.
- Its authority block sets generated rows, canonical runs, and `maximum_runs` to zero and both authorization flags false at [review-surface-manifest-v17.json:62](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v17.json:62>).

## V17 parent-diff audit

Object-level comparison against parent `574b4c67a894e48715107e730c0b7b33b9fab1c5` found no change to the curve grid, predicate formulas, representative compiler, optimizer objective, family-gate arithmetic, thresholds, or accounting formulas.

- Producer changes are V16→V17 schema/version/diagnostic routing substitutions and a family-gate criterion-version label. The mathematical constants remain at [sgcp_embed_family.py:45](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:45>).
- Verifier mathematical constants and reservation formulas remain at [verify_sgcp_embed_family.py:54](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:54>).
- The only substantive verifier logic change is the pre-normalization raw-path grammar and its reuse by the descriptor walker at [verify_sgcp_embed_family.py:7063](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7063>).
- The frozen compiler, optimizer, and gate remain defined at [specification.json:52](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:52>), [specification.json:70](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:70>), and [specification.json:84](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:84>).
- The committed characterization that V17 changes path-domain precision, controls, and review binding only is supported by the diff; see [revision-response-v17.md:23](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/revision-response-v17.md:23>).

## Canonical provenance/predicate vector

Independent reimplementation of the committed SHA-256 curve draw, rejection, point-enumeration, Möbius-nonce, and null-root-count rules reproduced the completed vector. The governing formulas are at [sgcp_embed_family.py:278](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:278>), [sgcp_embed_family.py:348](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:348>), [sgcp_embed_family.py:459](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:459>), and [verify_sgcp_embed_family.py:641](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:641>).

| Bits/seed | Accepted `(p,a,b,q)` | Draws | Nonsingular draws | Point enumerations | Admissible roots | Predicate hashes B4/B6/B8 |
|---|---|---:|---:|---:|---:|---:|
| 5/101 | `(29,4,28,31)` | 12 | 12 | 24 | 15 | `69/69/69` |
| 5/211 | `(23,2,17,19)` | 49 | 47 | 94 | 9 | `45/45/48` |
| 6/101 | `(47,17,20,37)` | 4 | 4 | 8 | 18 | `84/81/81` |
| 6/211 | `(43,35,37,47)` | 15 | 14 | 28 | 23 | `101/101/101` |
| 7/101 | `(89,69,72,107)` | 11 | 11 | 22 | 53 | `221/221/221` |
| 7/211 | `(89,36,83,83)` | 8 | 8 | 16 | 41 | `173/173/173` |
| 8/101 | `(199,55,163,211)` | 3 | 3 | 6 | 105 | `429/429/429` |
| 8/211 | `(131,58,79,139)` | 10 | 10 | 20 | 69 | `285/285/285` |
| **Total** | 8 curves | **112** | **109** | **218** | — | **4,218** |

Further reconciliation:

- Prime candidates: `2 × (16 + 32 + 64 + 128) = 480`.
- Curve hashes: `3 × 112 = 336`.
- Point enumerations: `2 × 109 = 218`.
- Three of 112 draws were singular and therefore did not perform point enumeration.
- Predicate hashes include failed Möbius nonce attempts and all four null-replicate admissible-root hashes.
- The committed test literal agrees at [test_sgcp_embed_family.py:3538](</private/tmp/sgcp-v17-review-d6b642d/tests/test_sgcp_embed_family.py:3538>).

Thus the exact vector is:

`480 prime candidates / 112 draws / 336 curve hashes / 218 point enumerations / 4,218 predicate hashes`

These are verifier provenance and predicate events—not field operations, group operations, inversions, instructions, or attack cost. That distinction is explicit at [contract.md:310](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/contract.md:310>) and [specification.json:101](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:101>).

## Hidden-cost audit

| Cost category | V17 status | Accounting conclusion |
|---|---|---|
| Offline/online split | No online final-join structure; no preprocessing crossover | Unmeasured and excluded. [literature-review-v1.md:37](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/literature-review-v1.md:37>) |
| Storage/advice | Source-table and JSON byte receipts exist, but nested sizes overlap | Not a complete storage model; serialized canonical B6/B8 output remains unmeasured. |
| CPU and field/group operations | Structural cells only | No complete CPU, field-operation, inversion, or group-operation total. |
| Wall time | Producer values would be observational only | No current V17 role timing; active wall budget is zero. |
| Peak RSS/parser/allocator | Input/source ceilings exist | No peak-RSS, parser-object, allocator-retention, or object-overhead measurement. |
| Cache and bandwidth | Insertions/calls structurally counted | No byte occupancy, cache traffic, or memory-bandwidth measurement. |
| Disk/I/O/durability | Publication semantics controlled | No disk volume, I/O throughput, filesystem-support, or durability proof. |
| Verifier | Structural verifier work is separate | Future verifier CPU, RSS, wall time, disk, and I/O remain mandatory role costs. |
| Relation probability/failures | Not implemented | Curve/predicate rejection counts are not relation-attempt counts. |
| Linear algebra/rank | Not implemented | No matrix dimensions, density, rank, or sparse-LA cost. |
| Descent/individual logs | Not implemented | No target descent or individual-log path. |
| Parallelism | No process/worker model | No processor count, communication, distinguished-point storage, or wall-time scaling. |

The exclusions are accurately stated at [contract.md:410](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/contract.md:410>), [protocol-amendment-v17.json:48](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v17.json:48>), and [specification.json:102](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:102>).

## Benchmark table

| Baseline/component | Proper accounting boundary | V17 comparison |
|---|---|---|
| Pollard rho, including applicable automorphism/endomorphism improvements | Approximately square-root group work; distinguish constants, failed walks, memory, and parallel wall time | Not comparable: V17 has no ECDLP solver, complete group-operation count, or scaling law. |
| BSGS/MITM | Square-root group work and square-root stored group elements, including lookup/storage cost | Not comparable: no target lookup, memory-normalized solver, or end-to-end result. |
| van Oorschot–Wiener parallel collision search | Rho-like total work plus processors, distinguished-point storage, communication, load balance, and wall time | Not comparable: V17 has no parallel/process or communication model. |
| Index-calculus/PDP pipeline | Factor-base construction, decomposition probability, failed attempts, relation collection, storage/advice, rank/linear algebra, factor-base logs, and target descent, split into preprocessing and online work | V17 measures only a toy structured-support prerequisite. Every attack-bearing component is absent. |

The structured-model expression `soft-O(S*T^2/q + delta*T)` in [literature-review-v1.md:8](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/literature-review-v1.md:8>) is not itself a conventional-encoding ECDLP attack cost and must not be compared directly to rho.

## Scaling estimate

V17 fixes:

- four 5–8-bit strata;
- two seeds;
- three fixed `B` values;
- seven families/replicates per curve-B pair;
- 168 rows and 672 cap cells.

See [specification.json:9](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:9>). Four tiny bit sizes and fixed `B={4,6,8}` support no fitted exponent or `n^(1/5)` schedule; this is explicitly prohibited at [contract.md:651](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/contract.md:651>).

Current scaling status:

| Quantity | Estimate |
|---|---|
| SGCP attack exponent | Unknown; no attack pipeline |
| Relation yield/probability | Unknown |
| Rank/LA scaling | Unknown |
| Target descent | Absent |
| Preprocessing/online crossover | Unknown |
| Pollard-rho crossover | Undefined |
| Canonical computational feasibility | Unmeasured, especially B6/B8 |
| Valid conclusion | Finite toy support experiment only |

## Budget, run, and authority audit

- Active specification status is `review_required`, version 17 at [specification.json:3](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:3>).
- Active budgets are exactly zero for wall time, CPU, memory, and `maximum_runs` at [specification.json:209](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:209>).
- Generated-row authorization is zero at [specification.json:112](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:112>).
- `ledger.json` has `runs: []`, `review_required`, and version 17 at [ledger.json:126](</private/tmp/sgcp-v17-review-d6b642d/ledger.json:126>).
- The active research-ledger row says zero generated V17 rows, zero runs, maximum runs zero, and forbids launch-plan design or execution pending reviews at [research_ledger.md:29](</private/tmp/sgcp-v17-review-d6b642d/research_ledger.md:29>).
- No V17 execution plan, launch plan, approval lock, runner receipt, or `runs/` artifact exists.
- `approved_by` is null, and execution-plan/immutable-run records are explicitly future artifacts at [specification.json:370](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/specification.json:370>).
- The generic runner rejects `review_required` before launch at [runner.py:1422](</private/tmp/sgcp-v17-review-d6b642d/src/crypto_autoresearcher/runner.py:1422>) and independently requires positive wall/CPU/memory budgets at [runner.py:1457](</private/tmp/sgcp-v17-review-d6b642d/src/crypto_autoresearcher/runner.py:1457>).
- The sole run-like path is historical `development/DEV-SGCP-EMBED-002-V1/run-manifest.json`, explicitly `canonical: false`, based on old commit `90246d…`, with a dirty originating worktree at [run-manifest.json:2](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/development/DEV-SGCP-EMBED-002-V1/run-manifest.json:2>). It supplies no V17 authority.

Therefore the exact reviewed commit contains no artifact authorizing launch-plan design or execution.

## Historical test-receipt audit

| Receipt | Historical recorded result | Fresh static scope check |
|---|---|---|
| Focused suite | 81 passed in 3.880s at [development-test-log-v17.md:36](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/development-test-log-v17.md:36>) | Current Git bytes contain exactly 81 `TestCase` methods in `test_sgcp_embed_family.py`. |
| Record validator | 19 records at [development-test-log-v17.md:75](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/development-test-log-v17.md:75>) | Static application of the committed selector at [records.py:184](</private/tmp/sgcp-v17-review-d6b642d/src/crypto_autoresearcher/records.py:184>) finds 16 decisions plus research question, hypothesis, and specification. Schema validity was not rerun. |
| Repository index | Generated index reported byte-identical to `ledger.json` at [development-test-log-v17.md:88](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/development-test-log-v17.md:88>) | Historical only; no fresh index was generated. The current SGCP ledger entry was inspected directly. |
| Repository `unittest discover` | 225 tests, one failure at [development-test-log-v17.md:94](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/development-test-log-v17.md:94>) | Current Git bytes contain exactly 225 `TestCase` methods. The 81 focused methods are a subset, not additional tests. |
| Sole failure | Immutable-run guard refused overwrite at [development-test-log-v17.md:112](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/development-test-log-v17.md:112>) | Named method exists at [test_sgcp_embed.py:627](</private/tmp/sgcp-v17-review-d6b642d/tests/test_sgcp_embed.py:627>). Failure outcome remains historical. |
| Pytest-style exclusions | 27 excluded functions at [development-test-log-v17.md:108](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/development-test-log-v17.md:108>) | Static AST count is exactly 16 in [test_outer_translator.py:62](</private/tmp/sgcp-v17-review-d6b642d/tests/test_outer_translator.py:62>) and 11 in [test_outer_translator_floor.py:101](</private/tmp/sgcp-v17-review-d6b642d/tests/test_outer_translator_floor.py:101>). |

The receipts are correctly presented as recorded development observations, not fresh independent execution evidence. The index receipt’s missing command/hash is retained as a low evidence-boundary caveat.

## Overclaim audit

No V17 artifact claims:

- a relation generator or relation probability;
- rank or linear-algebra success;
- factor-base logarithms or target descent;
- an offline/online preprocessing crossover;
- superiority to rho, BSGS, or van Oorschot–Wiener;
- an asymptotic exponent;
- deployment relevance or an ECDLP break.

The strongest allowed future positive result is a toy coordinate-structure signal, not an ECDLP claim, at [contract.md:595](</private/tmp/sgcp-v17-review-d6b642d/experiments/EXP-SGCP-EMBED-002/contract.md:595>). No attack-comparison overclaim was found.

## Final verdict

**GO for separate launch-plan design only**

This accounting-lane verdict is not execution approval and does not establish a mathematical, cryptanalytic, asymptotic, preprocessing, or ECDLP claim. It is only one input to the repository’s required multi-review and coordinator process. Any launch-plan design must remain non-executing and must bind exact bytes, role commands, immutable paths, external CPU/wall/RSS/disk/I/O limits, verifier cost, storage/cache/bandwidth accounting, failure handling, and an `INCONCLUSIVE` resource-exhaustion outcome.

## Handoff: V17 fresh pre-run accounting review

### Claim or task

Preserve this fresh exact-object accounting review and use it only as an input to a separate, non-executing launch-plan design review.

### Status

`OBSERVATION` — no blocking accounting or evidence-boundary defect was found at the exact reviewed commit; all residual boundaries above remain binding.

### Assumptions

- The review scope is exactly commit `d6b642defccddab7629678ee3514c48228844bfa`, sole parent `574b4c67a894e48715107e730c0b7b33b9fab1c5`, and tree `f27c736a2660155521b6da913bb1e7e0f3a9bffc`.
- Test and validator outcomes are historical receipts and were not rerun.
- Structural counters are not attack cost.
- No execution, mathematical claim, or cryptanalytic claim is authorized.

### Evidence so far

- All ten V17 Git-blob SHA-256 values match.
- The 179-path manifest and path-name digest reproduce exactly.
- The manifest is non-self-referential and review-only.
- V17 changes routing, raw-path policy, controls, and governance binding—not mathematical or accounting formulas.
- Independent arithmetic reproduces `480/112/336/218/4218`.
- Active generated-row and run budgets are zero; `maximum_runs=0`.
- No V17 launch plan, approval lock, runner receipt, run directory, or execution authority exists.
- The detached checkout remained clean before and after inspection.

### Failure modes

- Treating provenance/predicate counters as field or group operations.
- Treating toy support as relation yield or an attack.
- Omitting offline work, storage/advice, failed attempts, rank, linear algebra, descent, verifier cost, or external resources.
- Treating worst-case structural ceilings as demonstrated feasibility.
- Treating historical test receipts as fresh execution evidence.
- Treating this review alone as coordinator approval.

### Next concrete action

Prepare one separate hash-complete, non-executing launch-plan design that binds the exact commit/tree and specifies immutable inputs, exact producer/verifier commands, separate-role accounting, hard CPU/wall/RSS/disk/I/O limits, cache/storage/bandwidth measurement, failure and `INCONCLUSIVE` handling, and continued zero execution authority; then submit that design for independent review.

### Artifact paths

- Proposed only, not written: `experiments/EXP-SGCP-EMBED-002/pre-run-accounting-review-v17.md`
- `experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v17.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v17.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/handoff.md`
