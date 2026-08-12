# EXP-SGCP-EMBED-002 V13 Revision Response

## Reviewed boundary

V13 responds to the three fresh exact-commit reviews of
`9c170f70d6f4b7aafc20b5adfe70f22a702b5d8b` and coordinator decision
`DEC-SGCP-EMBED-002-012`. Theory and accounting issued scoped GO; red team
issued `REVISE before launch-plan design`. No V12 review authorized a generated
row, canonical matrix, runner, launch plan, execution, or budget increase.

## Finding disposition

| V12 finding | V13 disposition |
|---|---|
| A final destination could appear before a failed post-publication directory fsync or hard-link temporary cleanup | Output acceptance now requires a separate canonical completion receipt. The data path alone is an unaccepted orphan. Once the complete receipt reaches its content commit point, later cleanup, fsync, stat, or close errors are structured warnings and cannot change the call into a contradictory failure. |
| Hard-link publication could succeed before temporary-name unlink failed | The no-replace primitive reports whether temporary cleanup remains. Cleanup failure is retained in the publication warning vector; data and receipt publication continue, and exact receipt validation determines acceptance. |
| The committed record did not substantiate the stated real-exFAT observations | V13 describes only forced `ENOTSUP` controls. It makes no claim that an actual filesystem returned a particular error or supports a particular primitive. |
| Exceptional public-state restoration was untested | An injected escaping worker exception must close the inner state and restore the exact outer context. |
| Copied ContextVar state could alias mutable verifier state | Each state records its creating thread and a closed flag. Cross-thread copied-context use and use after public-call closure reject before semantics. |
| Callback re-entry into the internal path worker was untested | The path worker rejects re-entry, and its body requires the invocation-local worker token. |
| Zero-artifact wording ignored historical development artifacts | V13 states only that no generated V13 density row, canonical matrix, runner, launch plan, or run exists. Historical V1 development artifacts remain historical and are not relabeled. |

## Publication protocol

The writer serializes the verification report once and publishes it below the
development root through no-follow directory descriptors and no-overwrite
destination creation. It then publishes an adjacent canonical receipt binding:

- receipt schema and protocol version;
- experiment identifier;
- exact destination filename;
- payload byte count;
- payload SHA-256;
- receipt SHA-256 over the canonical receipt payload.

`publication_status` opens both names relative to the descriptor-walked parent,
requires regular files, snapshots stable bounded bytes, requires canonical JSON
and exact receipt keys/types, verifies the receipt digest, and verifies the
payload byte count and SHA-256.

The terminal states are:

- `absent`: neither accepted artifact nor orphan is present;
- `unaccepted_orphan`: data exists without a receipt;
- `unaccepted_invalid_receipt`: a receipt path exists but is incomplete,
  malformed, noncanonical, or self-inconsistent;
- `unaccepted_receipt_mismatch`: the receipt is well formed but the payload is
  absent or does not match;
- `accepted`: the complete canonical receipt and payload binding match.

All destination names are exclusive. Unaccepted paths are permanent and cannot
be overwritten or reused.

## State lifecycle

Every public `verify_document` call creates a fresh state containing actual
work, reservation, and registered-curve cache values. The state is bound to the
creating thread, the path worker is protected by an invocation-local token, and
the state is marked closed before the prior ContextVar is restored. Nested
public calls still receive independent states.

This is ordinary API isolation, not a hostile same-process Python sandbox.
Same-thread monkeypatching, introspection of internal sentinels, and arbitrary
mutation by code already executing inside the process remain out of scope.

## Claim and budget boundary

The mathematical predicate/compiler/gate is unchanged. The completed canonical
provenance/predicate vector remains `480/112/336/218/4218`; frozen expectations
remain zero.

No relation yield, matrix rank, linear algebra, target descent, fixed-curve
preprocessing crossover, rho improvement, fitted exponent, deployment result,
or ECDLP break is established. V13 remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

No generated V13 curve-family density row, canonical matrix, runner, launch
plan, or run is authorized. `maximum_runs=0`.
