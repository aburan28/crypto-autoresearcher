# Semaev degree-two cancellation lacks a nonzero fall bridge

- **Status:** `open`
- **Kind:** proof gap and interpretation gap
- **Affected work:** [FFD_SEMAEV_MEASUREMENT1](../research/FFD_SEMAEV_MEASUREMENT1.md), [frozen formal target](../formal/targets/semaev-s3-degree2-fall-witness.yaml), [Lean proof](../formal/CryptoResearch/Semaev/DegreeTwoFall.lean), [2026-10-20 validation report](../docs/reports/2026-10-20-formal-validation/report.md)
- **Next action owner:** formal research lane and Coordinator for claim wording
- **Last updated:** 2026-10-20

## Problem

The uniform claim that the Weil-descended Semaev `S_3` system has a nontrivial first fall at degree two is not established by its Lean theorem. The theorem cancels the degree-two coefficients when the target abscissa is nonzero, but does not prove that the resulting degree-at-most-one polynomial is nonzero or outside the lower-degree span. The frozen target and historical report describe the stronger conclusion.

The archived toy table covers `n=4..7`, factor-base dimension `n'=3,4`, ten Semaev draws per cell, and matched null draws. It records `d_ff=2` in 70 of 80 Semaev draws and `d_ff=3` in 10. Those summaries do not retain enough per-draw target and witness detail to explain the exceptions or to test the theorem's `x_R ≠ 0` condition on each draw.

## Evidence and uncertainty

- **Observed:** The eight rows in [`ffd_semaev_results.json`](../research/verification/ffd_semaev_results.json) sum to 70 `d_ff=2` and 10 `d_ff=3` Semaev outcomes. The [report](../research/FFD_SEMAEV_MEASUREMENT1.md) nevertheless says the degree is pinned at two in every cell.
- **Derived or proved:** [`DegreeTwoFall.lean`](../formal/CryptoResearch/Semaev/DegreeTwoFall.lean) proves the Artin–Schreier normalization and trace annihilation of the quadratic coefficients. Its own scope comment explicitly states that a nonzero surviving residue and hence a degree-two fall are unproved.
- **Suspected explanation:** Unknown. Degenerate lower-degree residues, target abscissa zero, or a difference between the measured polynomial model and the lemma are discriminating possibilities, not findings.
- **Missing capability:** An exact Lean model of the descended Boolean polynomial system and the quotient defining `new_falls(2)`, plus per-draw replay data sufficient to reconcile the ten exceptions.
- **What this evidence does not establish:** It neither refutes a correctly qualified degree-two fall theorem nor proves one; it supplies no solving-degree or ECDLP cost conclusion.

## What would unblock it

- [ ] Formalize the descended `S_3` equations, the degree filtration, and a nonzero class in `V_{F,2} / V_{F,1}`. State any exact restrictions on `n`, `V`, and `x_R` and prove that the premises hold for the claimed family, or supply a checked counterexample and narrow the claim.
- [ ] Replay the eight frozen cells with per-draw target abscissa, basis, coefficient vector, residual polynomial, `new_falls(2)`, seed, source revision, and independent checker output; reconcile every recorded `d_ff=3` case.

Satisfying both conditions would support a semantically faithful theorem for the resulting qualified scope. Performance and solving-degree claims would remain separate obligations.

## Next discriminating step

- **Action or proof obligation:** Derive and check the full residual polynomial for the smallest cell that recorded `d_ff=3`, then attempt a Lean statement for its nonzero class or a counterexample.
- **Inputs and controls:** Use the archived `n=4,n'=3` cell and the historical `ffd_semaev_measure.py` plus `ffd_frobenius_witness.py`; retain the support-matched null and independently computed row-space ranks.
- **Execution limits and stop condition:** First reproduce the archived cell and its seed policy exactly. Stop this diagnostic after one reconciled exceptional draw or a documented inability to reconstruct the historical input; a new scientific campaign needs its own frozen protocol and run record.
- **Outcomes and next actions:** A nonzero residue plus `d_ff=3` signals a model/rank mismatch to debug; a zero residue explains why cancellation is insufficient; a missing input becomes an access/reproducibility gap; a tool failure is an infrastructure result.
- **Recheck trigger:** Exact per-draw replay or a new theorem/counterexample for the nonzero class.

## Resolution and history

- 2026-10-20: Opened after comparing the frozen target, Lean scope comment, and raw summary. No research-state transition was made. Unresolved.
