---
id: KN-LIT-1912
type: literature
title: "The m = n + 1 Boundary of EME: A Splicing Distinguisher for the Unrefreshed"
authors:
  - "EME-Core Extension"
  - "Its Linear-Map"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1461"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1461"
tags: [quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
EME is a parallelizable encrypt–mix–encrypt wide-block construction proved secure for m-block messages only in the range m ≤ n, where n is the block length of the underlying block cipher. Halevi and Rogaway justified this restriction by giving a splicing distinguisher for m ≥ n + 2, but left open the first excluded length, m = n + 1.

## Key claims (as reported)
- We resolve that boundary for the direct, unrefreshed EME-core extension beyond its specified m ≤ n domain: the original formulas are applied to m = n + 1 blocks while continuing to use the same global mask.
- Under one fixed tweak, two encryption queries and one decryption query distinguish this extension from a random permutation.
- The result applies to this unrefreshed extension; refreshed variants such as EME∗ and IEEE EME2-AES are outside the scope of the distinguisher.
- The boundary attack is not a shortened form of the known zero-sum attack.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1461.pdf`
