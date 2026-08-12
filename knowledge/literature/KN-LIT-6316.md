---
id: KN-LIT-6316
type: literature
title: "Round-Efficient Black-Box Construction of Composable Multi-Party Computation"
authors:
  - "Susumu Kiyoshima"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a round-efficient black-box construction of a general MPC protocol that satisfies composability in the plain model. The security of our protocol is proven in angel-based UC framework under the minimal assumption of the existence of semi-honest oblivious transfer protocols.

## Key claims (as reported)
- When the round complexity of the underlying oblivious transfer protocol is rot (n), the round complexity of our protocol is max( e O(log2 n), O(rot (n))).
- Since constant-round semi-honest oblivious transfer protocols can be constructed under standard assumptions (such as the existence of enhanced trapdoor permutations), our result gives 2 e O(log n)-round protocol under these assumptions.
- Previously, only an O(max(n , rot (n)))-round protocol was shown, where  > 0 is an arbitrary constant.
- We obtain our MPC protocol by constructing a e O(log2 n)-round CCAsecure commitment scheme in a black-box way under the assumption of the existence of one-way functions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160135 (1).pdf`
- `downloads/86160135 (2).pdf`
- `downloads/86160135 (3).pdf`
- `downloads/86160135 (4).pdf`
- `downloads/86160135 (5).pdf`
- `downloads/86160135 (6).pdf`
- (+1 more duplicate copies)
