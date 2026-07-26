---
id: KN-LIT-2935
type: literature
title: "Coefficient Grouping: Breaking Chaghri and More"
authors:
  - "Fukang Liu"
  - "Ravi Anand"
  - "Libo Wang"
  - "Willi Meier"
  - "Takanori Isobe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, finite-field, groebner, hash, mpc, quantum, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose an efficient technique called coefficient grouping to evaluate the algebraic degree of the FHE-friendly cipher Chaghri, which has been accepted for ACM CCS 2022. It is found that the algebraic degree increases linearly rather than exponentially.

## Key claims (as reported)
- As a consequence, we can construct a 13-round distinguisher with time and data complexity of 263 and mount a 13.5-round key-recovery attack.
- In particular, a higherorder differential attack on 8 rounds of Chaghri can be achieved with time and data complexity of 238 .
- Hence, it indicates that the full 8 rounds are far from being secure.
- Furthermore, we also demonstrate the application of our coefficient grouping technique to the design of secure cryptographic components.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004039 (1).pdf`
- `downloads/14004039.pdf`
