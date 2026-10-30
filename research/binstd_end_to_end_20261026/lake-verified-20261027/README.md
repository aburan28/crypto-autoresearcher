# Pinned BINSTD full workspace and target verification

On 2026-10-27 UTC, the incremental `lake build` of the generated 48-module
root completed at the repository's frozen Lean 4.35.0-rc1 toolchain: 8,980
Lake jobs, exit 0. The exact `autoresearch formal verify` implementation,
called through `python -m orchestration.formal.cli`, then returned 0 with a
`machine_verified` receipt for
`CryptoResearch.Binstd.EncodedDivisors.archived_no_small_monic_divisors`.
Its internal root build reported 8,980 jobs, its named-module build two
jobs, `AxiomAudit.lean` reported 707 theorem declarations with only its
permitted standard axioms, and the generated requested-theorem audit passed.
The verifier found no forbidden constructs and recorded no infrastructure
failure. The raw command outputs and exit files are preserved here.

The receipt's task spec, theorem, toolchain and manifest hashes match the
earlier exact-pinned named Lake receipt. The frozen BINSTD source and target
bytes match producer revision `6409590d9bf26201956095e87f36f25d346cba68`;
the full verifier ran at PR revision
`98fca453a13b0e4e1ae866a96d14c2760cfb2aeb`. Its generated-root hash
matches the 48-module source in `../lake-workspace-20261027/`.

This machine result validates the **encoded finite computation theorem** as
stated. The verifier's `semantic_review` field remains `pending` because it
does not ingest independent reviews. The separate sealed J1/J2 review packet
at `../../binstd_encoded_lean_review_20261026/` establishes fidelity of the
same frozen finite statement within its stated scope. Neither artifact proves
that encoded `remFuel` is polynomial remainder, the original runner's field
model, a normal-basis identification, relation yield or attack cost. The
existing cyclotomic irreducibility and abstract canonical Frobenius proofs
are in separate, still-unmerged PR #2484; they are not promoted by this run.

`python3.11 make_receipt.py --check` recomputes the hashes and all assertions
in `full-gate-validation.json`. Hosted current-head Actions still cannot start
until the account payment/spending-limit gate is resolved; a local pass does
not bypass required checks, merge protection or the user's publication gate.
