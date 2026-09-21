## Handoff: v4 accounting checksum

### Claim or task

Independently recompute the v4 shape, census, component-cap, traffic-cap,
backend, hash-binding, and control-rank records.

### Status

`OBSERVATION` - `GO` for source implementation after the independent red-team
gate also returns `GO`; no run is authorized by this review.

### Assumptions

- Displayed caps are invalidation bounds, not performance evidence.
- Source-only counts and campaign counts are distinct phase scopes.
- Synthetic rank inputs are the frozen control-manifest records.

### Evidence so far

- Stage-A multiplications at `B=5` recompute to 3,925,025; stage B recomputes
  to 2,422,625; the total is 6,347,650.
- Stage-A and stage-B workspaces both peak at 15,625 words; the local matrix
  peaks at 78,125 words; the prohibited raw TT is 2,109,625 words.
- The campaign census recomputes to seven source cells, 63 source tensors, 30
  retained advice tensors, 25 target tensors, 352 rank jobs, 1,047
  normalization calls, 1,512 prefix factorizations, 8,376 two-sweep
  factorizations, and 9,888 total factorizations as upper bounds.
- The six operation vectors sum exactly to
  `(42e9,42e9,42e9,6e9,5e6,102e9,26e9,4.048e9,420e9)` in frozen component
  order. The six traffic caps sum exactly to 420 billion words.
- `150*(3947-1)^2=2,335,637,400`, matching the frozen int64 accumulator bound.
- All six bound protocol-file hashes and the Python executable hash matched.
- The rank-one, sum/product, asymmetric, common-prefix, cancellation,
  inflated-product, gauge, and B17 control ranks matched their frozen values.
- The local NumPy closure was independently recomputed by the coordinator a
  second time as 1,320 files with the same frozen digest.

### Failure modes

- Implementation-specific temporaries can still violate the reviewed shape
  model and require a pre-run implementation accounting audit.
- The v4 source subtotal and campaign total use different scopes but were not
  named explicitly enough for the first red-team pass.
- A passing checksum does not show the compiler completes within budget.

### Next concrete action

Version the source-subtotal plus target-delta reconciliation explicitly and
obtain a red-team `GO` before writing source.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/accounting-review-v1.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/accounting-model-v3.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/execution-matrix-v3.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/source-execution-matrix-v1.json`
