# EXP-SGCP-EMBED-002 V18 Independent Pre-Run Red-Team Review

## Findings

### Blocking findings

None.

### Residual risks, severity ordered

1. **MEDIUM — the historical manifest test does not itself verify Git mode/type.**

   `tests/test_sgcp_embed_family.py:1320-1371` enumerates decoded worktree paths, checks only that each is a regular file, and then appends literal `100644 NUL blob NUL` metadata. A selected `100755` blob would evade that control. It also does not consume raw `git ls-tree -rz` pathname bytes.

   This does not block this exact review because the manifest expressly delegates mode/type/raw-path verification to the independent reviewer, and the independent 200-entry Git-tree recomputation below found every selected entry to be exactly `100644 blob`.

2. **LOW — the recorded “validated 20 records” receipt covers the generic record router, not every experiment JSON artifact.**

   Static reconstruction finds 51 JSON files under EXP-SGCP-EMBED-002, of which 20 match `iter_record_paths` routing. Thirty-one custom or historical JSON files—including `protocol-amendment-v18.json`, `review-surface-manifest-v18.json`, and development results—are outside that generic validator. The development log states the exact count and does not literally claim all JSON was schema-validated, but the receipt must not be generalized to the whole review surface.

3. **LOW — decoded output strings with non-NUL controls or non-ASCII characters remain admissible by the output grammar.**

   `_raw_output_path` rejects NUL, terminal forms, relative paths, `..`, and exact leading `//`, but not newline, DEL, or non-ASCII characters. This is not a contradiction: V18’s ASCII/control restriction applies to selected Git review paths, not verifier output paths, and canonical JSON escaping keeps the publication receipt structurally unambiguous. A future launch plan should nevertheless bind one canonical ASCII output spelling to avoid tooling and operator ambiguity.

4. **LOW — `handoff.md` contains multiple historical `## Handoff` blocks with obsolete next actions.**

   The current V18 block is first and unambiguous, and every historical block retains zero-authority language. Naive tooling that selects the last or every heading could still surface obsolete V7/V10/V11 actions. Future closeout should distinguish the current handoff from archived handoff history.

5. **INFORMATIONAL — source-level gates are governance controls, not a Python sandbox.**

   The producer CLI refuses both canonical and development modes, and public generation APIs are gated. Private helpers remain importable, and the verifier CLI is directly callable without consulting experiment status. Neither route creates launch authority or a canonical run, but a future runner must bind exact commands and prevent unplanned direct invocation.

### Overclaim corrections

- Treat the recorded 81-test focused pass, 20-record validation, index comparison, and 225-test discovery result as historical receipts only.
- Do not describe the manifest receipt as a content digest. It binds selected mode/type/path metadata; the exact Git tree binds blob bytes.
- Preserve the exact statement: zero generated V18 curve-family density rows and zero canonical runs, alongside 17 historical V1 development rows and one historical development run manifest.
- Do not promote `480/112/336/218/4218` to field operations, group operations, runtime, memory, or attack cost.
- This review does not establish relation generation, rank, linear algebra, target descent, rho improvement, an exponent, deployment relevance, or an ECDLP result.

### Required controls for any separate launch-plan design

- Bind one canonical ASCII decoded output path and document the raw-argv-to-Python-string boundary.
- Recompute review inventories directly from `git ls-tree -rz`; add synthetic `100755`, symlink, newline, DEL, and non-ASCII pathname falsification cases.
- State exactly which custom JSON structures are covered by generic schema validation and which require dedicated validation.
- Bind generator and verifier commands, immutable inputs, exact protocol hashes, external CPU/wall/RSS/disk/I/O limits, cache/storage/bandwidth accounting, and failure-to-`INCONCLUSIVE` semantics.
- Keep launch-plan design non-executing. Any later execution still requires a hash-complete plan, fresh review, coordinator approval, positive budgets, and an approval lock.

### Next falsification tests

These were not run during this review:

- Flip one selected blob to Git mode `100755`; the successor selector must reject it.
- Add a selected symlink or control-bearing raw Git pathname; selection must reject deterministically before hashing.
- Supply terminal `/` and `/.` through a real process boundary; confirm the decoded string is preserved and rejected before input work.
- Use an admitted string-valued `__fspath__` callback that creates the destination, and a callback that raises after a side effect; classify all effects as caller-created.
- Attempt direct verifier and generic-runner invocation while status remains `review_required`; the launch wrapper must refuse canonical attribution.
- Mutate `agents/coordinator.md` or one historical development artifact in a synthetic successor tree; the selected-entry receipt must change.
- For the mathematical hypothesis, the clean scoped counterexample remains a complete valid exact 168-row matrix in which all six family-cap pairs fail.

## Exact review receipt

- Requested checkout: `/tmp/sgcp-v18-review-c02d31e`
- Physical path: `/private/tmp/sgcp-v18-review-c02d31e`
- Commit: `c02d31eb67e4e24f0866ba0a045e72dbe74a3844`
- Sole parent: `72b14ad6ae539c027856de5584d46352837d680c`
- Tree: `ec44de9a448e6b81a32b4f2f54764b17f3a859ae`
- Parent tree: `04372302d92be1af78fe49573ce24b4f0a204a96`
- Subject: `Harden SGCP V18 CLI and review manifest`
- Commit date: `2026-07-24T05:06:12-07:00`
- Initial state: detached and clean
- Final state: detached and clean
- Parent-to-HEAD `git diff --check`: clean
- Diff: 14 files, 1,079 insertions, 337 deletions; five additions and nine modifications
- Mode changes: none
- Artifact created by this review: none

The diff is confined to the V18 protocol/source/test/governance repair:

- `contract.md`
- `development-test-log-v18.md`
- `handoff.md`
- `hypothesis.json`
- `protocol-amendment-v18.json`
- `review-surface-manifest-v18.json`
- `revision-response-v18.md`
- `source-self-review-v18.md`
- `specification.json`
- `src/sgcp_embed_family.py`
- `src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `ledger.json`
- `research_ledger.md`

No producer, verifier, test, validator, indexer, runner, or experiment was executed.

## Ten hashes

All ten SHA-256 values recorded in `development-test-log-v18.md` independently match the exact commit blobs.

| Artifact | Independently recomputed SHA-256 | Match |
|---|---|---|
| `src/sgcp_embed_family.py` | `f9dc78ca8ff3b8d41d1e99b62a5d82a09c180ef1953dbb7401171882209dcea8` | yes |
| `src/verify_sgcp_embed_family.py` | `4310f6d5eeacace558a79670c944c55961f89f0c1db4aaee4d8b20d361501199` | yes |
| `tests/test_sgcp_embed_family.py` | `f5360f3f1dc345c9e29fb69fc673c67208918b5c8288c31f74dbf7f4a769b01e` | yes |
| `hypothesis.json` | `aca55cd96f5d94116d4a8ba811937f66c5087e26a0ca3d0a9672258538c49b86` | yes |
| `specification.json` | `579a4bd0bc8d8af67592635b3407754c95bb4a9cf5bb0a93fe668d65391e08a8` | yes |
| `contract.md` | `b93084cf19634533210fd0c48fd7ea2f84f9b718b9320f5d390b363f403df2fe` | yes |
| `protocol-amendment-v18.json` | `3dafb3f249225f99583d9ce90b8630e93013d40a06dfa8bd8f6312cf77b483d5` | yes |
| `revision-response-v18.md` | `49a37f395b36c40440f59aeb7153df853e897182c7800e8d1c5b9694424d0ba9` | yes |
| `source-self-review-v18.md` | `20f62ef17789fb94446dd6b0d5a489f2db13ac601d88bb9ed4d03e4990b0ef32` | yes |
| `review-surface-manifest-v18.json` | `587fd50831976921101060d1cac2e2d249f193b63b77bdf1362d08e1261a5c08` | yes |

## Manifest recomputation

The manifest was independently reconstructed from raw `git ls-tree -rz --full-tree` records, without using the repository test implementation.

| Selection class | Entries |
|---|---:|
| Repository exact paths | 14 |
| `schemas/*.json`, depth one | 9 |
| `src/crypto_autoresearcher/*.py`, depth one | 5 |
| `tests/*.py`, depth one | 14 |
| Recursive static EXP-SGCP-EMBED-002 entries | 154 |
| Exact historical-development overrides | 4 |
| **Total** | **200** |

Recomputed receipt:

- Record encoding: `mode NUL type NUL raw-path-bytes NUL`
- Sort: ascending raw pathname bytes
- Encoded receipt length: `12,882` bytes
- Entry count: `200`
- SHA-256: `bbff5e614b7b813f21fc7aa6e9ab2590155aed4f37e9359838193449e0bcb227`
- Manifest match: yes
- Non-ASCII selected paths: `0`
- ASCII-control-bearing selected paths: `0`
- Entries not exactly `100644 blob`: `0`
- Missing exact normative paths: `0`
- Missing historical override paths: `0`
- Future excluded V18 review/closeout paths already present: `0`

All 200 selected blobs, totaling `2,554,072` bytes, were read from the exact tree. Independent recomputation of each Git blob SHA-1 object identifier produced zero mismatches.

The selector includes the previously omitted README, three role contracts, lifecycle and evidence documents, shared record definitions, all flat schemas/core/tests, both inherited SGCP control files, complete static EXP-SGCP-EMBED-002 records, and the four historical development artifacts. No omitted current authority-, route-, schema-, or evidence-bearing normative file was found.

## Adversarial CLI/callback analysis

### CLI coercion and terminal syntax

V18 removes `type=Path` from both producer and verifier `--output` arguments. `argparse` therefore returns the same Python-decoded exact `str`, preserving terminal `/` and `/.`.

Verifier `main` performs:

1. argument parsing;
2. `output_path(args.output)`;
3. input verification;
4. `write_json_exclusive(args.output, report)`.

Thus terminal forms reject before input verification or writer invocation. The same decoded string—not a preconstructed normalized `Path`—is passed into the writer.

The producer also retains `--output` as a string, but both canonical and development branches raise `PermissionError` before using it.

### Raw argv versus Python strings

The claim is correctly limited to Python-decoded strings. Raw argv bytes, shell processing, operating-system decoding, and Python’s argv decoding remain external. No raw-byte preservation claim was found.

Direct Python APIs remain a different ingress model: passing a preconstructed `Path` cannot preserve discarded terminal spelling. V18 does not claim otherwise.

### Writer admission

`write_json_exclusive` first calls `output_path`, serializes only after admission, and invokes the descriptor walker with the admitted normalized `Path`. The descriptor walker repeats grammar and root-containment checks before creating parents.

The original decoded CLI string reaches the writer unchanged. It is not preserved through every internal descriptor operation, nor does V18 claim that it is.

### `__fspath__` callbacks

`os.fspath` necessarily executes caller code before return-type validation. V18 now states this explicitly.

- A string-valued callback may create caller effects before successful admission.
- A byte-valued callback may create its own candidate before exact-type rejection.
- Callback exceptions and `BaseException` can preserve prior caller effects.
- The verifier-created no-destination claim begins after `os.fspath` returns and applies to inert rejected inputs.
- Same-process monkeypatching, callback mutation, and hostile caller behavior remain outside the restricted guarantee.

This is an honest scope, not a sandbox claim.

## Review-surface and historical evidence audit

### Historical receipts

The recorded results were not rerun.

Static source inspection independently confirms:

- focused unittest methods in `test_sgcp_embed_family.py`: `81`;
- repository unittest methods: `225`;
- module-level pytest-style functions outside unittest discovery: `27`.

The historical V18 log records:

- focused suite: 81 passed;
- generic record validation: 20 records;
- freshly generated index: byte-identical to `ledger.json`;
- unittest discovery: 224 passed and one preserved immutable-run-guard failure;
- 27 module-level pytest-style functions not collected.

Those statements are internally consistent, subject to the validator-scope and Git-mode-test limitations in Findings.

### Historical development evidence

Independent committed-data parsing establishes:

- smoke artifact: one V1 development row;
- V1 raw result: sixteen V1 development rows;
- total historical V1 rows: `17`;
- historical development run manifests: `1`;
- historical manifest status: `completed_valid_development`;
- canonical flag: `false`;
- historical verification rows: `16/16` recorded valid.

The historical run-manifest byte bindings also match:

- `raw-result.json`: `513,609` bytes, SHA-256 `7b06643bced6be6837e8a502d5b772b632bebc83ddc89440fe5ceb1a98bd7821`;
- `verification-v4.json`: SHA-256 `59a492747aa84eb83a2be81da42f81b71ac9caf419e96f242f9fe0939ac9b808`.

These are immutable, noncanonical, dirty-worktree V1 development receipts. They are not V18 evidence and do not establish current execution.

### Current artifacts

No V18-schema generated row artifact exists. There is no EXP-SGCP-EMBED-002 `runs/` entry, no V18 decision, no V18 approval provenance, no execution approval, and no launch-plan artifact.

## Bypass and authority audit

### Producer and generated-row routes

- `generated_curve` raises before generation.
- `build_legacy_row` raises before row construction.
- `build_density_row` admits only the exact frozen p=19, B=4 association.
- `build_development_document` raises.
- Producer `main` refuses canonical mode because status is `review_required` and `maximum_runs=0`.
- Producer `main` also refuses development mode because the V18 row budget is zero.

Private factor-base and frozen-control helpers remain importable. They do not constitute canonical authority and must not be treated as a process-security boundary.

### Verifier routing

- Current schema: V18 only.
- Legacy set: V1 through V17.
- V1–V17 inputs route directly to unsupported-legacy rejection without semantic row verification.
- Unknown and malformed schemas reject before protocol interpretation.
- Public direct legacy-row and density-row verification APIs return disabled/non-evidence reports.
- Path-based `verify_document` remains the sole evidence-bearing verifier API.

No schema alias or fallback route to V17 semantics was found.

### Generic runner

The only repository CLI launch route calls `run_experiment`. At the exact V18 state it rejects before launching because:

- status is neither `approved` nor `draft`;
- `approved_by` is null;
- no `execution_plan` exists;
- all active resource budgets are zero;
- `maximum_runs=0`;
- the official runs list is empty.

Even after status mutation, the runner separately requires positive wall, CPU, and memory budgets, a matching execution plan, an external approval lock, exact protocol hashes, and run-count availability.

### Exact authority gates

| Gate | Exact state |
|---|---|
| Specification status | `review_required` |
| `approved_by` | `null` |
| `execution_plan` | absent |
| Wall seconds per run | `0` |
| Total CPU hours | `0` |
| Maximum memory GiB | `0` |
| `maximum_runs` | `0` |
| Ledger runs | `[]` |
| Generated V18 density rows | `0` |
| Canonical runs | `0` |
| Launch-plan authorized | `false` |
| Execution authorized | `false` |
| Last coordinator decision | V17 `revise` |

The hypothesis’s proposed future `900` seconds and `4` GiB per role are explicitly proposed estimates, not active budgets.

## Mathematical and claim audit

### Parent-to-HEAD invariance

The producer delta changes only:

- protocol/schema labels from V17 to V18;
- refusal strings;
- family-gate version label;
- removal of CLI `Path` coercion.

The verifier delta changes only:

- V17-to-V18 labels and helper names;
- inclusion of V17 in the legacy schema set;
- CLI output coercion;
- output preflight ordering;
- passing the decoded string directly to the writer.

No curve-grid, curve-generation formula, predicate, representative compiler, factor base, graph construction, optimizer, cap schedule, objective ordering, threshold, family gate, reservation formula, success criterion, or falsification criterion changed.

### Independent arithmetic

A standalone reimplementation of the committed SHA-256 curve generation, curve filtering, point counting, Möbius nonce, and null-root hash formulas reproduced:

- prime candidates: `2 × (16 + 32 + 64 + 128) = 480`;
- accepted-curve draws: `12 + 49 + 4 + 15 + 11 + 8 + 3 + 10 = 112`;
- curve hashes: `3 × 112 = 336`;
- nonsingular draws: `109`;
- registered-curve point enumerations: `2 × 109 = 218`;
- predicate hashes: `4,218`.

These are provenance and predicate events, not cryptanalytic cost.

### Baseline and success criterion

The matched baseline is four hash-ranked x-fiber controls under the same constrained-label cap. That is suitable for the narrow toy coordinate-retention question. It is not Pollard rho, BSGS, index calculus, or an end-to-end ECDLP baseline.

The success criterion is meaningful only as a finite descriptive signal: one fixed coordinate-family/cap pair must pass across the exact 168-row, 672-cell matrix. Six family-cap pairs are examined, and the protocol reports all passing pairs. This does not create statistical, distributional, or asymptotic evidence.

### Rank and target descent

The construction still lacks:

- relation-generation probability and cost;
- factor-base logarithm acquisition;
- matrix dimensions, density, and rank;
- sparse linear algebra;
- individual logarithm or target descent;
- fixed-curve preprocessing crossover;
- matched rho/BSGS cost;
- a public final-layer edge yielding the private final support;
- cryptographic-scale memory and runtime.

The public label-to-formal source table is charged advice, not a decomposition algorithm. Outside frozen B4, the secondary four objective fields are deterministic replay checks rather than a structurally separate complete oracle.

### Memory and scaling

The memory model is honest at this stage: serialized object sizes and structural cells are not presented as peak RSS, allocator retention, cache traffic, memory bandwidth, disk, or I/O. Those costs remain future external-runner obligations.

Four bit sizes are nominally swept, but all are 5–8-bit toy groups with two seeds. No exponent or deployment mapping is permitted.

### Strongest valid claim

V18 is a no-run governance, CLI-ingress, and review-binding repair. A future successful matrix could establish only a toy, compiler-bound coordinate-structure signal. It could not establish an ECDLP attack.

## Final verdict

**GO for separate launch-plan design only**

V18 closes every precise V17 blocker on the exact reviewed commit and tree. The residual risks above must be carried into any separate design, especially Git-native mode/type testing, validator-scope labeling, canonical ASCII output binding, and the distinction between governance gates and process security.

This verdict does not authorize execution, budget widening, generated V18 rows, a canonical matrix, or any mathematical or cryptanalytic claim. It is one independent red-team input; the remaining fresh reviews and coordinator process still govern any next state transition.

## Handoff: EXP-SGCP-EMBED-002 V18 independent pre-run red-team review

### Claim or task

Determine whether exact V18 commit `c02d31eb67e4e24f0866ba0a045e72dbe74a3844` closes the V17 red-team blockers without changing mathematical semantics, widening budgets, or creating execution authority.

### Status

`OBSERVATION` — no blocking V18 pre-run readiness defect was found within the exact committed, toy, model-bound, read-only scope.

### Assumptions

- Review scope is exactly the commit, sole parent, and tree recorded above.
- Ordinary Git object-integrity semantics apply.
- Recorded tests and validation are historical receipts and were not rerun.
- Python-decoded strings are distinct from raw argv bytes.
- Arbitrary same-process callbacks and monkeypatching are not sandboxed.
- Structural work is not attack cost.
- No cryptographic-scale inference is permitted.

### Evidence so far

- Detached identity and cleanliness matched before and after.
- Parent-to-HEAD diff hygiene is clean.
- All ten V18 SHA-256 values match.
- The 200-entry NUL-delimited mode/type/path receipt reproduces exactly.
- Every selected entry is an ASCII, control-free `100644 blob`.
- All selected Git blob object identifiers independently reproduce.
- V17 blocker dispositions are statically closed.
- Historical evidence is exactly one smoke row plus sixteen V1 rows and one noncanonical development manifest.
- No V18 generated row, canonical run, execution plan, approval, or launch artifact exists.
- All authority and resource gates remain zero or false.
- Independent arithmetic reproduces `480/112/336/218/4218`.
- Mathematical, baseline, memory, scaling, rank, and target-descent limitations remain explicit.

### Failure modes

- The historical focused test does not itself read Git modes/types.
- Generic record validation covers only routed records, not every custom JSON artifact.
- Output-path controls other than NUL remain admissible unless a future plan binds a canonical ASCII spelling.
- Direct Python/private-helper invocation is not prevented by governance metadata alone.
- Historical handoff blocks can confuse naive heading-based tooling.
- A future plan may omit external resources, failed attempts, storage/advice, verifier cost, rank, linear algebra, or target descent.
- A toy matrix pass may be misrepresented as an attack or scaling result.

### Next concrete action

Prepare one separate, hash-complete, non-executing launch-plan design binding the exact reviewed commit/tree, canonical ASCII role arguments, immutable inputs, exact protocol hashes, generator/verifier separation, hard CPU/wall/RSS/disk/I/O limits, cache/storage/bandwidth accounting, publication and failure semantics, and continued zero execution authority; submit that design for fresh independent review and coordinator decision before changing any budget or status.

### Artifact paths

- Proposed, not written: `experiments/EXP-SGCP-EMBED-002/pre-run-red-team-review-v18.md`
- `experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v18.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v18.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v18.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v18.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v18.md`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/handoff.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `ledger.json`
- `research_ledger.md`

<oai-mem-citation>
<citation_entries>
MEMORY.md:790-791|note=[used only for prior gate and claim-discipline context]
</citation_entries>
<rollout_ids>
</rollout_ids>
</oai-mem-citation>
