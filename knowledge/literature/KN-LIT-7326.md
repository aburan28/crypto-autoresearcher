---
id: KN-LIT-7326
type: literature
title: "Two-Tier Signatures, Strongly Unforgeable Signatures, and Fiat-Shamir without Random Oracles"
authors:
  - "Mihir Bellare"
  - "Sarah Shoup"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a positive result about the Fiat-Shamir (FS) transform in the standard model, showing how to use it to convert threemove identification protocols into two-tier signature schemes with a proof of security that makes a standard assumption on the hash function rather than modeling it as a random oracle. The result requires security of the starting protocol against concurrent attacks.

## Key claims (as reported)
- We can show that numerous protocols have the required properties and so obtain numerous efficient two-tier schemes.
- Our first application is a two-tier scheme based transform of any unforgeable signature scheme into a strongly unforgeable one.
- (This extends Boneh, Shen and Waters [8] whose transform only applies to a limited class of schemes.) The second application is new one-time signature schemes that, compared to one-way function based ones of the same computational cost, have smaller key and signature sizes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/44500201 (1).pdf`
- `downloads/44500201 (2).pdf`
- `downloads/44500201 (3).pdf`
- `downloads/44500201.pdf`
