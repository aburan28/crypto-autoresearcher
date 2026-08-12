---
id: KN-LIT-4272
type: literature
title: "How to Construct an Ideal Cipher from a Small Set of Public Permutations"
authors:
  - "Rodolphe Lampe"
  - "Yannick Seurin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show how to construct an ideal cipher with n-bit blocks and n-bit keys (i.e. a set of 2n public n-bit permutations) from a small constant number of n-bit random public permutations. The construction that we consider is the single-key iterated Even-Mansour cipher, which encrypts a plaintext x ∈ {0, 1}n under a key k ∈ {0, 1}n by alternatively xoring the key k and applying independent random public n-bit permutations P1 , . . . , Pr (this construction is also named a keyalternating cipher).

## Key claims (as reported)
- We analyze this construction in the plain indifferentiability framework of Maurer, Renner, and Holenstein (TCC 2004), and show that twelve rounds are sufficient to achieve indifferentiability from an ideal cipher.
- We also show that four rounds are necessary by exhibiting attacks for three rounds or less.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82710226 (1).pdf`
- `downloads/82710226 (2).pdf`
- `downloads/82710226 (3).pdf`
- `downloads/82710226.pdf`
