---
id: KN-LIT-2081
type: literature
title: "A high speed coprocessor for elliptic curve scalar multiplications over Fp"
authors:
  - "Nicolas Guillermin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, implementation, pairing, prime-field, provable-security, rsa, side-channel, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new hardware architecture to compute scalar multiplications in the group of rational points of elliptic curves defined over a prime field. We have made an implementation on Altera FPGA family for some elliptic curves defined over randomly chosen ground fields offering classic cryptographic security level.

## Key claims (as reported)
- Our implementations show that our architecture is the fastest among the public designs to compute scalar multiplication for elliptic curves defined over a general prime ground field.
- Our design is based upon the Residue Number System, guaranteeing carry-free arithmetic and easy parallelism.
- It is SPA resistant and DPA capable.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250046 (1).pdf`
- `downloads/62250046 (2).pdf`
- `downloads/62250046 (3).pdf`
- `downloads/62250046.pdf`
