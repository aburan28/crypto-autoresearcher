---
id: KN-LIT-4236
type: literature
title: "Homomorphic Network Coding Signatures in the Standard Model"
authors:
  - "Nuttapong Attrapadung"
  - "Benoı̂t Libert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, hash, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Network coding is known to provide improved resilience to packet loss and increased throughput. Unlike traditional routing techniques, it allows network nodes to perform transformations on packets they receive before transmitting them.

## Key claims (as reported)
- For this reason, packets cannot be authenticated using ordinary digital signatures, which makes it difficult to hedge against pollution attacks, where malicious nodes inject bogus packets in the network.
- To address this problem, recent works introduced signature schemes allowing to sign linear subspaces (namely, verification can be made w.r.t. any vector of that subspace) and which are well-suited to the network coding scenario.
- Currently known network coding signatures in the standard model are not homomorphic in that the signer is forced to sign all vectors of a given subspace at once.
- This paper describes the first homomorphic network coding signatures in the standard model: the security proof does not use random oracles and, at the same time, the scheme allows signing individual vectors on-the-fly and has constant per-packet overhead in terms of signature size.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65710019 (1).pdf`
- `downloads/65710019 (2).pdf`
- `downloads/65710019 (3).pdf`
- `downloads/65710019.pdf`
