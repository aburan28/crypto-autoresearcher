# Theory review v1

## Handoff: exact source-TT compiler theorem audit

### Claim or task

Audit the v1 exact finite-field TT compiler, target specialization, and narrow
claim boundary before implementation.

### Status

`REVISE`. V1 is not authorized for implementation.

### Assumptions

- The inherited curves, registries, RCB circuit, mode order, and tree are
  frozen.
- All arithmetic and ranks are exact over `F_p`.
- Producer preprocessing cannot read or enumerate a `B^5` tuple table.
- Verifier exhaustive replay remains separate audit work.

### Evidence so far

The review found two blockers.

First, v1 specialized trace-zero targets with `c3=X_Q^2`, omitting the term
`nY_Q^2`. The correct formula is

```text
h_Q = Z_Q^2 X2
    - 2X_QZ_Q XZ
    + (X_Q^2+nY_Q^2) Z2
    - 2nY_QZ_Q YZ
    + nZ_Q^2 Y2.
```

The error is exposed immediately by `Q=(0:1:0)`: v1 gives zero, while the
correct identity-target value is `nZ2`.

Second, a right-to-left sweep alone need not produce minimal bonds for an
arbitrary direct-sum TT. Direct-summing `u tensor v` and `u tensor w`, with
independent `v,w`, can leave a final-core row rank of two even though the
represented tensor `u tensor (v+w)` has cut rank one. The universal exact
normalizer must first sweep left to right to make prefixes full column rank,
then right to left to make suffixes full row rank and expose exact unfolding
ranks.

The review additionally requires:

- tagged canonical-zero semantics with reported exact ranks `(0,0,0,0)`;
- certified rank preservation, without a sweep, for nonzero scalar gates;
- separate streamed-prefix, raw-product, and final exact rank labels;
- wording "span dimension at most five," not exactly five;
- a mutation deleting `nY_Q^2` from `c3`;
- a nonzero-trace six-source control for `XY`;
- the narrow finite-instance claim and resource-stop boundary in v2.

### Failure modes

- Running or hashing v1 after either blocker is known.
- Calling one sweep universally minimal.
- Letting identity-target or general-basis controls pass the wrong formula.
- Treating a finite source compiler as a Fermat locator or ECDLP improvement.

### Next concrete action

Return `theory-v2.md`, `contract-v2.md`, and `specification.json` version 2 to
independent theory review before source implementation.

### Artifact paths

- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/theory-v1.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/theory-v2.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/contract-v1.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/contract-v2.md`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/specification-v1.json`
- `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/specification.json`
