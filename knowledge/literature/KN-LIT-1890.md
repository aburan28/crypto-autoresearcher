---
id: KN-LIT-1890
type: literature
title: "Study of Post Quantum status of Widely Used Protocols"
authors:
  - "Tushin Mallick∗"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2603.28728"
  url: "https://arxiv.org/abs/2603.28728"
tags: [dlp, ecdsa, elliptic-curve, factoring, pairing, pqc, protocol, quantum, rsa, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The advent of quantum computing poses significant threats to classical public-key cryptographic primitives such as RSA and elliptic-curve cryptography. As many critical network and security protocols depend on these primitives for key exchange and authentication, there is an urgent need to understand their quantum vulnerability and assess the progress made towards integrating post-quantum cryptography (PQC).

## Key claims (as reported)
- This survey provides a detailed examination of nine widely deployed protocols —TLS, IPsec, BGP, DNSSEC, SSH, QUIC, OpenID Connect, OpenVPN, and Signal Protocol —analysing their cryptographic foundations, quantum risks, and the current state of PQC migration.
- We find that TLS and Signal lead the transition with hybrid post-quantum key exchange already deployed at scale, while IPsec and SSH have standardised mechanisms but lack widespread production adoption.
- DNSSEC and BGP face the most significant structural barriers, as post-quantum signature sizes conflict with fundamental protocol constraints.
- Across all protocols, key exchange proves consistently easier to migrate than authentication, and protocol-level limitations such as message size and fragmentation often dominate over raw algorithm performance.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2603.28728v1.pdf`
