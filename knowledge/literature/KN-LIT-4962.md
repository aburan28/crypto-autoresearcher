---
id: KN-LIT-4962
type: literature
title: "More Powerful and Reliable Second-level"
authors:
  - "Statistical Randomness Tests"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Random number generators (RNGs) are essential for cryptographic systems, and statistical tests are usually employed to assess the randomness of their outputs. As the most commonly used statistical test suite, the NIST SP 800-22 suite includes 15 test items, each of which contains two-level tests.

## Key claims (as reported)
- For the test items based on the binomial distribution, we find that their second-level tests are flawed due to the inconsistency between the assessed distribution and the assumed one.
- That is, the sequence that passes the test could still have statistical flaws in the assessed aspect.
- For this reason, we propose Q-value as the metric for these second-level tests to replace the original P-value without any extra modification, and the first-level tests are kept unchanged.
- We provide the correctness proof of the proposed Q-value based second-level tests.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031180 (1).pdf`
- `downloads/10031180.pdf`
