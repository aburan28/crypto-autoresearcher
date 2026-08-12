---
id: KN-LIT-6355
type: literature
title: "Salvaging Merkle-Damgård for Practical Applications"
authors:
  - "Yevgeniy Dodis"
  - "Thomas Ristenpart"
  - "Thomas Shrimpton"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many cryptographic applications of hash functions are analyzed in the random oracle model. Unfortunately, most concrete hash functions, including the SHA family, use the iterative (strengthened) Merkle-Damgård transform applied to a corresponding compression function.

## Key claims (as reported)
- Moreover, it is well known that the resulting “structured” hash function cannot be generically used as a random oracle, even if the compression function is assumed to be ideal.
- This leaves a large disconnect between theory and practice: although no attack is known for many concrete applications utilizing existing (Merkle-Damgård based) hash functions, there is no security guarantee either, even by idealizing the compression function.
- Motivated by this question, we initiate a rigorous and modular study of developing new notions of (still idealized) hash functions which would be (a) natural and elegant; (b) sufficient for arguing security of important applications; and (c) provably met by the (strengthened) MerkleDamgård transform, applied to a “strong enough” compression function.
- In particular, we develop two such notions satisfying (a)-(c): a preimage aware function ensures that the attacker cannot produce a “useful” output of the function without already “knowing” the corresponding preimage, and a public-use random oracle, which is a random oracle that reveals to attackers messages queried by honest parties.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790371 (1).pdf`
- `downloads/54790371 (2).pdf`
- `downloads/54790371 (3).pdf`
- `downloads/54790371.pdf`
