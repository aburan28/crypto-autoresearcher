---
id: KN-LIT-3659
type: literature
title: "Efficiently Shuffling in Public"
authors:
  - "Udaya Parampalli"
  - "Kim Ramchen"
  - "Vanessa Teague"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, fhe, lattice, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit shuffling in public [AW07a], a scheme which allows a shuffle to be precomputed. We show how to obfuscate a Paillier shuffle with O(N log3.5 N ) exponentiations, leading to a very robust and efficient mixnet: when distributed over O(N ) nodes the mixnet achieves mixing in polylogarithmic time, independent of the level of privacy or verifiability required.

## Key claims (as reported)
- Our construction involves the use of layered Paillier applied to permutation networks.
- With an appropriate network the shuffle may be confined to a particular subset of permutations, for example to rotations.
- While it is possible that the mixnet may produce biased output, we show that certain networks lead to an acceptable bias-efficiency tradeoff.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930432 (1).pdf`
- `downloads/72930432 (2).pdf`
- `downloads/72930432 (3).pdf`
- `downloads/72930432.pdf`
