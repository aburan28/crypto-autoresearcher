# V26 Read-Only Recovery Review

## Handoff: V26 requires immutable shell-control evidence

### Claim or task

Review the immutable V26 successor after repairing V24 protocol defects and the
V25 pinned-zsh special-parameter failure.

### Status

NEGATIVE RESULT

### Assumptions

- Controls required by the protocol must be immutable and reviewable from P.
- Conversation-local transcripts are not protocol evidence.
- Protected source/test bytes remain unparsed and unexecuted.

### Evidence so far

- P: `e5ceec7e8de251306ecbde2ac3198941568453c3`
- Tree: `95bb44c88358e8404c31a4aa1ed78ec7f99ebea1`
- Sole parent: `29cbca599f518b29357d65c143be31537c51a773`
- Parent tree: `c0d229e83cff40449ab74658418b3862faae66a8`
- Exact five-file delta and all bound hashes matched.
- V24 findings were repaired.
- V25 `status` and `path` assignments were removed.
- Local pinned-zsh 0/1/128, marker, exact-ref, validator, inventory, and real
  V23 fixture controls passed.
- Theory and red team returned `GO`.
- Accounting returned `REVISE`.
- A, recovery C/R, recovery directory, Docker invocation, protected execution,
  and archive extraction are absent.

### Failure modes

`BLOCKING`: P requires pinned-zsh 0/1/128 and marker-retention controls before
review, but P contains no immutable runner, transcript, receipt, hash, or
validator binding for those controls. Conversation-local successful output is
not replayable evidence from the immutable package.

### Next concrete action

Create V27 with a committed shell-control runner and canonical replay receipt.
Bind both artifacts through P delta, protocol hashes, review receipts,
authorization decision, host preclaim, and evidence-input materialization.
Require reviewers to replay the safe control runner from exact P.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-protocol-v26.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-host-runner-v26.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-authorization-validator-v26.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-result-validator-v26.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-recovery-source-manifest-v26.json`
