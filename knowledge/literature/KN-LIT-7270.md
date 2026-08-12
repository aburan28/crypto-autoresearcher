---
id: KN-LIT-7270
type: literature
title: "TriviA: A Fast and Secure Authenticated Encryption Scheme"
authors:
  - "Avik Chakraborti"
  - "Anupam Chattopadhyay"
  - "Muhammad Hassan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, lattice, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose a new hardware friendly authenticated encryption (AE) scheme TriviA based on (i) a stream cipher for generating keys for the ciphertext and the tag, and (ii) a pairwise independent hash to compute the tag. We have adopted one of the ISOstandardized stream ciphers for lightweight cryptography, namely Trivium, to obtain our underlying stream cipher.

## Key claims (as reported)
- This new stream cipher has a state that is a little larger than the state of Trivium to accommodate a 128-bit secret key and IV.
- Our pairwise independent hash is also an adaptation of the EHC or “Encode-Hash-Combine” hash, that requires the optimum number of field multiplications and hence requires small hardware footprint.
- We have implemented the design in synthesizable RTL.
- Pre-layout synthesis, using 65 nm standard cell technology under typical operating conditions, reveals that TriviA is able to achieve a high throughput of 91.2 Gbps for an area of 24.4 KGE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930321 (1).pdf`
- `downloads/92930321.pdf`
