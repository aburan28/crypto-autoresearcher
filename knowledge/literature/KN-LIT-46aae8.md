---
id: KN-LIT-46aae8
type: literature
title: 'Square Root of All Evil: The Dangers of Falcon''s Superfluous Square Roots'
authors:
- Hiroto Kaihara
- Calvin Abou Haidar
- Mehdi Tibouchi
- Masayuki Abe
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/2046
identifiers:
  eprint: iacr:2026/2046
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/2046
source:
  citation: 'Hiroto Kaihara, Calvin Abou Haidar, Mehdi Tibouchi, Masayuki Abe. Square Root of All Evil: The Dangers of Falcon''s
    Superfluous Square Roots. Cryptology ePrint Archive 2026/2046, 2026.'
  url: https://eprint.iacr.org/2026/2046
tags:
- falcon
- fn-dsa
- fault-injection
- square-root
- implementation
- key-recovery
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

The authors show that Falcon’s floating-point square-root computations can be removed while retaining similar or slightly better speed. They demonstrate on Arm Cortex-M4 that a single injected glitch in one square root, followed by about one million ordinary signatures, yields full key recovery with 100% success in their reported experiments; faulty signatures are difficult to distinguish.

## Scope and evidence boundary

The key recovery requires physical fault injection plus many subsequent signatures in the tested implementation. Removing square roots is the mitigation and simplification, not a proof that every Falcon signer is vulnerable.

## Research follow-up

Benchmark the root-free signer, signature compatibility and timing, then repeat fault experiments across independent keys and target builds.

Source: [https://eprint.iacr.org/2026/2046](https://eprint.iacr.org/2026/2046); ePrint received 2026-09-15. Abstract and metadata read on 2026-09-26; result not reproduced.
