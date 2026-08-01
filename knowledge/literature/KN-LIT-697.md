---
id: KN-LIT-697
type: literature
title: "Optimizations of Side-Channel Attack on AES MixColumns Using Chosen Input"
authors:
  - "Aurelien Vasselle"
  - "Antoine Wurcker"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/343"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/343"
tags: [cryptanalysis, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Considering AES sub-steps that can be attacked with a small guess space, the most practicable is to target SubBytes of extremal rounds. For its contrast between candidates (non-linearity) and that the search space is reduced to 28 -sized blocks.

## Key claims (as reported)
- But when such point of interests are not available, MixColumns may be considered but involve search spaces of 232 -sized blocks.
- This number of attacks to run being often considered as unrealistic to reach, published papers propose to attack using chosen inputs in order to reduce back search space to 28 -sized blocks.
- Several sets of chosen inputs acquisition will then be required to succeed an attack.
- Our contribution consists in an optimization of usage of gained information that allows to drastically reduce the number of set needed to realize such an attack, even to only one set in some configurations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2019-343.pdf`
