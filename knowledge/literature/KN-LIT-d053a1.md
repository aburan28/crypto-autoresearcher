---
id: KN-LIT-d053a1
type: literature
title: 'Keep Track of Your Errors: Solving ILWE and Improving Attacks on ML-DSA'
authors:
- Mohamed ElGhamrawy
- Thomas Eisenbarth
- Julius Hermelink
- Anja Rabich
- Florian Sieck
- Silvan Streit
- Jonas Thietke
- Zhiyuan Zhang
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/2091
identifiers:
  eprint: iacr:2026/2091
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/2091
source:
  citation: 'Mohamed ElGhamrawy, Thomas Eisenbarth, Julius Hermelink, Anja Rabich, Florian Sieck, Silvan Streit, Jonas Thietke,
    Zhiyuan Zhang. Keep Track of Your Errors: Solving ILWE and Improving Attacks on ML-DSA. Cryptology ePrint Archive 2026/2091,
    2026.'
  url: https://eprint.iacr.org/2026/2091
tags:
- ml-dsa
- ilwe
- concealed-ilwe
- distribution-hints
- belief-propagation
- side-channel
- timing
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

Tracking the error distribution in leakage-derived (Concealed) ILWE samples lets the authors derive distribution hints and apply a belief-propagation solver. In a noise-free attack setting, their abstract reports an average 62-fold reduction in required ML-DSA signatures, from 139 million under the earlier linear-regression approach to 2.25 million, with larger gains under noise.

## Scope and evidence boundary

This result requires side information or timing leakage; the signature count does not describe a public-key-only attack. The abstract does not provide a common wall-clock or memory cost for both solvers.

## Research follow-up

Reproduce the ILWE sample extraction and compare success per key, leakage quality, total capture time and solver work on matched implementations.

Source: [https://eprint.iacr.org/2026/2091](https://eprint.iacr.org/2026/2091); ePrint received 2026-09-18. Abstract and metadata read on 2026-09-26; result not reproduced.
