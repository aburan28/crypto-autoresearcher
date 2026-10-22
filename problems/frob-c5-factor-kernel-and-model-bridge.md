# FROB C5 factor-kernel and archived-field bridge

- **Status:** `open`
- **Kind:** historical code-to-model bridge and independent semantic review
- **Affected work:** [EXP-FROB-91ee9c C5 specification](../experiments/EXP-FROB-91ee9c/specification.yaml), [frozen run](../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml), [factor-kernel formal targets](../formal/targets/frob-c5-factors-q11.yaml), [quotient-matrix target](../formal/targets/frob-c5-quotient-matrices.yaml)
- **Next action owner:** Coordinator to assign independent semantic/code review and the quotient-matrix C5 kernel link
- **Last updated:** 2026-10-22

## Problem

The mathematical C5 factor-kernel statement is proved in Lean for the three
canonical degree-five finite fields. A separate Lean certificate now proves
that q-power on each frozen polynomial quotient basis has the exact 5×5
matrix reconstructed from the archived outputs. The remaining gap is a
checked link from that quotient matrix to the C5 factor-kernel assertion and
the historical Sage execution, with original source custody and independent
semantic review. The frozen C5 control cannot yet be promoted to a
proof-backed historical run verdict. C8 and the experiment success gate
remain separate.

## Evidence and uncertainty

- **Observed:** The frozen [run](../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml) reports C5 equality and dimension four in all three core cells. The independent [object replay](../docs/reports/2026-10-22-frob-provenance-audit/core-object-replay.json) reconstructs the factor-kernel dimensions and point classifications using archived plain-Python checker primitives. The newer [source-bound matrix replay](../docs/reports/2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json) independently reconstructs the exact 5×5 Frobenius matrices from the three frozen moduli, checks factor kernels, directness, trace equality, fixed-line exclusion and a matrix mutation, and compares every archived C5 flag. It is executable evidence, not a Lean refinement proof of the historical code.
- **Proved:** [OrderFive.lean](../formal/CryptoResearch/FrobTrace/OrderFive.lean) gives the abstract trace-kernel identity. [FiniteFieldTrace.lean](../formal/CryptoResearch/FrobTrace/FiniteFieldTrace.lean) identifies the five-term q-power Frobenius sum with finite-field trace and proves its kernel has dimension four. [FactorKernel.lean](../formal/CryptoResearch/FrobTrace/FactorKernel.lean) proves the exact q=11 four-linear, q=13 one-quartic and q=19 two-quadratic nontrivial factorizations of `X^5−1`, irreducibility, coprimality where needed, and direct-sum equality with the trace kernel of dimension four. The [factor proof report](../docs/reports/2026-10-22-frob-c5-factor-kernels/REPORT.md) records its exact-source receipts. [QuotientMatrices.lean](../formal/CryptoResearch/FrobTrace/QuotientMatrices.lean) checks 12 exact polynomial divisions and all 75 entries of the frozen q-power matrices in the three archived quotient bases; its [report](../docs/reports/2026-10-22-frob-c5-quotient-matrices/REPORT.md) and exact-source receipt bind source commit `c685c2951ac3a972a0fc07154609a37540187441`. Independent semantic review remains pending.
- **Missing capability:** The matrix theorem proves basis coordinates in the quotient algebra but does not itself prove the modulus irreducible in Lean, identify the quotient with the canonical `GaloisField`, or prove the C5 factor-kernel identity for that exact matrix. The source-bound replay checks modulus irreducibility and C5 dimensions executably. Historical Sage implementation refinement, original source custody and independent code/semantic review remain open.
- **What this evidence does not establish:** It does not certify all operations in the historical driver, the run's C8 control, the experiment success gate, a performance advantage or deployed-size ECDLP behavior.

## What would unblock it

- [x] In Lean, prove the exact three core-cell cyclotomic factorizations, irreducibility, kernel direct sums and trace-kernel dimension four. The checked source is `FactorKernel.lean` at commit `2143dda2b698cf6e3fb4bafbe853af7262e3ffba`; exact-source receipts and semantic review status are in the linked report.
- [x] Prove the three exact quotient-basis q-power matrices in Lean. The [matrix target](../formal/targets/frob-c5-quotient-matrices.yaml) and [receipt](../docs/reports/2026-10-22-frob-c5-quotient-matrices/proof-verification.json) cover every entry and bind the theorem to the source-bound replay receipt. This is a mathematical quotient-algebra certificate, not a proof of the historical executable.
- [ ] Link the quotient-matrix action to the factor-kernel C5 theorem in Lean, either by a checked isomorphism to the canonical fields or by a direct matrix-model kernel proof. Check the historical implementation's field and matrix operations against that model, including a characteristic-five negative control and original source custody.
- [ ] Obtain independent formal semantic and code review before promoting the frozen C5 verdict.

The first two completed items close the canonical-field decomposition and the
exact quotient-basis matrix obligations. The remaining items connect them to
each other and to the historical implementation. Even after they pass, C8 and
the other frozen success gates require their own evidence.

## Next discriminating step

- **Action or proof obligation:** Use the now-proved q-power matrices to prove the exact nontrivial factor-kernel sums, directness and trace-kernel dimensions in each quotient matrix model, or construct a checked isomorphism to the canonical fields. Then review the archived Sage field and kernel paths against that model, with original source custody.
- **Inputs and controls:** Use the frozen `q,n,g` strings and raw output hashes, the committed factor targets, and an explicit characteristic-five countercontrol where squarefreeness fails. Reject any byte mismatch or unproved quotient-field assumption.
- **Execution limits and stop condition:** Proof/checker work may continue without a scientific trial. Preserve the frozen run. Stop any proposed C5 promotion if the model bridge, custody or independent review cannot be checked.
- **Outcomes and next actions:** A checked model bridge and review advance C5 to historical-control adjudication; a counterexample requires a scoped run correction; an unproved bridge leaves the control unestablished.
- **Recheck trigger:** A committed Lean quotient-matrix C5 kernel theorem or field isomorphism, plus independent code/semantic review and original source custody.

## Resolution and history

- 2026-10-22: Opened after the finite-field trace core. At that point the factor-kernel direct sum and archived-field representation were both unproved.
- 2026-10-22: The canonical-field factor-kernel proof and an independent source-bound matrix replay closed the mathematical decomposition gap and strengthened executable C5 validation. The historical code-to-model bridge and independent review remain open.
- 2026-10-22: The source-bound Lean quotient-basis certificate proved all 75 q-power matrix entries for the three frozen moduli. The quotient-matrix C5 kernel link, historical Sage refinement, source custody and independent review remain open.
