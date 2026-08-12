---
id: KN-LIT-3416
type: literature
title: "Differential Computation Analysis: Hiding your White-Box Designs is Not Enough"
authors:
  - "Joppe W. Bos"
  - "Charles Hubain"
  - "Wil Michiels"
  - "Philippe Teuwen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, pollard-rho, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Although all current scientific white-box approaches of standardized cryptographic primitives are broken, there is still a large number of companies which sell “secure” white-box products. In this paper, we present a new approach to assess the security of white-box implementations which requires neither knowledge about the look-up tables used nor any reverse engineering effort.

## Key claims (as reported)
- This differential computation analysis (DCA) attack is the software counterpart of the differential power analysis attack as applied by the cryptographic hardware community.
- We developed plugins to widely available dynamic binary instrumentation frameworks to produce software execution traces which contain information about the memory addresses being accessed.
- To illustrate its effectiveness, we show how DCA can extract the secret key from numerous publicly (non-commercial) available white-box programs implementing standardized cryptography by analyzing these traces to identify secret-key dependent correlations.
- This approach allows one to extract the secret key material from white-box implementations significantly faster and without specific knowledge of the white-box design in an automated manner.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130106 (1).pdf`
- `downloads/98130106.pdf`
