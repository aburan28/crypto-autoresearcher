# FROB C5 factor-kernel and archived-field bridge

- **Status:** `open`
- **Kind:** mathematical proof and code-to-model bridge gaps
- **Affected work:** [EXP-FROB-91ee9c C5 specification](../experiments/EXP-FROB-91ee9c/specification.yaml), [historical analysis](../experiments/EXP-FROB-91ee9c/analysis.md), [finite-field Lean target](../formal/targets/frob-c5-finite-field-trace.yaml), [characteristic-five control](../formal/targets/frob-c5-characteristic-five-control.yaml)
- **Next action owner:** Coordinator to assign an independent formal semantic review and a source-bound checker task
- **Last updated:** 2026-10-22

## Problem

The frozen C5 control requires the kernel of the field trace on each degree-five
extension to equal the direct sum of the kernels of the nontrivial irreducible
factors of `X^5-1` under Frobenius. The current Lean theorems establish the
finite-field trace polynomial, its four-dimensional kernel and the
Frobenius-difference range, but do not prove this factor-kernel direct sum or
identify the archived `F_q[z]/(g)` code representation with the formal field.
The q=11, 13 and 19 recorded cells therefore cannot receive a full
proof-backed C5 verdict from these theorems alone.

## Evidence and uncertainty

- **Observed:** The frozen [run](../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml) reports C5 dimensions in all three core cells. The independent [object replay](../docs/reports/2026-10-22-frob-provenance-audit/core-object-replay.json) reconstructs the relevant Frobenius factor-kernel dimensions and point classifications using the archived pure-Python checker primitives. That replay does not formally verify the checker implementation or the original Sage source custody.
- **Derived or proved:** [OrderFive.lean](../formal/CryptoResearch/FrobTrace/OrderFive.lean) proves the abstract order-five trace kernel is the range of `F-1` when `F^5=1` and five is invertible. [FiniteFieldTrace.lean](../formal/CryptoResearch/FrobTrace/FiniteFieldTrace.lean) has a passed exact-source verifier receipt for a stronger finite-field specialization: the five-term Frobenius sum is the embedded field trace, the kernel has dimension four, and in characteristic other than five it is the range of `F-1`. The latter source has explicit `GaloisField q 5` instances for q=11, 13 and 19. The [proof report](../docs/reports/2026-10-22-frob-c5-finite-field-trace/REPORT.md) records an 8,970-job full build and target axiom audit passing at source commit `0600270bcf4a49edfb65d0fe838ab5fa4442216c`; independent semantic review remains required.
- **Proved negative control:** [CharacteristicFive.lean](../formal/CryptoResearch/FrobTrace/CharacteristicFive.lean) proves `X^5 - 1 = (X - 1)^5` and non-squarefreeness over `ZMod 5`; the [source-bound report](../docs/reports/2026-10-22-frob-c5-characteristic-five-control/REPORT.md) records the 8,971-job build and passing axiom audit at source commit `203cff284eff59a81e8a98a4ff5fac0459d63790`. It checks the characteristic boundary of the coprime-factor argument. It does not validate any archived q=11/13/19 implementation or result. Independent semantic review is pending.
- **Suspected explanation:** None is asserted. The missing steps are formalization and implementation-refinement obligations, not evidence that C5 is false.
- **Missing capability:** Formal factorization and pairwise-coprimality certificates for the three `X^5-1` cases, the corresponding kernel direct-sum theorem, and a checked map from the archived polynomial quotient and Frobenius matrix to the Lean field model.
- **What this evidence does not establish:** It does not certify the historical driver, the exact archived field encoding, C8, the experiment success gate, or a performance claim.

## What would unblock it

- [ ] In Lean, prove the exact q=11 split-four-linear, q=13 single-quartic, and q=19 two-quadratic factorizations of the nontrivial part of `X^5-1`, their pairwise coprimality, and that the direct sum of their Frobenius kernels equals the field-trace kernel in each cell, with the recorded dimensions.
- [ ] Bind the archived lexicographically first irreducible `g` and its quotient-field basis to the formal finite field by a checked isomorphism or a verified Frobenius matrix certificate. Replay all C5 input bytes and obtain independent semantic and code review before interpreting the run control as proved.
- [x] Verify the characteristic-five negative control in Lean: `X^5 - 1` is not squarefree over `ZMod 5`. This discharges only the proof-boundary control, not the factor-kernel or archived-code obligations.

The first condition would close the abstract C5 factor decomposition for the
three finite fields. The second would link it to the tested implementation.
Even then, C8 and the other frozen success gates require their own evidence.

## Next discriminating step

- **Action or proof obligation:** Formalize the polynomial factorization and CRT/kernel direct-sum lemma for the three primes, then check it against the existing finite-field trace theorem.
- **Inputs and controls:** Use the frozen `q,n,g` and factor strings in the run, plus an explicit characteristic-five control where squarefreeness fails. Do not infer an archived field representation from the cardinality alone.
- **Execution limits and stop condition:** Proof work may continue without a scientific trial. Preserve the frozen run and stop any proposed C5 promotion if the factor or model bridge cannot be checked on the exact bytes.
- **Outcomes and next actions:** A proof and source-bound bridge advance C5 to independent semantic review; a counterexample requires a scoped run correction; an unproved bridge leaves the control unestablished.
- **Recheck trigger:** A committed Lean factor-kernel theorem or a source-bound quotient-field certificate.

A planned proof is not a completed experiment. Existing proof, validation,
review, and archival rules still govern the follow-up.

## Resolution and history

- 2026-10-22: Opened after the finite-field trace core was formalized. The
  factor-kernel direct sum and archived-field implementation bridge remain
  unproved. Unresolved.
- 2026-10-22: The source-bound characteristic-five negative control passed its
  Lean build and axiom audit. It confirms failure of squarefreeness at q=5;
  the archived q=11/13/19 C5 verdict remains subject to the factor proof,
  code bridge, source custody and independent review.
