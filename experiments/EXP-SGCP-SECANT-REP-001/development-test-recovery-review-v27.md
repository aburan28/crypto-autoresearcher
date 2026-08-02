# V27 Recovery Review

## Handoff: V27 consumed recovery ends in a serialization precondition failure

### Claim or task

Preserve the exact terminal outcome of the one authorized V27 recovery
invocation without retrying it or promoting it into ECDLP evidence.

### Status

NEGATIVE RESULT

### Assumptions

- Exact Git object and direct-ref semantics are trusted.
- The recorded host exit code and preserved recovery-directory artifacts are
  the evidence basis.
- Protected source/test semantics remain outside this review.

### Evidence so far

- Protocol P:
  `480570b3a80db4668e016ad2cdc2505312fbdda4`
- Protocol tree:
  `4cea0fc6d4bce60e38b67b1d71a44476066e6eb2`
- Authorization A:
  `1279e9a08065b72a261f4cb0453a428d494f15c5`
- Authorization tree:
  `569dc837417242549b9faff0e84ea6896ddb6330`
- Recovery consumption C:
  `b872486b0057dfd425b255618d6a738266e9b2d7`
- Recovery C tree:
  `54dbfec6bf2139a44824936a87a78a0e057226b4`
- C has sole parent A and records `maximum_runs_remaining: 0`.
- The exact instantiated bootstrap was 3,411 bytes with SHA-256
  `155f6d3a810b969a46c1f5399930893b0e45bc705cffeecdaf0410a9b75b267a`.
- The one invocation returned exit code 70 after approximately 2.7 seconds
  with no stdout.
- The committed shell-control replay byte-matched SHA-256
  `972ab93497f0cabe49b8d6532036a52af8695ce372e7cdaf99ae8914554e9a65`.
- Authorization validation was exactly `true`.
- The current 53-file source inventory byte-matched the exact expected
  manifest inventory.
- Fresh container-absence checks returned exit code 1 with exact empty-array
  stdout for both container ID and name.
- The V27 recovery result ref is absent.
- The original V23 result ref remains absent.
- `recovery-seal.json`, `recovery-validation.txt`,
  `result-tree-spec.txt`, and `recovery-result-commit-sha1.txt` are absent.

### Failure mode

`build_and_validate_seal` requires each source JSON input to be byte-identical
to canonical `jq -cS` output before semantic validation. The immutable
`docker-inspect-pre.json` parses successfully as JSON but is pretty-formatted,
so the first Docker-inspect canonical-byte predicate returns false. The
post-inspect artifact has the same formatting mismatch, but the host stopped
at the pre-inspect predicate.

This is a protocol precondition defect. It is not evidence against the V23
fixed public tests, the mathematical hypothesis, index calculus, or prime-field
ECDLP. No recovered seal was produced.

### Failure modes

- Recovery authority is consumed and must never be retried.
- A V28 successor must not attempt to recover this same V23 run.
- The preserved recovery directory is incomplete by design and must not be
  interpreted as a valid result package.
- Valid JSON and canonical JSON bytes were incorrectly conflated for immutable
  Docker receipts.

### Reusable lesson

Future one-shot protocols must either bind canonical serialization as an input
property before authorization or parse valid immutable JSON and apply semantic
validation without requiring byte canonicality. Every precondition over
consumed source artifacts needs a pre-authorization compatibility receipt.

### Next concrete action

Return to the live ECDLP research track and apply the compatibility-receipt
lesson to future controlled experiments; preserve V27 C, the absent result
refs, and this terminal negative result.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/RECOVERY-SGCP-SECANT-V23-V27/`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-protocol-v27.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-decision-v27.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-review-v27.md`
