---
id: KN-LIT-4823
type: literature
title: "Luby-Rackoff Backwards with More Users and More Security"
authors:
  - "Srimanta Bhattacharya"
  - "Mridul Nandi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
It is known, from the work of Dai et al. (in CRYPTO’17), that the PRF advantage of XORP (bitwise-xor of two outputs of n-bit random permutations with domain separated inputs), against an adversary making q queries, is about q/2n for q ≤ 2n−5 .

## Key claims (as reported)
- The same bound can be easily shown to hold for XORP[k] (bitwise-xor of k outputs n-bit pseudorandom random permutations with domain separated inputs), for k ≥ 3.
- In this work, we first consider multi-user security of XORP[3].
- We √ show that the multi-user PRF advantage of XORP[3] is about uqmax /2n n for all qmax ≤ 2 /12, where u is the number of users and qmax is the maximum number of queries the adversary can make to each user.
- In the multi-user setup, this implies that XORP[3] gives security for O(2n ) users even allowing almost O(2n ) queries to each user.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900031 (1).pdf`
- `downloads/130900031.pdf`
