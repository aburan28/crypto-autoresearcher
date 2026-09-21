# EXP-ECDLP-RECURSIVE-002 v2 independent pre-run red-team audit

**Verdict: REVISE. Do not approve or launch either canonical 31+31 run from commit `878acef6753fb6a4d7ed3fc8347bc453203d801c`.**

This is a pre-run protocol verdict, not evidence for or against the coordinate-family hypothesis. The target worktree `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy` was read only, tracked-clean, and exactly at the requested commit. No canonical evidence execution was performed.

Severity scale: `S0` blocks approval; `S1` can admit false canonical provenance/resource claims or materially misleading controls; `S2` narrows interpretation or durability without invalidating the repaired toy arithmetic.

## Scope and method

Audited in full: `AGENTS.md`, the v1 audit, v2 revision response, contract, specification, hypothesis, research question, checklist, implementation/analysis/handoff prose, generator, independent verifier, generic runner/CLI/record validation, experiment and run-manifest schemas, experiment tests, runner tests, and the pinned predecessor arithmetic sources.

All execution was from a temporary `git archive` export of the immutable commit. The repository suite passed all 24 tests in 8.983 seconds. Reduced/synthetic checks were correctness and falsification controls only:

- A nonfrozen nine-curve `2+2`-null, 128-target, four-order-seed, one-rho smoke completed valid in 18.91 seconds with 68,190,208 bytes child peak RSS and a 2,297,284-byte result. Independent reduced verification completed valid in 19.43 seconds with 74,186,752 bytes child peak RSS. The generator artifact SHA-256 was `12ddbb0ffe78bd40c81613555c0c8941f8d22aec1fa635cbfee0cee4eae01290`. This was not a hypothesis run.
- Independent combinatorial checks covered 90 `(S,k)` cases for the uniform-permutation first-hit formula.
- Synthetic harness checks attacked mutable plans, forged predecessors, post-launch tree mutation, descendant processes, and path aliases.

## Frozen hashes

The committed hashes independently match the v2 prose, verifier constants, and current execution-plan entries where applicable:

| Artifact | SHA-256 |
|---|---|
| `specification.json` | `f71157e2daa6c765aca545a91b3db5bfef0818ae21394ca1ffbcb58eb5466c26` |
| `contract.md` | `b629f5821dc13a60165511e07b6899fbe37f84256d75120422ceb6c73546629d` |
| v2 generator | `b3c9cd083af9e838c009bf76f83ac4fd6909c4c9160fcaada122d9f0a6de95bd` |
| v2 verifier | `77b45770d29835166b6dc81a91b10fc44ae6c47f55d79535a6a3a85a4f60bc48` |
| runner | `4da90cea377c1554b1fabbd4c314e37176d1bd3ad9d41a98b1f64276015f6b77` |
| experiment schema | `f9587a024b6e10ba93febe0b27af02767fe7f88a9b180512950190691a1e4816` |
| prior independent arithmetic verifier | `d677d1bc9c7efa9c3a94704eddd2f80ea651074f55c4a8452e5295f5d9797552` |
| prior recursive source | `c8e6986dd48e341b3e585a170990a018210602f99fc6cd748b81902f1b4e446d` |
| coordinate-energy source | `7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71` |

Using sorted compact UTF-8 JSON with no trailing newline, the exact execution-plan SHA-256 is `1649f4f0c5f3ffd718a8199b521085df65a87bb8de7de40faf77fd5a078fea4d`. The generator-run object hash is `fd71f71bc9733ef09c1cf916c23564b15aaf7b57f724d9a94bc87289bbedf7d2`; the verifier-run object hash is `67c34836faec3f78c8d7c03c7d72ee5688b88fb14910ba8ebb1a29e41d5f96d4`; and the protocol-hash-list hash is `057ed8464d78f4f027f0a62436bb8121dd8722d196d12d69db62779b6c596063`.

The two child argv lists, run IDs `003/004`, seeds, metadata, timeouts, roles, and predecessor path in `specification.json:44-105` match the commands in `contract.md:95-126`. The verifier's frozen config at `verify_null_calibrated_coverage.py:57-69` matches the generator plan.

## Risk list

### S0-1 — The audited execution plan still has no immutable trust root

The specification stores both the plan and the expected hashes (`specification.json:20-105`), but the specification is not itself a required protocol hash. The runner's required set is only runner, experiment schema, contract, and the first repository source it recognizes in each child argv (`runner.py:265-293`). The schema does not require `execution_plan` in the experiment's required fields (`schemas/experiment.schema.json:8`), and the runner silently falls back to an unplanned run when it is absent (`runner.py:149-154`). Inline `-c` commands are explicitly exempt from source discovery (`runner.py:246-248`, `:284-293`). The runner records whichever clean `HEAD` is current rather than an audited/allowed commit (`runner.py:86-90`, `:779-784`).

This is not merely theoretical. In a clean temporary export, a specification-only commit replaced an initially reviewed source-backed plan with a new inline `-c` plan and updated its own expected hashes. The unchanged runner accepted the replacement and recorded `completed_valid`; `specification.json` was absent from `_required_protocol_paths`, and no inline source was required.

The source boundary is also incomplete. The canonical wrapper invokes `crypto_autoresearcher.cli` (`contract.md:96-103`, `:117-124`), while the runner imports validation and serialization behavior from `records.py` (`runner.py:22`); neither `cli.py`, `records.py`, nor `schemas/run-manifest.schema.json` is required by `runner.py:265-293` or listed at `specification.json:22-43`.

**Failure mode:** a clean commit can redefine or remove the plan, alter its expected hashes, alter unpinned harness dependencies, or use an inline command while still satisfying the runner. The external v2 audit hash catches this only if a human independently enforces it at every transition. Therefore the claim that exact command/source provenance is harness-enforced (`specification.json:18`; `contract.md:128-131`; `implementation.md:48-51`) exceeds the mechanism.

**Required repair:** introduce a trust anchor outside the mutable specification that the launcher verifies: an immutable approval/decision record containing the execution-plan hash, complete protocol-file hash set, and allowed code-tree/commit transition. Make `execution_plan` schema-required for this protocol; forbid inline `-c`; pin `cli.py`, `records.py`, `run-manifest.schema.json`, the specification/approval record, and the interpreter/runtime boundary. Record the verified plan digest in every manifest.

### S0-2 — A forged predecessor manifest satisfies the run graph

Existing runs are schema-validated and checked for directory/experiment identity (`runner.py:334-369`). For a verifier predecessor, the runner checks only `completed_valid`, `result.valid=true`, recorded clean state, artifact existence, and agreement between the artifact and the manifest's recorded SHA-256 (`runner.py:372-416`). It never compares the predecessor manifest's command, seed, curve ID, parameters, timeout, commit, or protocol digest with the predecessor entry in the execution plan.

A synthetic predecessor was hand-written with status `completed_valid`, command `not the planned generator command`, seed `999` instead of planned seed `7`, zero resource use, and a self-consistent raw-result SHA. The planned verifier accepted it and completed valid. The post-verifier SHA check itself is sound (`runner.py:635-653`), but it authenticates the bytes, not how the bytes or predecessor manifest were produced.

**Failure mode:** a valid generator document can be produced outside the canonical launcher or outside budget, inserted with a forged low-resource manifest, and then independently verified. Arithmetic reconstruction would remain meaningful, but canonical execution, resource, and run-graph claims would be false.

**Required repair:** before verifier launch, compare the predecessor manifest exactly with its planned argv, seed, curve ID, parameters, timeout, approved protocol digest, and allowed commit. Add a hash-chained runner receipt or approval-ledger entry that cannot be replaced by a hand-written schema-valid manifest. Recompute all required artifact hashes and reject manifests lacking the complete runner-created artifact set.

### S1-1 — Wall, CPU, and memory enforcement covers the direct child, not the run process tree

On macOS, live RSS polling queries only the direct PID (`runner.py:450-465`); `wait4` returns as soon as that direct child exits (`runner.py:468-533`); and the resource limits are per process (`runner.py:426-435`). Normal child completion does not check for or terminate remaining process-group members.

In a synthetic run with a 0.2-second wall budget, 0.72 CPU-second budget, and 32 MiB memory budget, the direct child spawned a descendant that allocated 96 MiB and consumed about 0.8 CPU seconds, then immediately returned valid. The runner recorded `completed_valid` after 0.04596 seconds with 0.030186 CPU seconds and 15,400,960 bytes peak RSS; the over-budget descendant was still alive and finished later.

The frozen generator and verifier inspected here are single-process programs, so this counterexample does not by itself falsify their measured child use. It does falsify the general harness-enforcement claim and becomes reachable if the mutable-plan/source boundary changes.

**Required repair:** monitor the entire process group, aggregate descendant RSS and CPU, wait for group quiescence, and kill/reap leftovers on both timeout and normal parent exit. Include launcher JSON parsing, hashing, and artifact publication in the declared run resource model, or label the budget explicitly as direct-child execution only.

### S1-2 — Clean-tree and protocol hashes are only pre-launch snapshots

The runner samples Git state before launch (`runner.py:779-784`) and later writes that pre-launch value into the manifest (`runner.py:860-868`). It does not recheck Git state or protocol hashes after the child exits and before publishing the run (`runner.py:803-924`).

A synthetic child modified tracked `AGENTS.md`, returned exact JSON `valid=true`, and was recorded `completed_valid` with `code.dirty=false`, while the actual worktree was dirty after the run.

**Required repair:** after child termination and before manifest publication, recheck the tree and every protocol hash; invalidate on any change. Prefer execution from an immutable exported tree or read-only mount to remove the hash-to-exec and exec-to-publication race.

### S2-1 — Path escape defenses are strong for ordinary paths but do not identify hard-link aliases

Absolute paths, `..` traversal, symlink escapes, and duplicate symlink aliases were rejected as intended (`runner.py:217-243`, `:301-316`). A synthetic hard link to the same inode was accepted as a distinct protocol path because duplicate detection compares normalized strings and resolved `Path` objects, not file identity.

No current execution-plan entry uses an alias, so this is not a current-file mismatch. It is a remaining TOCTOU/alias hardening gap.

**Required repair:** reject duplicate `samefile`/device-inode identities, open protocol files without following links where supported, hash through retained file descriptors, and rehash after execution.

### S2-2 — “Wrapper peak RSS” and full-run budget wording is too broad

The manifest records child `wait4`/polling measurements (`runner.py:803-823`, `:880-883`). Wall timing ends before stdout JSON parsing, pretty serialization, artifact hashing, and manifest creation (`runner.py:812-846`), and parent CPU/RSS is not included. Thus `contract.md:42-45` and `specification.json:151` should say “wrapper-measured direct-child peak RSS” unless the accounting is expanded.

The reduced 2+2 output projects to roughly 19 MiB at 31+31 by row-count scaling and is comfortably below the verifier's 64 MiB input cap (`verify_null_calibrated_coverage.py:1461-1464`), so no canonical-size failure is established. This remains a model-labeling and enforcement-boundary issue.

## V1 finding recheck

| V1 finding | V2 result |
|---|---|
| S0-1 command/provenance | **PARTIAL / OPEN.** Exact current argv and listed hashes are correct, but S0-1 above leaves the plan, specification, allowed commit, and harness dependencies mutable. |
| S0-2 budgets/run graph | **PARTIAL / OPEN.** Direct-child count/timeout/memory/cumulative-CPU tests pass (`runner.py:690-825`; `tests/test_runner.py:170-381`), but forged predecessors and descendant processes bypass canonical provenance/resource semantics. |
| S1-1 positive control | **CLOSED.** Scalar progression failure makes `valid=false`, and `controls_passed=false` suppresses family promotion (`null_calibrated_coverage.py:745-754`, `:796-835`; verifier `:821-830`, `:872-915`). The synthetic nine-pass/controls-false aggregation promoted nothing. |
| S1-2 order dependence | **CLOSED for the primary metric.** Exact per-target `k` and uniform-order work are computed at `null_calibrated_coverage.py:259-287` and independently replayed at verifier `:308-340`; exact work drives the frontier (`null_calibrated_coverage.py:364-366`). Four complete per-target vectors are retained (`:289-349`). |
| S1-3 coordinate/offline cost | **CLOSED within the disclosed proxy model.** Binary-pow, RHS, square-map, rational-map multiplication/inversion charges are explicit (`null_calibrated_coverage.py:191-236`, `:367-388`) and independently replayed (`verify_null_calibrated_coverage.py:225-270`, `:426-448`). Reduced source-trace checks matched every formula. Hardware, additions/reductions, dictionary work, and full wrapper cost remain outside the model as disclosed. |
| S2-1 finite-null language/ranks | **SUBSTANTIALLY CLOSED.** Raw favorable/tied/null counts and denominator are retained (`null_calibrated_coverage.py:452-470`, `:506-534`), six-of-nine is explicitly exploratory (`contract.md:61-79`), and rank/tie mutations reject (`verify_null_calibrated_coverage.py:1270-1293`). |
| S2-2 repeated fields | **CLOSED.** The frozen schedule has nine distinct field primes and runtime rejection of repetition (`null_calibrated_coverage.py:662-680`; verifier `:723-742`, `:956-960`). |
| S2-3 semantic tests | **SUBSTANTIALLY CLOSED but incomplete at the harness boundary.** The full 24-test suite and 51 verifier mutations passed. Missing permanent regressions are the successful counterexamples in S0-1, S0-2, S1-1, S1-2, and the hard-link case. |

## Arithmetic and statistical controls that survived

- **Exact first hit:** enumeration over 90 abstract `(S,k)` cases matched `(S+1)/(k+1)` for `k>0` and `S` for `k=0`. Generator and verifier implementations agree (`null_calibrated_coverage.py:263-287`; verifier `:311-340`).
- **Sampled/exact gate:** the code gates each shuffled aggregate against the exact aggregate and gates aggregate shuffle variation at 25 percent (`null_calibrated_coverage.py:328-363`; verifier `:388-422`). A constructed two-target example with exact `[1,100]` and sampled `[100,1]` has aggregate error `0`, aggregate variation `1`, and target-level relative error `99x`. This does not bias promotion because the exact expectation is primary, but no per-target sampled stability may be claimed.
- **Ranks/ties:** endpoint direction and midrank ties are correct. With 31 nulls the finite denominator is 32; raw counts prevent threshold ambiguity (`null_calibrated_coverage.py:452-470`).
- **Six of nine:** at least six passes plus equality of represented size and seed sets is literal (`null_calibrated_coverage.py:591-627`; verifier `:680-720`). Five passes, six passes missing a seed, and controls-false synthetic cases did not promote.
- **Mandatory controls:** curve, positive, rho, order, field-distinctness, and global factor-base-seed reconstruction are binding (`null_calibrated_coverage.py:796-835`; verifier `:872-961`). Resource/command/linkage controls remain separate harness obligations and are the source of the blocking findings.
- **Verifier independence and strictness:** the verifier does not import v2 generator code and loads the prior independently written arithmetic verifier (`verify_null_calibrated_coverage.py:2-7`, `:95-106`). It recomputes all four frozen dependency hashes (`:48-92`), recursively exact-compares the complete document (`:118-135`, `:943-961`), and rejects duplicate keys and non-finite JSON (`:1002-1031`). Its own source is externally pinned by the current plan (`specification.json:27-30`).

## Frozen curve schedule

Independent generator/verifier reconstruction agreed exactly:

| Seed | Bits | p | q | Trace | j |
|---:|---:|---:|---:|---:|---:|
| 2473001 | 12 | 4051 | 4093 | -41 | 1684 |
| 2473001 | 14 | 15767 | 15881 | -113 | 1977 |
| 2473001 | 16 | 62743 | 62467 | 277 | 11147 |
| 2473004 | 12 | 4027 | 4093 | -65 | 1859 |
| 2473004 | 14 | 15739 | 15919 | -179 | 12667 |
| 2473004 | 16 | 62791 | 62627 | 165 | 29162 |
| 2473012 | 12 | 3863 | 3853 | 11 | 2959 |
| 2473012 | 14 | 15859 | 15761 | 99 | 8109 |
| 2473012 | 16 | 62903 | 62983 | -79 | 2584 |

These are nine deterministic curves over nine distinct fields but only eight distinct group orders (`q=4093` repeats). Current prose correctly claims distinct fields; avoid “nine independent group orders” or statistically independent curve draws.

## Claim-boundary review

The hypothesis and arithmetic result documents stay within finite-null toy additive geometry: rank, factor-base logarithms, relation independence, sparse linear algebra, descent, exponent fitting, faster-than-rho performance, and deployment are explicitly excluded (`hypothesis.json:17-23`; `contract.md:133-138`; generator `:851-864`; verifier `:926-998`). Rho is arithmetic scale only (`contract.md:29-31`, `:47`). No source claim turns a future pass into an ECDLP break.

The overclaims are infrastructural rather than cryptanalytic:

1. Replace “harness-enforced frozen execution plan” with “externally audited current plan, pending an immutable launcher trust anchor.”
2. Replace “clean-tree enforcement” with “pre-launch clean-tree snapshot” until post-run state and hashes are checked.
3. Replace “run memory/CPU/wall enforcement” with “direct-child enforcement” until process-tree and wrapper accounting are implemented.
4. Replace “predecessor run graph enforced” with “predecessor status and raw-byte SHA linkage enforced; predecessor plan provenance is not yet authenticated.”
5. Narrow `analysis.md:8` (“repairs those protocol defects”) to the arithmetic/control repairs; the provenance/resource defects above remain.

## Approval-only transition assessment

The intended approval diff can be manually reviewed safely only as an external ceremony: change exactly `status: review_required -> approved` and `approved_by: null -> <reviewer>`, preserve execution-plan hash `1649f4f0c5f3ffd718a8199b521085df65a87bb8de7de40faf77fd5a078fea4d`, preserve every hash in this audit, and record the resulting commit. That ceremony is not enforced by the current runner and does not cure forged predecessor or process-tree accounting. It is therefore insufficient for `GO` at this commit.

## Required controls before another GO review

1. Add an immutable approval/plan trust anchor and enforce the externally audited execution-plan digest and allowed commit/tree transitions.
2. Make `execution_plan` mandatory; forbid `-c`; pin `cli.py`, `records.py`, `run-manifest.schema.json`, specification/approval decision, and the Python runtime/environment boundary.
3. Bind predecessor manifests to the exact planned command, metadata, timeout, commit/tree digest, protocol digest, complete artifacts, and an unforgeable/hash-chained runner receipt.
4. Enforce wall, cumulative CPU, and memory over the complete process group; wait for no descendants; include or explicitly exclude wrapper postprocessing.
5. Recheck Git cleanliness and all protocol hashes after execution and before immutable publication; reject same-inode aliases.
6. Add permanent adversarial tests reproducing the clean plan replacement, forged predecessor, detached descendant, post-launch dirty tree, and hard-link alias cases.

## Next falsification tests

- The repaired launcher must reject a clean specification-only plan replacement even when all hashes inside that replacement are self-consistent.
- It must reject a hand-written `completed_valid` predecessor whose artifact SHA is correct but whose command, seed, parameters, commit, or receipt differs from plan.
- It must mark invalid a parent that returns valid while an over-budget descendant remains alive.
- It must mark invalid any run that changes a tracked protocol file after the pre-launch check, even if the child exits zero.
- It must reject symlink, hard-link, case, and normalized-path aliases of a pinned file.
- After these protocol repairs, rerun only the reduced suite and request a third independent pre-run audit. Do not execute 31+31 evidence before `GO`.

## Handoff: harden EXP-ECDLP-RECURSIVE-002 v2 canonical provenance

### Claim or task

Close the mutable-plan, forged-predecessor, process-tree resource, and post-launch cleanliness gaps without changing the repaired additive-geometry protocol.

### Status

NEGATIVE RESULT

### Assumptions

- This audit covers immutable commit `878acef6753fb6a4d7ed3fc8347bc453203d801c` only.
- Reduced and synthetic runs are correctness/falsification controls, not hypothesis evidence.
- Neither canonical 31+31 run has been launched.
- The current frozen generator and verifier are single-process under the inspected source boundary.

### Evidence so far

- All 24 repository tests, 51 verifier mutations, reduced exact reconstruction, nine-field schedule, first-hit formula, costs, ranks, and family aggregation survived.
- A clean plan replacement, forged predecessor, detached over-budget descendant, and post-launch tracked mutation were each accepted as valid by the current harness.
- Parent traversal, absolute paths, symlink escape, and symlink duplicate controls rejected; a hard-link alias did not.

### Failure modes

- Self-consistent plan/hash replacement can outrun the external audit.
- Noncanonical or out-of-budget generator artifacts can receive canonical-looking verifier linkage.
- Descendant work and postprocessing can escape resource accounting.
- Manifest clean state can disagree with the tree at publication.

### Next concrete action

Implement Required Controls 1-6, freeze new hashes in a versioned successor commit, run only reduced adversarial tests, and request a fresh independent pre-run audit.

### Artifact paths

- `/Volumes/Volume/autolab/research/prototypes/exp_ecdlp_recursive_002_pre_run_audit_v2.md`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-RECURSIVE-002/`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/src/crypto_autoresearcher/runner.py`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/tests/test_runner.py`

## Pre-run verdict

**REVISE — canonical execution remains prohibited.**

The finite-null toy additive-geometry design is now substantially sound: exact order work, mandatory controls, charged coordinate proxies, raw finite ranks, six-of-nine aggregation, distinct fields, and independent strict replay all survived. Approval is still unsafe because the audited plan is not rooted outside its mutable specification, predecessor provenance can be forged while preserving raw SHA linkage, and declared resource/clean-tree enforcement does not cover descendants or post-launch state. These are protocol blockers, not evidence against the mathematical hypothesis.
