---
id: KN-LIT-6770
type: literature
title: "SPHINCS: practical stateless hash-based signatures"
authors:
  - "Daniel J. Bernstein"
  - "Daira Hopwood"
  - "Andreas Hülsing"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, hyperelliptic, lattice, pairing, pqc, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces a high-security post-quantum stateless hash-based signature scheme that signs hundreds of messages per second on a modern 4-core 3.5GHz Intel CPU. Signatures are 41 KB, public keys are 1 KB, and private keys are 1 KB.

## Key claims (as reported)
- The signature scheme is designed to provide long-term 2128 security even against attackers equipped with quantum computers.
- Unlike most hash-based designs, this signature scheme is stateless, allowing it to be a drop-in replacement for current signature schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560214 (1).pdf`
- `downloads/90560214.pdf`
- `downloads/sphincs-20150202.pdf`
