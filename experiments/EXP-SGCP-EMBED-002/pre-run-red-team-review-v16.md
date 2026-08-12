# Pre-Run Red-Team Review — SGCP V16

## Verdict

**Outcome: `REVISE before launch-plan design`**

V16 has no containment escape, accounting defect, mathematical change, budget widening, or execution route. It does, however, repeat the kind of exact-path overclaim it was intended to close: the committed lexical-policy control claims coverage of every admitted and rejected spelling while omitting trailing-separator, relative-path, custom `os.PathLike`, and four-or-more-leading-separator cases.

No execution is authorized or recommended.

## Severity-ordered risk list

### Critical

**No Critical finding.**

### High

**No High finding.**

### Medium

1. **MEDIUM — Claim/control mismatch: the “complete” lexical path table is incomplete, and trailing separators expose an unclassified normalization rule.**

   The active handoff says one table covers “every admitted and rejected lexical spelling” and checks every admitted spelling after publication (`experiments/EXP-SGCP-EMBED-002/handoff.md:40-42`). The self-review repeats “Every admitted spelling” (`experiments/EXP-SGCP-EMBED-002/source-self-review-v16.md:38-46`), while the amendment calls the table an exact policy over its listed cases (`experiments/EXP-SGCP-EMBED-002/protocol-amendment-v16.json:10-12`).

   The implementation converts the caller’s raw spelling to `Path` before checking it (`experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7064-7073`; standalone parser at `tests/test_sgcp_embed_family.py:73-87`). That transformation erases trailing separators:

   ```text
   raw:
   /private/tmp/.../development/trailing.json/

   pathlib parts:
   (..., "development", "trailing.json")

   abspath:
   /private/tmp/.../development/trailing.json
   ```

   Therefore the writer, receipt path, production status, standalone status, and descriptor walker treat the raw trailing-slash spelling as the regular-file destination. Under direct POSIX pathname semantics, a trailing slash requires the terminal component to be a directory; the V16 API silently changes that semantic before admission.

   Relative paths are also unclassified: `abspath()` at verifier line 7073 binds admission to the process CWD. From repository root,

   ```text
   experiments/EXP-SGCP-EMBED-002/development/relative.json
   ```

   becomes an admitted in-root path; from another CWD the same raw spelling can reject. The contract does not define this CWD-dependent admission rule.

   The committed test table contains only absolute, dot, internal-double, exactly-three-leading, and one combined alias (`tests/test_sgcp_embed_family.py:4650-4660`). Its rejected table covers exact `//`, `..`, root, and outside (`tests/test_sgcp_embed_family.py:4701-4724`). It omits:

   - trailing `/` and trailing `/.`;
   - repository-relative and other relative spellings;
   - custom `os.PathLike` objects;
   - four or more leading separators, despite claiming “three or more”;
   - empty and null-byte spellings as explicit API-contract cases.

   This is **not an outside-root implementation escape**: normalized lexical containment and descriptor traversal still hold. It is a blocking exact-contract defect because V16’s stated purpose is to close the path-policy claim/control mismatch.

   Required correction: either reject trailing separators and all relative inputs from the raw `os.fspath()` string before `Path` normalization, or explicitly admit and document them as aliases, including the CWD rule. Replace “every spelling” with “the enumerated spelling classes” unless the control becomes exhaustive over the defined input grammar.

### Low

2. **LOW — Governance binding gap: the nine-file hash table is not a complete evidence or gate manifest.**

   All nine values are correct, but the table at `experiments/EXP-SGCP-EMBED-002/development-test-log-v16.md:17-31` omits:

   - `development-test-log-v16.md` itself;
   - `handoff.md`;
   - `ledger.json`;
   - `research_ledger.md`;
   - `AGENTS.md`;
   - runner and execution-approval schema code;
   - the V15 reviews, provenance, and decision;
   - the exact commit, parent, and tree identifiers.

   This limitation was already identified in the V15 accounting review (`experiments/EXP-SGCP-EMBED-002/pre-run-accounting-review-v15.md:43`). The V16 table accurately calls itself a list of the “exact files tested,” so it is not a false hash result. The Git commit and tree currently bind the omitted bytes.

   The related version-consistency test checks the amendment, specification, repository ledger, producer, verifier, and contract title (`tests/test_sgcp_embed_family.py:1228-1259`), but does not assert the active handoff, research-ledger wording, revision-response action, or test-log action. Those current bytes are statically consistent, so there is no stale-state defect at this commit.

   Required correction: use the exact commit/tree as the review root and add a non-self-referential manifest covering all governance, evidence, runner, schema, and approval-gate files before any hash-complete plan review.

**No additional Medium or Low finding.**

## Finding classification

| Category | Result |
|---|---|
| Implementation escape | None found |
| Claim/control mismatch | Medium: incomplete “every spelling” path-policy claim |
| Governance defect | Low: incomplete nine-file binding and partial current-state assertion |
| Disclosed residual limitation | Present and accurately bounded; not treated as a new defect |

## Exact commit identity and read-only receipt

- Requested checkout: `/tmp/sgcp-v16-review-d8ea562`
- Physical Git top level: `/private/tmp/sgcp-v16-review-d8ea562`
- HEAD: `d8ea562f1890ef07fd48b2bfeef41289599575e9`
- Parent: `d0a8ab5ad9f9385276ff061a520a0a07844f7bc5`
- Tree: `5e015c30df3aaae68aa9d6d830fea8c6221280c1`
- Subject: `Harden SGCP V16 POSIX path policy`
- Checkout state before and after review: detached and clean, `## HEAD (no branch)`
- `git diff --check` from parent to HEAD: clean

No producer, verifier, experiment, test, validator, indexer, or runner was executed. No file or artifact was created or modified. Path behavior was checked only with standalone Python standard-library semantics, without importing repository code.

## Parent-to-HEAD audit

The parent-to-HEAD diff changes 13 files:

- `contract.md`
- `development-test-log-v16.md`
- `handoff.md`
- `hypothesis.json`
- `protocol-amendment-v16.json`
- `revision-response-v16.md`
- `source-self-review-v16.md`
- `specification.json`
- producer
- verifier
- `ledger.json`
- `research_ledger.md`
- focused tests

The producer delta is protocol/version and gate wording. The verifier delta adds V15 to legacy routing, relabels V16, and implements the `//` anchor checks in public and descriptor admission. No curve grid, curve-generation rule, predicate, representative compiler, ordering, graph construction, optimizer, cap schedule, objective, threshold, success gate, or negative classification changed.

## Nine-hash verification

All nine logged SHA-256 values independently match the exact committed files:

| Artifact | Logged and observed SHA-256 | Result |
|---|---|---|
| `src/sgcp_embed_family.py` | `7af442bb69e06b2e36453353e100bb103086c8f791ce8a5434e1ffe54afa93d9` | MATCH |
| `src/verify_sgcp_embed_family.py` | `40eb3d503122ece701841004207f7f60311f5e0992baa0d450dd8fdd4cf5ae9f` | MATCH |
| `tests/test_sgcp_embed_family.py` | `0e4a368bd9a1be2634d94a98c582a07ae2a9416cfae5f214c132e4ac09b67383` | MATCH |
| `hypothesis.json` | `9a7600ce7bcbd02cfdf08be228bd498c07f94ea18239ba1926804171bcbe30d5` | MATCH |
| `specification.json` | `d298e18078a632d6b387d98d7057138fdbed0bb6ffbdbd1dca1c3d986a81cffa` | MATCH |
| `contract.md` | `4526ebcbb62b60d2a01718e185ab891b77a8702e37f74b3f4fb9116b0b9ecc33` | MATCH |
| `protocol-amendment-v16.json` | `30c63bc705a9bbf48c0a0d1a3c980eba8f54490bddf78bb8808b218f0d83bf3a` | MATCH |
| `revision-response-v16.md` | `34e4376ff11646e87620d9e75cbe6c90b1f0137d9d5d4267a7e99c330fb2bf73` | MATCH |
| `source-self-review-v16.md` | `d26932f93971bb03ea21cb31c2dd2541a449eda7e6b8f7197650269d739f7497` | MATCH |

The three V15 review hashes also match `independent-review-provenance-v15.json:16-37`:

- Theory: `ade02d877d3aab98c292cadd7e626382bf69523c5df44ca4afe363b58c54dc60`
- Accounting: `03c63432516b1734bc8365f9ab8155decf8a2483f09706428f5d92f630b529a6`
- Red team: `6b8fb1e1fffb2896d645e12f58ad8b820fd3b9827cedbb251176f4b7dc28e2ab`

All three V15 reviews issued `REVISE`; `decision-v15.json:11-19` accurately records their findings and retained zero authority.

## Counterexamples attempted

| Surface | Static result | Classification |
|---|---|---|
| Exact leading `//` | Preserved as anchor `//` and rejected before normalization | Control held |
| Leading `///` | Collapses to ordinary `/`, then containment applies | Control held |
| Leading `////` | Also collapses to `/`; implementation matches claim, but committed test covers only `///` | Coverage gap |
| Internal `//` | Normalized to one component path | Control held |
| `./` component | Normalized as alias | Control held |
| Explicit `..` | Remains in `Path.parts` and rejects before `abspath` | Control held |
| Development root | Rejects because no destination-relative parts remain | Control held |
| Ordinary outside absolute path | Fails lexical `relative_to(root)` | Control held |
| Trailing `/` after filename | Erased before admission and treated as the regular file | Unclassified counterexample |
| Relative in-root spelling | Admission depends on process CWD | Unclassified counterexample |
| Custom `os.PathLike` | Accepted by API through `os.fspath`, but absent from the control table | Required control |
| Symlinked output parent | Descriptor traversal uses `O_DIRECTORY|O_NOFOLLOW`; committed control exists at `tests/test_sgcp_embed_family.py:4575-4578` | Control held statically |
| Existing destination/receipt | Both names are preflighted and publication is no-replace (`verify_sgcp_embed_family.py:7371-7382`, `7680-7696`) | Control held statically |
| Same-destination race | Receipt binds the winning random identifier; historical control exists at `tests/test_sgcp_embed_family.py:4876` | Control held within disclosed boundary |
| Hard-link branch | Same-directory hard-link and cleanup-warning controls exist; mounted-filesystem support is not claimed (`tests/test_sgcp_embed_family.py:5142-5193`) | Disclosed residual |
| Standalone parser | Uses its own lexical and canonical receipt parsing, not production status/canonicalization helpers (`tests/test_sgcp_embed_family.py:73-195`) | Independence held |
| Standalone filesystem race | Uses sequential path reads and does not provide descriptor traversal | Accurately disclosed |
| V1–V15 relabeling | Returns no row reports and no mathematical interpretation (`verify_sgcp_embed_family.py:7008-7015`) | Control held |
| Manual private-helper assembly | Possible only through same-process introspection/manual state assembly | Explicitly out of scope at `contract.md:187-200` |
| Direct producer CLI | Canonical and development paths both refuse (`sgcp_embed_family.py:2123-2131`) | Gate held |
| Generic repository runner | Rejects `review_required`, then zero positive budgets and `maximum_runs=0` | Gate held |

## Test and record-scope audit

The current source contains:

- 225 `unittest.TestCase` test methods;
- 81 methods in `tests/test_sgcp_embed_family.py`;
- 27 module-level pytest-style functions:
  - 16 in `tests/test_outer_translator.py`;
  - 11 in `tests/test_outer_translator_floor.py`.

This agrees with the scope disclosure at `development-test-log-v16.md:89-112`. The broad recorded command failed only on the disclosed immutable pre-existing run guard; it is not described as an all-framework pass.

Static record selection is exactly 18 records:

- `research-question.json`
- `hypothesis.json`
- `specification.json`
- decisions V1–V15

The recorded validator and index outcomes remain historical evidence and were not rerun.

Assertion quality:

- The legacy-routing assertion checks invalidity, zero rows, and absence of graph checks (`tests/test_sgcp_embed_family.py:3807-3824`); source routing independently confirms no row semantics.
- Accounting suppression/overcharge tests require invalidity and exact mismatch diagnostics (`tests/test_sgcp_embed_family.py:3347-3424`).
- The path test meaningfully exercises each listed case, but can pass while leaving the omitted spelling classes untested.
- The current-state test can pass without checking the handoff and research-ledger prose; current prose is nevertheless consistent under static inspection.

## Accounting audit

No suppression or overcharge route was found in the committed verifier under the disclosed non-hostile process model.

- Charges require exact positive integers (`verify_sgcp_embed_family.py:563-573`).
- Completed graph and expansion work is equality-checked against reconstructed dimensions (`verify_sgcp_embed_family.py:608-628`).
- Completed provenance and predicate counts are derived from verified transcripts (`verify_sgcp_embed_family.py:640-677`).
- Suppression and one-unit overcharge controls require invalidity (`tests/test_sgcp_embed_family.py:3347-3503`).
- The committed completed vector is statically consistent with those formulas and test constants:
  - 480 prime candidates
  - 112 draws
  - 336 curve hashes
  - 218 registered-curve point enumerations
  - 4,218 predicate hashes

This vector is prospective completed-transcript accounting, not evidence from a V16 canonical run. It is not a field-operation count, group-operation count, CPU measurement, peak-memory measurement, or end-to-end attack cost. The specification states those exclusions at `specification.json:101-107`.

Memory, parser/allocator retention, disk, I/O, cache traffic, bandwidth, and external artifact-store costs remain unmeasured. That boundary is honest.

## Zero-authority audit

Zero authority holds independently:

- Experiment status is `review_required` (`specification.json:5-8`).
- Wall, CPU, memory, and run budgets are all zero (`specification.json:208-212`).
- `approved_by` is null (`specification.json:367-368`).
- The amendment says `launch_plan_authorized: false` (`protocol-amendment-v16.json:37-45`).
- Repository ledger records `runs: []`, `review_required`, V16 (`ledger.json:126-132`).
- The generic runner accepts only approved locked experiments or explicit draft development runs; `review_required` rejects before launch (`src/crypto_autoresearcher/runner.py:1423-1442`).
- Zero wall/CPU/memory budgets independently fail the runner’s positive-budget checks (`runner.py:1457-1471`).
- `maximum_runs=0` independently rejects at `runner.py:1538-1542`.
- Public generated-curve and legacy-row construction raise (`sgcp_embed_family.py:404-410`, `1311-1324`).
- Density-row construction admits only the exact frozen p=19, B=4 control (`sgcp_embed_family.py:1463-1506`).
- Both canonical and development producer CLI routes refuse (`sgcp_embed_family.py:2123-2131`).
- No V16 curve-family density row, canonical matrix, run directory, execution plan, approval lock, runner receipt, or launch-plan artifact exists.

Only the repository Coordinator may change official status (`AGENTS.md:7-11`), and execution requires prior controls, budgets, and artifacts (`AGENTS.md:15-24`, `48-56`).

## Claim and baseline boundaries

The mathematical framing is appropriately narrow:

- Prospective grid: generated 5–8-bit curves, two seeds, B in `{4,6,8}`, 168 rows and 672 cap cells (`specification.json:10-24`).
- Four tiny sizes do not support an exponent fit.
- Pollard rho, parallel van Oorschot–Wiener, and BSGS remain the proper generic baselines, but V16 has no relation generator, rank computation, factor-base logarithms, target descent, preprocessing crossover, or complete DLP cost to compare against them.
- No Semaev/Gröbner/index-calculus comparison is meaningful without a relation system, matrix, and descent.
- Success would be only a toy coordinate-structure signal (`contract.md:578-585`).
- The contract explicitly excludes rank, descent, rho improvement, deployment relevance, and prime-field ECDLP results (`contract.md:626-631`).
- Invalid, incomplete, or resource-exhausted evidence remains `INCONCLUSIVE`, not mathematical falsification (`specification.json:214-238`).

No wording was found that turns V16 into an ECDLP attack, asymptotic improvement, or deployment claim.

## Controls that held

- Exact V16 identity, parent, tree, detached state, and clean worktree.
- All nine V16 logged hashes.
- All three V15 review hashes and provenance.
- V15 review/decision preservation and V16 current-state wording.
- V1–V15 rejection before row semantics.
- Exact `//` rejection and three/four-leading host behavior.
- Dot/internal-separator aliasing and explicit parent rejection.
- Lexical root/outside containment.
- Descriptor-relative no-follow parent traversal.
- No-overwrite data and receipt publication.
- Attempt-bound publication identifiers and raw-alias attribution for the enumerated aliases.
- Standalone receipt-parser implementation independence.
- Completed accounting equality checks and suppression/overcharge invalidation.
- Correct 18-record inventory and 225/81/27 test-scope counts.
- Zero budgets, null approval, empty run ledger, and runner refusal.
- Producer construction and CLI gates.
- No mathematical or success-gate change.
- Honest toy, memory, baseline, rank, descent, and ECDLP boundaries.

## Disclosed residual risks

The following are accurately disclosed and are not new V16 defects:

- hostile same-process monkeypatching or private-helper assembly;
- unauthenticated hostile same-user filesystem mutation;
- sequential, non-pair-atomic payload and receipt snapshots;
- `BaseException`, process death, power loss, or memory exhaustion after commit;
- lack of cross-platform path-semantics guarantees;
- standalone parser exclusion from descriptor-race safety;
- hard-link support tested only on a compatible temporary filesystem;
- lack of proof that every durability syscall succeeded;
- unmeasured CPU, RSS, allocator, storage, I/O, cache, and bandwidth costs;
- diagnostic source hash rather than executed-code attestation.

These boundaries are stated at `protocol-amendment-v16.json:26-35`, `source-self-review-v16.md:68-83`, and `contract.md:187-200`.

## Required controls and next falsification tests

Before another exact-commit review:

1. Define raw input grammar before `Path` normalization: string/Path/`os.PathLike`, absolute versus relative, empty, null-byte, trailing separator, trailing `/.`, exact `//`, and arbitrary 3+ leading separators.
2. Decide explicitly whether trailing separators and relative paths reject or normalize. If relative paths are admitted, bind the required CWD.
3. Extend the same table through public admission, receipt path, production status, standalone status, writer, and descriptor walker.
4. Publish through a trailing-separator alias if admitted and require exact receipt attribution; if rejected, require rejection before directory creation.
5. Add at least `////`, relative in-root, relative escape, and a custom `os.PathLike` implementation.
6. Replace universal “every spelling” wording with the finite enumerated grammar actually tested.
7. Extend current-state consistency checks to the active handoff, research ledger, revision-response action, and test-log action.
8. Bind the complete review and governance surface through the exact Git tree or a separate non-self-referential manifest.
9. Re-freeze affected hashes and obtain fresh read-only exact-commit theory, accounting, and red-team reviews.

Do not design a launch plan until that revision receives the required reviews. Do not authorize execution.

## Handoff: EXP-SGCP-EMBED-002 V16 adversarial review

### Claim or task

Falsify the exact-commit V16 path-policy, routing, accounting, governance, claim-boundary, and zero-authority repair through read-only inspection.

### Status

`OBSERVATION` — `REVISE before launch-plan design`.

### Assumptions

- Controlled current macOS/POSIX and Python `pathlib` semantics.
- No hostile same-user filesystem mutation or hostile same-process monkeypatching.
- Historical test, validator, index, and timing results were inspected but not rerun.
- Git commit and tree identity bind all current bytes, including files omitted from the nine-file table.
- No mathematical or cryptographic-scale inference is drawn from prospective toy rows.

### Evidence so far

- Exact HEAD, parent, tree, detached state, and clean status were verified.
- All nine V16 hashes and all three V15 review-provenance hashes match.
- No implementation containment escape, accounting defect, mathematical change, budget widening, or run route was found.
- Trailing-separator and CWD-relative spellings falsify the claim that the committed lexical table covers every admitted and rejected spelling.
- V1–V15 route to rejection without row semantics.
- The 18-record and 225/81/27 test inventories reconcile statically.
- All canonical authority remains zero.
- Rank, descent, rho, scaling, memory, and ECDLP boundaries remain explicit.

### Failure modes

- Treating a finite path table as exhaustive over raw POSIX and `os.PathLike` spellings.
- Treating `Path` normalization as preserving terminal-slash POSIX semantics.
- Allowing relative admission to depend on an unstated process CWD.
- Treating the nine-file table as a complete governance or launch manifest.
- Treating historical test receipts as tests rerun during this review.
- Treating the structural counter vector as end-to-end cryptanalytic cost.
- Treating any future toy support signal as relation generation, rank, descent, or an ECDLP improvement.

### Next concrete action

Prepare one no-run V17 that explicitly classifies trailing-separator, relative, arbitrary-leading-separator, and custom-`os.PathLike` inputs across every path entry; narrows universal wording; extends governance binding; preserves all mathematical bytes and zero budgets; then request fresh exact-commit review before any launch-plan design.

### Artifact paths

- `pre-run-red-team-review-v16.md` — this preservation-ready review; not written during the read-only audit
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v16.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v16.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v16.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v16.md`
- `experiments/EXP-SGCP-EMBED-002/handoff.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/pre-run-theory-review-v15.md`
- `experiments/EXP-SGCP-EMBED-002/pre-run-accounting-review-v15.md`
- `experiments/EXP-SGCP-EMBED-002/pre-run-red-team-review-v15.md`
- `experiments/EXP-SGCP-EMBED-002/independent-review-provenance-v15.json`
- `experiments/EXP-SGCP-EMBED-002/decision-v15.json`
- `ledger.json`
- `research_ledger.md`
- `src/crypto_autoresearcher/runner.py`
- `AGENTS.md`
