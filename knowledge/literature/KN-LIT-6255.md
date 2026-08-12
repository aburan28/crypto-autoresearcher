---
id: KN-LIT-6255
type: literature
title: "Revisiting AES-GCM-SIV: Multi-user Security"
authors:
  - "Faster Key Derivation"
  - "Better Bounds"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper revisits the multi-user (mu) security of symmetric encryption, from the perspective of delivering an analysis of the AES-GCM-SIV AEAD scheme. Our end result shows that its mu security is comparable to that achieved in the single-user setting.

## Key claims (as reported)
- In particular, even when instantiated with short keys (e.g., 128 bits), the security of AES-GCM-SIV is not impacted by the collisions of two user keys, as long as each individual nonce is not re-used by too many users.
- Our bounds also improve existing analyses in the single-user setting, in particular when messages of variable lengths are encrypted.
- We also validate security against a general class of key-derivation methods, including one that halves the complexity of the final proposal.
- As an intermediate step, we consider mu security in a setting where the data processed by every user is bounded, and where user keys are generated according to arbitrary, possibly correlated distributions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822313 (1).pdf`
- `downloads/10822313.pdf`
