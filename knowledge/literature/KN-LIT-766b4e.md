---
id: KN-LIT-766b4e
type: literature
title: Computing 256-bit elliptic curve discrete logarithms in 26 days on a fault-tolerant trapped-ion quantum computer with
  20,000 qubits
authors:
- Thomas Häner
- Felix Tripier
- Jacob Young
- Michael Naehrig
- Andrii Maksymov
- Safwan Alam
- Dmitri Maslov
- Matthew Parrott
- Yvette de Sereville
- Jordan Sullivan
- Mark Webster
- Nicolas Delfosse
- John Gamble
- Martin Roetteler
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/1916
identifiers:
  eprint: iacr:2026/1916
  arxiv: '2609.05625'
  doi: null
  url: https://eprint.iacr.org/2026/1916
source:
  citation: Thomas Häner, Felix Tripier, Jacob Young, Michael Naehrig, Andrii Maksymov, Safwan Alam, Dmitri Maslov, Matthew
    Parrott, Yvette de Sereville, Jordan Sullivan, Mark Webster, Nicolas Delfosse, John Gamble, Martin Roetteler. Computing
    256-bit elliptic curve discrete logarithms in 26 days on a fault-tolerant trapped-ion quantum computer with 20,000 qubits.
    Cryptology ePrint Archive 2026/1916, 2026.
  url: https://eprint.iacr.org/2026/1916
tags:
- ecdlp
- secp256k1
- shor
- quantum
- resource-estimate
- physical-qubits
- trapped-ion
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

For an assumed Walking Cat trapped-ion architecture, the authors compile an ECDLP circuit with approximately 1,450 logical qubits and 40 million Toffoli gates. Their architecture-specific schedule estimates 19,397 physical qubits, 25.7 days per secp256k1 solve and 63% success; a CCZ injection improvement is one contributor.

## Scope and evidence boundary

This is a projected fault-tolerant attack conditional on architecture, error correction, factory and compilation assumptions. No 256-bit ECDLP was executed on a quantum computer. Logical-qubit, physical-qubit, gate-count and runtime figures must not be compared as if interchangeable.

## Research follow-up

Recompute sensitivity to gate latency, physical error rates and factory throughput, preserving assumptions and per-attempt success probability.

Source: [https://eprint.iacr.org/2026/1916](https://eprint.iacr.org/2026/1916); ePrint received 2026-09-08. Abstract and metadata read on 2026-09-26; result not reproduced.
