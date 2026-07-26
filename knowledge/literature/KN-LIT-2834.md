---
id: KN-LIT-2834
type: literature
title: "Candidate Obfuscation via Oblivious LWE Sampling"
authors:
  - "Hoeteck Wee"
  - "Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, pqc, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new, simple candidate construction of indistinguishability obfuscation (iO). Our scheme is inspired by lattices and learning-with-errors (LWE) techniques, but we are unable to prove security under a standard assumption.

## Key claims (as reported)
- Instead, we formulate a new falsifiable assumption under which the scheme is secure.
- Furthermore, the scheme plausibly achieves post-quantum security.
- Our construction is based on the recent “split FHE” framework of Brakerski, Döttling, Garg, and Malavolta (EUROCRYPT ’20), and we provide a new instantiation of this framework.
- As a first step, we construct an iO scheme that is provably secure assuming that LWE holds and that it is possible to obliviously generate LWE samples without knowing the corresponding secrets.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960205 (1).pdf`
- `downloads/126960205.pdf`
