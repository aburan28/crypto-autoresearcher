# Finite Frobenius certificate for the archived BINSTD field

**Scope:** `EXP-BINSTD-8bdf86`, the n=17 bitmask field helper at PR #2484 head `c03b34d71ca81ac630eed25dc92db10cfe5bb5b5`. This is a deterministic source and finite-algebra diagnostic. It changes no archived run, experiment decision, performance estimate, or formal theorem status.

## Observation

The archived runner uses modulus bitmask `131081` (`t^17+t^3+1`). The [audit source](audit.py) reads `gf2.py` from that exact Git commit and requires its SHA-256 to equal the archived run's `402cf41f4d528346798eb873d09bd1a2f1f204ed6ea654a2d2bfb668c8b3d955`. It imports that frozen source in a temporary directory. The independent arithmetic uses a separate bit-position squaring implementation and polynomial remainder routine.

The [certificate](certificate.json) records these deterministic results:

| Finite check | Result |
| --- | --- |
| Archived `Field.sqr` versus independent squaring and F₂ matrix action | Identical for all 131,072 17-bit values |
| Monic proper divisors of `t^17+t^3+1`, degrees 1–8 | None among 510 candidates |
| Frobenius matrix order | 17 |
| Cyclic/normal orbit witness | Bitmask 3; orbit rank 17 |
| Irreducible factor bitmasks of `X^17+1` | 3, 313, 471; product checked |
| Factor-kernel dimensions in the concrete matrix | 1, 8, 8 |
| Degree subset sums | 0, 1, 8, 9, 16, 17 |

The [editable visual source](plot.py), [SVG](factor-kernels.svg), [vector figure](factor-kernels-figure.pdf), and [report PDF](report.pdf) show the factor-kernel dimensions and the derived subset sums. The bar lengths are dimensions, not performance measurements.

## Interpretation

The orbit-rank witness and order check supply finite premises for identifying the actual runner's Frobenius action as a cyclic F₂[X]-module with annihilating polynomial `X^17+1`. The factor checks and kernel dimensions agree with the archived admissible-dimension table. This provides a concrete bridge target for the existing Lean factorization and canonical-field theorems in PR #2484; it is **not** a Lean proof of the runner-to-canonical isomorphism or of the complete invariant-subspace classification.

## Limits and next proof obligations

The checker is Python code and relies on its own arithmetic, Git input, and interpreter. An exhaustive finite comparison is stronger than sampled testing of this 17-bit implementation, but it does not prove a universal algebraic theorem or authenticate historical execution. The standard cyclic-module/ideal correspondence needed to conclude that **every** invariant subspace has one of these six dimensions remains to be formalized and independently reviewed. The empirical relation-yield matrices, target sampling, runtime, attack cost, and security claims are outside this audit.

The next formal steps are: prove the archived modulus defines a field in Lean; bind the runner's bitmask operations and squaring to that field; transport Frobenius to the canonical `GaloisField 2 17`; and prove the ideal classification of invariant subspaces from the three square-free factors. The existing [bridge problem](../../../problems/binstd-frobenius-invariant-dimension-lean-bridge.md) remains open. No canonical performance graph changes because this report adds structural evidence only.

## Reproduction

From a checkout containing the source commit:

```sh
python3 docs/reports/2026-10-27-binstd-concrete-frobenius-check/audit.py \
  --repo . --revision c03b34d71ca81ac630eed25dc92db10cfe5bb5b5 \
  --out /tmp/binstd-concrete-frobenius.json
python3 docs/reports/2026-10-27-binstd-concrete-frobenius-check/plot.py
```

The audit refuses to overwrite its output and fails if the runner source hash, any finite equality, irreducibility check, matrix order, orbit rank, factor product, or kernel dimension differs. A normal run and `python3 -O` run produced byte-identical JSON in the local verification. The PDF source is [report.tex](report.tex); its vector figure was converted from the SVG with `svglib`/ReportLab and the report rendered with Tectonic. The report PDF page was inspected before publication.
