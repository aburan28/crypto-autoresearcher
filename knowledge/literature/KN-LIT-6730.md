---
id: KN-LIT-6730
type: literature
title: "Soft Decision Error Correction for Compact Memory-Based PUFs using a Single Enrollment"
authors:
  - "Vincent van der Leest"
  - "Bart Preneel"
  - "Erik van der Sluis"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secure storage of cryptographic keys in hardware is an essential building block for high security applications. It has been demonstrated that Physically Unclonable Functions (PUFs) based on uninitialized SRAM are an effective way to securely store a key based on the unique physical characteristics of an Integrated Circuit (IC).

## Key claims (as reported)
- The startup state of an SRAM memory is unpredictable but not truly random as well as noisy, hence privacy amplification techniques and a Helper Data Algorithm (HDA) are required in order to recover the correct value of a full entropy secret key.
- At the core of an HDA are error correcting techniques.
- The best known method to recover a full entropy 128-bit key requires 4700 SRAM cells.
- Earlier work by Maes et al. has reduced the number of SRAM cells to 1536 by using soft decision decoding; however, this method requires multiple measurements (and thus also power resets) during the storage of a key, which will be shown to be an unacceptable overhead for many applications.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280266 (1).pdf`
- `downloads/74280266 (2).pdf`
- `downloads/74280266 (3).pdf`
- `downloads/74280266.pdf`
