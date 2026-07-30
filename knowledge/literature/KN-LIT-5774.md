---
id: KN-LIT-5774
type: literature
title: "Plaintext Recovery Attacks Against WPA/TKIP?"
authors:
  - "Kenneth G. Paterson"
  - "Bertram Poettering"
  - "Jacob C. N. Schuldt"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, protocol, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We conduct an analysis of the RC4 algorithm as it is used in the IEEE WPA/TKIP wireless standard. In that standard, RC4 keys are computed on a per-frame basis, with specific key bytes being set to known values that depend on 2 bytes of the WPA frame counter (called the TSC).

## Key claims (as reported)
- We observe very large, TSC-dependent biases in the RC4 keystream when the algorithm is keyed according to the WPA specification.
- These biases permit us to mount an effective statistical, plaintextrecovering attack in the situation where the same plaintext is encrypted in many different frames (the so-called “broadcast attack” setting).
- We assess the practical impact of these attacks on WPA/TKIP.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400140 (1).pdf`
- `downloads/85400140 (2).pdf`
- `downloads/85400140 (3).pdf`
- `downloads/85400140.pdf`
