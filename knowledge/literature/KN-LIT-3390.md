---
id: KN-LIT-3390
type: literature
title: "Design of Testable Random Bit Generators"
authors:
  - "Marco Bucci"
  - "Raimondo Luzzi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, the evaluation of random bit generators for security applications is discussed and the concept of stateless generator is introduced. It is shown how, for the proposed class of generators, the verification of a minimum entropy limit can be performed directly on the post-processed random numbers thus not requiring a good statistic quality for the noise source itself, provided that a sufficient compression is adopted in the post-processing unit.

## Key claims (as reported)
- Assuming that the noise source is stateless, a straightforward entropy estimator to drive an adaptive compression algorithm is proposed.
- Examples of stateless sources are also discussed.
- Finally, an attack scenario against a noise source is defined and an effective approach to the attack detection is presented.
- The entropy estimator and the attack detection together guarantee the unpredictability of the generated random numbers.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/011 (1).pdf`
- `downloads/011 (2).pdf`
- `downloads/011 (3).pdf`
- `downloads/011.pdf`
