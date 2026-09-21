# EXP-SGCP-EMBED-002 V17 Fresh Independent Pre-Run Red-Team Review

## Findings

### Blocking defects

1. **Critical — the verifier CLI erases two rejected raw spellings before V17 admission.**

   The API grammar rejects terminal `/` and terminal `/.` only when it receives the original string (`src/verify_sgcp_embed_family.py:7065-7092`). However, the CLI declares `--output` as `type=Path`, then passes that already-normalized object through `output_path` and the writer (`src/verify_sgcp_embed_family.py:7784-7795`).

   On the controlled runtime, both `/development/probe.json/` and `/development/probe.json/.` become `/development/probe.json` during `Path` construction. They can therefore be published instead of rejected. This directly contradicts the every-ingress and pre-`Path` claims in `contract.md:226-233`, `revision-response-v17.md:28-44`, and `source-self-review-v17.md:20-37`.

   The focused table exercises direct APIs with exact strings but never the upstream CLI coercion (`tests/test_sgcp_embed_family.py:4752-4948`). The producer also declares `--output` as `type=Path` (`src/sgcp_embed_family.py:2105-2120`), although its current `main` refuses all row production before writing.

   **Cleanest counterexample:** invoke the verifier CLI with an otherwise valid input and an absent in-root destination spelled with terminal `/` or `/.`; the spelling is normalized before `_raw_output_path` can reject it.

2. **High — the 179-path manifest is not the claimed complete governance/evidence/approval review surface.**

   The finite rules include `AGENTS.md`, selected root files, flat schemas/core/tests, two predecessor files, and most static EXP-SGCP-EMBED-002 files (`review-surface-manifest-v17.json:22-56`). They omit:

   - `README.md`;
   - `agents/coordinator.md`;
   - `agents/executor.md`;
   - `agents/idea-generator.md`;
   - `docs/task-lifecycle.md`;
   - `docs/evidence-and-reproducibility.md`;
   - `templates/research-records.md`.

   These are not incidental documentation. The repository map identifies them as coordinator authority, executor semantics, the state machine, evidence rules, and shared record definitions (`README.md:20-35`). Coordinator-only approval authority is defined in `agents/coordinator.md:7-15`; approval-to-execution transitions are defined in `docs/task-lifecycle.md:29-37`; the audited approval-lock workflow is documented in `README.md:89-104`.

   Therefore the manifest does not satisfy the V16 decision’s requirement to cover governance, evidence, runner, schema, and approval-gate paths (`decision-v16.json:34-40`), despite the completion claims in `revision-response-v17.md:20` and `source-self-review-v17.md:51-61`.

   The exact Git tree binds these omitted bytes, but byte binding is not review-surface inclusion: a reviewer following the manifest is never instructed to inspect them.

3. **High — the manifest’s zero-artifact language is unqualified and literally contradicted by excluded immutable evidence.**

   The manifest requires verification of “zero generated curve-family density rows and zero runs” and records `generated_curve_family_density_rows: 0` (`review-surface-manifest-v17.json:11-19,63-67`), while explicitly excluding `development` and `runs` components (`review-surface-manifest-v17.json:43-47`).

   The excluded committed development manifest records:

   - one prior smoke row;
   - sixteen additional development rows;
   - seventeen total rows consumed;
   - a `completed_valid_development` run manifest.

   See `development/DEV-SGCP-EMBED-002-V1/run-manifest.json:2-6,76-80`. The specification also acknowledges seventeen rows consumed before V17 (`specification.json:112-116`).

   The defensible current-state statement is narrower: **zero generated V17 rows and zero canonical runs**. That qualified statement appears in `handoff.md:60-64`; the generated ledger has no canonical runs (`ledger.json:126-132`). The manifest’s field and reviewer instruction must use the same qualification and inventory the four historical development artifacts needed to verify it.

### Residual limitations

4. **Custom `__fspath__` can cause filesystem effects before rejection.**

   `_raw_output_path` must execute caller-controlled `os.fspath(path)` before it can inspect the returned type or spelling (`src/verify_sgcp_embed_family.py:7065-7073`). A byte-valued custom `PathLike` can create its proposed destination inside `__fspath__`, return bytes, and then be rejected. The inert custom classes in `tests/test_sgcp_embed_family.py:4755-4767` do not test this.

   This is not a V17 descriptor-walker containment escape; it is arbitrary same-process callback behavior. Nevertheless, “every rejected class creates no candidate destination” is too strong (`source-self-review-v17.md:39-49`). Scope that assertion to inert `__fspath__` implementations or explicitly place callback side effects inside the hostile same-process boundary.

5. **Manifest encoding and glob semantics should be hardened for successor trees.**

   The current 179 entries are all regular `100644` Git blobs; no selected symlink or mode anomaly was found. The count and digest reproduce exactly. Still:

   - `*.json`/`*.py` matching semantics are not tied to a named Git-path algorithm;
   - newline-joined Git paths are not prefix-free if a future Git pathname contains a newline;
   - the receipt does not record modes/types, although the exact tree does bind them.

   A successor should define raw NUL-delimited Git-tree enumeration or reject control-bearing pathnames and include `mode`, `type`, and pathname in its canonical receipt.

## Overclaim corrections

- Replace “finite grammar through every ingress” with “finite grammar through direct Python entries on the controlled POSIX runtime”; restore the stronger statement only after preserving raw CLI strings.
- Replace “complete governance/evidence/runner/schema/approval surface” with either the actual 179-path subset or expand the manifest to include all normative repository files above.
- Replace “zero generated rows/runs” with “zero generated V17 curve-family density rows and zero canonical runs; seventeen historical V1 development rows and one historical development run manifest remain.”
- Limit no-destination claims to path coercions whose `__fspath__` has no external side effects.
- Continue treating every recorded test result as historical. V17 records 81 focused passes, but repository-wide unittest discovery had one failure and omitted 27 module-level pytest-style tests (`development-test-log-v17.md:36-48,94-117`).

## Required controls before renewed review

1. Parse verifier `--output` as an uncoerced exact string and pass it directly to the writer. Add CLI-level terminal `/` and `/.` rejection controls that assert no destination or parent is created.
2. Add a side-effecting string-valued and byte-valued `PathLike` control, then state precisely whether callback effects are in or out of scope.
3. Expand the manifest with the normative `README`, `agents`, `docs`, and template files plus exact historical EXP-SGCP-EMBED-002 development artifacts.
4. Qualify row/run fields by protocol version and canonical/development status.
5. Pin Git path matching, pathname encoding, and entry-mode rules; recompute the successor inventory and digest independently.
6. Preserve `maximum_runs=0`; rerun validation only in the successor’s separately authorized preflight, not as part of this review.

## Next falsification tests

- **CLI counterexample:** terminal `/` and `/.` must survive argument parsing and be rejected before output-parent creation.
- **Callback counterexample:** a rejected `PathLike.__fspath__` that creates its candidate path must either falsify the no-creation claim or be explicitly excluded.
- **Manifest omission counterexample:** alter `agents/coordinator.md` in a synthetic successor tree; the review-surface digest must change.
- **Historical-evidence counterexample:** alter or add an excluded development row artifact; the authority receipt must detect or explicitly classify it.
- **Path inventory counterexample:** introduce a newline-bearing pathname or selected symlink in a synthetic tree and require deterministic rejection or an unambiguous mode-aware digest.

## Verification receipts

### Exact checkout

- Requested path: `/tmp/sgcp-v17-review-d6b642d`
- Physical path: `/private/tmp/sgcp-v17-review-d6b642d`
- Commit: `d6b642defccddab7629678ee3514c48228844bfa`
- Parent: `574b4c67a894e48715107e730c0b7b33b9fab1c5`
- Tree: `f27c736a2660155521b6da913bb1e7e0f3a9bffc`
- Initial status: detached and clean
- Final status: detached and clean
- Mutable worktree file bytes inspected: none
- Repository programs/tests/producer/verifier/validator/indexer/runner/experiment executed: none
- Proposed artifact path, not written: `experiments/EXP-SGCP-EMBED-002/pre-run-red-team-review-v17.md`

### Manifest recomputation

- Recomputed paths: `179`
- Recomputed path-name SHA-256: `bc8034d20ac3d092270d749b6cb363df4f8f4531bccc0dd9a6616120f51de952`
- Receipt match: yes
- Selected non-regular or non-`100644` entries: none
- Manifest includes its own pathname but not its own byte hash; the exact tree supplies byte and mode binding. No current self-hash paradox was found.

### Ten recorded artifact hashes

All values in `development-test-log-v17.md:20-31` match the corresponding commit blobs:

| Artifact | SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `e9ba02997893cd2307e7489b7dea15e270e584af80797ded1c7d77c1372ad454` |
| `src/verify_sgcp_embed_family.py` | `e3ff7af6c379b9bc52ec0d1e3e6f9ef874cf258351665f897462a4ee1c93612a` |
| `tests/test_sgcp_embed_family.py` | `f35ec050c2acfcdbb4332abf517d91d2366f1bd8217bc5ed077408691fbfd745` |
| `hypothesis.json` | `4c5763186ae60fc63f711315d7861fb0fafb233788c59a778210035178cd2052` |
| `specification.json` | `c31b14595d6750617c6d2f7933b850c6144d94d35fb9c8aaac3b11ba4fcb3ea9` |
| `contract.md` | `5f7d610b3a138d54c47ff2a5c96f2ae8609547b92c05ed59e0bfaed0372c10fb` |
| `protocol-amendment-v17.json` | `6ebdb14f160e75d9bb6b74d6d5b72797d03c0c234e8e0558c9ac63ca68a18465` |
| `revision-response-v17.md` | `1eb21f4a7ecfa5c26ceaff8f2a47351d3bfe324225a8f3928b072af33b48db76` |
| `source-self-review-v17.md` | `9a9c750c9271b6180110a5d8c9d53bb804fd41991b452251614eb225bde576f3` |
| `review-surface-manifest-v17.json` | `e8e21e6de35d775efadee6f3b8584273923af8394247fd9e28e388594c5b1e39` |

### Current-state and authority checks

- Producer and verifier identify V17 (`src/sgcp_embed_family.py:25-30`; `src/verify_sgcp_embed_family.py:30-53`).
- V1–V16 schemas route to explicit rejection without row verification (`src/verify_sgcp_embed_family.py:6974-7016`).
- Handoff and active research-ledger row correctly request fresh review and prohibit plan design/execution (`handoff.md:1-15,86-91`; `research_ledger.md:24-30`).
- Status is `review_required`; budget is zero in every dimension; `approved_by` is null (`specification.json:209-216,378-379`).
- Ledger canonical runs are empty (`ledger.json:126-132`).
- No EXP-SGCP-EMBED-002 launch-plan or approval artifact is present.
- No current execution authority was found.

### Mathematical and accounting invariance

The parent diff changes producer/verifier protocol identifiers, legacy routing, messages, path admission, tests, and governance records. It does not alter the curve grid, curve predicates, representative compiler, graph construction, optimizer objective, cap schedule, family thresholds, reservation formulas, or mathematical success criterion.

An independent standalone arithmetic reconstruction—without importing repository code—reproduced:

- prime candidates: `480`;
- accepted-curve draws: `112`;
- curve hash calls: `336`;
- registered-curve point enumerations: `218`;
- predicate hash calls: `4218`.

The claim boundary remains appropriately narrow: toy, model-bound, compiler-bound, and novelty-unverified (`hypothesis.json:7-13,76-88`). Rank, target descent, factor-base logarithms, rho crossover, cryptographic scaling, and deployment claims remain excluded (`contract.md:651-656`). Structural counts remain explicitly distinct from CPU, field-operation, RSS, parser, allocator, disk, I/O, cache, and bandwidth costs (`contract.md:395-425`).

## Final verdict

**REVISE before launch-plan design**

This verdict authorizes neither execution nor any mathematical or cryptanalytic claim.

## Handoff: V17 pre-run red-team closeout

### Claim or task

Determine whether exact V17 commit `d6b642defccddab7629678ee3514c48228844bfa` is ready to permit separate launch-plan design.

### Status

`NEGATIVE RESULT` for V17 pre-run readiness only. No mathematical hypothesis was tested or falsified.

### Assumptions

- Review was confined to immutable Git objects at the exact commit, parent, and tree above.
- Recorded tests were treated as historical.
- The direct Python path grammar was evaluated separately from CLI coercion and arbitrary same-process callback behavior.
- Zero canonical budget and no execution authority remain binding.

### Evidence so far

- Checkout identity, detached state, and cleanliness matched before and after.
- All ten byte hashes, the 179-path receipt, and the five accounting totals reproduce.
- V17 mathematical and reservation semantics are unchanged from the parent.
- The CLI raw-spelling bypass, omitted normative review-surface files, and unqualified zero-artifact fields remain blocking.

### Failure modes

- Terminal `/` and `/.` can be normalized away by CLI parsing and published.
- A manifest-compliant review can omit authority-bearing repository files.
- Historical development rows can coexist with an unqualified zero-row receipt because their directory is excluded.
- Caller-controlled `__fspath__` can perform effects before type rejection.

### Next concrete action

Implement one no-run successor that preserves raw CLI strings through admission, qualifies and binds historical-versus-V17 row/run state, expands the normative review surface, and adds the listed falsification controls before requesting fresh exact-commit review.

### Artifact paths

- Proposed, not written: `experiments/EXP-SGCP-EMBED-002/pre-run-red-team-review-v17.md`
- `experiments/EXP-SGCP-EMBED-002/review-surface-manifest-v17.json`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/handoff.md`
