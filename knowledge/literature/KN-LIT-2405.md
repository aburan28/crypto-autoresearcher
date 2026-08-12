---
id: KN-LIT-2405
type: literature
title: "Algebraic Side-Channel Analysis in the Presence of Errors"
authors:
  - "Yossef Oren"
  - "Mario Kirschbaum"
  - "Thomas Popp"
  - "Avishai Wool"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Measurement errors make power analysis attacks difficult to mount when only a single power trace is available: the statistical methods that make DPA attacks so successful are not applicable since they require many (typically thousands) of traces. Recently it was suggested by [18] to use algebraic methods for the single-trace scenario, converting the key recovery problem into a Boolean satisfiability (SAT) problem, then using a SAT solver.

## Key claims (as reported)
- However, this approach is extremely sensitive to noise (allowing an error rate of well under 1% at most), and the question of its practicality remained open.
- In this work we show how a single-trace side-channel analysis problem can be transformed into a pseudo-Boolean optimization (PBOPT) problem, which takes errors into consideration.
- The PBOPT instance can then be solved using a suitable optimization problem solver.
- The PBOPT syntax provides for a more expressive input specification which allows a very natural representation of measurement errors.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250418 (1).pdf`
- `downloads/62250418 (2).pdf`
- `downloads/62250418 (3).pdf`
- `downloads/62250418.pdf`
