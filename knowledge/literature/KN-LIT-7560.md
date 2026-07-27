---
id: KN-LIT-7560
type: literature
title: "“HILA5 Pindakaas”: On the CCA security of lattice-based encryption with error correction"
authors:
  - "Tanja Lange"
  - "Lorenz Panny"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hyperelliptic, lattice, pairing, pqc, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that HILA5 is not secure against chosen-ciphertext attacks. Specifically, we demonstrate a key-recovery attack on HILA5 using an active attack on reused keys.

## Key claims (as reported)
- The attack works around the error correction in HILA5.
- The attack applies to the HILA5 key-encapsulation mechanism (KEM), and also to the public-key encryption mechanism (PKE) obtained by NIST’s procedure for combining the KEM with authenticated encryption.
- This contradicts the most natural interpretation of the IND-CCA security claim for HILA5.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/hila5-20171218.pdf`
- `downloads/hila5-20180308.pdf`
