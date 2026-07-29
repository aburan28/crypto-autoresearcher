---
id: KN-LIT-4053
type: literature
title: "Garbled RAM Revisited"
authors:
  - "Craig Gentry"
  - "Shai Halevi"
  - "Steve Lu"
  - "Rafail Ostrovsky"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
, simplify and generalize the main ideas behind the Lu-Ostrovsky construction, and show two alternatives constructions that overcome the circularity of assumptions. Our first construction breaks the circularity by replacing the PRF-based encryption in the Lu-Ostrovsky construction by identity-based encryption (IBE).

## Key claims (as reported)
- The result retains the same asymptotic performance characteristics of the original Lu-Ostrovsky construction, namely overhead of O(poly(κ)polylog(n)) (with κ the security parameter and n the data size).
- Our second construction breaks the circularity assuming only the existence of one way functions, but with overhead O(poly(κ)nε ) for any constant ε > 0.
- This construction works by adaptively “revoking” the PRFs at selected points, and using a delicate recursion argument to get successively better performance characteristics.
- It remains as an interesting open problem to achieve an overhead of poly(κ)polylog(n) assuming only the existence of one-way functions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410175 (1).pdf`
- `downloads/84410175 (2).pdf`
- `downloads/84410175 (3).pdf`
- `downloads/84410175.pdf`
