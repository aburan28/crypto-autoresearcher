---
id: KN-LIT-2095
type: literature
title: "A Lightweight Identification Protocol Based on Lattices"
authors:
  - "Samed Düzlü"
  - "Juliane Krämer"
  - "Thomas Pöppelmann"
  - "Patrick Struck"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, lattice, mov-fr, pqc, provable-security, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work we present a lightweight lattice-based identification protocol based on the CPA-secured public key encryption scheme Kyber. It is designed as a replacement for existing classical ECC- or RSA-based identification protocols in IoT, smart card applications, or for device authentication.

## Key claims (as reported)
- The proposed protocol is simple, efficient, and implementations are supposed to be easy to harden against side-channel attacks.
- Compared to standard constructions for identification protocols based on lattice-based KEMs, our construction achieves this by avoiding the Fujisaki-Okamoto transform and its impact on implementation security.
- Moreover, contrary to prior lattice-based identification protocols or standard constructions using signatures, our work does not require rejection sampling and can use more efficient parameters than signature schemes.
- We provide a generic construction from CPA-secured public key encryption schemes to identification protocols and give a security proof of the protocol in the ROM.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940099 (1).pdf`
- `downloads/13940099.pdf`
