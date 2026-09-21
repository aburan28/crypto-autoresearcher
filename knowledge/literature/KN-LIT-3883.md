---
id: KN-LIT-3883
type: literature
title: "Finding Collisions on a Public Road, or Do Secure Hash Functions Need Secret Coins?"
authors:
  - "Chun-Yuan Hsiao"
  - "Leonid Reyzin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, pairing, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many cryptographic primitives begin with parameter generation, which picks a primitive from a family. Such generation can use public coins (e.g., in the discrete-logarithm-based case) or secret coins (e.g., in the factoring-based case).

## Key claims (as reported)
- We study the relationship between publiccoin and secret-coin collision-resistant hash function families (CRHFs).
- Specifically, we demonstrate that: – there is a lack of attention to the distinction between secret-coin and public-coin definitions in the literature, which has led to some problems in the case of CRHFs; – in some cases, public-coin CRHFs can be built out of secret-coin CRHFs; – the distinction between the two notions is meaningful, because in general secret-coin CRHFs are unlikely to imply public-coin CRHFs.
- The last statement above is our main result, which states that there is no black-box reduction from public-coin CRHFs to secret-coin CRHFs.
- Our proof for this result, while employing oracle separations, uses a novel approach, which demonstrates that there is no black-box reduction without demonstrating that there is no relativizing reduction.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/crypto-final (1).pdf`
- `downloads/crypto-final (2).pdf`
- `downloads/crypto-final.pdf`
