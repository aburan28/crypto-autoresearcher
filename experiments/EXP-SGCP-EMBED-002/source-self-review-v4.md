# EXP-SGCP-EMBED-002 source self-review v4

## Handoff: coordinator pre-independent audit

### Claim or task

Check whether the no-run V4 source and tests implement the repairs required by
`decision-v3.json` closely enough to justify fresh independent review.

### Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, `NOVELTY-UNVERIFIED`, and
`review_required`. This is not independent GO.

### Assumptions

- Dynamic evidence is restricted to unit, abstract, provenance, factor-base,
  synthetic-envelope, and frozen `p=19` controls.
- No generated family row or canonical matrix was created.
- Hashes and commands are recorded in `development-test-log-v4.md`.

### Evidence so far

#### Provenance and ordering

- Duplicate candidates now retain duplicate and mathematical reasons; producer
  and verifier derive their lists independently.
- The emitted ordering contract freezes factor-point and formal indices, EC
  point order, point labels, predicate ties, hash encoding, alternation, and
  representative selection.
- The representative compiler identifier is V2 because ordering is now part of
  its public contract.

#### Exact schemas

- V4 document and row schemas close nested keys before reconstruction.
- Exact type validation covers curve transcripts, factor records, formal and
  point records, public edges and sources, graph transcripts, optimizer and
  frontier receipts, ratios, expansion histograms, structural work, wall
  times, byte receipts, parameters, summaries, and top-level identities.
- Type-aware equality replaces permissive Python equality on reconstructed
  structured objects.
- The focused mutation matrix rejects Boolean/integer/float aliases after
  enclosing receipts are refreshed.

#### Optimization and canonical envelope

- Producer and verifier gate helpers enforce the full authenticated exhausted
  state before evaluating any family statistic.
- The independent canonical matrix auditor checks exact row order, cap
  schedules and associations, curve consistency, cross-seed uniqueness, node
  caps, and all cap exactness fields.
- A direct exhaustive oracle checks the complete objective and lexical witness
  for every independent frozen B=4 subset and all four caps without invoking
  the optimizer or deterministic replay.

#### Interpretation and accounting

- Mathematical falsification now requires a complete valid exact matrix.
- Implementation, provenance, type, control, scalar, resource, and verifier
  failures are invalid evidence and `INCONCLUSIVE`.
- The V3 accounting boundary is unchanged: structural cells are not operation
  totals, nested byte measures are nonadditive, wall times are observational,
  and future generator/verifier resources must be charged separately.

### Failure modes

1. The canonical 672-cell feasibility question remains unmeasured because V4
   authorizes zero family rows.
2. The third oracle is exhaustive only on frozen B=4; future larger graphs need
   a reviewed independent proof strategy and explicit verifier budget.
3. Producer and verifier still share the mathematical definition of retained
   models even though their EC, search, transcript, and exhaustive paths are
   separately implemented.
4. A future runner must bind the exact V4 schema, source hashes, command,
   environment, row count, cell count, role resources, retries, isolation,
   output ceilings, and claim boundary. No such plan exists yet.
5. The finite effect may be compiler-specific and cannot imply an exponent or
   attack path.

### Next concrete action

Commit the exact V4 snapshot, then request fresh read-only theory, accounting,
and red-team `GO` or `REVISE` decisions. Keep `maximum_runs=0` and do not design
a launch adapter unless all three reviews explicitly authorize plan design.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v4.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v4.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v4.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
