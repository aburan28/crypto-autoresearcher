---
id: KN-LIT-5599
type: literature
title: "On the Streaming Indistinguishability of a"
authors:
  - "Random Permutation"
  - "a Random Function"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An adversary with S bits of memory obtains a stream of Q elements that are uniformly drawn from the set {1, 2, . . . , N }, either with or without replacement. This corresponds to sampling Q elements using either a random function or a random permutation.

## Key claims (as reported)
- The adversary’s goal is to distinguish between these two cases.
- This problem was first considered by Jaeger and Tessaro (EUROCRYPT 2019), which proved that the adversary’s advantage is upper bounded by p Q · S/N .
- Jaeger and Tessaro used this bound as a streaming switching lemma which allowed proving that known time-memory tradeoff attacks on several modes of operation (such as counter-mode) are optimal up to a factor of O(log N ) if Q · S ≈ N .
- However, the bound’s proof assumed an unproven combinatorial conjecture. p Moreover, if Q · S N there is a gap between the upper bound of Q · S/N and the Q · S/N advantage obtained by known attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105202 (1).pdf`
- `downloads/12105202.pdf`
