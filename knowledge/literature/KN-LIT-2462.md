---
id: KN-LIT-2462
type: literature
title: "An Analysis of NIST SP 800-90A"
authors:
  - "Joanne Woodage"
  - "Dan Shumow"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We investigate the security properties of the three deterministic random bit generator (DRBG) mechanisms in NIST SP 800-90A [2]. The standard received considerable negative attention due to the controversy surrounding the now retracted DualEC-DRBG, which appeared in earlier versions.

## Key claims (as reported)
- Perhaps because of the attention paid to the DualEC, the other algorithms in the standard have received surprisingly patchy analysis to date, despite widespread deployment.
- This paper addresses a number of these gaps in analysis, with a particular focus on HASH-DRBG and HMAC-DRBG.
- We uncover a mix of positive and less positive results.
- On the positive side, we prove (with a caveat) the robustness [13] of HASH-DRBG and HMAC-DRBG in the random oracle model (ROM).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760349 (1).pdf`
- `downloads/114760349.pdf`
