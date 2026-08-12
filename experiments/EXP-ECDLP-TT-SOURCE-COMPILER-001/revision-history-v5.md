# Revision history v5

## Preserved status

- V4 accounting review returned `GO`: every shape, census, operation-cap sum,
  traffic-cap sum, int64 bound, bound-file hash, and sampled control rank
  reconciled.
- V4 red-team review returned `REVISE` because source-partition counts and
  campaign counts were mathematically compatible but not explicitly named and
  reconciled next to each other.
- Pending `review_required` and `approved_by:null` fields remain unchanged; a
  pending review cannot approve itself.
- No source implementation or run exists.

## V5 repair

The target-free `source-execution-matrix-v2.json` now labels its count block
`source_partition_counts` with scope `source_generator_only`. It uses explicit
`source_` prefixes for all normalization and factorization upper bounds.

The harness-only `execution-matrix-v4.json` labels its block
`campaign_counts_per_baseline_path` and freezes this separate reconciliation:

```text
source subtotal       = (1022, 1512, 8176, 9688)
target delta          = (  25,    0,  200,  200)
campaign upper bound  = (1047, 1512, 8376, 9888)
```

The tuple order is normalization calls, streamed-prefix factorizations,
two-sweep factorizations, and total rank factorizations. The target delta stays
withheld from both source processes.

`accounting-model-v4.md` and `contract-v5.md` state the same equations and
clarify that early zero/zero-coefficient work can lower observed counts only
when the omission is reported.

## Unchanged boundaries

- Source-visible files remain target-free and are staged without repository,
  target, mutation, or prior-artifact state.
- The exact runtime, operation IR, componentwise accounting, controls, and 29
  mutations are unchanged except for versioned file identities.
- Passing remains toy, restricted, and model-bound; it is not a locator,
  relation algorithm, sub-rho result, or ECDLP improvement.

## Execution effect

The experiment remains `REVIEW_REQUIRED`. A post-repair accounting checksum
and red-team `GO` are required before the coordinator may approve source
implementation.

## Handoff: v5 closeout

### Claim or task

Verify that the v5 scope labels and equations remove the sole substantive v4
red-team ambiguity without weakening target redaction.

### Status

`OPEN`

### Assumptions

- The 25 target linear combinations each contribute at most one normalization
  and eight two-sweep factorizations.
- Target specialization has no streamed Hadamard prefix factorization.

### Evidence so far

- The four reconciliation equations are exact integer equalities.
- The source-visible file contains only the source subtotal.
- The full matrix binds the new source matrix, accounting model, and mutation
  manifest hashes.

### Failure modes

- A stale path or hash can invalidate the versioned repair.
- A renamed count can drift from the unchanged arithmetic census.

### Next concrete action

Run the v5 accounting checksum and red-team closeout against current hashes.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/revision-history-v5.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/source-execution-matrix-v2.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/execution-matrix-v4.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/accounting-model-v4.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/contract-v5.md`
