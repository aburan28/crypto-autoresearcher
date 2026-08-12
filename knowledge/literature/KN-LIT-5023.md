---
id: KN-LIT-5023
type: literature
title: "Multi-user Schnorr security, revisited"
authors:
  - "IL –"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdsa, elliptic-curve, pairing, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Three recent proposals for standardization of next-generation ECC signatures have included “key prefixing” modifications to Schnorr’s signature system. Bernstein, Duif, Lange, Schwabe, and Yang stated in 2011 that key prefixing is “an inexpensive way to alleviate concerns that several public keys could be attacked simultaneously”.

## Key claims (as reported)
- However, a 2002 theorem by Galbraith, Malone-Lee, and Smart states that, for the classic Schnorr signature system, single-key security tightly implies multi-key security.
- Struik and then Hamburg, citing this theorem, argued that key prefixing was unnecessary for multi-user security and should not be standardized.
- This paper identifies an error in the 2002 proof, and an apparently insurmountable obstacle to the claimed theorem.
- The proof idea does, however, lead to a different theorem, stating that single-key security of the classic Schnorr signature system tightly implies multi-key security of the key-prefixed variant of the system.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/multischnorr-20151012.pdf`
