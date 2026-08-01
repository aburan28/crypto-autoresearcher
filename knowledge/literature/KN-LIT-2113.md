---
id: KN-LIT-2113
type: literature
title: "A Mix-Net From Any CCA2 Secure Cryptosystem"
authors:
  - "Shahram Khazaei"
  - "Tal Moran"
  - "Douglas Wikström"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, pairing, provable-security, quantum, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a provably secure mix-net from any CCA2 secure cryptosystem. The mix-net is secure against active adversaries that statically corrupt less than λ out of k mix-servers, where λ is a threshold parameter, and it is robust provided that at most min(λ − 1, k − λ) mix-servers are corrupted.

## Key claims (as reported)
- The main component of our construction is a mix-net that outputs the correct result if all mix-servers behaved honestly, and aborts with probability 1−O(H −(t−1) ) otherwise (without disclosing anything about the inputs), where t is an auxiliary security parameter and H is the number of honest parties.
- The running time of this protocol for long messages is roughly 3tc, where c is the running time of Chaum’s mix-net (1981).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580600 (1).pdf`
- `downloads/76580600 (2).pdf`
- `downloads/76580600 (3).pdf`
- `downloads/76580600.pdf`
