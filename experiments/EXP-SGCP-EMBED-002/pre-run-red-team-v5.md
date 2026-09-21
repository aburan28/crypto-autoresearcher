## Handoff: SGCP V5 exact-commit adversarial audit

### Claim or task

Review only commit `606daf8fee72979403915d23011f987f01007b74` for
EXP-SGCP-EMBED-002 V5 verifier totality, routing, receipt truthfulness,
resource enforcement, oracle independence, and gate-boundary correctness.

### Status

`OBSERVATION`; the underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

Recommendation: `REVISE`. Launch-plan design and execution remain `NO-GO`, and
`maximum_runs=0` remains in force.

### Assumptions

- The review used only committed blobs at the exact requested commit.
- Mutation probes were verifier-only and created no registered family rows,
  canonical matrix, runner, plan, or execution artifact.
- A valid receipt must hash the same immutable bytes it parsed.
- Receipt phase claims must report actual control flow, not a static list of
  checks the route might have performed.
- Bounded JSON is not a sufficient verifier-work bound.

### Evidence so far

- All nine committed V5 hashes match the development log.
- The zero-run governance boundary, disabled producer CLI, V1-V4 rejection,
  exception classification, frozen B4 control, exact-type mutations, and
  existing gate arithmetic behaved as documented.
- The standalone B4 oracle contains no imports or references to producer or
  verifier semantic helpers.
- Existing invalid current-schema and legacy mutations return stable invalid
  receipts in the committed focused suite.
- No family row, canonical matrix, runner, launch plan, or execution
  authorization exists.

### Failure modes

#### Blocking: parsed bytes and receipted bytes can differ

`strict_load` parses one read of the input path, while `verify_document`
reopens the path to compute `input_file_sha256`. In a changing-file probe, the
verifier returned `valid=true` after parsing byte sequence A while the receipt
reported the digest of later byte sequence B. A hash-complete plan cannot bind
that receipt to the verified object.

#### Blocking: bounded input can trigger unbounded pre-primary work

Curve `bits` is not restricted to the registered grid before prime-list
construction. A digest-refreshed current-schema input with `bits=40` and
`draw=0` passes envelope parsing and enters an enormous prime enumeration.
Likewise, the generic B=64 ceiling permits combinatorial degree-eight
expansion far beyond a practical verifier budget.

#### Blocking: known-invalid envelopes still execute row semantics

Document-envelope errors are accumulated while every row is still verified.
An invalid seven-row frozen document invoked row verification seven times.
The measured path scaled from about 0.031 seconds for one row to about 0.369
seconds for twelve rows. Invalid scope, grid, curve, B, cap, or row association
must fail before graph construction, replay, or independent proof.

#### High: static receipt phase lists overclaim execution

- With an invalid verifier node budget, `strict_load` was called zero times but
  the receipt still claimed bounded strict JSON parsing.
- With an extra V5 document key, exact-type validation was not reached but the
  receipt still claimed schema and exact-type checks.

The receipt needs an actual phase ledger derived from control flow.

#### High: resource ceilings are not role budgets

- An input-controlled optimizer cap can request up to 100 million nodes for
  each cap independently of the trusted verifier proof budget.
- One-GiB input and ten-million-node parser ceilings do not enforce peak RSS.
- Nonregular or changing files defeat the current file-size and hash intent.
- Replay, proof, structural expansion, graph, and cache work lack aggregate
  trusted budgets.

#### Medium: one gate fixture is nondiscriminating

The duplicate-null fixture `[8,10,10,12]` has median 10 both before and after
deduplication. `[8,8,10,12]` distinguishes the registered median 9 from an
incorrect deduplicated median 10.

#### Medium: the standalone oracle follows untrusted envelope values

The oracle trusts emitted curve metadata, B, and cap schedule, and compares
aggregate graph summaries rather than full candidate, edge,
constrained-label, and source transcripts. A frozen oracle should derive the
registered p=19, B4, factor base, and cap schedule independently.

### Next concrete action

Implement V6 with a single regular-file read whose exact bytes are size-bound,
hashed, decoded, and parsed once; reject every invalid registered-envelope or
matrix association before row math; enforce trusted cumulative expansion,
replay, proof, graph, and cache limits; derive receipt phases from actual
control flow; and add changing-file, special-file, huge-bits,
duplicate-amplification, replay-budget, discriminating-median, exact-ratio,
strata, and all-family-collapse regressions.

### Artifact paths

- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/contract.md`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/specification.json`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/protocol-amendment-v5.json`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `606daf8fee72979403915d23011f987f01007b74:experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `606daf8fee72979403915d23011f987f01007b74:tests/test_sgcp_embed_family.py`

Final recommendation: **REVISE. Launch-plan design and execution remain
NO-GO.**
