## Handoff: SGCP implementation source red-team v1

### Claim or task

Determine whether the version-3a five-bit builder and verifier were ready for
source freeze and canonical preflight execution.

### Status

NEGATIVE RESULT, REVISE. Canonical execution remains unauthorized.

### Assumptions

- Review covered the dirty development worktree before any canonical output.
- Findings concern implementation and certificate integrity, not the SGCP
  mathematical hypothesis or prime-field ECDLP.
- The reviewer made no file changes.

### Evidence so far

- The focused 14-test suite passed before adversarial probes.
- The existing witness, star-edge, placeholder, and digest mutations were
  rejected.
- A caller-selected `README.md` contract, with matching self-recorded hash,
  passed the verifier.
- Perturbing verifier scalar ground truth made all P2 scalar checks false but
  left overall `valid=true`.
- Builder and verifier output guards accepted source, registry, and contract
  paths as overwrite targets.
- Zeroed operation counters, unit memory/time values, and scalar material
  appended to `command_argv` passed verification.

### Failure modes

1. HIGH: the mathematical and experiment contract paths and hashes were not
   pinned independently in builder and verifier.
2. HIGH: independently computed scalar compatibility was report metadata, not
   a validity gate.
3. HIGH: outputs were permitted anywhere in the worktree and could overwrite
   protected inputs or sources; cwd, branch, and dirty-state policy was absent.
4. HIGH: execution and resource receipts were excluded from the deterministic
   digest and only weakly validated; unknown argv tokens were accepted.
5. HIGH: exact comparison relied on builder-shaped serializer logic instead of
   a separately checked semantic intermediate representation. The two verifier
   density serializers already disagreed on the nonidentity denominator.
6. MEDIUM: source records, schema placement, and required byte/diagnostic
   metrics did not literally match contract v3a.
7. MEDIUM: optimizer outcome rows were hashed in integer-mask order rather than
   the contracted lexicographic subset order.

The reviewer found no omitted five-bit subset in the current exhaustive
enumeration. That does not cure the proof-object ordering or independence
defects.

### Required repairs

- Pin exact paths and hashes for both contracts, literature, and controls.
- Gate validity on every applicable scalar check and a pinned scalar-table
  digest.
- Restrict outputs to exact preflight filenames, reject existing/protected
  paths, and bind cwd, branch, commit, and dirty-tree policy.
- Reject unknown argv material and make every receipt field independently
  checkable or explicitly diagnostic and non-attested.
- Establish a semantic verifier oracle before builder-compatible serialization
  and differentially test every row.
- Reconcile source records, certificate layout, metric fields, and density
  denominator with the version-3a contract.
- Sort optimizer outcome rows by the specified subset order before hashing.

### Next concrete action

Implement a versioned source repair and rerun the exact false-pass probes plus
the focused and repository-wide suites, then request a fresh read-only source
red-team review.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/control-registry-v2.json`
- `experiments/EXP-SGCP-EMBED-001/contract.md`
- `notes/sgcp_embed_001_contract_20260717.md`
- `tests/test_sgcp_embed.py`
