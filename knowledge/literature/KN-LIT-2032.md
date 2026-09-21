---
id: KN-LIT-2032
type: literature
title: "A Differential Fault Attack on MICKEY 2.0"
authors:
  - "Subhadeep Banik"
  - "Subhamoy Maitra"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present a differential fault attack on the stream cipher MICKEY 2.0 which is in eStream’s hardware portfolio. While fault attacks have already been reported against the other two eStream hardware candidates Trivium and Grain, no such analysis is known for MICKEY.

## Key claims (as reported)
- Using the standard assumptions for fault attacks, we show that if the adversary can induce random single bit faults in the internal state of the cipher, then by injecting around 216.7 faults and performing 232.5 computations on an average, it is possible to recover the entire internal state of MICKEY at the beginning of the key-stream generation phase.
- We further consider the scenario where the fault may affect at most three neighbouring bits and in that case we require around 218.4 faults on an average.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860110 (1).pdf`
- `downloads/80860110 (2).pdf`
- `downloads/80860110 (3).pdf`
- `downloads/80860110.pdf`
