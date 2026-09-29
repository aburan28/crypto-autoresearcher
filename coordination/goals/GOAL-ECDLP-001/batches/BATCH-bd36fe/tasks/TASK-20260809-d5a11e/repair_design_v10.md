# BATCH-bd36fe v10 control-plane repair

This is a superseding, design-only repair for the four blocking findings in
the independent v9 freeze review TASK-20260809-369268. It is synthetic
control-plane work only. It does not implement an ECDLP method, specify an
experiment, approve a run, admit an Executor, create evidence, or change
research status.

## Findings addressed

1. The v9 validator's nested v8 subprocess uses `sys.executable`, absolute
   paths, and an absolute repository root. v10 treats that nested call as
   non-authoritative and runs the archived v8 validator independently using
   the exact archived canonical argv, with `python3`, repository-relative
   paths, and `--repo-root .`. The v10 contract and metadata bind that exact
   argv byte-for-byte.
2. v10 compares accepted-case path strings before any `Path` normalization.
   The only accepted spelling is exactly `<fixture_id>.json`; `./` prefixes,
   absolute paths, traversal components, and alternate spellings fail.
3. v10 binds the six-case map to the immutable v8 manifest bytes and requires
   exact list equality, six unique fixture IDs, six unique canonical paths,
   and complete expected coverage. Mutating both v10 map copies to six
   duplicate entries therefore fails.
4. v10 binds `case_authority.fixture_root` to the exact canonical v6 fixture
   root string and rejects absolute or relocated roots before joining paths.

## Predecessor architecture

The v9 package remains immutable and is hash-bound to snapshot commit
`2513b4e7b15ac4ec343fe2622903a47667ba39ce`, parent
`efe31d0812484370f8804644f273f76ed885e1f7`. v10 verifies every v9 source
artifact hash, runs the exact v9 command as a legacy predecessor check, then
replays the v9 strict fixture checks without treating v9's non-canonical
nested v8 subprocess as authoritative. It separately runs the exact archived
v8 canonical command and requires `VALIDATION_PASS`. This makes the v10-owned
v8 invocation the authoritative predecessor witness while preserving the
immutable v9 result.

## Required controls

- Actual v10 `sys.argv` must equal the canonical metadata argv before parsing
  or loading inputs.
- The v9 and v8 command arrays used by subprocesses must equal their archived
  canonical metadata arrays exactly; their working directory must be the
  repository root.
- v9 root, contract, manifest, metadata, and all v9 artifact bytes must match
  the archived snapshot bindings.
- The canonical v6 fixture root and the exact six-case map must be bound to
  immutable v8 manifest content.
- Every accepted-case mutation is applied in memory and must be rejected.
- All inherited validators remain fixture-only and no-run.

## Claim ceiling

Passing this validator is evidence only that synthetic provenance controls
reject the declared and fresh mutations. It is not ECDLP evidence, a
cryptographic result, a cost result, a security claim, or authorization to
run an experiment.
