---
id: KN-LIT-2153
type: literature
title: "A New Model for Error-Tolerant Side-Channel Cube Attacks"
authors:
  - "Zhenqi Li"
  - "Bin Zhang∗"
  - "Junfeng Fan⋄"
  - "Ingrid Verbauwhede⋄"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Side-channel cube attacks are a class of leakage attacks on block ciphers in which the attacker is assumed to have access to some leaked information on the internal state of the cipher as well as the plaintext/ciphertext pairs. The known Dinur-Shamir model and its variants require error-free data for at least part of the measurements.

## Key claims (as reported)
- In this paper, we consider a new and more realistic model which can deal with the case when all the leaked bits are noisy.
- In our model, the key recovery problem is converted to the problem of decoding a binary linear code over a binary symmetric channel with the crossover probability which is determined by the measurement quality and the cube size.
- We use the maximum likelihood decoding method to recover the key.
- As a case study, we demonstrate efficient key recovery attacks on PRESENT.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860205 (1).pdf`
- `downloads/80860205 (2).pdf`
- `downloads/80860205 (3).pdf`
- `downloads/80860205.pdf`
