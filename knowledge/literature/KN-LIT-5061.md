---
id: KN-LIT-5061
type: literature
title: "Near Collision Attack on the Grain v1 Stream Cipher"
authors:
  - "Bin Zhang∗"
  - "Zhenqi Li"
  - "Dengguo Feng"
  - "Dongdai Lin∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Grain v1 is one of the 7 finalists selected in the final portfolio by the eSTREAM project. It has an elegant and compact structure, especially suitable for a constrained hardware environment.

## Key claims (as reported)
- Though a number of potential weaknesses have been identified, no key recovery attack on the original design in the single key model has been found yet.
- In this paper, we propose a key recovery attack, called near collision attack, on Grain v1.
- The attack utilizes the compact NFSR-LFSR combined structure of Grain v1 and works even if all of the previous identified weaknesses have been sewed and if a perfect key/IV initialization algorithm is adopted.
- Our idea is to identify near collisions of the internal states at different time instants and restore the states accordingly.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240483 (1).pdf`
- `downloads/84240483 (2).pdf`
- `downloads/84240483 (3).pdf`
- `downloads/84240483.pdf`
