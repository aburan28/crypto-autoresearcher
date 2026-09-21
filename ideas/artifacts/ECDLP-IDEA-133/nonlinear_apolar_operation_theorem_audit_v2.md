# P1514 IDEA-133 producer-receipt scope correction V2

Reviewed: 2026-07-18 00:12:00 -0700

## Verdict

The immutable producer receipt `nonlinear_apolar_operation_theorem.md`, SHA-256
`4093e48132d96706db1155c44a8ab0f82de5ae997885df56b6ba1074022f297e`, requires
`REVISE` at its meet-in-the-middle and dense-Macaulay scope boundaries. It remains
preserved byte-for-byte as negative-evidence history. This V2 note supersedes the broad
wording identified below; it does not replace or silently repair the producer receipt.
`ECDLP-IDEA-133` remains deferred.

A concurrent producer correction, `nonlinear_apolar_operation_theorem_v2.md`, SHA-256
`b97666d65119c90eb7c63ac9df3be650af1b1e42854f613d1b39dc1eb68c50b2`, correctly
narrows the sufficient-cutoff and streamed-memory claims but does not fully distinguish
reusable-deck campaign time, direct-enumeration reuse, or the nonreduced primary-algebra
obligation. It is preserved as an intermediate correction and is superseded on those
points by this audit.

This is a deterministic, non-ECDLP scope audit. No relation collection, factor-log solve,
target descent, scaling experiment, algorithm promotion, or breakthrough claim occurred.

## Corrected meet-in-the-middle and direct-enumeration boundary

A two-plus-three split has decks of sizes `B^2` and `B^3`.

- Materializing and indexing a reusable larger deck charges `Theta(B^3)`
  precomputation time and state. With `Theta(B^2)` lookup work per target, the
  `Theta(B)`-target relation campaign remains `Theta(B^3)` total campaign time.
- Streaming the larger deck can retain `Theta(B^2)` working memory, but still costs
  `Theta(B^3)` time per target and `Theta(B^4)=Theta(N^0.8)` across `Theta(B)` relation
  queries under `N=Theta(B^5)`.
- Direct `B^5` source enumeration may be precomputed and indexed once at
  `Theta(B^5)` time and state, or rescanned at `Theta(B^5)` time per target and
  `Theta(B^6)` campaign time. The producer receipts' wording must not conflate these
  reuse choices. Both routes fail the frozen complete-path gate, for different charged
  resources.

Constant relation density, `Theta(B)` relation-query count, constant fiber rank, and
full output-rank growth are favorable `heuristic` and `model-bound` controls here, not
proved properties of the elliptic fibers.

## Corrected dense-Macaulay boundary

The cited Janovitz-Freireich–Mourrain–Rónyai–Szántó Theorem 3.5 supplies
`k=sum(d_i)-m=5B-3` as a sufficient cutoff where its condition holds. It does not prove
that every valid construction must use monomials through that degree, and it does not
make `5B-3` a compulsory minimum.

Instantiating the cited theorem-guaranteed dense route at that sufficient cutoff uses

`binomial((5B-3)+5,5)=binomial(5B+2,5)=Theta(B^5)`

coordinates and fails the frozen gate before its subsequent linear algebra. This closes
only that frozen instantiation. Adaptive early stabilization, a smaller fiber-specific
cutoff, sparse or multihomogeneous constructions, and an elliptic-specific structured
target-local moment oracle remain open and require complete charged recurrences.

## Corrected nonreduced-source boundary

For a reduced fiber, joint eigenvalues and eigenspaces can recover support. For a
nonreduced fiber, exact multiplicity and scheme structure require the full joint primary
decomposition and nilpotent local algebra, or an explicitly justified equivalent whose
local-space dimensions recover lengths. A spectrum or generalized eigenspace alone is
not a complete multiplicity/source biconditional.

## Verifier lineage and current plan

The current canonical `verify_nonlinear_apolar_theorem.py`, SHA-256
`cafef7ab468f11d3c68d58ab3105c3c76ebc33a7ffcdd3ec519c6a6cdbc43ec4`, reads only
this checkout, normalizes Markdown whitespace before exact semantic-token checks,
preserves both producer hashes, recomputes the corrected finite cost cells, and rejects
mutations that restore the overclaims or drop the nonreduced primary-decomposition
obligation. It writes nothing unless invoked with `--write`; any requested output is
rejected if it resolves outside this repository. This current canonical revision has not
been run and remains behind the retired, `review_required`, zero-run contract.

Three earlier execution histories are preserved as invalid evidence:

- an overwritten external-path revision, recorded at SHA-256
  `ae8c549ab5781acc98d99c73325ffa99da16cf8f65aab87fe6d5753bdfd0e25e`, was executed
  during the first audit and wrote outside this checkout; its raw source bytes were not
  retained before the boundary repair, which is an explicit provenance limitation;
- `verify_nonlinear_apolar_theorem_v2.py`, SHA-256
  `de07cdefea70091f193a0bb6b28e5dc38d0fc29fcf809295a0a30f29561b9ef9`, contains an
  impossible immutable-receipt token check and its external execution is invalid; and
- `verify_nonlinear_apolar_theorem_v3.py`, SHA-256
  `8d17e1339c98d586a3d1bb67032ba30fe364b9b76d9171f6cb88bebcc0c9293b`, loosens some
  semantic checks and was also executed through external contract/output paths despite
  the workspace and zero-run boundaries.

The two preserved verifier variants are rejected sources, not competing current
verifiers or claim evidence. The live focus state marks every external execution invalid
and keeps exactly the canonical repository-confined audit planned and unrun.

## Claim boundary

The durable P1514 result is a scoped input-and-cost screen. Supplied moments remain an
inadmissible constructor oracle; the direct and frozen sufficient-cutoff routes above
miss the complete cost gate. An adaptive or structured target-local operation with an
exact reduced and nonreduced source inverse remains unproved and unruled-out. Correct
moments, flatness, valid relations, or toy source recovery would not establish a generic
prime-field ECDLP improvement or breakthrough.
