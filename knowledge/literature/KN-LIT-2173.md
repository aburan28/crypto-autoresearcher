---
id: KN-LIT-2173
type: literature
title: "A Novel Completeness Test for Leakage Models and its Application to Side Channel Attacks and Responsibly Engineered Simulators"
authors:
  - "Si Gao"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Today’s side channel attack targets are often complex devices in which instructions are processed in parallel and work on 32-bit data words. Consequently, the state that is involved in producing leakage in these modern devices is not only large, but also hard to predict due to various micro-architectural factors that users might not be aware of.

## Key claims (as reported)
- On the other hand, security evaluations— basing on worst case attacks or simulators — explicitly rely on the underlying state: a potentially incomplete state can easily lead to wrong conclusions.
- We put forward a novel notion for the “completeness” of an assumed state, together with an efficient statistical test that is based on “collapsed models”.
- Our novel test can be used to recover a state that contains multiple 32-bit variables in a grey box setting.
- We illustrate how our novel test can help to guide side channel attacks and we reveal new attack vectors for existing implementations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760313 (1).pdf`
- `downloads/132760313.pdf`
