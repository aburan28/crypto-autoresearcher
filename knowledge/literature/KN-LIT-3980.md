---
id: KN-LIT-3980
type: literature
title: "Fully Adaptive Schnorr Threshold Signatures"
authors:
  - "Elizabeth Crites"
  - "Chelsea Komlo"
  - "Mary Maller"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We prove adaptive security of a simple three-round threshold Schnorr signature scheme, which we call Sparkle. The standard notion of security for threshold signatures considers a static adversary – one who must declare which parties are corrupt at the beginning of the protocol.

## Key claims (as reported)
- The stronger adaptive adversary can at any time corrupt parties and learn their state.
- This notion is natural and practical, yet not proven to be met by most schemes in the literature.
- In this paper, we demonstrate that Sparkle achieves several levels of security based on different corruption models and assumptions.
- To begin with, Sparkle is statically secure under minimal assumptions: the discrete logarithm assumption (DL) and the random oracle model (ROM).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850182 (1).pdf`
- `downloads/140850182.pdf`
