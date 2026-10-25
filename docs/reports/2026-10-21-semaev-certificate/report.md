# Semaev decomposition certificate: Lean decision theorem — 2026-10-21

**Scope.** This formalizes Lemma 3 of
[`THM_SEMAEV_FALL1`](../../../research/THM_SEMAEV_FALL1.md) for frozen target
[`TASK-20260916-b55948`](../../../formal/targets/semaev-decomposition-certificate.yaml).
The proof source is [`Certificate.lean`](../../../formal/CryptoResearch/Semaev/Certificate.lean),
committed at `84b0dd14a8c827bef6337c958b0bf96f1a2d7a5a`. It verifies a
certificate predicate for any tuple length, declared finite spanning family,
curve, and target; it makes no assertion that a certificate exists or that a
solver finds one at a particular rate.

## Exact checked proposition

Let `F` be a finite field, `K` a field with decidable equality and an
`F`-algebra structure, `W` an affine Weierstrass curve over `K`, and
`basis : Fin b → K`. Set `V = Submodule.span F (Set.range basis)`. The point
predicate excludes infinity and checks the explicit Weierstrass equation
and `x ∈ V`. The `Decidable` instance searches the finite coefficient set
`Fin b → F` for `Σ cᵢ • basisᵢ = x` and compares the curve-group sum with the
target. The frozen named theorem proves:

```text
decide (validDecomposition W basis P R) = true
  iff every P_i is a finite curve point with x(P_i) in V
      and (sum_i P_i) = R in Mathlib's curve group.
```

`equationCheck_iff_equation` connects the computable coordinate formula to
Mathlib's `W.Equation`; `inDeclaredSpan_iff_mem_span` connects finite
coefficient search to submodule membership. The
`validDecomposition_iff_curve_span_sum` theorem proves the underlying
predicate equivalence independently of the boolean wrapper. A supplemental
`validRawDecomposition` instance accepts raw `(x,y)` pairs, rejects invalid
curve coordinates, reifies valid pairs into Mathlib points, and checks the
same span and group-sum conditions. Its separate iff theorem covers that
untrusted-input path. [The diagram](diagram.svg) shows these checks and their
evidence boundary.

## Validation

| Check | Result | Evidence and limit |
|:--|:--|:--|
| Pinned Lean workspace | **PASS, 2,075 jobs** on Lean 4.35.0-rc1 | [Build log](evidence/lake-build.log); Mathlib manifest unchanged. |
| Project axiom audit | **PASS, 494 theorem declarations**, standard axioms only | [Axiom audit log](evidence/axiom-audit.log). |
| Exact frozen target verifier | **machine_verified**; semantic review pending | [Source-bound receipt](evidence/target-receipt.json) binds the target, theorem SHA-256 `aa022e4829eefc2cbe9ac05cbeb39f81e9e3eaa8147e2e41e9d718f11976bd89`, toolchain, manifest, and source commit. |
| Named theorem and raw checker axiom printouts | **standard axioms only** (`propext`, `Classical.choice`, `Quot.sound`) | [Printout](evidence/statement-and-axioms.log). |
| Complete formal target verifier | **64 machine verified, 0 not verified, 0 infrastructure failures, 2 undischarged** | [Full corpus log](evidence/full-target-verification.log). The two missing theorem files are NCP reachability and NCP commutator-ideal refutation. Every verified target still needs semantic review. |

The first exact-target attempt returned `formalization_blocked` even though
the source built: its requested-declaration audit requires a *theorem*, while
the initial source exported only the required `Decidable` instance under the
frozen name. The [initial source](evidence/initial-instance-only-source.lean.txt),
[receipt](evidence/initial-instance-only-receipt.json), and
[verifier output](evidence/initial-instance-only-verifier.log) retain that
failure. The final source retains the instance under
`instDecidableValidDecomposition` and supplies the frozen name as the
kernel-checked `decide = true` iff theorem; the final receipt passes.

## Boundary and remaining work

The basis parameter is any finite spanning family; linearly independent
bases are included. `K` need only have decidable equality, so finite fields
are included without requiring a finite enumeration of all of `K`. The
coefficient search is exact but can be expensive for large `b` or `F`;
this theorem gives no runtime bound. It does not prove decomposition
existence, probability, solver completeness, or ECDLP performance. It does
not replay archived Semaev measurements, so those experimental claims still
need their own evidence checks. Independent semantic-fidelity review is
pending before official claim promotion.

No canonical performance graph or dashboard was changed: this theorem
produced no new timing measurement. The added visual is a proof-boundary
diagram, also embedded in the [PDF](report.pdf).

## Reproduction

```sh
python3.12 tools/rebuild_formal_root.py
cd formal
lake build
lake env lean AxiomAudit.lean
cd ..
python3.12 -m orchestration.formal.cli verify \
  --task-file formal/targets/semaev-decomposition-certificate.yaml \
  --artifact-out /tmp/new-semaev-certificate-receipt.json
python3.12 tools/verify_formal_targets.py --artifact-dir /tmp/new-formal-receipts
```

The artifact paths must be fresh because the verifier preserves receipts
immutably. To rebuild the PDF, run `render.py` in this report directory with
`svglib`, `reportlab`, and `tectonic` installed.
