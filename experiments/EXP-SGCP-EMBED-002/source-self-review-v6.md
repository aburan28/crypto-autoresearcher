# EXP-SGCP-EMBED-002 source self-review v6

## Task

Check whether the no-run V6 source and controls close the exact snapshot,
registered-scope, fail-fast, resource, receipt, oracle, and gate findings in the
V5 independent reviews without widening the mathematical claim or consuming a
curve-row/run budget.

## Status

`OBSERVATION`; underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

## Checks

- Producer and verifier emit only schema/protocol V6; the producer still rejects
  both CLI modes.
- V1-V5 schemas are rejected before row verification.
- Input admission reads one no-follow regular-file snapshot and hashes and
  parses the same bytes. Directory, symlink, changing-path, malformed JSON,
  duplicate-key, nonobject, and invalid-budget controls fail closed.
- Files are limited to 256 MiB; JSON is limited to 2,000,000 nodes, depth 64,
  and 8 MiB strings/keys.
- Direct row verification requires explicit `frozen_fixture` or `canonical`
  scope. The source-owned caps are exactly 100000 and 2000000 respectively.
- Only exact registered B values, curves, families, replicates, rows, caps, and
  order are admitted before curve or graph work. A `bits=40` mutation performs
  zero semantic curve calls.
- Invalid frozen documents with seven or twelve repeated rows perform zero row
  semantic calls.
- Row digest, protocol, validity, and ordering errors return before curve
  provenance.
- Worst-case curve draws, expansion, graph, replay, proof, replay caches,
  primary caches, retained-model calls, and retained-model cells are separately
  reserved before semantics. Per-cap and aggregate replay overbudget controls
  perform zero replay/row work.
- Receipts separate the reservation from actual replay, proof, and cache
  counters. Phase lists are emitted from actual control flow, and only passed
  phases populate `independent_checks`.
- The standalone frozen-B4 oracle follows no emitted curve, B, or cap value and
  calls no producer/verifier semantic helper. It matches every registered
  factor-base, representative, rejection, conflict, graph, selected-mask,
  formal-family, constrained-label, edge, source-table, digest, axiom, and
  cap-winner transcript.
- `[8,8,10,12]` distinguishes the registered multiset median 9 from an invalid
  deduplicated median 10. Exact `1/10`, three-strata, two-family, every-family,
  17/18, 18/24, two/three-strata, and cross-cap controls pass.
- The focused 41-test suite passes.
- No family row, canonical matrix, runner, launch plan, or execution artifact
  was created.

## Failure modes still open

1. The worst-case reservation proves a finite source-bound combinatorial
   envelope. It does not enforce wall time, peak RSS, disk, I/O, Python object
   overhead, memory traffic, process count, or CPU instructions.
2. Canonical B6/B8 exact feasibility, artifact size, and actual cache occupancy
   remain unmeasured. Hitting any future role limit is `INCONCLUSIVE`.
3. The document-local registered-curve cache is process memory, and its entry
   count is receipted; a future immutable runner must still prohibit
   unreceipted cross-role caches.
4. A final exception boundary converts an unexpected valid-input bug into an
   invalid receipt. Such an exception must be investigated before any result.
5. The standalone semantic oracle is complete only for frozen p=19, B=4,
   least-x. Canonical Mobius and hash-null derivations still rely on producer/
   verifier diversity plus focused provenance controls.
6. No relation generation, relation rank, linear algebra, target descent,
   fixed-curve preprocessing crossover, rho comparison, exponent, or ECDLP
   claim exists.

## Next action

Freeze the exact V6 snapshot and obtain fresh independent theory, accounting,
and red-team `GO` or `REVISE` decisions. Keep `maximum_runs=0`; do not design a
launch plan unless all three reviews explicitly authorize that separate step.

## Artifact paths

- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v6.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v6.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v6.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
