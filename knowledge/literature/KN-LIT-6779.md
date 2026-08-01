---
id: KN-LIT-6779
type: literature
title: "SQISign: Compact Post-Quantum"
authors:
  - "Christophe Petit"
  - "Benjamin Wesolowski"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, elliptic-curve, endomorphism, hash, isogeny, pqc, protocol, provable-security, quantum, sidh-csidh, signature, supersingular, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new signature scheme, SQISign, (for Short Quaternion and Isogeny Signature) from isogeny graphs of supersingular elliptic curves. The signature scheme is derived from a new one-round, high soundness, interactive identification protocol.

## Key claims (as reported)
- Targeting the postquantum NIST-1 level of security, our implementation results in signatures of 204 bytes, secret keys of 16 bytes and public keys of 64 bytes.
- In particular, the signature and public key sizes combined are an order of magnitude smaller than all other post-quantum signature schemes.
- On a modern workstation, our implementation in C takes 0.6s for key generation, 2.5s for signing, and 50ms for verification.
- While the soundness of the identification protocol follows from classical assumptions, the zero-knowledge property relies on the second main contribution of this paper.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491357 (1).pdf`
- `downloads/12491357.pdf`
