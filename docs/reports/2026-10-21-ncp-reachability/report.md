# NCP shadow reachability: exact Lean iff — 2026-10-21

**Scope.** This formalizes Lemma 2(b) of
[`THM_COMMUTATOR_KERNEL1`](../../../research/THM_COMMUTATOR_KERNEL1.md) for
frozen target [`TASK-20260822-3dd086`](../../../formal/targets/ncp-reachability.yaml).
The proof source is [`Reachability.lean`](../../../formal/CryptoResearch/NCP/Reachability.lean),
committed at `25952e8b31bd357716d2058780de6cd57a752f6b`. It imports the
same `signedCount` and `shadowSign` definitions used in the earlier
[affine-normal-form proof](../2026-10-21-ncp-affine-normal-form/report.md),
so each translation's sign still depends on negations **to its right**.

## Exact statement and proof

For `a : Fin B → ℤ`, let `vectorWeight a = Σᵢ |aᵢ|`. For `e ∈ {+1,−1}`,
`shadowPenalty e a` is 0 when `e=+1` and every `aᵢ≥0`, 1 when `e=−1`, and
2 when `e=+1` and some `aᵢ<0`. The frozen named theorem proves, for every
natural degree bound `d`, the **full equivalence**:

```text
exists word w with length(w) <= d,
  shadowSign(w) = e and signedCount(w,i) = a_i for every i
iff
  vectorWeight(a) + shadowPenalty(e,a) <= d.
```

The lower bound proves `vectorWeight(signedCount w) + negCount w ≤ length w`.
With no negations, every signed count is nonnegative. A negative shadow sign
needs at least one negation; a positive sign with a negative coordinate
needs at least two. For the converse, the proof constructs pure translation
words `T+` and `T−` from the positive and negative parts of each coordinate.
It uses `T+`, `T− ν T+`, or `T+ ν T− ν` in the three cases, attaining the
lower bound exactly. [The diagram](diagram.svg) shows the case split.

## Validation

| Check | Result | Evidence and limit |
|:--|:--|:--|
| Pinned Lean workspace | **PASS** on Lean 4.35.0-rc1 | [Build log](evidence/lake-build.log); Mathlib lockfile unchanged. |
| Project and named axiom audit | **PASS, 498 theorem declarations**, standard axioms only | [Audit](evidence/axiom-audit.log) and [named theorem printout](evidence/statement-and-axioms.log). |
| Exact frozen target verifier | **machine_verified**; independent semantic review pending | [Source-bound receipt](evidence/target-receipt.json) binds task, source SHA-256 `11d5b4ef03ff895d195b028cf1ec9459a83da39e05f35b13a69c8a1aa6cf67fc`, toolchain, manifest, and source commit. |
| Direct exhaustive shadow crosscheck | **28 `(B,d)` cases, 9,190 word evaluations, 0 missing or extra shadows** for `B=0..3`, `d=0..6` | [Independent enumerator](evidence/shadow-crosscheck.py) and [log](evidence/shadow-crosscheck.log). This bounded check corroborates the convention; the Lean proof covers every `B`, `a`, and `d`. |
| Complete formal target verifier | **65 machine verified, 0 not verified, 0 infrastructure failures, 1 undischarged** | [Full corpus log](evidence/full-target-verification.log). The only absent theorem file is the NCP commutator-ideal refutation. Every verified target still needs semantic review. |

The crosscheck enumerates words directly, computes positional signed counts
by scanning each word from the right, and independently enumerates integer
vectors satisfying the degree formula. It compares complete shadow pairs
before reducing modulo a group order. The earlier archived
[`EXP-NCP-001` replay](../2026-10-21-ncp-affine-normal-form/report.md)
checked 12 frozen value sets and 12,000 shadow words; that value-level
replay was not repeated for this report.

## Boundary and remaining work

This theorem characterizes which combinatorial shadows can be represented
at a degree. It does not prove the path-algebra kernel ideal, an NC search
algorithm's cost, elliptic-curve implementation correctness, or ECDLP
performance. The commutator-ideal refutation remains a separate frozen
formal target. Independent semantic-fidelity review is pending before
official claim promotion.

No canonical numerical graph or performance dashboard was changed: this
proof and bounded crosscheck produced no new timing datum. The proof diagram
is also embedded in the [PDF](report.pdf).

## Reproduction

```sh
python3.12 tools/rebuild_formal_root.py
cd formal
lake build
lake env lean AxiomAudit.lean
cd ..
python3.12 -m orchestration.formal.cli verify \
  --task-file formal/targets/ncp-reachability.yaml \
  --artifact-out /tmp/new-ncp-reachability-receipt.json
python3.12 docs/reports/2026-10-21-ncp-reachability/evidence/shadow-crosscheck.py
```

Use a project Python environment with PyYAML for the formal CLI. Artifact
paths must be fresh because verifier receipts are immutable. Rebuild the PDF
with `render.py` in this report directory using `svglib`, `reportlab`, and
`tectonic`.
