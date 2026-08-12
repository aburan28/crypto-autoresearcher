---
id: KN-LIT-4702
type: literature
title: "Leaked-State-Forgery Attack Against The Authenticated Encryption Algorithm ALE"
authors:
  - "Shengbao Wu"
  - "Hongjun Wu"
  - "Tao Huang"
  - "Mingsheng Wang"
  - "Wenling Wu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, pairing, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
ALE is a new authenticated encryption algorithm published at FSE 2013. The authentication component of ALE is based on the strong Pelican MAC, and the authentication security of ALE is claimed to be 128-bit.

## Key claims (as reported)
- In this paper, we propose the leaked-state-forgery attack (LSFA) against ALE by exploiting the state information leaked from the encryption of ALE.
- The LSFA is a new type of differential cryptanalysis in which part of the state information is known and exploited to improve the differential probability.
- Our attack shows that the authentication security of ALE is only 97-bit.
- And the results may be further improved to around 93-bit if the whitening key layer is removed.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82710137 (1).pdf`
- `downloads/82710137 (2).pdf`
- `downloads/82710137 (3).pdf`
- `downloads/82710137.pdf`
