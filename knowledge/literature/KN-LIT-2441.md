---
id: KN-LIT-2441
type: literature
title: "Amortizing Garbled Circuits"
authors:
  - "Yan Huang"
  - "Jonathan Katz"
  - "Vladimir Kolesnikov"
  - "Ranjit Kumaresan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider secure two-party computation in a multipleexecution setting, where two parties wish to securely evaluate the same circuit multiple times. We design efficient garbled-circuit-based two-party protocols secure against malicious adversaries.

## Key claims (as reported)
- Recent works by Lindell (Crypto 2013) and Huang-Katz-Evans (Crypto 2013) have obtained optimal complexity for cut-and-choose performed over garbled circuits in the single execution setting.
- We show that it is possible to obtain much lower amortized overhead for cut-and-choose in the multiple-execution setting.
- Our efficiency improvements result from a novel way to combine a recent technique of Lindell (Crypto 2013) with LEGO-based cut-and-choose techniques (TCC 2009, Eurocrypt 2013).
- In concrete terms, for 40-bit statistical security we obtain a 2× improvement (per execution) in communication and computation for as few as 7 executions, and require only 8 garbled circuits (i.e., a 5× improvement) per execution for as low as 3500 executions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160276 (1).pdf`
- `downloads/86160276 (2).pdf`
- `downloads/86160276 (3).pdf`
- `downloads/86160276 (4).pdf`
- `downloads/86160276 (5).pdf`
- `downloads/86160276.pdf`
