---
id: KN-LIT-6296
type: literature
title: "Robust Profiling for DPA-Style Attacks"
authors:
  - "Carolyn Whitnall"
  - "Elisabeth Oswald"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Profiled side-channel attacks are understood to be powerful when applicable: in the best case when an adversary can comprehensively characterise the leakage, the resulting model leads to attacks requiring a minimal number of leakage traces for success. Such ‘complete’ leakage models are designed to capture the scale, location and shape of the profiling traces, so that any deviation between these and the attack traces potentially produces a mismatch which renders the model unfit for purpose.

## Key claims (as reported)
- This severely limits the applicability of profiled attacks in practice and so poses an interesting research challenge: how can we design profiled distinguishers that can tolerate (some) differences between profiling and attack traces?
- This submission is the first to tackle the problem head on: we propose distinguishers (utilising unsupervised machine learning methods, but also a ‘down-to-earth’ method combining mean traces and PCA) and evaluate their behaviour across an extensive set of distortions that we apply to representative trace data.
- Our results show that the profiled distinguishers are effective and robust to distortions to a surprising extent.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930001 (1).pdf`
- `downloads/92930001.pdf`
