---
id: KN-LIT-2398
type: literature
title: "Algebraic Decomposition for Probing Security"
authors:
  - "Claude Carlet"
  - "Emmanuel Prouff"
  - "Matthieu Rivain"
  - "Thomas Roche"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, mpc, pairing, provable-security, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The probing security model is very popular to prove the sidechannel security of cryptographic implementations protected by masking. A common approach to secure nonlinear functions in this model is to represent them as polynomials over a binary field and to secure their nonlinear multiplications thanks to a method introduced by Ishai, Sahai and Wagner at Crypto 2003.

## Key claims (as reported)
- Several schemes based on this approach have been published, leading to the recent proposal of Coron, Roy and Vivek which is currently the best known method when no particular assumption is made on the algebraic structure of the function.
- In the present paper, we revisit this idea by trading nonlinear multiplications for lowdegree functions.
- Specifically, we introduce an algebraic decomposition approach in which a nonlinear function is represented as a sequence of functions with low algebraic degrees.
- We therefore focus on the probingsecure evaluation of such low-degree functions and we introduce three novel methods to tackle this particular issue.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160288 (1).pdf`
- `downloads/92160288 (2).pdf`
- `downloads/92160288.pdf`
