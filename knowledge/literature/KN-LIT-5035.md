---
id: KN-LIT-5035
type: literature
title: "Multiparty Generation of an RSA Modulus Megan Chen, Ran Cohen, Jack Doerner, Yashvanth Kondi"
authors:
  - "Eysa Lee"
  - "Schuyler Rosefield"
  - "abhi shelat"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, fhe, mpc, pairing, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new multiparty protocol for the distributed generation of biprime RSA moduli, with security against any subset of maliciously colluding parties assuming oblivious transfer and the hardness of factoring. Our protocol is highly modular, and its uppermost layer can be viewed as a template that generalizes the structure of prior works and leads to a simpler security proof.

## Key claims (as reported)
- We introduce a combined sampling-and-sieving technique that eliminates both the inherent leakage in the approach of Frederiksen et al.
- (Crypto’18), and the dependence upon additively homomorphic encryption in the approach of Hazay et al.
- We combine this technique with an efficient, privacy-free check to detect malicious behavior retroactively when a sampled candidate is not a biprime, and thereby overcome covert rejection-sampling attacks and achieve both asymptotic and concrete efficiency improvements over the previous state of the art.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171397 (1).pdf`
- `downloads/12171397.pdf`
