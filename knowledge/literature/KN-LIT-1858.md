---
id: KN-LIT-1858
type: literature
title: "Scaling of Memory and Bandwidth Requirements of Post-Quantum Signatures with Message Size Falko Strenzke[0009−0006−6574−2904]"
authors:
  - "MTG AG"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/617"
  doi: "10.1007/978-3-032-28946-9_6"
  arxiv: null
  url: "https://eprint.iacr.org/2026/617"
tags: [elliptic-curve, lattice, pairing, pqc, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
1 In this work we analyse the qualitative memory and bandwidth efficiency properties of the currently standardised post-quantum signatures as such and of their protocol integrations mainly in the X.509 context. The term “qualitative” in this respect refers to how memory and bandwidth requirements scale with the size of the signed message.

## Key claims (as reported)
- Specifically, we address the question in how far the algorithms support online-computations, a.k.a streaming, with respect to the signed message in the signing and verification operations.
- Further, we review the possibilities for the pre-computation of a short message representative outside the cryptographic module responsible for the signing or verification operation of the different signature schemes.
- We also give a preview on the corresponding cryptographic API of the PKCS#11 standard which introduces numerous PQC signature algorithms in the upcoming version 3.2.
- We demonstrate that for specific realistic use cases, the qualitative memory and bandwidth efficiency of the PQC signature schemes in protocol use is widely varied and by tendency substantially degraded compared to the traditional signature schemes based on RSA and elliptic curves, which always allow for the pre-computation of a short message representative in the form of a hash value.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-617.pdf`
