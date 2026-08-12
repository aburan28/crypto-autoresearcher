---
id: KN-LIT-1154
type: literature
title: "Partial Sums Meet FFT: Improved Attack on 6-Round"
authors:
  - "Gaetan Leurent"
  - "Avichai Marmor"
  - "Victor Mollimard"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/1659"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/1659"
tags: [cryptanalysis, finite-field, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The partial sums cryptanalytic technique was introduced in 2000 by Ferguson et al., who used it to break 6-round AES with time complexity of 252 S-box computations – a record that has not been beaten ever since. In 2014, Todo and Aoki showed that for 6-round AES, partial sums can be replaced by a technique based on the Fast Fourier Transform (FFT), leading to an attack with a comparable complexity.

## Key claims (as reported)
- In this paper we show that the partial sums technique can be combined with an FFT-based technique, to get the best of the two worlds.
- Using our combined technique, we obtain an attack on 6-round AES with complexity of about 246.4 additions.
- We fully implemented the attack experimentally, along with the partial sums attack and the Todo-Aoki attack, and confirmed that our attack improves the best known attack on 6-round AES by a factor of more than 32.
- We expect that our technique can be used to significantly enhance numerous attacks that exploit the partial sums technique.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-1659.pdf`
