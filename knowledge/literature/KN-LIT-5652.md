---
id: KN-LIT-5652
type: literature
title: "Optimal Forgeries Against Polynomial-Based MACs and GCM"
authors:
  - "Atul Luykx"
  - "Bart Preneel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, mov-fr, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Polynomial-based authentication algorithms, such as GCM and Poly1305, have seen widespread adoption in practice. Due to their importance, a significant amount of attention has been given to understanding and improving both proofs and attacks against such schemes.

## Key claims (as reported)
- At EUROCRYPT 2005, Bernstein published the best known analysis of the schemes when instantiated with PRPs, thereby establishing the most lenient limits on the amount of data the schemes can process per key.
- A long line of work, initiated by Handschuh and Preneel at CRYPTO 2008, finds the best known attacks, advancing our understanding of the fragility of the schemes.
- Yet surprisingly, no known attacks perform as well as the predicted worst-case attacks allowed by Bernstein’s analysis, nor has there been any advancement in proofs improving Bernstein’s bounds, and the gap between attacks and analysis is significant.
- We settle the issue by finding a novel attack against polynomial-based authentication algorithms using PRPs, and combine it with new analysis, to show that Bernstein’s bound, and our attacks, are optimal.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822253 (1).pdf`
- `downloads/10822253.pdf`
- `downloads/10993158 (1).pdf`
- `downloads/10993158.pdf`
