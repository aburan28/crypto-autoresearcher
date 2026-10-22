# FROB C5 factor-kernel and archived-field bridge

- **Status:** `open`
- **Kind:** historical code-to-model bridge and independent semantic review
- **Affected work:** [EXP-FROB-91ee9c C5 specification](../experiments/EXP-FROB-91ee9c/specification.yaml), [frozen run](../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml), [factor-kernel formal targets](../formal/targets/frob-c5-factors-q11.yaml)
- **Next action owner:** Coordinator to assign an independent formal semantic review and a source-bound quotient-field checker task
- **Last updated:** 2026-10-22

## Problem

The mathematical C5 factor-kernel statement has now been proved in Lean for
the three canonical degree-five finite fields. The historical run used a
specific `F_q[z]/(g)` representation and executable Frobenius matrix. No
checked isomorphism or verified matrix certificate yet binds those exact
archived bytes to the Lean field model. The frozen C5 control cannot be
promoted to a proof-backed historical run verdict on the finite-field theorem
alone. C8 and the experiment success gate remain separate.

## Evidence and uncertainty

- **Observed:** The frozen [run](../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml) reports C5 equality and dimension four in all three core cells. The independent [object replay](../docs/reports/2026-10-22-frob-provenance-audit/core-object-replay.json) reconstructs the factor-kernel dimensions and point classifications using archived plain-Python checker primitives. The newer [source-bound matrix replay](../docs/reports/2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json) independently reconstructs the exact 5×5 Frobenius matrices from the three frozen moduli, checks factor kernels, directness, trace equality, fixed-line exclusion and a matrix mutation, and compares every archived C5 flag. It is executable evidence, not a Lean refinement proof of the historical code.
- **Proved:** [OrderFive.lean](../formal/CryptoResearch/FrobTrace/OrderFive.lean) gives the abstract trace-kernel identity. [FiniteFieldTrace.lean](../formal/CryptoResearch/FrobTrace/FiniteFieldTrace.lean) identifies the five-term q-power Frobenius sum with finite-field trace and proves its kernel has dimension four. [FactorKernel.lean](../formal/CryptoResearch/FrobTrace/FactorKernel.lean) proves the exact q=11 four-linear, q=13 one-quartic and q=19 two-quadratic nontrivial factorizations of `X^5−1`, irreducibility, coprimality where needed, and direct-sum equality with the trace kernel of dimension four. The [proof report](../docs/reports/2026-10-22-frob-c5-factor-kernels/REPORT.md) records the exact source commit and verifier receipts. Independent semantic review remains pending.
- **Missing capability:** A checked map from each archived lexicographically first irreducible `g` and quotient basis to the corresponding Lean field, or a Lean-verified Frobenius matrix certificate bound to the original run bytes, plus independent code/semantic review and original source custody.
- **What this evidence does not establish:** It does not certify all operations in the historical driver, the run's C8 control, the experiment success gate, a performance advantage or deployed-size ECDLP behavior.

## What would unblock it

- [x] In Lean, prove the exact three core-cell cyclotomic factorizations, irreducibility, kernel direct sums and trace-kernel dimension four. The checked source is `FactorKernel.lean` at commit `2143dda2b698cf6e3fb4bafbe853af7262e3ffba`; exact-source receipts and semantic review status are in the linked report.
- [ ] Bind each archived `g` and its quotient-field basis to the formal finite field by a checked isomorphism, or prove a source-bound Frobenius matrix certificate in Lean on the exact archived bytes. Check the historical implementation's field and matrix operations against that model, including a characteristic-five negative control and original source custody.
- [ ] Obtain independent formal semantic and code review before promoting the frozen C5 verdict.

The first completed item closes the mathematical factor-kernel obligation for
the three canonical fields. The remaining items bind that result to the
historical implementation. Even after they pass, C8 and the other frozen
success gates require their own evidence.

## Next discriminating step

- **Action or proof obligation:** Formalize the three archived quotient moduli `z^5+2z^4+1` over `F_11`, `z^5+8z^4+1` over `F_13`, and `z^5+3z^4+1` over `F_19`, and prove a basis-preserving map or matrix certificate for q-power Frobenius and the factor polynomials. The source-bound replay provides the expected 5×5 matrices and mutation control.
- **Inputs and controls:** Use the frozen `q,n,g` strings and raw output hashes, the committed factor targets, and an explicit characteristic-five countercontrol where squarefreeness fails. Reject any byte mismatch or unproved quotient-field assumption.
- **Execution limits and stop condition:** Proof/checker work may continue without a scientific trial. Preserve the frozen run. Stop any proposed C5 promotion if the model bridge, custody or independent review cannot be checked.
- **Outcomes and next actions:** A checked model bridge and review advance C5 to historical-control adjudication; a counterexample requires a scoped run correction; an unproved bridge leaves the control unestablished.
- **Recheck trigger:** A committed Lean quotient-field isomorphism or source-bound matrix certificate and independent review.

## Resolution and history

- 2026-10-22: Opened after the finite-field trace core. At that point the factor-kernel direct sum and archived-field representation were both unproved.
- 2026-10-22: The canonical-field factor-kernel proof and an independent source-bound matrix replay closed the mathematical decomposition gap and strengthened executable C5 validation. The historical code-to-model bridge and independent review remain open.
