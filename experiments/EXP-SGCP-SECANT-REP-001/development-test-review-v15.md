# Development-Test Execution Review V15

## Handoff: raw-causality and outer-timeout state gaps

### Claim or task

Determine whether V15 safely constructs and authorizes exactly one isolated
five-test development run.

### Status

NEGATIVE RESULT

### Evidence so far

- Static review at commit
  `7f4e5ce39bd2b3cd335624fae6a5d1c73ab894ee`, tree
  `306d523505a6d3562e9408786c46d5f29b99768c`.
- Sole parent:
  `e8c58bfa387e0b66599f59698393293fd9a83bd0`.
- Protocol SHA-256:
  `95db5ef85f75928acde1c371be6cc273e06f6cbedc56a0642b7faebec47ea2ad`.
- Host SHA-256:
  `052cd2f489767a5daeabbd2b2543f18abd0aa6e180a68f9feba229b2c0c84ae2`.
- Authorization-validator SHA-256:
  `e1b028e166fd5ca729c516fa12fe1dd934817d88eec63db4d8d655eea2b5cbe4`.
- Result-validator SHA-256:
  `14e1a7e4fdbbafa076559ba1e605fbe0cb20d6811cf957540fe925c8655736fa`.
- Theory principal `019fae36-65c8-7fb3-8763-dd3a41020530`,
  accounting principal `019fae36-8a3d-7bb3-8502-1ced64a0cd51`, and
  red-team principal `019fae36-af3e-7d72-91e5-a14cb32b5d0b` returned
  `REVISE`.
- Inert controls confirmed aggregate TERM and KILL diagnostics, zero-only
  create completion, exact receipt-hash rejection, and contradictory
  classification rejection. No protected parser, import, compile, test,
  runner, validator, bootstrap, or experiment execution occurred.

### Positive controls that survived

1. The selected receipt hash map is recomputed and compared exactly.
2. Three pipeline statuses are carried into the receipt and checked against
   classification-specific predicates.
3. Full C validation and authoritative C-to-R cross-binding remain exact.
4. Fixed-overhead and candidate Git-write plans remain immutable and scoped
   without false exact physical-write or resource-accounting claims.
5. Create/signal windows and the host footer preserve unresolved ownership as
   process-only states rather than accepted R classifications.

### Failure modes

1. `PINNED_TIMEOUT_PREFIX_MISMATCH`: the host invokes GNU `gtimeout`, whose
   verbose diagnostics begin `gtimeout:`, but searches for `timeout:`. A real
   protected timeout would therefore be sealed as infrastructure failure.
2. `OUTER_TIMEOUT_ERASES_OWNERSHIP_STATE`: the aggregate wrapper omits
   `--preserve-status`, so a TERM handler returning exit 78 or 80 is externally
   collapsed to 124. The caller loses whether create publication or an owned
   container remains unresolved.
3. `PIPELINE_WIRE_FORMAT_IS_LOOSE`: the parser does not reject a nonempty
   unterminated fourth record and therefore does not enforce exactly three
   LF-terminated integer records.
4. `RAW_CAUSAL_ARTIFACTS_ARE_UNBOUND`: recovery recomputes selected receipt
   hashes but omits the raw pipeline, wrapper, container, timeout, OOM, and
   cleanup artifacts. Receipt self-consistency is therefore stronger than V14,
   but independent raw-causality reconstruction is not established.
5. `HOST_137_IS_NOT_RESOURCE_PROOF`: an undiagnosed or natural host exit 137
   is ambiguous; only a validated result with raw `OOMKilled=true` can prove
   the `RESOURCE_EXHAUSTION` classification.

### Strongest valid statement

V15 closes V14's selected-hash, pipeline-receipt, failure-predicate, active
footer, and aggregate KILL-mapping defects. It remains unauthorized because
the protected-timeout diagnostic is never recognized, aggregate timeout masks
unresolved ownership states, the pipeline wire format is underchecked, and
raw causal artifacts are not independently bound to the receipt.

### Next concrete action

Create V16 with the exact `gtimeout:` prefix, combined outer-timeout states
that preserve exits 78 and 80, strict three-record pipeline parsing, raw causal
artifact hashes and tuple reconstruction, and OOM-only resource attribution.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v15.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v15.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-authorization-validator-v15.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-result-validator-v15.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-review-v15.md`

No development-test or experiment-execution authority is granted.
