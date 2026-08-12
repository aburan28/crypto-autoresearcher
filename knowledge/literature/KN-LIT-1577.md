---
id: KN-LIT-1577
type: literature
title: "Breaking ACDGV MinRank Gabidulin encryption schemes over matrix codes"
authors:
  - "Thai Hung Le"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/972"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/972"
tags: [cryptanalysis, groebner, pqc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Enhanced Gabidulin Matrix Codes (EGMC), introduced by Aragon, Couvreur, Dyseryn, Gaborit, and Vinçotte at Asiacrypt 2024, were designed to hide the algebraic structure of Gabidulin matrix codes while enabling very compact McEliece- and Niederreiter-type encryption schemes, with ciphertexts as small as 65 bytes at the claimed 128-bit security level. Their security relies on the assumption that a masked EGMC code is hard to distinguish from a random matrix code.

## Key claims (as reported)
- We show that this enhanced construction leaves enough structure for an equivalent code of the secret key to be recovered.
- Unlike previous cryptanalysis [12], our attack combines combinatorial and algebraic techniques to recover a Gabidulin-equivalent compressed code.
- This code can then be extended to a full-length equivalent secret key in polynomial time.
- As a result, the attack provides both a distinguisher and a key-recovery attack against the EGMC encryption schemes.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-972.pdf`
