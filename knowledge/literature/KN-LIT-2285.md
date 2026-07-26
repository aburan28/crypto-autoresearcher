---
id: KN-LIT-2285
type: literature
title: "A Very High Speed True Random Number Generator with Entropy Assessment"
authors:
  - "Abdelkarim Cherkaoui"
  - "Viktor Fischer"
  - "Laurent Fesquet"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The proposed true random number generator (TRNG) exploits the jitter of events propagating in a self-timed ring (STR) to generate random bit sequences at a very high bit rate. It takes advantage of a special feature of STRs that allows the time elapsed between successive events to be set as short as needed, even in the order of picoseconds.

## Key claims (as reported)
- If the time interval between the events is set in concordance with the clock jitter magnitude, a simple entropy extraction scheme can be applied to generate random numbers.
- The proposed STR-based TRNG (STRNG) follows AIS31 recommendations: by using the proposed stochastic model, designers can compute a lower entropy bound as a function of the STR characteristics (number of stages, oscillation period and jitter magnitude).
- Using the resulting entropy assessment, they can then set the compression rate in the arithmetic post-processing block to reach the required security level determined by the entropy per output bit.
- Implementation of the generator in two FPGA families confirmed its feasibility in digital technologies and also confirmed it can provide high quality random bit sequences that pass the statistical tests required by AIS31 at rates as high as 200 Mbit/s.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860154 (1).pdf`
- `downloads/80860154 (2).pdf`
- `downloads/80860154 (3).pdf`
- `downloads/80860154.pdf`
