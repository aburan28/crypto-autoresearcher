---
id: KN-LIT-2813
type: literature
title: "Broadcast-Optimal Two Round MPC with an Honest Majority"
authors:
  - "Ivan Damgård"
  - "Bernardo Magri"
  - "Divya Ravi"
  - "Luisa Siniscalchi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [glv-gls]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper closes the question of the possibility of two-round MPC protocols achieving different security guarantees with and without the availability of broadcast in any given round. [CGZ20] study this question in the dishonest majority setting; we complete the picture by studying the honest majority setting.

## Key claims (as reported)
- In the honest majority setting, given broadcast in both rounds, it is known that the strongest guarantee — guaranteed output delivery — is achievable [GLS15].
- We show that, given broadcast in the first round only, guaranteed output delivery is still achievable.
- Given broadcast in the second round only, we give a new construction that achieves identifiable abort, and we show that fairness — and thus guaranteed output delivery — are not achievable in this setting.
- Finally, if only peer-to-peer channels are available, we show that the weakest guarantee — selective abort — is the only one achievable for corruption thresholds t > 1 and for t = 1 and n = 3.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826081 (1).pdf`
- `downloads/12826081.pdf`
