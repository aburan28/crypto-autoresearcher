---
id: KN-LIT-b97b9f
type: literature
title: 'Quasipolynomial Cryptanalysis of the McEliece Cryptosystem (or: PIR Meets McEliece) — August revision'
authors:
- Ashrujit Ghoshal
- Yuval Ishai
- Aayush Jain
- Nuozhou Sun
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/1630
identifiers:
  eprint: iacr:2026/1630
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/1630
source:
  citation: 'Ashrujit Ghoshal, Yuval Ishai, Aayush Jain, Nuozhou Sun. Quasipolynomial Cryptanalysis of the McEliece Cryptosystem
    (or: PIR Meets McEliece). Cryptology ePrint Archive 2026/1630, revised 2026-08-27.'
  url: https://eprint.iacr.org/2026/1630
tags:
- classic-mceliece
- code-based
- goppa
- quasipolynomial
- distinguisher
- heuristic-key-recovery
- revision
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

The original paper gives a provable n^O(log n) distinguisher for the specified asymptotic binary-Goppa McEliece regime. Its August 27 revision adds a heuristic n^O(log n) equivalent-key recovery route alongside heuristic ciphertext decryption. The updated abstract states decryption is not concretely efficient and says key recovery is closer to the distinguisher and may matter for NIST levels.

## Scope and evidence boundary

The distinguisher, heuristic decryption and heuristic equivalent-key recovery are different security games. The abstract alone supplies no independently checked per-parameter concrete work or practical key recovery. This new entry supersedes KN-LIT-7baf07 only as a record of the updated abstract, not as verification of the heuristic.

## Research follow-up

Read the revised full paper and compare equivalent-key recovery and decoding costs against exact Classic McEliece sets, accounting for memory and preprocessing.

Source: [https://eprint.iacr.org/2026/1630](https://eprint.iacr.org/2026/1630); ePrint received 2026-08-07; substantively revised 2026-08-27. Abstract and metadata read on 2026-09-26; result not reproduced.
