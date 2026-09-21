---
id: KN-LIT-303
type: literature
title: "A New Approach to Practical Active-Secure Two-Party Computation?"
authors:
  - "Jesper Buus Nielsen"
  - "Peter Sebastian Nordholt"
  - "Claudio Orlandi"
year: 2011
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2011/091"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2011/091"
tags: [fhe, hash, mpc, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new approach to practical two-party computation secure against an active adversary. All prior practical protocols were based on Yao’s garbled circuits.

## Key claims (as reported)
- We use an OT-based approach and get efficiency via OT extension in the random oracle model.
- To get a practical protocol we introduce a number of novel techniques for relating the outputs and inputs of OTs in a larger construction.
- We also report on an implementation of this approach, that shows that our protocol is more efficient than any previous one: For big enough circuits, we can evaluate more than 20000 Boolean gates per second.
- As an example, evaluating one oblivious AES encryption (∼ 34000 gates) takes 64 seconds, but when repeating the task 27 times it only takes less than 3 seconds per instance.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170674 (1).pdf`
- `downloads/74170674 (2).pdf`
- `downloads/74170674 (3).pdf`
- `downloads/74170674 (4).pdf`
- `downloads/74170674.pdf`
