# ECDLP alternatives intake audit — 2026-10-01

Disposition: three directions already have records; create one proposed measurement
record for the remaining bounded diagnostic scope. This is an intake decision,
not a novelty finding or an assessment that any historical proposal is correct.

| Direction | Disposition and existing coverage |
| --- | --- |
| Useful scalar-relation lifting | Already represented by IDEA-20260905-848b77 (torsion/formal-group splitting and useful-lift decodability) and IDEA-20260905-4dca34 (canonical versus arbitrary lift observables). Both are proposals. |
| Direct scalar-multiplication algebraic structure | No exact scope match found in the searches below. Add IDEA-20261001-e1fcbf as a proposed structural measurement on public, known-scalar forward computations. Original motivation is understanding global equation structure; this intake does not propose inversion or claim a solving advantage. |
| Isogeny transport to an easier representation | Already represented by proposed IDEA-20260905-1dd2e5 on arithmetic heterogeneity within an isogeny class and auxiliary computation. Whole transport cost remains unresolved. |
| Coordinate invariants and scalar information | Already represented by active question RQ-ECDLP-4fcbd3, including coordinate bias and Fourier diagnostics. |

The parent source reader `/root` read the source material on 2026-10-01 and
supplied excerpts to TASK-20261001-1d7296. This author used those excerpts;
historical theorem claims and experiments were not independently verified.
The frozen handoff is `TASK-20261001-1d7296.yaml` in this directory. Its
`source_sha256` entries identify the supplied source snapshots.
The accompanying `frontier-evidence.txt` has SHA256
`02e46d128caa19f5980093fa2c3889074b7608ff24a83efea8ea4ac082be9169`.

Search coverage supplied by the parent:

- 2,241 parsed proposal/question entries at source commit
  `e9d654daa065b8b8ebdee7210ed9592c549850b8`.
- Additional current-origin/main grep at
  `0945f107be66bf3c024c27a47975a100b62bad33` covered direct scalar, scalar
  multiplication with encoding/constraint/circuit, direct algebraic/SAT/encoding,
  circuit inversion/ECDLP, and treewidth phrases; no exact match was reported.
- The parent subsequently checked main at
  `73c07430c51c32c452093747687578b8b5e6843b`; the intervening changes did not
  affect proposal, question, frontier or intake-input sources. Frozen evidence
  remains pinned to `0945f107be66bf3c024c27a47975a100b62bad33`.
- The older semantic-search CLI failed because `typer` was missing. This reduces
  duplicate-search coverage; it is not negative search evidence.
- A limited external query about ECDLP direct scalar-multiplication SAT encoding
  without summation polynomials returned mostly adjacent quantum and forward
  multiplication literature. External novelty review remains incomplete.

Nearby internal scopes are explicitly retained: IDEA-20260906-b035a5 concerns
separators in implicit factor-base relation hypergraphs; IDEA-20260906-c662ad
concerns differential-ladder reachability correctness; KN-OPEN-007 concerns
Semaev resultant-tree tensor-rank growth. None establishes the correctness or
usefulness of this diagnostic. All supplied frontier hits, including the highest
ranked KR-IC-b0fcda and generic-bound row KR-RHO-13bf67, are assessed in the
new proposal. Search scores carry no evidential weight.

Only the audit and proposed record are intake outputs. No measurements,
experiments, scalar recovery, or operational attack development were performed.
The existing full-ledger baseline was reported failed before this intake (2,540
errors, including sparse missing experiments and prior citation/review-plan
issues). This audit makes no global validation-PASS assertion.
