# EXP-SGCP-EMBED-002 V18 Independent Pre-Run Theory Review

## Findings

### Blocking findings

None.

### Non-blocking findings

1. **LOW — The historical focused manifest control is not itself a Git-entry proof.**

   `tests/test_sgcp_embed_family.py:1320-1371` enumerates the working tree, checks that selected paths are regular files, and then synthesizes literal `100644\0blob\0` prefixes. It would not independently detect an executable Git mode or non-blob tree entry. This is not a blocker because the manifest requires reviewer-side `git ls-tree -rz --full-tree` verification, and this review independently confirmed all 200 selected entries are actual `100644 blob` entries and reproduced the exact receipt.

2. **INFORMATIONAL — Recorded validation and test results remain historical receipts.**

   The development log records 81 focused tests passing, 20 records validated, a byte-identical generated index, and 225 repository `unittest` methods with one preserved unrelated immutable-run-guard failure (`development-test-log-v18.md:37-126`). None was rerun. This review makes no fresh dynamic-test claim.

3. **THEORY RESIDUAL — All attack-bearing cryptanalytic obligations remain open.**

   V18 establishes neither relation generation nor factor-base logarithms, smoothness behavior, matrix rank, sparse linear algebra, individual-log descent, preprocessing crossover, rho improvement, scaling exponent, deployment relevance, or a prime-field ECDLP result. These are open obligations, not negative conclusions about ECDLP.

## Exact review receipt

- Requested checkout: `/tmp/sgcp-v18-review-c02d31e`
- Physical checkout: `/private/tmp/sgcp-v18-review-c02d31e`
- Commit: `c02d31eb67e4e24f0866ba0a045e72dbe74a3844`
- Sole parent: `72b14ad6ae539c027856de5584d46352837d680c`
- Tree: `ec44de9a448e6b81a32b4f2f54764b17f3a859ae`
- Parent tree: `04372302d92be1af78fe49573ce24b4f0a204a96`
- Subject: `Harden SGCP V18 CLI and review manifest`
- State before review: detached and clean
- State after review: detached and clean
- Symbolic branch: absent, confirming detached HEAD
- Worktree and index diffs before and after: empty
- Parent-to-HEAD `git diff --check`: clean
- Artifact created by this review: none

The parent-to-HEAD diff contains 14 paths: five additions and nine modifications, with no deletion, rename, type change, or executable-mode change. Every changed entry is mode `100644`.

The additions are the V18 amendment, response, self-review, development-test log, and review-surface manifest. The modifications are confined to the contract, handoff, hypothesis, specification, producer, verifier, focused test file, and two ledgers. The source deltas are version/routing text, CLI output-string preservation, verifier preflight ordering, and associated controls; no mathematical algorithm hunk was added.

Only committed Git/tree blobs and static source or documentation were inspected. No producer, verifier, test, validator, indexer, runner, or experiment was executed.

### Ten exact artifact hashes

All SHA-256 values in `development-test-log-v18.md:20-31` independently match their exact Git blobs.

| Artifact | Independently recomputed SHA-256 | Result |
|---|---|---|
| `src/sgcp_embed_family.py` | `f9dc78ca8ff3b8d41d1e99b62a5d82a09c180ef1953dbb7401171882209dcea8` | MATCH |
| `src/verify_sgcp_embed_family.py` | `4310f6d5eeacace558a79670c944c55961f89f0c1db4aaee4d8b20d361501199` | MATCH |
| `tests/test_sgcp_embed_family.py` | `f5360f3f1dc345c9e29fb69fc673c67208918b5c8288c31f74dbf7f4a769b01e` | MATCH |
| `hypothesis.json` | `aca55cd96f5d94116d4a8ba811937f66c5087e26a0ca3d0a9672258538c49b86` | MATCH |
| `specification.json` | `579a4bd0bc8d8af67592635b3407754c95bb4a9cf5bb0a93fe668d65391e08a8` | MATCH |
| `contract.md` | `b93084cf19634533210fd0c48fd7ea2f84f9b718b9320f5d390b363f403df2fe` | MATCH |
| `protocol-amendment-v18.json` | `3dafb3f249225f99583d9ce90b8630e93013d40a06dfa8bd8f6312cf77b483d5` | MATCH |
| `revision-response-v18.md` | `49a37f395b36c40440f59aeb7153df853e897182c7800e8d1c5b9694424d0ba9` | MATCH |
| `source-self-review-v18.md` | `20f62ef17789fb94446dd6b0d5a489f2db13ac601d88bb9ed4d03e4990b0ef32` | MATCH |
| `review-surface-manifest-v18.json` | `587fd50831976921101060d1cac2e2d249f193b63b77bdf1362d08e1261a5c08` | MATCH |

## Analysis of CLI/callback closure

V18 closes the V17 CLI-coercion blocker within its stated Python-decoded-string and controlled-POSIX model.

The producer and verifier now declare `--output` without `type=Path`:

- producer: `src/sgcp_embed_family.py:2105-2119`;
- verifier: `src/verify_sgcp_embed_family.py:7785-7790`.

The verifier then:

1. retains `args.output` as the decoded string;
2. calls `output_path(args.output)` before `verify_document`;
3. passes the same `args.output` string to `write_json_exclusive`.

See `src/verify_sgcp_embed_family.py:7793-7797`.

`_raw_output_path` receives the uncoerced value and rejects terminal `/` at lines 7081-7082 and terminal `/.` at lines 7083-7085. Thus `Path` construction cannot erase those spellings before classification. The preflight occurs before input verification, writer invocation, or output-parent creation.

The producer preserves the same decoded spelling but remains independently disabled: its `main` refuses both canonical and development family-row execution before using the output path (`src/sgcp_embed_family.py:2123-2131`).

### Restricted theorem candidate: V18 CLI terminal-form rejection

**Status:** `RESTRICTED THEOREM`.

**Model:** CPython-style `argparse` receiving decoded string arguments, the committed V18 verifier, an available development root, and controlled POSIX path semantics.

**Claim:** For a verifier CLI output argument whose decoded string ends in `/` or has terminal component `.`, `main` raises during output admission before calling `verify_document`, `write_json_exclusive`, or any output-parent creation path.

**Proof sketch:** `parse_args` performs no output `Path` coercion; `main` calls `output_path` first; `output_path` invokes `_raw_output_path`; the ordered terminal checks reject; subsequent verifier and writer statements are unreachable.

**Counterexample routes and limitations:**

- raw argv bytes, shell decoding, OS decoding, and Python argv decoding precede the model;
- alternate operating systems or path flavors are outside the controlled-POSIX claim;
- failure or hostile mutation of the development root may change the exception but does not create a valid publication route;
- hostile same-process monkeypatching is outside the model;
- the theorem concerns rejection ordering, not universal filesystem isolation.

### Callback-effect closure

V18 also closes the arbitrary-`__fspath__` wording blocker by narrowing the claim rather than pretending to sandbox caller code.

`_raw_output_path` necessarily calls `os.fspath` before it can inspect the result (`src/verify_sgcp_embed_family.py:7066-7074`). Arbitrary callback effects occurring during that call are expressly outside the verifier-created-no-destination guarantee. The guarantee begins only after `os.fspath` returns and applies to verifier-created effects for inert rejected inputs.

Static controls record both directions:

- a string-valued callback creates a caller marker and then returns an admissible destination;
- a byte-valued callback creates its own candidate and is then rejected because the return is not an exact `str`.

See `tests/test_sgcp_embed_family.py:4792-4808,5003-5035`. These controls delimit callback effects; they do not claim to prevent them.

## Cross-artifact consistency

### Version and routing

The producer, verifier, contract, specification, ledger, handoff, and manifest consistently identify V18.

The verifier’s legacy set contains the V1 development schema, V2 development schema, and candidate schemas V3 through V17 (`src/verify_sgcp_embed_family.py:30-47`). Only the V18 candidate schema is current.

After bounded parsing and source-shape admission, every recognized legacy schema reaches the explicit unsupported-legacy branch, produces no row reports, and states that no mathematical checks were executed (`src/verify_sgcp_embed_family.py:7010-7017`). Malformed legacy-shaped documents may fail earlier source bounds, but neither route reaches EC, graph, optimizer, or density-row mathematics.

### Historical versus current artifacts

The active V18 artifacts consistently state:

- zero generated V18 curve-family density rows;
- zero canonical runs;
- 17 historical V1 development rows;
- one historical development run manifest;
- `maximum_runs=0`.

The four exact historical paths are enumerated in `review-surface-manifest-v18.json:85-90`.

Static inspection establishes the 17-row total:

- `development/DEV-SGCP-EMBED-002-SMOKE/raw-result.json`: one row, `canonical:false`;
- `development/DEV-SGCP-EMBED-002-V1/raw-result.json`: sixteen rows, `canonical:false`;
- `development/DEV-SGCP-EMBED-002-V1/run-manifest.json`: one manifest, `canonical:false`, `status:"completed_valid_development"`, and `total_rows_consumed:17`.

The current V18 result schema string appears only in the producer and verifier source. No committed V18 result blob exists. `ledger.json:126-132` records `runs:[]`, `review_required`, version 18, and no `experiments/EXP-SGCP-EMBED-002/runs/` tree exists.

Active zero-artifact wording is properly qualified. Older appended handoff sections remain explicitly version-labelled historical records and do not override the leading V18 handoff.

### Normative surface

The V17 omissions are closed. The exact-path inventory now includes:

- `README.md`;
- all three files in `agents/`;
- both files in `docs/`;
- `templates/research-records.md`;
- the constitution, roadmap, build metadata, ledgers, inherited SGCP controls, schemas, harness source, tests, static EXP-SGCP-EMBED-002 records, and four historical development artifacts.

No normative file in the repository’s `agents`, `docs`, or `templates` directories remains outside the inventory.

## Manifest recomputation

The receipt was independently reconstructed from:

`git ls-tree -rz --full-tree ec44de9a448e6b81a32b4f2f54764b17f3a859ae`

The recomputation parsed raw NUL-delimited Git records, applied the manifest’s finite union of exact paths, one-level directory rules, static experiment rules, exclusions, and historical overrides, rejected selected non-ASCII/control-bearing paths, required mode `100644` and type `blob`, sorted by raw path bytes, and hashed:

`mode NUL type NUL raw-path NUL`

### Recomputed inventory

| Selection class | Entries |
|---|---:|
| Repository exact paths | 14 |
| Flat-directory entries | 28 |
| Static experiment entries | 154 |
| Exact historical-development entries | 4 |
| **Total** | **200** |

Additional receipts:

- complete tree entries inspected: 904;
- selected entries resolved through Git object lookup: 200;
- selected blobs resolved: 200;
- non-blob or missing selected objects: 0;
- first selected path: `AGENTS.md`;
- last selected path: `tests/test_tt_norm_rank.py`;
- recomputed SHA-256: `bbff5e614b7b813f21fc7aa6e9ab2590155aed4f37e9359838193449e0bcb227`;
- manifest SHA-256: `bbff5e614b7b813f21fc7aa6e9ab2590155aed4f37e9359838193449e0bcb227`;
- result: **MATCH**.

All five intentionally future V18 review/closeout outputs are absent from the reviewed tree.

### Restricted theorem: manifest receipt correctness

**Status:** `RESTRICTED THEOREM`.

**Claim:** Applying the manifest’s stated finite entry-selection and record-encoding rules to tree `ec44de9a448e6b81a32b4f2f54764b17f3a859ae` yields exactly 200 `100644 blob` entries and the stated SHA-256 receipt.

**Proof sketch:** Direct raw-byte enumeration, finite selection, metadata validation, raw-byte sorting, NUL-delimited record construction, and SHA-256 evaluation reproduce the manifest values.

**Limitations:** The receipt binds selected mode, type, and pathname metadata, not blob contents. Blob-byte binding is delegated to the independently verified exact Git tree under ordinary Git object-integrity assumptions. This is not a formal collision-freedom theorem for Git or SHA-256.

## Mathematical/cryptanalytic boundary

### Mathematical invariance

**Status:** `OBSERVATION` from static parent-to-HEAD comparison.

The producer delta changes only:

- V17-to-V18 schema and protocol labels;
- refusal and diagnostic text;
- family-gate version label;
- removal of CLI `Path` coercion.

The verifier delta changes only:

- V18 schema and receipt labels;
- addition of V17 to the legacy set;
- V17-to-V18 helper names and diagnostics;
- output CLI string preservation;
- the pre-verification `output_path` call;
- passing the same raw decoded string to the writer.

No curve generation, curve predicate, factor-base definition, representative compiler, ordering digest, order-ideal construction, conflict graph, optimizer objective, cap schedule, matched-null threshold, family gate arithmetic, source-table rule, structural accounting formula, or completed operation-vector formula changed.

The contract, hypothesis, and specification likewise retain:

- the generated 5–8-bit grid;
- seeds 101 and 211;
- `B={4,6,8}`;
- three coordinate families and four null replicates;
- 168 rows and 672 cap cells;
- the fixed five-field objective;
- the same persistence, matched-null, and collapse thresholds;
- frozen-B4 as the only structurally separate complete five-field oracle.

The declared `480/112/336/218/4218` provenance/predicate vector is unchanged, but it remains a historical/static receipt in this review, not a freshly recomputed execution result.

### Claim taxonomy

| Claim | Status | Boundary |
|---|---|---|
| CLI terminal-form rejection | `RESTRICTED THEOREM` | Decoded-string, committed-Python, controlled-POSIX model |
| Manifest receipt correctness | `RESTRICTED THEOREM` | Exact Git tree and finite selector |
| Parent-to-HEAD mathematical invariance | `OBSERVATION` | Static source/blob comparison |
| Coordinate-density hypothesis | `HYPOTHESIS`, `MODEL-BOUND`, `TOY-EVIDENCE`, `NOVELTY-UNVERIFIED` | Fixed compiler, order ideal, tiny generated curves |
| Generated-curve/predicate representativeness | `HEURISTIC` | No distributional theorem |
| Historical test outcomes | `OBSERVATION` | Recorded receipts only |
| Attack construction and scaling | `OPEN` | No end-to-end algorithm exists |

A complete valid matrix in which every fixed family-cap pair fails would weaken or reject only this predicate-plus-compiler hypothesis. It would not reject coordinate-specific structured embeddings generally.

Model-escape routes remain:

- another representative compiler;
- a formal quotient or different partial-operation model;
- source-recoverable non-tree operations;
- another coordinate representation;
- non-generic algebraic relation generation;
- Semaev/summation-polynomial or Weil-descent routes;
- trace, norm, isogeny, or endomorphism-derived structure.

Outside both restricted infrastructure theorems and the tested SGCP toy model are relation probability, factor-base smoothness, polynomial-system degree growth, matrix rank, sparse linear algebra, target descent, fixed-curve preprocessing economics, and comparison with rho, BSGS, or parallel collision search.

## Authorization boundary

The exact commit contains no launch-plan or execution authority.

Independent gates are:

- status `review_required` (`specification.json:7`);
- `approved_by:null`;
- no `execution_plan` field;
- wall-clock, CPU, memory, and `maximum_runs` all zero (`specification.json:211-215`);
- empty official run ledger (`ledger.json:126-132`);
- zero additional V18 development rows (`specification.json:112-120`);
- producer CLI refusal for both canonical and development family-row execution;
- no EXP-SGCP-EMBED-002 run directory;
- no launch-plan, execution-plan, approval-lock, runner-receipt, or canonical-run artifact;
- manifest authority fields all zero or false (`review-surface-manifest-v18.json:97-104`);
- research ledger instruction: obtain fresh reviews and do not design a launch plan or execute.

The generic runner independently rejects `review_required` because only approved locked experiments or explicit draft-development experiments are admissible (`src/crypto_autoresearcher/runner.py:1422-1442`). It also requires positive wall, CPU, and memory budgets and rejects an exhausted zero-run budget.

This theory verdict is one prerequisite only. It does not alter the current prohibition. Separate accounting and red-team review, coordinator action, and a later independently reviewed hash-complete launch plan remain necessary before design authority; execution would require still further approval and nonzero budgets.

## Final verdict

**GO for separate launch-plan design only**

No blocking theory defect was found in V18’s closure of the V17 CLI-coercion, normative-surface, historical/current wording, callback-effect, or Git-entry-encoding findings.

This verdict authorizes neither immediate launch-plan design under the current commit nor execution. It supports plan design only after the remaining required exact-commit reviews and coordinator gate succeed. It establishes no mathematical, asymptotic, cryptanalytic, deployment, or prime-field ECDLP result.

## Handoff: EXP-SGCP-EMBED-002 V18 independent pre-run theory review

### Claim or task

Independently determine whether exact commit `c02d31eb67e4e24f0866ba0a045e72dbe74a3844` closes V17’s specified blockers without changing the mathematical hypothesis or creating launch-plan or execution authority.

### Status

`OBSERVATION`

No blocking theory finding was identified within the exact-Git, decoded-string, controlled-POSIX, toy, and model-bound scope. Two infrastructure claims admit restricted-theorem statements as recorded above.

### Assumptions

- The reviewed state is exactly the stated commit, parent, and tree.
- Ordinary Git object-integrity semantics apply.
- Python receives decoded string CLI arguments.
- The development root exists and controlled POSIX path behavior applies.
- Arbitrary callback-created effects and hostile same-process mutation are outside the no-destination theorem.
- Recorded tests and validation outcomes are historical and were not rerun.
- No cryptographic-scale or ECDLP inference is drawn from the toy model.

### Evidence so far

- Detached cleanliness and exact object identity were confirmed before and after review.
- Parent-to-HEAD diff hygiene is clean and mathematically invariant.
- All ten V18 blob hashes match.
- The 200-entry NUL-delimited mode/type/path receipt reproduces exactly.
- Every selected Git entry is a resolvable `100644 blob`.
- All named normative files and four historical-development artifacts are included.
- Verifier CLI terminal forms reach raw admission before `Path` coercion.
- Callback effects are correctly scoped outside verifier-created effects.
- V1–V17 route to legacy rejection without mathematical row verification.
- There are zero generated V18 curve-family density result rows and zero canonical runs.
- Seventeen historical V1 rows and one noncanonical historical development run manifest remain disclosed.
- `maximum_runs=0`, no execution plan exists, and launch-plan design and execution remain unauthorized.
- Mathematical and cryptanalytic obligations remain explicitly open.

### Failure modes

- Confusing decoded CLI strings with raw argv-byte preservation.
- Extending the path theorem to other operating systems or hostile same-process mutation.
- Treating the metadata receipt as independent blob-content attestation.
- Treating historical test receipts as fresh execution evidence.
- Treating zero V18/canonical artifacts as zero historical development evidence.
- Promoting toy structured-support evidence into relation generation, rank, descent, asymptotic, rho, deployment, or ECDLP claims.
- Treating this single theory review as coordinator authorization.

### Next concrete action

Obtain fresh independent read-only accounting and red-team reviews of this exact commit and the same 200-entry receipt; only after both issue scoped GO and the coordinator acts may a separate hash-complete launch-plan design begin.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/pre-run-theory-review-v18.md` — proposed preservation path; not created by this review
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v18.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v18.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v18.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v18.md`
- `experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v18.json`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/handoff.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `ledger.json`
- `research_ledger.md`
