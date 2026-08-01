# EXP-SGCP-EMBED-002 V14 Revision Response

## Reviewed boundary

V14 responds to the three fresh exact-commit reviews of
`e44edde4231604abd76e481b7b4ed90359e42d09` and coordinator decision
`DEC-SGCP-EMBED-002-013`. Theory and accounting issued scoped GO; red team
issued `REVISE before launch-plan design`. No V13 review authorized a generated
row, canonical matrix, runner, launch plan, execution, or budget increase.

## Finding disposition

| V13 finding | V14 disposition |
|---|---|
| A receipt-commit syscall could succeed before the helper returned, leaving an accepted pair after a failed call | The receipt is attempt-bound. Once receipt publication begins, every ordinary synchronous exception is reconciled against the exact expected publication identifier and payload. A matching pair returns accepted with a structured warning; any other terminal state preserves the failure. Absolute guarantees for `BaseException`, process death, memory exhaustion, and hostile monkeypatching are removed. |
| A stale receipt could validate a retried identical payload | Both the data and deterministic receipt names are preflighted before data creation. A stale name blocks retry. The receipt also binds a random 256-bit publication identifier and development-root-relative destination path. |
| Concurrent calls could confuse failure attribution | Each call samples its own identifier. No-overwrite decides the winner, and exact-attempt reconciliation cannot accept the other call's receipt. A barrier-controlled same-destination test verifies one accepted identifier and one failed identifier. |
| A direct public writer could escape the development root through lexical `..` | `write_json_exclusive` now invokes `output_path` internally. Public status and receipt-path entries do the same, and `_open_output_parent` independently rejects empty and dot components before descriptor traversal. |
| Direct `O_EXCL` publication could warn on a definite inode type or size mismatch and still return accepted | An observed nonregular or wrong-size direct inode is a hard failure. Metadata-access failure may be recorded as a warning, but accepted return still requires exact final data/receipt validation. |
| The hard-link-success control did not call `os.link` | The control forces the production hard-link branch on a test-only hard-link-capable temporary root, wraps the real `os.link`, and observes both data and receipt link calls. Cleanup failure and post-receipt-link exception paths are controlled separately. |
| The independent receipt check reused production `publication_status` | A standalone test parser now implements its own duplicate-key rejection, exact types and keys, canonical JSON, self-digest, destination-relative-path, identifier, payload-size, and payload-hash checks without calling production status or canonicalization helpers. |
| V12 provenance named the wrong red-team artifact | `independent-review-provenance-v12-correction-v1.json` preserves the correct filename and matching artifact hash without modifying the original immutable record. |

## Publication protocol

Each write samples a 64-character lowercase hexadecimal publication identifier.
The canonical receipt binds:

- receipt schema, experiment, and protocol;
- publication identifier;
- exact destination basename;
- development-root-relative destination path;
- payload byte count and SHA-256;
- canonical receipt self-digest.

Before writing, descriptor-relative `lstat` semantics require both final names
to be absent. Data and receipt remain no-overwrite. The terminal validator uses
bounded no-follow regular-file snapshots, exact receipt types and keys,
canonical encoding, the receipt self-digest, and the payload binding.

The public status classes are:

- `absent`;
- `unaccepted_path`;
- `unaccepted_orphan`;
- `unaccepted_invalid_receipt`;
- `unaccepted_receipt_mismatch`;
- `unaccepted_attempt_mismatch` for exact-attempt reconciliation;
- `unaccepted_validation_error`;
- `accepted`.

The receipt is unkeyed. It is an accidental-state and controlled-workspace
integrity record, not hostile same-user authentication. Data and receipt
snapshots are sequential, not pair-atomic. Receipt visibility is a logical
content commit, not a durability certificate.

## Control independence

The mounted development volume may reject hard links. V14 therefore uses a
test-only temporary root to execute the real `os.link` path. This demonstrates
the branch state machine but makes no claim about hard-link support on the
mounted volume.

The standalone parser is intentionally test-local and structurally separate
from production status. It does not inherit production descriptor-walk code, so
its agreement is evidence for receipt semantics and canonical binding, not an
independent filesystem-race theorem.

## Claim and budget boundary

The curve grid, predicates, compiler, ordering digest, graph, cap schedule,
objective, family gate, and completed operation vector
`480/112/336/218/4218` are unchanged.

No relation yield, rank, linear algebra, target descent, fixed-curve
preprocessing crossover, rho improvement, fitted exponent, deployment result,
or ECDLP break is established. V14 remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

No generated V14 curve-family density row, canonical matrix, runner, launch
plan, or run is authorized. `maximum_runs=0`.
