---
id: KN-LIT-2389
type: literature
title: "Algebraic Attacks on Stream Ciphers with Linear Feedback"
authors:
  - "Nicolas T. Courtois"
  - "Willi Meier"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A classical construction of stream ciphers is to combine several LFSRs and a highly non-linear Boolean function f . Their security is usually analysed in terms of correlation attacks, that can be seen as solving a system of multivariate linear equations, true with some probability.

## Key claims (as reported)
- At ICISC’02 this approach is extended to systems of higher-degree multivariate equations, and gives an attack in 292 for Toyocrypt, a Cryptrec submission.
- In this attack the key is found by solving an overdefined system of algebraic equations.
- In this paper we show how to substantially lower the degree of these equations by multiplying them by well-chosen multivariate polynomials.
- Thus we are able to break Toyocrypt in 249 CPU clocks, with only 20 Kbytes of keystream, the fastest attack proposed so far.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/26560345 (1).pdf`
- `downloads/26560345 (2).pdf`
- `downloads/26560345.pdf`
