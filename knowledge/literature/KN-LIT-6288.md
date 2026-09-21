---
id: KN-LIT-6288
type: literature
title: "Ring/Module Learning with Errors under Linear"
authors:
  - "Zhedong Wang"
  - "Qiqi Lai"
  - "Feng-Hao Liu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, pqc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper studies the hardness of decision Module Learning with Errors (MLWE) under linear leakage, which has been used as a foundation to derive more efficient lattice-based zero-knowledge proofs in a recent paradigm of Lyubashevsky, Nguyen, and Seiler (PKC 21). Unlike in the plain LWE setting, it was unknown whether this problem remains provably hard in the module/ring setting.

## Key claims (as reported)
- This work shows a reduction from the standard search MLWE to decision MLWE with linear leakage.
- Thus, the main problem remains hard asymptotically as long as the non-leakage version of MLWE is hard.
- Additionally, we also refine the paradigm of Lyubashevsky, Nguyen, and Seiler (PKC 21) by showing a more fine-grained tradeoff between efficiency and leakage.
- This can lead to further optimizations of lattice proofs under the paradigm.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602110 (1).pdf`
- `downloads/14602110.pdf`
