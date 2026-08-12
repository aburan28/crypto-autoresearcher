---
id: KN-LIT-2347
type: literature
title: "Adaptively Secure Garbled Circuits from One-Way Functions Brett Hemenway1 , Zahra Jafargholi2 , Rafail Ostrovsky3,?"
authors:
  - "Alessandra Scafuro"
  - "Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A garbling scheme is used to garble a circuit C and an input x in a way that reveals the output C(x) but hides everything else. In many settings, the circuit can be garbled off-line without strict efficiency constraints, but the input must be garbled very efficiently on-line, with much lower complexity than evaluating the circuit.

## Key claims (as reported)
- Yao’s garbling scheme [31] has essentially optimal on-line complexity, but only achieves selective security, where the adversary must choose the input x prior to seeing the garbled circuit.
- It has remained an open problem to achieve adaptive security, where the adversary can choose x after seeing the garbled circuit, while preserving on-line efficiency.
- In this work, we modify Yao’s scheme in a way that allows us to prove adaptive security under one-way functions.
- In our main instantiation we achieve on-line complexity only proportional to the width w of the circuit.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98160142 (1).pdf`
- `downloads/98160142.pdf`
