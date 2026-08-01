---
id: KN-LIT-3768
type: literature
title: "Factoring Products of Braids via Garside Normal Form"
authors:
  - "Simon-Philipp Merz"
  - "Christophe Petit"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, ecdlp, elliptic-curve, factoring, finite-field, isogeny, lattice, pairing, protocol, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Braid groups are infinite non-abelian groups naturally arising from geometric braids. For two decades they have been proposed for cryptographic use.

## Key claims (as reported)
- In braid group cryptography public braids often contain secret braids as factors and it is hoped that rewriting the product of braid words hides individual factors.
- We provide experimental evidence that this is in general not the case and argue that under certain conditions parts of the Garside normal form of factors can be found in the Garside normal form of their product.
- This observation can be exploited to decompose products of braids of the form ABC when only B is known.
- Our decomposition algorithm yields a universal forgery attack on WalnutDSATM , which is one of the 20 proposed signature schemes that are being considered by NIST for standardization of quantum-resistant public-key cryptography.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420121 (1).pdf`
- `downloads/114420121.pdf`
