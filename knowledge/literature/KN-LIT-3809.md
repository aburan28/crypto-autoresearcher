---
id: KN-LIT-3809
type: literature
title: "Fast Near Collision Attack on the Grain v1 Stream Cipher"
authors:
  - "Bin Zhang"
  - "Chao Xu"
  - "Willi Meier"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Modern stream ciphers often adopt a large internal state to resist various attacks, where the cryptanalysts have to deal with a large number of variables when mounting state recovery attacks. In this paper, we propose a general new cryptanalytic method on stream ciphers, called fast near collision attack, to address this situation.

## Key claims (as reported)
- It combines a near collision property with the divide-and-conquer strategy so that only subsets of the internal state, associated with different keystream vectors, are recovered first and merged carefully later to retrieve the full large internal state.
- A self-contained method is introduced and improved to derive the target subset of the internal state from the partial state difference efficiently.
- As an application, we propose a new key recovery attack on Grain v1, one of the 7 finalists selected by the eSTREAM project, in the single-key setting.
- Both the pre-computation and the online phases are tailored according to its internal structure, to provide an attack for any fixed IV in 275.7 cipher ticks after the pre-computation of 28.1 cipher ticks, given 228 -bit memory and about 219 keystream bits.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822401 (1).pdf`
- `downloads/10822401.pdf`
