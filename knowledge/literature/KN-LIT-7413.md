---
id: KN-LIT-7413
type: literature
title: "Universally-Composable Two-Party Computation in Two Rounds"
authors:
  - "Omer Horvitz"
  - "Jonathan Katz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Round complexity is a central measure of efficiency, and characterizing the round complexity of various cryptographic tasks is of both theoretical and practical importance. We show here a universallycomposable (UC) protocol (in the common reference string model) for two-party computation of any functionality, where both parties receive output, using only two rounds.

## Key claims (as reported)
- (This assumes honest parties are allowed to transmit messages simultaneously in any given round; we obtain a three-round protocol when parties are required to alternate messages.) Our results match the obvious lower bounds for the round complexity of secure two-party computation under any reasonable definition of security, regardless of what setup is used.
- Thus, our results establish that secure two-party computation can be obtained under a commonly-used setup assumption with maximal security (i.e., security under general composition) in a minimal number of rounds.
- To give but one example of the power of our general result, we observe that as an almost immediate corollary we obtain a two-round UC blind signature scheme, matching a result by Fischlin at Crypto 2006 (though, in contrast to Fischlin, we use specific number-theoretic assumptions).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/46220111 (1).pdf`
- `downloads/46220111 (2).pdf`
- `downloads/46220111 (3).pdf`
- `downloads/46220111.pdf`
