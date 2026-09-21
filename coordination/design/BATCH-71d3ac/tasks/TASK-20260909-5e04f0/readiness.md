# Readiness — `TASK-20260909-5e04f0`

## Current state

This is a BATCH-local, zero-run symbolic-design package for the reserved
`H-ECDLP-5014e2` / `EXP-ECDLP-9d1966` identifiers.  It is **not** a canonical
hypothesis or experiment, has no Coordinator approval, and authorizes neither
implementation nor scientific execution.

## What the package fixes

The draft defines a finite full-binary tree of depth three, bounded integer
window variables, a declared symbolic leaf-weight equation, and a fixed
threshold of 24 symbolic-weight units.  It also fixes the leaf-record fields,
classification precedence, cost-accounting vector, and synthetic controls.
This makes the bookkeeping question reviewable: whether a proposed symbolic
tree is completely and uniquely classified under one declared threshold.

The package does not establish that the tree represents an elliptic-curve
decomposition, a Semaev summation polynomial, a factor-base condition, a
lattice instance, a small-root condition, or any ECDLP computation.

## Gates

| Gate | State | Evidence or required next action |
| --- | --- | --- |
| Finite symbolic grammar | Draft complete | `specification.yaml` has a closed tree, variable, weight, threshold, and verdict contract. |
| Source provenance for recalled mathematics | Blocked | Retain and hash primary source bytes with exact proposition locators before any mathematical applicability claim. |
| Duplicate and Pareto review | Inconclusive | No repository-wide semantic comparison or source-backed literature comparison has been performed. |
| Independent design review | Required | Review the exact symbolic grammar, accounting identity, controls, and boundary against cryptanalytic overinterpretation. |
| Implementation/custody design | Not started | A separate plan must bind source commit, renderer hash, fixture inventory, output schema, refusal paths, and archive ownership. |
| Implementation authorization | Disabled | `implementation_authorized: false`; no code or fixtures may be created. |
| Scientific execution | Disabled | `maximum_scientific_runs: 0`; no `RUN-*`, benchmark, curve, relation, or DLP work exists. |

## Review boundary

An independent reviewer may decide only whether the finite symbolic contract
has a well-defined grammar, exhaustive classifications, recomputable weights,
and controls that reject cryptographic overinterpretation.  A holding review
would support at most a Coordinator decision to convert this package into a
canonical **proposed** zero-run record.  It would not support an implementation,
execution, or scientific conclusion.

## Source impediment

The proposal that motivated this design names Semaev and Jochemsz--May topics.
No source was read or retained in this task.  Those names remain recalled,
unverified search pointers.  They cannot establish novelty, known status,
adaptation, a cost model, an attack baseline, or applicability to ECDLP.

## Next action

Pre-register and obtain an independent source-only review of the symbolic
interface and its controls.  Keep the source-retrieval and implementation
gates separate; a passing grammar review does not clear either one.
