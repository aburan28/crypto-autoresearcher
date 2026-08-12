# EXP-SGCP-EMBED-002 source self-review v12

## Handoff: V12 invocation and publication boundary

### Claim or task

Check whether V12 closes the exact V11 invocation-state, legacy-control scope,
output-publication, internal-entry, and work-charge findings without widening
the mathematical claim or consuming a curve-row or run budget.

### Status

`OBSERVATION`; launch-plan design remains `NO-GO`. The underlying claim remains
`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

### Assumptions

- Context-local state protects ordinary concurrent and nested public verifier
  calls; it is not a hostile same-process Python sandbox.
- Repository tests intentionally inject the internal path sentinel through
  test-file introspection and produce no evidence-bearing report outside the
  public path API.
- On exFAT, no-overwrite publication is direct through an exclusive final
  descriptor. A successful return and complete self-hash are both required;
  an interrupted partial path is permanently unaccepted.
- The transient frozen B4/B6/B8 legacy rows reproduce predecessor semantics
  only. The separate frozen B4 density document remains the sole constructed
  density-row control.

### Evidence so far

- Producer and verifier emit schema/protocol V12. V1-V11 schemas reject without
  row verification.
- Module-global mutable accounting, reservation, and curve-cache dictionaries
  are gone. Every public path call installs a fresh `_VerificationState` in a
  `ContextVar` and restores the previous token on every return path.
- Two verifier threads synchronize inside graph reconstruction yet each returns
  the exact serial receipt. A nested verification inside outer factor-base
  reconstruction returns the serial receipt and leaves the outer receipt
  unchanged.
- All internal semantic entry points reject without the active identity-checked
  path permit. Public direct row APIs remain invalid and producer output helpers
  that used replace semantics were removed while producer execution is closed.
- Exact positive-integer checking occurs before every actual-work mutation.
  Boolean, zero, negative, float, string, and null controls leave the receipt
  unchanged.
- Output parents are traversed through no-follow directory descriptors.
  Existing and race-created destinations remain byte-for-byte unchanged;
  parent symlinks reject; unpublished temporary inodes are removed.
- The actual exFAT volume rejects hard links and exclusive rename. The
  descriptor-relative `O_EXCL` fallback succeeds, while an injected interrupted
  final write leaves an unaccepted partial path that a second call cannot
  overwrite.
- Exactly three transient legacy semantic controls are constructed, at B=4,6,8,
  and their digests are receipted separately from the frozen-B4 density
  document. No generated curve-family density row is constructed.
- The focused 71-test suite passes.
- All 14 scoped research records validate, and a freshly generated repository
  index matches `ledger.json` exactly.
- The repository suite passes 214 of 215 tests. Its sole failure is the
  preserved pre-existing SGCP-EMBED-001 immutable test-run directory guard, not
  a V12 assertion.
- The exact completed canonical provenance/predicate vector remains
  `480/112/336/218/4218`; all inherited finite semantic and accounting controls
  continue to pass.

### Failure modes

1. Same-process code with deliberate Python introspection can reach private
   objects; only an immutable external runner can bind executed code and roles.
2. An interrupted exFAT direct write can leave an incomplete visible path. It
   is fail-closed, not atomically invisible, and requires a fresh path for any
   retry.
3. The 256 MiB parser path still needs external CPU, wall-time, peak-RSS,
   allocator, parser-object, disk, I/O, cache-traffic, and memory-bandwidth
   receipts.
4. Canonical B6/B8 exact feasibility and the complete curve-family matrix remain
   unmeasured. The structurally distinct complete semantic oracle remains
   frozen-B4 only.
5. No current artifact supports relation generation, rank, linear algebra,
   target descent, preprocessing crossover, rho improvement, exponent, or
   ECDLP claims.

### Next concrete action

Freeze exact artifact hashes, commit V12, and obtain fresh read-only theory,
accounting, and red-team review. Keep `maximum_runs=0`.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v12.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v12.md`
- `experiments/EXP-SGCP-EMBED-002/source-self-review-v12.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
