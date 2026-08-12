---
id: KN-LIT-2084
type: literature
title: "A hybrid lattice-reduction and meet-in-the-middle attack against NTRU"
authors:
  - "Nick Howgrave-Graham"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
To date the NTRUEncrypt security parameters have been based on the existence of two types of attack: a meet-in-the-middle attack due to Odlyzko, and a conservative extrapolation of the running times of the best (known) lattice reduction schemes to recover the private key. We show that there is in fact a continuum of more efficient attacks between these two attacks.

## Key claims (as reported)
- We show that by combining lattice reduction and a meet-in-the-middle strategy one can reduce the number of loops in attacking the NTRUEncrypt private key from 284.2 to 260.3 , for the k = 80 parameter set.
- In practice the attack is still expensive (dependent on ones choice of cost-metric), although there are certain space/time tradeoffs that can be applied.
- Asymptotically our attack remains exponential in the security parameter k, but it dictates that NTRUEncrypt parameters must be chosen so that the meet-in-the-middle attack has complexity 2k even after an initial lattice basis reduction of complexity 2k .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/46220150 (1).pdf`
- `downloads/46220150 (2).pdf`
- `downloads/46220150 (3).pdf`
- `downloads/46220150.pdf`
