# FROB C5 factor-kernel proof audit — 2026-10-22

**Scope.** This is a mathematical proof review of frozen
`EXP-FROB-91ee9c` control C5 for the three core base fields. The Lean source
is [FactorKernel.lean](../../../formal/CryptoResearch/FrobTrace/FactorKernel.lean)
at commit `2143dda2b698cf6e3fb4bafbe853af7262e3ffba`. The three
[target specifications](../../../formal/targets/) bind the q=11, 13 and 19
field-level equality theorems. The [editable diagram](proof.dot),
[rendered graph](proof.svg) and [inspected PDF](report.pdf) show the proof
path and the remaining run bridge.

## Checked mathematical result

| Canonical field | Nontrivial irreducible factors of `X^5−1` | Kernel conclusion |
| --- | --- | --- |
| `GaloisField 11 5` | `X+2`, `X+6`, `X+7`, `X+8` | Four successive disjoint kernel summands have sum `ker Tr`, dimension 4. |
| `GaloisField 13 5` | `X^4+X^3+X^2+X+1` | The sole factor kernel equals `ker Tr`, dimension 4. |
| `GaloisField 19 5` | `X^2+5X+1`, `X^2+15X+1` | The two factor kernels are disjoint and have sum `ker Tr`, dimension 4. |

Lean checks exact cyclotomic factorizations and factor irreducibility. The
q=11 factors are linear. For q=13 and 19, Mathlib's finite-field cyclotomic
criterion applies after proving the orders of 13 and 19 modulo 5 are 4 and
2. A concrete Bézout certificate proves the q=19 quadratics coprime; distinct
linear factors give the q=11 coprimality statements. Mathlib's
`sup_ker_aeval_eq_ker_aeval_mul_of_coprime` and
`disjoint_ker_aeval_of_isCoprime` then establish the direct sums. The
previously verified [finite-field trace theorem](../2026-10-22-frob-c5-finite-field-trace/REPORT.md)
identifies the five-term Frobenius polynomial with the embedded field trace
and proves its kernel has dimension four.

## Verification and provenance

The source file compiled under the repository's pinned Lean `4.35.0-rc1`
workspace without proof errors. Each exact-source verifier receipt binds its
target, source commit `2143dda2b698cf6e3fb4bafbe853af7262e3ffba`, theorem
file SHA-256 `9adac769ca20c415d6a3afad7423ec385e69e7331606f23e0afd9d37450001ac`,
toolchain and dependency manifest.

| Field | Target | Exact receipt SHA-256 |
| --- | --- | --- |
| q=11 | `TASK-20261022-0b7f1e` | [q11-proof-verification.json](q11-proof-verification.json): `bed0ae94c784a90894e0152a0415de59e19d3be6edf135f50064d0ba2eae518a` |
| q=13 | `TASK-20261022-9d138c` | [q13-proof-verification.json](q13-proof-verification.json): `9be5c73505a17d14f0e15694556e6d9575e3fe90b90f7428903bc48c86db813e` |
| q=19 | `TASK-20261022-fb5ba5` | [q19-proof-verification.json](q19-proof-verification.json): `91e7f2ad9ccc5efbbb0fa74f9c92e3be57c2711155b1ae0e882155280c036889` |

All three receipts report `machine_verified`, passed target axiom audits, no
forbidden constructs, an **8,971-job full build**, and a workspace axiom
audit of **612 theorem declarations using standard axioms only**. Independent
semantic review remains pending; the hosted `lean-verification.yml` workflow
is manually disabled, so these local exact-source receipts are the available
formal gate evidence.

## Archived implementation inspection

The frozen Sage [core](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work/core.py)
and [driver](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/implementation.py)
construct the q-power Frobenius matrix with columns equal to the images of
`1,z,…,z^4`. Its constant-first polynomial evaluator forms the factor
matrices, takes their right kernels, sums those subspaces, compares the sum
with the trace matrix kernel, and tests directness by dimension additivity.
The three archived output files
([q11](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work/FROB-SPLIT-q11n5.out.json),
[q13](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work/FROB-NOLATTICE-q13n5.out.json),
[q19](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/work/FROB-EQDEG-q19n5.out.json))
record the same factor strings as the Lean file and true C5 equality/directness
flags. The separate [plain-Python checker](../../../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/checker.py)
reconstructs the quotient arithmetic and Frobenius matrix without importing
the Sage driver; for C5 it independently checks the trace-kernel dimension.
It does not independently certify the full sum equality or prove that either
implementation refines the Lean field model. The new [source-bound matrix
replay](recheck_matrix.py) checks that narrower gap independently of both
archived code imports. It first checks the frozen fixture cells and the specification SHA-256.
For each frozen `g`, it checks irreducibility with a finite-field polynomial
criterion, checks each modulus is the lexicographically first irreducible
under the archived constant-first selector, checks the recorded factors are
irreducible, and reconstructs the
5×5 Frobenius
matrix from quotient arithmetic, checks `F^5=I`, multiplies all factors to
`X^5−1`, computes every factor kernel, checks directness by rank, checks that the
factor basis is killed by the trace matrix, and uses the trace matrix rank to
establish equality. It also checks the fixed line lies outside the trace
kernel, compares every archived C5 flag, and re-runs the same order,
factor-kernel, trace, and fixed-line checks after changing one matrix entry.
The mutation fails the factor-kernel dimension check in all three cells.
The byte-exact [matrix receipt](c5-matrix-replay.json) has SHA-256
`22bcbdbdc6dd8c020456549cb1aa2edf887422cb10912105d9fa0508a6ee1005`.
This executable replay strengthens the archived C5 check; it is not a Lean
refinement of the quotient implementation or a substitute for independent
semantic code review. Those obligations remain open.

A separate [source-bound Lean certificate](../2026-10-22-frob-c5-quotient-matrices/REPORT.md)
now proves all 75 entries of the three recorded q-power matrices in the
archived quotient bases. Its exact-source verifier passed, but it does not
prove the historical Sage implementation refines the quotient algebra or
connect this matrix action to the canonical-field factor-kernel theorem. A
[second Lean certificate](../2026-10-22-frob-c5-quotient-matrix-kernels/REPORT.md)
applies the factor polynomials directly to the exact recorded matrices and
proves their kernel sums, directness and trace-kernel dimension four.

## Boundary and next check

The factor-kernel theorem uses canonical `GaloisField q 5` values. The quotient
certificate proves q-power images of the frozen basis monomials, and the
matrix-kernel certificate proves C5 for the resulting exact matrices. A
full-map q-power linearity/representation lemma and checked historical Sage
refinement remain open. Source custody and independent review are required
before the historical C5 control can be called proof-backed. The
[open problem](../../../problems/frob-c5-factor-kernel-and-model-bridge.md)
tracks those checks. C8 and the full experiment success gate remain open.

No experiment was rerun, no new timing or attack-cost measurement was made,
and no performance graph value was changed. The diagram and PDF were updated
to show the newly proved mathematical result and the unresolved code bridge.
