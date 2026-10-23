# Order-five trace kernel: a Lean proof of C5's algebraic core

**Date:** 2026-10-22; **Experiment:** `EXP-FROB-91ee9c`, frozen control C5;
**Formal target:** `TASK-20261022-adb94b`.
**Source:** [C5 specification](../../../experiments/EXP-FROB-91ee9c/specification.yaml), [experiment analysis](../../../experiments/EXP-FROB-91ee9c/analysis.md)

This is a formalization of one structural lemma used in C5, not a new
experiment, performance result, or adjudication of the frozen C5 control.
The [diagram](trace.svg) distinguishes the proved abstract statement from
the archived cell computations and the remaining cell-specific proof. A
[one-page PDF](report.pdf) contains the same boundary.

## Machine-checked proposition

In the pinned Lean workspace, let `R` be any field, `V` any `R`-vector space,
and `F : V →ₗ[R] V`. Assume `F ^ 5 = 1` and `(5 : R) ≠ 0`. With
`T(F) = 1 + F + F² + F³ + F⁴`, the theorem
[`ker_trace5_eq_range_sub`](../../../formal/CryptoResearch/FrobTrace/OrderFive.lean)
proves `ker T(F) = range(F − 1)`. The companion theorem
`fixed_trace5_eq_zero` proves that a vector fixed by `F` and killed by `T(F)`
is zero. The file also proves the elementwise equivalence and two polynomial
identities used by the kernel proof.

The proof uses field arithmetic and the endomorphism ring. It has no `sorry`,
`admit`, custom axiom, or `unsafe` declaration. The target spec is
[`frob-c5-order-five-trace-kernel.yaml`](../../../formal/targets/frob-c5-order-five-trace-kernel.yaml).
The exact compiler, build and axiom-audit receipt is recorded separately by
the formal verifier; a successful local `lean` command alone does not imply
semantic fidelity or promotion of a research claim.

## Relationship to the frozen experiment

The frozen C5 specification asserts more: for each completed `q=11,13,19`,
`n=5` cell, the directly constructed trace matrix equals the trace polynomial
in Frobenius; the nontrivial irreducible factor kernels form a direct sum
equal to `ker Tr`; that kernel has dimension four; and the one-dimensional
fixed field is excluded. The archived report records those cell computations.
The abstract Lean theorem does **not** construct any of those finite fields,
identify `F` with their Frobenius maps, prove `F^5=1` for their concrete
representations, calculate dimensions, or prove the factor-kernel direct sum.
Those are open formal obligations. The independent C8 instrument checks are
also separately incomplete, as documented by the
[FROB provenance audit](../2026-10-22-frob-provenance-audit/REPORT.md) and
[problem record](../../../problems/frob-c8-independent-recheck-incomplete.md).

No canonical performance graph changes as a result of this algebraic lemma:
it supplies no new measurements or cost comparisons. The reviewed diagram
here records only proof dependencies and the missing linkage.
