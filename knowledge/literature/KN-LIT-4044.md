---
id: KN-LIT-4044
type: literature
title: "Fuzzy Extractors: How to Generate Strong Keys from Biometrics and Other Noisy Data"
authors:
  - "Yevgeniy Dodis"
  - "Leonid Reyzin"
  - "Adam Smith"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide formal definitions and efficient secure techniques for – turning biometric information into keys usable for any cryptographic application, and – reliably and securely authenticating biometric data. Our techniques apply not just to biometric information, but to any keying material that, unlike traditional cryptographic keys, is (1) not reproducible precisely and (2) not distributed uniformly.

## Key claims (as reported)
- We propose two primitives: a fuzzy extractor extracts nearly uniform randomness R from its biometric input; the extraction is error-tolerant in the sense that R will be the same even if the input changes, as long as it remains reasonably close to the original.
- Thus, R can be used as a key in any cryptographic application.
- A secure sketch produces public information about its biometric input w that does not reveal w, and yet allows exact recovery of w given another value that is close to w.
- Thus, it can be used to reliably reproduce error-prone biometric inputs without incurring the security risk inherent in storing them.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/DRS-ec2004-final (1).pdf`
- `downloads/DRS-ec2004-final (2).pdf`
- `downloads/DRS-ec2004-final.pdf`
