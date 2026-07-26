---
id: KN-LIT-4340
type: literature
title: "Identity-Based Encryption Resilient to Continual Auxiliary Leakage"
authors:
  - "Tsz Hon Yuen"
  - "Sherman S. M. Chow"
  - "Ye Zhang"
  - "Siu Ming Yiu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We devise the first identity-based encryption (IBE) that remains secure even when the adversary is equipped with auxiliary input (STOC ’09) – any computationally uninvertible function of the master secret key and the identity-based secret key. In particular, this is more general than the tolerance of Chow et al.’s IBE schemes (CCS ’10) and Lewko et al.’s IBE schemes (TCC ’11), in which the leakage is bounded by a pre-defined number of bits; yet our construction is also fully secure in the standard model based on only static assumptions, and can be easily extended to give the first hierarchical IBE with auxiliary input.

## Key claims (as reported)
- Furthermore, we propose the model of continual auxiliary leakage (CAL) that can capture both memory leakage and continual leakage.
- The CAL model is particularly appealing since it not only gives a clean definition when there are multiple secret keys (the master secret key, the identitybased secret keys, and their refreshed versions), but also gives a generalized definition that does not assume secure erasure of secret keys after each key update.
- This is different from previous definitions of continual leakage (FOCS ’10, TCC ’11) in which the length-bounded leakage is only the secret key in the current time period.
- Finally, we devise an IBE scheme which is secure in this model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370118 (1).pdf`
- `downloads/72370118 (2).pdf`
- `downloads/72370118 (3).pdf`
- `downloads/72370118.pdf`
