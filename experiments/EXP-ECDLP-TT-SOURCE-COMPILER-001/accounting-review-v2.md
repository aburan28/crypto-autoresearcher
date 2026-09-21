## Handoff: v5 accounting closeout

### Claim or task

Verify the v5 phase equations and changed protocol bindings without reopening
the unchanged v4 arithmetic surfaces.

### Status

`OBSERVATION` - `GO` for source implementation; no run authorization.

### Assumptions

- The target-free source matrix must contain only its source subtotal.
- The harness-only full matrix may contain the target delta and campaign total.

### Evidence so far

- `1022+25=1047` normalizations.
- `1512+0=1512` streamed-prefix factorizations.
- `8176+200=8376` two-sweep factorizations.
- `9688+200=9888` total rank factorizations.
- SHA-256 recomputation matched all six changed bindings: source manifest,
  source execution matrix, target manifest, control manifest, mutation
  manifest, and accounting model.
- The target delta is absent from the source-visible matrix.

### Failure modes

- Implementation code can still add unmodeled temporaries or operation paths.
- Source hashes and runtime closure must be frozen only after implementation.

### Next concrete action

Freeze the approved protocol in Git, implement the source compiler, and obtain
a separate implementation accounting review before any run.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/accounting-review-v2.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/source-execution-matrix-v2.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/execution-matrix-v4.json`
