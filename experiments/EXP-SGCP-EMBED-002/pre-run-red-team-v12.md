# Independent Red Team Review — EXP-SGCP-EMBED-002 V12

Reviewed commit `9c170f70d6f4b7aafc20b5adfe70f22a702b5d8b` with required parent `0d5d541e344818fa84ec18279ced3c2b19324423`.

The worktree is detached and clean: `git status --porcelain=v1` and `git branch --show-current` both produced no entries. I inspected committed bytes only. I did not execute the producer, verifier, tests, or experiments.

## Findings

### 1. Medium — Publication can create the final destination and still return failure

Type: exploitable static defect / publication-state ambiguity.

The writer publishes the destination before its final directory `fsync`:

- [`verify_sgcp_embed_family.py:7203`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7203) marks publication complete.
- [`verify_sgcp_embed_family.py:7205`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7205) then performs the directory `fsync`.
- If that fails, the exception handler performs another unguarded `fsync` at [`verify_sgcp_embed_family.py:7214`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7214), potentially masking the original error. The destination remains present.

The hard-link path has a second variant: `os.link` may create the destination and the following temporary-name `unlink` may fail at [`verify_sgcp_embed_family.py:7105`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7105)-[`7112`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7112). Because `_publish_no_replace` then raises before `published=True`, cleanup removes only the temporary name if possible, not the already linked destination.

This does not overwrite an existing destination, but it creates an ambiguous terminal state: an apparently complete final artifact can exist after an unsuccessful call, cannot be retried under the exclusive-name policy, and cannot later carry independently demonstrable evidence that the writer returned successfully. That matters because the acceptance rule depends on “successful writer return” in [`contract.md:227`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/contract.md:227)-[`229`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/contract.md:229).

Before launch-plan design, publication needs an explicit recoverable/terminal protocol: for example, a separately durable completion receipt or a defined quarantine rule for every destination that appears before a failed return. Tests should inject post-publish directory-fsync failure and hard-link-success/unlink-failure.

### 2. Medium — The claimed real exFAT observation is not preserved as reviewable evidence

Type: documentation/evidence defect.

The committed documents assert that the actual target volume returned `ENOTSUP` for both hard-link and `RENAME_EXCL` publication:

- [`revision-response-v12.md:23`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/revision-response-v12.md:23)-[`26`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/revision-response-v12.md:26)
- [`development-test-log-v12.md:67`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/development-test-log-v12.md:67)-[`70`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/development-test-log-v12.md:70)

No raw command, stdout/stderr, filesystem identity, errno transcript, or immutable observation artifact is committed. The cited unit control merely replaces `_publish_no_replace` with a function that synthetically raises `ENOTSUP` at [`test_sgcp_embed_family.py:4198`](/tmp/sgcp-v12-review-9c170f7/tests/test_sgcp_embed_family.py:4198)-[`4202`](/tmp/sgcp-v12-review-9c170f7/tests/test_sgcp_embed_family.py:4202).

Moreover, on macOS `_publish_no_replace` selects `renameatx_np` when present and returns or raises without trying the hard-link path ([`verify_sgcp_embed_family.py:7078`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7078)-[`7103`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7103)). Therefore a normal writer call cannot establish that both primitives failed.

The synthetic fallback test supports the fallback logic, but not the stated real-volume observation. Preserve a read-only observation artifact with exact probes and environment, or narrow the documents to the injected `ENOTSUP` control.

### 3. Low — Tests do not cover exceptional public-state restoration or inherited child contexts

Type: evidence-coverage defect; no demonstrated false-valid path in the ordinary API.

The state construction/reset pattern at [`verify_sgcp_embed_family.py:7007`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7007)-[`7013`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7013) correctly isolates successive calls, ordinary nested public calls, and threads that start independent contexts. The committed tests exercise two synchronized calls and one successful nested call at [`test_sgcp_embed_family.py:4095`](/tmp/sgcp-v12-review-9c170f7/tests/test_sgcp_embed_family.py:4095)-[`4149`](/tmp/sgcp-v12-review-9c170f7/tests/test_sgcp_embed_family.py:4149).

They do not establish:

- restoration after an exception escapes the public worker;
- callback re-entry into `_verify_document_with_active_path_state` while the outer permit is active;
- a child `contextvars.copy_context()` or asynchronous task inheriting the same mutable `_VerificationState`;
- concurrent mutation of the aliased `actual_work`, cache, or reservation from such a child context.

A copied context propagates the same mutable state object, not a copy. This is not reachable from hostile input through the documented synchronous API, so I do not classify it as an ordinary false-valid defect. The documentation should nevertheless avoid implying isolation from child contexts, and tests should cover exceptional restoration before launch-plan design.

## Adversarial state/routing analysis

Each public `verify_document` constructs a fresh `_VerificationState`, installs it with a token, and resets that token in `finally`. Nested public calls therefore restore the precise outer object in LIFO order. Separate threads get independent context state. Successive calls do not reuse cache, reservation, or work dictionaries.

The work mutation boundary rejects Boolean, float, zero, negative, string, and null amounts because it requires `type(amount) is int and amount > 0` at [`verify_sgcp_embed_family.py:546`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:546)-[`555`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:555). Completed graph/expansion and provenance/predicate counters are equality-checked, not merely reservation-dominated.

Partial semantic, replay, and primary-proof failures generally call `mark_actual_work_incomplete`; completed cap equality requires a finished proof and coincident lower bound, upper bound, and optimum. Cache hits and misses are separately charged, and completed cache entries/misses are reconciled.

Public `verify_row` is fail-closed before semantic work at [`verify_sgcp_embed_family.py:2271`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:2271)-[`2276`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:2276). Internal semantic helpers require the identity-checked active permit. There is no ordinary caller-supplied callback or permit argument, so I found no static hostile-document path that fabricates the permit.

The production test wrapper remains present at [`verify_sgcp_embed_family.py:6554`](/tmp/sgcp-v12-review-9c170f7/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6554), but it cannot create a permit. Calling it normally fails before reset or semantic work.

The exact V12 router accepts only `CURRENT_SCHEMA`; V1–V11 are enumerated and rejected without row verification. Canonical routing requires the exact ordered 168-row grid and 672 cap cells.

## Adversarial publication analysis

Input admission opens the final component with `O_NOFOLLOW`, requires a regular inode, reads one descriptor-bound fixed-size snapshot, hashes those same bytes, and compares device, inode, size, mtime, and ctime before and after. Renaming the pathname after open cannot substitute the bytes. Parent input symlinks remain deliberately admitted and disclosed.

Output placement is lexically normalized beneath the development root. Parent components are descriptor-walked with `O_DIRECTORY|O_NOFOLLOW`; symlinked components reject. Destination creation uses no-replace rename, hard-link publication, or descriptor-relative `O_EXCL`. Existing files, final symlinks, and hard-link names resist overwrite.

The `renameatx_np` declaration has the expected five-argument shape, with descriptor/name pairs and an unsigned flags argument; `0x4` is used for `RENAME_EXCL`. Unsupported fallback is restricted to `ENOTSUP`/`EOPNOTSUPP`, while collision and other errors remain failures. That is conservative, though other filesystems may report unsupported semantics differently and become unavailable rather than unsafe.

The direct exFAT fallback intentionally exposes a partial final file after write or fsync failure. It is no-overwrite, not atomic. The more subtle complete-destination-after-failure states identified in Finding 1 are not tested or fully operationalized.

The producer diff removes both stale replace-based writer functions, including `os.replace`, and removes the now-unused `os` import. I found no remaining producer CLI writer: `main` terminates with `PermissionError`, generated-curve construction and legacy-row construction remain disabled, and `build_density_row` admits only the exact frozen p=19/B4 association.

## Scope/authority analysis

The committed authority remains narrow:

- status is `review_required`;
- `maximum_runs=0`;
- zero V12 generated curve-family density rows;
- zero V12 canonical matrices, runners, launch plans, or executions;
- one frozen B4 density document control;
- exactly three transient, noncanonical B4/B6/B8 legacy semantic rows in test setup.

Older committed V1 development artifacts remain in the repository, but V12 does not relabel them and its router rejects their schemas. I found no new persisted V12 generated density artifact or run directory in the reviewed diff.

No document widens the result into fixed-curve preprocessing, rho improvement, an exponent, relation yield, rank, linear algebra, target descent, deployment relevance, or an ECDLP result. The hypothesis remains restricted to generated 5–8-bit toy curves and a preregistered finite predicate/compiler matrix.

Hostile same-process Python behavior is explicitly out of scope. Such a process can introspect the module sentinel, instantiate `_VerificationState`, replace globals, mutate state dictionaries, or invoke internal workers during an active permit. That is not a Python security boundary and must not be treated as one. These capabilities are distinct from an ordinary document or public API false-valid path.

## Independent vector and hash checks

The nine committed-blob hashes match the V12 log:

| Artifact | Independently computed SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `a0287723c447b4db29eed495e80ea06fda03a21d90159c01dd96f26aa9f9380e` |
| `src/verify_sgcp_embed_family.py` | `a203016c22f45fde84a245d611cac035cf62ddfd933cb6526621a195274207ad` |
| `tests/test_sgcp_embed_family.py` | `454693a4cce435949b07b39b531c14efaab5e918733afdcbb90645ba365f4fcc` |
| `hypothesis.json` | `fac5fb25b3d46afaee7290687f564205ea7d965fe74406bb9384f265c3bcbd82` |
| `specification.json` | `98e2d5a78aeee8f9dc7c2497f4ecbbfa191cae61750832039ff21301d8596a51` |
| `contract.md` | `49b44860fc63da06d15e605aab69ef55c11ae2db3baaf28e691ca7e53a990f94` |
| `protocol-amendment-v12.json` | `dca7fef2dfa8aa0548a2084a3735369209d2e51e3a4217f7517637b7cc014858` |
| `revision-response-v12.md` | `f30b442dde20fff87b8f5e200ec623eb816d633e564a31dd704e73edfe2f9af5` |
| `source-self-review-v12.md` | `0850dafa892c084d10c917ad4cde47cd4084963001c5d1df00044ae51e4fc74e` |

Independent canonical work-vector derivation:

- Prime candidates: two seeds across bit sizes 5–8 give  
  `2 × (2^4 + 2^5 + 2^6 + 2^7) = 2 × 240 = 480`.
- Accepted-draw transcript lengths:  
  `12 + 49 + 4 + 15 + 11 + 8 + 3 + 10 = 112`.
- Three domain-separated curve hashes per draw:  
  `3 × 112 = 336`.
- Nonsingular draws are  
  `12 + 47 + 4 + 14 + 11 + 8 + 3 + 10 = 109`; each is independently enumerated twice, giving `2 × 109 = 218`.
- Across three B values and four null replicates, the eight curve transcripts contribute  
  `12 × (15+9+18+23+53+41+105+69) = 12 × 333 = 3,996` null hashes. Mobius and two-Mobius nonce derivations contribute `72+150=222`. Total: `3,996+222=4,218`.

Thus the canonical completed vector is exactly `480/112/336/218/4218`. Frozen-fixture expectations for these five counters are zero.

## Residual risks

Even after the two publication/evidence issues are repaired:

- `ContextVar` protects normal invocation composition, not hostile introspection, monkeypatching, signals, or deliberately copied child contexts.
- The verifier source hash is a module-load diagnostic, not executed-code attestation.
- Parent input symlinks are allowed; the opened inode is protected, but pathname provenance is not.
- The exFAT direct-write fallback remains visibly partial on interruption.
- Filesystem and directory durability depend on platform behavior and successful fsync operations.
- Resource reservations are source-level combinatorial bounds, not hard CPU, RSS, allocator, I/O, or memory-bandwidth limits.
- Deterministic replay of secondary objective fields is not structurally independent in the same sense as the frozen B4 oracle.
- All evidence remains toy-scale implementation preflight and cannot support a cryptographic-scale claim.

## Handoff

```yaml
handoff:
  id: TASK-20260723-001
  from: coordinator
  to: executor
  objective: remove publication terminal-state ambiguity and preserve reviewable filesystem evidence before any launch-plan design
  inputs:
    - commit 9c170f70d6f4b7aafc20b5adfe70f22a702b5d8b
    - parent 0d5d541e344818fa84ec18279ced3c2b19324423
    - this independent red-team review
  constraints:
    - no generated curve-family density row
    - no canonical matrix, runner, launch plan, or execution
    - preserve maximum_runs=0
    - do not widen mathematical or ECDLP claims
  deliverables:
    - explicit protocol for a destination appearing after unsuccessful publication
    - controls for post-publish directory-fsync failure
    - controls for hard-link success followed by temporary-unlink failure
    - committed raw evidence or corrected wording for the claimed exFAT observations
    - exceptional and inherited-child-context state tests with accurately scoped documentation
  budget:
    wall_clock_seconds: null
    memory_gb: null
    maximum_runs: 0
  completion_gate:
    - no unsuccessful publication can be mistaken for accepted evidence
    - every visible failure-state destination has a documented terminal classification
    - real-filesystem claims are backed by immutable artifacts or removed
    - fresh exact-commit theory, accounting, and red-team review
```

REVISE before launch-plan design