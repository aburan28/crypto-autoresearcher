---
id: KN-LIT-3208
type: literature
title: "Crowd-Blending Privacy"
authors:
  - "Johannes Gehrke"
  - "Michael Hay"
  - "Edward Lui"
  - "Rafael Pass"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new definition of privacy called crowd-blending privacy that strictly relaxes the notion of differential privacy. Roughly speaking, k-crowd blending private sanitization of a database requires that each individual i in the database “blends” with k other individuals j in the database, in the sense that the output of the sanitizer is “indistinguishable” if i’s data is replaced by j’s.

## Key claims (as reported)
- We demonstrate crowd-blending private mechanisms for histograms and for releasing synthetic data points, achieving strictly better utility than what is possible using differentially private mechanisms.
- Additionally, we demonstrate that if a crowd-blending private mechanism is combined with a “pre-sampling” step, where the individuals in the database are randomly drawn from some underlying population (as is often the case during data collection), then the combined mechanism satisfies not only differential privacy, but also the stronger notion of zero-knowledge privacy.
- This holds even if the pre-sampling is slightly biased and an adversary knows whether certain individuals were sampled or not.
- Taken together, our results yield a practical approach for collecting and privately releasing data while ensuring higher utility than previous approaches.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170473 (1).pdf`
- `downloads/74170473 (2).pdf`
- `downloads/74170473 (3).pdf`
- `downloads/74170473 (4).pdf`
- `downloads/74170473 (5).pdf`
- `downloads/74170473.pdf`
