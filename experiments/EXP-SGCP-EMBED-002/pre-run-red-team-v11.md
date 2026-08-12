## Findings

1. **High — mutable module-global accounting and cache state is unsafe for concurrent or re-entrant verification.** `_ACTIVE_ACTUAL_WORK`, `_ACTIVE_RESOURCE_RECEIPT`, and `_REGISTERED_CURVE_CACHE` are process-global and repeatedly cleared or replaced without locking or per-invocation ownership. A concurrent/re-entrant call can reset counters or clear cached provenance while another verification is active, producing suppression, overcharge, incorrect completeness, or cross-request receipts. This prevents readiness for any launch-plan design that might reuse a verifier process.  
   `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:493`, `:505`, `:512`, `:931`, `:943`, `:6275`, `:6281`, `:6792`, `:6793`.

2. **High — V11’s “one frozen B4 row only” claim omits generated B6/B8 legacy rows created by the focused tests.** `_build_frozen_legacy_control_row` admits B values 4, 6, and 8 and performs factor-base, expansion, graph, pair-output, optimizer, model, and row construction. The test suite explicitly invokes it for all three values and assigns the results to `row`. Thus the log’s statements that the scope covers “one … B=4 density row” and that “only frozen B4 density construction is admitted” are materially incomplete unless legacy B6/B8 rows are expressly disclosed and classified.  
   `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1331-1452`; `tests/test_sgcp_embed_family.py:1012-1021`; `experiments/EXP-SGCP-EMBED-002/development-test-log-v11.md:5-9`, `:49-51`, `:77-78`.

3. **Medium — output admission has a check/use race and overwrite path unsuitable for immutable launch artifacts.** `output_path` resolves and checks nonexistence separately; `write_atomic` later creates a predictable PID-named temporary and uses `os.replace`, which overwrites a destination created after the earlier check. Directory-component changes between resolution and creation are also not descriptor-bound. This does not falsify read-only verification, but it blocks designing a trustworthy immutable runner around this writer.  
   `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6960-6976`.

4. **Medium — private “unchecked” and “for tests” entry points retain authorization-boundary bypasses.** Public wrappers reject direct verification, but `_verify_legacy_row_unchecked`, `_verify_density_row_unchecked`, `_verify_density_row_for_tests`, and `_verify_v11_document_value_for_tests` remain callable imports. They bypass the sole-evidence path’s regular-file snapshot, exact path routing, and final report closure. Naming conventions are not an enforceable authorization boundary for a future launcher.  
   `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:2098`, `:4420`, `:5145`, `:6516`; compare public closures at `:2234-2239` and `:5252-5269`.

5. **Low — raw counter mutation accepts negative and non-exact-integer amounts.** `charge_actual_work` validates the existing counter but not `amount`; internal or re-entrant callers can decrement counters or exploit `bool` as an integer. Final nonnegative checks do not prove monotonic charging. Current committed call sites appear controlled, so this is not demonstrated as a JSON-input bypass, but it weakens the accounting API boundary.  
   `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:512-518`; final checks at `:6047-6051`.

No additional input-driven equality-placement, transcript-authentication, bool/int, JSON lexical, report-closure, or final-component symlink bypass was established within the inspected blobs. The snapshot binds hashing and parsing to one opened inode, although parent-symlink traversal is intentionally permitted.

## HASH_CHECK

**PASS.** All nine SHA-256 values in `development-test-log-v11.md:18-26` match the exact commit blobs:

- `42e77b58419c2e5e1d1df4fc9e21a1ecc736863f2cff2bb6eda0bad8c25f0282`
- `a0bab9d018ea12af5bfbfa9f80d7ac55094cc2355f7367ad330f91c8fd8d093b`
- `45b2665b44fd0bc3ca0c7feac7c86df24ea2c85390ff3f7defa19801acb5afef`
- `31bf9007fb61e85e01db9ec1bb51885d1f9c5a2b8875b7d3c75f3ab5d37ac1a8`
- `d2d63fedabed0ea5f220ea002628e9c2a8871059c736513261f21cc40e8ae17f`
- `3ac4bc7265f767736d4070f196fca5f9399b83e61da638abeb85d4de035a3ee5`
- `4a101b1e8eccf2ca4f460d4d0c92e98bde8cdefb40514e2bbab07df52041cda9`
- `59412b0a01db07688b4107e35f547dae28d26c8875c2fe5928b3599249b602df`
- `69104e98e690beb0ed4009c0fcd52e5f37131fdc155760e578f32f15d3314fb0`

The five independently derived totals also match:

- Prime candidates: `2 × (16+32+64+128) = 480`
- Draws: `12+49+4+15+11+8+3+10 = 112`
- Curve hashes: `3 × 112 = 336`
- Point enumerations: `2 × (12+47+4+14+11+8+3+10) = 218`
- Predicate hashes across 168 transcript rows: `4,218`

## SCOPE_CHECK

**PASS.** Review scope was exact commit `f8e4606d7aa86fac9d79872be63e9a22e3854d52` and parent `2a954438add9ba6c1ce487b25d3d71a21e4019e5`, accessed through `git show`/exact-commit diff only. No mutable working-tree bytes or memory files were read, and no files were modified.

## Decision

**REVISE for launch-plan DESIGN ONLY.** Execution remains unauthorized and `maximum_runs=0`.

## Handoff: EXP-SGCP-EMBED-002 V11 independent red-team review

### Claim or task

Falsify readiness of exact V11 commit `f8e4606d7aa86fac9d79872be63e9a22e3854d52` for launch-plan design.

### Status

`REVISE` for launch-plan design only. Never authorization to execute.

### Assumptions

Private/test-only callables are not security or authorization boundaries, and a future launcher may invoke verification concurrently or re-entrantly.

### Evidence so far

All nine committed hashes and all five completed-work totals match, but process-global accounting/cache state is invocation-unsafe and the test log omits constructed frozen B6/B8 legacy rows.

### Failure modes

Concurrent verification can corrupt receipts; internal direct APIs bypass the evidence path; output publication is race-prone; launch artifacts could inherit undisclosed legacy-row construction.

### Next concrete action

Implement one no-run V12 repair that makes verifier state invocation-local, removes or hard-gates direct unchecked/test entry points, descriptor-binds no-overwrite output publication, and explicitly accounts for every B4/B6/B8 legacy row constructed by tests.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v11.md`
- `tests/test_sgcp_embed_family.py`