---
id: KN-LIT-1303
type: literature
title: "SQIAsignHD: SQIsignHD Adaptor Signature"
authors:
  - "Farzin Renan"
  - "Péter Kutas"
year: 2024
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2404.09026"
  url: "https://arxiv.org/abs/2404.09026"
tags: [ecdsa, elliptic-curve, isogeny, pairing, pqc, protocol, quantum, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Adaptor signatures can be viewed as a generalized form of standard digital signature schemes by linking message authentication to the disclosure of a secret value. As a recent cryptographic primitive, they have become essential for blockchain applications, including cryptocurrencies, by reducing on-chain costs, improving fungibility, and enabling off-chain payments in payment-channel networks, payment-channel hubs, and atomic swaps.

## Key claims (as reported)
- However, existing adaptor signature constructions are vulnerable to quantum attacks due to Shor’s algorithm.
- In this work, we introduce SQIAsignHD, a new quantum-resistant adaptor signature scheme based on isogenies of supersingular elliptic curves, using SQIsignHD - as the underlying signature scheme - and exploiting the idea of the artificial orientation on the supersingular isogeny Diffie-Hellman key exchange protocol, SIDH, to define the underlying hard relation.
- We, furthermore, provide a formal security proof for our proposed scheme.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2404.09026v4.pdf`
