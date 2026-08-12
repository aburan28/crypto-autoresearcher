---
id: KN-LIT-4412
type: literature
title: "Improved indifferentiability security analysis of chopMD Hash Function"
authors:
  - "Donghoon Chang⋆"
  - "Mridul Nandi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The classical design principle Merkle-Damgård [13, 6] is scrutinized by many ways such as Joux’s multicollision attack, Kelsey-Schneier second preimage attack etc. In TCC’04, Maurer et al. introduced a strong security notion called as “indifferentiability” for a hash function based on a compression function.

## Key claims (as reported)
- The classical design principle is also insecure against this strong security notion whereas chopMD hash is secure with the security bound roughly σ 2 /2s where s is the number of chopped bits and σ is the total number of message blocks queried by a distinguisher.
- In case of n = 2s where n is the output size of a compression function, the value σ to get a significant bound is 2s/2 which is the birthday complexity, where the hash output size is s-bit.
- In this paper, we present an improved security bound for chopMD.
- The improved bound shown in this paper is (3(n − s) + 1)q/2s + q/2n−s−1 + σ 2 /2n+1 where q is the total number of queries.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/50860436 (1).pdf`
- `downloads/50860436 (2).pdf`
- `downloads/50860436 (3).pdf`
- `downloads/50860436.pdf`
