---
id: KN-LIT-1337
type: literature
title: "A Robust Variant of ChaCha20-Poly1305"
authors:
  - "Tim Beyne"
  - "Yu Long Chen"
  - "Michiel Verbauwhede"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/222"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/222"
tags: [implementation, pairing, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The ChaCha20-Poly1305 AEAD scheme is widely used as an alternative for AES-GCM on platforms without AES hardware instructions. Although recent analysis by Degabriele et al. shows that ChaCha20-Poly1305 provides adequate security in the conventional multiuser model, the construction is totally broken when a single nonce is repeated – a real-world scenario that can occur due to faulty implementations or the desire to use random nonces.

## Key claims (as reported)
- We present a new nonce-misuse resistant and key-committing authenticated encryption scheme, called ChaCha20-Poly1305-PSIV, that is based on carefully combining the ChaCha20-Poly1305 building blocks into the NSIV paradigm proposed by Peyrin and Seurin (CRYPTO 2016) without performance loss.
- We analyze the security of the underlying mode PSIV in the multi-user faulty-nonce model assuming that the underlying permutation is ideal, and prove its key-committing security in the cmt1 model.
- Rust and C implementations are provided, and benchmarks confirm that performance is comparable to the ChaCha20-Poly1305 implementation in libsodium.
- In terms of security and efficiency (without hardware support), our proposal compares favorably to AES-GCM-SIV.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-222.pdf`
