---
id: KN-LIT-4190
type: literature
title: "Hiding in Plain Sight: Memory-tight Proofs via Randomness Programming"
authors:
  - "Ashrujit Ghoshal"
  - "Riddhi Ghosal"
  - "Joseph Jaeger"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, elliptic-curve, finite-field, lattice, mov-fr, pairing, provable-security, rsa, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper continues the study of memory-tight reductions (Auerbach et al, CRYPTO ’17). These are reductions that only incur minimal memory costs over those of the original adversary, allowing precise security statements for memory-bounded adversaries (under appropriate assumptions expressed in terms of adversary time and memory usage).

## Key claims (as reported)
- Despite its importance, only a few techniques to achieve memorytightness are known and impossibility results in prior works show that even basic, textbook reductions cannot be made memory-tight.
- This paper introduces a new class of memory-tight reductions which leverage random strings in the interaction with the adversary to hide state information, thus shifting the memory costs to the adversary.
- We exhibit this technique with several examples.
- We give memory-tight proofs for digital signatures allowing many forgery attempts when considering randomized message distributions or probabilistic RSA-FDH signatures specifically.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760193 (1).pdf`
- `downloads/132760193.pdf`
