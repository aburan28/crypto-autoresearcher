# FROB C5 factor-kernel and archived-field bridge

- **Status:** `open`
- **Kind:** historical code-to-model bridge and independent semantic review
- **Affected work:** [EXP-FROB-91ee9c C5 specification](../experiments/EXP-FROB-91ee9c/specification.yaml), [frozen run](../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml), [factor-kernel formal targets](../formal/targets/frob-c5-factors-q11.yaml), [quotient-matrix target](../formal/targets/frob-c5-quotient-matrices.yaml), [matrix-kernel target](../formal/targets/frob-c5-quotient-matrix-kernels.yaml), [full-map target](../formal/targets/frob-c5-quotient-frobenius-map.yaml), [quotient-kernel target](../formal/targets/frob-c5-quotient-kernel-transport.yaml), [characteristic-five control](../formal/targets/frob-c5-characteristic-five-control.yaml)
- **Next action owner:** Coordinator to assign independent semantic/code review and historical Sage refinement/source-custody check
- **Last updated:** 2026-10-22

## Problem

The mathematical C5 factor-kernel statement is proved in Lean for the three
canonical degree-five finite fields. A separate Lean certificate now proves
that q-power on each frozen polynomial quotient basis has the exact 5×5
matrix reconstructed from the archived outputs. The exact recorded matrices
now have Lean-checked C5 factor-kernel sums and trace-kernel dimension four.
The full q-power endomorphism has the certified matrix in each quotient power
basis. Lean now proves the C5 factor-kernel sums, trace-kernel dimension,
fifth-power identity, and fixed-line separation for those actual quotient
endomorphisms. A link to historical Sage execution, original source custody,
and independent semantic review remain open. The frozen C5 control cannot yet be promoted to a
proof-backed historical run verdict. C8 and the experiment success gate
remain separate.

## Evidence and uncertainty

- **Observed:** The frozen [run](../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml) reports C5 equality and dimension four in all three core cells. The independent [object replay](../docs/reports/2026-10-22-frob-provenance-audit/core-object-replay.json) reconstructs the factor-kernel dimensions and point classifications using archived plain-Python checker primitives. The newer [source-bound matrix replay](../docs/reports/2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json) independently reconstructs the exact 5×5 Frobenius matrices from the three frozen moduli, checks factor kernels, directness, trace equality, fixed-line exclusion and a matrix mutation, and compares every archived C5 flag. It is executable evidence, not a Lean refinement proof of the historical code.
- **Proved:** [OrderFive.lean](../formal/CryptoResearch/FrobTrace/OrderFive.lean) gives the abstract trace-kernel identity. [FiniteFieldTrace.lean](../formal/CryptoResearch/FrobTrace/FiniteFieldTrace.lean) identifies the five-term q-power Frobenius sum with finite-field trace and proves its kernel has dimension four. [FactorKernel.lean](../formal/CryptoResearch/FrobTrace/FactorKernel.lean) proves the exact q=11 four-linear, q=13 one-quartic and q=19 two-quadratic nontrivial factorizations of `X^5−1`, irreducibility, coprimality where needed, and direct-sum equality with the trace kernel of dimension four. The [factor proof report](../docs/reports/2026-10-22-frob-c5-factor-kernels/REPORT.md) records its exact-source receipts. [QuotientMatrices.lean](../formal/CryptoResearch/FrobTrace/QuotientMatrices.lean) checks 12 exact polynomial divisions and all 75 entries of the frozen q-power matrices in the three archived quotient bases; its [report](../docs/reports/2026-10-22-frob-c5-quotient-matrices/REPORT.md) and exact-source receipt bind source commit `c685c2951ac3a972a0fc07154609a37540187441`. Independent semantic review remains pending.
- **Proved on exact matrices:** [QuotientMatrixKernels.lean](../formal/CryptoResearch/FrobTrace/QuotientMatrixKernels.lean) applies those factor polynomials to the exact matrices, proves the direct sums and trace-kernel dimensions, and records an [exact-source receipt](../docs/reports/2026-10-22-frob-c5-quotient-matrix-kernels/proof-verification.json) and [report](../docs/reports/2026-10-22-frob-c5-quotient-matrix-kernels/REPORT.md). Independent semantic review remains pending.
- **Proved full map:** [QuotientFrobeniusMap.lean](../formal/CryptoResearch/FrobTrace/QuotientFrobeniusMap.lean) identifies the full base-field-linear q-power endomorphism of each archived quotient with the exact frozen matrix in its power basis. Its [report](../docs/reports/2026-10-22-frob-c5-full-map/REPORT.md) and [exact-source receipt](../docs/reports/2026-10-22-frob-c5-full-map/proof-verification.json) bind source commit `1993b13e4a245b5e92ac8748198d2e9d0013e885`. Independent semantic review remains pending.
- **Proved quotient controls:** [QuotientKernelTransport.lean](../formal/CryptoResearch/FrobTrace/QuotientKernelTransport.lean) transports the exact matrix trace rank and fifth-power results through the power basis, applies the checked factor identities to the actual q-power maps, and proves the trace and fixed-space dimensions and disjointness. Its [formal target](../formal/targets/frob-c5-quotient-kernel-transport.yaml), [report](../docs/reports/2026-10-22-frob-c5-quotient-kernel-transport/REPORT.md) and [exact-source receipt](../docs/reports/2026-10-22-frob-c5-quotient-kernel-transport/proof-verification.json) bind the precise scope. Independent semantic review remains pending.
- **Proved negative control:** [CharacteristicFive.lean](../formal/CryptoResearch/FrobTrace/CharacteristicFive.lean) proves `X^5−1=(X−1)^5`, the repeated quartic, and non-squarefreeness over `ZMod 5`. Its [source-bound report](../docs/reports/2026-10-22-frob-c5-characteristic-five-control/REPORT.md) records the passed Lean build and axiom audit. This is a proof-boundary control, not an archived q=5 run cell.
- **Missing capability:** The moduli are not proved irreducible in Lean or identified with the canonical `GaloisField`; the source-bound replay checks irreducibility and C5 dimensions executably. Historical Sage implementation refinement, original execution-source custody and independent code/semantic review remain open. The driver's `T_equals_hM` flag compares two constructions of the same matrix polynomial, so that flag alone is only a consistency check; kernel equality, rank and directness are the load-bearing C5 checks.
- **What this evidence does not establish:** It does not certify all operations in the historical driver, the run's C8 control, the experiment success gate, a performance advantage or deployed-size ECDLP behavior.

## What would unblock it

- [x] In Lean, prove the exact three core-cell cyclotomic factorizations, irreducibility, kernel direct sums and trace-kernel dimension four. The checked source is `FactorKernel.lean` at commit `2143dda2b698cf6e3fb4bafbe853af7262e3ffba`; exact-source receipts and semantic review status are in the linked report.
- [x] Prove the three exact quotient-basis q-power matrices in Lean. The [matrix target](../formal/targets/frob-c5-quotient-matrices.yaml) and [receipt](../docs/reports/2026-10-22-frob-c5-quotient-matrices/proof-verification.json) cover every entry and bind the theorem to the source-bound replay receipt. This is a mathematical quotient-algebra certificate, not a proof of the historical executable.
- [x] Prove the direct factor-kernel sums and trace-kernel dimension four for the exact recorded matrices in Lean. The [matrix-kernel target](../formal/targets/frob-c5-quotient-matrix-kernels.yaml) and [receipt](../docs/reports/2026-10-22-frob-c5-quotient-matrix-kernels/proof-verification.json) bind this result to source commit `458c91dbdcb8b0116173014e421da852333e4e1a`.
- [x] Verify the characteristic-five negative control in Lean: `X^5−1` is not squarefree over `ZMod 5`. This discharges only the proof-boundary control.
- [x] Prove the full q-power endomorphism is base-field linear and has the exact frozen matrix in each archived quotient power basis. The [full-map target](../formal/targets/frob-c5-quotient-frobenius-map.yaml) and [receipt](../docs/reports/2026-10-22-frob-c5-full-map/proof-verification.json) bind the source and standard-axiom audit.
- [x] Prove the quotient q-power endomorphisms themselves satisfy the factor-kernel, trace, fifth-power and fixed-line controls. The [quotient-kernel target](../formal/targets/frob-c5-quotient-kernel-transport.yaml) and [receipt](../docs/reports/2026-10-22-frob-c5-quotient-kernel-transport/proof-verification.json) bind the result.
- [ ] Check historical implementation field and matrix operations against this mathematical model, resolve original execution-source custody, and prove or independently validate modulus irreducibility at the required trust level.
- [ ] Obtain independent formal semantic and code review before promoting the frozen C5 verdict.

The completed items cover canonical-field decomposition, exact quotient-basis
matrix entries, factor-kernel arithmetic on those matrices, the full
q-power map's matrix, and its quotient-level C5 controls. The remaining items
connect the model to the historical implementation. Even after they pass, C8 and
the other frozen success gates require their own evidence.

## Next discriminating step

- **Action or proof obligation:** Check the archived Sage field construction, power-basis coordinates, polynomial evaluation and kernel paths against the proved quotient model, with original execution-source custody and independent semantic review. Prove the three moduli irreducible in Lean if the intended historical field claim requires a formal field isomorphism.
- **Inputs and controls:** Use the frozen `q,n,g` strings and raw output hashes, the committed factor targets, and an explicit characteristic-five countercontrol where squarefreeness fails. Reject any byte mismatch or unproved quotient-field assumption.
- **Execution limits and stop condition:** Proof/checker work may continue without a scientific trial. Preserve the frozen run. Stop any proposed C5 promotion if the model bridge, custody or independent review cannot be checked.
- **Outcomes and next actions:** A checked model bridge and review advance C5 to historical-control adjudication; a counterexample requires a scoped run correction; an unproved bridge leaves the control unestablished.
- **Recheck trigger:** Independent code/semantic review and original source custody, followed by an updated historical-control adjudication.

## Resolution and history

- 2026-10-22: Opened after the finite-field trace core. At that point the factor-kernel direct sum and archived-field representation were both unproved.
- 2026-10-22: The canonical-field factor-kernel proof and an independent source-bound matrix replay closed the mathematical decomposition gap and strengthened executable C5 validation. The historical code-to-model bridge and independent review remain open.
- 2026-10-22: The source-bound Lean quotient-basis certificate proved all 75 q-power matrix entries for the three frozen moduli. The quotient-matrix C5 kernel link, historical Sage refinement, source custody and independent review remain open.
- 2026-10-22: Lean proved the exact recorded matrices' factor-kernel sums and trace-kernel dimensions. Full-map q-power representation, historical Sage refinement, source custody and independent review remain open.
- 2026-10-22: The characteristic-five control proved failure of squarefreeness at q=5. This does not alter the q=11/13/19 historical-control boundary.
- 2026-10-22: Lean identified the full q-power endomorphism's matrix in each quotient power basis. Explicit kernel transport, historical Sage refinement, source custody and independent review remain open.
- 2026-10-22: Lean proved C5 factor-kernel, trace, fifth-power and fixed-line controls for the actual quotient endomorphisms. Historical Sage refinement, source custody and independent review remain open.
