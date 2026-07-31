---
id: KN-LIT-2905
type: literature
title: "Circuit Compilers with O(1/ log(n)) Leakage Rate"
authors:
  - "Marcin Andrychowicz"
  - "Stefan Dziembowski"
  - "Sebastian Faust"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The goal of leakage-resilient cryptography is to construct cryptographic algorithms that are secure even if the devices on which they are implemented leak information to the adversary. One of the main parameters for designing leakage resilient constructions is the leakage rate, i.e., a proportion between the amount of leaked information and the complexity of the computation carried out by the construction.

## Key claims (as reported)
- We focus on the so-called circuit compilers, which is an important tool for transforming any cryptographic algorithm (represented as a circuit) into one that is secure against the leakage attack.
- Our model is the “probing attack” where the adversary learns the values on some (chosen by him) wires of the circuit.
- Our results can be summarized as follows.
- First, we construct circuit compilers with perfect security and leakage rate O(1/ log(n)), where n denotes the security parameter (previously known constructions achieved rate O(1/n)).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650173 (1).pdf`
- `downloads/96650173.pdf`
