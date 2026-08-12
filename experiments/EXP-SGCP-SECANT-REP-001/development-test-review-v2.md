# Development-Test Execution Review V2

## Handoff: container runner with insufficient launch trust

### Claim or task

Determine whether V2 safely authorizes exactly one immutable, isolated run of
the five hash-bound public development tests.

### Status

NEGATIVE RESULT

### Assumptions

- Trusted-local static review at the exact committed V2 target.
- Protected source and tests were inspected only as plain text.
- No protected source/test was parsed by a tool, imported, compiled, tested,
  or executed; neither V2 runner was invoked.
- The result concerns the V2 launch and accounting contract, not the static
  mathematical core or test semantics.

### Evidence so far

- Reviewed commit:
  `d5d946319026ba57aafe922332acc3f315c16cee`.
- Reviewed tree:
  `990ecdd3746a7712561398a2efb094c252352f79`.
- Sole parent:
  `1ed6a17e4deffd88e5c07c8788aa18fb1f0d3407`.
- Protocol SHA-256:
  `026e940ea7304dab1db0847503054143288b43ff6b43b2f3b674c1ee319885fa`.
- Host-runner SHA-256:
  `86cc01e3c04155cb6b5903c3ce30baff43abe57ae2674d7146b810dbcf1a6e70`.
- Container-runner SHA-256:
  `8c7f0e68139cb166af705df619374ef7bc02b35579b7302dbcd271edb77808f6`.
- Theory principal `019fad1f-84b2-7192-bb18-32228f769735` returned
  `GO` for exact five-test selection, Python startup isolation, absence of
  external-input routes, and the narrow development-only interpretation.
- Accounting principal `019fad1f-b288-7410-a7be-62f61e8e4a1f` and
  red-team principal `019fad1f-e820-77c2-881b-4d2a86da8d87` returned
  `REVISE`.
- The complete three-file Git delta, modes, hashes, 36 exclusions, image
  identity, empty physical inventories, and absent run directory all passed.

### Failure modes

- `RUNNER_BEFORE_TRUST`: the bootstrap streams the runner from arbitrary
  current HEAD before trusted code binds the reviewed runner hash and commit
  topology; replacement objects are not disabled.
- `AUTHORIZATION_SCHEMA_PARTIAL`: runtime checks accept schema subsets,
  wrong types, omitted authority fields, non-raw deltas, stale inventories,
  and principal-ID forgeries.
- `REMOVABLE_ONE_SHOT`: deleting the untracked run directory permits replay;
  worker mode does not require a durable launch claim.
- `PATH_REOPEN_TOCTOU`: the host runner and mounted input directory are
  reopened by mutable path after hashing.
- `UNOWNED_CONTAINER_REMOVAL`: a name race can cause cleanup to inspect and
  remove a foreign container; cleanup failure does not prevent a valid result.
- `MULTI_JSON_FALSE_PASS`: direct `jq -e` stream validation accepts extra JSON
  documents when the final document passes.
- `TIMEOUT_OOM_AMBIGUITY`: timeout diagnostics share untrusted stderr, timeout
  can mask OOM, and failed inspect/cleanup can coexist with a valid result.
- `STALE_OR_FAIL_OPEN_INVENTORY`: complete physical inventories are not
  rechecked before protected execution and the post-run pipeline lacks
  fail-closed traversal status.
- `INCOMPLETE_RESOURCE_EVIDENCE`: host `time` does not measure container CPU or
  peak memory, several configured limits are not runtime-attested, Docker logs
  can persist, and redirected host output is not hard-bounded.

### Strongest valid statement

The V2 container/test core is a useful design signal: it selects exactly the
five bound tests, disables ambient Python startup, requests a no-network
read-only Linux container, and preserves a development-only interpretation.
V2 as a whole does not authorize execution because its pre-execution trust,
one-shot, container-ownership, transcript, and accounting controls are
insufficient.

### Next concrete action

Create V3 with a hash-verifying bootstrap trust root, exact typed
decision/receipt validation, raw Git mode/topology checks with replacement
objects disabled, a committed consumption marker, stream-delivered
content-addressed inputs, container creation by returned ID, exact HostConfig
and cgroup/usage receipts, bounded host output, separate timeout diagnostics,
one-object canonical JSON validation, and mandatory inspect/cleanup success.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v2.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v2.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-container-runner-v2.py`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-review-v2.md`

No development-test or experiment-execution authority is granted.
