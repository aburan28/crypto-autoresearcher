---
id: KN-LIT-5955
type: literature
title: "Protecting AES with Shamir’s Secret Sharing Scheme"
authors:
  - "Louis Goubin"
  - "Ange Martinelli"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mpc, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Cryptographic algorithms embedded on physical devices are particularly vulnerable to Side Channel Analysis (SCA). The most common countermeasure for block cipher implementations is masking, which randomizes the variables to be protected by combining them with one or several random values.

## Key claims (as reported)
- In this paper, we propose an original masking scheme based on Shamir’s Secret Sharing scheme [22] as an alternative to Boolean masking.
- We detail its implementation for the AES using the same tool than Rivain and Prouff in CHES 2010 [16]: multi-party computation.
- We then conduct a security analysis of our scheme in order to compare it to Boolean masking.
- Our results show that for a given amount of noise the proposed scheme - implemented to the first order provides the same security level as 3rd up to 4th order boolean masking, together with a better efficiency.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170080 (1).pdf`
- `downloads/69170080 (2).pdf`
- `downloads/69170080 (3).pdf`
- `downloads/69170080.pdf`
