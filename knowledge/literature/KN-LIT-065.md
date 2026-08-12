---
id: KN-LIT-065
type: literature
title: An efficient key recovery attack on SIDH
authors: [Castryck Wouter, Decru Thomas]
year: 2023
venue: EUROCRYPT 2023, LNCS 14008, pp. 423-447 (ePrint 2022)
identifiers:
  eprint: iacr:2022/975
  doi: 10.1007/978-3-031-30589-4_15
  url: https://eprint.iacr.org/2022/975
tags: [sidh, sike, cryptanalysis, torsion-points, kani, abelian-surface, key-recovery, isogeny, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
The first break of SIDH: recovers Bob's secret key in *heuristically polynomial*
time by exploiting the torsion-point images the protocol publishes, via Kani's
reducibility criterion (KN-LIT-068). The secret isogeny is embedded into a
reducible principally polarized abelian surface (a product of elliptic curves
reached by a (2,2)-isogeny chain), which "glue-and-split" detects.

## Key claims (as reported)
- Classical time polynomial in the input (heuristic), aside from factoring a few
  parameter-dependent integers; a Magma implementation broke SIKEp434 (NIST
  level 1) in ~10 minutes on one core.
- As first presented, assumed a special starting curve with known small-degree
  endomorphism structure (removed by KN-LIT-066, KN-LIT-067).

## Relevance to this program
The canonical example of AUXILIARY INFORMATION (published torsion-point images)
collapsing a problem believed exponentially hard -- methodologically central to
this repo's theme that extra algebraic structure/information changes
cryptanalytic complexity (cf. the program's ECDLP transfer/cover attacks,
RQ-ISO-001, and the "does auxiliary structure lower the complexity driver?"
questions KN-OPEN-005). Supersingular-isogeny setting (F_{p^2}); adjacent to the
ordinary-prime-field ECDLP mission, sharing isogeny/Velu machinery.

## Not verified here
Full paper not read; the glue-and-split mechanism and the SIKEp434 timing relayed
from the abstract (hence confidence: reported). Fields confirmed against IACR
ePrint 2022/975 and the Springer DOI via search, not by fetching the primary
pages.
