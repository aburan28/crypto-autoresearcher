---
id: KN-LIT-1807
type: literature
title: "PIKE: Faster Isogeny-Based Public Key Encryption with Pairing-Assisted Decryption"
authors:
  - "Shiping Cai"
  - "Mingjie Chen"
  - "Yi-Fu Lai"
  - "Kaizhan LinB"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/473"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/473"
tags: [cryptanalysis, dlp, isogeny, pairing, pqc, protocol, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recent work at Eurocrypt 2025 by Basso and Maino introduced POKÉ, an isogeny-based public key encryption (PKE) scheme. POKÉ shows how two parties can derive a shared secret on a higherdimensional, SIDH-like commutative diagram via basis evaluations, giving the fastest isogeny-based PKE to date with performance comparable to the original SIDH.

## Key claims (as reported)
- In this paper we present PIKE, a new isogeny-based PKE obtained by tweaking the POKÉ design.
- Our key change is to use pairings to derive the shared secret while preserving post-quantum security.
- This brings two benefits: (i) decryption is directly faster, and (ii) by relaxing the required prime form, we can choose smaller primes, further improving overall runtime.
- We provide a proof-of-concept implementation in SageMath.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-473.pdf`
