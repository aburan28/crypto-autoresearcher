---
id: KN-LIT-2610
type: literature
title: "Attacking RSA–CRT Signatures with"
authors:
  - "Mehdi Tibouchi"
  - "Jean-Christophe Zapalowicz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, implementation, pairing, provable-security, quantum, rsa, side-channel, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present several efficient fault attacks against implementations of RSA–CRT signatures that use modular exponentiation algorithms based on Montgomery multiplication. They apply to any padding function, including randomized paddings, and as such are the first fault attacks effective against RSA–PSS.

## Key claims (as reported)
- The new attacks work provided that a small register can be forced to either zero, or a constant value, or a value with zero high-order bits.
- We show that these models are quite realistic, as such faults can be achieved against many proposed hardware designs for RSA signatures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280444 (1).pdf`
- `downloads/74280444 (2).pdf`
- `downloads/74280444 (3).pdf`
- `downloads/74280444.pdf`
