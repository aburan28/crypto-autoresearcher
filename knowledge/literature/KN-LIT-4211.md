---
id: KN-LIT-4211
type: literature
title: "Higher Order Universal One-Way Hash Functions from the Subset Sum Assumption"
authors:
  - "Ron Steinfeld"
  - "Josef Pieprzyk"
  - "Huaxiong Wang"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Universal One-Way Hash Functions (UOWHFs) may be used in place of collision-resistant functions in many public-key cryptographic applications. At Asiacrypt 2004, Hong, Preneel and Lee introduced the stronger security notion of higher order UOWHFs to allow construction of long-input UOWHFs using the Merkle-Damgård domain extender.

## Key claims (as reported)
- However, they did not provide any provably secure constructions for higher order UOWHFs.
- We show that the subset sum hash function is a kth order Universal OneWay Hash Function (hashing n bits to m < n bits) under the Subset Sum assumption for k = O(log m).
- Therefore we strengthen a previous result of Impagliazzo and Naor, who showed that the subset sum hash function is a UOWHF under the Subset Sum assumption.
- We believe our result is of theoretical interest; as far as we are aware, it is the first example of a natural and computationally efficient UOWHF which is also a provably secure higher order UOWHF under the same well-known cryptographic assumption, whereas this assumption does not seem sufficient to prove its collision-resistance.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/39580158 (1).pdf`
- `downloads/39580158 (2).pdf`
- `downloads/39580158 (3).pdf`
- `downloads/39580158.pdf`
