---
id: KN-LIT-2983
type: literature
title: "Communication-Efficient Unconditional MPC with Guaranteed Output Delivery"
authors:
  - "Vipul Goyal"
  - "Yanyi Liu"
  - "Yifan Song(Γ)"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the communication complexity of unconditionally secure MPC with guaranteed output delivery over point-to-point channels for corruption threshold t < n/3. We ask the question: “is it possible to construct MPC in this setting s.t. the communication complexity per multiplication gate is linear in the number of parties?” While a number of works have focused on reducing the communication complexity in this setting, the answer to the above question has remained elusive for over a decade.

## Key claims (as reported)
- We resolve the above question in the affirmative by providing an MPC with communication complexity O(Cnκ + n3 κ) where κ is the size of an element in the field, C is the size of the (arithmetic) circuit, and, n is the number of parties.
- This represents a strict improvement over the previously best known communication complexity of O(Cnκ + DM n2 κ + n3 κ) where DM is the multiplicative depth of the circuit.
- To obtain this result, we introduce a novel technique called 4-consistent tuples of sharings which we believe to be of independent interest.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940219 (1).pdf`
- `downloads/116940219.pdf`
