---
id: KN-LIT-5607
type: literature
title: "On Tight Quantum Security of HMAC and NMAC in the Quantum Random Oracle Model"
authors:
  - "Akinori Hosoyamada"
  - "Tetsu Iwata"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, pqc, provable-security, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
HMAC and NMAC are the most basic and important constructions to convert Merkle-Damgård hash functions into message authentication codes (MACs) or pseudorandom functions (PRFs). In the quantum setting, at CRYPTO 2017, Song and Yun showed that HMAC and NMAC are quantum pseudorandom functions (qPRFs) under the standard assumption that the underlying compression function is a qPRF.

## Key claims (as reported)
- Their proof guarantees security up to O(2n/5 ) or O(2n/8 ) quantum queries when the output length of HMAC and NMAC is n bits.
- However, there is a gap between the provable security bound and a simple distinguishing attack that uses O(2n/3 ) quantum queries.
- This paper settles the problem of closing the gap.
- We show that the tight bound of the number of quantum queries to distinguish HMAC or NMAC from a random function is Θ(2n/3 ) in the quantum random oracle model, where compression functions are modeled as quantum random oracles.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826169 (1).pdf`
- `downloads/12826169.pdf`
