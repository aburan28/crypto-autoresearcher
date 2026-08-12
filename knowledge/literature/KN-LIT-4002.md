---
id: KN-LIT-4002
type: literature
title: "Fully Secure Functional Encryption without Obfuscation"
authors:
  - "Sanjam Garg"
  - "Craig Gentry"
  - "Shai Halevi"
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [glv-gls, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Previously known functional encryption (FE) schemes for general circuits relied on indistinguishability obfuscation, which in turn either relies on an exponential number of assumptions (basically, one per circuit), or a polynomial set of assumptions, but with an exponential loss in the security reduction. Additionally most of these schemes are proved in the weaker selective security model, where the adversary is forced to specify its target before seeing the public parameters.

## Key claims (as reported)
- For these constructions, full security can be obtained but at the cost of an exponential loss in the security reduction.
- In this work, we overcome the above limitations and realize an adaptively secure functional encryption scheme without using indistinguishability obfuscation.
- Specifically the security of our scheme relies only on the polynomial hardness of simple assumptions on composite order multilinear maps.
- Though we do not currently have secure instantiations for these assumptions, we expect that multilinear maps supporting these assumptions will discovered in the future.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/95621065 (1).pdf`
- `downloads/95621065.pdf`
