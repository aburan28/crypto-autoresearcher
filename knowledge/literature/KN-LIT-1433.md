---
id: KN-LIT-1433
type: literature
title: "On the Fiat–Shamir Security of Succinct Arguments from Functional Commitments"
authors:
  - "Alessandro Chiesa"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/902"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/902"
tags: [pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the security of a popular paradigm for constructing SNARGs, closing a key security gap left open by prior work. The paradigm consists of two steps: first, construct a public-coin succinct interactive argument by combining a functional interactive oracle proof (FIOP) and a functional commitment scheme (FC scheme); second, apply the Fiat–Shamir transformation in the random oracle model.

## Key claims (as reported)
- Prior work did not consider this generalized setting nor prove the security of this second step (even in special cases).
- We prove that the succinct argument obtained in the first step satisfies state-restoration security, thereby ensuring that the second step does in fact yield a succinct non-interactive argument.
- This holds provided the FIOP satisfies state-restoration security and the FC scheme satisfies a natural state-restoration variant of function binding (a generalization of position binding for vector commitment schemes).
- Moreover, we prove that notable FC schemes satisfy state-restoration function binding, allowing us to establish, via our main result, the security of several SNARGs of interest (in the random oracle model).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-902.pdf`
