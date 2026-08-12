---
id: KN-LIT-7480
type: literature
title: "VSH, an Efficient and Provable Collision-Resistant Hash Function"
authors:
  - "Scott Contini"
  - "Arjen K. Lenstra"
  - "Ron Steinfeld"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, factoring, hash, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce VSH, very smooth hash, a new S-bit hash function that is provably collision-resistant assuming the hardness of finding nontrivial modular square roots of very smooth numbers modulo an Sbit composite. By very smooth, we mean that the smoothness bound is some fixed polynomial function of S.

## Key claims (as reported)
- We argue that finding collisions for VSH has the same asymptotic complexity as factoring using the Number Field Sieve factoring algorithm, i.e., subexponential in S.
- VSH is theoretically pleasing because it requires just a single multiplication modulo the S-bit composite per Ω(S) message-bits (as opposed to O(log S) message-bits for previous provably secure hashes).
- It is relatively practical.
- A preliminary implementation on a 1GHz Pentium III processor that achieves collision resistance at least equivalent to the difficulty of factoring a 1024-bit RSA modulus, runs at 1.1 MegaByte per second, with a moderate slowdown to 0.7MB/s for 2048-bit RSA security.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40040166 (1).pdf`
- `downloads/40040166 (2).pdf`
- `downloads/40040166 (3).pdf`
- `downloads/40040166.pdf`
