---
id: KN-LIT-6679
type: literature
title: "Simulatable Leakage: Analysis, Pitfalls, and new Constructions"
authors:
  - "J. Longo Galea"
  - "D. Martin"
  - "E. Oswald"
  - "D. Page"
  - "M. Stam"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 2013, Standaert et al. proposed the notion of simulatable leakage to connect theoretical leakage resilience with the practice of side channel attacks. Their use of simulators, based on physical devices, to support proofs of leakage resilience allows verification of underlying assumptions: the indistinguishability game, involving real vs. simulated leakage, can be ‘played’ by an evaluator.

## Key claims (as reported)
- Using a concrete, block cipher based leakage resilient PRG and high-level simulator definition (based on concatenating two partial leakage traces), they included detailed reasoning why said simulator (for AES-128) resists state-of-the-art side channel attacks.
- In this paper, we demonstrate a distinguisher against their simulator and thereby falsify their hypothesis.
- Our distinguishing technique, which is evaluated using concrete implementations of the Standaert et al. simulator on several platforms, is based on ‘tracking’ consistency (resp. identifying simulator inconsistencies) in leakage traces by means of crosscorrelation.
- In attempt to rescue the approach, we propose several alternative simulator definitions based on splitting traces at points of low intrinsic cross-correlation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730123 (1).pdf`
- `downloads/88730123 (2).pdf`
- `downloads/88730123 (3).pdf`
- `downloads/88730123.pdf`
