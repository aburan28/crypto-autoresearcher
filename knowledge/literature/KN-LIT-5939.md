---
id: KN-LIT-5939
type: literature
title: "Promise Σ-protocol: How to Construct Efficient Threshold ECDSA from Encryptions Based on Class Groups"
authors:
  - "Yi Deng"
  - "Shunli Ma"
  - "Xinxuan Zhang"
  - "Hailong Wang"
  - "Xuyang Song"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, dlp, ecdsa, elliptic-curve, fhe, number-theory, pairing, protocol, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Threshold Signatures allow n parties to share the ability of issuing digital signatures so that any coalition of size at least t + 1 can sign, whereas groups of t or fewer players cannot. The currently known class-group-based threshold ECDSA constructions are either inefficient (requiring parallel-repetition of the underlying zero knowledge proof with small challenge space) or requiring rather non-standard low order assumption.

## Key claims (as reported)
- In this paper, we present efficient threshold ECDSA protocols from encryption schemes based on class groups with neither assuming the low order assumption nor parallel repeating the underlying zero knowledge proof, yielding a significant efficiency improvement in the key generation over previous constructions.
- Along the way we introduce a new notion of promise Σ-protocol that satisfies only a weaker soundness called promise extractability.
- An accepting promise Σ-proof for statements related to class-group-based encryptions does not establish the truth of the statement but provides security guarantees (promise extractability) that are sufficient for our applications.
- We also show how to simulate homomorphic operations on a (possibly invalid) class-group-based encryption whose correctness has been proven via our promise Σ-protocol.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900093 (1).pdf`
- `downloads/130900093.pdf`
