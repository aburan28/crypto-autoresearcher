# BATCH-048 scope decision

BATCH-048 is a pure mathematical analysis batch. No code, no experiment,
no run, no hypothesis-status change.

## What this batch does

One research-deep analysis task (TASK-20260804-002) formally evaluates the
class-invariant argument surfaced by RT-047-B1 in BATCH-047:

> Ordinary ell-isogenies preserve the trace of Frobenius (equivalently: they
> map within isogeny classes, i.e., within conductor rings). Anomalous curves
> (trace t = 1, N = p) occupy a separate conductor class from all generic curves
> (trace t ≠ 1). Therefore a BFS walk in the ordinary 2-isogeny graph starting
> from a generic curve never reaches an anomalous endpoint.

The analysis must state this argument with explicit theorem citations, determine
whether it holds unconditionally or only conditionally, identify any gap or
exception, and name the forward direction.

## What this batch cannot do

- Not a hypothesis-status transition (H-IT-001 stays `specified` throughout)
- Not an experiment
- Not an implementation
- Not a crypto-scale claim
- Not a GOAL completion

## Forward gate

If the analysis confirms the class-invariant infeasibility at all scales:
the Coordinator will use the analysis to decide whether to (a) weakly close
H-IT-001's ordinary-isogeny scope with a named successor, or (b) reformulate
H-IT-001 around a feasible transfer mechanism (e.g., supersingular paths,
or a different special-curve family that IS reachable via ordinary isogenies).

A scope-closure decision on H-IT-001 is NOT made in this batch; it follows the
analysis in a subsequent ledger record.
