---
id: KN-LIT-3828
type: literature
title: "Faster Binary-Field Multiplication and Faster Binary-Field MACs"
authors:
  - "Daniel J. Bernstein"
  - "Tung Chou"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, hash, implementation, pairing, prime-field, quantum, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper shows how to securely authenticate messages using just 29 bit operations per authenticated bit, plus a constant overhead per message. The authenticator is a standard type of “universal” hash function providing information-theoretic security; what is new is computing this type of hash function at very high speed.

## Key claims (as reported)
- At a lower level, this paper shows how to multiply two elements of a field of size 2128 using just 9062 ≈ 71 · 128 bit operations, and how to multiply two elements of a field of size 2256 using just 22164 ≈ 87 · 256 bit operations.
- This performance relies on a new representation of field elements and new FFT-based multiplication techniques.
- This paper’s constant-time software uses just 1.89 Core 2 cycles per byte to authenticate very long messages.
- On a Sandy Bridge it takes 1.43 cycles per byte, without using Intel’s PCLMULQDQ polynomialmultiplication hardware.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/auth256-20140918.pdf`
