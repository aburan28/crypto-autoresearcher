# Pre-run red-team review v2

## Handoff: final outer-translator pre-run review

### Claim or task

Determine whether the reviewed snapshot may begin the noncanonical development
run.

### Status

`OPEN`: `REVISE / NO-GO`. Do not launch development. Canonical execution is
not authorized.

### Assumptions

- The reviewed snapshot was based on HEAD
  `f86baf7453780e73dcaa7c745f1a8c6be3b9858b` plus untracked experiment files.
- Timing remains an unattested diagnostic and cannot support continuation.
- No files were edited by the reviewer.

### Evidence so far

Focused tests passed: `46 tests, 12 subtests`. Independent curve/order/MOV,
source-map, S3/S4, witness, workspace, projection, scalar-resultant, and
Sylvester checks are present. Four launch blockers remain:

1. `P0`: the continuation signal does not implement the complete contract.
   Criterion 6 requires non-worsening degree, density, and operation trends,
   but no executable trend predicate exists. The final gate uses only the
   supported-target pre-gate plus matched null, rather than a translator-wide
   functional gate covering identity and matched-uniform controls. The verifier
   independently reproduces the same incomplete formula.
2. `P0`: coordinate-target cardinality can silently clamp without failing
   continuation. Supported coordinate targets use `min(requested, available)`,
   but have no requested/realized status or conjunctive cardinality gate.
3. `P1`: the direct scalar-f4 comparator is systematically weak. Both invariant
   f3 coefficient triples are recomputed inside every tuple iteration. The
   verifier enshrines the inflated vector; its Sylvester calculation establishes
   correctness, not comparator competitiveness. An honest arithmetic baseline
   must cache invariant triples.
4. `P0`: launch provenance is not satisfied. The reviewed tree is untracked and
   rejected by the clean-worktree guard; the later theory v3 review and this
   review were not yet source-bound in the reviewed snapshot.

### Failure modes

- A family can emit a continuation signal despite an undefined or worsening
  scaling trend.
- Insufficient supported-target cardinality can be evaluated as though the
  requested schedule completed.
- The nested kernel can appear better against avoidably repeated direct-f4 work.
- A run before a clean, reviewed commit lacks the required provenance.

### Next concrete action

Create one revised, still-unrun snapshot that defines and independently verifies
a fail-closed trend predicate, exact coordinate-cardinality gate,
translator-wide functional conjunction, and cached direct-f4 comparator; add
isolated mutation tests, source-bind the reviews, then commit the snapshot
cleanly for re-review.

### Artifact paths

- `contract.md`
- `src/outer_translator.py`
- `src/verify_outer_translator.py`
- `src/run_development.py`
- `tests/test_outer_translator.py`

## Coordinator response

The v2 `NO-GO` is preserved. No development or canonical run was started. All
four findings are mandatory repair and re-review items.
