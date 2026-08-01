---
id: KN-LIT-7167
type: literature
title: "Time-Memory tradeoffs for large-weight syndrome decoding in ternary codes"
authors:
  - "Pierre Karpman"
  - "Charlotte Lefevre"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose new algorithms for solving a class of large-weight syndrome decoding problems in random ternary codes. This is the main generic problem underlying the security of the recent Wave signature scheme (Debris-Alazard et al., 2019), and it has so far received limited attention.

## Key claims (as reported)
- At SAC 2019 Bricout et al. proposed a reduction to a binary subset sum problem requiring many solutions, and used it to obtain the fastest known algorithm.
- However —as is often the case in the coding theory literature— its memory cost is proportional to its time cost, which makes it unattractive in most applications.
- In this work we propose a range of memory-efficient algorithms for this problem, which describe a near-continuous time-memory tradeoff curve.
- Those are obtained by using the same reduction as Bricout et al. and carefully instantiating the derived subset sum problem with exhaustivesearch algorithms from the literature, in particular dissection (Dinur et al., 2012) and dissection in tree (Dinur, 2019).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770046 (1).pdf`
- `downloads/131770046.pdf`
