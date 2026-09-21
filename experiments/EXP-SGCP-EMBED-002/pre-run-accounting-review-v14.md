## Handoff: EXP-SGCP-EMBED-002 V14 accounting review

### Claim or task

Independent static review of exact detached commit `371790de7418aee8b1f56b7fa872f91bbec43899`, parent `bc11b2dca2a216bab0c28ec93ed168ab271fa77e`.

The checkout remains clean and detached. No producer, verifier, test suite, experiment, launch workflow, or record validator was run; no file was modified and no experiment ran.

### Status

`REVISE`

The accounting and publication state machine are otherwise coherent for later non-executable launch-plan design, but one exact-claim correction is required first: V14 overstates rejection of lexical `.`/empty path components.

This status authorizes no launch plan, generated row, execution, or budget increase.

### Assumptions

- The publication threat model is an ordinary controlled workspace, not a hostile same-user or hostile same-process environment.
- Receipt identifiers rely on normal `secrets.token_hex(32)` behavior.
- The completed operation vector is a prospective exact canonical-matrix expectation, not an observed V14 run result.
- Recorded test outcomes are historical and were not reproduced.

### Evidence so far

- Identity and scope:
  - Detached exact commit and parent confirmed; final status remained clean.
  - Ledger remains `runs: []`, `review_required`, version 14 at [ledger.json:127](/tmp/sgcp-v14-review-371790d/ledger.json:127).
  - Active budgets are zero: wall time, CPU, memory, and runs at [specification.json:208](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/specification.json:208). The `900s/4GB` figures are explicitly proposed future per-role ceilings, not active authority, at [hypothesis.json:68](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/hypothesis.json:68).
  - Zero generated V14 density rows and zero runs are recorded at [research_ledger.md:29](/tmp/sgcp-v14-review-371790d/research_ledger.md:29).

- Independent completed-vector derivation, without invoking the repository expected-value helper:
  - Prime candidates: `2 × (16+32+64+128) = 480`.
  - Draws: `12+49+4+15+11+8+3+10 = 112`.
  - Curve hashes: `3 × 112 = 336`.
  - Point enumerations: `2 × (12+47+4+14+11+8+3+10) = 218`.
  - Predicate hashes: `74 × 3 + 12 × (15+9+18+23+53+41+105+69) = 222+3996 = 4218`.
  - The fixed transcript inputs appear at [pre-run-accounting-review-v13.md:19](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/pre-run-accounting-review-v13.md:19); current charging semantics remain at [verify_sgcp_embed_family.py:1003](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:1003), [verify_sgcp_embed_family.py:938](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:938), and [verify_sgcp_embed_family.py:1135](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:1135).

- All nine SHA-256 values at [development-test-log-v14.md:19](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:19) match the exact committed blobs:
  - Producer `8a98e94a…efbe`
  - Verifier `9aa3bef0…e2f`
  - Focused tests `9c61fa2b…3170`
  - Hypothesis `d8f4df40…ae83`
  - Specification `ebb0735d…21b2`
  - Contract `ef6903da…992a`
  - Amendment `365b337c…59f9`
  - Revision response `921758f2…9afc`
  - Self-review `3e4d37b4…684f`

- Static counts:
  - 81 focused `unittest` methods.
  - 225 repository `unittest` methods; another 27 module-level pytest-style functions are not counted by `unittest discover`.
  - 16 record objects: research question, hypothesis, specification, and 13 decisions. The selector semantics are at [records.py:184](/tmp/sgcp-v14-review-371790d/src/crypto_autoresearcher/records.py:184).
  - Historical observations report 81 focused tests and 225 repository tests at [development-test-log-v14.md:38](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:38) and [development-test-log-v14.md:101](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:101). These were not rerun.

- Publication state machine:
  - Both deterministic names are preflighted before data creation at [verify_sgcp_embed_family.py:7663](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7663).
  - Data and receipt each use no-overwrite publication at [verify_sgcp_embed_family.py:7667](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7667).
  - Every normal accepted return requires exact-attempt terminal validation at [verify_sgcp_embed_family.py:7680](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7680).
  - Ordinary post-receipt exceptions reconcile only to the expected identifier and payload at [verify_sgcp_embed_family.py:7691](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7691).
  - Accepted results contain identifier, path, sizes/hashes, both publication methods, receipt digest, and warnings at [verify_sgcp_embed_family.py:7731](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7731).
  - Absent, orphan, invalid-receipt, receipt-mismatch, attempt-mismatch, validation-error, path-error, and accepted states are distinct at [verify_sgcp_embed_family.py:7441](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7441) and [verify_sgcp_embed_family.py:7587](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7587).
  - Definite direct-write nonregular or wrong-size observations are fatal; unavailable `fstat`/durability information is warning-only but cannot bypass terminal validation at [verify_sgcp_embed_family.py:7189](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7189).
  - The production hard-link branch actually calls `os.link` at [verify_sgcp_embed_family.py:7158](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7158). Historical controls wrap the real call on a temporary root at [test_sgcp_embed_family.py:4872](/tmp/sgcp-v14-review-371790d/tests/test_sgcp_embed_family.py:4872) and [test_sgcp_embed_family.py:5012](/tmp/sgcp-v14-review-371790d/tests/test_sgcp_embed_family.py:5012). No mounted-filesystem support or durability claim is made.

- Cost boundaries are properly separated:
  - Structural counters and overlapping serialized-byte receipts are not CPU, field-operation, memory, or end-to-end costs at [contract.md:380](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/contract.md:380).
  - Producer and verifier wall time, CPU, peak RSS, parser objects, allocator retention, disk, I/O, cache traffic/occupancy, memory bandwidth, output size, and role-specific costs remain unmeasured external obligations at [contract.md:395](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/contract.md:395) and [protocol-amendment-v14.json:30](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v14.json:30).
  - Warning preservation and immutable external artifact storage remain future-runner obligations at [contract.md:260](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/contract.md:260).

### Failure modes/findings, ordered by severity

- No Critical, High, or Medium accounting/state-machine defect found.

- Low — required exact-claim correction: lexical dot-component rejection is overstated. `output_path` first converts the supplied spelling to `Path`, then inspects `.parts`; `Path` has already collapsed `.` and repeated empty separators, so only `..` is meaningfully detected at [verify_sgcp_embed_family.py:7062](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7062). The descriptor walker repeats the same ineffective checks for `.`/empty components at [verify_sgcp_embed_family.py:7079](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7079), while the sole new control tests only `..` traversal at [test_sgcp_embed_family.py:4601](/tmp/sgcp-v14-review-371790d/tests/test_sgcp_embed_family.py:4601). This does not reopen the V13 outside-root escape—the `..` exploit is blocked and descriptor containment remains sound—but it contradicts the broader “lexical dot components” claims at [source-self-review-v14.md:16](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/source-self-review-v14.md:16) and [contract.md:226](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/contract.md:226).

- Informational — the repository-wide historical suite was not fully green: 224/225 passed and the existing immutable-run guard refused overwrite at [development-test-log-v14.md:108](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:108). This is not a V14 assertion failure, but it is historical evidence rather than fresh confirmation.

- Informational — accepted content is not proof of durability, pair-atomicity, hostile-actor authentication, mounted-filesystem hard-link support, or successful external preservation. These boundaries are accurately disclosed at [development-test-log-v14.md:123](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:123).

### Next concrete action

Correct the exact path claim before launch-plan design:

- Either inspect the raw path spelling before `Path` normalization and add controls for raw `./`, repeated separators, and `../`; or
- Narrow every V14 claim to the property actually needed and established: normalized containment plus explicit parent-traversal (`..`) rejection and no-follow descriptor walking.

Then commit a new exact snapshot and obtain fresh read-only theory, accounting, and red-team review. Preserve `maximum_runs=0`, all execution budgets at zero, and create no row, plan, or run artifact during the correction.

### Artifact paths

- [contract.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/contract.md)
- [development-test-log-v14.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md)
- [handoff.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/handoff.md)
- [hypothesis.json](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/hypothesis.json)
- [protocol-amendment-v14.json](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v14.json)
- [revision-response-v14.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/revision-response-v14.md)
- [source-self-review-v14.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/source-self-review-v14.md)
- [specification.json](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/specification.json)
- [sgcp_embed_family.py](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py)
- [verify_sgcp_embed_family.py](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py)
- [test_sgcp_embed_family.py](/tmp/sgcp-v14-review-371790d/tests/test_sgcp_embed_family.py)
- [ledger.json](/tmp/sgcp-v14-review-371790d/ledger.json)
- [research_ledger.md](/tmp/sgcp-v14-review-371790d/research_ledger.md)

