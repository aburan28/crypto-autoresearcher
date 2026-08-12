---
id: KN-LIT-3396
type: literature
title: "Designing an ASIP for Cryptographic Pairings over Barreto-Naehrig Curves ?"
authors:
  - "Markus Langenberg"
  - "Dominik Auras"
  - "Gerd Ascheid"
  - "Rudolf Mathar"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdlp, elliptic-curve, finite-field, implementation, pairing, quantum, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a design-space exploration of an application-specific instruction-set processor (ASIP) for the computation of various cryptographic pairings over Barreto-Naehrig curves (BN curves). Cryptographic pairings are based on elliptic curves over finite fields—in the case of BN curves a field Fp of large prime order p.

## Key claims (as reported)
- Efficient arithmetic in these fields is crucial for fast computation of pairings.
- Moreover, computation of cryptographic pairings is much more complex than elliptic-curve cryptography (ECC) in general.
- Therefore, we facilitate programming of the proposed ASIP by providing a C compiler.
- In order to speed up Fp arithmetic, a RISC core is extended with additional scalable functional units.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470255 (1).pdf`
- `downloads/57470255 (2).pdf`
- `downloads/57470255 (3).pdf`
- `downloads/57470255.pdf`
