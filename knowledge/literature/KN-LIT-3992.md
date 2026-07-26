---
id: KN-LIT-3992
type: literature
title: "Fully Homomorphic Encryption without Modulus Switching from Classical GapSVP"
authors:
  - "Zvika Brakerski⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new tensoring technique for LWE-based fully homomorphic encryption. While in all previous works, the ciphertext noise grows quadratically (B → B 2 · poly(n)) with every multiplication (before “refreshing”), our noise only grows linearly (B → B · poly(n)).

## Key claims (as reported)
- We use this technique to construct a scale-invariant fully homomorphic encryption scheme, whose properties only depend on the ratio between the modulus q and the initial noise level B, and not on their absolute values.
- Our scheme has a number of advantages over previous candidates: It uses the same modulus throughout the evaluation process (no need for “modulus switching”), and this modulus can take arbitrary form.
- In addition, security can be classically reduced from the worst-case hardness of the GapSVP problem (with quasi-polynomial approximation factor), whereas previous constructions could only exhibit a quantum reduction from GapSVP.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170863 (1).pdf`
- `downloads/74170863 (2).pdf`
- `downloads/74170863 (3).pdf`
- `downloads/74170863.pdf`
