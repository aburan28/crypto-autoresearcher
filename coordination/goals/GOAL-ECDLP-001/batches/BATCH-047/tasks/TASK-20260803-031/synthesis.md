# BATCH-047 synthesis

**Task:** TASK-20260803-031  
**Batch:** BATCH-047  
**Date:** 2026-08-04

## What this batch did

BATCH-047 executed EXP-IT-001 under frozen PA-IT-001-v3-rc45-repair-5 with the
three BF-1..BF-3 control repairs mandated by DEC-20260803-004. All three controls
were mechanically closed:

- **BF-1** (CTRL-ANOMALOUS-TRACE1): A genuine Smart anomalous curve at bits=20
  was found and certified (p=771853, N=p, trace=1, C_special_smart=157, ratio 0.202).
- **BF-2** (CTRL_NULL_IT_PLANT): recompute_null_plant_from_ledger.py was run and
  produced a 48-row non-empty edge ledger.
- **BF-3** (CTRL-NULL-PACKAGING-GATE): Gate correctly rejected a synthetic
  R_xfer=0.5 claim without a certificate.

## What this batch established

**Density observation**: rho_special=0.0 for all three tested prime fields
(bits=20, 24, 28 ordinary 2-isogeny graphs). No anomalous, MOV, or subfield-friendly
special curves were found in any density universe at these scales.

This observation is correctly labeled as a null measurement and is NOT negative
evidence against H-IT-001 or against ECDLP hardness (AGENTS.md rules 5-7).

## Why the batch is inconclusive (DEC-20260803-51bcb6)

The Red Team returned FAIL on three formal blocking objections:

**RT-047-B1** reveals a structural issue: the frozen contract R5-FIX-PRESERVE-M1
requires the planted path positive control to start from a non-special curve.
The Executor found it was impossible to satisfy this requirement: the planted
control was forced to start from a special curve precisely because ordinary
2-isogenies preserve trace of Frobenius (isogeny-class invariant). An anomalous
curve (trace=1) occupies its own isogeny class; no ordinary isogeny walk from a
generic non-anomalous curve can reach it. The control started from a
special-embedding-degree-1 MOV curve instead.

This is not merely a procedural violation. It reveals that rho_special=0 may be
a structural mathematical property of the ordinary isogeny graph rather than a
finite-scale artifact:

> Ordinary ell-isogenies preserve the trace of Frobenius (equivalently: they
> map curves in the same isogeny class, i.e., curves with the same conductor
> ring). Anomalous curves (trace=1) form their own conductor class, distinct
> from all generic curves (trace ≠ 1). Therefore, a BFS walk in the ordinary
> 2-isogeny graph starting from a generic curve can never reach an anomalous
> endpoint, regardless of scale.

If this argument is correct, the H-IT-001 mechanism (transfer from generic curves
to anomalous endpoints via ordinary isogeny paths) is infeasible at ALL scales,
not just at toy scale. This must be formally confirmed before further Executor
work.

**RT-047-B2**: Non-reserved run-id, non-frozen mode, and broken batch provenance
(manifest cites BATCH-046 opener DEC-20260803-003). These formal failures do not
affect the scientific content but prevent the run from being cited as
contract-compliant.

**RT-047-B3**: Dirty worktree (run_bounded_toy.py modified). Reproducibility from
committed state is unconfirmed.

## What was NOT established

- No transfer-gate measurement (rho_special=0; no certificate-bearing sub-rho result)
- No H-IT-001 status change (stays `specified`)
- No support, weaken, or reject_scoped decision
- No asymptotic claim (all four promotion gates remain open)
- No crypto-scale result (toy tier only)
- No GOAL-ECDLP-001 completion
- No knowledge promotion

## Exact next action

Dispatch a mathematical analysis task (research-deep, reasoning_effort: max) to
formally evaluate the class-invariant argument:
1. State and prove or refute: do ordinary ell-isogenies preserve conductor?
2. If yes, is the H-IT-001 mechanism infeasible for ordinary isogenies at all scales?
3. If infeasible, propose: (a) a scoped closure of H-IT-001's ordinary-isogeny
   claim with an explicit named successor (e.g., supersingular isogeny transfer),
   or (b) a restatement of H-IT-001 restricted to provably reachable special curves.

This analysis runs BEFORE any further Executor batch on the current H-IT-001
formulation.
