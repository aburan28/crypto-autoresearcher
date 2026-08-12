---
id: KN-LIT-1239
type: literature
title: "General Practical Cryptanalysis of the Sum of"
authors:
  - "Round-Reduced Block Ciphers"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/2033"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/2033"
tags: [cryptanalysis, mov-fr, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new approach between classical security proofs of modes of operation and dedicated security analysis for known cryptanalysis families: General Practical Cryptanalysis. This allows us to analyze generically the security of the sum of two keyed permutations against known attacks.

## Key claims (as reported)
- In many cases (of course, not all), we show that the security of the sum is strongly linked to that of the composition of the two permutations.
- This enables the construction of beyond-birthday bound secure low-latency PRFs by cutting a known-to-be-secure block cipher into two equal parts.
- As a side result, our general analysis shows an inevitable difficulty for the key recovery based on differential-type attacks against the sum, which leads to a correction of previously published attacks on the dedicated design Orthros.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-2033.pdf`
