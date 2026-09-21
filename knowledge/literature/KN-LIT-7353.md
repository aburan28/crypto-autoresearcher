---
id: KN-LIT-7353
type: literature
title: "Unconditionally Secure Computation Against Low-Complexity Leakage"
authors:
  - "Andrej Bogdanov"
  - "Yuval Ishai"
  - "Akshayaram Srinivasan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, pairing, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the problem of constructing leakage-resilient circuit compilers that are secure against global leakage functions with bounded output length. By global, we mean that the leakage can depend on all circuit wires and output a low-complexity function (represented as a multi-output Boolean circuit) applied on these wires.

## Key claims (as reported)
- In this work, we design compilers both in the stateless (a.k.a. single-shot leakage) setting and the stateful (a.k.a. continuous leakage) setting that are unconditionally secure against AC0 leakage and similar low-complexity classes.
- In the stateless case, we show that the original private circuits construction of Ishai, Sahai, and Wagner (Crypto 2003) is actually secure against AC0 leakage.
- In the stateful case, we modify the construction of Rothblum (Crypto 2012), obtaining a simple construction with unconditional security.
- Prior works that designed leakage-resilient circuit compilers against AC0 leakage had to rely either on secure hardware components (Faust et al., Eurocrypt 2010, Miles-Viola, STOC 2013) or on (unproven) complexity-theoretic assumptions (Rothblum, Crypto 2012).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940327 (1).pdf`
- `downloads/116940327.pdf`
