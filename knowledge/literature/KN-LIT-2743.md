---
id: KN-LIT-2743
type: literature
title: "Blind Source Separation from Single Measurements using Singular Spectrum Analysis"
authors:
  - "Santos Merino Del Pozo"
  - "François-Xavier Standaert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, provable-security, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Singular Spectrum Analysis (SSA) is a powerful data decomposition/recompostion technique that can be used to reduce the noise in time series. Compared to existing solutions aiming at similar purposes, such as frequency-based filtering, it benefits from easier-to-exploit intuitions, applicability in contexts where low sampling rates make standard frequency analyses challenging, and the (theoretical) possibility to separate a signal source from a noisy source even if both run at the same frequency.

## Key claims (as reported)
- In this paper, we first describe how to apply SSA in the context of side-channel analysis, and then validate its interest in three different scenarios.
- Namely, we consider unprotected software, masked software, and unprotected hardware block cipher implementations.
- Our experiments confirm significant noise reductions in all three cases, leading to success rates improved accordingly.
- They also put forward the stronger impact of SSA in more challenging scenarios, e.g. masked implementations (because the impact of noise increases exponentially with the number of shares in this case), or noisy hardware implementations (because of the established connection between the amount of noise and the attacks’ success rate in this case).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930042 (1).pdf`
- `downloads/92930042.pdf`
