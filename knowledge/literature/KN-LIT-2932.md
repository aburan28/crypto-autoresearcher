---
id: KN-LIT-2932
type: literature
title: "Coded-BKW with Sieving"
authors:
  - "Qian Guo"
  - "Thomas Johansson"
  - "Erik Mårtensson"
  - "Paul Stankovski"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, groebner, lattice, pairing, pqc, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Learning with Errors problem (LWE) has become a central topic in recent cryptographic research. In this paper, we present a new solving algorithm combining important ideas from previous work on improving the BKW algorithm and ideas from sieving in lattices.

## Key claims (as reported)
- The new algorithm is analyzed and demonstrates an improved asymptotic performance.
- For Regev parameters q = n2 and noise level σ = √ 1.5 2 n /( 2π log2 n), the asymptotic complexity is 20.895n in the standard setting, improving on the previously best known complexity of roughly 20.930n .
- Also for concrete parameter instances, improved performance is indicated.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240219 (1).pdf`
- `downloads/106240219.pdf`
