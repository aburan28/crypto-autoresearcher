---
id: KN-LIT-6478
type: literature
title: "Securing Circuits Against Constant-Rate Tampering"
authors:
  - "Dana Dachman-Soled"
  - "Yael Tauman Kalai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a compiler that converts any circuit into one that remains secure even if a constant fraction of its wires are tampered with. Following the seminal work of Ishai et. al.

## Key claims (as reported)
- (Eurocrypt 2006), we consider adversaries who may choose an arbitrary set of wires to corrupt, and may set each such wire to 0 or to 1, or may toggle with the wire.
- We prove that such adversaries, who continuously tamper with the circuit, can learn at most logarithmically many bits of secret information (in addition to black-box access to the circuit).
- Our results are information theoretic.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170529 (1).pdf`
- `downloads/74170529 (2).pdf`
- `downloads/74170529 (3).pdf`
- `downloads/74170529 (4).pdf`
- `downloads/74170529 (5).pdf`
- `downloads/74170529.pdf`
