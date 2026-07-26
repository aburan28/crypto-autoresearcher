---
id: KN-LIT-2683
type: literature
title: "Better than Advertised Security for Non-Interactive Threshold Signatures Mihir Bellare1[0000000287655573]"
authors:
  - "Mary Maller"
  - "Stefano Tessaro"
  - "Chenzhi Zhu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, mov-fr, pairing, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a unified syntax, and a hierarchy of definitions of security of increasing strength, for non-interactive threshold signature schemes. These are schemes having a single-round signing protocol, possibly with one prior round of message-independent pre-processing.

## Key claims (as reported)
- We fit FROST1 and BLS, which are leading practical schemes, into our hierarchy, in particular showing they meet stronger security definitions than they have been shown to meet so far.
- We also fit in our hierarchy a more efficient version FROST2 of FROST1 that we give.
- These definitions and results, for simplicity, all assume trusted key generation.
- Finally, we prove the security of FROST2 with key generation performed by an efficient distributed key generation protocol.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070469 (1).pdf`
- `downloads/135070469.pdf`
