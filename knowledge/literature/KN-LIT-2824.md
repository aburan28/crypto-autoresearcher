---
id: KN-LIT-2824
type: literature
title: "Cache-Timing Template Attacks"
authors:
  - "Billy Bob Brumley⋆"
  - "Risto M. Hakala"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, ecdsa, elliptic-curve, lattice, pairing, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Cache-timing attacks are a serious threat to security-critical software. We show that the combination of vector quantization and hidden Markov model cryptanalysis is a powerful tool for automated analysis of cache-timing data; it can be used to recover critical algorithm state such as key material.

## Key claims (as reported)
- We demonstrate its effectiveness by running an attack on the elliptic curve portion of OpenSSL (0.9.8k and under).
- This involves automated lattice attacks leading to key recovery within hours.
- We carry out the attack on live cache-timing data without simulating the side channel, showing these attacks are practical and realistic.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59120664 (1).pdf`
- `downloads/59120664 (2).pdf`
- `downloads/59120664 (3).pdf`
- `downloads/59120664.pdf`
