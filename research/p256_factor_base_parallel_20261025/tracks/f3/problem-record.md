# Natural useful dependencies in coefficient-labelled P-256 bases lack a costed solver

Draft for Coordinator integration; it is not an official problem-state change.
The executor may only write `tracks/f3/**`.

- **Status:** open.
- **Kind:** implementation/proof gap; separately, Kudo chapter full-text access gap.
- **Affected work:** TASK-20261025-1f3375; report.md and result.json in this folder.
- **Next action owner:** Coordinator for a prospective solver handoff and problem index.
- **Last updated:** 2026-10-25.

## Problem

On published P-256, construction of `R_i=a_iG+b_iQ` with recorded independent
labels is executable, but no solver with a complete justified cost and natural
useful-dependency success law has been supplied for large bases. The tested
hybrid is complete only on the fixed m=3 domains. A single dependency helps
only when its net Q coefficient B is nonzero. Label-arithmetic dependencies
arranged without a target witness have A=B=0 in the demonstrated construction.

## Evidence and uncertainty

- **Observed:** 97 Python checks, 100 independent Sage assertions; one natural
  24-point case has no dependency in its 8/8/8 domains; arranged useful and
  zero-Q controls each have exactly one. Receipts bind exact cases and commands.
- **Derived:** independent uniform labels retain uniform B conditional on point-only
  selection of a nonzero relation vector; adaptive labels need a separate proof.
  Arranging a useful coefficient kernel for arbitrary Q is equivalent to knowing
  its logarithm; a genuine relation search remains allowed.
- **Missing:** full large-instance solver and success/cost analysis; Kudo full text.
- **Not established:** generic failure, impossibility, attack improvement, practical
  security, or performance inference from these correctness cases.

## What would unblock it

- [ ] Supply an explicit solver on natural P-256 labelled bases, with no hidden
  target scalar in search, charging all setup, rejections, residual solves,
  rational sign recovery, failed attempts, B=0 outputs, memory and verification.
- [ ] Prove its success/cost law or obtain observations through an independently
  admitted fixed protocol; retain a constructed positive, inverse, distinct-label
  zero-Q, and corrupted-label control, plus independent point checks.

These establish the solver's declared scope only; comparative scientific claims
still require matched evidence and independent review under repository rules.

## Next discriminating step

Derive a partition-compatible m=4/higher hybrid and its symbolic full-cost model,
including a costed label algorithm for any structured/adaptive base. Use public
unknown-log hash-to-point targets and points-only relation search, with fixed
controls; first perform theory/implementation checks within a two-GiB,
one-process envelope. Do not start an unadmitted performance panel. A correct
construction supplies a concrete prospective trial; a missing solver or failed
check records the exact gap; bounded emptiness leaves broader existence open.
Recheck on delivery of the solver or lawful access to Kudo's chapter. Unresolved.
