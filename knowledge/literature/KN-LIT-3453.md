---
id: KN-LIT-3453
type: literature
title: "Distributed Merkle’s Puzzles"
authors:
  - "Itai Dinur"
  - "Ben Hasson"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Merkle’s puzzles were proposed in 1974 by Ralph Merkle as a key agreement protocol between two players based on symmetric-key primitives. In order to agree on a secret key, each player makes T queries to a random function (oracle), while any eavesdropping adversary has to make Ω(T 2 ) queries to the random oracle in order to recover the key with high probability.

## Key claims (as reported)
- The quadratic gap between the query complexity of the honest players and the eavesdropper was shown to be optimal by Barak and Mahmoody [CRYPTO‘09].
- We consider Merkle’s puzzles in a distributed setting, where the goal is to allow all pairs among M honest players with access to a random oracle to agree on secret keys.
- We devise a protocol in this setting, where each player makes T queries to the random oracle and communicates at most T bits, while any adversary has to make Ω(M ·T 2 ) queries to the random oracle (up to logarithmic factors) in order to recover any one of the keys with high probability.
- Therefore, the amortized (per-player) complexity of achieving secure communication (for a fixed security level) decreases with the size of the network.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130420136 (1).pdf`
- `downloads/130420136.pdf`
