# Semaev degree-two cancellation lacks a nonzero fall bridge

- **Status:** `open`
- **Kind:** proof gap and interpretation gap
- **Affected work:** [FFD_SEMAEV_MEASUREMENT1](../research/FFD_SEMAEV_MEASUREMENT1.md), [frozen formal target](../formal/targets/semaev-s3-degree2-fall-witness.yaml), [Lean proof](../formal/CryptoResearch/Semaev/DegreeTwoFall.lean), [2026-10-20 validation report](../docs/reports/2026-10-20-formal-validation/report.md), [2026-10-22 per-draw replay](../docs/reports/2026-10-22-semaev-first-fall-replay/report.md)
- **Next action owner:** formal research lane and Coordinator for claim wording
- **Last updated:** 2026-10-22

## Problem

The uniform claim that the Weil-descended Semaev `S_3` system has a nontrivial first fall at degree two is not established by its Lean theorem. The theorem cancels the degree-two coefficients when the target abscissa is nonzero, but does not prove that the resulting degree-at-most-one polynomial is nonzero or outside the lower-degree span. The frozen target and historical report describe the stronger conclusion. A checked finite example now contradicts the uniform wording **within the archived Boolean first-fall model**; this does not refute the narrower Lean identity.

The archived toy table covers `n=4..7`, factor-base dimension `n'=3,4`, ten Semaev draws per cell, and matched null draws. It records `d_ff=2` in 70 of 80 Semaev draws and `d_ff=3` in 10. The October 22 replay reconstructs all 80 inputs: five degree-three draws have `x_R=0`, outside the theorem premise, and **five have `x_R≠0`**. The latter show that the premise alone cannot make the stronger archived first-fall statement true.

## Evidence and uncertainty

- **Observed:** The eight rows in [`ffd_semaev_results.json`](../research/verification/ffd_semaev_results.json) sum to 70 `d_ff=2` and 10 `d_ff=3` Semaev outcomes. The [report](../research/FFD_SEMAEV_MEASUREMENT1.md) nevertheless says the degree is pinned at two in every cell. The original summary script reproduced that JSON byte for byte on October 22. The [per-draw record](../docs/reports/2026-10-22-semaev-first-fall-replay/evidence/draws.json) retains all 80 Semaev seeds, targets, bases, equation vectors, ranks and trace residuals, plus 200 null-control seeds and grades. Its independent checker compared 21,760 field products, 12,800 direct `S_3` assignments, and separate row-space ranks for all 280 draws; every archived cell matched.
- **Derived or proved:** [`DegreeTwoFall.lean`](../formal/CryptoResearch/Semaev/DegreeTwoFall.lean) proves the Artin–Schreier normalization and trace annihilation of the quadratic coefficients. Its own scope comment explicitly states that a nonzero surviving residue and hence a degree-two fall are unproved.
- **Concrete finite explanation:** For `n=4,n'=4,s=1`, `x_R=1` and basis `[9,3,2,12]`, trace cancels the quadratic part but its residual `u₀+u₃+w₀+w₃` is already the fourth degree-one generator. The independent checker gives `dim V₁=1` and `dim(V₂∩R_{≤1})=1`, hence `new_falls(2)=0`; degree three is the first fall. Four nonzero-target degree-three draws have a nonzero trace residual already in `V₁`, and one has a zero trace residual. Five zero-target draws are outside the theorem premise.
- **Missing capability:** An exact Lean model of the descended Boolean polynomial system and the quotient defining `new_falls(2)`, a kernel-checked finite counterexample or qualified positive theorem, and an additive correction to the broader frozen claim through the repository's review process.
- **What this evidence does not establish:** It does not refute a correctly qualified degree-two fall theorem for another scope or prove one; it supplies no solving-degree or ECDLP cost conclusion.

## What would unblock it

- [ ] Formalize the descended `S_3` equations, the degree filtration, and a nonzero class in `V_{F,2} / V_{F,1}`. State any exact restrictions on `n`, `V`, and `x_R` and prove that the premises hold for the claimed family, or supply a checked counterexample and narrow the claim.
- [x] Replay the eight frozen cells with per-draw target abscissa, basis, equation coefficient masks, trace residual (or explicit inapplicability at `x_R=0`), `new_falls(2)`, seed, source revision, and independent checker output. All ten recorded `d_ff=3` cases are classified. The 200 null-control grades and support profiles were also replayed; no new timing was measured.

Satisfying both conditions would support a semantically faithful theorem for the resulting qualified scope. Performance and solving-degree claims would remain separate obligations.

## Next discriminating step

- **Action or proof obligation:** Formalize the archived Boolean filtration and the `n=4,n'=4,s=1,x_R=1` rank certificate in Lean. State the finite counterexample with the same monomial equations and exact `V₁,V₂` dimensions; then propose an additive correction to the frozen target's uniform interpretation.
- **Inputs and controls:** Use the source-hash-bound per-draw equation masks and independent projection-rank receipt. Preserve the existing trace lemma and support-matched null replay as controls. Any positive theorem must state restrictions on `n`, `V` and `x_R` that exclude the checked exceptions.
- **Execution limits and stop condition:** Do not edit the frozen target or fabricate a universal repair. A finite Lean certificate would settle this toy counterexample, not general solving degree or ECDLP cost.
- **Outcomes and next actions:** A kernel-checked finite counterexample supports correction of the uniform claim; a failed Lean model requires the precise definition mismatch to be recorded; a qualified positive theorem needs independent semantic review against the archived observable.
- **Recheck trigger:** Kernel-checked finite rank model or a reviewed additive correction.

## Resolution and history

- 2026-10-20: Opened after comparing the frozen target, Lean scope comment, and raw summary. No research-state transition was made. Unresolved.
- 2026-10-22: Replayed all eight summary cells byte for byte and independently checked the 80 Semaev draws and 200 null controls. Five nonzero-target degree-three cases make the archived uniform first-fall wording false in its own Boolean model. The Lean filtration bridge and additive claim correction remain open; no official state transition was made.
