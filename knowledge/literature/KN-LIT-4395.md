---
id: KN-LIT-4395
type: literature
title: "Improved Cryptanalysis of Skein Jean-Philippe Aumasson1, , Çağdaş Çalık2 , Willi Meier1, , Onur Özen3"
authors:
  - "Raphael C.-W. Phan"
  - "Kerem Varıcı"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The hash function Skein is the submission of Ferguson et al. to the NIST Hash Competition, and is arguably a serious candidate for selection as SHA-3. This paper presents the first third-party analysis of Skein, with an extensive study of its main component: the block cipher Threefish.

## Key claims (as reported)
- We notably investigate near collisions, distinguishers, impossible differentials, key recovery using related-key differential and boomerang attacks.
- In particular, we present near collisions on up to 17 rounds, an impossible differential on 21 rounds, a related-key boomerang distinguisher on 34 rounds, a known-related-key boomerang distinguisher on 35 rounds, and key recovery attacks on up to 32 rounds, out of 72 in total for Threefish-512.
- None of our attacks directly extends to the full Skein hash.
- However, the pseudorandomness of Threefish is required to validate the security proofs on Skein, and our results conclude that at least 36 rounds of Threefish seem required for optimal security guarantees.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59120540 (1).pdf`
- `downloads/59120540 (2).pdf`
- `downloads/59120540 (3).pdf`
- `downloads/59120540.pdf`
