## Handoff: SGCP V7 exact-commit adversarial review

### Claim or task

Determine whether commit `fe093d3d80bba38e729fd8c98f78bed569e5087d`
is ready for launch-plan design only.

### Status

`NEGATIVE RESULT` for V7 launch-plan-design readiness. The mathematical
hypothesis remains `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and
`NOVELTY-UNVERIFIED`.

Decision: `REVISE`. No execution, runner, density row, plan, or budget change
is authorized.

### Assumptions

- Review was read-only and confined to exact commit content.
- Unrelated worktree state was ignored.
- Tests and canonical work were not executed.
- POSIX `O_NOFOLLOW`, `O_NONBLOCK`, `fstat`, and regular-file semantics are
  assumed.
- Public direct-call entry points count as verifier surface because the
  contract claims direct row verification requires registered scope.
- Rank, relation yield, linear algebra, target descent, rho comparison, and
  cryptographic scaling remain outside this design review.

### Evidence so far

- Final-component symlinks, FIFOs, directories, and initially oversized sparse
  files are rejected before reading; parent symlink traversal is explicitly
  allowed and disclosed.
- Input hashing and parsing use the same captured bytes.
- Mask text is length-checked before integer conversion.
- The source hash is correctly labeled diagnostic-only, not execution
  attestation.
- Producer CLI family-row and canonical modes remain disabled.
- Tests construct one frozen p=19 density row; generated controls stop at
  curve/factor-base scope.
- The legacy document router rejects V1-V6 without row verification.
- The claim boundary excludes exponent, rank, descent, and ECDLP conclusions.
- All nine hashes in `development-test-log-v7.md` match the corresponding
  `fe093d3` blob bytes. This authenticates committed content only; it does not
  independently authenticate the logged test execution.

### Findings

1. `HIGH`: the public legacy row entry point bypasses the claimed registered-
   scope boundary. `verify_row(row, maximum_nodes)` accepts no scope and calls
   `_verify_legacy_row_unchecked`. A bad row digest appends an error but then
   continues into attacker-selected curve construction, point enumeration,
   graph work, and primary proof. A huge type-correct prime candidate can
   therefore enter trial-division work before fail-fast rejection.
2. `HIGH`: the document schema is not closed at `family_gate`, and late-invalid
   data can consume every proof. The gate is initially checked only as a
   dictionary. A re-digested frozen document with an extra gate field can pass
   scope, row preflight, reservation, and all four proof cells before late
   rejection; the canonical case can reach all 672 cells. Wrong summary values
   and nested source/edge digests are also rejected after avoidable work.
3. `HIGH`: a successful V7 receipt undercounts density-primary point
   enumeration while claiming complete work. The exact-count test checks only
   actual less than or equal to reservation. Frozen enumeration is recorded
   under a differently named field than its reservation, leaving no exact
   mapping.
4. `HIGH`: phase and exception receipts are not globally truthful. A global
   phase can be marked passed after an early cap even when later caps never
   run. Mid-function replay/proof exceptions can report zero failing-cap nodes
   and cache entries after nonzero work, while retained-model cells are charged
   before all cells execute.
5. `HIGH`: diagnostic and report limits are bypassable. Input
   `document_sha256` is reflected before exact type validation; a legacy or V7
   type failure can place a large object in the report. Diagnostic totals cover
   only top-level errors, not nested row/cap errors. Unexpected-key sampling
   sorts the full set before slicing the bounded sample.
6. `MEDIUM`: pre-reservation validation remains amplifiable. Shape validation
   materializes entries for full collections before B-derived bounds reject
   them. Selected maxima are converted, deduplicated, and sorted before their
   B-derived limit; nonempty frontiers are traversed before the exact-empty
   check. Existing controls do not approach the global node/file ceilings.
7. `MEDIUM`: candidate/eligible independence is narrower than readiness prose
   suggests. The complete standalone comparison is a frozen-B4 regression;
   B6/B8 rely on structurally similar producer and verifier implementations.
8. `MEDIUM`: structural reservation is not a memory model. At the admitted
   primary-node budget, cache-entry counts are not converted to allocator bytes
   or enforced RSS. The reservation is not evidence that a proposed four-GiB
   role is feasible.

### Overclaim corrections

- Closed exact schema is unsupported until `family_gate` and every receipt
  field are closed and bounded.
- Verifier entry-point totality does not include the unrestricted legacy direct
  API, pre-reservation amplification, parser/OOM paths, or reflected values.
- Completed phase/work claims require exact point counts, cap-scoped phase
  semantics, and explicit interrupted-work lower bounds.
- SHA-256 fields provide deterministic integrity checks, not origin, commit,
  command, dependency, or executed-code authentication.
- Complete candidate/eligible independence means frozen-B4 standalone-versus-
  verifier regression only.

### Required controls

- Disable or frozen-scope the legacy direct row API and prove rejected legacy
  rows invoke zero curve, graph, replay, or proof helpers.
- Close and bound `family_gate`; preflight summary/gate consistency and nested
  table digests before expensive semantics.
- Assert exact actual-to-reservation mappings, charge every point enumeration,
  and require nonzero counts when corresponding phases execute.
- Make phases row/cap scoped or mark aggregate phases passed only after every
  registered cell completes.
- Represent interrupted counters as lower bounds/unknowns and inject failures
  after nonzero replay/proof work.
- Sanitize `input_document_sha256`, recursively account diagnostics, and cap
  total serialized invalid-report size.
- Length-check collections before traversal/canonicalization and test near-
  ceiling collections and digest values.
- Preserve source-hash diagnostic labeling and the zero-run,
  zero-generated-density-row boundary.

### Next concrete action

Prepare one no-run V8 repair commit closing findings 1-6 and containing the
falsification controls above; keep `maximum_runs=0` and launch-plan design
locked.

### Artifact paths

- `fe093d3:experiments/EXP-SGCP-EMBED-002/contract.md`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/specification.json`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/protocol-amendment-v7.json`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/development-test-log-v7.md`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/source-self-review-v7.md`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `fe093d3:experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `fe093d3:tests/test_sgcp_embed_family.py`

