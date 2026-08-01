---
id: KN-LIT-4787
type: literature
title: "Low Communication Complexity Protocols"
authors:
  - "Collision Resistant Hash Functions"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study communication complexity in computational settings where bad inputs may exist, but they should be hard to find for any computationally bounded adversary. We define a model where there is a source of public randomness but the inputs are chosen by a computationally bounded adversarial participant after seeing the public randomness.

## Key claims (as reported)
- We show that breaking the known communication lower bounds of the private coins model in this setting is closely connected to known cryptographic assumptions.
- We consider the simultaneous messages model and the interactive communication model and show that for any non trivial predicate (with no redundant rows, such as equality): √ 1.
- Breaking the Ω( n) bound in the simultaneous message case or the Ω(log n) bound in the interactive communication case, implies the existence of distributional collision-resistant hash functions (dCRH).
- This is shown using techniques from Babai and Kimmel [BK97].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070148 (1).pdf`
- `downloads/135070148.pdf`
