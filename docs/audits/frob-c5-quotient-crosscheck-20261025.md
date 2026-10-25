# FROB C5 quotient matrix cross-check, 2026-10-25

This is an operator cross-check of the existing C5 quotient-matrix certificate,
not a Coordinator evidence decision or an independent Reviewer attestation. It
does not change the frozen run, its outcome, or the proof verification receipt.

## Inputs and method

The read-only [checker](frob_c5_quotient_crosscheck.py) binds the frozen
`RUN-FROB-91ee9c-7119f2` files to the
[C5 replay](../reports/2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json)
with SHA-256 `22bcbdbdc6dd8c020456549cb1aa2edf887422cb10912105d9fa0508a6ee1005`.
It checks the specification, fixtures, Sage core, lattice module, driver,
archived checker, replay checker, and three raw cell outputs against the
receipt's hashes. It also checks each raw file's embedded cell, parameter and
modulus fields. It reads the 75 matrix literals from
[QuotientMatrices.lean](../../formal/CryptoResearch/FrobTrace/QuotientMatrices.lean)
at SHA-256 `9de7bc465a4a12f6e325ddd61b67dd275d8ef6f622307bd2244707aaf081c39b`.

For each modulus, a separate pure-Python polynomial implementation computes
`X^(q*j) mod g(X)` for `j=0..4`, then compares all five coefficients with the
replay and Lean literals. A Rabin criterion check establishes executable
degree-five irreducibility. Checking all lexicographically earlier candidate
tuples establishes that each modulus is the first monic irreducible under the
specification's constant-first ordering: tuples with zero constant have factor
`X`; the only remaining earlier tuples have the same zero middle coefficients
and a smaller `X^4` coefficient. These are executable checks, not Lean proofs.

## Observed result

The [machine-readable output](frob-c5-quotient-crosscheck-20261025.json)
records seven matching source hashes, three matching raw-output hashes, 25 of
25 matrix entries for each of `q=11`, `13`, and `19`, and passing executable
irreducibility and ordering checks for all three moduli. The checker reads
archived files and performs no scientific trial. The existing
[source-bound replay checker](../reports/2026-10-22-frob-c5-factor-kernels/recheck_matrix.py)
and [Lean generator](../reports/2026-10-22-frob-c5-quotient-matrices/generate_quotient_matrix.py)
also passed their `--check` modes against the same repository state.

The raw cell files store the modulus and C5 outcome flags; they do **not**
serialize the Frobenius matrix. The matrix literals are reconstructed in the
later replay from those moduli. The equality between that reconstruction and
the mathematical quotient operation is now checked twice in Python and in
Lean. This does not establish that the historical Sage process ran the exact
committed source or that every operation in its driver refines the Lean model.

## Remaining boundary and next check

The proof receipt's semantic-review status remains `pending`. The
[bridge problem](../../problems/frob-c5-factor-kernel-and-model-bridge.md)
still requires source custody, historical Sage code-to-model validation, and
an independent formal semantic/code review. The executable irreducibility
check does not supply a Lean irreducibility theorem or a field isomorphism.
C8 and the experiment success gate remain separate.

The existing quotient-matrix proof graph and report were checked. The graph's
raw-run and replay labels were corrected in this change to show where the
matrix was reconstructed. Its verified algebraic edges and quantitative
dashboard coverage do not change; this audit adds a second arithmetic check.
No performance dashboard value changes.

The refreshed PNG is rendered from the same `proof.dot` as the SVG and figure
PDF with `dot -Gdpi=72 -Tpng proof.dot -o proof.png`; its labels were visually
inspected at the resulting 648×389 resolution. The vector exports preserve
full resolution.
