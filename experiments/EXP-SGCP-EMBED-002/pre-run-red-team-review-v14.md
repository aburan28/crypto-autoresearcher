## Findings

**Critical — none.**

**High — none.**

**Medium — none.**

**Low**

1. **Raw `.` and empty path components are normalized away, not rejected as claimed.** `output_path` first constructs a `Path`, then inspects `.parts`; `pathlib` has already collapsed `.` and repeated separators at that point. The descriptor walker consequently receives the normalized path. Containment remains safe because `..`, outside-root paths, parent symlinks, and final symlinks are still rejected, but the exact rejection claim and control coverage are inaccurate. The only new path control exercises `..`, not raw `.`, trailing `/.`, or repeated separators. [verifier:7062](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7062), [verifier:7079](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7079), [path test:4601](/tmp/sgcp-v14-review-371790d/tests/test_sgcp_embed_family.py:4601), [self-review:16](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/source-self-review-v14.md:16), [contract:226](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/contract.md:226).

2. **The committed current-state and next-action text is stale.** The primary handoff still directs the coordinator to finish validation, freeze hashes, and commit V14, while the reviewed object is already that committed snapshot and the test log records those historical validations. The research ledger similarly says “under validation” and “Validate and commit.” This is workflow/documentation drift, not a publication or mathematical defect. [handoff:80](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/handoff.md:80), [test log:79](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:79), [test log:134](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:134), [research ledger:29](/tmp/sgcp-v14-review-371790d/research_ledger.md:29).

3. **The durable-artifact ledger still omits four committed V7 predecessor records.** It jumps from `decision-v6.json` to the V7 reviews, omitting `protocol-amendment-v7.json`, `revision-response-v7.md`, `development-test-log-v7.md`, and `source-self-review-v7.md`, although the specification correctly requires them. This is an inherited provenance-inventory defect. [research ledger:215](/tmp/sgcp-v14-review-371790d/research_ledger.md:215), [research ledger:223](/tmp/sgcp-v14-review-371790d/research_ledger.md:223), [specification:275](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/specification.json:275).

## Informational / residual risks

- Checkout confirmed clean and detached at `371790de7418aee8b1f56b7fa872f91bbec43899`, with sole parent `bc11b2dca2a216bab0c28ec93ed168ab271fa77e`.
- No producer, verifier, tests, validator, experiment, or runner ran. No file or artifact was modified. Only Git/object reads, hashes, source inspection, static counts, path-normalization checks, and a standalone arithmetic calculation were performed.
- Exact-attempt reconciliation is sound within the documented ordinary synchronous, available-memory, non-hostile-process boundary. Rename, actual hard-link, and direct `O_EXCL` receipt exceptions can return accepted only after ID-and-payload validation; descriptor-close errors become warnings. [verifier:7637](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7637).
- `KeyboardInterrupt`, `SystemExit`, process death, power loss, practical memory exhaustion, and hostile monkeypatching can still prevent a success return after a matching pair becomes visible. That limitation is disclosed without overclaim. [protocol:27](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v14.json:27).
- Stale data/receipt names block retries; concurrent legitimate writers have one data winner; reconciliation checks the expected publication ID. Ordinary public status remains forgeable through valid re-signing, as expected for an unkeyed receipt. [verifier:7354](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7354), [verifier:7540](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7540).
- Definite direct-write type/size mismatches fail; unavailable `fstat`, fsync, or close may warn, but cannot produce acceptance unless terminal descriptor-based validation succeeds. [verifier:7168](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7168).
- The hard-link controls statically wrap the real `os.link`. The test-local validator shares no production status/canonicalization helper, while correctly disclaiming filesystem-race independence. [tests:73](/tmp/sgcp-v14-review-371790d/tests/test_sgcp_embed_family.py:73), [tests:4883](/tmp/sgcp-v14-review-371790d/tests/test_sgcp_embed_family.py:4883).
- All nine logged SHA-256 values match. Static counts are 81 focused and 225 repository test methods. The reported 81-test success and 224/225 repository outcome remain historical and were not rerun. [test log:15](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:15), [test log:94](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:94).
- Independent arithmetic reproduced `480/112/336/218/4218`.
- The parent diff does not alter the curve grid, predicates, representative compiler, objective, family gate, or frozen controls beyond V14 identifiers. Public generated construction remains gated, with only frozen B4 density and transient B4/B6/B8 legacy controls statically admitted. [producer:1463](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1463).
- `ledger.json` has `runs: []`, `review_required`, version 14. All active execution budgets are zero; no V14 family-density row, canonical matrix, runner, launch plan, exponent, or ECDLP claim exists. [ledger:126](/tmp/sgcp-v14-review-371790d/ledger.json:126), [specification:208](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/specification.json:208).

### Claim or task

Independent static exact-commit red-team review of EXP-SGCP-EMBED-002 V14 against its requested parent.

### Status

**REVISE.** This verdict authorizes nothing: no launch-plan design, runner, execution, generated row, canonical matrix, budget increase, or mathematical/ECDLP claim.

### Assumptions

The publication assessment assumes standard library/syscall behavior, available memory, and no hostile same-process or same-user mutation. Historical runtime logs were inspected only as committed claims.

### Evidence so far

The V13 high/medium publication defects are materially repaired: exact-attempt receipts, stale-name preflight, winning-writer attribution, final-pair validation, actual hard-link controls, and fail-closed direct-size handling are statically present. The remaining findings are exact documentation/control-coverage defects, not demonstrated containment or mathematical failures.

### Failure modes

Raw path spelling is not preserved across `Path` normalization; excluded interruption classes can leave a visible pair without a success return; unkeyed receipts remain forgeable; sequential snapshots are not pair-atomic; and durability/resource/executed-code attestation remains a future external-runner obligation.

### Artifact paths

- [V14 protocol](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v14.json)
- [Producer](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py)
- [Verifier](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py)
- [Tests](/tmp/sgcp-v14-review-371790d/tests/test_sgcp_embed_family.py)
- [Handoff](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/handoff.md)
- [Research ledger](/tmp/sgcp-v14-review-371790d/research_ledger.md)

### Next concrete action

Coordinator: issue one no-run successor-repair handoff covering the raw-path claim/control mismatch, committed-state wording, and missing V7 durable-artifact entries while preserving every zero budget.