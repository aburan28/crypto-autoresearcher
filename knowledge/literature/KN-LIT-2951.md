---
id: KN-LIT-2951
type: literature
title: "Collision-resistant No More: Hash-and-sign Paradigm Revisited Ilya Mironov"
authors:
  - "Microsoft Research (Silicon Valley Campus)"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A signature scheme constructed according to the hash-andsign paradigm—hash the message and then sign the hash, symbolically σ(H(M ))—is no more secure than the hash function H against a collisionfinding attack. Recent attacks on standard hash functions call the paradigm into question.

## Key claims (as reported)
- It is well known that a simple modification of the hash-and-sign paradigm may replace the collision-resistant hash with a weaker primitive—a target-collision resistant hash function (also known as a universal one-way hash, UOWHF).
- The signer generates a random key k and outputs the pair (k, σ(k||Hk (M ))) as a signature on M .
- The apparent problem with this approach is the increase in the signature size.
- In this paper we demonstrate that for three concrete signature schemes, DSA, PSS-RSA, and Cramer-Shoup, the message can be hashed simultaneously with computing the signature, using one of the signature’s components as the key for the hash function.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/39580141 (1).pdf`
- `downloads/39580141 (2).pdf`
- `downloads/39580141 (3).pdf`
- `downloads/39580141.pdf`
