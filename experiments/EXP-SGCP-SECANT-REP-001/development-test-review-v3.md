# Development-Test Execution Review V3

## Handoff: durable consumption with incomplete pre-trust neutralization

### Claim or task

Determine whether V3 safely authorizes exactly one immutable, isolated run of
the five hash-bound public development tests under its explicit trusted-local
model.

### Status

NEGATIVE RESULT

### Assumptions

- Static review at the exact committed V3 target.
- Protected source/tests were inspected only as plain text.
- No protected source/test was parsed by a tool, imported, compiled, tested,
  or executed; no V3 repository runner was invoked.
- Inert Docker and Git probes contained no protected input.

### Evidence so far

- Reviewed commit:
  `2f98f853ee1db7f9d68aa082cc33ce66a29483ee`.
- Reviewed tree:
  `04f813f98b35339e8f3deab858c1200b674d021f`.
- Sole parent:
  `c2048512ae6d151e532eff41bfd13de5a77316da`.
- Protocol SHA-256:
  `01524b0fccd65ec2a01aac1eefb985687120d6d16550d14c504baf055d8ea554`.
- Host-runner SHA-256:
  `a677db9fa280d7ff9b75f2e4fffa166d19ced8d1cbd54d7a9c73772ed4398892`.
- Authorization-validator SHA-256:
  `417f432e089ad9247b23977e2f5bc10a904317f60c9ad117c30d29396b23d81e`.
- Container-runner SHA-256:
  `8ab5ae9c6495a430badcb803956cca1a02593a510a0b1def5e2c5d065d3e5cf5`.
- Theory principal `019fad42-6d1f-7340-ab5a-c8be2ed072da` returned
  scoped `GO`.
- Accounting principal `a6ee6cd6-0096-45c5-bf62-c4f1bb4ac1f7` and
  red-team principal `0429e651-0480-4ffe-987b-be7bcc223f68` returned
  `REVISE`.
- Git identity, four-file modes/delta, hashes, tools/image, current
  inventories, durable marker-before-Docker ordering, archive stream,
  one-document validator, timeout/OOM separation, and exact-ID cleanup design
  otherwise passed.

### Failure modes

- `PRETRUST_FSMONITOR_EXECUTION`: bootstrap and host cleanliness checks do not
  override repository-local `core.fsmonitor`, allowing configured code to run
  before the host runner is trusted.
- `PRECLAIM_FIND_STATUS_DROPPED`: command substitution tests empty output but
  discards `find` failure status.
- `PRINCIPAL_AUTHENTICITY_OVERSTATED`: the validator proves UUID syntax,
  exclusion absence, and distinction, not orchestrator authenticity; receipt
  authenticity remains a trusted external assumption.
- `CONTAINER_COMMAND_UNBOUND`: inspect validation omits exact `Config.Cmd`,
  runtime, and OOM-policy fields.
- `FRACTIONAL_COUNTERS_ACCEPTED`: JSON number/range checks do not require
  integral cgroup counters.
- `NONDETERMINISTIC_ENV_ORDER`: exact positional `Config.Env` comparison
  rejects valid containers because Docker returns override order
  nondeterministically.
- `PRESTART_REJECTION_LEAK`: full HostConfig rejection after `docker create`
  bypasses cleanup of the returned exact ID.
- `LINKED_WORKTREE_METADATA_UNDERCOUNTED`: declared `.git` paths do not resolve
  the actual worktree gitdir/common-dir writes, lock files, reflogs, and
  `COMMIT_EDITMSG`.
- `PIPELINE_STATUS_NOT_REQUIRED`: writing the three pipeline statuses is
  unchecked and valid-result logic does not require their exact contents.
- `TERMINAL_TIMEOUT_SCOPE_NARROW`: the 180-second limit covers the protected
  archive/attach pipeline, not every Git/Docker setup and cleanup operation.

### Strongest valid statement

V3 establishes useful restricted design results: runner bytes are hash-checked
before execution, authorization is exactly typed, a marker-only Git commit can
consume the run before protected execution, inputs can be streamed without a
host mount, containers can be owned by returned ID, and valid output can be
restricted to one canonical JSON value. V3 as a whole remains unauthorized
because pre-trust Git configuration, inventory failure, deterministic inspect,
cleanup, and evidence-accounting controls are incomplete.

### Next concrete action

Create V4 using config-neutralized bounded Git commands and plumbing-only
marker construction, fail-closed inventory status, externally trusted receipt
authenticity wording, exact `Config.Cmd` and security projection, exact
environment multiset/cardinality, integer resource counters, immediate
returned-ID cleanup finalization, linked-worktree physical metadata paths,
mandatory pipeline status validation, final inventories, and a complete
artifact checksum manifest.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v3.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v3.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-authorization-validator-v3.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-container-runner-v3.py`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-review-v3.md`

No development-test or experiment-execution authority is granted.
