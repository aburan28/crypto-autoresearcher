---
id: KN-LIT-68585e
type: literature
title: Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition
authors:
- Han Luo
- Ziyi Yang
- Jingquan Luo
- Ziruo Wang
- Yuexin Su
- Xiaoming Sun
- Lvzhou Li
- Tongyang Li
year: 2026
venue: arXiv preprint arXiv:2607.13816
identifiers:
  eprint: null
  arxiv: '2607.13816'
  doi: null
  url: https://arxiv.org/abs/2607.13816
source:
  citation: Han Luo, Ziyi Yang, Jingquan Luo, Ziruo Wang, Yuexin Su, Xiaoming Sun, Lvzhou Li, Tongyang Li. Quantum Algorithm
    for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition. arXiv:2607.13816, 2026.
  url: https://arxiv.org/abs/2607.13816
tags:
- ecdlp
- prime-field
- quantum
- logical-qubits
- modular-inversion
- toffoli
confidence: reported
citation_verified: web
citation_verified_note: Primary arXiv abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

A compact reversible modular-inversion circuit enables a prime-field ECDLP construction reported at 3n+6*floor(log2(n))+O(1) logical qubits and 919*n^3/log2(n)+O(n^2) Toffoli gates. For a 256-bit prime-field curve the authors give 835 logical qubits, versus cited earlier estimates of 1,098 and 1,175 logical qubits.

## Scope and evidence boundary

The 835 count is a *logical* qubit estimate. This trades space against a stated Toffoli cost and does not imply a physical-qubit count, 26-day runtime, or a quantum solution on existing hardware.

## Research follow-up

For any physical comparison, compile both logical circuits under the same code, error rate, cycle time and success probability.

Source: [https://arxiv.org/abs/2607.13816](https://arxiv.org/abs/2607.13816); arXiv submitted 2026-07-15. Abstract and metadata read on 2026-09-26; result not reproduced.
