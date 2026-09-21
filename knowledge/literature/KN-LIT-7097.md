---
id: KN-LIT-7097
type: literature
title: "Three Halves Make a Whole? Beating the Half-Gates Lower Bound for Garbled Circuits?"
authors:
  - "Mike Rosulek"
  - "Lawrence Roy"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, pairing, provable-security, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a garbling scheme for boolean circuits, in which XOR gates are free and AND gates require communication of 1.5κ + 5 bits. This improves over the state-of-the-art “half-gates” scheme of Zahur, Rosulek, and Evans (Eurocrypt 2015), in which XOR gates are free and AND gates cost 2κ bits.

## Key claims (as reported)
- The half-gates paper proved a lower bound of 2κ bits per AND gate, in a model that captured all known garbling techniques at the time.
- We bypass this lower bound with a novel technique that we call slicing and dicing, which involves slicing wire labels in half and operating separately on those halves.
- Ours is the first to bypass the lower bound while being fully compatible with free-XOR, making it a drop-in replacement for half-gates.
- Our construction is proven secure from a similar assumption to prior free-XOR garbling (circular correlation-robust hash), and uses only slightly more computation than half-gates.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826084 (1).pdf`
- `downloads/12826084.pdf`
