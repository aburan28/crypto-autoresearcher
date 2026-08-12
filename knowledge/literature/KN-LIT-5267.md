---
id: KN-LIT-5267
type: literature
title: "Oblivious Hashing Revisited, and Applications to"
authors:
  - "Asymptotically Efficient ORAM"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Oblivious RAM (ORAM) is a powerful cryptographic building block that allows a program to provably hide its access patterns to sensitive data. Since the original proposal of ORAM by Goldreich and Ostrovsky, numerous improvements have been made.

## Key claims (as reported)
- To date, the best asymptotic overhead achievable for general block sizes is O(log2 N/ log log N ), due to an elegant scheme by Kushilevitz et al., which in turn relies on the oblivious Cuckoo hashing scheme by Goodrich and Mitzenmacher.
- In this paper, we make the following contributions: we first revisit the prior O(log2 N/ log log N )-overhead ORAM result.
- We demonstrate the somewhat incompleteness of this prior result, due to the subtle incompleteness of a core building block, namely, Goodrich and Mitzenmacher’s oblivious Cuckoo hashing scheme.
- Even though we do show how to patch the prior result such that we can fully realize Goodrich and Mitzenmacher’s elegant blueprint for oblivious Cuckoo hashing, it is clear that the extreme complexity of oblivious Cuckoo hashing has made understanding, implementation, and proofs difficult.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240254 (1).pdf`
- `downloads/106240254.pdf`
