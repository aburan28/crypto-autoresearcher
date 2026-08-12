---
id: KN-LIT-7580
type: literature
title: Complex-Multiplication Terminals for Supersingular Isogeny Path-Finding
authors:
  - "Zheng Tao"
  - "Zhi Hu"
  - "Yijing Zhang"
  - "Changan Zhao"
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1516'
identifiers:
  eprint: iacr:2026/1516
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1516
tags: [isogeny, supersingular, isogeny-path-problem, delfs-galbraith, complex-multiplication, hilbert-class-polynomial, klpt, endomorphism-ring, precomputation, time-memory, cost-model, post-quantum]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Proposes a complementary stopping rule for the subfield-search stage of supersingular
isogeny path-finding — the bottleneck of the Delfs–Galbraith / SuperSolver algorithm.
Instead of walking the supersingular 2-isogeny graph only until it hits the subfield
terminal set `S_p`, the walk also stops on a *precomputed* set of complex-multiplication
(CM) supersingular vertices `S_CM(M)`, built from roots of Hilbert class polynomials
`H_D(X)` over `F_{p^2}` for inert negative fundamental discriminants `|D| < M`.

## Key claims (as reported)
- The enlarged terminal set is `S_p ∪ S_CM(M)`; the only extra per-visit cost is an
  expected `O(1)` hash-table membership query against the precomputed CM table.
- Heuristic growth of the precomputed table: `|S_CM(M)| = Θ(M^{3/2})`, with the overlap
  `S_CM(M) ∩ S_p` of lower order.
- Terminal-connection procedures convert a search that stops at a CM vertex into a full
  isogeny path, **under the standard quaternionic and KLPT heuristics**.
- The method **does not change the asymptotic exponent** of the underlying
  Delfs–Galbraith search. The authors present it as a complementary technique, not an
  exponent improvement.
- Small-parameter experiments reduce both visited vertices and field multiplications;
  lookup benchmarks at SQIsign parameters report stable, moderate per-visit overhead.

## Relevance to this program
This is the most directly instrumented entry in the 2026-07-27 gather, and it is a
textbook instance of the trade the program's own cost discipline exists to price.

- `KN-TECH-029` (supersingular isogeny-problem algorithms, classical and quantum
  path-finding) is the entry this bears on. Delfs–Galbraith is the classical baseline
  recorded there; this paper touches its *constant factor and memory profile*, not its
  exponent. Nothing in `KN-TECH-029` is superseded, and this entry does not rewrite it.
- `KN-TECH-024` (supersingular isogeny graphs and the CGL hash) supplies the walk model
  the stopping rule modifies.
- `KN-TECH-028` (endomorphism rings, Deuring, KLPT, SQIsign) is where the
  terminal-connection step's heuristics live — the conversion from "stopped at a CM
  vertex" to "produced a path" is KLPT-conditional, so the claim inherits KLPT's
  heuristic status.
- `KN-OPEN-013` (hardness of the supersingular endomorphism-ring / isogeny-path problem)
  is the open problem in scope. This does not move it: a constant-factor speedup with a
  `Θ(M^{3/2})` precomputed table is precisely the kind of result the program's claim-tier
  discipline (`docs/claims-and-verification.md`) scores below an exponent change.

The reusable instrument is the shape of the trade, not the isogeny content. Enlarging a
terminal/stopping set by precomputation, so that a random walk terminates sooner at the
cost of a table, is structurally the same move as enlarging a factor base in index
calculus, and it is governed by the same accounting: the walk gets shorter, the table
gets bigger, and whether that is a win depends entirely on whether the cost model charges
for the table. `KN-TECH-035` (memory-charged cost models) and `KN-TECH-050` are the
relevant instruments. A `Θ(M^{3/2})`-sized table queried once per visited vertex is not
free in any machine model that charges for storage and wiring, and the paper's own
framing — "does not change the asymptotic exponent" — is consistent with that.

**Does not bear on the ECDLP.** The supersingular isogeny problem is a different object
from the elliptic-curve discrete logarithm. Nothing here touches the `sqrt(p)` barrier or
the index-calculus line. It is recorded because the corpus tracks post-quantum
alternatives and because the precompute-to-shorten-the-walk trade is directly reusable.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved from
eprint.iacr.org on 2026-07-27 (hence `confidence: reported`). ePrint history: received
2026-07-24, approved 2026-07-27. Not peer-reviewed or formally published as of this
entry; no DOI on the ePrint page.

NOT verified here: the `Θ(M^{3/2})` growth heuristic and its constant; the claim that the
overlap `S_CM(M) ∩ S_p` is lower order; the correctness and heuristic cost of the
terminal-connection procedures; the *preprocessing* cost of computing Hilbert class
polynomials `H_D(X)` over `F_{p^2}` up to bound `M` (which the abstract says is
"estimated" but does not state, and which could dominate at cryptographic `p`); the
experimental speedup factors, the parameter sizes at which they were measured, and
whether the "small parameters" extrapolate; and the memory footprint of the CM table at
SQIsign parameters. **No isogeny parameter set should be re-costed on the basis of this
entry.** The characterisation of Delfs–Galbraith/SuperSolver as the baseline was not
independently cross-checked against `KN-TECH-029`'s sources.
