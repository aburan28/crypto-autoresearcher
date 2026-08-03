# Development-Test Execution Review V1

## Handoff: ambient macOS runner rejection

### Claim or task

Determine whether execution protocol V1 may authorize exactly one bounded run
of the five hash-bound public development tests.

### Status

NEGATIVE RESULT

### Assumptions

- Trusted-local static review of the protocol and plain-text source/test surface.
- No protected source or test was parsed by a tool, imported, compiled,
  analyzed, formatted, tested, or executed.
- The result concerns the V1 macOS runner, not the mathematical core or tests.

### Evidence so far

- Reviewed commit:
  `be238efa46a1578a0d863b5e3b188d1b88a61f44`.
- Reviewed tree:
  `4d0afd913bbf1a2a2866e7afae9e698857e0ffb8`.
- Sole parent:
  `4c24c1fb986190631a7015431c07cf829bbde88f`.
- Protocol SHA-256:
  `def603a7d9e6fd885d3c16312f63882f98a8d15a1bf88aa42668a841957745af`.
- Runner-script SHA-256:
  `5b79fefb8250b5b196c32d499f4d8ec33f708112443d86fc841c9684962a6488`.
- Protected-source SHA-256:
  `8b8781d688188afa41e87f33e15a306fc5a9f5326b8e93316247263ee8f933bd`.
- Test-source SHA-256:
  `2b0e34524f22cf5d2dd70c3eff857b186c10c9d8882bb2893999febc1352417a`.
- Theory principal `019fad01-09aa-7031-bff9-9ec16b12e896`,
  accounting principal `019fad01-0a29-7202-abe0-8d054f75dc85`, and
  red-team principal `019fad01-0a91-7ce2-8658-6d9d09de04ff` each returned
  `REVISE`.
- The exact `ulimit -v 1048576` operation failed on the bound macOS host with
  `setrlimit failed: invalid argument`, leaving virtual memory unlimited.
- A harmless timeout probe demonstrated that `gtimeout --preserve-status`
  can return zero after a timeout.
- The bound Python installation contains executable `.pth` startup imports
  outside the protocol's hash-bound surface.
- The run directory remained absent and the checkout remained clean.

### Failure modes

- `ADDRESS_SPACE_LIMIT_NOT_ENFORCED`: the failed macOS virtual-memory limit
  did not stop the runner.
- `AMBIENT_PYTHON_STARTUP`: `-B` still permits mutable `.pth` and site-startup
  code; omission of `-P` also leaves an avoidable import-shadow route.
- `TIMEOUT_STATUS_AMBIGUOUS`: `--preserve-status` does not provide an
  independent timeout fact.
- `ONE_SHOT_NOT_ATOMIC`: a separate existence check followed by `mkdir -p`
  permits concurrent claims and does not reject every symlink case.
- `FAILURE_RECEIPT_UNDEFINED`: the success-only receipt cannot preserve test
  failure, timeout, preflight failure, or infrastructure failure even though
  every attempted authorization must be consumed.
- `RUNTIME_IDENTITY_NOT_ATTESTED`: the runner does not recheck the bound
  commit, decision, source/test hashes, runtime image, and import origin at
  launch.
- `ACCOUNTING_INCOMPLETE`: timestamps and full-wrapper resource use are not
  retained, and the post-run receipt lacks explicit write authority.
- `TRANSCRIPT_GATE_TOO_WEAK`: required substrings do not prove that exactly
  five named unittest records completed successfully.

### Strongest valid statement

V1 does not safely authorize a resource-bounded, hermetic development test on
this macOS host. This is a negative result for the runner contract only. It
does not weaken the static V22 source/test review, and it provides no ECDLP
performance or scaling evidence.

### Next concrete action

Replace V1 with a Linux-container protocol bound to an immutable image digest,
cgroup limits, no network, read-only inputs, `python -I -S -P`, atomic output
acquisition, immediate identity checks, exact transcript validation, explicit
timestamps and whole-wrapper accounting, and receipts for every terminal
outcome; obtain three fresh reviews before any protected execution.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v1.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-review-v1.md`

No development-test or experiment-execution authority is granted.
