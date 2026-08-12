---
id: KN-LIT-4260
type: literature
title: "How to Avoid Obfuscation Using Witness PRFs"
authors:
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [glv-gls, mpc, pairing, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new cryptographic primitive called witness pseudorandom functions (witness PRFs). Witness PRFs are related to witness encryption, but appear strictly stronger: we show that witness PRFs can be used for applications such as multi-party key exchange without trusted setup, polynomially-many hardcore bits for any one-way function, and several others that were previously only possible using obfuscation.

## Key claims (as reported)
- Thus we improve the minimal assumptions required for these applications.
- Moreover, current candidate obfuscators are far from practical and typically rely on unnatural hardness assumptions about multilinear maps.
- We give a construction of witness PRFs from multilinear maps that is simpler and much more efficient than current obfuscation candidates, thus bringing several applications of obfuscation closer to practice.
- Our construction relies on new but very natural hardness assumptions about the underlying maps that appear to be resistant to a recent line of attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/95621006 (1).pdf`
- `downloads/95621006.pdf`
