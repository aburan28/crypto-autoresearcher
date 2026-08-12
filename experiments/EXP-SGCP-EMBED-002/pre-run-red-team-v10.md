# EXP-SGCP-EMBED-002 pre-run red-team review v10

## Findings

### HIGH: deterministic provenance and predicate counters lack completed equality

The reservation admits large upper bounds for registered prime candidates,
curve draws, curve hashes, curve point enumerations, and predicate hashes, but
completed-path equality does not independently derive these five counters from
the authenticated curve and factor-base transcripts. Suppression or an
overcharge below the reservation can therefore leave a completed report valid.

Evidence:

- `src/verify_sgcp_embed_family.py:5780` reserves generated-curve work from
  worst-case draw bounds.
- `src/verify_sgcp_embed_family.py:5967` exact-checks selected cache and point-
  enumeration counters but omits the five deterministic provenance/predicate
  dimensions.

Required repair: derive exact completed counts from authenticated transcripts
and add suppress-one and overcharge-one controls for every omitted counter.

### MEDIUM: pre-parse input amplification remains large

The verifier admits up to 256 MiB, accumulates the file into a block list,
joins it, decodes another full ASCII string, and only then applies generic JSON
node, depth, and string bounds. A future plan needs hard external CPU/RSS
containment and either a substantially tighter input ceiling or a bounded
streaming/pre-parse structural path with near-limit controls.

Evidence:

- `src/verify_sgcp_embed_family.py:602` accumulates input blocks.
- `src/verify_sgcp_embed_family.py:581` decodes before standard JSON parsing.

## Handoff: V10 exact-commit red-team review

### Claim or task

Try to falsify launch-plan-design readiness for exact commit
`3af44e847392c4c7e258ef60d0bf3e5dc01daa43`.

### Status

`NEGATIVE RESULT` for V10 plan-design readiness. The mathematical hypothesis
remains open and unchanged.

### Assumptions

- All nine test-log hashes match exact Git blobs.
- The review authorizes neither generated rows nor execution.
- `maximum_runs=0` remains binding.

### Evidence so far

- The public legacy producer and the four completed graph/expansion equality
  checks close the V9 findings.
- Five other deterministic generated-work counters remain suppressible or
  overchargeable below their upper bounds.
- Parser allocation is acknowledged as external, but the current 256 MiB
  pre-parse path still creates a concrete launch-planning risk.

### Failure modes

- A completed receipt can understate or overstate deterministic provenance work.
- A near-limit input can multiply memory before structural rejection.
- External-resource language without an executable containment design is not a
  resource guarantee.

### Next concrete action

Implement exact completed equality for all five omitted counters, add suppress
and overcharge controls, and close the parser amplification boundary before
fresh exact-commit review.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/development-test-log-v10.md`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `git:3af44e847392c4c7e258ef60d0bf3e5dc01daa43`

## Verdict

`REVISE` for launch-plan design. Execution is not authorized.
