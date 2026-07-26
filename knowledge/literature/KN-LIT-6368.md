---
id: KN-LIT-6368
type: literature
title: "Scalable Ciphertext Compression Techniques for"
authors:
  - "Post-Quantum KEMs"
  - "their Applications"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [isogeny, lattice, pairing, pqc, quantum, sidh-csidh]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A multi-recipient key encapsulation mechanism, or mKEM, provides a scalable solution to securely communicating to a large group, and offers savings in both bandwidth and computational cost compared to the trivial solution of communicating with each member individually. All prior works on mKEM are only limited to classical assumptions and, although some generic constructions are known, they all require specific properties that are not shared by most post-quantum schemes.

## Key claims (as reported)
- In this work, we first provide a simple and efficient generic construction of mKEM that can be instantiated from versatile assumptions, including post-quantum ones.
- We then study these mKEM instantiations at a practical level using 8 post-quantum KEMs (which are lattice and isogeny-based NIST candidates), and CSIDH, and show that compared to the trivial solution, our mKEM offers savings of at least one order of magnitude in the bandwidth, and make encryption time shorter by a factor ranging from 1.92 to 35.
- Additionally, we show that by combining mKEM with the TreeKEM protocol used by MLS – an IETF draft for secure group messaging – we obtain significant bandwidth savings.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491258 (1).pdf`
- `downloads/12491258.pdf`
