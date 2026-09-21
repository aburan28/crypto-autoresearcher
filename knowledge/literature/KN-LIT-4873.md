---
id: KN-LIT-4873
type: literature
title: "McBits: fast constant-time code-based cryptography"
authors:
  - "Daniel J. Bernstein"
  - "Tung Chou"
  - "Peter Schwabe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, complexity-theory, finite-field, implementation, pairing, pqc, quantum, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents extremely fast algorithms for code-based public-key cryptography, including full protection against timing attacks. For example, at a 2128 security level, this paper achieves a reciprocal decryption throughput of just 60493 cycles (plus cipher cost etc.) on a single Ivy Bridge core.

## Key claims (as reported)
- These algorithms rely on an additive FFT for fast root computation, a transposed additive FFT for fast syndrome computation, and a sorting network to avoid cache-timing attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860180 (1).pdf`
- `downloads/80860180 (2).pdf`
- `downloads/80860180 (3).pdf`
- `downloads/80860180.pdf`
- `downloads/mcbits-20130616.pdf`
