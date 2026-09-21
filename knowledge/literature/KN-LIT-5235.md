---
id: KN-LIT-5235
type: literature
title: "Nonce-Based Cryptography: Retaining Security when Randomness Fails"
authors:
  - "Mihir Bellare"
  - "Björn Tackmann"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, protocol, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We take nonce-based cryptography beyond symmetric encryption, developing it as a broad and practical way to mitigate damage caused by failures in randomness, whether inadvertent (bugs) or malicious (subversion). We focus on definitions and constructions for noncebased public-key encryption and briefly treat nonce-based signatures.

## Key claims (as reported)
- We introduce and construct hedged extractors as a general tool in this domain.
- Our nonce-based PKE scheme guarantees that if the adversary wants to violate IND-CCA security then it must do both of the following: (1) fully compromise the RNG (2) penetrate the sender system to exfiltrate a seed used by the sender.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650274 (1).pdf`
- `downloads/96650274.pdf`
