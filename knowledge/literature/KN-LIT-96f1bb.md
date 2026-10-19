---
id: KN-LIT-96f1bb
type: literature
title: "Isogeny volcanoes and the SEA algorithm"
authors:
  - "Mireille Fouquet"
  - "François Morain"
year: 2002
venue: "Algorithmic Number Theory (ANTS-V, Sydney, July 2002), Lecture Notes in Computer Science 2369, pp. 276-291, Springer"
identifiers:
  eprint: null
  doi: "10.1007/3-540-45455-1_23"
  arxiv: null
  url: "https://doi.org/10.1007/3-540-45455-1_23"
tags: [isogeny, volcano, endomorphism-ring, conductor, modular-polynomial, SEA, point-counting, ordinary, finite-field]
confidence: reported
citation_verified: metadata
added: "2026-10-12"
superseded_by: null
---

## Contribution
Introduces the name and the picture "isogeny volcano" for the graph of
rational ℓ-isogenies between ordinary elliptic curves over a finite field,
building on Kohel's thesis (KN-LIT-a4c123) on the conductor of the
endomorphism ring: the crater is the set of curves whose endomorphism ring is
maximal at ℓ, each level below it multiplies the ℓ-part of the conductor by
ℓ, and the floor is the level where the conductor of End(E) equals the ℓ-part
of the conductor of Z[π]. The paper shows how to walk the volcano with the
modular polynomials Φ_ℓ(X, Y) without knowing the cardinality of the curve,
and how the shape of the volcano (height and crater) yields information on
the Frobenius trace that the SEA point-counting algorithm can use.

## Key claims (as reported)
- The ℓ-isogeny graph of an ordinary isogeny class is a disjoint union of
  volcanoes; the level of a curve is v_ℓ of the conductor of End(E) and the
  height is v_ℓ of the conductor of Z[π].
- Rational ℓ-isogeny counts distinguish the levels: ℓ + 1 above the floor,
  1 on the floor; on the crater the number of horizontal edges is
  1 + (D_K / ℓ).
- Walking with Φ_ℓ (roots of Φ_ℓ(X, j) over F_q, non-backtracking)
  locates the floor and the crater, and the resulting local structure
  constrains t mod ℓ^k, which SEA exploits.

## Relevance to this program
The per-prime level vector (v_ℓ(f_E))_ℓ that the isogeny-stratified lane
records (RQ-VOLC-f6253b; `research/isogeny_stratified_ml_blueprint_triage_20261010/`)
is exactly the volcano position this paper defines; the crypto repository's
`isogeny_algos/src/path/volcano.rs`, `src/isogeny/volcano.rs` and the
binary-field walker in `isogeny_algos/examples/binary_level_yield.rs`
implement the walk. The 2002 construction underlies Sutherland's later
algorithms (KN-LIT-360, KN-LIT-251).

## Not verified here
Metadata (authors, venue, pages, DOI) verified on 2026-10-12 against the
publisher record and the first author's bibliography; the body above is
relayed from the abstract and from the secondary sources in this corpus, not
from a full read of the paper.
