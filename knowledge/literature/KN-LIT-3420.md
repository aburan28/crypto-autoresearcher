---
id: KN-LIT-3420
type: literature
title: "Differential Cryptanalysis of the Stream Ciphers"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Py and Pypy are efficient array-based stream ciphers designed by Biham and Seberry. Both were submitted to the eSTREAM competition.

## Key claims (as reported)
- This paper shows that Py and Pypy are practically insecure.
- If one key is used with about 216 IVs with special differences, with high probability two identical keystreams will appear.
- This can be exploited in a key recovery attack.
- For example, for a 16-byte key and a 16-byte IV, 223 chosen IVs can reduce the effective key size to 3 bytes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45150276 (1).pdf`
- `downloads/45150276 (2).pdf`
- `downloads/45150276 (3).pdf`
- `downloads/45150276.pdf`
