---
id: KN-LIT-4487
type: literature
title: "Indistinguishability Obfuscation from Compact Functional Encryption"
authors:
  - "Prabhanjan Ananth"
  - "Abhishek Jain"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The arrival of indistinguishability obfuscation (iO) has transformed the cryptographic landscape by enabling several security goals that were previously beyond our reach. Consequently, one of the pressing goals currently is to construct iO from well-studied standard cryptographic assumptions.

## Key claims (as reported)
- In this work, we make progress in this direction by presenting a reduction from iO to a natural form of public-key functional encryption (FE).
- Specifically, we construct iO for general functions from any single-key FE scheme for NC1 that achieves selective, indistinguishability security against sub-exponential time adversaries.
- Further, the FE scheme should be compact, namely, the running time of the encryption algorithm must only be a polynomial in the security parameter and the input message length (and not in the function description size or its output length).
- We achieve this result by developing a novel arity amplification technique to transform FE for single-ary functions into FE for multi-ary functions (aka multi-input FE).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160339 (1).pdf`
- `downloads/92160339 (2).pdf`
- `downloads/92160339.pdf`
