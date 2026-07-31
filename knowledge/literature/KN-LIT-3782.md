---
id: KN-LIT-3782
type: literature
title: "Fast Algorithms for the Free Riders Problem in Broadcast Encryption"
authors:
  - "Zulfikar Ramzan"
  - "David P. Woodruff"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide algorithms to solve the free riders problem in broadcast encryption. In this problem, the broadcast server is allowed to choose some small subset F of the revoked set R of users to allow to decrypt the broadcast, despite having been revoked.

## Key claims (as reported)
- This may allow the server to significantly reduce network traffic while only allowing a small set of non-privileged users to decrypt the broadcast.
- Although there are worst-case instances of broadcast encryption schemes where the free riders problem is difficult to solve (or even approximate), we show that for many specific broadcast encryption schemes, there are efficient algorithms.
- In particular, for the complete subtree method [25] and some other schemes in the subset-cover framework, we show how to find the optimal assignment of free riders in O(|R||F |) time, which is independent of the total number of users.
- We also define an approximate version of this problem, and study specific distributions of R for which this relaxation yields even faster algorithms.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170305 (1).pdf`
- `downloads/41170305 (2).pdf`
- `downloads/41170305 (3).pdf`
- `downloads/41170305.pdf`
