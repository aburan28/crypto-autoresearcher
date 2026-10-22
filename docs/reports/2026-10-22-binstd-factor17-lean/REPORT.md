# Lean check of the BINSTD n=17 factor product

The frozen BINSTD Stage-1 files list the bitmask polynomials 3, 313
and 471 as factors of `x^17-1` over `F₂`. In characteristic two this is
`x^17+1`. The new Lean theorem
`CryptoResearch.Binstd.x17_factorization` proves the exact product

`(X+1)(X^8+X^5+X^4+X^3+1)(X^8+X^7+X^6+X^4+X^2+X+1)=X^17+1`

in `(ZMod 2)[X]`. The [source-binding checker](check_source_binding.py)
reads both frozen admissible-dimension files, verifies that they have
identical SHA-256 values, and converts each Lean factor definition
back to its exact archived bitmask. Its [receipt](source-binding.json)
binds the source and Lean hashes.

The [formal task](../../../formal/targets/binstd-x17-factorization.yaml)
names the exact theorem and frozen source. The [Lean source](../../../formal/CryptoResearch/Binstd/Factorization.lean)
expands the product with `ring_nf` and discharges its even
coefficients using characteristic two. The [machine-verification
receipt](proof-verification.json) records the pinned Lean version,
build, theorem identity and axiom audit. It reports
`machine_verified` under Lean 4.35.0-rc1: full build passed,
617 theorem declarations had only standard axioms, the exact target
axiom audit passed, and there were no forbidden constructs. The
receipt still marks independent semantic review pending. The
[editable graph](factorization.dot),
[SVG](factorization.svg), [PNG](factorization.png),
[figure PDF](factorization-figure.pdf) and [report PDF](report.pdf)
separate the proved product from the remaining obligations.

This theorem does **not** establish irreducibility of the two
degree-eight factors, the normal-basis identification of field
Frobenius with the polynomial module, or the completeness of the
archived invariant-subspace dimension table. The prior
[toy-yield replay](../2026-10-22-binstd-ell89-replay/report.md)
checks separate empirical runs; no Lean theorem here proves their
hit counts, performance or security significance. No numerical
dashboard value changes.
