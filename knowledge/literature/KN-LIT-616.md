---
id: KN-LIT-616
type: literature
title: "No-signaling Linear PCPs"
authors:
  - "Susumu Kiyoshima"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/649"
  doi: "10.1007/978-3-030-03807-6_3"
  arxiv: null
  url: "https://eprint.iacr.org/2018/649"
tags: [fhe, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we give a no-signaling linear probabilistically checkable proof (PCP) system for polynomial-time deterministic computation, i.e., a PCP system for P such that (1) the honest PCP oracle is a linear function and (2) the soundness holds against any (computational) no-signaling cheating prover, who is allowed to answer each query according to a distribution that depends on the entire query set in a certain way. To the best of our knowledge, our construction is the first PCP system that satisfies these two properties simultaneously.

## Key claims (as reported)
- As an application of our PCP system, we obtain a 2-message delegating computation scheme by using a known transformation.
- Compared with the existing 2-message delegating computation schemes that are based on standard cryptographic assumptions, our scheme requires preprocessing but has a simpler structure and makes use of different (possibly cheaper) standard cryptographic primitives, namely additive/multiplicative homomorphic encryption schemes.
- This article is a full version of an earlier article: No-signaling Linear PCPs, in Proceedings of TCC 2018, ©IACR 2018, https://doi.org/10.1007/978-3-030-03807-6_3.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2018-649 (1).pdf`
- `downloads/2018-649.pdf`
