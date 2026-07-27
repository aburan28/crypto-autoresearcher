---
id: KN-LIT-4082
type: literature
title: "Generic Attacks against Beyond-Birthday-Bound MACs"
authors:
  - "Gaëtan Leurent"
  - "Mridul Nandi"
  - "Ferdinand Sibleyras"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, pollard-rho, protocol, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we study the security of several recent MAC constructions with provable security beyond the birthday bound. We consider block-cipher based constructions with a double-block internal state, such as SUM-ECBC, PMAC+, 3kf9, GCM-SIV2, and some variants (LightMAC+, 1kPMAC+).

## Key claims (as reported)
- All these MACs have a security proof up to 22n/3 queries, but there are no known attacks with less than 2n queries.
- We describe a new cryptanalysis technique for double-block MACs based on finding quadruples of messages with four pairwise collisions in halves of the state.
- We show how to detect such quadruples in SUM-ECBC, PMAC+, 3kf9, GCM-SIV2 and their variants with O(23n/4 ) queries, and how to build a forgery attack with the same query complexity.
- The time complexity of these attacks is above 2n , but it shows that the schemes do not reach full security in the information theoretic model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993269 (1).pdf`
- `downloads/10993269.pdf`
