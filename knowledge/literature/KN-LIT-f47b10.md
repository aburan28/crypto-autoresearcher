---
id: KN-LIT-f47b10
type: literature
title: "Random Walks Revisited: Extensions of Pollard's Rho Algorithm for Computing Multiple Discrete Logarithms"
authors:
  - "Fabian Kuhn"
  - "René Struik"
year: 2001
venue: "SAC 2001, LNCS 2259, pp. 212-229"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/3-540-45537-X_17"
  url: null
tags: [pollard-rho, multi-target, batch-dlp, collision-search, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Solving L discrete logarithms in one group by keeping the distinguished points from earlier solves, so later logarithms are cheaper. Related: Hitchcock-Montague-Carter-Dawson, "The efficiency of solving multiple discrete logarithm problems and the implications for the security of fixed elliptic curves", IJIS 3:86-98 (2004), doi:10.1007/s10207-004-0045-9; and the matching generic lower bound by Yun, EUROCRYPT 2015, LNCS 9057, pp. 817-836, doi:10.1007/978-3-662-46803-6_27.

## Key claims (as reported)

- Total cost for L logarithms grows roughly like sqrt(L*n) rather than L*sqrt(n) (standard statement; exact constant not re-verified).

## Relevance to this program

Solving L discrete logs costs ≈ √(2Ln) total by reusing distinguished points. The program's prime-field 'ic prime' batch pipeline (cryptanalysis suite/docs/ic) reaching 0.72–0.89 of the folded Kuhn–Struik expectation is measured against this; batch 'speedups' over per-target rho are this paper, not index calculus.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
