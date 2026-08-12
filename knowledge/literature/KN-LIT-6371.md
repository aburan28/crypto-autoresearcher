---
id: KN-LIT-6371
type: literature
title: "Scalable Multi-Party Private Set-Intersection"
authors:
  - "Carmit Hazay⋆"
  - "Muthuramakrishnan Venkitasubramaniam⋆⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work we study the problem of private set-intersection in the multi-party setting and design two protocols with the following improvements compared to prior work. First, our protocols are designed in the so-called star network topology, where a designated party communicates with everyone else, and take a new approach of leveraging the 2PC protocol of [FNP04].

## Key claims (as reported)
- This approach minimizes the usage of a broadcast channel, where our semi-honest protocol does not make any use of such a channel and all communication is via point-to-point channels.
- In addition, the communication complexity of our protocols scales with the number of parties.
- More concretely, (1) our first semi-honest secure protocol implies communication ∑ complexity that is linear in the input sizes, namely O(( n i=1 mi ) · κ) bits of communication where κ is the security parameter and mi is the size of Pi ’s input set, whereas overall computational overhead is quadratic in the input sizes only for a designated party, and linear for the rest.
- We further reduce this overhead by employing two types of hashing schemes.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/101740170 (1).pdf`
- `downloads/101740170 (2).pdf`
- `downloads/101740170 (3).pdf`
- `downloads/101740170 (4).pdf`
- `downloads/101740170.pdf`
