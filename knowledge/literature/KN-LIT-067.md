---
id: KN-LIT-067
type: literature
title: Breaking SIDH in Polynomial Time
authors: [Robert Damien]
year: 2023
venue: EUROCRYPT 2023, LNCS 14008, pp. 472-503 (ePrint 2022)
identifiers:
  eprint: iacr:2022/1038
  doi: 10.1007/978-3-031-30589-4_17
  url: https://eprint.iacr.org/2022/1038
tags: [sidh, cryptanalysis, higher-dimensional-isogeny, abelian-variety, polynomial-time, key-recovery, isogeny, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Proves a fully (classical) POLYNOMIAL-TIME attack on SIDH in ALL cases, including
a random/arbitrary starting curve, removing the heuristics and GRH /
known-endomorphism-ring caveats of the abelian-surface attacks (KN-LIT-065,
KN-LIT-066). Embeds the secret isogeny into higher-dimensional abelian varieties
-- dimension-4 or dimension-8 isogenies -- where it is always reconstructible from
the torsion-point images.

## Key claims (as reported)
- The higher dimension guarantees the required reducible/decomposable structure
  ALWAYS exists, yielding a provable (not heuristic) polynomial-time result.
- Completes the trio of 2022 breaks: Castryck-Decru (heuristic, special curve),
  Maino-Martindale et al. (subexponential, arbitrary curve), Robert (provable
  poly-time, all cases).

## Relevance to this program
The strongest form of the auxiliary-information collapse: raising the embedding
dimension makes the torsion-image attack UNCONDITIONALLY efficient (KN-TECH-026).
A vivid instance of the program's theme that added structure can convert an
apparently exponential problem into a provably polynomial one (KN-OPEN-015).
Adjacent to the ECDLP mission (supersingular isogeny / abelian-variety setting).

## Not verified here
Full paper not read; the dimension-4/8 embedding and provable-poly-time claim
relayed from the abstract (hence confidence: reported). Fields confirmed against
IACR ePrint 2022/1038 and the Springer DOI via search, not by fetching the primary
pages.
