---
id: KN-LIT-6935a1
type: literature
title: "The Four Faces of Lifting for the Elliptic Curve Discrete Logarithm Problem"
authors:
  - "Joseph H. Silverman"
year: 2007
venue: "11th Workshop on Elliptic Curve Cryptography (ECC 2007), Shannon Institute, Dublin, 5-7 September 2007 (invited talk slides)"
identifiers:
  doi: null
  arxiv: null
  url: null
tags: [ecdlp, lifting, xedni, index-calculus, canonical-height, formal-group, masser, mazur, serre, obstruction-taxonomy, prime-field, survey, ecc2007, slides]
confidence: reported
citation_verified: read
added: "2026-08-09"
superseded_by: null
---

## Contribution

A complete two-by-two taxonomy of *every* way one may try to lift a prime-field
ECDLP instance `(F_p, E, S, T)` with `T = mS` to characteristic zero, together
with the *distinct* structural obstruction that defeats each cell. The axes are
**local vs global** (the lift ring `R̂ ⊂ K̂` is `Z_p`-like or `Z`/`O_K`-like)
and **torsion vs nontorsion** (the lifted points `Ŝ, T̂` are torsion or not).
Silverman's framing is that ECDLP is "a castle with four walls", one lifting
army per wall, and that the instructive content is *why each army fails
differently*.

Read from the local corpus copy `downloads/ECC4FacesOfLifts.pdf`.

## The four faces and their obstructions (as reported)

| Face | Construction | Obstruction |
|---|---|---|
| **Local nontorsion** | Hensel-lift `S, T` to `Ê(Q_p)`; multiply by `N = #E(F_p)` into the formal group and read `m = log_F(N T̂)/log_F(N Ŝ)`. | **Consistency.** Each step to `p^{k+1}` admits `p` lifts; once `S_2` is fixed, exactly one of the `p` choices for `T_2` preserves `T_2 = m S_2`, and no method is known to make the consistent choice without already knowing `m`. |
| **Local torsion** | The lift of a point of order `n != p` to a point of order `n` in `E(Q_p)` is **unique**, so `T̂ = m Ŝ` is preserved automatically. | **Formal-group annihilation.** Multiplying by `n` to enter the formal group turns `T̂ = m Ŝ` into `Ô = m Ô`. No efficient method is known to solve ECDLP in `E(Q_p)` *without* passing through the formal logarithm. |
| **Global torsion** | Lift to `Ŝ, T̂ ∈ Ê(K)_tors`; then `T̂ = m Ŝ` may be read off modulo small primes and reassembled by CRT. | **Field degree / torsion size.** Mazur: `#Ê(Q)_tors <= 16`. Serre: a point of order `n` generally needs `[K:Q] >= c·#GL_2(Z/nZ) ≈ c·n^4`. |
| **Global nontorsion, "easy" method** | Use linear algebra to force a cubic form through up to 9 prescribed lifted points `Q̂_i` (10 coefficients); if `rank Ê(Q) <= 8` find a relation by descent/heights and reduce mod `p`. | **Masser independence.** For a parameterised family, the parameter set where prescribed independent sections become dependent has density zero; the slide states this suggests dependency probability below `1/p`. Rank-lowering heuristics (BSD-flavoured) do not repair it. |
| **Global nontorsion, "hard" method** (xedni-flavoured) | Lift `E` and `S` only, hope `rank Ê(Q) = 1`, then *find* the lift `T̂` of `T`. | **Canonical height.** `T̂ = m Ŝ` forces `ĥ(T̂) = m^2 ĥ(Ŝ)`, so `T̂`'s coordinates have size exponential in `m^2`; the slide's worked `m = 5` example already has 23-digit numerators, and `m = 53` would have "thousands of digits". No algorithm is known to find `T̂` even when it is known to exist. |

The worked example throughout is `E: Y^2 = X^3 + 23X + 11` over `F_257`, with
`S = (7,1)`; the hard-lifting example exhibits `T̂ = 5Ŝ` explicitly.

## Key claims (as reported)

- The four cells are presented as an exhaustive enumeration of *lifting* attacks
  on prime-field ECDLP in characteristic zero. Global-nontorsion splits into an
  easy and a hard sub-method with different obstructions, so the practical count
  of distinct obstructions is five.
- None of the routes succeeds; each fails for a *different* reason, and the
  reasons are not interchangeable.
- The talk is a survey/synthesis with worked examples, not a new algorithm and
  not a proof of impossibility. It states no theorem of the form "no lift can
  work"; each cell is closed by a named theorem (Mazur, Serre, Masser) or by an
  explicit "no method is known" (local nontorsion consistency, local torsion
  non-formal solution, hard-lift search).

## Relevance

- Directly serves `KN-OPEN-019` ("what object does each ECDLP attack family
  track, and is that enumeration closed?"). This is the first primary source in
  the corpus that supplies an explicit, author-asserted *exhaustive* enumeration
  for the lifting family together with per-cell obstructions.
- Indexes this program's whole lifting/xedni lane. See `KN-TECH-06bb4e` for the
  cell assignment of the program's own lifting records, including the
  **function-field fifth face** (`F_p(t)` lifts) that Silverman's characteristic-zero
  grid does not cover, and which is where `KN-FIND-003`/`004`/`005`/`010`/`011`
  actually live.
- The local-torsion cell is sharpened by this program in `KN-TECH-3b593f` and
  reopened as `KN-OPEN-3417fc`: reduction restricted to prime-to-`p` torsion is
  a group *isomorphism*, so the cell is closed for every group-theoretic
  invariant, and only coordinate/valuation invariants remain.
- The canonical-height obstruction is the exact obstruction named by active idea
  `ECDLP-IDEA-005` (height-compressing global lift); the Masser obstruction is
  the one that `ECDLP-IDEA-435` proposes to test directly in the function-field
  face.
- No breakthrough content. This is `LITERATURE-DERIVED` context and an
  obstruction map, not evidence for or against any candidate algorithm.
