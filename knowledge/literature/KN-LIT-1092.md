---
id: KN-LIT-1092
type: literature
title: "CSI-Otter: Isogeny-based (Partially) Blind Signatures from the Class Group Action with a Twist"
authors:
  - "Shuichi Katsumata"
  - "Yi-Fu Lai"
  - "Jason T. LeGrow"
  - "Ling Qin"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/1239"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/1239"
tags: [class-group, cryptanalysis, elliptic-curve, hash, isogeny, lattice, number-theory, pairing, pqc, quantum, sidh-csidh, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
group actions (but still more restrictive than modules). The basic scheme has public key size 128 B and signature size 8 KB under the CSIDH-512 parameter sets—these are the smallest among all provably secure post-quantum secure blind signatures.

## Key claims (as reported)
- Relying on a new ring variant of the group action inverse problem (rGAIP), we can halve the signature size to 4 KB while increasing the public key size to 512 B.
- We provide preliminary cryptanalysis of rGAIP and show that for certain parameter settings, it is essentially as secure as the standard GAIP.
- Finally, we show a novel way to turn our blind signature into a partially blind signature, where we deviate from prior methods since they require hashing into the set of public keys while hiding the corresponding secret key—constructing such a hash function in the isogeny setting remains an open problem.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850136 (1).pdf`
- `downloads/140850136.pdf`
- `downloads/2023-1239.pdf`
