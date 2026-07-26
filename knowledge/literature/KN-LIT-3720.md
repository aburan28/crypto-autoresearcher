---
id: KN-LIT-3720
type: literature
title: "Exact Security Analysis of ASCON"
authors:
  - "Bishwajit Chakraborty"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Ascon cipher suite, offering both authenticated encryption with associated data (AEAD) and hashing functionality, has recently emerged as the winner of the NIST Lightweight Cryptography (LwC) standardization process. The AEAD schemes within Ascon, namely Ascon-128 and Ascon-128a, have also been previously selected as the preferred lightweight authenticated encryption solutions in the CAESAR competition.

## Key claims (as reported)
- In this paper, we present a tight and comprehensive security analysis of the Ascon AEAD schemes within the random permutation model.
- Existing integrity analyses of Ascon (and any Duplex AEAD scheme in general) commonly include the term DT /2c , where D and T represent data and time complexities respectively, and c denotes the capacity of the underlying sponge.
- In this paper, we demonstrate that Ascon achieves AE security when T is bounded by min{2κ , 2c } (where κ is the key size), and DT is limited to 2b (with b being the size of the underlying permutation, which is 320 for Ascon).
- Our findings indicate that in accordance with NIST requirements, Ascon allows for a tag size as low as 64 bits while enabling a higher rate of 192 bits, surpassing the recommended rate.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438080 (1).pdf`
- `downloads/14438080.pdf`
