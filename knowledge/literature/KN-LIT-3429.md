---
id: KN-LIT-3429
type: literature
title: "Differential-Linear Cryptanalysis of ICEPOLE"
authors:
  - "Tao Huang"
  - "Ivan Tjuawinata"
  - "Hongjun Wu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, mov-fr, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
ICEPOLE is a CAESAR candidate with the intermediate level of robustness under nonce misuse circumstances in the original document. In particular, it was claimed that key recovery attack against ICEPOLE is impossible in the case of nonce misuse.

## Key claims (as reported)
- ICEPOLE is strong against the differential cryptanalysis and linear cryptanalysis.
- In this paper, we developed the differential-linear attacks against ICEPOLE when nonce is misused.
- Our attacks show that the state of ICEPOLE–128 and ICEPOLE–128a can be recovered with data complexity 246 and time complexity 246 ; the state of ICEPOLE–256a can be recovered with data complexity 260 and time complexity 260 .
- For ICEPOLE–128a and ICEPOLE–256a, the secret key is recovered once the state is recovered.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400137 (1).pdf`
- `downloads/85400137.pdf`
